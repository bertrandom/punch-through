import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Annotated, Optional, Union

import aiohttp
from appcfg import get_config
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class Keypress(BaseModel):
    client_id: str
    key: str

logger = logging.getLogger(__name__)

config = get_config(__name__)

session = None

@asynccontextmanager
async def lifespan(app: FastAPI):

    global session

    session = aiohttp.ClientSession()
    yield
    await session.close()

app = FastAPI(lifespan=lifespan)

def valid_request(auth: Optional[str]):

    if auth is None:
        return False

    parts = auth.split(" ")
    if len(parts) == 2 and parts[0] == "Bearer":
        token = parts[1]
        if token == config["secret"]:
            return True
    
    return False

@app.middleware("http")
async def check_authorization_header(request: Request, call_next):

    auth = request.headers.get('Authorization')

    if not valid_request(auth):
        return JSONResponse(content=None, status_code=401)
    response = await call_next(request)
    return response

@app.post("/punch")
async def punch():
    async with session.post(f"http://nuke.smittn.com/key/press", json={
        "client_id": "punch",
        "key": "KEY_GARAGE"
    }) as resp:
        response = await resp.json()
        logger.info(response)

    return {"ok": True}
