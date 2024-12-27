from datetime import datetime
from django import forms

ALL_CONSTANT = 'ALL'


class ExportToCSVForm(forms.Form):
    month = forms.ChoiceField()

    def __init__(self, queryset, *args, **kwargs):
        super().__init__(*args, **kwargs)
        month_choices = (
            (ALL_CONSTANT, 'All Donations'),
            *((x, x.strftime('%b, %Y')) for x in queryset),
        )

        self.fields['month'].choices = month_choices  # type: ignore
        self.fields['month'].label = ''

    def get_month(self):
        month = self.cleaned_data.get('month')

        if month == ALL_CONSTANT:
            return None

        return datetime.strptime(month, '%Y-%m-%d')  # type: ignore

from django import forms
from .models import Donation

class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = [
            'title',
            'postcode',
            'last_name',
            'address',
            'postal_town',
        ]


        widgets = {

        }
        labels = {
            'title': 'Title',
            'postcode': 'Postcode',
            'last_name': 'Last Name',
            'address': 'Address',
            'postal_town': 'Town/City'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Debug: Print the fields and their labels during form initialization
        for field_name, field in self.fields.items():
            print(f"Field: {field_name}, ID: {field.widget.attrs.get('id', None)}")

    def clean_postcode(self):
        """Validate the format of the postcode."""
        postcode = self.cleaned_data.get('postcode')
        if len(postcode) < 5:
            raise forms.ValidationError("Postcode must be at least 5 characters long.")
        return postcode


