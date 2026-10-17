from contextlib import contextmanager
from decimal import localcontext


@contextmanager
def cost_precision():
    # Nested recipes multiply quantities by eight-decimal unit costs. Keep
    # these intermediates exact before any final presentation rounding.
    with localcontext() as context:
        context.prec = 80
        yield

