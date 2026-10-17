import streamlit as st
import pandas as pd
import requests
from datetime import date

st.set_page_config(page_title="销售数据仪表盘", page_icon=":bar_chart:", layout="wide")

if "import_notice" not in st.session_state:
    st.session_state.import_notice = None

# 在侧边栏添加一个文件上传器
st.sidebar.header("📁 数据导入")
uploaded_file = st.sidebar.file_uploader("上传订单 CSV 文件", type=["csv"])

if uploaded_file is not None:
    if st.sidebar.button("确认导入"):
        with st.spinner("正在上传并解析数据..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
            upload_url = "http://127.0.0.1:8000/upload_order_csv"
            try:
                response = requests.post(upload_url, files=files)
                if response.status_code == 200:
                    message = response.json().get("message", "导入完成")
                    level = "warning" if "成功插入0条" in message else "success"
                    st.session_state.import_notice = {"level": level, "text": message}
                    st.rerun()
                else:
                    detail = "上传失败"
                    try:
                        detail = response.json().get("detail") or detail
                    except ValueError:
                        detail = response.text or detail
                    st.session_state.import_notice = {"level": "error", "text": f"上传失败：{detail}"}
            except requests.exceptions.RequestException as e:
                st.session_state.import_notice = {"level": "error", "text": f"连接后端失败：{e}"}

notice = st.session_state.import_notice
if notice:
    getattr(st.sidebar, notice["level"])(notice["text"])

st.title("SKU 销售数据仪表盘")
if notice:
    getattr(st, notice["level"])(notice["text"])
st.markdown("欢迎使用 实时销售数据仪表盘")

st.sidebar.header("筛选条件")
selected_date = st.sidebar.date_input("请选择查询日期", date(2023, 9, 1))

API_URL = "http://localhost:8000/analytics/sales"

params = {"start_date": selected_date.strftime("%Y-%m-%d")}

try:
    response = requests.get(API_URL, params=params)
    
    if response.status_code == 200:
        data = response.json()

        if not data:
            st.error("没有找到任何销售数据")
        else:
            df=pd.DataFrame(data)
            df_sorted=df.sort_values(by="total_revenue", ascending=False)

            with st.expander("点击查看原始数据表格"):
                st.dataframe(df_sorted)

            st.subheader("SKU 销售额排名")
            chart_data=df_sorted.set_index("sku")["total_revenue"]
            st.bar_chart(chart_data)

            st.subheader("SKU 销售数量排名")
            chart_data_quantity=df_sorted.set_index("sku")["total_quantity"]
            st.bar_chart(chart_data_quantity)
    elif response.status_code == 404:
        st.warning("没有找到任何销售数据,404错误")
    else:
        st.error(f"请求失败,状态码: {response.status_code}")
except requests.exceptions.ConnectionError as e:
    st.error(f"无法连接到API服务器: {e}")

if "order_detail" not in st.session_state:
    st.session_state.order_detail = None

st.sidebar.header("订单详情")
order_id = st.sidebar.text_input("请输入订单ID")
if order_id:
    try:
        response = requests.get(f"http://localhost:8000/orders/{order_id}")
        if response.status_code == 200:
            st.session_state.order_detail = response.json()
        else:
            st.session_state.order_detail = None
            detail = "订单不存在"
            try:
                detail = response.json().get("detail") or detail
            except ValueError:
                pass
            st.sidebar.error(f"{detail},状态码: {response.status_code}")
    except requests.exceptions.ConnectionError as e:
        st.sidebar.error(f"无法连接到API服务器: {e}")
if st.session_state.order_detail:
    st.sidebar.json(st.session_state.order_detail)
