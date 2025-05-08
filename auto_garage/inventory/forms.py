from django import forms
from .models import Vehicle, Part, Bill


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['owner_name', 'model', 'registration_number', 'description', 'service_date']
        widgets = {
            'service_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class PartForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = ['name', 'category', 'serial_number', 'quantity', 'price']

class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['bill_number', 'customer_name', 'vehicle', 'date', 'total_amount', 'status', 'description', 'parts_used']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'parts_used': forms.SelectMultiple(attrs={'class': 'form-control'})
        }
