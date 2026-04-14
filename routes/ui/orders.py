# =========================
# IMPORT
# =========================

import os
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from core.database import BASE_DIR


# =========================
# ROUTER ORDERS UI
# =========================

router = APIRouter(prefix="/orders", tags=["orders_ui"])
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


# =========================
# GET: pagina orders (HTML)
# =========================

@router.get("/ui", response_class=HTMLResponse)
def orders_ui(request: Request):
    return templates.TemplateResponse(
        "orders.html",  # Uses the orders template
        {"request": request, "pizze": [], "msg": None, "ok": True}
    )
