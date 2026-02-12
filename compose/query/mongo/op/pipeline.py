from .base import ListExpression, Operator


class Pipeline(Operator):
    def __init__(self, *ops: Operator):
        self.ops = list(ops)

    def expression(self) -> ListExpression:
        result: ListExpression = []
        for op in self.ops:
            expr = op.expression()
            if not expr:
                continue
            if isinstance(expr, list):
                result.extend(expr)
            else:
                result.append(expr)
        return result
