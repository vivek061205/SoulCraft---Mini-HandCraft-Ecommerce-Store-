"""
Session-based shopping cart (Requirement: Cart page).

Stored in request.session so it works for anonymous visitors; converted to an
Order at checkout.
"""

from decimal import Decimal

from .models import Product

CART_SESSION_KEY = "cart"


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if cart is None:
            cart = self.session[CART_SESSION_KEY] = {}
        self.cart = cart

    def save(self):
        self.session.modified = True

    def add(self, product_id, quantity=1, replace=False):
        pid = str(product_id)
        try:
            qty = int(quantity)
        except (TypeError, ValueError):
            qty = 1
        qty = max(1, min(qty, 99))
        if replace:
            self.cart[pid] = qty
        else:
            self.cart[pid] = self.cart.get(pid, 0) + qty
        self.save()

    def remove(self, product_id):
        pid = str(product_id)
        if pid in self.cart:
            del self.cart[pid]
            self.save()

    def clear(self):
        self.session[CART_SESSION_KEY] = {}
        self.cart = self.session[CART_SESSION_KEY]
        self.save()

    def iter_items(self):
        """Yields (product, quantity, line_total) for items still for sale."""
        ids = [int(pid) for pid in self.cart.keys()]
        products = {
            p.pk: p for p in Product.objects.filter(pk__in=ids, is_active=True)
        }
        stale = []
        for pid_s, qty in self.cart.items():
            product = products.get(int(pid_s))
            if product is None:
                stale.append(pid_s)
                continue
            price = product.price
            yield product, qty, price * qty
        if stale:
            for pid_s in stale:
                self.cart.pop(pid_s, None)
            self.save()

    def __iter__(self):
        return self.iter_items()

    def count(self):
        return sum(qty for _, qty in self.cart.items())

    def subtotal(self):
        return sum((line_total for _, _, line_total in self.iter_items()), Decimal("0.00"))
