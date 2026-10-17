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
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "python_file_data" / "shop.db"


def insert_many_order(orders):
    """一次连接写入整批订单，失败则整批回滚。"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    try:
        for order in orders:
            cursor.execute("""
            INSERT OR IGNORE INTO products (sku, price, cost)
            VALUES (?, ?, ?)
            """, (order.sku, order.price, order.cost))
            cursor.execute("""
            INSERT OR IGNORE INTO orders (order_id, date, store)
            VALUES (?, ?, ?)
            """, (order.order_id, order.date, order.store))
            cursor.execute("""
            INSERT INTO order_items (order_id, sku, price, cost, quantity)
            SELECT ?, ?, ?, ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM order_items WHERE order_id = ? AND sku = ?
            )
            """, (order.order_id, order.sku, order.price, order.cost, order.quantity, order.order_id, order.sku))
        conn.commit()
        logging.debug(f"订单{order.order_id}插入成功")
    except Exception as e:
        conn.rollback()
        logging.error(f"订单{order.order_id}插入失败: {e}")
    finally:
        cursor.close()
        conn.close()





def get_summary_data():
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
GROUP BY oi.sku, o.store
    """
    cursor.execute(sql)
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
    


