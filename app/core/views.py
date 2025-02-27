from django.views.generic import CreateView, DetailView, ListView, UpdateView, FormView
from decimal import Decimal

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DetailView, ListView, UpdateView, FormView

from .forms import DonationForm
from .mixins import StepMixin
from .models import Donation


# -------------------------------------------------------------------------------------------------
# Customer Views
# -------------------------------------------------------------------------------------------------


class Step1View(StepMixin, FormView):
    """
    Welcome page that asks the user to enter their number plate.
    """
    template_name = 'customer/step1-enter-registration.html'
    step_num = 1

    # Define the form inline in the view
    class NumberPlateForm(forms.Form):
        number_plate = forms.CharField(max_length=20)

    def get_form_class(self):
        return self.NumberPlateForm

    def form_valid(self, form):
        # Save the form data to the session instead of creating a Donation object
        self.request.session['number_plate'] = form.cleaned_data['number_plate']
        # Redirect to the next step
        return redirect(reverse('step-2-donation-amount'))

class Step2View(StepMixin, FormView):
    """
    Page for the user to enter their donation amount.
    """

    template_name = 'customer/step2-donation-amount.html'

    step_num = 2
    back_url_name = ''

    # Define the form field inline in the view todo move this
    class DonationAmountForm(forms.Form):
        amount = forms.DecimalField(max_digits=10, decimal_places=2)

    def get_form_class(self):
        return self.DonationAmountForm

    def form_valid(self, form):
        # Save the amount to the session
        self.request.session['amount'] = str(form.cleaned_data['amount'])
        # Redirect to the next step without saving to the database
        return redirect(reverse('step-3-customer-details'))


class Step3View(StepMixin, FormView):
    """
    Page for the user to select if they would like to Gift Aid their donation.

    Then add surname and postcode to search. Which then GETs to SearchResults.
    """

    template_name = 'customer/step3-customer-details.html'
    step_num = 3

    # Define the form for the customer details
    class CustomerDetailsForm(forms.Form):

        last_name = forms.CharField(max_length=50)
        postcode = forms.CharField(max_length=10)

    def get_form_class(self):
        return self.CustomerDetailsForm

    def form_valid(self, form):
        # Save the form data to the session or handle as needed
        self.request.session['customer_details'] = form.cleaned_data

        # Redirect to the next step (you can specify the URL or use reverse)
        return redirect(reverse('step-4-customer-email'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Retrieve the amount from the session and convert to Decimal
        amount = Decimal(self.request.session.get('amount', 0))  # Default to 0 if not found
        # Calculate the boost amount
        context['boost_amount'] = round(amount * Decimal(0.25), 2)

        # You can access session or other data here if needed
        #donation hasn't been created yet
        context['opt_out_link'] = reverse('step-3-are-you-sure')
        return context





class SearchResults(ListView, CreateView): #todo change this to not use ListView and CreateView
    """
    Display search results for donations or show a form to create a new one.
    """

    model = Donation
    context_object_name = 'object_list'
    form_class = DonationForm

    def get_queryset(self):
        """
        Perform the search based on GET parameters.
        """
        last_name = self.request.GET.get('last_name', '')
        postcode = self.request.GET.get('postcode', '')

        if last_name and postcode:
            return Donation.objects.filter(last_name__icontains=last_name, postcode__icontains=postcode).order_by(
                '-donation_date')[:1]
        return Donation.objects.none()

    def get_template_names(self):
        """
        Return a different template based on whether results are found.
        """
        if self.get_queryset().exists():
            return ['customer/step4-customer-search-results.html']
        #name and postcode in th context
        return ['customer/step4-customer-new.html']


    def get_context_data(self, **kwargs):
        """
        Add both the object list and form to the context for rendering.
        """
        context = {}

        # Retrieve the search parameters from GET
        last_name = self.request.GET.get('last_name', '')
        postcode = self.request.GET.get('postcode', '')


        object_list = self.get_queryset()


        if object_list.exists(): #if we have some then return the results
            context['object_list'] = object_list
        else: #else display the form
            form = self.get_form()
            form.initial = {
                'last_name': last_name,
                'postcode': postcode,
            }

            context['form'] = form

        return context


    def post(self, request, *args, **kwargs):
        """
        Handle form submissions when creating a new donation.
        """
        form = self.get_form()
        if form.is_valid():
            new_donation = form.save(commit=False)

            amount_str = self.request.session.get('amount', '0')
            number_plate = self.request.session.get('number_plate', '')
            new_donation.amount = Decimal(amount_str)
            new_donation.number_plate = number_plate
            new_donation.save()

            # Redirect to the next step with the new record's ID
            return redirect(reverse('step-4-customer-email', args=[new_donation.id]))
        # Re-render the template with errors if the form is invalid
        return self.render_to_response(self.get_context_data(form=form))







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

    def get_object(self, queryset=None):
        return get_object_or_404(Donation, pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('step-5-complete', args=[self.object.id])  # type: ignore



from .models import Donation




from django.views.generic.edit import FormView
from django.urls import reverse
from django.shortcuts import redirect
from django.utils import timezone
from django import forms
from decimal import Decimal
from .models import Donation

class Step3BView(StepMixin, FormView):
    """
    Page user is redirected to if they do not opt-in to Gift Aid.
    Here, a new Donation object is created based on session data.
    """
    template_name = 'customer/step3b-are-you-sure.html'
    step_num = 3

    class DonationForm(forms.Form):
        gift_aid = forms.BooleanField(required=False, label="Would you like to Gift Aid this donation?")

    def get_form_class(self):
        return self.DonationForm

    def dispatch(self, request, *args, **kwargs):
        """Ensure that a donation is created before rendering the form."""
        if 'donation_id' not in request.session:
            donation = self.create_donation_from_session()
            request.session['donation_id'] = str(donation.id)  # ✅ Convert UUID to string


        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Process the form submission."""
        donation_id = self.request.session.get('donation_id')
        donation = Donation.objects.get(id=donation_id)

        # Update Gift Aid preference
        donation.gift_aid = form.cleaned_data['gift_aid']
        donation.save()

        # Redirect to the next step
        return redirect(reverse('step-4-customer-email', args=[donation.id]))

    def create_donation_from_session(self):
        """Create a new Donation object from session data."""
        amount_str = self.request.session.get('amount', '0')
        number_plate = self.request.session.get('number_plate', '')
        customer_details = self.request.session.get('customer_details', {})
        last_name = customer_details.get('last_name', '')
        postcode = customer_details.get('postcode', '')

        donation = Donation.objects.create(
            amount=Decimal(amount_str),
            number_plate=number_plate,
            last_name=last_name,
            postcode=postcode,
            donation_date=timezone.now(),
        )

        return donation

    def get_context_data(self, **kwargs):
        """Pass donation-related links to the template."""
        context = super().get_context_data(**kwargs)

        donation_id = self.request.session.get('donation_id')
        if donation_id:
            context['customer_details_link'] = reverse('step-3-customer-details')
            context['customer_email_link'] = reverse('step-4-customer-email', args=[donation_id])

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
