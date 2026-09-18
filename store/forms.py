from django import forms


class CheckoutForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "you@example.com", "autocomplete": "email"}),
    )
    full_name = forms.CharField(
        label="Full name",
        max_length=150,
        widget=forms.TextInput(attrs={"placeholder": "Ada Lovelace", "autocomplete": "name"}),
    )
    address = forms.CharField(
        label="Shipping address",
        widget=forms.Textarea(
            attrs={"rows": 3, "placeholder": "Street, city, postal code", "autocomplete": "street-address"}
        ),
    )
