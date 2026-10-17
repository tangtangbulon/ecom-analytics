# 1. 导入 FastAPI 框架
from fastapi import FastAPI
from routers import router



# 2. 创建 FastAPI 实例，通常命名为 app
app = FastAPI()

app.include_router(router)




