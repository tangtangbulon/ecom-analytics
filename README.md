# Ecom Analytics 订单分析系统

这是一个基于 Python 的订单数据统计与分析项目，旨在从电商订单数据中提取有价值的业务洞察。

## ✨ 核心功能 (Features)
- 数据清洗：处理缺失值与异常订单。
- 基础统计：计算总销售额、订单量、客单价。
- 维度分析：按时间、地区、商品类别进行销售趋势分析。
- 数据可视化：生成直观的销售报表（未来计划支持）。

## 🛠️ 技术栈 (Tech Stack)
- 语言：Python 3.x
- 环境管理：uv (现代、极速的 Python 环境管理器)
- 数据分析：Pandas, NumPy (待安装)
- 数据可视化：Matplotlib / Seaborn (待安装)

## 📁 项目结构 (Project Structure)
```text
ecom-analytics/
├── data/               # 存放原始数据与清洗后的数据
├── notebooks/          # Jupyter 实验笔记本
├── src/                # 核心代码目录
│   ├── __init__.py
│   └── analysis.py     # 数据分析逻辑
├── .gitignore          # Git 忽略文件配置
├── README.md           # 项目说明文档
└── pyproject.toml      # uv 环境配置文件

