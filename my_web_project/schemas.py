from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


# 把 dataclass 升级成 Pydantic 的 BaseModel
class Order(BaseModel):
    order_id: str
    sku: str
    price: float
    quantity: int = Field(default=1, gt=0)


class OrderQuery(BaseModel):
    start_date: date
    end_date: date
    sku: Optional[str] = None


class SalesSummary(BaseModel):
    sku: str
    total_quantity: int
    total_revenue: float
