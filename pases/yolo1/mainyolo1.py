import os
from flask import Flask, request, jsonify, send_from_directory
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
from pases.yolo1.modelyolo1 import YOLO1
from mysql import *
from clear_by_time import start_clean_timer

app = Flask(__name__)
CORS(app)
jwt = JWTManager(app)
detector = YOLO1()

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




# @jwt.expired_token_loader   token合法,但是过期了
# @jwt_required() 给这个接口加上一个权限,表示访问这个接口必须带有有效的token
#


@app.route("/api/login", methods=["POST"])
def login():
    username = request.json.get("username")
    password = request.json.get("password")
    if not username or not password:
        return jsonify({"success": False, "msg": "账号或密码不能为空"}), 403

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
    return jsonify(
        {
            "success": True,
            "msg": f"检测成功：{img.filename}",
            "imgurl": result_img_url,
            "record_path": img_res["record_path"],
            "result_info": img_res["result_info"],
            "analysis_result": img_res["analysis_result"],
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

            results.append({
                "filename": f.filename,
                "success": True,
                "imgurl": result_img_url,
                "record_path": img_res["record_path"],
                "result_info": img_res.get("result_info", ""),
                "analysis_result": img_res.get("analysis_result", {})
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
    page = int(request.json.get("page"))
    res =users(page)
    return jsonify({"success": True, "msg": res})
@app.route('/api/user/add',methods=["POST"])
@jwt_required()
def user_add():
    res =useradd(request.json.get("username"),request.json.get("password"), request.json.get("phone"),request.json.get("role"))
    return jsonify({"success": True, "msg": res})

@app.route('/api/user/update',methods=["POST"])
@jwt_required()
def user_update():
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
    res = userdel(request.json.get("id"))
    return jsonify({"success": True, "msg": res})





if __name__ == "__main__":
    start_clean_timer()
    app.run(host="127.0.0.1", port=8080)
