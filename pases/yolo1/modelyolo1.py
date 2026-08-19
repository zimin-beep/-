import copy
import cv2
import torch
import numpy as np
import time
import os
import os.path as osp
from ultralytics import YOLO

# ===================== 全局常量定义 =====================
# 模型默认权重路径，可自行修改
DEFAULT = r'D:\pycharm\en\demo\ultralytics-main\runs\detect\train-6\weights\best.pt'


class YOLO1:
    """
    YOLOv8 病害检测推理封装类
    功能：图片目标检测、可视化编号标注、置信度评级、目标位置解析、结果结构化整理、图片自动存档
    """
    def __init__(self, weights_path: str = DEFAULT):
        """
        类初始化
        :param weights_path: YOLO模型权重文件路径，不传则使用默认best.pt
        """
        self.weights_path = weights_path
        # 加载YOLO模型实例
        self.model = self.load_model()
        # 置信度阈值：低于该值的框直接过滤
        self.conf_thres = 0.25
        # NMS非极大抑制IOU阈值：去除重叠冗余框
        self.iou_thres = 0.45
        # 是否保存txt检测标签文件
        self.save_txt = False
        # 是否在txt中保存置信度
        self.save_conf = False
        # 是否裁剪检测目标单独保存
        self.save_crop = False

    @torch.no_grad()
    def load_model(self):
        """
        加载YOLO模型
        @torch.no_grad：关闭梯度计算，推理阶段加速、节省显存
        :return: YOLO模型对象
        """
        return YOLO(self.weights_path)

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
            tmp_path = "images/tmp/single_result.jpg"
            cv2.imwrite(tmp_path, im0)

            # 生成带时间戳的存档图片，永久保存到record/img
            time_re = time.strftime("result_%Y-%m-%d_%H-%M-%S_%A")
            record_dir = "record/img"
            os.makedirs(record_dir, exist_ok=True)
            record_path = osp.join(record_dir, f"{time_re}.jpg")
            cv2.imwrite(record_path, annotated_img)

            # 类别中英文映射字典，可扩充病害中英文对照
            result_names = result.names
            name_map = {"basketball": "篮球"}

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
