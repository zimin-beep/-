import os
import time
import threading
import schedule
from pathlib import Path


def clean_folder_by_time(folder_path: str, keep_days: int = 7):
    """
    删除文件夹内 N 天之前的图片文件
    :param folder_path: 目标文件夹路径
    :param keep_days: 保留最近几天的文件，超过自动删除
    """
    # 允许清理的图片后缀
    img_suffix = {".jpg", ".jpeg", ".png"}
    folder = Path(folder_path)
    if not folder.exists():
        return

    now = time.time()
    expire_sec = keep_days * 24 * 60 * 60  # 过期总秒数

    for file in folder.iterdir():
        # 只处理文件，跳过子文件夹
        if not file.is_file():
            continue
        if file.suffix.lower() not in img_suffix:
            continue
        # Windows: st_ctime=创建时间；Linux: st_ctime=修改时间
        create_time = file.stat().st_ctime
        if now - create_time > expire_sec:
            try:
                os.remove(file)
                print(f"【定时清理】已删除过期文件: {file.name}")
            except Exception as e:
                print(f"【定时清理】删除失败 {file.name}: {e}")


# ---------------------- 定时任务配置区 ----------------------
def _resolve_paths():
    """
    动态解析上传 / 结果图目录，与 mainyolo1.py 保持一致
    避免硬编码相对路径出错（upload_demo → upload-demo 中划线问题等）
    """
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))   # .../pases/yolo1
    project_root = os.path.dirname(os.path.dirname(script_dir))  # .../demo
    upload_dir = os.path.join(project_root, "pases", "upload-demo", "static", "upload")
    result_dir = os.path.join(script_dir, "record", "img")
    return upload_dir, result_dir


def clean_job():
    """定时执行的清理任务，按需修改文件夹与保留天数"""
    upload_dir, result_dir = _resolve_paths()
    # 1.临时预览图：upload 只保留1天
    clean_folder_by_time(upload_dir, keep_days=1)
    # 2.历史存档图：record/img 保留30天
    clean_folder_by_time(result_dir, keep_days=30)
    # 可继续添加其他文件夹
    # clean_folder_by_time("你的文件夹路径", 保留天数)


def run_schedule_loop():
    """定时循环守护线程，后台持续运行定时任务"""
    # 设置：每天凌晨 02:00 自动执行一次清理
    schedule.every().day.at("02:00").do(clean_job)
    # 无限循环检测定时任务
    while True:
        schedule.run_pending()
        time.sleep(60)  # 60秒检测一次任务


# 程序入口启动定时线程
def start_clean_timer():
    # daemon=True 守护线程：主程序关闭，定时任务自动结束
    timer_thread = threading.Thread(target=run_schedule_loop, daemon=True)
    timer_thread.start()
    print("图片定时清理线程已启动，每日凌晨2点自动清理")
