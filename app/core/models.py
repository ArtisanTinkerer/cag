import uuid

from django.db import models
from django.core.validators import RegexValidator


class Donation(models.Model):
    """
    Model to store information about a donation from a customer.
    """

    class TitleChoices(models.TextChoices):
        MR = 'Mr'
        MRS = 'Mrs'
        MISS = 'Miss'
        MS = 'Ms'
        MX = 'Mx'
        DR = 'Dr'

    class Meta:
        ordering = ['-donation_date']

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    number_plate = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-z0-9 ]*$',
                message='Please only enter alphanumeric characters.',
            )
        ],
    )

    title = models.CharField(max_length=10, choices=TitleChoices.choices, blank=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    address = models.CharField(
        max_length=255, help_text='House name / number & road', blank=True
    )
    postal_town = models.CharField(max_length=255, blank=True)
    postcode = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)

    amount = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    donation_date = models.DateTimeField(auto_now_add=True)

    card_payment = models.BooleanField(null=True)
    donation_taken = models.BooleanField(default=False)
    donation_taken_date = models.DateTimeField(null=True)
    transaction_code = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f'{self.id}'

    @property
    def customer_name(self):
        if self.title:
            return ' '.join([self.title, self.first_name, self.last_name])
        return '-'
