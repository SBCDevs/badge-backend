from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Request

with open("public/index.html", "r") as f:
    index_page = f.read()

async def handler(request: Request):
    return HTMLResponse(content=index_page)

def setup(router: APIRouter):
    router.add_route(
        path="/",
        name="Index page",
        endpoint=handler,
        methods=["GET"]
    )
