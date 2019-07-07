import re
from uuid import uuid4

import aiotask_context as context
from aiohttp import web

from .exceptions import TitleExplorerException

ID_HEADER = 'X-Request-ID'
ID_PATTERN = re.compile(r'^[0-9a-z]+$')


@web.middleware
async def request_id_middleware(request: web.Request, handler):
    request_id = request.headers.get(ID_HEADER)
    if not request_id or not ID_PATTERN.match(request_id):
        request_id = str(uuid4())
    request['request_id'] = request_id
    context.set('request_id', request_id)

    response = await handler(request)
    response.headers[ID_HEADER] = request_id
    return response


@web.middleware
async def exception_filter(request: web.Request, handler):
    try:
        response = await handler(request)
        if response.status != 404:
            return response

    except TitleExplorerException as e:
        res = web.json_response({
            'error': e.message,
            'status': e.status_code
        }, status=e.status_code)

    except web.HTTPException as ex:
        if ex.status != 404:
            raise
        message = ex.reason
        res = web.json_response({
            'error': message,
            'status': 404
        }, status=404)
    return res
