def calculate_revenue(price:float,qquality:int)->float:
    """
    计算总收入
    :param price:单价(浮点数)
    :param qquality:数量(整数)
    :return:收入(浮点数)
    """
    revenue=price*qquality
    return revenue



def calculate_profit(revenue:float,costs:float)->float:
    """
    计算利润
    :param revenue:收入(浮点数)
    :param costs:成本(浮点数)
    :return:利润(浮点数)
    """

    frofit=revenue-costs
    return frofit

import logging
import os
import sqlite3
from pathlib import Path
import csv
import io
from schemas import Order
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

db_path = os.getenv("DB_PATH")
if not db_path:
    raise RuntimeError("缺少环境变量 DB_PATH，请在项目根目录的 .env 中配置")

DB_PATH = Path(db_path)
if not DB_PATH.is_absolute():
    DB_PATH = PROJECT_ROOT / DB_PATH


def insert_many_order(orders):
    """一次连接写入整批订单，失败则整批回滚。"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    try:
        inserted_count = 0
        for order in orders:
            cursor.execute("""
            INSERT INTO raw_orders (order_id, date, store, sku, price, cost, quantity, status, coupon_fee, other_fee)
            SELECT ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM raw_orders WHERE order_id = ? AND sku = ?
            )
            """, (
                order.order_id, order.date, order.store, order.sku, order.price, order.cost,
                order.quantity, order.status, order.coupon_fee, order.other_fee,
                order.order_id, order.sku,
            ))
            cursor.execute("""
            INSERT OR IGNORE INTO products (sku, price, cost)
            VALUES (?, ?, ?)
            """, (order.sku, order.price, order.cost))
            cursor.execute("""
            INSERT OR IGNORE INTO orders (order_id, date, store)
            VALUES (?, ?, ?)
            """, (order.order_id, order.date, order.store))
            cursor.execute("""
            INSERT OR IGNORE INTO stores (store_id, commission_rate, base_shipping_fee)
            VALUES (?, ?, ?)
            """, (order.store, order.commission_rate, order.base_shipping_fee))
            cursor.execute("""
            INSERT INTO order_items (order_id, sku, price, cost, quantity, coupon_fee, other_fee)
            SELECT ?, ?, ?, ?, ?, ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM order_items WHERE order_id = ? AND sku = ?
            )
            """, (
                order.order_id, order.sku, order.price, order.cost, order.quantity,
                order.coupon_fee, order.other_fee, order.order_id, order.sku,
            ))
            inserted_count += cursor.rowcount
        conn.commit()
        logging.debug(f"订单写入完成，新增明细 {inserted_count} 条")
        return inserted_count
    except Exception as e:
        conn.rollback()
        logging.error(f"订单写入失败: {e}")
        raise
    finally:
        cursor.close()
        conn.close()





def get_summary_data(start_date=None):
    """按 SKU 和店铺汇总销量、销售额、成本和利润。"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    sql="""
    SELECT
    oi.sku,
    o.store,
    SUM(oi.quantity) AS total_quantity,
    SUM(oi.quantity * oi.price) AS total_revenue,
    SUM(oi.quantity * p.cost) AS product_cost,
    SUM(oi.quantity * oi.price * s.commission_rate) AS commission_cost,
    SUM(oi.quantity * oi.coupon_fee) AS coupon_cost,
    SUM(oi.quantity * oi.other_fee) AS other_cost,
    SUM(
            oi.quantity * oi.price
                - oi.quantity * oi.coupon_fee
                - oi.quantity * p.cost
                - (oi.quantity * oi.price * s.commission_rate)
                - oi.quantity * oi.other_fee
    ) AS total_profit,
    CASE
    WHEN SUM(oi.quantity * oi.price) = 0 THEN 0
    ELSE (
        SUM(oi.quantity * oi.price) - SUM(oi.quantity * p.cost)
    ) / SUM(oi.quantity * oi.price)
END AS gross_margin

FROM order_items oi
JOIN products p ON oi.sku = p.sku
JOIN orders o ON oi.order_id = o.order_id
JOIN stores s ON o.store = s.store_id

    """
    params=[]
    if start_date is not None:
        params.append(start_date.strftime("%Y-%m-%d"))
        sql += " WHERE o.date >= ?"
    sql += " GROUP BY oi.sku, o.store"
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    summary_list = []
    for row in rows:
        summary_list.append({
            "sku":row["sku"],
            "store":row["store"],
            "total_quantity":row["total_quantity"],
            "total_revenue":row["total_revenue"],
            "product_cost":row["product_cost"],
            "commission_cost":row["commission_cost"],
            "coupon_cost":row["coupon_cost"],
            "other_cost":row["other_cost"],
            "total_profit":row["total_profit"],
            "gross_margin":row["gross_margin"]
        })
    cursor.close()
    conn.close()
    return summary_list


def _to_float(value, default=0.0):
    if value is None or str(value).strip() == "":
        return default
    return float(value)


def process_order_csv_and_insert(file_content: bytes) -> int:
    """解析上传的 CSV，并写入订单相关表。返回新写入的订单明细条数。"""
    text = file_content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    orders = []
    for line_no, row in enumerate(reader, start=2):
        try:
            quantity = int(float(row["quantity"])) if row.get("quantity") else 0
            price = _to_float(row.get("price"))
            if price < 0 or quantity <= 0:
                logging.warning(f"第{line_no}行价格或数量不合法，已跳过")
                continue
            orders.append(type("CsvOrder", (), {
                "order_id": str(row["order_id"]),
                "date": row["date"],
                "store": row["store"],
                "sku": row["sku"],
                "price": price,
                "cost": _to_float(row.get("cost")),
                "quantity": quantity,
                "status": row.get("status") or "",
                "coupon_fee": _to_float(row.get("coupon_fee")),
                "other_fee": _to_float(row.get("other_fee")),
                "commission_rate": _to_float(row.get("commission_rate")),
                "base_shipping_fee": _to_float(row.get("base_shipping_fee")),
            })())
        except (KeyError, TypeError, ValueError) as e:
            logging.warning(f"第{line_no}行解析失败，已跳过: {e}")
            continue
    if not orders:
        raise ValueError("CSV 中没有可导入的有效订单")
    return insert_many_order(orders)


def get_order_by_id(order_id:str):
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor=conn.cursor()
    try:
        cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
        row=cursor.fetchone()
        if row is None:
            return None
        return dict(row)
    finally:
        cursor.close()
        conn.close()
    
    

