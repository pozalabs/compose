from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.product.adapter.repository import ProductRepository
from src.product.adapter.table import metadata
from src.product.domain.command import AddProduct
from src.product.service.command_handler import AddProductHandler

from compose.uow.sql import SQLUnitOfWork


def main():
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)

    repository = ProductRepository()
    uow = SQLUnitOfWork(session_factory=session_factory)
    handler = AddProductHandler(product_repository=repository, uow=uow)

    # 상품 추가
    product1 = handler.handle(AddProduct(name="Keyboard", price=50000))
    product2 = handler.handle(AddProduct(name="Mouse", price=30000))
    product3 = handler.handle(AddProduct(name="Monitor", price=250000))
    print(f"Added: {product1.name} (id={product1.id})")
    print(f"Added: {product2.name} (id={product2.id})")
    print(f"Added: {product3.name} (id={product3.id})")

    # 단건 조회
    with session_factory() as session:
        found = repository.find_by_id(product1.id, session)
        print(f"\nFind by id({product1.id}): {found.name}, price={found.price}")

    # 이름으로 조회
    with session_factory() as session:
        found = repository.find_by_name("Mouse", session)
        print(f"Find by name('Mouse'): id={found.id}, price={found.price}")

    # 목록 조회 (가격 오름차순)
    with session_factory() as session:
        products = repository.list_by({}, session, sort=[("price", 1)])
        print("\nAll products (sorted by price asc):")
        for p in products:
            print(f"  - {p.name}: {p.price}")

    # 수정
    with session_factory() as session:
        product = repository.find_by_id(product1.id, session)
        product.update(name="Mechanical Keyboard", price=75000)
        repository.update(product, session)
        session.commit()

        updated = repository.find_by_id(product1.id, session)
        print(f"\nUpdated: {updated.name}, price={updated.price}")

    # 삭제
    with session_factory() as session:
        repository.delete(product3.id, session)
        session.commit()

        remaining = repository.list_by({}, session)
        print(f"\nAfter delete (remaining {len(remaining)}):")
        for p in remaining:
            print(f"  - {p.name}: {p.price}")


if __name__ == "__main__":
    main()
