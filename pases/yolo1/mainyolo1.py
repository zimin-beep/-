import os
import io
import base64
import random
import string
import time
from flask import Flask, request, jsonify, send_from_directory,Response
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from datetime import datetime
from werkzeug.utils import secure_filename
from mysql import *
from clear_by_time import start_clean_timer
from modelyolo1 import *

import modelyolo1 as _m1
from ptz_control import PTZController
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024  # 允许上传最大 500MB 模型文件
CORS(app)
jwt = JWTManager(app)

# 启动时从 model_config.json 读取上一次保存的模型路径 + 阈值
load_model_config()
# 如果配置文件里有模型路径就用它，否则用 DEFAULT 默认权重
detector = YOLO1(weights_path=current_model_path or DEFAULT, conf_thres=conf_thres, iou_thres=iou_thres)

# RTSP 实时检测线程对象（None 表示未开启）
_rtsp_thread = None

# PTZ 云台控制器（懒加载，首次调用接口时才连接摄像头）
_ptz = None
# 摄像头 ONVIF 认证信息（与 RTSP 一致）
_PTZ_IP = "192.168.1.79"
_PTZ_USER = "admin"
_PTZ_PASS = "L2801724"

def _get_ptz():
    """懒加载 PTZ 控制器，连接失败返回 None"""
    global _ptz
    if _ptz is None:
        try:
            _ptz = PTZController(_PTZ_IP, _PTZ_USER, _PTZ_PASS)
            print("✅ ONVIF PTZ 控制器已连接")
        except Exception as e:
            print(f"⚠️  PTZ 连接失败（需在摄像头后台开启 ONVIF）：{e}")
            _ptz = None
    return _ptz

####注释掉的代码都是第一次写的,有很多问题,为了方便对照问题
app.config["JWT_SECRET_KEY"] = "zimin-demo1"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = (
    3600  # 这个是前端登录后给到的令牌,有效期是一个小时,(单位是秒),expired:过期的,失效
)
# 刷新凭证7天，用来无感续期
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = 7 * 24 * 3600


# 模型检测结果图URL前缀
RESULT_URL_PATH = "/pases/yolo1/record/img"
# 浏览器访问URL前缀
URL_REGEX = "/pases/upload-demo/static/knowledge"
# 检测图本地存放文件夹
URL_RES = "http://127.0.0.1:8080/pases/yolo1/record/img"





# 1. 获取当前脚本 mainyolo1.py 所在目录
script_dir = os.path.dirname(__file__)
# 往上两级，拿到项目根目录 D:\pycharm\en\demo
project_root = os.path.dirname(os.path.dirname(script_dir))
print("项目工程根目录：", project_root)
# 提取工程文件夹名称（demo）
project_name = os.path.basename(project_root)
print("工程目录名：", project_name)

# 模型权重存放目录
WEIGHTS_DIR = os.path.join(script_dir, "weights")
if not os.path.exists(WEIGHTS_DIR):
    os.makedirs(WEIGHTS_DIR)
    print("模型权重目录已自动创建：", WEIGHTS_DIR)
# ----------------------
# 示例1：原图上传文件夹
# ----------------------
upload_folder = os.path.join(project_root, "pases", "upload-demo", "static", "upload")
# 判断不存在就创建（递归创建多级目录）
if not os.path.exists(upload_folder):
    os.makedirs(upload_folder)
    print("文件夹已自动创建：", upload_folder)
else:
    print("文件夹已存在：", upload_folder)


knowledge_folder = os.path.join(
    project_root, "pases", "upload-demo", "static", "knowledge"
)
# 判断不存在就创建（递归创建多级目录）
if not os.path.exists(knowledge_folder):
    os.makedirs(knowledge_folder)
    print("文件夹已自动创建：", knowledge_folder)
else:
    print("文件夹已存在：", knowledge_folder)
# ----------------------
# 示例2：模型检测结果图文件夹
# ----------------------
result_img_folder = os.path.join(project_root, "pases", "yolo1", "record", "img")
if not os.path.exists(result_img_folder):
    os.makedirs(result_img_folder)
    print("结果图文件夹已自动创建：", result_img_folder)
else:
    print("结果图文件夹已存在：", result_img_folder)

# 直接赋值给你的全局变量，替代硬编码
# 样例图片本地存放文件夹
UPLOAD = upload_folder
RESULT_DIR = result_img_folder
UPLOAD_KNOWLEDGE = knowledge_folder


@jwt.expired_token_loader
def expired_token(jwt_header, jwt_payload):
    return jsonify({"success": False, "msg": "登录已过期,请重新登录"}), 401


def _check_admin():
    """校验当前JWT用户是否为系统管理员，不是则返回错误响应"""
    payload = get_jwt()
    role = payload.get("role", "")
    if role != "系统管理员":
        return jsonify({"success": False, "msg": "权限不足，仅系统管理员可访问"}), 403
    return None


# 仅校验 refresh_token，不需要业务access_token
@app.route("/api/refresh_token", methods=["POST"])
@jwt_required(refresh=True)
def refresh_token():
    # 获取登录用户名
    username = get_jwt_identity()
    payload = get_jwt()
    role = payload.get("role")
    # 生成全新的业务token返回前端
    new_access_token = create_access_token(identity=username, additional_claims={"role": role})
    return jsonify({
        "success": True,
        "new_access_token": new_access_token
    })




# 验证码存储 {captcha_id: {"text": "ABCD", "time": timestamp}}
_captcha_store = {}
CAPTCHA_EXPIRE_SECONDS = 300  # 验证码5分钟过期

def _generate_captcha_text(length=4):
    """生成随机验证码文本(字母+数字,排除易混字符)"""
    chars = string.ascii_uppercase + string.digits
    chars = chars.replace('O', '').replace('0', '').replace('I', '').replace('1', '')
    return ''.join(random.choice(chars) for _ in range(length))

def _generate_captcha_image(text, width=120, height=40):
    """生成验证码图片(PIL)，返回base64编码的PNG"""
    # 创建图像
    img = Image.new('RGB', (width, height), (240, 240, 240))
    draw = ImageDraw.Draw(img)

    # 尝试加载字体,失败则用默认
    try:
        font = ImageFont.truetype("arial.ttf", 28)
    except:
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/simhei.ttf", 28)
        except:
            font = ImageFont.load_default()

    # 绘制文字
    char_width = width // (len(text) + 1)
    for i, char in enumerate(text):
        x = char_width * i + char_width // 4
        y = random.randint(2, 8)
        color = (random.randint(30, 100), random.randint(30, 100), random.randint(30, 100))
        draw.text((x, y), char, fill=color, font=font)

    # 添加干扰线
    for _ in range(4):
        x1, y1 = random.randint(0, width), random.randint(0, height)
        x2, y2 = random.randint(0, width), random.randint(0, height)
        color = (random.randint(150, 200), random.randint(150, 200), random.randint(150, 200))
        draw.line([(x1, y1), (x2, y2)], fill=color, width=1)

    # 添加干扰点
    for _ in range(50):
        x, y = random.randint(0, width), random.randint(0, height)
        color = (random.randint(100, 180), random.randint(100, 180), random.randint(100, 180))
        draw.point((x, y), fill=color)

    # 转为base64
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return img_base64

@app.route("/api/captcha", methods=["GET"])
def get_captcha():
    """获取验证码"""
    captcha_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
    captcha_text = _generate_captcha_text()
    captcha_img = _generate_captcha_image(captcha_text)

    _captcha_store[captcha_id] = {
        "text": captcha_text,
        "time": time.time()
    }

    # 清理过期验证码
    now = time.time()
    expired_ids = [k for k, v in _captcha_store.items() if now - v["time"] > CAPTCHA_EXPIRE_SECONDS]
    for k in expired_ids:
        del _captcha_store[k]

    return jsonify({
        "success": True,
        "captcha_id": captcha_id,
        "captcha_image": "data:image/png;base64," + captcha_img
    })

@app.route("/api/login", methods=["POST"])
def login():
    username = request.json.get("username")
    password = request.json.get("password")
    captcha_id = request.json.get("captcha_id")
    captcha_text = request.json.get("captcha_text")

    if not username or not password:
        return jsonify({"success": False, "msg": "账号或密码不能为空"}), 403

    # 验证码校验
    if not captcha_id or not captcha_text:
        return jsonify({"success": False, "msg": "请输入验证码"}), 403

    captcha_data = _captcha_store.get(captcha_id)
    if not captcha_data:
        return jsonify({"success": False, "msg": "验证码已过期,请刷新"}), 403

    if time.time() - captcha_data["time"] > CAPTCHA_EXPIRE_SECONDS:
        del _captcha_store[captcha_id]
        return jsonify({"success": False, "msg": "验证码已过期,请刷新"}), 403

    if captcha_text.upper() != captcha_data["text"]:
        return jsonify({"success": False, "msg": "验证码错误"}), 403

    # 一次性使用,验证后删除
    del _captcha_store[captcha_id]

    sql = "SELECT * FROM users WHERE username = %s"
    result = query_one(sql, (username,))

    if not result or result["password"] != password:
        return jsonify({"success": False, "msg": "用户名或密码错误"})

    if result["role"] == "1":
        role = "系统管理员"
    else:
        role = "普通用户"

    access_token = create_access_token(identity=username, additional_claims={"role": role})
    refresh_token =create_refresh_token(identity=username)
    # create_access_token 是flask-jwt-extended内置函数,用于生成access token ,
    # 里面的identity就是jwt的header,
    # additional_claims 就是jwt的payload

    return jsonify({"success": True,
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "msg": role,
                    "msg1":result['role']
                    }), 200



@app.route("/api/gettime", methods=["POST"])
def gettime():
    day_str = datetime.now().strftime("%Y-%m-%d")
    return jsonify({"time": day_str})


# 检测结果图访问路由
@app.route(f"{RESULT_URL_PATH}/<filename>")
def real_img(filename):
    return send_from_directory(RESULT_DIR, filename)


# 访问模型检测结果图片和样例图片
@app.route(f"{URL_REGEX}/<path:filename>")
def serve_upload(filename):
    return send_from_directory(UPLOAD_KNOWLEDGE, filename)


@app.route("/api/upload", methods=["POST"])
@jwt_required()
def upload():
    # 1. 判断前端有没有传图片，file是前端上传字段名
    if "file" not in request.files:
        return jsonify({"success": False, "msg": "未上传图片"})
    img = request.files["file"]

    # 2. 判断文件名为空的情况
    if img.filename == "":
        return jsonify({"success": False, "msg": "文件名为空"})

    # 3. 校验图片后缀格式
    suffix = img.filename.split(".")[-1].lower()
    allow = ["jpg", "png", "jpeg"]
    if suffix not in allow:
        return jsonify({"success": False, "msg": "文件格式不匹配，仅支持jpg/png/jpeg"})

    # 4. 拼接本地保存路径，保存原图
    save_path = os.path.join(UPLOAD, img.filename)
    img.save(save_path)

    # 5. YOLO模型检测图片
    img_res = detector.detect_image(save_path)
    # 判断检测是否成功
    if not img_res["success"]:
        return jsonify({"success": False, "msg": img_res["error"]})

    img_path = img_res["record_path"]
    real_filename = os.path.basename(img_path)
    result_img_url = f"{URL_RES}/{real_filename}"

    # 6. 保存到数据库
    user_id = get_jwt().get("user_id")
    detected_objects = img_res["analysis_result"]["detected_objects"]
    detect_list = [{"name": obj["name_cn"], "confidence": obj["confidence"]} for obj in detected_objects]
    db_ok, record_id = model_add(result_img_url, user_id, detect_list)

    # 7. 查询治理方法
    disease_names = list(set(obj["name_cn"] for obj in detected_objects))
    treatments = get_disease_treatments(disease_names)

    return jsonify(
        {
            "success": True,
            "msg": f"检测成功：{img.filename}",
            "imgurl": result_img_url,
            "record_path": img_res["record_path"],
            "record_id": record_id if db_ok else None,
            "save_status": "ok" if db_ok else f"入库失败：{record_id}",
            "result_info": img_res["result_info"],
            "analysis_result": img_res["analysis_result"],
            "treatments": treatments,
        }
    )
# 多张图片并发检测
@app.route("/api/batch_upload", methods=["POST"])
@jwt_required()
def batch_upload():
    # 1. 接收多个文件
    files = request.files.getlist("files")
    if not files:
        return jsonify({"success": False, "msg": "未上传任何图片"})

    # 2. 校验每个文件
    allow = ["jpg", "png", "jpeg"]
    valid_files = []
    errors = []

    for idx, f in enumerate(files):
        if f.filename == "":
            errors.append({"index": idx, "filename": "空文件名", "error": "文件名为空"})
            continue
        suffix = f.filename.split(".")[-1].lower()
        if suffix not in allow:
            errors.append({
                "index": idx,
                "filename": f.filename,
                "error": f"格式不支持（仅支持 {allow}）"
            })
            continue
        valid_files.append(f)

    if not valid_files:
        return jsonify({
            "success": False,
            "msg": "没有有效文件",
            "total": len(files),
            "results": [],
            "errors": errors
        })

    # 3. 逐个检测（串行，避免 GPU 内存溢出）
    user_id = get_jwt().get("user_id")
    results = []
    for f in valid_files:
        try:
            # 3a. 时间戳重命名，避免文件名冲突
            ts = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            safe_name = secure_filename(f.filename)
            new_name = f"{ts}_{safe_name}"
            save_path = os.path.join(UPLOAD, new_name)
            f.save(save_path)

            # 3b. YOLO 检测
            img_res = detector.detect_image(save_path)

            if not img_res.get("success"):
                results.append({
                    "filename": f.filename,
                    "success": False,
                    "error": img_res.get("error", "检测失败")
                })
                continue

            # 3c. 拼接结果
            img_path = img_res["record_path"]
            real_filename = os.path.basename(img_path)
            result_img_url = f"{URL_RES}/{real_filename}"

            # 3d. 保存到数据库
            detected_objects = img_res["analysis_result"]["detected_objects"]
            detect_list = [{"name": obj["name_cn"], "confidence": obj["confidence"]} for obj in detected_objects]
            db_ok, record_id = model_add(result_img_url, user_id, detect_list)

            # 3e. 查询治理方法
            disease_names = list(set(obj["name_cn"] for obj in detected_objects))
            treatments = get_disease_treatments(disease_names)

            results.append({
                "filename": f.filename,
                "success": True,
                "imgurl": result_img_url,
                "record_path": img_res["record_path"],
                "record_id": record_id if db_ok else None,
                "save_status": "ok" if db_ok else f"入库失败：{record_id}",
                "result_info": img_res.get("result_info", ""),
                "analysis_result": img_res.get("analysis_result", {}),
                "treatments": treatments,
            })

        except Exception as e:
            results.append({
                "filename": f.filename,
                "success": False,
                "error": str(e)
            })

    # 4. 汇总返回
    success_count = sum(1 for r in results if r.get("success"))
    fail_count = len(results) - success_count

    return jsonify({
        "success": True,
        "msg": f"批量检测完成：成功 {success_count} 张，失败 {fail_count} 张",
        "total": len(valid_files),
        "success_count": success_count,
        "fail_count": fail_count,
        "results": results,
        "errors": errors  # 格式错误的文件
    })







# 最近检测记录
@app.route("/api/record", methods=["POST"])
@jwt_required()
def record():
    result = get_detect_records()
    return jsonify(
        {
            "success": True,
            "msg": result,
        }
    )


# 病虫害类型排行榜
@app.route("/api/sum", methods=["POST"])
@jwt_required()
def sum1():
    sum1 = final_disease_sum()
    return jsonify(
        {
            "success": True,
            "msg": sum1,
        }
    )


# 病虫害各自对比上周的变化
@app.route("/api/total", methods=["POST"])
@jwt_required()
def total():
    result = total_count()
    return jsonify({"success": True, "msg": result})


@app.route("/api/total_record", methods=["POST"])
@jwt_required()
def total_record():

    result = request.json.get("period")
    if result == "week":
        res = total_week_cnt()
        return jsonify({"success": True, "msg": res})
    elif result == "month":
        res = total_month_cnt()
        return jsonify({"success": True, "msg": res})
    else:
        res = total_year_cnt()
        return jsonify({"success": True, "msg": res})


# 查询前10条记录
@app.route("/api/all_record", methods=["POST"])
@jwt_required()
def allrecord():
    number = request.json.get("page")
    res = all_record(number)
    return jsonify({"success": True, "msg": res})


# 筛选信息查询
@app.route("/api/detectItem/list", methods=["POST"])
@jwt_required()
def detectItemList():
    data = request.json.get("info")
    print(data)
    res = detectitem(
        int(data.get("page")),
        filters={
            "startTime": data.get("startTime"),
            "endTime": data.get("endTime"),
            "disease_type": data.get("disease_type"),
            "item_audit_status": data.get("item_audit_status"),
            "keyword": data.get("keyword"),
        },
    )
    return jsonify({"success": True, "msg": res})



@app.route('/api/get_knowledge',methods=["POST"])
@jwt_required()
def get_knowledge():
           
    res =knowledge()
    return jsonify({"success": True, "msg": res})

# 更新详情信息
# 更新详情信息
@app.route("/api/detect/updateAudit", methods=["POST"])
@jwt_required()
def update_audit():
    data = request.get_json()
    # 提取前端参数，容错默认空
    item_id = data.get("itemId")
    record_id = data.get("recordId")
    final_disease_id = data.get("finalDiseaseId")
    final_result = data.get("finalResult")
    item_audit_status = data.get("itemAuditStatus")
    audit_remark = data.get("auditRemark", "")
    auditor_id = data.get("loginUserId")



    # 调用mysql封装函数
    ok, msg = update_audit_item_record(
        item_id, record_id, final_disease_id, final_result, item_audit_status, auditor_id, audit_remark
    )
    if ok:
        return jsonify({"success": True, "msg": msg})
    else:
        return jsonify({"success": False, "msg": "更新失败", "err": msg})


# 获取知识库列表
@app.route("/api/get_knowledge_item", methods=["POST"])
@jwt_required()
def get_knowledge_item():
    json_data = request.get_json()
    page = json_data.get("page")
    filters = {"name": json_data.get("name"), "type": json_data.get("type")}
    res = knowledge_item(page, filters)
    return jsonify({"success": True, "msg": res})

# 知识库添加
@app.route('/api/knowledge/add', methods=["POST"])
@jwt_required()
def knowledge_add():
    # 1. 判断前端有没有传图片，file是前端上传字段名
    if "file" not in request.files:
        return jsonify({"success": False, "msg": "未上传图片"})
    img = request.files["file"]
    # 2. 判断文件名为空的情况
    if img.filename == "":
        return jsonify({"success": False, "msg": "文件名为空"})

    # 3. 校验图片后缀格式
    suffix = img.filename.split(".")[-1].lower()
    allow = ["jpg", "png", "jpeg"]
    if suffix not in allow:
        return jsonify({"success": False, "msg": "文件格式不匹配，仅支持jpg/png/jpeg"})
        # 时间戳重命名防文件名冲突
    new_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S%f')}_{secure_filename(img.filename)}"
    new_name1 = f"{URL_REGEX}/{datetime.now().strftime('%Y%m%d_%H%M%S%f')}_{secure_filename(img.filename)}"
    save_path = os.path.join(UPLOAD_KNOWLEDGE, new_name)
    img.save(save_path)
    url = new_name1
    form_data = {"name": request.form.get("name"), "type": request.form.get("type"),"imgUrl":url,"symptom":request.form.get("symptom"),"treat":request.form.get("treat")}
    res =add_knowledge(form_data)
    return jsonify({"success": True, "msg": res})

#知识库更新
@app.route('/api/knowledge/update', methods=["POST"])
@jwt_required()
def knowledge_update():
    item_id = request.form.get("id")
    name = request.form.get("name")
    type = request.form.get("type")
    symptom = request.form.get("symptom")
    treat = request.form.get("treat")
    old_img_url = request.form.get("img_url", "")
    # 2. 图片处理：有新图就用新图，没新图就保留原图
    if "file" in request.files and request.files["file"].filename:
        img = request.files["file"]
        suffix = img.filename.split(".")[-1].lower()
        if suffix not in ["jpg", "png", "jpeg"]:
            return jsonify({"success": False, "msg": "文件格式不匹配"})
        new_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S%f')}_{secure_filename(img.filename)}"
        save_path = os.path.join(UPLOAD_KNOWLEDGE, new_name)
        img.save(save_path)
        img_url = f"{URL_REGEX}/{new_name}"
    else:
        img_url = old_img_url
        # 没换图就用原来的
    res =update_knowledge(name, type, img_url, symptom, treat, item_id)
    return jsonify({"success": True, "msg": res})

# #知识库单删除
@app.route('/api/knowledge/del',methods=["POST"])
@jwt_required()
def knowledge_del():
    del_id =request.json.get("id")
    res=del_knowledge(del_id)
    return jsonify({"success": True, "msg": res})



#知识库多条删除
@app.route('/api/knowledge/batch_del',methods=["POST"])
@jwt_required()
def knowledge_batch_del():
    id_list = request.json.get("ids",[])
    res =del_choose_knowledge(id_list)
    return jsonify({"success": True, "msg": res})


def delete_local_img(img_url: str):
    if not img_url or not isinstance(img_url, str):
        return True
        # 只处理本服务内部图片，外部网络图片不删除
    if not img_url.startswith(URL_REGEX):
        return True
        # 截取文件名
    filename = img_url.replace(URL_REGEX, "").lstrip("/")
    local_path = os.path.join(UPLOAD_KNOWLEDGE, filename)
    # 文件不存在直接放行
    if not os.path.exists(local_path):
        return True
    try:
        os.remove(local_path)
        print(f"成功删除本地图片：{local_path}")
        return True
    except PermissionError:
        print(f"图片被占用，删除失败：{local_path}")
        return False
    except Exception as e:
        print(f"文件删除异常：{local_path}，{str(e)}")
        return False

@app.route('/api/userlist',methods=["POST"])
@jwt_required()
def userlist():
    err = _check_admin()
    if err:
        return err
    page = int(request.json.get("page"))
    res =users(page)
    return jsonify({"success": True, "msg": res})
@app.route('/api/user/add',methods=["POST"])
@jwt_required()
def user_add():
    err = _check_admin()
    if err:
        return err
    res =useradd(request.json.get("username"),request.json.get("password"), request.json.get("phone"),request.json.get("role"))
    return jsonify({"success": True, "msg": res})

@app.route('/api/user/update',methods=["POST"])
@jwt_required()
def user_update():
    err = _check_admin()
    if err:
        return err
    res = userupdate(
        request.json.get("id"),
        request.json.get("username"),
        request.json.get("password"),
        request.json.get("phone"),
        request.json.get("role"),
    )
    return jsonify({"success": True, "msg": res})

@app.route('/api/user/delete',methods=["POST"])
@jwt_required()
def user_del():
    err = _check_admin()
    if err:
        return err
    res = userdel(request.json.get("id"))
    return jsonify({"success": True, "msg": res})


# 实时画面流接口
@app.route("/api/video_feed")
def video_feed():
    return Response(generate_mjpeg(), mimetype="multipart/x-mixed-replace; boundary=frame")


# 获取最新检测结构化JSON数据接口，Vue可以轮询拿病害信息
@app.route("/api/latest_result")
def latest_result():
    with lock:
        data = global_latest_analysis
    if data is None:
        return jsonify({"success": False, "msg": "暂无检测数据"})
    return jsonify({"success": True, "data": data})


# 查询实时检测开关状态（前端初始化时判断按钮应该显示"开启"还是"停止"）
@app.route("/api/rtsp/status", methods=["GET"])
def rtsp_status():
    running = False
    with lock:
        if _rtsp_thread is not None and getattr(_rtsp_thread, "running", False) and _rtsp_thread.thread.is_alive():
            running = True
    return jsonify({
        "success": True,
        "msg": {
            "running": running,
            "rtsp_url": RTSP_URL,
        }
    })


# 前端点击【开启实时检测】
@app.route("/api/rtsp/start", methods=["POST"])
@jwt_required()
def rtsp_start():
    global _rtsp_thread
    # 1. 已在运行则直接返回（防重复启动）
    if (
        _rtsp_thread is not None
        and getattr(_rtsp_thread, "running", False)
        and _rtsp_thread.thread.is_alive()
    ):
        return jsonify({"success": True, "msg": "实时检测已在运行，无需重复开启"})

    # 2. 上一个线程已停止 → 清理引用并清空遗留的最后一帧
    with lock:
        _m1.global_frame = None
        _m1.global_latest_analysis = None
    _rtsp_thread = None

    # 3. 启动新的采集 + 检测线程
    try:
        _rtsp_thread = RtspReadThread(RTSP_URL, detector)
        print("✅ RTSP 实时检测线程已启动（前端触发）")
        return jsonify({
            "success": True,
            "msg": "开启成功：正在连接摄像头并加载 YOLO 检测，1-3 秒后即可看到画面",
        })
    except Exception as e:
        _rtsp_thread = None
        err = str(e)
        print(f"❌ RTSP 线程启动失败（前端触发）：{err}")
        return jsonify({
            "success": False,
            "msg": f"开启失败：{err}",
            "tip": "请检查摄像头是否在线 / RTSP 地址是否正确 / 网络是否可达",
        })


# 前端点击【停止检测】
@app.route("/api/rtsp/stop", methods=["POST"])
@jwt_required()
def rtsp_stop():
    global _rtsp_thread
    # 1. 通知线程停止循环、释放摄像头
    if _rtsp_thread is not None:
        try:
            _rtsp_thread.stop()
        except Exception as e:
            print(f"⚠️  停止 RTSP 线程时出现非致命异常：{e}")

    # 2. 清空全局帧缓存 + 分析结果，让 MJPEG 占位图重新显示引导文字
    with lock:
        _m1.global_frame = None
        _m1.global_latest_analysis = None

    _rtsp_thread = None
    print("🛑 RTSP 实时检测线程已停止（前端触发）")
    return jsonify({"success": True, "msg": "已停止实时检测"})


# ===================== PTZ 云台控制 =====================

@app.route("/api/ptz/move", methods=["POST"])
@jwt_required()
def ptz_move():
    """
    云台方向控制
    body: {"direction": "up|down|left|right|zoom_in|zoom_out", "speed": 0.5}
    """
    data = request.get_json() or {}
    direction = data.get("direction", "")
    speed = float(data.get("speed", 0.5))

    ptz = _get_ptz()
    if ptz is None:
        return jsonify({"success": False, "msg": "PTZ 未连接，请在摄像头后台开启 ONVIF 服务"})

    action_map = {
        "up":       ptz.up,
        "down":     ptz.down,
        "left":     ptz.left,
        "right":    ptz.right,
        "zoom_in":  ptz.zoom_in,
        "zoom_out": ptz.zoom_out,
    }
    fn = action_map.get(direction)
    if fn is None:
        return jsonify({"success": False, "msg": f"未知方向：{direction}"})

    try:
        fn(speed=speed, timeout=0)
        return jsonify({"success": True, "msg": f"已发送 {direction} 指令"})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)})


@app.route("/api/ptz/stop", methods=["POST"])
@jwt_required()
def ptz_stop():
    """停止云台转动"""
    ptz = _get_ptz()
    if ptz is None:
        return jsonify({"success": False, "msg": "PTZ 未连接"})
    try:
        ptz.stop()
        return jsonify({"success": True, "msg": "已停止"})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)})


# ===================== 模型配置接口 =====================
@app.route("/api/get_model_config")
@jwt_required()
def api_get_model_config():
    """返回当前模型路径 + 阈值，供前端展示。优先返回实例变量（最准确）"""
    err = _check_admin()
    if err:
        return err
    return jsonify({
        "success": True,
        "msg": {
            "model_path": _m1.current_model_path or _m1.DEFAULT,
            "conf_thres": detector.conf_thres,
            "iou_thres": detector.iou_thres,
        }
    })


@app.route("/api/save_model_config", methods=["POST"])
@jwt_required()
def api_save_model_config():
    """前端切换模型 / 阈值 → 热加载新权重 + 清空检测状态"""
    err = _check_admin()
    if err:
        return err
    data = request.get_json() or {}
    new_path = data.get("model_path", "")
    new_conf = data.get("conf_thres")
    new_iou = data.get("iou_thres")

    # 1. 写入 JSON + 更新全局变量
    _m1.save_model_config(new_path, new_conf, new_iou)

    # 2. 判断是否需要重新加载模型（路径变化才重载，只改阈值直接赋值）
    need_reload = bool(new_path) and (new_path != detector.weights_path)

    if need_reload:
        try:
            detector.reload_model(new_path, conf_thres=new_conf, iou_thres=new_iou)
            print(f"✅ 模型热加载成功：{new_path}")
        except Exception as e:
            print(f"❌ 模型热加载失败：{e}")
            return jsonify({"success": False, "msg": f"模型加载失败：{e}"})
    else:
        # 只改阈值时，直接同步到实例（路径没变或路径为空）
        if new_conf is not None:
            detector.conf_thres = new_conf
        if new_iou is not None:
            detector.iou_thres = new_iou
        # 如果传了新路径但和当前相同，仍需更新 weights_path 记录
        if new_path and new_path == detector.weights_path:
            detector.weights_path = new_path

    # 3. 切换模型后清空全局帧 + 分析结果（MJPEG 自动切回占位图）
    with _m1.lock:
        _m1.global_frame = None
        _m1.global_latest_analysis = None

    return jsonify({"success": True, "msg": "模型配置已保存并热加载"})


@app.route("/api/upload_model", methods=["POST"])
@jwt_required()
def upload_model():
    """上传 .pt 权重文件，保存到 weights 目录，返回保存后的绝对路径"""
    err = _check_admin()
    if err:
        return err
    if "file" not in request.files:
        return jsonify({"success": False, "msg": "未上传文件"})

    f = request.files["file"]
    if not f.filename.endswith(".pt"):
        return jsonify({"success": False, "msg": "仅支持 .pt 权重文件"})

    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_name = secure_filename(f.filename)
    save_name = f"{ts}_{safe_name}"
    save_path = os.path.join(WEIGHTS_DIR, save_name)
    f.save(save_path)

    return jsonify({
        "success": True,
        "msg": "权重上传成功",
        "model_path": save_path
    })


if __name__ == "__main__":
    start_clean_timer()
    # ⚠️ 注意：RtspReadThread 不再在服务启动时自动开启，改为前端点击【开启实时检测】按钮后
    #         调用 POST /api/rtsp/start 按需启动（避免摄像头离线 / 无人使用时白白占用 GPU/带宽）
    app.run(host="127.0.0.1", port=8080)
