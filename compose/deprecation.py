import warnings


class ComposeDeprecationWarning(UserWarning):
    pass


def deprecated_alias[T](old_name: str, new_class: type[T]) -> type[T]:
    def __init__(self, *args, **kwargs):
        warnings.warn(
            f"`{old_name}` is deprecated. Use `{new_class.__name__}` instead.",
            category=ComposeDeprecationWarning,
            stacklevel=2,
        )
        super(alias, self).__init__(*args, **kwargs)

    alias = type(old_name, (new_class,), {"__init__": __init__})
    return alias
