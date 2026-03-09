from fastapi import APIRouter

from compose.fastapi import injected_route
from src.dependency import container

router = APIRouter(route_class=injected_route(container))
