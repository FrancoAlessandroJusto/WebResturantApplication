# =========================
# IMPORT
# =========================

import os
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from core.database import BASE_DIR


# =========================
# ROUTER ANALYTICS UI
# =========================

router = APIRouter(prefix="/analytics", tags=["analytics_ui"])
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


# =========================
# GET: pagina analytics (HTML)
# =========================

@router.get("/ui", response_class=HTMLResponse)
def analytics_ui(request: Request):
    return templates.TemplateResponse(
        "analytics.html",  # Uses the analytics template
        {"request": request, "pizze": [], "msg": None, "ok": True}
    )
