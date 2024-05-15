import pydantic

IS_PYDANTIC_V2 = int(pydantic.VERSION.split(".")[0]) >= 2
