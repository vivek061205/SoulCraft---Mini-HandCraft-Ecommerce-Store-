"""
Storefront views (Requirement 1 pages: Dashboard, Product Detail, Cart, Checkout).
"""

from django.contrib import messages
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render

from .cart import Cart
from .forms import CheckoutForm
from .models import Category, Order, OrderItem, Product


def dashboard(request):
    """Home / catalog page."""
    query = (request.GET.get("q") or "").strip()
    category_slug = request.GET.get("category") or ""

    products = Product.objects.filter(is_active=True).select_related("category")
    categories = Category.objects.all()

    if category_slug:
        products = products.filter(category__slug=category_slug)
    if query:
        products = products.filter(name__icontains=query)

    return render(
        request,
        "store/dashboard.html",
        {
            "products": products,
            "categories": categories,
            "active_category": category_slug,
            "query": query,
        },
    )


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("category").prefetch_related("images"),
        slug=slug,
        is_active=True,
    )
    related = (
        Product.objects.filter(category=product.category, is_active=True)
        .exclude(pk=product.pk)[:4]
    )
    return render(
        request,
        "store/product_detail.html",
        {"product": product, "related": related},
    )


def buy_now(request, product_id):
    """Add the item to the cart and go straight to checkout."""
    if request.method != "POST":
        return redirect("store:dashboard")
    cart = Cart(request)
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    if not product.in_stock:
        messages.error(request, "Sorry, that piece is out of stock.")
        return redirect("store:product_detail", slug=product.slug)
    quantity = request.POST.get("quantity", 1)
    cart.add(product.pk, quantity)
    return redirect("store:checkout")


def cart_view(request):
    cart = Cart(request)
    items = list(cart)
    return render(
        request,
        "store/cart.html",
        {"items": items, "subtotal": cart.subtotal()},
    )


def cart_add(request, product_id):
    if request.method != "POST":
        return redirect("store:dashboard")
    cart = Cart(request)
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    quantity = request.POST.get("quantity", 1)
    if product.in_stock:
        cart.add(product.pk, quantity)
        messages.success(request, f"Added “{product.name}” to your cart.")
    else:
        messages.error(request, "Sorry, that item is out of stock.")
    return redirect(request.POST.get("next") or "store:cart")


def cart_update(request, product_id):
    if request.method != "POST":
        return redirect("store:cart")
    cart = Cart(request)
    quantity = int(request.POST.get("quantity", 1))
    if quantity <= 0:
        cart.remove(product_id)
    else:
        cart.add(product_id, quantity, replace=True)
    return redirect("store:cart")


def cart_remove(request, product_id):
    if request.method != "POST":
        return redirect("store:cart")
    Cart(request).remove(product_id)
    return redirect("store:cart")


def checkout_view(request):
    cart = Cart(request)
    items = list(cart)
    if not items:
        messages.info(request, "Your cart is empty.")
        return redirect("store:cart")

    form = CheckoutForm(request.POST or None, initial={"email": getattr(request.user, "email", "") or ""})
    if request.method == "POST" and form.is_valid():
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            email=form.cleaned_data["email"],
            full_name=form.cleaned_data["full_name"],
            address=form.cleaned_data["address"],
        )
        total = 0
        for product, qty, line_total in items:
            OrderItem.objects.create(
                order=order, product=product, quantity=qty, unit_price=product.price
            )
            Product.objects.filter(pk=product.pk).update(stock=F("stock") - qty)
            total += line_total
        order.total = total
        order.save(update_fields=["total"])
        cart.clear()
        messages.success(request, f"Order #{order.pk} placed! (Demo checkout — no payment was charged.)")
        return redirect("store:dashboard")

    return render(
        request,
        "store/checkout.html",
        {"form": form, "items": items, "subtotal": cart.subtotal()},
    )

