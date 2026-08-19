import pymysql

config_create_db = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "584521",
    "charset": "utf8mb4",
}
# 使用with自动关闭连接
# 创建数据库表
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


create_table_sql_list = ["""
    CREATE TABLE IF NOT EXISTS `users` (
      `user_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户唯一 ID',
      `username` VARCHAR(50) NOT NULL COMMENT '登录账号',
      `password` VARCHAR(255) NOT NULL COMMENT '加密密码',
      `phone` VARCHAR(20) DEFAULT NULL COMMENT '手机号',
      `role` VARCHAR(20) NOT NULL COMMENT '1=admin管理员，0=普通用户',
      `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
      PRIMARY KEY (`user_id`),
      UNIQUE KEY `uk_username` (`username`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统用户表';
    """,

    # 2. disease_knowledge 病虫害知识库
    """
    CREATE TABLE IF NOT EXISTS `disease_knowledge` (
        `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '病害ID',
        `disease_name` VARCHAR(100) NOT NULL COMMENT '病虫害名称（与YOLO类别严格一致）',
        `symptom` TEXT COMMENT '典型症状',
        `treatment` TEXT COMMENT '治理处理方案',
        `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '录入时间',
        `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
        PRIMARY KEY (`id`),
        UNIQUE KEY `uk_disease_name` (`disease_name`)
        ALTER TABLE disease_knowledge
ADD COLUMN disease_type TINYINT NOT NULL DEFAULT 0 COMMENT '0-病害 1-虫害';
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='病虫害知识库';
    """,

    # 3. detect_record 检测主表
    """
    CREATE TABLE IF NOT EXISTS `detect_record` (
      `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '检测主记录ID',
      `image_url` VARCHAR(255) NOT NULL COMMENT '图片存储地址',
      `audit_status` TINYINT NOT NULL DEFAULT 0 COMMENT '0-未审核 1-部分审核 2-已审核',
      `auditor_id` INT UNSIGNED DEFAULT NULL COMMENT '审核人ID，关联users.user_id',
      `audit_time` DATETIME DEFAULT NULL COMMENT '审核时间',
      `audit_remark` VARCHAR(255) DEFAULT NULL COMMENT '审核备注',
      `detect_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '检测时间',
      `user_id` INT UNSIGNED DEFAULT NULL COMMENT '上传用户ID',
      `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      PRIMARY KEY (`id`),
      INDEX idx_user_detect_time (`user_id`, `detect_time`),
      INDEX idx_audit_status (`audit_status`),
      CONSTRAINT fk_record_user FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE SET NULL,
      CONSTRAINT fk_record_auditor FOREIGN KEY (`auditor_id`) REFERENCES `users`(`user_id`) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='检测主记录表';
    """,

    # 4. detect_record_item 明细子表
    """
    CREATE TABLE IF NOT EXISTS `detect_record_item` (
      `item_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '明细主键',
      `record_id` INT UNSIGNED NOT NULL COMMENT '关联 detect_record.id',
      `disease_id` INT UNSIGNED NOT NULL COMMENT '识别病害ID',
      `disease_name` VARCHAR(100) NOT NULL COMMENT '冗余：YOLO识别病害名',
      `confidence` DECIMAL(5,4) NOT NULL CHECK (confidence BETWEEN 0 AND 1) COMMENT '置信度',
      `item_audit_status` TINYINT NOT NULL DEFAULT 0 COMMENT '0-无需审核 1-待审 2-已审',
      `final_disease_id` INT UNSIGNED DEFAULT NULL COMMENT '人工确认病害ID',
      `final_result` VARCHAR(100) DEFAULT NULL COMMENT '冗余：人工确认病害名',
      `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      PRIMARY KEY (`item_id`),
      INDEX idx_record_id (`record_id`),
      INDEX idx_disease_id (`disease_id`),
      CONSTRAINT fk_item_record FOREIGN KEY (`record_id`) REFERENCES `detect_record`(`id`) ON DELETE CASCADE,
      CONSTRAINT fk_item_disease FOREIGN KEY (`disease_id`) REFERENCES `disease_knowledge`(`id`),
      CONSTRAINT fk_item_final_disease FOREIGN KEY (`final_disease_id`) REFERENCES `disease_knowledge`(`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='检测识别明细表';
    """]
with pymysql.connect(**db_config) as conn:
    with conn.cursor() as cur:
        for sql in create_table_sql_list:
            sql =sql.strip()
            if not sql:
                continue
            cur.execute(sql)
        conn.commit()
        print("数据表创建成功")