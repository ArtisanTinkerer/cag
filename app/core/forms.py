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
