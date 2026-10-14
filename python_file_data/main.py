from pathlib import Path
import csv
import json
from dataclasses import dataclass,asdict
import logging
import sys


log_format="%(asctime)s - %(levelname)s - %(message)s"

    
current_dir=Path(__file__).parent
#csv_file_path=current_dir/"orders.csv"
log_file_path=current_dir/"logs.log"
finance_dir = Path(__file__).resolve().parents[1] / "pandas_file_data" / "FinanceProject"
sys.path.append(str(finance_dir))
from test_finance import calculate_gross_margin

logging.basicConfig(
    level=logging.DEBUG,
    format=log_format,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file_path,encoding="utf-8")
    ]
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
    data_list=[]
    try:
        with open(file_path,mode="r",encoding="utf-8") as f:
            reader=csv.DictReader(f)
            for row in reader:
                raw_cost=row.get('cost',0.0)
                cost_value=float(raw_cost) if raw_cost else 0.0
                try:
                    price_value=float(row['price'] if row['price'] else 0.0)
                    quantity_value=int(row['quantity'] if row['quantity'] else 0)

                    if price_value<0:
                        raise ValueError(f"金额不能为负(SKU:{row['sku']},价格:{price_value})")
                    
                    if quantity_value<=0:
                        raise ValueError(f"数量不能为负(SKU:{row['sku']},数量:{quantity_value})")

                    order=Order(
                        sku=row['sku'],
                        price=price_value,
                        quantity=quantity_value,
                        cost=cost_value,
                        order_id=row['order_id'],
                        date=row['date'],
                        store=row['store']
                    )
                    data_list.append(order)

                except ValueError as e:
                    logging.warning(f"第{reader.line_num}行数据校验失败，跳过该行: {e}")
                    continue
                logging.info(f"-> 正在处理 SKU: {row.get('sku', '未知')} 的后续逻辑...")
                
        return data_list
    except FileNotFoundError:
        logging.error(f"文件不存在: {file_path}")
        return []

    except UnicodeDecodeError:
        logging.error(f"文件编码错误: {file_path}")
        return []





if __name__=="__main__":

    if len(sys.argv)<2:
        logging.warning("错误：请在命令中指定文件名，例如: python main.py orders.csv")
        sys.exit(1)
    input_file=sys.argv[1]
    csv_file_path=current_dir/input_file


    data_list=read_csv_data(csv_file_path)  
    
    if not data_list:
        logging.warning(f"未获取到有效数据,退出程序")
        sys.exit(0)
    # else:
        json_file_path=current_dir/"orders.json"
        try:
            data_list=[asdict(order) for order in data_list]
            with open(json_file_path,mode="w",encoding="utf-8") as f:
                json.dump(data_list,f,ensure_ascii=False,indent=4)
            logging.info(f"成功导出JSON文件: {json_file_path}")
        except Exception as e:
            logging.error(f"导出JSON文件失败: {e}")


    summary={}
    for order in data_list:
        sku=order.sku
        if sku not in summary:
            summary[sku]={
                "total_quantity":0,
                "total_price":0.0,
                "total_cost":0.0
                
            }
        summary[sku]["total_quantity"]+=order.quantity
        summary[sku]["total_price"]+=order.price*order.quantity
        summary[sku]["total_cost"]+=order.cost*order.quantity
    

    for sku, data in summary.items():
        data["gross_margin"] = calculate_gross_margin(
            data["total_price"],   # 销售额
            data["total_cost"],    # 成本
        )

    print("\n" + "-" * 78)
    print(f"{'SKU':<10} | {'总销量':<10} | {'总销售额':<15} | {'总成本':<15} | {'毛利率':<15}")
    print("-" * 78)
    for sku,data in summary.items():
        print(f"{sku:<10} | {data['total_quantity']:<10} | {data['total_price']:>15.2f} | {data['total_cost']:>15.2f} | {data['gross_margin']:>15.2f}")
    print("-" * 78+"\n")