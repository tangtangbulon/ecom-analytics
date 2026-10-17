from pathlib import Path
import csv
import json
from dataclasses import dataclass,asdict
import logging
import sys
import sqlite3


log_format="%(asctime)s - %(levelname)s - %(message)s"

    
current_dir=Path(__file__).parent
#csv_file_path=current_dir/"orders.csv"
log_file_path=current_dir/"logs.log"
project_dir = Path(__file__).resolve().parents[1]
finance_dir = project_dir / "pandas_file_data" / "FinanceProject"
sys.path.append(str(finance_dir))
sys.path.append(str(project_dir))
from test_finance import calculate_gross_margin
from utils import get_summary_data, insert_many_order

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
logging.basicConfig(
    level=logging.DEBUG,
    format=log_format,
    handlers=[console_handler, file_handler],
)


@dataclass
class Order:
    order_id:str
    date:str
    sku:str
    price:float
    quantity:int
    cost: float
    store:str

def read_csv_data(file_path):
    orders = []
    try:
        with open(file_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                raw_cost = row.get("cost", 0.0)
                cost_value = float(raw_cost) if raw_cost else 0.0
                try:
                    price_value = float(row["price"] if row["price"] else 0.0)
                    quantity_value = int(row["quantity"] if row["quantity"] else 0)

                    if price_value < 0:
                        raise ValueError(f"金额不能为负(SKU:{row['sku']},价格:{price_value})")

                    if quantity_value <= 0:
                        raise ValueError(f"数量不能为负(SKU:{row['sku']},数量:{quantity_value})")

                    orders.append(Order(
                        sku=row["sku"],
                        price=price_value,
                        quantity=quantity_value,
                        cost=cost_value,
                        order_id=row["order_id"],
                        date=row["date"],
                        store=row["store"],
                    ))
                except ValueError as e:
                    logging.warning(f"第{reader.line_num}行数据校验失败，跳过该行: {e}")
                    continue
        logging.info(f"读取完成，有效订单 {len(orders)} 条")
        return orders
    except FileNotFoundError:
        logging.error(f"文件不存在: {file_path}")
        return []
    except UnicodeDecodeError:
        logging.error(f"文件编码错误: {file_path}")
        return []


def export_to_json(data):
    with open('summary_report.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)



def display_width(text):
    width = 0
    for ch in str(text):
        width += 2 if ord(ch) > 127 else 1
    return width


def pad(text, width, align="left"):
    text = str(text)
    gap = max(width - display_width(text), 0)
    if align == "right":
        return " " * gap + text
    return text + " " * gap


def print_summary(summary_list):
    headers = ("SKU", "店铺", "总销量", "总销售额", "商品成本", "佣金", "优惠", "其他费用", "利润")
    widths = (10, 12, 8, 12, 12, 10, 10, 10, 12)
    aligns = ("left", "left", "right", "right", "right", "right", "right", "right", "right")

    def format_row(values):
        cells = [pad(value, width, align) for value, width, align in zip(values, widths, aligns)]
        return " | ".join(cells)

    line = "-" * display_width(format_row(headers))
    print("\n" + line)
    print(format_row(headers))
    print(line)
    for row in summary_list:
        print(format_row((
            row["sku"],
            row["store"],
            row["total_quantity"],
            f"{row['total_revenue']:.2f}",
            f"{row['product_cost']:.2f}",
            f"{row['commission_cost']:.2f}",
            f"{row['coupon_cost']:.2f}",
            f"{row['other_cost']:.2f}",
            f"{row['total_profit']:.2f}",
        )))
    print(line + "\n")


if __name__ == "__main__":
    print("🚀 系统启动，正在从数据库获取数据...")
    finally_report = get_summary_data()
    print_summary(finally_report)
    export_to_json(finally_report)
    print("🎉 数据导出完成，保存在 summary_report.json 文件中")