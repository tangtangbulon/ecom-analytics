def calculate_revenue(price:float,qquality:int)->float:
    """
    计算总收入
    :param price:单价(浮点数)
    :param qquality:数量(整数)
    :return:收入(浮点数)
    """
    revenue=price*qquality
    return revenue



def calculate_profit(revenue:float,costs:float)->float:
    """
    计算利润
    :param revenue:收入(浮点数)
    :param costs:成本(浮点数)
    :return:利润(浮点数)
    """

    frofit=revenue-costs
    return frofit


print("----测试收入计算------")
test_revenue=calculate_revenue(10.5,3)
print(f"单价10.5,数量3,预期收入31.5,实际收入:{test_revenue}")

print("----测试利润计算------")
test_profit=calculate_profit(test_revenue,10)
print(f"收入31.5，成本10.0，预期利润21.5，实际结果:{test_profit}")


print("----额外测试----")
print(calculate_revenue(99.9,5))
print(calculate_profit(1000,250.5))


