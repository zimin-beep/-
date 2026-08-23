"""
摄像头云台（PTZ）控制模块 —— 基于 ONVIF 协议
直接使用 HTTP Digest Auth + SOAP/XML，不依赖 onvif-zeep 的 WSDL 文件
适用于大华/乐橙/海康等支持 ONVIF 的网络摄像头
"""
import time
import requests
from requests.auth import HTTPDigestAuth
from xml.etree import ElementTree as ET

ONVIF_PORT = 80

# ONVIF XML 命名空间
NS = {
    "s": "http://www.w3.org/2003/05/soap-envelope",
    "onvif": "http://www.onvif.org/ver10/device/wsdl",
    "ptz": "http://www.onvif.org/ver20/ptz/wsdl",
    "media": "http://www.onvif.org/ver10/media/wsdl",
    "tt": "http://www.onvif.org/ver10/schema",
}


class PTZController:
    """ONVIF PTZ 云台控制器 —— 纯 requests + SOAP 实现"""

    def __init__(self, ip, user, password, port=ONVIF_PORT):
        self.base_url = f"http://{ip}:{port}"
        self.auth = HTTPDigestAuth(user, password)
        self.profile_token = self._get_first_profile_token()

    def _send_soap(self, path, xml_body):
        """发送 SOAP 请求并返回解析后的 XML"""
        url = f"{self.base_url}{path}"
        headers = {"Content-Type": "application/soap+xml; charset=utf-8"}
        resp = requests.post(url, data=xml_body.encode("utf-8"),
                             headers=headers, auth=self.auth, timeout=5)
        resp.raise_for_status()
        return ET.fromstring(resp.content)

    def _get_first_profile_token(self):
        """获取第一个 Media Profile 的 token"""
        body = f"""<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope">
  <s:Body>
    <GetProfiles xmlns="http://www.onvif.org/ver10/media/wsdl"/>
  </s:Body>
</s:Envelope>"""
        root = self._send_soap("/onvif/media_service", body)
        # 找到第一个 Profile 的 token
        for token in root.iter("{http://www.onvif.org/ver10/schema}Profiles"):
            for name in token.iter("{http://www.onvif.org/ver10/schema}Name"):
                # token 在 Profile 元素的属性里
                pass
        # 更直接的方式：找 Profile 元素的 token 属性
        for elem in root.iter():
            if "Profile" in elem.tag:
                token = elem.get("token", "")
                if token:
                    return token
        raise RuntimeError("摄像头没有可用的 Media Profile，请确认 ONVIF 已开启")

    def move(self, pan=0.0, tilt=0.0, zoom=0.0, timeout=0):
        """
        连续移动
        :param pan:   水平 [-1.0, 1.0]，负=左，正=右
        :param tilt:  垂直 [-1.0, 1.0]，负=下，正=上
        :param zoom:  变焦 [-1.0, 1.0]，负=缩小，正=放大
        :param timeout: 持续时间（秒），0=不自动停止
        """
        body = f"""<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"
            xmlns:ptz="http://www.onvif.org/ver20/ptz/wsdl"
            xmlns:tt="http://www.onvif.org/ver10/schema">
  <s:Body>
    <ptz:ContinuousMove>
      <ptz:ProfileToken>{self.profile_token}</ptz:ProfileToken>
      <ptz:Velocity>
        <tt:PanTilt x="{pan}" y="{tilt}"/>
        <tt:Zoom x="{zoom}"/>
      </ptz:Velocity>
    </ptz:ContinuousMove>
  </s:Body>
</s:Envelope>"""
        self._send_soap("/onvif/ptz_service", body)
        if timeout > 0:
            time.sleep(timeout)
            self.stop()

    def stop(self):
        """立即停止所有云台动作"""
        body = f"""<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"
            xmlns:ptz="http://www.onvif.org/ver20/ptz/wsdl">
  <s:Body>
    <ptz:Stop>
      <ptz:ProfileToken>{self.profile_token}</ptz:ProfileToken>
      <ptz:PanTilt>true</ptz:PanTilt>
      <ptz:Zoom>true</ptz:Zoom>
    </ptz:Stop>
  </s:Body>
</s:Envelope>"""
        self._send_soap("/onvif/ptz_service", body)

    # ============= 方向快捷方法 =============
    def up(self, speed=0.5, timeout=0):
        self.move(tilt=speed, timeout=timeout)

    def down(self, speed=0.5, timeout=0):
        self.move(tilt=-speed, timeout=timeout)

    def left(self, speed=0.5, timeout=0):
        self.move(pan=-speed, timeout=timeout)

    def right(self, speed=0.5, timeout=0):
        self.move(pan=speed, timeout=timeout)

    def zoom_in(self, speed=0.5, timeout=0):
        self.move(zoom=speed, timeout=timeout)

    def zoom_out(self, speed=0.5, timeout=0):
        self.move(zoom=-speed, timeout=timeout)
