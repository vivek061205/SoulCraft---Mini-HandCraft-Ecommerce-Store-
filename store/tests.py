"""
Requirement 1 & 4 tests: storefront pages, cart/checkout, admin access control.

Run with:  python manage.py test store
"""

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import Category, Order, Product

User = get_user_model()


class StorefrontTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Desk")
        self.product = Product.objects.create(
            category=self.category,
            name="Test Lamp",
            description="A lamp for testing.",
            price=49.99,
            stock=10,
        )

    def test_dashboard_lists_active_products(self):
        resp = self.client.get(reverse("store:dashboard"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Test Lamp")

    def test_dashboard_search_filters(self):
        resp = self.client.get(reverse("store:dashboard"), {"q": "lamp"})
        self.assertContains(resp, "Test Lamp")
        resp = self.client.get(reverse("store:dashboard"), {"q": "zzz-nothing"})
        self.assertContains(resp, "No products found")

    def test_product_detail_page(self):
        resp = self.client.get(reverse("store:product_detail", args=[self.product.slug]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Test Lamp")
        self.assertContains(resp, "₹49.99")
        self.assertContains(resp, "Buy Now")

    def test_inactive_product_hidden(self):
        Product.objects.create(
            category=self.category, name="Hidden Item",
            description="x", price=1, stock=1, is_active=False,
        )
        resp = self.client.get(reverse("store:dashboard"))
        self.assertNotContains(resp, "Hidden Item")


class CartFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Home")
        self.product = Product.objects.create(
            category=self.category, name="Cart Widget",
            description="d", price=20.00, stock=5,
        )
        self.add_url = reverse("store:cart_add", args=[self.product.pk])
        self.cart_url = reverse("store:cart")

    def test_add_to_cart_session(self):
        resp = self.client.post(self.add_url, {"quantity": 2}, follow=True)
        self.assertEqual(resp.status_code, 200)
        session = self.client.session
        self.assertEqual(session["cart"][str(self.product.pk)], 2)

    def test_update_and_remove(self):
        self.client.post(self.add_url, {"quantity": 1})
        update_url = reverse("store:cart_update", args=[self.product.pk])
        self.client.post(update_url, {"quantity": 3})
        self.assertEqual(self.client.session["cart"][str(self.product.pk)], 3)

        remove_url = reverse("store:cart_remove", args=[self.product.pk])
        self.client.post(remove_url, {})
        self.assertNotIn(str(self.product.pk), self.client.session.get("cart", {}))

    def test_checkout_creates_order_and_clears_cart(self):
        self.client.post(self.add_url, {"quantity": 2})
        resp = self.client.post(reverse("store:checkout"), {
            "email": "shopper@example.com",
            "full_name": "Test Shopper",
            "address": "1 Test Way, Testville",
        }, follow=True)
        self.assertEqual(resp.status_code, 200)
        order = Order.objects.get(email="shopper@example.com")
        self.assertEqual(order.items.count(), 1)
        item = order.items.first()
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.unit_price, self.product.price)
        # stock decremented, cart emptied
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)
        self.assertEqual(self.client.session.get("cart"), {})

    def test_checkout_empty_cart_redirects(self):
        resp = self.client.get(reverse("store:checkout"), follow=True)
        self.assertRedirects(resp, self.cart_url)

    def test_buy_now_goes_straight_to_checkout(self):
        """Buy Now: adds the item and lands on checkout, ready to order."""
        resp = self.client.post(reverse("store:buy_now", args=[self.product.pk]),
                                {"quantity": 1})
        self.assertRedirects(resp, reverse("store:checkout"))
        self.assertEqual(self.client.session["cart"][str(self.product.pk)], 1)
        # And checkout completes the order.
        resp = self.client.post(reverse("store:checkout"), {
            "email": "buyer@example.com", "full_name": "Quick Buyer",
            "address": "2 Fast Lane",
        }, follow=True)
        self.assertTrue(Order.objects.filter(email="buyer@example.com").exists())

    def test_buy_now_out_of_stock_redirects_back(self):
        self.product.stock = 0
        self.product.save()
        resp = self.client.post(reverse("store:buy_now", args=[self.product.pk]),
                                {"quantity": 1}, follow=True)
        self.assertRedirects(
            resp, reverse("store:product_detail", args=[self.product.slug]))
        self.assertEqual(self.client.session.get("cart", {}), {})


class AdminAccessTests(TestCase):
    """Requirement 4: only staff may touch admin; customers never can."""

    def setUp(self):
        self.category = Category.objects.create(name="Kitchen")
        self.product = Product.objects.create(
            category=self.category, name="Admin Test Cup",
            description="d", price=10.00, stock=3,
        )

    def test_anonymous_redirected_from_admin(self):
        resp = self.client.get("/admin/")
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/admin/login/", resp.url)

    def test_regular_customer_cannot_access_admin(self):
        User.objects.create_user(email="cust@example.com", password="Cust-Pass-123456")
        self.client.login(email="cust@example.com", password="Cust-Pass-123456")
        resp = self.client.get("/admin/store/product/")
        # Redirected away to admin login (staff_member_required)
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/admin/login/", resp.url)

    def test_staff_can_crud_product_via_admin(self):
        User.objects.create_superuser(email="boss@example.com", password="Boss-Pass-123456")
        self.client.login(email="boss@example.com", password="Boss-Pass-123456")

        # Add page reachable, with the multi-image inline present
        resp = self.client.get("/admin/store/product/add/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Product images")   # multi-image inline present

        # Add a product through the admin change form
        form = {
            "name": "Admin Made Mug",
            "slug": "",
            "category": self.category.pk,
            "description": "Made in the admin.",
            "price": "12.50",
            "stock": "7",
            "is_active": "on",
            "images-TOTAL_FORMS": "2",
            "images-INITIAL_FORMS": "0",
            "images-MIN_NUM_FORMS": "0",
            "images-MAX_NUM_FORMS": "1000",
            "images-0-position": "0",
            "images-1-position": "1",
        }
        resp = self.client.post("/admin/store/product/add/", form, follow=True)
        self.assertEqual(resp.status_code, 200)
        product = Product.objects.get(name="Admin Made Mug")
        self.assertEqual(product.price, 12.50)

        # Edit it
        change_url = f"/admin/store/product/{product.pk}/change/"
        form["price"] = "15.00"
        form["slug"] = product.slug
        resp = self.client.post(change_url, form, follow=True)
        self.assertEqual(resp.status_code, 200)
        product.refresh_from_db()
        self.assertEqual(product.price, 15.00)

        # Delete it
        delete_url = f"/admin/store/product/{product.pk}/delete/"
        resp = self.client.post(delete_url, {"post": "yes"}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Product.objects.filter(pk=product.pk).exists())

    def test_category_admin_crud(self):
        User.objects.create_superuser(email="boss2@example.com", password="Boss-Pass-123456")
        self.client.login(email="boss2@example.com", password="Boss-Pass-123456")
        resp = self.client.post("/admin/store/category/add/", {
            "name": "Garden", "slug": "", "description": "", 
        }, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Category.objects.filter(name="Garden").exists())
