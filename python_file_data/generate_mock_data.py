import random
import csv
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
DB_PATH = Path(__file__).resolve().parent / "shop.db"

# 1. 设定基础参数
skus = ['ABC', 'XYZ', 'MNB', 'QWE']
stores = ['杭州店', '上海店', '北京店']
statuses = ['paid', 'unpaid']
start_date = datetime(2023, 10, 1)
commission_rates = [0.1, 0.15, 0.2]
base_shipping_fees = [10, 20, 30]

# 2. 生成 1000 条随机数据
mock_orders = []
for i in range(1, 1001):
    order_id = i
    # 随机日期（过去30天内）
    random_days = random.randint(0, 30)
    date_str = (start_date + timedelta(days=random_days)).strftime('%Y-%m-%d')
    store = random.choice(stores)
    status = random.choice(statuses)
    sku = random.choice(skus)
    quantity = random.randint(1, 10)
    commission_rate = random.choice(commission_rates)
    base_shipping_fee = random.choice(base_shipping_fees)
    coupon_fee = random.randint(0, 10)
    other_fee = random.randint(0, 10)
    # 为了测试，设定固定的价格和成本
    price = 100.0 if sku in ['ABC', 'XYZ'] else 50.0
    cost = 50.0 if sku in ['ABC', 'XYZ'] else 20.0
    other_cost = cost * 0.1
    mock_orders.append({
        'order_id': order_id, 'date': date_str, 'store': store, 'status': status,
        'sku': sku, 'quantity': quantity, 'price': price, 'cost': cost, 'commission_rate': commission_rate, 'base_shipping_fee':base_shipping_fee, 'other_cost': other_cost, 'coupon_fee': coupon_fee, 'other_fee': other_fee
    })

# 3. 导出到 CSV (为了旧系统 main.py 准备)
with open('mock_data.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=mock_orders[0].keys())
    writer.writeheader()
    writer.writerows(mock_orders)
print("✅ mock_data.csv 生成完毕！")

# 4. 批量插入 SQLite (为了新系统 main_db.py 准备)
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
try:
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # 使用 executemany 批量插入，性能极高！
    # 注意：由于有外键约束，需要先提取唯一的商品和订单信息插入主表，再插明细表
    # 简化处理：用 INSERT OR IGNORE 解决主表重复问题
    for order in mock_orders:
        cursor.execute("INSERT OR IGNORE INTO raw_orders (order_id,date,store,sku,price,cost,quantity,status,coupon_fee,other_fee) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                       (order['order_id'], order['date'], order['store'], order['sku'], order['price'], order['cost'], order['quantity'],order['status'], order['coupon_fee'], order['other_fee']))          
        cursor.execute("INSERT OR IGNORE INTO products (sku, price, cost) VALUES (?, ?, ?)", 
                       (order['sku'], order['price'], order['cost']))
        cursor.execute("INSERT OR IGNORE INTO orders (order_id, date, store) VALUES (?, ?, ?)", 
                       (order['order_id'], order['date'], order['store']))
        cursor.execute("INSERT OR IGNORE INTO stores (store_id, commission_rate, base_shipping_fee) VALUES (?, ?, ?)", 
                       (order['store'], order['commission_rate'], order['base_shipping_fee']))
            
        cursor.execute("INSERT INTO order_items (order_id, sku, price,cost, quantity,coupon_fee,other_fee) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                       (order['order_id'], order['sku'], order['price'], order['cost'], order['quantity'], order['coupon_fee'], order['other_fee']))
        
    conn.commit()
    print("✅ 1000条数据已成功写入 SQLite 数据库！")
except Exception as e:
    conn.rollback()
    print(f"❌ 写入失败: {e}")
finally:
    conn.close()