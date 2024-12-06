import csv

from django.http import HttpResponse

from .models import Donation


def generate_donations_csv(month):
    """
    On the first of the month, or the month specified, generate a CSV file containing data about
    the donations.
    """
    donations = Donation.objects.filter(amount__isnull=False).exclude(title='')

    if month:
        donations = donations.filter(
            donation_date__year=month.year,
            donation_date__month=month.month,
        )

    donations = donations.order_by('-donation_date')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename=CagWashDonations.csv'

    writer = csv.writer(response)
    field_names = [
        'Title',
        'First name',
        'Last name',
        'House name or number',
        'Postcode',
        'Aggregated donations',
        'Sponsored event',
        'Donation date',
        'Amount',
    ]
    writer.writerow(field_names)

    for donation in donations:
        writer.writerow(
            [
                donation.title,
                donation.first_name,
                donation.last_name,
                donation.address,
                donation.postcode,
                '',
                '',
                donation.donation_date.strftime('%m/%d/%Y'),
                donation.amount,
            ]
        )

    return response
