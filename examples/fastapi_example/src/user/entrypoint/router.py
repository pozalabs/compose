from fastapi import APIRouter

from src.dependency import container
from src.dependency.routing import create_auto_wired_route

router = APIRouter(route_class=create_auto_wired_route(container))
