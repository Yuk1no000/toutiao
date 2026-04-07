from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


def success_response(message: str = "success", data=None):
    content = {
        "code": 200,
        "message": message,
        "data": data
    }
    # 目标：把任何的FastAPI,Pydantic,ORM对象都正常相应，转换成JSON格式
    return JSONResponse(content=jsonable_encoder(content))
