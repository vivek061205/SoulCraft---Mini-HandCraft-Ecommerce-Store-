from django import forms

from .models import SupportTicket


class SupportTicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ["email", "subject", "message"]
        widgets = {
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com"}),
            "subject": forms.TextInput(attrs={"placeholder": "What's the issue?"}),
            "message": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Describe your issue and include your order number if relevant."}
            ),
        }
