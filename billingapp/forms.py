from django import forms
from .models import Invoice

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ["name", "mobile", "email", "gst_no", "address","country","city","pincode","state"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter customer name"}),
            "mobile": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter mobile number"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Enter email address"}),
            "gst_no": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter candidate GST number"}),
            "address": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter address"}),
            "city": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter city"}),
            "pincode": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Enter pincode"}),
            "state": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter state"}),
            "country": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter country"}),
        }