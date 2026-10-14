import pandas as pd

def calculate_gross_margin(sales,cost):
    if sales == 0 or sales is None or pd.isna(sales):
        return 0
    if cost is None or pd.isna(cost):
        cost=0
    profit=sales-cost
    margin=profit/sales
    return margin


def test_normal_margin():
    assert calculate_gross_margin(200,80) == 0.6

def test_loss_margin():
    assert calculate_gross_margin(100,150) == -0.5

def test_zero_sales():
    assert calculate_gross_margin(0,0) == 0

def test_zero_sales_and_cost():
    assert calculate_gross_margin(0,100) == 0

def test_zero_profit():
    assert calculate_gross_margin(100,100) == 0

# 测试用例6：销售额为空值（None），应返回0（对应图片：空值不参与计算）
def test_none_sales():
    assert calculate_gross_margin(None, 50) == 0

# 测试用例7：成本为空值（None），应视为0成本计算毛利率 (100-0)/100 = 1.0
def test_none_cost():
    assert calculate_gross_margin(100, None) == 1.0

# 测试用例8：销售额为负数（业务异常场景），比如退货 100，成本50，毛利率应为 1.5 (因为 (-100-50)/-100 = 1.5)
def test_negative_sales():
    assert calculate_gross_margin(-100, 50) == 1.5

# 测试用例9：成本为负数（业务异常场景，比如供应商返利），销售额100，成本-20，毛利率 (100-(-20))/100 = 1.2
def test_negative_cost():
    assert calculate_gross_margin(100, -20) == 1.2

# 测试用例10：销售额和成本均为0（全空/全零场景），应返回0
def test_all_zero():
    assert calculate_gross_margin(0, 0) == 0