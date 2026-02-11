import compose


class AddUser(compose.command.Command):
    name: str
    email: str
