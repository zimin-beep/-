import pymysql

config_create_db = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "584521",
    "charset": "utf8mb4",
}

# 创建数据库
with pymysql.connect(**config_create_db) as conn:
    with conn.cursor() as cur1:
        sql = "CREATE DATABASE IF NOT EXISTS pases DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
        cur1.execute(sql)
        print("数据库创建完成")

db_config = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "584521",
    "database": "pases",
    "charset": "utf8mb4",
}

create_table_sql_list = [
# users 用户表
"""
CREATE TABLE IF NOT EXISTS `users` (
  `user_id` INT NOT NULL AUTO_INCREMENT COMMENT '用户唯一ID',
  `username` VARCHAR(50) NOT NULL COMMENT '登录账号',
  `password` VARCHAR(255) NOT NULL COMMENT '加密密码',
  `phone` VARCHAR(20) DEFAULT NULL COMMENT '手机号',
  `role` VARCHAR(20) NOT NULL COMMENT '1=admin管理员，0=普通用户',
  `create_time` DATETIME DEFAULT NULL COMMENT '创建时间',
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
""",

# detect_record 检测主记录表
"""
CREATE TABLE IF NOT EXISTS `detect_record` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '检测主记录ID',
  `image_url` VARCHAR(255) NOT NULL COMMENT '图片存储地址',
  `auditor_id` INT DEFAULT NULL COMMENT '审核人ID，关联users.user_id',
  `audit_time` DATETIME DEFAULT NULL COMMENT '审核时间',
  `audit_remark` VARCHAR(255) DEFAULT NULL COMMENT '审核备注',
  `detect_time` DATETIME DEFAULT NULL COMMENT '检测时间',
  `user_id` INT DEFAULT NULL COMMENT '上传用户ID',
  `update_time` DATETIME DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='检测主记录表';
""",

# detect_record_item 检测明细子表
"""
CREATE TABLE IF NOT EXISTS `detect_record_item` (
  `item_id` INT NOT NULL AUTO_INCREMENT COMMENT '明细主键',
  `record_id` INT NOT NULL COMMENT '关联 detect_record.id',
  `disease_id` INT NOT NULL COMMENT '识别病害ID',
  `disease_name` VARCHAR(100) NOT NULL COMMENT '冗余：YOLO识别病害名',
  `confidence` DECIMAL(5,4) NOT NULL COMMENT '置信度',
  `item_audit_status` TINYINT NOT NULL COMMENT '0-无需审核 1-待确认 2-已确认 3-误报 4-治理中 5-治',
  `final_disease_id` INT DEFAULT NULL COMMENT '人工确认病害ID',
  `final_result` VARCHAR(100) DEFAULT NULL COMMENT '冗余：人工确认病害名',
  `update_time` DATETIME DEFAULT NULL,
  `disease_type` TINYINT DEFAULT NULL COMMENT '0-病害 1-虫害',
  PRIMARY KEY (`item_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='检测明细子表';
""",

# disease_knowledge 病害知识库
"""
CREATE TABLE IF NOT EXISTS `disease_knowledge` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '病害ID',
  `disease_name` VARCHAR(100) NOT NULL COMMENT '病虫害名称（与YOLO类别严格一致）',
  `symptom` TEXT DEFAULT NULL COMMENT '典型症状',
  `treatment` TEXT DEFAULT NULL COMMENT '治理处理方案',
  `create_time` DATETIME DEFAULT NULL COMMENT '录入时间',
  `update_time` DATETIME DEFAULT NULL COMMENT '更新时间',
  `disease_type` TINYINT NOT NULL COMMENT '0-病害 1-虫害',
  `example_url` VARCHAR(255) NOT NULL COMMENT '样例实物图片',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='病害知识库';
"""
]

try:
    with pymysql.connect(**db_config) as conn:
        with conn.cursor() as cur:
            for sql in create_table_sql_list:
                sql = sql.strip()
                if not sql:
                    continue
                cur.execute(sql)
        conn.commit()
    print("✅ 数据表创建成功")
except Exception as e:
    print(f"❌异常：{e}")
    raise
