"""
Support center + lightweight rule-based chatbot.

The bot answers from a small intent map (support/bot.py) and always offers
escalation to a human ticket. The chat API is a CSRF-protected JSON endpoint.
"""

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .bot import get_bot_reply
from .forms import SupportTicketForm
from .models import SupportTicket


def support_home(request):
    return render(
        request,
        "support/support.html",
        {"form": SupportTicketForm()},
    )


@require_POST
def chat_api(request):
    """POST {message: str} -> {reply: str}. CSRF-checked by middleware."""
    import json

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"reply": get_bot_reply("")}, status=400)

    message = str(payload.get("message", ""))[:500]
    return JsonResponse({"reply": get_bot_reply(message)})


def ticket_create(request):
    if request.method != "POST":
        return render(request, "support/support.html", {"form": SupportTicketForm()})

    form = SupportTicketForm(request.POST)
    if form.is_valid():
        ticket = form.save(commit=False)
        if request.user.is_authenticated:
            ticket.user = request.user
            ticket.email = ticket.email or request.user.email
        ticket.save()
        return render(
            request,
            "support/support.html",
            {"form": SupportTicketForm(), "ticket_created": True},
        )
    return render(request, "support/support.html", {"form": form})
