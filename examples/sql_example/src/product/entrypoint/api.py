from dependency_injector.wiring import inject
from fastapi import Depends
from sqlalchemy.orm import sessionmaker
from src import constants
from src.dependency import provide
from src.product import schema, service
from src.product.adapter.repository import ProductRepository

import compose

from .router import router


@router.get(
    "/v1/products/{product_id}",
    response_model=schema.Product,
    tags=[constants.OpenApiTag.PRODUCT],
    summary="상품 조회",
)
@inject
def retrieve_product(
    product_id: int,
    product_repository: ProductRepository = Depends(provide(ProductRepository)),
    session_factory: sessionmaker = Depends(provide(sessionmaker)),
):
    with session_factory() as session:
        if (product := product_repository.find_by_id(product_id, session)) is None:
            raise compose.exceptions.DoesNotExistError()

        return schema.Product.model_validate(product.model_dump(mode="json"))


@router.get(
    "/v1/products",
    response_model=list[schema.Product],
    tags=[constants.OpenApiTag.PRODUCT],
    summary="상품 목록 조회",
)
@inject
def list_products(
    name: str | None = None,
    product_repository: ProductRepository = Depends(provide(ProductRepository)),
    session_factory: sessionmaker = Depends(provide(sessionmaker)),
):
    filter_ = {}
    if name is not None:
        filter_["name"] = name

    with session_factory() as session:
        products = product_repository.list_by(filter_, session)
        return [schema.Product.model_validate(p.model_dump(mode="json")) for p in products]


@router.post(
    "/v1/products",
    response_model=schema.Product,
    tags=[constants.OpenApiTag.PRODUCT],
    summary="상품 추가",
)
@inject
def add_product(
    cmd: service.command.AddProduct,
    handler: service.AddProductHandler = Depends(provide(service.AddProductHandler)),
):
    return handler.handle(cmd)
