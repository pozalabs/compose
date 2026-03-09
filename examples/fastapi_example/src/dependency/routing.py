import inspect
import types
from collections.abc import Callable
from typing import Annotated, Any, Union, get_args, get_origin

from dishka import AsyncContainer, FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi.routing import APIRoute


def create_auto_wired_route(container: AsyncContainer) -> type[APIRoute]:
    resolvable = _collect_resolvable_types(container)

    class AutoWiredDishkaRoute(DishkaRoute):
        def __init__(self, path: str, endpoint: Callable[..., Any], **kwargs: Any):
            endpoint = _convert_signature(endpoint, resolvable)
            super().__init__(path, endpoint, **kwargs)

    return AutoWiredDishkaRoute


def _collect_resolvable_types(container: AsyncContainer) -> set[type]:
    result: set[type] = set()
    registry = container.registry
    while registry is not None:
        for key in registry.factories:
            if isinstance(key.type_hint, type):
                result.add(key.type_hint)
        registry = getattr(registry, "child_registry", None)
    result.discard(AsyncContainer)
    return result


def _is_excluded_type(hint: Any) -> bool:
    if hint is inspect.Parameter.empty or hint is Any:
        return True
    origin = get_origin(hint)
    if origin is Annotated:
        return True
    if origin is Union or origin is types.UnionType:
        return True
    return False


def _convert_signature(
    endpoint: Callable[..., Any],
    resolvable: set[type],
) -> Callable[..., Any]:
    sig = inspect.signature(endpoint)
    hints = {k: v for k, v in inspect.get_annotations(endpoint).items() if k != "return"}

    new_params = []
    new_annotations = {}
    changed = False

    for name, param in sig.parameters.items():
        hint = hints.get(name, inspect.Parameter.empty)

        if _is_excluded_type(hint):
            new_params.append(param)
            if name in hints:
                new_annotations[name] = hints[name]
            continue

        bare_type = get_args(hint)[0] if get_origin(hint) else hint
        if bare_type in resolvable:
            from_dishka = FromDishka[bare_type]
            new_params.append(
                param.replace(annotation=from_dishka, default=inspect.Parameter.empty)
            )
            new_annotations[name] = from_dishka
            changed = True
        else:
            new_params.append(param)
            if name in hints:
                new_annotations[name] = hints[name]

    if not changed:
        return endpoint

    if "return" in inspect.get_annotations(endpoint):
        new_annotations["return"] = inspect.get_annotations(endpoint)["return"]

    endpoint.__signature__ = sig.replace(parameters=new_params)
    endpoint.__annotations__ = new_annotations
    return endpoint
