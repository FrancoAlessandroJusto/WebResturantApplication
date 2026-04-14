# =========================
# IMPORT
# =========================

import os
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from core.database import get_conn, BASE_DIR

# =========================
# ROUTER INGREDIENTI MANAGEMENT UI
# =========================

router = APIRouter(prefix="/ingredienti", tags=["ingredienti_management_ui"])
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# =========================
# GET: pagina ingredienti management (HTML)
# =========================

@router.get("/ui", response_class=HTMLResponse)
def ingredienti_management_ui(request: Request):
    """
    Renderizza la pagina dedicata alla gestione ingredienti
    """
    return templates.TemplateResponse(
        "ingredienti_management.html",
        {"request": request}
    )
