# 迷你电商订单数据分析工具 (Ecom Analytics)

这是一个用于清洗、校验并汇总订单数据的 Python 命令行小工具。

## 功能特性
- 读取 CSV 订单数据
- 异常数据校验（负金额、零/负数量、格式错误）
- 自动按 SKU 汇总总销量与总销售额
- 日志记录（记录到 `logs.log`）
- 结果格式化打印到终端

## 环境依赖
- Python 3.10+ (推荐 3.12)
- 无第三方外部依赖（全部使用 Python 标准库：`csv`, `json`, `pathlib`, `logging`, `dataclasses`, `sys`）

## 如何运行
1. 准备好你的 CSV 文件（例如 `orders.csv`），格式如下：
   ```csv
   sku,price,quantity
   A123,10.5,3