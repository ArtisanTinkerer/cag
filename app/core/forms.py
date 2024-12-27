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
            'first_name',
            'last_name',
            'address',
            'postal_town',
            'postcode',
            'email',
        ]

        # { % include
        # 'widgets/forms/select.html'
        # with field=form.title required=True %}  # }
        # { % include
        # 'widgets/forms/input.html'
        # with field=form.postcode required=True %}
        # { % include
        # 'widgets/forms/input.html'
        # with field=form.last_name required=True %}


#{  # {% include 'widgets/forms/input.html' with field=form.address required=True %}#}
 #   {  # {% include 'widgets/forms/input.html' with field=form.postal_town required=True %}#}
  #      {  # {% include 'widgets/forms/input.html' with field=form.postcode required=True %}#}


        widgets = {

            'title': forms.Select(
                attrs={
                    'class': 'form-select',
                    'placeholder': 'Select your title'
                },
                template_name='widgets/forms/select.html'  # Specify your custom template
            ),

            'postcode': forms.Select(
                attrs={
                    'class': 'form-select',
                    'placeholder': 'Postcode'
                },
                template_name='widgets/forms/input.html'  # Specify your custom template
            ),



        }
        labels = {
            'title': 'Title',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'address': 'Address',
            'postal_town': 'Town/City',
            'postcode': 'Postcode',
            'email': 'Email Address',
        }

    def clean_postcode(self):
        """Validate the format of the postcode."""
        postcode = self.cleaned_data.get('postcode')
        if len(postcode) < 5:
            raise forms.ValidationError("Postcode must be at least 5 characters long.")
        return postcode

    def clean_email(self):
        """Validate that the email is properly formatted."""
        email = self.cleaned_data.get('email')
        if email and '@' not in email:
            raise forms.ValidationError("Please enter a valid email address.")
        return email

