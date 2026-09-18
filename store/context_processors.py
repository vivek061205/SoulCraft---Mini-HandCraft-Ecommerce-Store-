def cart_count(request):
    """Context processor: badge count for the cart icon in the navbar."""
    try:
        from .cart import Cart

        return {"cart_count": Cart(request).count()}
    except Exception:
        return {"cart_count": 0}
