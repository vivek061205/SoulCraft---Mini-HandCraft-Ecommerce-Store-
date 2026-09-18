"""
Tiny intent-matching chatbot. Deterministic, dependency-free, safe: the user's
message is only ever regex-matched, never evaluated or rendered raw.
"""

import re

RULES = [
    (
        r"\b(order|track|shipment|delivery|package)\b",
        "You can review order status from your account profile. Orders placed in "
        "this demo are recorded immediately — staff can see them under Orders in "
        "the admin.",
    ),
    (
        r"\b(refund|return|exchange)\b",
        "Every handcrafted piece is covered by a 7-day return window. Submit a "
        "ticket below with your order number and we'll take care of it.",
    ),
    (
        r"\b(shipping|deliver|how long|arrive)\b",
        "Standard shipping takes 3–5 business days; express is 1–2 business days. "
        "Each piece is packed by hand, and you'll get a confirmation email when "
        "your order ships.",
    ),
    (
        r"\b(password|login|sign ?in|account)\b",
        "You can sign in with your email and password, or use “Continue with "
        "Google”. If you forget your password, contact us and we'll help you "
        "recover the account.",
    ),
    (
        r"\b(price|discount|coupon|promo|sale)\b",
        "Prices include all fees. Because pieces are made in small batches, we "
        "occasionally run seasonal sales — keep an eye on the collection page.",
    ),
    (
        r"\b(pottery|ceramic|jewelry|candle|handmade|artisan|craft|care)\b",
        "Each piece is shaped by hand, so small variations in glaze, grain or "
        "finish are part of its character. Wipe ceramics with a soft cloth and "
        "keep candles out of drafts — ask us anything else below!",
    ),
    (
        r"\b(hello|hi|hey|help)\b",
        "Hi there! I can help with orders, shipping, returns, or caring for your "
        "handcrafted pieces. What do you need?",
    ),
]

FALLBACK = (
    "I'm not sure about that one. Please submit a ticket below and a human "
    "from the SoulCraft studio will get back to you by email."
)


def get_bot_reply(message: str) -> str:
    text = (message or "").lower()
    for pattern, reply in RULES:
        if re.search(pattern, text):
            return reply
    return FALLBACK
