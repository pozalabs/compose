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
        new_class.__init__(self, *args, **kwargs)

    return type(old_name, (new_class,), {"__init__": __init__})  # type: ignore[return-value]
