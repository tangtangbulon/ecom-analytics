from fastapi import APIRouter,HTTPException,UploadFile,File
from typing import List,Optional
import services
from schemas import Order,SalesSummary
from datetime import date
import logging


router = APIRouter()

# 4. 编写第二个路由：GET /orders

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.get("/analytics/sales", response_model=List[SalesSummary])
def get_sales_analytics(start_date: Optional[date] = None):
    try:
        # 1. 调用 utils.py 中的真实业务逻辑去查数据库
        data = services.get_summary_data(start_date)
        
        # 2. 模拟查不到数据的情况（比如数据库是空的）
        if not data: # 如果 data 是空列表 [] 或 None
            # 主动抛出 404 错误，附带友好的提示
            raise HTTPException(status_code=404, detail="没有找到任何销售数据")
            
        # 3. 如果一切正常，返回数据
        # 注意：因为我们用了 response_model=List[SalesSummary]
        # FastAPI 会自动把查出来的数据按昨天写的模型格式化好再返回
        return data

    except HTTPException:
        # 如果是我们自己抛出的 404，原样抛出去，不要被下面的 Exception 抓走
        raise
    except Exception as e:
        # 4. 模拟数据库连不上或其他代码报错的情况
        print(f"服务器后台报错啦：{e}") # 打印在终端，方便你自己排错
        # 抛出 500 错误，不要给前端暴露敏感信息（比如数据库密码）
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后再试")


@router.post("/upload_order_csv")
async def upload_order_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="请上传CSV文件")
    try:
        file_content = await file.read()
        inserted_count = services.process_order_csv_and_insert(file_content)
        return {"message": f"成功插入{inserted_count}条订单数据"}
    except Exception as e:
        logging.error(f"上传CSV文件失败: {e}")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


@router.get("/orders/{order_id}")
def get_order_by_id(order_id: str):
    try:
        order = services.get_order_by_id(order_id)
        if order is None:
            raise HTTPException(status_code=404, detail="订单不存在")
        return order
    except Exception as e:
        logging.error(f"获取订单失败: {e}")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


