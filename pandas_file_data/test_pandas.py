
# %%
import pandas as pd

# 构造一个包含30多天、多个SKU的测试数据集
data = {
    '日期': ['2023-09-20', '2023-09-25', '2023-10-01', '2023-10-15', '2023-10-20', 
             '2023-10-20', '2023-10-21', '2023-10-22', '2023-10-22', '2023-10-23'],
    'SKU': ['S01', 'S02', 'S01', 'S03', 'S01', 
            'S02', 'S03', 'S01', 'S02', 'S01'],
    '销售额': [200, 150, 300, 400, 250, 
             100, 500, 600, 200, 300]
}
df = pd.DataFrame(data)
df.head()
# %%
df.info()
# %%
df['日期']=pd.to_datetime(df['日期'])
# %%
df.info()
# %%
latest_date=df['日期'].max()
seven_days_ago=latest_date-pd.Timedelta(days=7)
df_7d=df[df['日期']>=seven_days_ago]
report_7d=df_7d.groupby('日期').agg({'销售额': 'sum'}).reset_index()
# %%
