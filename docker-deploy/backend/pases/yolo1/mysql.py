import pymysql

from pymysql.cursors import DictCursor






db_config = {
    "host": "mysql",  # Docker 部署：使用 docker-compose 中的 MySQL 服务名
    "port": 3306,
    "user": "root",
    "password": "584521",
    "database": "pases",
    "charset": "utf8mb4",
}


# 查询单行函数
def query_one(sql, params=None):
    params = params or ()
    with pymysql.connect(**db_config) as conn:
        with conn.cursor(DictCursor) as cur:
            cur.execute(sql, params)
            return cur.fetchone()


# 多行查询
def query(sql, params=None):
    """
    查询语句 select
    :param sql: 查询sql
    :param params: 参数元组，防止sql注入
    :return: 全部查询结果 tuple
    """
    params = params or ()
    with pymysql.connect(**db_config) as conn:
        with conn.cursor(DictCursor) as cur:
            cur.execute(sql, params)
            return cur.fetchall()


def execute(sql, params=None):
    """
    执行增删改: insert / update / delete
    返回受影响行数
    """
    params = params or ()
    with pymysql.connect(**db_config) as conn:
        with conn.cursor(DictCursor) as cur:
            cur.execute(sql, params)
            conn.commit()
            return cur.rowcount


def get_detect_records(limit=10):
    sql = """
  SELECT
    dr.id AS record_id,
    dr.image_url,
    -- 北京时间格式化
    DATE_FORMAT(CONVERT_TZ(dr.detect_time, '+00:00','+08:00'), '%%Y-%%m-%%d %%H:%%i:%%s') AS detect_time,
    DATE_FORMAT(CONVERT_TZ(dr.audit_time, '+00:00','+08:00'), '%%Y-%%m-%%d %%H:%%i:%%s') AS audit_time,
    -- 上传用户、审核用户
    u_upload.username AS upload_user,
    u_audit.username AS auditor,
    dr.audit_remark,
    -- 拼接本条记录所有病害结果：人工结果优先
    GROUP_CONCAT(
        DISTINCT CONCAT(
            IF(dri.final_result IS NOT NULL AND dri.final_result <> '', dri.final_result, dri.disease_name),
            '(置信度:', ROUND(dri.confidence, 3), ')'
        )
        SEPARATOR '、'
    ) AS all_detect_result,
    -- 明细整体审核状态汇总展示
    GROUP_CONCAT(
        DISTINCT CONCAT(
            '条目', dri.item_id,
            ':',
            CASE dri.item_audit_status
                WHEN 0 THEN '待确认'
                WHEN 1 THEN '待确认'
                WHEN 2 THEN '已确认'
                WHEN 3 THEN '误报'
                WHEN 4 THEN '治理中'
                WHEN 5 THEN '治理完成'
            END
        ) SEPARATOR ' | '
    ) AS item_audit_detail,
    -- 整条记录综合审核状态（推荐用主表audit_status）
    
FROM detect_record dr
-- 上传人关联
LEFT JOIN users u_upload ON dr.user_id = u_upload.user_id
-- 审核人关联
LEFT JOIN users u_audit ON dr.auditor_id = u_audit.user_id
-- 关联明细条目
LEFT JOIN detect_record_item dri ON dr.id = dri.record_id
-- 按记录分组
GROUP BY dr.id
-- 最新记录在前
ORDER BY dr.detect_time DESC
-- 分页占位符
LIMIT %s, 10;

      
      
      
    """
    params = (limit,)
    with pymysql.connect(**db_config) as conn:
        with conn.cursor(DictCursor) as cur:
            cur.execute(sql, params)
            return cur.fetchall()


# 病虫害的数量合计
def final_disease_sum():
    sql = """
    SELECT
    dk.disease_name AS disease_name,
    COUNT(*) AS total
FROM detect_record_item dri
JOIN disease_knowledge dk ON dri.final_disease_id = dk.id
WHERE dri.final_disease_id IS NOT NULL
GROUP BY dk.id, dk.disease_name
ORDER BY total DESC;
    """
    with pymysql.connect(**db_config) as conn:
        with conn.cursor(DictCursor) as cur:
            cur.execute(sql)
            return cur.fetchall()


# 病虫害各自的已审核和未审核的次数,各自出现的次数 (本周与上周)
def total_count():
    sql = """
   SELECT
    -- ========== 原有字段（名称完全不变，保留前端兼容） ==========
    -- 本周病害总数
    SUM(CASE WHEN update_time >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) AND disease_type = 0 THEN 1 ELSE 0 END) AS this_week_disease,
    -- 上周病害总数
    SUM(CASE WHEN update_time >= DATE_SUB(CURDATE(), INTERVAL 14 DAY) AND update_time < DATE_SUB(CURDATE(), INTERVAL 7 DAY) AND disease_type = 0 THEN 1 ELSE 0 END) AS last_week_disease,

    -- 本周虫害总数
    SUM(CASE WHEN update_time >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) AND disease_type = 1 THEN 1 ELSE 0 END) AS this_week_pest,
    -- 上周虫害总数
    SUM(CASE WHEN update_time >= DATE_SUB(CURDATE(), INTERVAL 14 DAY) AND update_time < DATE_SUB(CURDATE(), INTERVAL 7 DAY) AND disease_type = 1 THEN 1 ELSE 0 END) AS last_week_pest,

    -- ========== 新增：病害细分 已审核 / 待审核 ==========
    -- 本周病害-已审核
    SUM(CASE WHEN update_time >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) AND disease_type = 0 AND item_audit_status = 2 THEN 1 ELSE 0 END) AS this_week_disease_audited,
    -- 本周病害-待审核
    SUM(CASE WHEN update_time >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) AND disease_type = 0 AND item_audit_status <> 2 THEN 1 ELSE 0 END) AS this_week_disease_pending,
    -- 上周病害-已审核
    SUM(CASE WHEN update_time >= DATE_SUB(CURDATE(), INTERVAL 14 DAY) AND update_time < DATE_SUB(CURDATE(), INTERVAL 7 DAY) AND disease_type = 0 AND item_audit_status = 2 THEN 1 ELSE 0 END) AS last_week_disease_audited,
    -- 上周病害-待审核
    SUM(CASE WHEN update_time >= DATE_SUB(CURDATE(), INTERVAL 14 DAY) AND update_time < DATE_SUB(CURDATE(), INTERVAL 7 DAY) AND disease_type = 0 AND item_audit_status <> 2 THEN 1 ELSE 0 END) AS last_week_disease_pending,

    -- ========== 新增：虫害细分 已审核 / 待审核 ==========
    -- 本周虫害-已审核
    SUM(CASE WHEN update_time >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) AND disease_type = 1 AND item_audit_status = 2 THEN 1 ELSE 0 END) AS this_week_pest_audited,
    -- 本周虫害-待审核
    SUM(CASE WHEN update_time >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) AND disease_type = 1 AND item_audit_status <> 2 THEN 1 ELSE 0 END) AS this_week_pest_pending,
    -- 上周虫害-已审核
    SUM(CASE WHEN update_time >= DATE_SUB(CURDATE(), INTERVAL 14 DAY) AND update_time < DATE_SUB(CURDATE(), INTERVAL 7 DAY) AND disease_type = 1 AND item_audit_status = 2 THEN 1 ELSE 0 END) AS last_week_pest_audited,
    -- 上周虫害-待审核
    SUM(CASE WHEN update_time >= DATE_SUB(CURDATE(), INTERVAL 14 DAY) AND update_time < DATE_SUB(CURDATE(), INTERVAL 7 DAY) AND disease_type = 1 AND item_audit_status <> 2 THEN 1 ELSE 0 END) AS last_week_pest_pending,
       
       -- 本周病害：治理完成
    SUM(CASE 
        WHEN update_time >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
         AND disease_type = 0
         AND item_audit_status = 5 
        THEN 1 ELSE 0 END) AS disease_treated,
       
        SUM(CASE 
        WHEN update_time >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
         AND disease_type = 0
         AND item_audit_status = 1
        THEN 1 ELSE 0 END) AS disease_untreated,
        
    -- 本周虫害：治理完成
    SUM(CASE 
        WHEN update_time >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
         AND disease_type = 1
         AND item_audit_status = 5 
        THEN 1 ELSE 0 END) AS pest_treated,  
       
       
        -- 本周虫害：未治理/未处理
    SUM(CASE 
        WHEN update_time >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
         AND disease_type = 1
         AND item_audit_status = 1 
        THEN 1 ELSE 0 END) AS pest_untreated

    
FROM detect_record_item;
    """
    with pymysql.connect(**db_config) as conn:
        with conn.cursor(DictCursor) as cur:
            cur.execute(sql)
            return cur.fetchall()


# 每年的
def total_year_cnt():
    sql = """
    SELECT 
    'year' AS period_type,
    CAST(year_val AS CHAR) AS period_label,
    year_val AS period_value,
  
    disease_cnt,
    pest_cnt
FROM (
    SELECT 
        YEAR(update_time) AS year_val,
     
        SUM(CASE WHEN disease_type = 0 THEN 1 ELSE 0 END) AS disease_cnt,
        SUM(CASE WHEN disease_type = 1 THEN 1 ELSE 0 END) AS pest_cnt
    FROM detect_record_item
    WHERE final_result IS NOT NULL
      AND final_result <> ''
      AND update_time >= DATE_SUB(CURDATE(), INTERVAL 5 YEAR)
    GROUP BY YEAR(update_time)
) t
ORDER BY year_val;

    """
    with pymysql.connect(**db_config) as conn:
        with conn.cursor(DictCursor) as cur:
            cur.execute(sql)
            return cur.fetchall()


# 本年每个月的
def total_month_cnt():
    sql = """
    SELECT 
    'month' AS period_type,
    DATE_FORMAT(update_time, '%m') AS period_label,  -- X轴：2025-01
    DATE_FORMAT(update_time, '%m') AS period_value,    -- 排序：202501
    COUNT(*) AS total_cnt,
    SUM(CASE WHEN disease_type = 0 THEN 1 ELSE 0 END) AS disease_cnt,
    SUM(CASE WHEN disease_type = 1 THEN 1 ELSE 0 END) AS pest_cnt,
    MIN(update_time) AS period_start,
    MAX(update_time) AS period_end
FROM detect_record_item
WHERE final_result IS NOT NULL
  AND final_result <> ''
  AND YEAR(update_time) = YEAR(CURDATE())  -- 只查本年
GROUP BY DATE_FORMAT(update_time, '%m')
ORDER BY DATE_FORMAT(update_time, '%m');

    """
    with pymysql.connect(**db_config) as conn:
        with conn.cursor(DictCursor) as cur:
            cur.execute(sql)
            return cur.fetchall()


# 本月每个周
def total_week_cnt():
    sql = """
    SELECT 
    'week' AS period_type,
    CONCAT(
        DATE_FORMAT(DATE_SUB(week_date, INTERVAL WEEKDAY(week_date) DAY), '%m-%d'),
        '~',
        DATE_FORMAT(DATE_ADD(DATE_SUB(week_date, INTERVAL WEEKDAY(week_date) DAY), INTERVAL 6 DAY), '%m-%d')
    ) AS period_label,
    yearweek_val AS period_value,
 
    disease_cnt,
    pest_cnt
FROM (
    SELECT 
        YEARWEEK(update_time, 1) AS yearweek_val,
        MAX(update_time) AS week_date,  
        
        SUM(CASE WHEN disease_type = 0 THEN 1 ELSE 0 END) AS disease_cnt,
        SUM(CASE WHEN disease_type = 1 THEN 1 ELSE 0 END) AS pest_cnt
    FROM detect_record_item
    WHERE final_result IS NOT NULL
      AND final_result <> ''
      AND YEAR(update_time) = YEAR(CURDATE())
      AND MONTH(update_time) = MONTH(CURDATE())
    GROUP BY YEARWEEK(update_time, 1)
) t
ORDER BY yearweek_val;

    """
    with pymysql.connect(**db_config) as conn:
        with conn.cursor(DictCursor) as cur:
            cur.execute(sql)
            return cur.fetchall()


# 检测历史记录查询
def all_record(page=None):
    offset = (page - 1) * 10
    sql = """
    SELECT
    i.item_id,
    i.record_id,
    i.disease_id,
    i.disease_name,
    i.confidence,
    i.item_audit_status,
    i.final_disease_id,
    i.final_result,
    i.disease_type,
    CASE i.item_audit_status
        WHEN 0 THEN '待确认'
        WHEN 1 THEN '待确认'
        WHEN 2 THEN '已确认'
        WHEN 3 THEN '误报'
        WHEN 4 THEN '治理中'
        WHEN 5 THEN '治理完成'
        ELSE '未知'
    END AS audit_status_text,
    DATE_FORMAT(i.update_time, '%%Y-%%m-%%d %%H:%%i:%%s') AS update_time_str,
    u_up.username AS upload_user,
    u_ad.username AS audit_user,
    r.id AS record_main_id,
    r.image_url,
    r.audit_remark,
    r.detect_time,
    r.audit_time,
    d.id AS knowledge_id,
    d.disease_name AS knowledge_disease_name,
    d.symptom,
    d.treatment,
    d.create_time AS knowledge_create_time,
    d.update_time AS knowledge_update_time,
    d.disease_type AS knowledge_disease_type,
    d.example_url
FROM detect_record_item i
INNER JOIN detect_record r ON i.record_id = r.id
LEFT JOIN users u_up ON r.user_id = u_up.user_id
LEFT JOIN users u_ad ON r.auditor_id = u_ad.user_id
LEFT JOIN disease_knowledge d ON i.disease_id = d.id
ORDER BY i.update_time DESC
LIMIT %s, 10;

    """

    with pymysql.connect(**db_config) as conn:
        with conn.cursor(DictCursor) as cur:
            cur.execute(sql, (offset,))
            return cur.fetchall()


# 根据数据筛选信息
def detectitem(page=None, filters=None):
    if filters is None:
        filters = {}

    offset = (page - 1) * 10

    sql = """
    SELECT i.*, u.username AS upload_user, u_ad.username AS audit_user,
DATE_FORMAT(i.update_time, '%%Y-%%m-%%d %%H:%%i:%%s') AS update_time_str,
        CASE i.item_audit_status
        WHEN 0 THEN '待确认'
        WHEN 1 THEN '待确认'
        WHEN 2 THEN '已确认'
        WHEN 3 THEN '误报'
        WHEN 4 THEN '治理中'
        WHEN 5 THEN '治理完成'
        ELSE '未知'
    END AS audit_status_text
FROM detect_record_item i
JOIN detect_record r ON i.record_id = r.id
JOIN users u ON r.user_id = u.user_id
LEFT JOIN users u_ad ON r.auditor_id = u_ad.user_id
WHERE 1=1
    """
    params = []

    # 1. 时间范围
    if filters.get("startTime"):
        sql += " AND DATE(i.update_time) >= %s"
        params.append(filters["startTime"])

    if filters.get("endTime"):
        sql += " AND DATE(i.update_time) <= %s"
        params.append(filters["endTime"])

    # 2. 病虫害类型
    if filters.get("disease_type") != "" and filters.get("disease_type") is not None:
        sql += " AND i.disease_type = %s"
        params.append(int(filters["disease_type"]))

    # 3. 审核状态
    if (
        filters.get("item_audit_status") != ""
        and filters.get("item_audit_status") is not None
    ):
        sql += " AND i.item_audit_status = %s"
        params.append(int(filters["item_audit_status"]))

    # 4. 关键词
    if filters.get("keyword"):
        sql += " AND (i.disease_name LIKE %s OR u.username LIKE %s OR u_ad.username LIKE %s)"
        kw = f"%{filters['keyword']}%"
        params.extend([kw, kw, kw])

    # 排序 + 分页
    sql += " ORDER BY update_time DESC LIMIT %s, 10"

    params.append(offset)

    with pymysql.connect(**db_config) as conn:
        with conn.cursor(DictCursor) as cur:
            cur.execute(sql, params)
            return cur.fetchall()


# 知识库
def knowledge():

    sql = """
    SELECT 
    id,
    disease_name,
    symptom,
    treatment,
    create_time,
    update_time,
    disease_type,
    example_url
FROM disease_knowledge;
    
    
    """

    with pymysql.connect(**db_config) as conn:
        with conn.cursor(DictCursor) as cur:
            cur.execute(sql)
            return cur.fetchall()


def update_audit_item_record(
    item_id,
    record_id,
    final_disease_id,
    final_result,
    item_audit_status,
    auditor_id,
    audit_remark,
):
    """
    审核明细+主记录双表更新，事务原子化
    :param item_id: 明细主键
    :param record_id: 主记录主键
    :param final_disease_id: 最终病害ID
    :param final_result: 最终病害名称
    :param item_audit_status: 明细审核状态 0~5
    :param auditor_id: 审核人登录ID
    :param audit_remark: 审核备注
    :return: (成功布尔值, 提示文本)
    """
    # 明细更新：只修改最终结果、审核状态
    SQL_UPDATE_ITEM_AUDIT = """
    UPDATE detect_record_item
    SET final_disease_id = %s, final_result = %s, item_audit_status = %s, update_time = NOW()
    WHERE item_id = %s;
    """
    # final_disease_id 为 None 时显式转为 NULL
    if final_disease_id in (None, '', 'null'):
        final_disease_id = None
    # 主记录更新：审核人、备注、审核时间，audit_status不和明细共用，单独使用
    SQL_UPDATE_RECORD_AUDIT = """
    UPDATE detect_record
    SET auditor_id = %s, audit_remark = %s, audit_time = NOW()
    WHERE id = %s;
    """
    conn = None
    try:
        conn = pymysql.connect(**db_config)
        conn.autocommit(False)
        cur = conn.cursor(DictCursor)
        # 执行两条更新
        cur.execute(
            SQL_UPDATE_ITEM_AUDIT,
            (final_disease_id, final_result, item_audit_status, item_id),
        )
        cur.execute(SQL_UPDATE_RECORD_AUDIT, (auditor_id, audit_remark, record_id))
        # 判断是否有数据被修改
        affect_row = cur.rowcount
        conn.commit()
        cur.close()
        if affect_row <= 0:
            return False, "未匹配到数据，修改无效"
        return True, "审核提交成功"
    except Exception as e:
        if conn:
            conn.rollback()
        err_msg = f"数据库更新异常:{str(e)}"
        print(err_msg)
        return False, err_msg
    finally:
        if conn:
            conn.close()


def knowledge_item(page=None, filters=None):
    filters = filters or {}

    page = int(page) if page is not None else 1
    page_size = 10
    offset = (page - 1) * page_size

    disease_name = filters.get("name") or None

    disease_type_raw = filters.get("type")
    if disease_type_raw is None or disease_type_raw == "":
        disease_type = None
    else:
        disease_type = int(disease_type_raw)

    where_sql = """
        WHERE
            (%s IS NULL OR disease_name LIKE CONCAT('%%', %s, '%%'))
            AND (%s IS NULL OR disease_type = %s)
    """

    sql_list = f"""
        SELECT
            id,
            disease_name,
            symptom,
            treatment,
            create_time,
            update_time,
            disease_type,
            example_url
        FROM disease_knowledge
        {where_sql}
        ORDER BY id ASC
        LIMIT %s OFFSET %s
    """

    sql_count = f"""
        SELECT COUNT(*) AS total
        FROM disease_knowledge
        {where_sql}
    """

    list_params = [
        disease_name,
        disease_name,
        disease_type,
        disease_type,
        page_size,
        offset,
    ]

    count_params = [disease_name, disease_name, disease_type, disease_type]

    with pymysql.connect(**db_config) as conn:
        with conn.cursor(DictCursor) as cur:
            cur.execute(sql_list, list_params)
            data_list = cur.fetchall()

            cur.execute(sql_count, count_params)
            count_res = cur.fetchone()

            total = count_res["total"] if count_res else 0

    return {"list": data_list, "total": total}


# 新增
def add_knowledge(form_data):
    sql = "INSERT INTO disease_knowledge(disease_name,disease_type,example_url,symptom,treatment,create_time,update_time) VALUES(%s,%s,%s,%s,%s,NOW(),NOW())"
    with pymysql.connect(**db_config) as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql,
                (
                    form_data["name"],
                    form_data["type"],
                    form_data["imgUrl"],
                    form_data["symptom"],
                    form_data["treat"],
                ),
            )
            conn.commit()
    return {"code": 200, "msg": "新增成功"}


# 单删
def del_knowledge(del_id):
    from mainyolo1 import delete_local_img
    sql = "DELETE FROM disease_knowledge WHERE id=%s"
    sql1 = "SELECT example_url FROM disease_knowledge WHERE id=%s"
    with pymysql.connect(**db_config) as conn:
        with conn.cursor(DictCursor) as cur:
            cur.execute(sql1, (del_id,))
            res = cur.fetchone()
            if res and res.get("example_url"):
                
                delete_local_img(res["example_url"])
                # 第二步：删除数据库记录
            cur.execute(sql, (del_id,))
            conn.commit()
    return {"code": 200, "msg": "删除成功"}


# 多条删除
def del_choose_knowledge(id_list):
    
    place = ",".join(["%s"] * len(id_list))
    sql = f"DELETE FROM disease_knowledge WHERE id IN ({place})"
    sql1 = f"SELECT example_url FROM disease_knowledge WHERE id IN ({place})"
    with pymysql.connect(**db_config) as conn:
        with conn.cursor(DictCursor) as cur:
            cur.execute(sql1, id_list)
            img_list = cur.fetchall()
            for item in img_list:
                url = item.get("example_url")
                if url:
                    from mainyolo1 import delete_local_img
                    delete_local_img(url)
            cur.execute(sql, id_list)
            conn.commit()
    return {"code": 200, "msg": "批量删除成功"}


# 更新数据库
def update_knowledge(name, type, img_url, symptom, treat, item_id):
    sql = """
    UPDATE disease_knowledge
    SET disease_name=%s,disease_type=%s,example_url=%s,symptom=%s,treatment=%s,update_time=NOW()
    WHERE id=%s
    
    """
    with pymysql.connect(**db_config) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (name, type, img_url, symptom, treat, item_id))
            conn.commit()
    return {"code": 200, "msg": "更新成功"}


def users(page =None):
    offset = (page - 1) * 10
    sql="""
    SELECT
    user_id,
    username,
    password,
    phone,
    CASE role
        WHEN 1 THEN '系统管理员'
        WHEN 0 THEN '普通用户'
    END AS role,
    DATE_FORMAT(create_time, '%%Y-%%m-%%d %%H:%%i') AS create_time
FROM users
ORDER BY user_id ASC
LIMIT %s, 10;
    
    """
    with pymysql.connect(**db_config) as conn:
        with conn.cursor(DictCursor) as cur:
            cur.execute(sql,(offset,))
    return cur.fetchall()

def useradd(username, password, phone, role):
    sql ="""
    INSERT INTO users(username,password,phone,role,create_time)
VALUES(%s,%s,%s,%s,NOW());
   
    """
    with pymysql.connect(**db_config) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (username, password, phone, role))
            conn.commit()
    return {"code":200,"msg":"添加成功"}

def userupdate(user_id, username, password, phone, role):
    sql = """
   UPDATE users
SET username=%s,password=%s,phone=%s,role=%s
WHERE user_id=%s;

    """
    with pymysql.connect(**db_config) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (username,password, phone, role, user_id))
            conn.commit()
    return {"code":200,"msg":"更新成功"}


def userdel(user_id):
    sql = """
    DELETE FROM users WHERE user_id=%s;  
    """
    with pymysql.connect(**db_config) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (user_id,))
            conn.commit()
    return {"code":200,"msg":"删除成功"}


# 根据病虫害名称查询知识库，返回 {id, disease_type, symptom, treatment} 或 None
def get_disease_by_name(disease_name: str):
    sql = "SELECT id, disease_type, symptom, treatment FROM disease_knowledge WHERE disease_name = %s"
    return query_one(sql, (disease_name,))


# 批量查询病虫害治理方法，返回 {disease_name: {symptom, treatment}}
def get_disease_treatments(disease_names: list):
    if not disease_names:
        return {}
    placeholders = ','.join(['%s'] * len(disease_names))
    sql = f"""
        SELECT disease_name, symptom, treatment
        FROM disease_knowledge
        WHERE disease_name IN ({placeholders})
    """
    results = query(sql, tuple(disease_names))
    return {r['disease_name']: r for r in results}


# 确保 detect_record_item 表的关键字段允许 NULL（用于"未检测出"记录）
def _ensure_nullable_columns():
    try:
        conn = pymysql.connect(**db_config)
        with conn.cursor() as cur:
            cur.execute("ALTER TABLE detect_record_item MODIFY COLUMN disease_id INT NULL")
            cur.execute("ALTER TABLE detect_record_item MODIFY COLUMN final_disease_id INT NULL")
            cur.execute("ALTER TABLE detect_record_item MODIFY COLUMN disease_type INT NULL")
        conn.close()
    except Exception:
        pass

_ensure_nullable_columns()

# 迁移：旧数据 item_audit_status=0 统一更新为 1（待确认），舍弃"无需审核"状态
try:
    conn = pymysql.connect(**db_config)
    with conn.cursor() as cur:
        cur.execute("UPDATE detect_record_item SET item_audit_status = 1 WHERE item_audit_status = 0")
        conn.commit()
    conn.close()
except Exception:
    pass

# 模型检测完后的信息存放入数据库中
# detect_result_list: [{"name": "叶霉病", "confidence": 0.95}, ...]
def model_add(image_url: str, user_id: int, detect_result_list: list):
    try:
        conn = pymysql.connect(**db_config)
        conn.begin()
        with conn.cursor() as cur:
            # 1. 插入主表 detect_record
            cur.execute(
                "INSERT INTO detect_record (image_url, detect_time, user_id, update_time) "
                "VALUES (%s, NOW(), %s, NOW())",
                (image_url, user_id)
            )
            record_id = cur.lastrowid

            # 2. 逐条插入子表 detect_record_item
            for item in detect_result_list:
                name = item["name"]
                confidence = item["confidence"]

                # 查知识库获取 disease_id 和 disease_type
                cur.execute(
                    "SELECT id, disease_type FROM disease_knowledge WHERE disease_name = %s",
                    (name,)
                )
                row = cur.fetchone()
                if not row:
                    continue
                disease_id = row[0]
                disease_type = row[1]

                # 置信度 > 0.8 自动归为已确认(2)，否则待确认(1)
                auto_status = 2 if confidence > 0.8 else 1

                cur.execute(
                    "INSERT INTO detect_record_item "
                    "(record_id, disease_id, disease_name, confidence, "
                    "item_audit_status, final_disease_id, final_result, "
                    "disease_type, update_time) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())",
                    (record_id, disease_id, name, confidence,
                     auto_status, disease_id, name, disease_type)
                )

        conn.commit()
        return True, record_id
    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        return False, f"入库异常：{str(e)}"
