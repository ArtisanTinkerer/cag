from django.contrib import admin, messages
from django.urls import reverse_lazy
from django.contrib.auth.models import Group
from django.urls import path
from django.shortcuts import redirect, render

from core.forms import ExportToCSVForm

from .models import Donation
from .utils import generate_donations_csv


admin.site.site_url = reverse_lazy('admin-donations-today')
admin.site.site_header = 'Challenge Adventure Group Car Wash'
admin.site.unregister(Group)


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            'Customer',
            {
                'fields': (
                    'number_plate',
                    'title',
                    'first_name',
                    'last_name',
                    'address',
                    'postal_town',
                    'postcode',
                )
            },
        ),
        (
            'Donation',
            {'fields': ('amount', 'donation_date')},
        ),
        (
            'Payment',
            {'fields': ('card_payment', 'donation_taken', 'donation_taken_date')},
        ),
    )
    readonly_fields = ['id', 'donation_date', 'donation_taken_date']
    list_display = [
        'amount',
        'client_full_name',
        'number_plate',
        'donation_date',
        'card_payment',
        'donation_taken',
    ]
    search_fields = [
        'id',
        'amount',
        'donation_date',
        'first_name',
        'last_name',
        'number_plate',
    ]
    list_filter = [
        'donation_taken',
        'donation_date',
    ]
    change_list_template = 'admin/core/donation_change_list.html'

    def client_full_name(self, obj):
        return obj.first_name + ' ' + obj.last_name

    def get_urls(self):
        urls = [
            path(
                'export/',
                self.admin_site.admin_view(self.export_as_csv_view),
                name='donations_to_csv',
            ),
        ]
        urls += super().get_urls()
        return urls

    def export_as_csv_view(self, request):
        donation_months = Donation.objects.all().dates(
            'donation_date', 'month', order='DESC'
        )

        if request.method == 'POST':
            form = ExportToCSVForm(donation_months, data=request.POST)
            if form.is_valid():
                response = generate_donations_csv(form.get_month())
                return response
            else:
                message = 'Something went wrong when trying to export donations. Please try again.'
                self.message_user(request, message, level=messages.ERROR)
                return redirect('admin:core_donation_changelist')
        else:
            context = {
                'has_permission': True,  # Needed to show user links
                'form': ExportToCSVForm(donation_months),
            }
            return render(request, 'admin/core/export_as_csv.html', context)
