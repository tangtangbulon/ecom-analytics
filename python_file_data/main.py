from pathlib import Path
import csv
import json
from dataclasses import dataclass,asdict




@dataclass
class Order:
    sku:str
    price:float
    quantity:int


    
current_dir=Path(__file__).parent
csv_file_path=current_dir/"orders.csv"


def read_csv_data(file_path):
    data_list=[]
    try:
        with open(file_path,mode="r",encoding="utf-8") as f:
            reader=csv.DictReader(f)
            for row in reader:
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
                        quantity=quantity_value
                    )
                    data_list.append(order)

                except ValueError as e:
                    print(f"数据校验失败，跳过改行: {e}")
                    continue
                print(f"-> 正在处理 SKU: {row.get('sku', '未知')} 的后续逻辑...")
                
            return data_list
    except UnicodeDecodeError:
        print("UTF-8 读取失败，正在尝试GBK编码...")
        

        with open(file_path,mode="r",encoding="gbk") as f:
            reader=csv.DictReader(f)
            for row in reader:
                row['price']=float(row['price'])
                row['quantity']=int(row['quantity'])
                data_list.append(row)
            return data_list


data_list=[asdict(order) for order in read_csv_data(csv_file_path)]
print(data_list)


json_file_path=current_dir/"orders.json"
with open(json_file_path,mode="w",encoding="utf-8") as f:
    json.dump(data_list,f,ensure_ascii=False,indent=4)
print(f"成功导出JSON文件: {json_file_path}")