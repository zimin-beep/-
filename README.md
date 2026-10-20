[zimin.md](https://github.com/user-attachments/files/33723616/zimin.md)
# 病虫害管理系统 - 开发文档

## 1. 项目概述

本系统是一个基于 YOLOv8 的农作物病虫害检测与管理平台，提供图片检测、批量检测、RTSP 实时摄像头检测、检测记录审核、知识库管理、用户权限管理等功能。

**技术栈：**
- 前端：Vue 3 + Vite + Element Plus + Axios
- 后端：Flask + PyTorch + Ultralytics YOLO + PyMySQL
- 数据库：MySQL
- 摄像头：ONVIF PTZ 云台控制

---

## 2. 目录结构

### 2.1 后端目录（`/Users/mac/PycharmProjects/en/`）

```
en/
├── .gitignore                          # Git 忽略规则
├── pases/
│   ├── upload-demo/static/
│   │   ├── upload/                     # 用户上传原图（临时，定时清理）
│   │   └── knowledge/                  # 知识库图片
│   └── yolo1/
│       ├── mainyolo1.py                # 主入口：Flask 路由 + 业务逻辑
│       ├── modelyolo1.py               # YOLO 推理封装 + RTSP 多线程
│       ├── mysql.py                    # MySQL 数据库操作封装
│       ├── ptz_control.py              # ONVIF PTZ 云台控制
│       ├── clear_by_time.py            # 定时清理任务
│       ├── model_config.json           # 模型配置（路径/阈值/摄像头）
│       ├── pest_api.json               # 病虫害 API 数据
│       ├── weights/                    # 模型权重存放目录（.gitignore 忽略）
│       ├── images/tmp/                 # 临时预览图（.gitignore 忽略）
│       └── record/img/                 # 检测结果存档图（.gitignore 忽略）
```

### 2.2 前端目录（`/Users/mac/vscode/en/bingchonghaiguanlixitong/`）

```
bingchonghaiguanlixitong/
├── vite.config.js                      # Vite 构建配置 + 代理
├── index.html
├── package.json
└── src/
    ├── main.js                         # Vue 应用入口
    ├── App.vue                         # 根组件
    ├── router/index.js                 # 路由 + Axios 拦截器
    ├── login/
    │   ├── login.vue                   # 登录页面
    │   └── login.css                   # 登录页样式
    ├── components/Navbar/
    │   └── Navbar.vue                  # 顶部导航
    ├── views/
    │   ├── Overview/Overview.vue       # 数据概览
    │   ├── Detection/Detection.vue     # 病虫害检测
    │   ├── Record/Record.vue           # 检测记录
    │   └── Knowledge/Knowledge.vue     # 知识库管理
    ├── UserList/UserList.vue           # 用户管理（管理员）
    └── assets/image.ts                 # 图片资源
```

---

## 3. 后端架构

### 3.1 模块职责

| 模块 | 文件 | 职责 |
|------|------|------|
| 路由层 | `mainyolo1.py` | Flask 路由定义、JWT 认证、请求处理、业务编排 |
| 推理层 | `modelyolo1.py` | YOLO 模型加载/热加载、图片/视频推理、RTSP 多线程采集 |
| 数据层 | `mysql.py` | 数据库连接、CRUD 操作、审核事务 |
| 云台控制 | `ptz_control.py` | ONVIF SOAP 协议控制摄像头方向/变焦 |
| 定时任务 | `clear_by_time.py` | 每日凌晨 2 点清理过期图片 |

### 3.2 启动流程

```
mainyolo1.py 入口
  ├── load_model_config()        # 从 model_config.json 读取配置
  ├── YOLO1(weights_path, ...)  # 初始化 YOLO 检测器
  ├── start_clean_timer()        # 启动定时清理守护线程
  └── app.run(host, port)        # Flask 启动 (127.0.0.1:8080)
```

### 3.3 路由总览

#### 认证模块

| 路由 | 方法 | 认证 | 说明 |
|------|------|------|------|
| `/api/captcha` | GET | 无 | 获取验证码图片(base64) |
| `/api/login` | POST | 无 | 登录，返回 access_token + refresh_token |
| `/api/refresh_token` | POST | refresh_token | 刷新 access_token |

#### 图片检测

| 路由 | 方法 | 认证 | 说明 |
|------|------|------|------|
| `/api/upload` | POST | JWT | 单张图片检测 |
| `/api/batch_upload` | POST | JWT | 多张图片批量检测 |

#### 记录查询

| 路由 | 方法 | 认证 | 说明 |
|------|------|------|------|
| `/api/record` | POST | JWT | 最近 10 条检测记录 |
| `/api/sum` | POST | JWT | 病虫害类型排行榜 |
| `/api/total` | POST | JWT | 本周/上周对比统计 |
| `/api/total_record` | POST | JWT | 按周/月/年统计 |
| `/api/all_record` | POST | JWT | 分页查询历史记录 |
| `/api/detectItem/list` | POST | JWT | 条件筛选检测记录 |
| `/api/detect/updateAudit` | POST | JWT | 审核操作（双表事务） |

#### 知识库

| 路由 | 方法 | 认证 | 说明 |
|------|------|------|------|
| `/api/get_knowledge` | POST | JWT | 获取全部知识库 |
| `/api/get_knowledge_item` | POST | JWT | 分页+筛选知识库 |
| `/api/knowledge/add` | POST | JWT | 新增知识库 |
| `/api/knowledge/update` | POST | JWT | 编辑知识库 |
| `/api/knowledge/del` | POST | JWT | 单条删除 |
| `/api/knowledge/batch_del` | POST | JWT | 批量删除 |

#### 用户管理（管理员）

| 路由 | 方法 | 认证 | 说明 |
|------|------|------|------|
| `/api/userlist` | POST | JWT + 管理员 | 用户列表 |
| `/api/user/add` | POST | JWT + 管理员 | 新增用户 |
| `/api/user/update` | POST | JWT + 管理员 | 编辑用户 |
| `/api/user/delete` | POST | JWT + 管理员 | 删除用户 |

#### 实时摄像头

| 路由 | 方法 | 认证 | 说明 |
|------|------|------|------|
| `/api/video_feed` | GET | 无 | MJPEG 视频流 |
| `/api/latest_result` | GET | 无 | 最新检测结果 JSON |
| `/api/rtsp/status` | GET | 无 | 检测开关状态 |
| `/api/rtsp/start` | POST | JWT | 开启实时检测 |
| `/api/rtsp/stop` | POST | JWT | 停止实时检测 |
| `/api/ptz/move` | POST | JWT | 云台方向控制 |
| `/api/ptz/stop` | POST | JWT | 停止云台转动 |

#### 模型配置（管理员）

| 路由 | 方法 | 认证 | 说明 |
|------|------|------|------|
| `/api/get_model_config` | GET | JWT + 管理员 | 获取当前配置 |
| `/api/save_model_config` | POST | JWT + 管理员 | 保存配置+热加载 |
| `/api/upload_model` | POST | JWT + 管理员 | 上传 .pt 权重 |

#### 静态资源

| 路由 | 方法 | 说明 |
|------|------|------|
| `/pases/yolo1/record/img/<filename>` | GET | 检测结果图访问 |
| `/pases/upload-demo/static/knowledge/<filename>` | GET | 知识库图片访问 |

---

## 4. 核心模块详解

### 4.1 YOLO 推理（modelyolo1.py）

#### 类 `YOLO1`

```python
class YOLO1:
    NAME_MAP = { ... }  # 英文病害名 → 中文映射

    def __init__(self, weights_path, conf_thres, iou_thres)
    def load_model(self)           # 自动选择 CUDA/MPS/CPU
    def reload_model(self, ...)    # 热加载新权重
    def detect_image(self, image_path) -> dict   # 单张图片检测
    def detect_frame(self, frame) -> tuple       # 实时帧检测（ByteTrack 跟踪）
```

**关键参数：**
- `imgsz=800`：推理尺寸必须与训练一致（不可改为 640）
- `conf_thres`：默认 0.25，前端可动态调整
- `iou_thres`：默认 0.45
- `persist=True`：跨帧跟踪状态保持

**`detect_image` 返回结构：**

```json
{
  "success": true,
  "result_image": "临时预览图路径",
  "result_info": "枯萎病:2个\n褐斑病:1个\n",
  "record_path": "存档图路径",
  "analysis_result": {
    "detected_objects": [...],
    "summary": {
      "total": 3,
      "avg_confidence": 0.85,
      "class_summary": {...},
      "level_distribution": {...}
    }
  }
}
```

#### 多线程 RTSP 架构

```
RtspReadThread
  ├── _capture_loop()   采集线程：读 RTSP → 丢弃旧帧 → 交付最新帧
  ├── _infer_loop()     推理线程：取最新帧 → YOLO 推理 → 更新全局帧
  └── stop()            停止：先 running=False → join 线程 → 释放摄像头
```

**全局共享变量：**
- `global_frame`：最新带框帧（MJPEG 推流用）
- `global_latest_analysis`：最新检测结果 JSON
- `_cached_jpeg`：预编码 JPEG 缓存（避免多连接重复编码）
- `frame_ready`：Condition 变量，帧就绪时唤醒推流线程

### 4.2 数据库设计（mysql.py）

#### 数据表

| 表名 | 说明 |
|------|------|
| `users` | 用户表（user_id, username, password, phone, role） |
| `detect_record` | 检测主记录（id, image_url, detect_time, user_id, auditor_id, audit_time, audit_remark） |
| `detect_record_item` | 检测明细（item_id, record_id, disease_name, confidence, item_audit_status, final_result, final_disease_id, disease_type） |
| `disease_knowledge` | 知识库（id, disease_name, symptom, treatment, disease_type, example_url） |

#### 审核状态

| 值 | 状态 |
|----|------|
| 0 | 待确认（旧数据，已迁移为 1） |
| 1 | 待确认 |
| 2 | 已确认（置信度 > 0.8 自动设置） |
| 3 | 误报 |
| 4 | 治理中 |
| 5 | 治理完成 |

#### 核心函数

```python
query_one(sql, params)       # 单行查询
query(sql, params)           # 多行查询
execute(sql, params)         # 增删改

get_detect_records(limit)    # 检测记录列表（含审核状态汇总）
final_disease_sum()          # 病虫害数量统计
total_count()                # 本周/上周对比
total_year_cnt()             # 年度统计
total_month_cnt()            # 月度统计
total_week_cnt()             # 周度统计
all_record(page)             # 历史记录分页
detectitem(page, filters)    # 条件筛选
knowledge()                  # 知识库全量
knowledge_item(page, filters) # 知识库分页筛选
update_audit_item_record(...)  # 审核操作（双表事务）
```

### 4.3 PTZ 云台控制（ptz_control.py）

基于 ONVIF 协议的纯 `requests + SOAP/XML` 实现，支持大华/乐橙/海康等支持 ONVIF 的摄像头。

```python
PTZController(ip, user, password)
  ├── move(pan, tilt, zoom, timeout)   # 连续移动
  ├── stop()                           # 停止
  ├── up/down/left/right(speed, timeout)
  └── zoom_in/zoom_out(speed, timeout)
```

懒加载模式：首次调用接口时才连接，PTZ 配置变更后自动重置重连。

### 4.4 定时清理（clear_by_time.py）

- 上传目录：保留 1 天
- 结果图目录：保留 30 天
- 执行时间：每日凌晨 02:00
- 守护线程：`daemon=True`，主程序关闭自动结束

---

## 5. 前端架构

### 5.1 路由

| 路径 | 组件 | 说明 | 权限 |
|------|------|------|------|
| `/` | - | 重定向到 `/login` | - |
| `/login` | login.vue | 登录页 | 公开 |
| `/overview` | Overview.vue | 数据概览 | 登录 |
| `/detection` | Detection.vue | 病虫害检测 | 登录 |
| `/record` | Record.vue | 检测记录 | 登录 |
| `/knowledge` | Knowledge.vue | 知识库管理 | 登录 |
| `/userlist` | UserList.vue | 用户管理 | 管理员 |

### 5.2 Axios 拦截器

- **请求拦截**：自动携带 `access_token`（登录/刷新接口除外）
- **响应拦截**：401 时自动刷新 token，刷新失败跳转登录页；402 直接跳登录
- **请求队列**：刷新期间并发请求排队，刷新后统一重发

### 5.3 页面功能

| 页面 | 功能 |
|------|------|
| 登录页 | 验证码登录，支持点击刷新验证码 |
| 数据概览 | 病害/虫害统计卡片、趋势图表（周/月/年）、TOP5 排行 |
| 病虫害检测 | 单张/批量检测、实时摄像头、模型配置、结果展示+治理方法 |
| 检测记录 | 时间/类型/状态/关键词筛选、分页、审核操作弹窗 |
| 知识库管理 | 列表/搜索/分页、新增/编辑/删除、图片上传 |
| 用户管理 | 用户 CRUD（仅管理员可见） |

### 5.4 Vite 代理配置

```javascript
proxy: {
  '/api':   { target: 'http://127.0.0.1:8080', changeOrigin: true, ws: true },
  '/pases': { target: 'http://127.0.0.1:8080', changeOrigin: true }
}
```

---

## 6. 认证机制

### 6.1 JWT 双 Token

- **access_token**：有效期 1 小时，业务接口认证
- **refresh_token**：有效期 7 天，无感续期
- **Claims**：`{ username, role, user_id }`

### 6.2 管理员校验

```python
def _check_admin():
    payload = get_jwt()
    role = payload.get("role", "")
    if role != "系统管理员":
        return jsonify({"success": False, "msg": "权限不足"}), 403
```

用户管理、模型配置等接口在路由层调用 `_check_admin()` 进行二次校验。

### 6.3 验证码

- 4 位随机字符（排除 O/0/I/1）
- PIL 生成图片，跨平台字体自适应
- 5 分钟过期，一次性使用
- 存储：内存字典 `_captcha_store`

---

## 7. 配置文件

### 7.1 model_config.json

```json
{
  "model_path": "/path/to/best.pt",
  "conf_thres": 0.25,
  "iou_thres": 0.45,
  "rtsp_url": "rtsp://...",
  "ptz_ip": "192.168.1.79",
  "ptz_user": "admin",
  "ptz_pass": "password"
}
```

### 7.2 .gitignore 规则

- `*.pt`：模型权重文件（超 Gitee 100MB 限制）
- `.idea/`、`.vscode/`：IDE 配置
- `__pycache__/`、`*.pyc`：Python 缓存
- `pases/yolo1/record/img/`：检测结果图
- `pases/yolo1/images/tmp/`：临时预览图
- `pases/upload-demo/static/upload/`：用户上传原图

---

## 8. 开发约定

### 8.1 后端

- 图片 URL 使用相对路径，不硬编码后端地址
- 审核操作从 JWT claims 获取 `user_id`，不依赖前端传值
- 数据库写入使用 `NOW()` 记录时间
- 置信度 > 0.8 自动标记为"已确认"(status=2)，<=0.8 为"待确认"(status=1)
- RTSP 采集与 YOLO 推理必须分线程，队列解耦
- 停止检测时先 `running=False` → `join` 线程 → 释放摄像头
- 推理尺寸 `imgsz` 必须与训练尺寸一致（800）

### 8.2 前端

- 图片 URL 使用相对路径，Vite 代理转发
- 登录/刷新接口不携带 access_token
- 管理员页面通过 `meta.requiresAdmin` + `localStorage` 校验
- 页面标题通过路由 `meta.title` 动态设置

---

## 9. 部署

### 9.1 开发环境

```bash
# 后端
cd /Users/mac/PycharmProjects/en/pases/yolo1
python mainyolo1.py    # 启动在 127.0.0.1:8080

# 前端
cd /Users/mac/vscode/en/bingchonghaiguanlixitong
npm install
npm run dev            # 启动在 127.0.0.1:5173
```

### 9.2 生产部署

**推荐架构：Nginx 静态托管 + 反向代理 Flask**

```
浏览器 → Nginx:80
            ├── / → 静态文件 (dist/)
            ├── /api/ → 反向代理 → Flask:8080
            └── /pases/ → 反向代理 → Flask:8080
```

**后端生产服务器：**
```bash
pip install waitress
waitress-serve --host=0.0.0.0 --port=8080 mainyolo1:app
```

**前端构建：**
```bash
npm run build          # 输出到 dist/
```

**Nginx 配置要点：**
- `location /` 指向 `dist/` 目录
- `location /api` 和 `location /pases` 反向代理到 Flask
- MJPEG 流需设置 `proxy_buffering off`

---

## 10. 使用方式

### 10.1 环境准备

#### 后端依赖

```bash
cd /Users/mac/PycharmProjects/en
pip install -r requirements.txt
```

**核心依赖：**

| 包名 | 用途 |
|------|------|
| `flask` | Web 框架 |
| `flask-jwt-extended` | JWT 认证 |
| `ultralytics` | YOLOv8 推理 |
| `torch` + `torchvision` | 深度学习后端 |
| `opencv-python` | 图像处理 / RTSP 读取 |
| `pymysql` | MySQL 驱动 |
| `pillow` (PIL) | 验证码图片生成 |
| `requests` | ONVIF SOAP 通信 |
| `schedule` | 定时任务调度 |

#### 前端依赖

```bash
cd /Users/mac/vscode/en/bingchonghaiguanlixitong
npm install
```

**核心依赖：** `vue@3`、`vue-router`、`axios`、`element-plus`、`@vitejs/plugin-vue`

#### 数据库初始化

1. 创建 MySQL 数据库 `pases`（utf8mb4 编码）
2. 创建 4 张数据表：`users`、`detect_record`、`detect_record_item`、`disease_knowledge`
3. 修改 [mysql.py](file:///Users/mac/PycharmProjects/en/pases/yolo1/mysql.py) 中的 `db_config`，填入本地数据库连接信息：

```python
db_config = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "你的密码",
    "database": "pases",
    "charset": "utf8mb4",
}
```

4. 初始化一个管理员账号：

```sql
INSERT INTO users (username, password, phone, role) VALUES ('admin', '123456', '13800000000', '1');
-- role=1 为系统管理员，role=0 为普通用户
```

### 10.2 配置模型

编辑 [model_config.json](file:///Users/mac/PycharmProjects/en/pases/yolo1/model_config.json)：

```json
{
  "model_path": "/你的路径/best.pt",
  "conf_thres": 0.25,
  "iou_thres": 0.45,
  "rtsp_url": "",
  "ptz_ip": "",
  "ptz_user": "",
  "ptz_pass": ""
}
```

- `model_path`：YOLO 权重文件路径，留空则使用 `DEFAULT` 默认权重
- `conf_thres`：置信度阈值，建议 0.25（过低会漏检，过高会误检）
- `iou_thres`：NMS 阈值，默认 0.45
- `rtsp_url`：摄像头 RTSP 地址（不需要实时检测可留空）
- `ptz_*`：ONVIF 云台认证信息（无摄像头可留空）

也可以在系统中通过 **检测页 → 模型配置 Tab** 动态修改，支持热加载。

### 10.3 启动系统

#### 启动后端

```bash
cd /Users/mac/PycharmProjects/en/pases/yolo1
python mainyolo1.py
```

启动成功标志：

```
项目工程根目录：/Users/mac/PycharmProjects/en
[YOLO] 推理设备: mps
✅ 模型已加载
图片定时清理线程已启动
 * Running on http://127.0.0.1:8080
```

#### 启动前端

```bash
cd /Users/mac/vscode/en/bingchonghaiguanlixitong
npm run dev
```

启动成功后访问 `http://127.0.0.1:5173`，自动跳转到登录页。

### 10.4 功能操作指南

#### 登录

1. 输入用户名和密码（初始管理员：admin / 123456）
2. 输入验证码（点击图片可刷新）
3. 登录成功后自动跳转到数据概览页

#### 图片检测

1. 进入 **病虫害检测** 页面
2. 选择 **图片检测** Tab
3. 点击上传区域选择图片（支持 jpg/png/jpeg/webp）
4. 点击 **开始检测**，等待 YOLO 推理完成
5. 查看检测结果：标注图、目标列表、置信度评级、治理方法
6. 检测结果自动入库，置信度 > 0.8 自动标记为"已确认"

#### 批量检测

1. 在检测页选择 **批量检测** Tab
2. 选择多张图片上传
3. 系统逐张推理（串行，避免 GPU 溢出）
4. 查看每张图片的检测结果和汇总统计

#### 实时摄像头检测

1. 先在 **模型配置** 中填写 RTSP 地址
2. 切换到 **实时摄像头** Tab
3. 点击 **开启实时检测**，1-3 秒后显示画面
4. 查看实时检测结果（右侧面板展示当前帧病害信息）
5. 使用云台控制按钮可调整摄像头方向（需摄像头支持 ONVIF）
6. 点击 **停止检测** 关闭

#### 检测记录审核

1. 进入 **检测记录** 页面
2. 使用筛选条件（时间范围、病虫害类型、审核状态、关键词）查找记录
3. 点击记录行的 **审核** 按钮
4. 在弹窗中：确认/修改病害名称、设置审核状态、填写备注
5. 审核状态可选：待确认、已确认、误报、治理中、治理完成

#### 知识库管理

1. 进入 **知识库管理** 页面
2. 按名称或类型（病害/虫害）搜索
3. **新增**：填写名称、类型、症状描述、治理方法、上传示例图片
4. **编辑**：修改信息，可选择更换图片
5. **删除**：支持单条和批量删除

#### 用户管理（仅管理员）

1. 进入 **用户管理** 页面（非管理员自动拦截）
2. 新增用户：用户名、密码、手机号、角色（管理员/普通用户）
3. 编辑/删除已有用户

#### 模型配置（仅管理员）

1. 在检测页选择 **模型配置** Tab
2. **上传模型**：上传 `.pt` 权重文件（最大 500MB）
3. **切换模型**：选择已上传的权重，点击保存
4. **调整阈值**：修改置信度/NMS 阈值
5. **摄像头配置**：填写 RTSP 地址、PTZ 认证信息
6. 保存后自动热加载，无需重启服务

### 10.5 常见问题排查

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 登录提示"验证码已过期" | 验证码 5 分钟有效 | 点击验证码图片刷新 |
| 检测结果为空 | 未检测到目标或置信度阈值过高 | 降低 conf_thres（建议 0.25） |
| 实时检测画面卡住 | RTSP 连接失败或网络延迟 | 检查 RTSP 地址和网络连通性 |
| 实时检测闪退 | 摄像头资源被并发访问 | 确保停止检测后再重新开启 |
| 云台控制无响应 | 摄像头未开启 ONVIF | 登录摄像头后台开启 ONVIF 服务 |
| 图片上传失败 | 文件格式不支持 | 仅支持 jpg/png/jpeg/webp |
| 模型热加载失败 | 权重文件路径错误或格式不兼容 | 确认 `.pt` 文件路径正确且为 YOLOv8 格式 |
| 登录后 token 过快过期 | 系统时间不同步 | 同步系统时间 |
| 403 权限不足 | 普通用户访问管理员接口 | 使用管理员账号登录 |
