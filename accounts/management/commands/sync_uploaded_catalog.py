from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from store.models import Category, Product, ProductImage


PRODUCTS = [
    {
        "old_name": "Carved Sheesham Wall Panel",
        "name": "Carved Teakwood Divine Wall Panel",
        "category": "Home Decor",
        "image": "3.jpeg",
        "price": "2499.00",
        "description": "Hand-carved teakwood wall art depicting a timeless divine couple. A warm, detailed statement piece for a living room or entryway.",
    },
    {
        "old_name": "Block-Print Cushion Cover",
        "name": "Embroidered Garden Wall Art",
        "category": "Home Decor",
        "image": "4.jpeg",
        "price": "1499.00",
        "description": "A cheerful textile artwork stitched with playful figures, flowers, and tactile button details. Ready to bring color to a quiet wall.",
    },
    {
        "old_name": "Brass Wrap Bangle",
        "name": "Handcrafted Leather Backpack",
        "category": "Bags & Accessories",
        "image": "5.jpeg",
        "price": "2999.00",
        "description": "A sturdy full-grain leather backpack with hand-finished straps, brass buckles, and enough room for everyday essentials.",
    },
    {
        "old_name": "Jute & Wool Table Runner",
        "name": "Handwoven Patterned Runner",
        "category": "Textiles & Woven Goods",
        "image": "6.jpeg",
        "price": "1799.00",
        "description": "A richly patterned handwoven runner with a traditional geometric motif, made to add texture and warmth to a hallway or room.",
    },
    {
        "old_name": "Hand-Glazed Serving Bowl",
        "name": "Blue Pottery Tableware Set",
        "category": "Pottery & Ceramics",
        "image": "7.jpeg",
        "price": "1899.00",
        "description": "A vivid blue-and-white pottery set with hand-painted floral details. Each piece brings artisan color to serving and display.",
    },
    {
        "old_name": "Beaded Loom Bracelet",
        "name": "Embroidered Folk Art Tote",
        "category": "Bags & Accessories",
        "image": "8.jpeg",
        "price": "1299.00",
        "description": "A roomy fabric tote decorated with colorful folk embroidery, sturdy handles, and a pattern that makes every errand feel special.",
    },
    {
        "old_name": "Brass Taper Holder Trio",
        "name": "Woven Rattan Lantern",
        "category": "Home Decor",
        "image": "9.jpeg",
        "price": "1599.00",
        "description": "A handwoven rattan lantern with a soft warm glow, shaped to bring an easy, natural mood to shelves, tables, or bedside corners.",
    },
    {
        "old_name": "Sand Mosaic Pillar Candle",
        "name": "Painted Folk Lantern",
        "category": "Home Decor",
        "image": "10.jpeg",
        "price": "899.00",
        "description": "A colorful hand-painted lantern with detailed folk motifs and a gently glowing center, made for a festive shelf or cozy nook.",
    },
    {
        "old_name": "Soy Wax Taper Pair",
        "name": "Folk Dance Wall Frame",
        "category": "Home Decor",
        "image": "img2.jpeg",
        "price": "1799.00",
        "description": "A framed folk-art scene featuring bright traditional dancers and intricate textile-inspired details. A joyful accent for an artful home.",
    },
    {
        "old_name": "Block-Printed Napkin Set",
        "name": "Ocean Resin Serving Tray",
        "category": "Home Decor",
        "image": "WhatsApp Image 2026-09-17 at 13.29.15.jpeg",
        "price": "2199.00",
        "description": "A one-of-a-kind resin tray with a turquoise ocean scene, natural wood grain, and polished gold-tone handles for serving or display.",
    },
]


class Command(BaseCommand):
    help = "Replace the placeholder storefront catalog with uploaded product images."

    @transaction.atomic
    def handle(self, *args, **options):
        media_prefix = "products/2026"
        Product.objects.update(is_active=False)
        updated = 0

        for item in PRODUCTS:
            category, _ = Category.objects.get_or_create(name=item["category"])
            product = Product.objects.filter(
                name__in=[item["old_name"], item["name"]]
            ).first()
            if not product:
                raise self.CommandError(
                    f"Could not find product '{item['old_name']}' or '{item['name']}'."
                )
            product.name = item["name"]
            product.slug = slugify(item["name"])
            product.category = category
            product.description = item["description"]
            product.price = item["price"]
            product.is_active = True
            product.cover_image.name = f"{media_prefix}/{item['image']}"
            product.save()

            ProductImage.objects.filter(product=product).delete()
            ProductImage.objects.create(
                product=product,
                image=f"{media_prefix}/{item['image']}",
                alt_text=item["name"],
                position=0,
            )
            updated += 1

        self.stdout.write(self.style.SUCCESS(f"Updated {updated} products with uploaded catalog images."))
