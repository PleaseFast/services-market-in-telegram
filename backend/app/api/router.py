from fastapi import APIRouter

from app.api.v1 import (
    applications,
    auth,
    customers,
    notifications,
    projects,
    reviews,
    services,
    specialists,
    timeline,
    users,
)

api_v1 = APIRouter(prefix="/api/v1")
api_v1.include_router(auth.router)
api_v1.include_router(users.router)
api_v1.include_router(specialists.router)
api_v1.include_router(timeline.router)
api_v1.include_router(services.router)
api_v1.include_router(customers.router)
api_v1.include_router(projects.router)
api_v1.include_router(applications.router)
api_v1.include_router(reviews.router)
api_v1.include_router(notifications.router)
