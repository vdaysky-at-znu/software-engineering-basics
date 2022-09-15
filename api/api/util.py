from fastapi.responses import JSONResponse, Response
from pydantic.main import BaseModel


def response(
        http_status=None,
        message=None,
        data=None,
        error=None,
        error_code=None,
):
    http_status_class = http_status // 100
    if http_status_class == 2:
        api_status = 1
    elif http_status_class == 5:
        api_status = -1
    else:
        api_status = 0

    content = {
        'status': api_status,
        'message': message,
    }

    if data:
        content['data'] = data

    if error:
        # TODO: Rename to `error` when handling errors
        content['message'] = error
        if error_code:
            content['error_code'] = error_code

    return JSONResponse(status_code=http_status, content=content)


class OrmBaseModel(BaseModel):
    class Config:
        orm_mode = True
