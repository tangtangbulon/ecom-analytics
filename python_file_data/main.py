from pathlib import Path
import csv
import json

current_dir=Path(__file__).parent
csv_file_path=current_dir/"orders.csv"


def read_csv_data(file_path):
    try:
        data_list=[]
        with open(file_path,mode="r",encoding="utf-8") as f:
            reader=csv.DictReader(f)
            for row in reader:
                row['price']=float(row['price'])
                row['quantity']=int(row['quantity'])
                data_list.append(row)
            return data_list
    except UnicodeDecodeError:
        print("UTF-8 读取失败，正在尝试GBK编码...")
        data_list=[]
        with open(file_path,mode="r",encoding="gbk") as f:
            reader=csv.DictReader(f)
            for row in reader:
                row['price']=float(row['price'])
                row['quantity']=int(row['quantity'])
                data_list.append(row)
            return data_list


data_list=read_csv_data(csv_file_path)
print(data_list)


json_file_path=current_dir/"orders.json"
with open(json_file_path,mode="w",encoding="utf-8") as f:
    json.dump(data_list,f,ensure_ascii=False,indent=4)
print(f"成功导出JSON文件: {json_file_path}")