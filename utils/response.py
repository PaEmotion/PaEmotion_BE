from fastapi.responses import JSONResponse
from schemas.response import ResponseSchemas
from fastapi.encoders import jsonable_encoder

def response_success(data=None, message="요청이 성공했습니다.", status_code=200):
    return JSONResponse(
        status_code=status_code,
        content = jsonable_encoder(ResponseSchemas(success=True, message=message, data=data))
    )

def response_error(message="요청이 실패했습니다.", status_code = 400):
    return JSONResponse(
        status_code=status_code,
        content = jsonable_encoder(ResponseSchemas(success=False, message=message, data=None))
    )