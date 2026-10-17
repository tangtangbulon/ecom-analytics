# 📊 订单分析系统 (Order Analysis System)

这是一个基于 **FastAPI** 和 **Streamlit** 构建的轻量级订单分析系统。旨在将本地数据脚本升级为标准的 Web API 服务和可视化仪表盘。

## ✨ 功能特性
*   **标准三层架构**：API层、Service层、数据层分离，代码更健壮。
*   **数据校验**：使用 Pydantic 对输入输出数据进行严格校验，防止脏数据。
*   **自动化测试**：使用 Pytest 和 TestClient 保证接口稳定性。
*   **交互式看板**：使用 Streamlit 制作实时交互的销售数据图表。

## 🛠️ 技术栈
*   **后端**：Python, FastAPI, Uvicorn, Pydantic
*   **数据库**：SQLite
*   **前端**：Streamlit, Pandas
*   **测试**：Pytest, HTTPX

## 🚀 如何运行这个项目？

### 1. 安装依赖
在终端中运行以下命令，安装所有必需的 Python 库：
```bash
pip install -r requirements.txt