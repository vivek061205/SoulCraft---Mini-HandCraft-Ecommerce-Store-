"""
Seed demo content so every page has something to show:

    python manage.py seed_data

Creates (idempotently):
- superuser  admin@soulcraft.test / AdminPass!2345   (change in production!)
- customer   demo@soulcraft.test / DemoPass!2345
- 5 handcrafted categories and 15 products with generated placeholder images.
- Legacy Aurora Goods demo users are renamed to the new domain if present.
"""

import io

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from store.models import Category, Product, ProductImage

CATALOG = {
    "Pottery & Ceramics": [
        ("Studio Stoneware Mug", 649.00, "Wheel-thrown stoneware mug with a satin reactive glaze. Holds 350 ml and feels just right in the hand.", 24),
        ("Hand-Glazed Serving Bowl", 1149.00, "Generous ceramic bowl in a speckled matte glaze — each one pools color differently. Oven and dishwasher friendly.", 15),
        ("Terracotta Planter", 499.00, "Unglazed terracotta with a drainage tray; breathes with the soil and ages beautifully. Fits 4-inch nursery pots.", 30),
    ],
    "Handmade Jewelry": [
        ("Brass Wrap Bangle", 899.00, "Hand-forged brass bangle, hammered for texture and polished soft. Adjusts gently to fit. Tarnishes warmly with wear.", 20),
        ("Silver Drop Earrings", 1299.00, "Sterling silver drops with a brushed finish, hung on hand-formed ear wires. Feather-light for all-day wear.", 18),
        ("Beaded Loom Bracelet", 749.00, "Glass beads woven on a loom in earthy desert tones, finished with a brass clasp.", 35),
    ],
    "Home Decor": [
        ("Carved Sheesham Wall Panel", 2499.00, "Floral lattice carved by hand into sheesham wood. Arrives ready to hang with a natural oil finish.", 8),
        ("Block-Print Cushion Cover", 599.00, "Cotton canvas printed with hand-carved wooden blocks and natural dyes; hidden zip closure. 45 × 45 cm.", 40),
        ("Brass Taper Holder Trio", 1049.00, "Cast brass holders in three rising heights, hand-polished to a soft glow. Candles not included.", 12),
    ],
    "Candles & Fragrance": [
        ("Soy Wax Taper Pair", 449.00, "Hand-poured soy tapers with cotton wicks — a calm, clean burn of roughly six hours each.", 48),
        ("Sand Mosaic Pillar Candle", 699.00, "Pillar candle wrapped in layered desert sands, set in a reusable glass vessel.", 25),
        ("Lemongrass Room Spray", 399.00, "Essential-oil room spray with lemongrass and vetiver. No synthetic fixatives; shake and mist.", 60),
    ],
    "Textiles & Woven Goods": [
        ("Handloom Cotton Throw", 1899.00, "Woven on wooden handlooms in soft cotton checks — light, breathable, and softer with every wash. 130 × 180 cm.", 14),
        ("Jute & Wool Table Runner", 999.00, "Jute warp with wool weft in a herringbone path; hand-finished fringe. 35 × 180 cm.", 22),
        ("Block-Printed Napkin Set", 649.00, "Set of four cotton napkins printed with hand-carved blocks and mordant-dyed in warm ochre.", 50),
    ],
}

PALETTES = [
    ("#8b6f47", "#f4ecdd"),   # toasted creme
    ("#e8a13a", "#fdf3e3"),   # warm amber
    ("#a9825f", "#f6efe2"),   # camel
    ("#6f5738", "#efe6d6"),   # deep creme
]


def make_image(text, fg, bg, size=(800, 600)):
    """Generate a simple branded placeholder image with Pillow."""
    from PIL import Image, ImageDraw

    img = Image.new("RGB", size, bg)
    draw = ImageDraw.Draw(img)
    # Soft geometric accent
    draw.ellipse([size[0] * 0.55, -size[1] * 0.25, size[0] * 1.25, size[1] * 0.75], fill=fg)
    draw.rectangle([40, size[1] - 90, 40 + 8 * min(len(text), 18), size[1] - 60], fill=fg)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=88)
    return ContentFile(buf.getvalue())


class Command(BaseCommand):
    help = "Seed demo categories, handcrafted products (with images), and users."

    def handle(self, *args, **options):
        User = get_user_model()

        # Users ------------------------------------------------------------
        # Rename any legacy Aurora Goods demo users so old DBs rebrand cleanly.
        for old, new in (
            ("admin@aurora.test", "admin@soulcraft.test"),
            ("demo@aurora.test", "demo@soulcraft.test"),
        ):
            legacy = User.objects.filter(email=old).first()
            if legacy:
                if not User.objects.filter(email=new).exists():
                    legacy.email = new
                    legacy.save()
                    self.stdout.write(f"Renamed {old} -> {new}")

        if not User.objects.filter(email="admin@soulcraft.test").exists():
            User.objects.create_superuser(
                email="admin@soulcraft.test",
                password="AdminPass!2345",
                first_name="SoulCraft",
                last_name="Studio",
            )
            self.stdout.write(self.style.SUCCESS("Created superuser admin@soulcraft.test / AdminPass!2345"))
        if not User.objects.filter(email="demo@soulcraft.test").exists():
            User.objects.create_user(
                email="demo@soulcraft.test",
                password="DemoPass!2345",
                first_name="Demo",
                last_name="Shopper",
            )
            self.stdout.write(self.style.SUCCESS("Created customer demo@soulcraft.test / DemoPass!2345"))

        # Catalog ----------------------------------------------------------
        product_count = 0
        for ci, (cat_name, products) in enumerate(CATALOG.items()):
            category, _ = Category.objects.get_or_create(name=cat_name)
            fg, bg = PALETTES[ci % len(PALETTES)]

            for name, price, description, stock in products:
                product, created = Product.objects.get_or_create(
                    name=name,
                    defaults={
                        "category": category,
                        "price": price,
                        "description": description,
                        "stock": stock,
                    },
                )
                if not created:
                    continue
                product_count += 1

                # Cover image
                fname = f"{product.slug}-cover.jpg"
                product.cover_image.save(fname, make_image(name, fg, bg), save=False)
                product.save()

                # Two gallery images per product
                for pos in range(2):
                    img = ProductImage(product=product, position=pos, alt_text=f"{name} view {pos + 1}")
                    img.image.save(
                        f"{product.slug}-{pos}.jpg",
                        make_image(name, fg if pos else bg, bg if pos else fg),
                        save=True,
                    )

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {product_count} handcrafted pieces across {len(CATALOG)} categories."
        ))
