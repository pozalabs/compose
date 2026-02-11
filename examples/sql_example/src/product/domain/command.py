import compose


class AddProduct(compose.command.Command):
    name: str
    price: int
