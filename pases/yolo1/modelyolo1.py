import copy
import json
import cv2
import torch
import time
import os
import os.path as osp
import threading
from datetime import datetime
from ultralytics import YOLO

# ===================== 全局常量定义 =====================
# 模型默认权重路径，可自行修改
DEFAULT = "/Users/mac/PycharmProjects/train/corn-disease-download/corn-disease-best.pt"

# 当前生效的模型权重路径（由 load_model_config 读取，空字符串表示用 DEFAULT）
current_model_path = ""
# 模型配置 JSON 文件路径
CONFIG_JSON_PATH = "model_config.json"
# 全局置信度 / NMS 阈值，前端可通过 /api/save_model_config 动态修改
conf_thres = 0.25
iou_thres = 0.45
# 摄像头 RTSP 地址 + PTZ 认证（前端可配置）
rtsp_url = ""




def _resolve_dirs():
    """
    与 mainyolo1.py 保持一致地动态解析目录（避免顶层循环 import）
    返回：(临时预览图目录 tmp_dir, 结果存档目录 result_dir)
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))   # .../pases/yolo1
    project_root = os.path.dirname(os.path.dirname(script_dir))  # .../demo
    tmp_dir = os.path.join(script_dir, "images", "tmp")
    result_dir = os.path.join(script_dir, "record", "img")
    os.makedirs(tmp_dir, exist_ok=True)
    os.makedirs(result_dir, exist_ok=True)
    return tmp_dir, result_dir


# 提前解析出绝对路径并建目录，后续 detect_image 直接使用
_TMP_DIR, _RESULT_DIR = _resolve_dirs()


def load_model_config():
    """从 model_config.json 读取模型路径 + 阈值 + 摄像头配置，写回全局变量"""
    global current_model_path, conf_thres, iou_thres, rtsp_url, ptz_ip, ptz_user, ptz_pass
    if osp.exists(CONFIG_JSON_PATH):
        with open(CONFIG_JSON_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            current_model_path = cfg.get("model_path", "")
            conf_thres = cfg.get("conf_thres", 0.25)
            iou_thres = cfg.get("iou_thres", 0.45)
            rtsp_url = cfg.get("rtsp_url", "")
            ptz_ip = cfg.get("ptz_ip", "")
            ptz_user = cfg.get("ptz_user", "")
            ptz_pass = cfg.get("ptz_pass", "")


def save_model_config(model_path, new_conf=None, new_iou=None, new_rtsp=None, new_ptz_ip=None, new_ptz_user=None, new_ptz_pass=None):
    """保存模型路径 + 阈值 + 摄像头配置到 JSON，同时更新全局变量"""
    global current_model_path, conf_thres, iou_thres, rtsp_url, ptz_ip, ptz_user, ptz_pass
    current_model_path = model_path
    if new_conf is not None:
        conf_thres = new_conf
    if new_iou is not None:
        iou_thres = new_iou
    if new_rtsp is not None:
        rtsp_url = new_rtsp
    if new_ptz_ip is not None:
        ptz_ip = new_ptz_ip
    if new_ptz_user is not None:
        ptz_user = new_ptz_user
    if new_ptz_pass is not None:
        ptz_pass = new_ptz_pass
    cfg = {
        "model_path": model_path,
        "conf_thres": conf_thres,
        "iou_thres": iou_thres,
        "rtsp_url": rtsp_url,
        "ptz_ip": ptz_ip,
        "ptz_user": ptz_user,
        "ptz_pass": ptz_pass,
    }
    with open(CONFIG_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


class YOLO1:
    """
    YOLOv8 病害检测推理封装类
    功能：图片目标检测、可视化编号标注、置信度评级、目标位置解析、结果结构化整理、图片自动存档
    """
    # 病虫害中英文映射字典（可按需扩充）
    NAME_MAP = {
        "Blight": "枯萎病",
        "brown_spot": "褐斑病",
        "corn_rust": "玉米锈病",
        "corn_smut": "玉米肿瘤病",
        "downy_mildew": "霜霉病",
        "fall-armyworm-larva": "秋黏虫幼虫",
        "grey_leaf_spot": "灰斑病",
        "healthy": "健康",
        "maize-streak-disease": "玉米条斑病",
        "yellow-stem-borer": "黄茎螟",
        "yellow-stem-borer-larva": "黄茎螟幼虫"
    }

    def __init__(self, weights_path: str = DEFAULT, conf_thres: float = None, iou_thres: float = None):
        """
        类初始化
        :param weights_path: YOLO模型权重文件路径，不传则使用默认best.pt
        :param conf_thres: 置信度阈值，不传则使用模块级全局变量（从配置文件读取）
        :param iou_thres: NMS IOU阈值，不传则使用模块级全局变量
        """
        self.weights_path = weights_path
        # 加载YOLO模型实例
        self.model = self.load_model()
        # 置信度阈值：优先使用传入参数，否则使用模块级配置
        self.conf_thres = conf_thres if conf_thres is not None else globals().get('conf_thres', 0.25)
        # NMS非极大抑制IOU阈值
        self.iou_thres = iou_thres if iou_thres is not None else globals().get('iou_thres', 0.45)
        # 是否保存txt检测标签文件
        self.save_txt = False
        # 是否在txt中保存置信度
        self.save_conf = False
        # 是否裁剪检测目标单独保存
        self.save_crop = False

    @staticmethod
    def _resolve_device():
        """自动选择最优推理设备：CUDA > MPS > CPU"""
        if torch.cuda.is_available():
            return "cuda"
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    @torch.no_grad()
    def load_model(self):
        """
        加载YOLO模型，自动选择最优设备（CUDA / MPS / CPU）
        @torch.no_grad：关闭梯度计算，推理阶段加速、节省显存
        :return: YOLO模型对象
        """
        device = self._resolve_device()
        print(f"[YOLO] 推理设备: {device}")
        model = YOLO(self.weights_path)
        model.to(device)
        return model

    def reload_model(self, model_path, conf_thres=None, iou_thres=None):
        """热加载新模型权重，切换检测模型，同时更新阈值。自动清理旧模型显存。"""
        self.weights_path = model_path
        del self.model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        self.model = YOLO(model_path)
        self.model.to(self._resolve_device())
        if conf_thres is not None:
            self.conf_thres = conf_thres
        if iou_thres is not None:
            self.iou_thres = iou_thres

    def _judge_probability(self, conf):
        """
        私有方法：根据置信度划分可信度等级 + 给出人工复核建议
        :param conf: 单个目标置信度浮点值
        :return: (等级文字, 复核建议)
        """
        if conf >= 0.90:
            return "很高", "模型高度确信，建议采用"
        elif conf >= 0.80:
            return "较高", "模型比较确定，基本可信"
        elif conf >= 0.70:
            return "中等", "有一定可信度，建议复核"
        elif conf >= 0.50:
            return "较低", "可信度不足，建议人工确认"
        else:
            return "很低", "模型不确定，必须人工审核"

    def _draw_number_in_box(self, img, number, x1, y1, x2, y2):
        """
        私有绘制方法：目标框内部中心绘制圆形编号，目标少时使用
        :param img: 原图numpy数组
        :param number: 当前目标序号
        :param x1,y1: 左上角坐标
        :param x2,y2: 右下角坐标
        """
        # 计算框中心点
        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)

        # 根据框大小自适应圆圈半径，限制最大最小尺寸
        box_w = x2 - x1
        radius = min(int(box_w * 0.15), 20, int((y2 - y1) * 0.15))
        radius = max(radius, 12)

        # 绘制红色实心圆底色
        cv2.circle(img, (cx, cy), radius, (0, 0, 255), -1)
        # 白色外圈描边
        cv2.circle(img, (cx, cy), radius, (255, 255, 255), 2)

        # 自适应字体大小，个位数大一点、两位数缩小
        font_scale = 0.5 if number < 10 else 0.4
        thickness = 2
        text = str(number)
        # 获取文字宽高
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
        # 文字居中坐标
        tx = cx - tw // 2
        ty = cy + th // 2

        # 绘制白色序号文字
        cv2.putText(
            img,
            text,
            (tx, ty),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            (255, 255, 255),
            thickness,
        )

    def _draw_number_with_line(self, img, number, x1, y1, x2, y2, direction_idx):
        """
        私有绘制方法：多目标时使用引线外置编号，防止框内文字重叠遮挡
        :param img: 图片数组
        :param number: 序号
        :param x1,y1,x2,y2: 框坐标
        :param direction_idx: 方向索引，轮流上下左右引线，避免标签扎堆
        """
        # 目标框中心
        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)

        # 4个引线方向：上、右、下、左
        img_h, img_w = img.shape[:2]
        directions = [
            (0, -40),  # 向上
            (40, 0),   # 向右
            (0, 40),   # 向下
            (-40, 0),  # 向左
        ]
        dx, dy = directions[direction_idx % 4]

        # 引线终点边界约束，防止标签超出图片画面
        tx = max(25, min(img_w - 25, cx + dx))
        ty = max(25, min(img_h - 25, cy + dy))

        # 绘制红色引线
        cv2.line(img, (cx, cy), (tx, ty), (0, 0, 255), 2)

        # 标签矩形尺寸
        label_w = 26 if number < 10 else 32
        label_h = 22

        # 红色标签底色矩形
        cv2.rectangle(
            img,
            (tx - label_w // 2, ty - label_h // 2),
            (tx + label_w // 2, ty + label_h // 2),
            (0, 0, 255),
            -1,
        )
        # 白色边框
        cv2.rectangle(
            img,
            (tx - label_w // 2, ty - label_h // 2),
            (tx + label_w // 2, ty + label_h // 2),
            (255, 255, 255),
            1,
        )

        # 标签文字绘制
        font_scale = 0.5
        thickness = 2
        text = str(number)
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
        ttx = tx - tw // 2
        tty = ty + th // 2

        cv2.putText(
            img,
            text,
            (ttx, tty),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            (255, 255, 255),
            thickness,
        )

    def detect_image(self, image_path: str, output_size: int = 480):
        """
        对外核心推理接口：单张图片完整检测流程
        :param image_path: 待检测图片路径
        :param output_size: 前端预览图高度，等比例缩放
        :return: 字典，success标记成败，附带图片路径、结构化检测数据、统计分析
        """
        try:
            # YOLO执行推理检测
            results = self.model(
                image_path,
                imgsz=800,
                conf=self.conf_thres,
                iou=self.iou_thres,
                save_txt=self.save_txt,
                save_conf=self.save_conf,
                save_crop=self.save_crop,
            )

            result = results[0]
            # YOLO自带绘制框的图片
            img_array = result.plot()

            num_boxes = len(result.boxes)
            annotated_img = img_array.copy()

            # 根据目标数量自动选择标注方式：少目标框内编号、多目标引线编号
            for i, box in enumerate(result.boxes):
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                if num_boxes <= 3:
                    self._draw_number_in_box(annotated_img, i + 1, x1, y1, x2, y2)
                else:
                    self._draw_number_with_line(annotated_img, i + 1, x1, y1, x2, y2, i)

            # 生成前端临时预览图（缩放固定高度）
            im0 = copy.deepcopy(annotated_img)
            resize_scale = output_size / im0.shape[0]
            im0 = cv2.resize(im0, (0, 0), fx=resize_scale, fy=resize_scale)
            tmp_path = os.path.join(_TMP_DIR, "single_result.jpg")
            cv2.imwrite(tmp_path, im0)

            # 生成带时间戳的存档图片，永久保存到 record/img（微秒级精度，防止批量检测时文件名冲突覆盖）
            time_re = datetime.now().strftime("result_%Y-%m-%d_%H-%M-%S_%f")
            record_path = osp.join(_RESULT_DIR, f"{time_re}.jpg")
            cv2.imwrite(record_path, annotated_img)

            # 类别中英文映射字典，可扩充病害中英文对照
            result_names = result.names
            name_map = self.NAME_MAP

            detected_objects = []   # 存放所有目标详细信息
            confidence_list = []    # 收集全部置信度，用于后续平均值计算

            # 遍历每一个检测框，结构化解析信息
            for i, box in enumerate(result.boxes):
                conf = float(box.conf)
                confidence_list.append(conf)

                cls_id = int(box.cls)
                en_name = result_names[cls_id]
                cn_name = name_map.get(en_name, en_name)

                # 置信度评级与建议
                level, suggestion = self._judge_probability(conf)

                # 计算框中心相对图片宽高比例
                img_h, img_w = img_array.shape[:2]
                cx = float(box.xywh[0][0])
                cy = float(box.xywh[0][1])
                rel_x = cx / img_w
                rel_y = cy / img_h

                # 位置中文描述
                position_desc = self._get_position_description(rel_x, rel_y)

                # 单个目标结构化数据
                obj = {
                    "id": i + 1,
                    "class_id": cls_id,
                    "name_en": en_name,
                    "name_cn": cn_name,
                    "confidence": round(conf, 4),
                    "confidence_percent": f"{conf * 100:.2f}%",
                    "position": {
                        "x1": round(float(box.xyxy[0][0]), 2),
                        "y1": round(float(box.xyxy[0][1]), 2),
                        "x2": round(float(box.xyxy[0][2]), 2),
                        "y2": round(float(box.xyxy[0][3]), 2),
                        "description": position_desc,
                    },
                    "judgment": {
                        "level": level,
                        "suggestion": suggestion,
                    },
                }
                detected_objects.append(obj)

            # 分类统计：每个类别数量、对应序号
            class_summary = {}
            for obj in detected_objects:
                name = obj["name_cn"]
                if name not in class_summary:
                    class_summary[name] = {"count": 0, "objects": []}
                class_summary[name]["count"] += 1
                class_summary[name]["objects"].append(obj["id"])

            # 拼接文本汇总信息
            result_info = ""
            for name, info in class_summary.items():
                result_info += f"{name}:{info['count']}个\n"
           

            total_count = len(detected_objects)
            # 平均置信度
            avg_conf = sum(confidence_list) / len(confidence_list) if confidence_list else 0

            # 置信度等级数量统计
            level_count = {}
            for obj in detected_objects:
                level = obj["judgment"]["level"]
                level_count[level] = level_count.get(level, 0) + 1

            # 整体分析汇总
            analysis_result = {
                "detected_objects": detected_objects,
                "summary": {
                    "total": total_count,
                    "avg_confidence": round(avg_conf, 4),
                    "class_summary": class_summary,
                    "level_distribution": level_count,
                },
            }

            # 正常成功返回
            return {
                "success": True,
                "result_image": tmp_path,
                "result_info": result_info,
                "record_path": record_path,
                "analysis_result": analysis_result,
            }

        except Exception as e:
            # 异常捕获，返回错误信息
            return {"success": False, "error": str(e)}

    def detect_frame(self, frame, output_size: int = 720):
        """
        【内存实时推理，用于摄像头流，不读写磁盘｜ByteTrack跟踪模式】
        :param frame: numpy数组 BGR摄像头帧
        :param output_size: 输出预览高度
        :return: success, annotated_img(带框numpy), analysis_result结构化数据
        """
        try:
            # track增加 persist=True，指定bytetrack跟踪器
            results = self.model.track(
                frame,
                imgsz=800,
                conf=self.conf_thres,
                iou=self.iou_thres,
                persist=True,  # ✅关键：维持跟踪器跨帧状态
                tracker="bytetrack.yaml",  # ✅跟踪算法
                save_txt=False,
                save_conf=False,
                save_crop=False,
            )
            result = results[0]
            img_array = result.plot()
            num_boxes = len(result.boxes)
            annotated_img = img_array.copy()

            # 绘制编号
            for i, box in enumerate(result.boxes):
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                if num_boxes <= 3:
                    self._draw_number_in_box(annotated_img, i + 1, x1, y1, x2, y2)
                else:
                    self._draw_number_with_line(annotated_img, i + 1, x1, y1, x2, y2, i)

            result_names = result.names
            name_map = self.NAME_MAP
            detected_objects = []
            confidence_list = []

            for i, box in enumerate(result.boxes):
                conf = float(box.conf)
                confidence_list.append(conf)
                cls_id = int(box.cls)
                en_name = result_names[cls_id]
                cn_name = name_map.get(en_name, en_name)
                level, suggestion = self._judge_probability(conf)

                img_h, img_w = img_array.shape[:2]
                cx = float(box.xywh[0][0])
                cy = float(box.xywh[0][1])
                rel_x = cx / img_w
                rel_y = cy / img_h
                position_desc = self._get_position_description(rel_x, rel_y)

                # --------使用track_id，没有id时回退帧内下标--------
                if box.id is not None:
                    track_id = int(box.id.item())
                else:
                    track_id = i + 1

                obj = {
                    "id": i + 1,  # 统一字段名，前端用这个渲染编号
                    "track_id": track_id,  # ✅跟踪全局ID，业务存库用这个
                    "frame_index_id": i + 1,  # ✅本帧数组下标，绘图显示用
                    "class_id": cls_id,
                    "name_en": en_name,
                    "name_cn": cn_name,
                    "confidence": round(conf, 4),
                    "confidence_percent": f"{conf * 100:.2f}%",
                    "position": {
                        "x1": round(float(box.xyxy[0][0]), 2),
                        "y1": round(float(box.xyxy[0][1]), 2),
                        "x2": round(float(box.xyxy[0][2]), 2),
                        "y2": round(float(box.xyxy[0][3]), 2),
                        "description": position_desc,
                    },
                    "judgment": {"level": level, "suggestion": suggestion},
                }
                detected_objects.append(obj)

            class_summary = {}
            for obj in detected_objects:
                name = obj["name_cn"]
                if name not in class_summary:
                    class_summary[name] = {"count": 0, "objects": []}
                class_summary[name]["count"] += 1
                class_summary[name]["objects"].append(obj["track_id"])  # 汇总用track_id

            total_count = len(detected_objects)
            avg_conf = (
                sum(confidence_list) / len(confidence_list) if confidence_list else 0
            )
            level_count = {}
            for obj in detected_objects:
                lv = obj["judgment"]["level"]
                level_count[lv] = level_count.get(lv, 0) + 1

            analysis_result = {
                "detected_objects": detected_objects,
                "summary": {
                    "total": total_count,
                    "avg_confidence": round(avg_conf, 4),
                    "class_summary": class_summary,
                    "level_distribution": level_count,
                },
            }
            return True, annotated_img, analysis_result
        except Exception as e:
            return False, None, {"error": str(e)}



    def _get_position_description(self, rel_x, rel_y):
        """
        私有方法：根据目标中心点相对图片坐标，生成中文方位描述
        :param rel_x: 中心点X / 图片总宽度，0~1
        :param rel_y: 中心点Y / 图片总高度，0~1
        :return: 方位中文描述
        """
        # 中心区域
        if 0.4 <= rel_x <= 0.6 and 0.4 <= rel_y <= 0.6:
            return "图片正中央"

        # 四个角落判断
        if rel_x < 0.2 and rel_y < 0.2:
            return "左上角"
        if rel_x > 0.8 and rel_y < 0.2:
            return "右上角"
        if rel_x < 0.2 and rel_y > 0.8:
            return "左下角"
        if rel_x > 0.8 and rel_y > 0.8:
            return "右下角"

        # 横竖粗略分区
        h = "左侧" if rel_x < 0.33 else ("右侧" if rel_x > 0.66 else "中央")
        v = "上方" if rel_y < 0.33 else ("下方" if rel_y > 0.66 else "中部")

        return f"{v}{h}"


# 乐橙RTSP地址：从 model_config.json 读取，前端可配置
# 若配置文件未提供，使用此默认值
_DEFAULT_RTSP_URL = "rtsp://admin:L2801724@192.168.1.79:554/cam/realmonitor?channel=1&subtype=0?tcp"
RTSP_URL = rtsp_url or _DEFAULT_RTSP_URL
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000

# 推理跳帧数：每 N 帧推理一次，其余帧只更新画面
SKIP_FRAME = 3

# 推理输出帧最大高度，超过则等比缩小
MJPEG_MAX_HEIGHT = 720
MJPEG_QUALITY = 70

# 全局共享变量
global_frame = None          # 最新帧（用于MJPEG推流）
global_latest_analysis = None  # 最新分析结果
lock = threading.Lock()
# 帧就绪通知：新帧到达或状态变化时唤醒推流
frame_ready = threading.Condition(lock)

# 预编码JPEG缓存，避免多连接重复resize+imencode
_cached_jpeg = None
_cached_jpeg_lock = threading.Lock()


class RtspReadThread:
    """
    采集线程只负责读RTSP取最新帧 → 推理线程独立消费，队列解耦。
    推理慢时丢弃旧帧，永远只处理最新帧。
    """
    def __init__(self, rtsp_url, yolo_ins: YOLO1):
        self.yolo = yolo_ins
        self.rtsp_url = rtsp_url
        self.cap = None
        self.running = True
        # 最新原始帧 + 是否有新帧待推理
        self._latest_raw_frame = None
        self._frame_lock = threading.Lock()
        self._infer_cond = threading.Condition(self._frame_lock)
        self._has_new = False
        self._infer_thread = None
        self._open_cap()

    def _open_cap(self):
        """（重建）打开RTSP连接"""
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception:
                pass
        self.cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    def start(self):
        """启动采集线程和推理线程"""
        self._infer_thread = threading.Thread(target=self._infer_loop, daemon=True)
        self._infer_thread.start()
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()

    def _capture_loop(self):
        """采集线程：只读RTSP取最新帧，不做推理"""
        consecutive_fail = 0
        while self.running:
            try:
                # 快速丢弃缓冲区积压的旧帧（非阻塞，最多丢3帧）
                for _ in range(3):
                    if not self.cap.grab():
                        break
                ret, frame = self.cap.retrieve()
                if not ret:
                    consecutive_fail += 1
                    if consecutive_fail > 10:
                        print("[RTSP] 连续读取失败，尝试重连...")
                        self._open_cap()
                        consecutive_fail = 0
                        time.sleep(1.0)
                    else:
                        time.sleep(0.05)
                    continue
                consecutive_fail = 0

                # 把最新帧推给推理线程
                with self._infer_cond:
                    self._latest_raw_frame = frame
                    self._has_new = True
                    self._infer_cond.notify_all()

            except Exception as e:
                print(f"[RTSP] 采集异常: {e}")
                self._open_cap()
                time.sleep(1.0)

    def _infer_loop(self):
        """推理线程：从采集线程拿最新帧做YOLO推理"""
        global global_frame, global_latest_analysis
        while self.running:
            # 等待新帧到来
            with self._infer_cond:
                while not self._has_new and self.running:
                    self._infer_cond.wait(timeout=1.0)
                if not self.running:
                    break
                frame = self._latest_raw_frame
                self._has_new = False

            if frame is None:
                continue

            # 每帧都推理：YOLO检测 + 标注
            ok, annotated_img, analysis = self.yolo.detect_frame(frame)
            with frame_ready:
                if ok:
                    global_frame = annotated_img
                else:
                    # 推理失败/无目标：用原始帧继续推流，不冻结画面
                    global_frame = frame
                global_latest_analysis = analysis
                _update_cached_jpeg()
                frame_ready.notify_all()

    def stop(self):
        self.running = False
        # 唤醒可能阻塞的推理线程，等待其退出后再释放cap
        with self._infer_cond:
            self._infer_cond.notify_all()
        if self._infer_thread is not None:
            self._infer_thread.join(timeout=3.0)
        if self.thread is not None:
            self.thread.join(timeout=2.0)
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()


def _update_cached_jpeg():
    """将 global_frame resize + 编码为 JPEG 缓存，所有MJPEG连接共享"""
    global _cached_jpeg
    frame = global_frame
    if frame is None:
        return
    h, w = frame.shape[:2]
    if h > MJPEG_MAX_HEIGHT:
        scale = MJPEG_MAX_HEIGHT / h
        frame = cv2.resize(frame, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    ok, buf = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), MJPEG_QUALITY])
    if ok:
        with _cached_jpeg_lock:
            _cached_jpeg = buf.tobytes()


def _build_placeholder_jpeg(text: str = "等待摄像头画面...", size=(640, 360)) -> bytes:
    import numpy as np
    img = np.zeros((size[1], size[0], 3), dtype=np.uint8)
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.8
    thickness = 2
    (tw, th), _ = cv2.getTextSize(text, font, font_scale, thickness)
    tx = (size[0] - tw) // 2
    ty = (size[1] + th) // 2
    cv2.putText(img, text, (tx, ty), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)
    ok, buf = cv2.imencode('.jpg', img)
    return buf.tobytes() if ok else b''


_PLACEHOLDER_JPEG = _build_placeholder_jpeg(text="请点击【开启实时检测】按钮")


def generate_mjpeg():
    """MJPEG流生成器，所有连接共享预编码JPEG，无重复resize+imencode"""
    if _PLACEHOLDER_JPEG:
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + _PLACEHOLDER_JPEG + b'\r\n')

    sent_placeholder = False
    last_sent = None
    while True:
        with frame_ready:
            # 等待新帧就绪（事件驱动，不再sleep轮询）
            jpeg = _cached_jpeg
            if jpeg is None:
                if not sent_placeholder and _PLACEHOLDER_JPEG:
                    jpeg = _PLACEHOLDER_JPEG
                    sent_placeholder = True
                else:
                    frame_ready.wait(timeout=0.5)
                    continue
            else:
                sent_placeholder = False
                # 帧未变化时不重复发送
                if jpeg == last_sent:
                    frame_ready.wait(timeout=0.5)
                    continue
                last_sent = jpeg

        if jpeg is None:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n')