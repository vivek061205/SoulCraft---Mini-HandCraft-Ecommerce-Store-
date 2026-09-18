"""
Requirement 4: Django Admin customized for product management.

- Admin can add/edit/delete products (name, description, price, stock,
  category, MULTIPLE images via ProductImageInline).
- Categories managed the same way (add/edit/delete).
- Access control is Django's own: only staff/superusers can reach /admin/
  (admin.site.login + staff_member_required internally). Regular customers
  created through signup get is_staff=False and can never see these screens.

The admin is themed to match the storefront via config/settings.AURORA_THEME
(see templates/admin/base_site.html).
"""

from django.contrib import admin
from django.forms import ModelForm
from django.utils.html import format_html

from .models import Category, Order, OrderItem, Product, ProductImage


class ProductImageForm(ModelForm):
    """Treat gallery rows with no uploaded file as 'not filled in' so saving
    a product from the admin never creates empty image records."""

    class Meta:
        model = ProductImage
        fields = "__all__"

    def clean(self):
        cleaned = super().clean()
        has_file = bool(cleaned.get("image")) or bool(
            self.instance and self.instance.pk and self.instance.image
        )
        if not has_file:
            # Mark the row deleted so the formset skips it entirely.
            cleaned["DELETE"] = True
        return cleaned


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    form = ProductImageForm
    extra = 2
    fields = ("image", "alt_text", "position")
    readonly_fields = ("preview",)

    @admin.display(description="Preview")
    def preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" style="height:56px;border-radius:8px;" alt="{}" />',
                obj.image.url,
                obj.alt_text or "",
            )
        return "—"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "product_count", "created_at")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}

    @admin.display(description="Products")
    def product_count(self, obj):
        return obj.products.count()


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "thumbnail",
        "name",
        "category",
        "price",
        "stock",
        "is_active",
        "image_count",
        "updated_at",
    )
    list_filter = ("is_active", "category", "created_at")
    list_editable = ("price", "stock", "is_active")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline]
    date_hierarchy = "created_at"
    list_per_page = 25

    fieldsets = (
        (None, {
            "fields": ("name", "slug", "category", "description"),
        }),
        ("Pricing & inventory", {
            "fields": ("price", "stock", "is_active"),
        }),
        ("Media", {
            "fields": ("cover_image",),
            "description": "Optional hero image. Additional gallery images can be added below.",
        }),
    )

    @admin.display(description="Image")
    def thumbnail(self, obj):
        url = obj.primary_image
        if url:
            return format_html(
                '<img src="{}" style="height:40px;width:40px;object-fit:cover;border-radius:8px;" />', url
            )
        return "—"

    @admin.display(description="Gallery")
    def image_count(self, obj):
        return obj.images.count()

    actions = ["activate_products", "deactivate_products"]

    @admin.action(description="Mark selected products as active")
    def activate_products(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description="Mark selected products as inactive (hidden)")
    def deactivate_products(self, request, queryset):
        queryset.update(is_active=False)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "unit_price")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "full_name", "status", "total", "created_at")
    list_filter = ("status",)
    search_fields = ("email", "full_name")
    inlines = [OrderItemInline]
    list_editable = ("status",)
