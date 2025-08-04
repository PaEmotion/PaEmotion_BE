from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

async def custom_http_exception(request:Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content= {
            "success": False,
            "message" : exc.detail,
            "data" : None
        }
    )