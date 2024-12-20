from decimal import Decimal
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


from .models import Donation
from .mixins import StepMixin

from django.views.decorators.csrf import csrf_exempt


# -------------------------------------------------------------------------------------------------
# Customer Views
# -------------------------------------------------------------------------------------------------


class Step1View(StepMixin, CreateView):
    """
    Welcome page that asks the user to enter their number plate.
    """

    model = Donation
    fields = ['number_plate']
    template_name = 'customer/step1-enter-registration.html'
    step_num = 1

    def get_success_url(self):
        return reverse('step-2-donation-amount', args=[self.object.id])  # type: ignore


class Step2View(StepMixin, UpdateView):
    """
    Page for the user to enter their donation amount.
    """

    template_name = 'customer/step2-donation-amount.html'
    model = Donation
    fields = ['amount']
    step_num = 2
    back_url_name = ''

    def get_success_url(self):
        return reverse('step-3-customer-details', args=[self.object.id])  # type: ignore


class Step3View(StepMixin, UpdateView):
    """
    Page for the user to select if they would like to Gift Aid their donation.

    Then add surname and postcode to search. Which then GETs to SearchResults.
    """

    template_name = 'customer/step3-customer-details.html'
    model = Donation
    fields = ['title', 'first_name', 'last_name', 'address', 'postal_town', 'postcode']
    step_num = 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        donation = self.get_object()
        context['opt_out_link'] = reverse('step-3-are-you-sure', args=[donation.id]) #links for the buttons
        context['boost_amount'] = round(donation.amount * Decimal(0.25), 2)
        return context

    def get_success_url(self): #this is where to fo after
        return reverse('step-4-customer-search')  # type: ignore



class SearchResults(StepMixin, ListView):
    """
    Page for the user to select if they would like to Gift Aid their donation.
    """

    template_name = 'customer/step4-customer-search-results.html'
    step_num = 3


    def get_queryset(self):

       #search here using postcode and surname from previous donations
        # Get surname and postcode from the request's GET parameters
        last_name = self.request.GET.get('last_name', '')
        postcode = self.request.GET.get('postcode', '')


       # Perform the query and return the results

        if last_name and postcode:
            return Donation.objects.filter(last_name__icontains=last_name, postcode__icontains=postcode)
        return Donation.objects.none()


    def get_success_url(self):# this is where to go next - after the form has posted
        return reverse('step-4-customer-email', args=[self.object.id])  # type: ignore

# need to display the rest


class Step4View(StepMixin, UpdateView):
    """
    View to display a template showing donation has been submitted.
    """

    template_name = 'customer/step4-customer-email.html'
    model = Donation
    fields = ['email']
    step_num = 4

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)


    def get_success_url(self):
        return reverse('step-5-complete', args=[self.object.id])  # type: ignore


class Step3BView(StepMixin, DetailView):
    """
    Page user is redirected to if they do not opt-in to Gift Aid.
    """

    template_name = 'customer/step3b-are-you-sure.html'
    model = Donation
    step_num = 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        donation_id = self.get_object().id

        context['customer_details_link'] = reverse(
            'step-3-customer-details', args=[donation_id]
        )
        context['customer_email_link'] = reverse(
            'step-4-customer-email', args=[donation_id]
        )
        return context

class Step5View(StepMixin, DetailView):
    """
    View to display a template showing donation has been submitted.
    """

    template_name = 'customer/step5-complete.html'
    model = Donation
    step_num = 5


# -------------------------------------------------------------------------------------------------
# Worker Views
# -------------------------------------------------------------------------------------------------


class DonationsTodayView(LoginRequiredMixin, ListView):
    """
    Display the Donations today that have not had their money taken for yet.
    """

    template_name = 'worker/donations_list.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:  # type: ignore
            return redirect('admin:login')

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        today = timezone.now().date()
        return Donation.objects.filter(
            amount__isnull=False, donation_date__date=today, donation_taken=False
        )


class UnpaidDonationView(LoginRequiredMixin, DetailView):
    """
    Display an unpaid Donation for selection of the payment type.
    """

    template_name = 'worker/donation_view.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:  # type: ignore
            return redirect('admin:login')

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Donation.objects.filter(amount__isnull=False, donation_taken=False)

    def post(self, request, *args, **kwargs):
        """Delete the donation."""
        donation = self.get_object()
        donation.delete()
        return redirect('admin-donations-today')


def payment_complete(request, pk):
    """
    This is the endpoint in which SumUp redirects to once the payment has been taken on the card.
    It is either when the payment has succeeded or failed.

    It is also the screen which is redirected to if the user selects the cash payment.
    """
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('admin:login')

    queryset = Donation.objects.filter(donation_taken=False)
    donation = get_object_or_404(queryset, pk=pk)

    if request.GET.get('cash'):
        payment_type = 'cash'
        payment_success = True
        transaction_code = ''
    else:
        payment_type = 'card'
        payment_success = request.GET.get('smp-status') == 'success'
        transaction_code = request.GET.get('smp-tx-code', '')

    if payment_success:
        donation.card_payment = payment_type == 'card'
        donation.donation_taken = True
        donation.donation_taken_date = timezone.now()
        donation.transaction_code = transaction_code
        donation.save()

    return render(
        request,
        'worker/payment_complete.html',
        {
            'donation': donation,
            'payment_success': payment_success,
            'payment_type': payment_type,
            'transaction_code': transaction_code,
            'donations_today_href': reverse('admin-donations-today'),
        },
    )

@csrf_exempt #todo remove
def search(request):
    if request.method == 'GET':
        postcode = request.GET.get('postcode', '')
        surname = request.GET.get('surname', '')


        #search the donations table for records with this postcode and surname
        results = (Donation.objects.filter(postcode=postcode, last_name__icontains=surname)
                   .values('id', 'first_name', 'last_name', 'address', 'postcode', 'amount', 'donation_date'))



        return JsonResponse(list(results), safe=False)
    return JsonResponse({'error': 'Invalid request'}, status=400)
