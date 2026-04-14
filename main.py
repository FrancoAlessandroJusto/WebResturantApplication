from fastapi import FastAPI

from core.database import init_db

# Import UI routes
from routes.ui.management import router as management_ui_router
from routes.ui.ingredienti_management import router as ingredienti_management_ui_router
from routes.ui.orders import router as orders_ui_router
from routes.ui.analytics import router as analytics_ui_router

# Import API routes
from routes.api.menu import router as menu_api_router
from routes.api.ingredienti import router as ingredienti_api_router
from routes.api.orders import router as orders_api_router
from routes.api.analytics import router as analytics_api_router

app = FastAPI(title="Pizzeria - Management System")

@app.on_event("startup")
def startup():
    init_db()

# Include UI routes
app.include_router(management_ui_router)
app.include_router(ingredienti_management_ui_router)
app.include_router(orders_ui_router)
app.include_router(analytics_ui_router)

# Include API routes
app.include_router(menu_api_router)
app.include_router(ingredienti_api_router)
app.include_router(orders_api_router)
app.include_router(analytics_api_router)

# Include order modifications routes
from routes.api.order_modifications import router as order_modifications_router
app.include_router(order_modifications_router, prefix="/api/v1")

