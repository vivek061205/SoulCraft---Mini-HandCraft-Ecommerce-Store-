from django.test import Client, TestCase
from django.urls import reverse

from .bot import get_bot_reply
from .models import SupportTicket


class BotTests(TestCase):
    def test_shipping_intent(self):
        self.assertIn("3–5", get_bot_reply("How long does shipping take?"))

    def test_returns_intent(self):
        self.assertIn("30-day", get_bot_reply("I want a refund"))

    def test_fallback(self):
        self.assertIn("ticket", get_bot_reply("what is the meaning of life").lower())


class SupportViewsTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_support_page_renders(self):
        resp = self.client.get(reverse("support:home"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "SoulCraft Assistant")

    def test_chat_api(self):
        resp = self.client.post(
            reverse("support:chat"),
            data='{"message": "how long does shipping take?"}',
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("3–5", resp.json()["reply"])

    def test_chat_api_requires_post(self):
        resp = self.client.get(reverse("support:chat"))
        self.assertEqual(resp.status_code, 405)

    def test_chat_api_requires_csrf(self):
        csrf_client = Client(enforce_csrf_checks=True)
        resp = csrf_client.post(
            reverse("support:chat"),
            data='{"message": "hi"}',
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 403)

    def test_ticket_creation(self):
        resp = self.client.post(reverse("support:ticket"), {
            "email": "needhelp@example.com",
            "subject": "Broken mug",
            "message": "It arrived cracked.",
        })
        self.assertEqual(SupportTicket.objects.filter(email="needhelp@example.com").count(), 1)
