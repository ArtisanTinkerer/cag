from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model

from ..models import Donation

User = get_user_model()


class Step1ViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('step-1-enter-registration'))

        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('step-1-enter-registration'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'customer/step1-enter-registration.html')  # type: ignore

    def test_step_in_context(self):
        response = self.client.get(reverse('step-1-enter-registration'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['step_num'], 1)  # type: ignore

    def test_form_invalid_no_number_plate_supplied(self):
        # Test when the number plate does not just contain letters and numbers.
        response = self.client.post(
            reverse('step-1-enter-registration'),
            data={'number_plate': ''},
        )

        # Should redirect if successful.
        self.assertEqual(response.status_code, 200)

    def test_form_invalid_number_plate_container_non_alphanumeric(self):
        response = self.client.post(
            reverse('step-1-enter-registration'),
            data={'number_plate': 'ABC!!!'},
        )

        # Should redirect if successful.
        self.assertEqual(response.status_code, 200)

    def test_form_valid(self):
        self.assertFalse(Donation.objects.exists())

        response = self.client.post(
            reverse('step-1-enter-registration'),
            data={'number_plate': 'ABC123'},
        )

        self.assertTrue(Donation.objects.exists())
        self.assertEqual(Donation.objects.count(), 1)

        donation_id = Donation.objects.get().id
        self.assertRedirects(
            response, expected_url=reverse('step-2-donation-amount', args=[donation_id])  # type: ignore
        )


class Step2ViewTest(TestCase):
    def setUp(self):
        self.donation = Donation.objects.create(number_plate='DB1 007')

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(f'/step-2/donation/{self.donation.id}/')

        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(
            reverse('step-2-donation-amount', args=[self.donation.id])
        )

        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(
            reverse('step-2-donation-amount', args=[self.donation.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'customer/step2-donation-amount.html')  # type: ignore

    def test_step_in_context(self):
        response = self.client.get(
            reverse('step-2-donation-amount', args=[self.donation.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['step_num'], 2)  # type: ignore

    def test_form_valid(self):
        self.assertEqual(Donation.objects.count(), 1)
        self.assertIsNone(self.donation.amount)

        data = {'amount': 10.49}
        response = self.client.post(
            reverse('step-2-donation-amount', args=[self.donation.id]), data=data
        )

        self.assertEqual(Donation.objects.count(), 1)

        donation = Donation.objects.get()

        self.assertRedirects(
            response, expected_url=reverse('step-3-customer-details', args=[donation.id])  # type: ignore
        )

        self.assertEqual(float(donation.amount), 10.49)


class Step3ViewTest(TestCase):
    def setUp(self):
        self.donation = Donation.objects.create(
            number_plate='DB1 007',
            amount=10,
        )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(f'/step-3/gift-aid/{self.donation.id}/')

        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(
            reverse('step-3-customer-details', args=[self.donation.id])
        )

        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(
            reverse('step-3-customer-details', args=[self.donation.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'customer/step3-customer-details.html')  # type: ignore

    def test_step_in_context(self):
        response = self.client.get(
            reverse('step-3-customer-details', args=[self.donation.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['step_num'], 3)  # type: ignore

    def test_context_data(self):
        response = self.client.get(
            reverse('step-3-customer-details', args=[self.donation.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['opt_out_link'])  # type: ignore
        self.assertEqual(float(response.context['boost_amount']), float(self.donation.amount) * 0.25)  # type: ignore

    def test_form_valid(self):
        data = {
            'title': Donation.TitleChoices.MR,
            'first_name': 'Max',
            'last_name': 'Wilkinson',
            'address': '123 Random Street',
            'postal_town': 'London',
            'postcode': 'AB12 1CD',
        }
        response = self.client.post(
            reverse('step-3-customer-details', args=[self.donation.id]),
            data=data,
        )

        self.assertEqual(Donation.objects.count(), 1)

        donation = Donation.objects.get()

        self.assertRedirects(
            response, expected_url=reverse('step-4-customer-email', args=[donation.id])  # type: ignore
        )

        self.assertEqual(donation.title, data['title'])
        self.assertEqual(donation.first_name, data['first_name'])
        self.assertEqual(donation.last_name, data['last_name'])
        self.assertEqual(donation.address, data['address'])
        self.assertEqual(donation.postal_town, data['postal_town'])
        self.assertEqual(donation.postcode, data['postcode'])


class Step3BViewTest(TestCase):
    def setUp(self):
        self.donation = Donation.objects.create(
            number_plate='DB1 007',
            amount=10,
        )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(f'/step-3/are-you-sure/{self.donation.id}/')

        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(
            reverse('step-3-are-you-sure', args=[self.donation.id])
        )

        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(
            reverse('step-3-are-you-sure', args=[self.donation.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'customer/step3b-are-you-sure.html')  # type: ignore

    def test_step_in_context(self):
        response = self.client.get(
            reverse('step-3-are-you-sure', args=[self.donation.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['step_num'], 3)  # type: ignore

    def test_context_data(self):
        response = self.client.get(
            reverse('step-3-are-you-sure', args=[self.donation.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['customer_details_link'])  # type: ignore
        self.assertIsNotNone(response.context['customer_email_link'])  # type: ignore


class Step4ViewTest(TestCase):
    def setUp(self):
        self.donation = Donation.objects.create(
            number_plate='DB1 007',
            amount=10,
            title=Donation.TitleChoices.MR,
            first_name='Max',
            last_name='Wilkinson',
            address='123 Random Street',
            postal_town='London',
            postcode='AB12 1CD',
        )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(f'/step-4/email/{self.donation.id}/')

        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(
            reverse('step-4-customer-email', args=[self.donation.id])
        )

        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(
            reverse('step-4-customer-email', args=[self.donation.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'customer/step4-customer-email.html')  # type: ignore

    def test_step_in_context(self):
        response = self.client.get(
            reverse('step-4-customer-email', args=[self.donation.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['step_num'], 4)  # type: ignore

    def test_form_valid(self):
        data = {'email': 'test@email.com'}
        response = self.client.post(
            reverse('step-4-customer-email', args=[self.donation.id]),
            data=data,
        )

        self.assertEqual(Donation.objects.count(), 1)

        donation = Donation.objects.get()

        self.assertRedirects(
            response, expected_url=reverse('step-5-complete', args=[donation.id])  # type: ignore
        )

        self.assertEqual(donation.email, data['email'])


class Step5ViewTest(TestCase):
    def setUp(self):
        self.donation = Donation.objects.create(
            number_plate='DB1 007',
            amount=10,
            title=Donation.TitleChoices.MR,
            first_name='Max',
            last_name='Wilkinson',
            address='123 Random Street',
            postal_town='London',
            postcode='AB12 1CD',
            email='test@email.com',
        )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(f'/step-5/complete/{self.donation.id}/')

        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('step-5-complete', args=[self.donation.id]))

        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('step-5-complete', args=[self.donation.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'customer/step5-complete.html')  # type: ignore

    def test_step_in_context(self):
        response = self.client.get(reverse('step-5-complete', args=[self.donation.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['step_num'], 5)  # type: ignore


class DonationsTodayViewTest(TestCase):
    def setUp(self):
        self.donation = Donation.objects.create(
            number_plate='DB1 007',
            amount=10,
            title=Donation.TitleChoices.MR,
            first_name='Max',
            last_name='Wilkinson',
            address='123 Random Street',
            postal_town='London',
            postcode='AB12 1CD',
            email='test@email.com',
        )

        self.user = User.objects.create_user(username='test', is_staff=True)  # type: ignore
        self.client.force_login(self.user)

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(f'/administration/')

        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('admin-donations-today'))

        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('admin-donations-today'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'worker/donations_list.html')  # type: ignore

    def test_must_be_authenticated_and_staff(self):
        # Test when not staff.
        self.user.is_staff = False
        self.user.save()

        response = self.client.get(reverse('admin-donations-today'))
        self.assertRedirects(response, expected_url=reverse('admin:login'))  # type: ignore

        # Test when not logged in.
        self.client.logout()

        response = self.client.get(reverse('admin-donations-today'))
        self.assertRedirects(response, expected_url=reverse('admin:login'))  # type: ignore

    def test_get_queryset(self):
        self.donation.delete()

        yesterday_donation = Donation.objects.create(
            number_plate='DB1 007', amount='10.00'
        )
        yesterday_donation.donation_date -= timezone.timedelta(days=1)
        yesterday_donation.save(update_fields=['donation_date'])

        today_donation_not_paid = Donation.objects.create(
            number_plate='DB1 007', amount='10.00'
        )
        today_donation_paid = Donation.objects.create(
            number_plate='DB1 007', amount='10.00', donation_taken=True
        )

        tomorrow_donation = Donation.objects.create(
            number_plate='DB1 007', amount='10.00'
        )
        tomorrow_donation.donation_date += timezone.timedelta(days=1)
        tomorrow_donation.save(update_fields=['donation_date'])

        donation_no_amount = Donation.objects.create(number_plate='DB1 007')

        self.assertEqual(Donation.objects.count(), 5)

        response = self.client.get(reverse('admin-donations-today'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['object_list']), 1)  # type: ignore
        self.assertEqual(
            response.context['object_list'][0].id, today_donation_not_paid.id  # type: ignore
        )


class UnpaidDonationViewTest(TestCase):
    def setUp(self):
        self.donation = Donation.objects.create(
            number_plate='DB1 007',
            amount=10,
            title=Donation.TitleChoices.MR,
            first_name='Max',
            last_name='Wilkinson',
            address='123 Random Street',
            postal_town='London',
            postcode='AB12 1CD',
            email='test@email.com',
            donation_taken=False,
            donation_taken_date=None,
        )

        self.user = User.objects.create_user(username='test', is_staff=True)  # type: ignore
        self.client.force_login(self.user)

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(f'/administration/{self.donation.id}/')

        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(
            reverse('admin-unpaid-donation', args=[self.donation.id])
        )

        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(
            reverse('admin-unpaid-donation', args=[self.donation.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'worker/donation_view.html')  # type: ignore

    def test_must_be_authenticated_and_staff(self):
        # Test when not staff.
        self.user.is_staff = False
        self.user.save()

        response = self.client.get(
            reverse('admin-unpaid-donation', args=[self.donation.id])
        )
        self.assertRedirects(response, expected_url=reverse('admin:login'))  # type: ignore

        # Test when not logged in.
        self.client.logout()

        response = self.client.get(
            reverse('admin-unpaid-donation', args=[self.donation.id])
        )
        self.assertRedirects(response, expected_url=reverse('admin:login'))  # type: ignore

    def test_get_queryset(self):
        # Test 404 error on specific conditions.
        donation_already_taken = Donation.objects.create(
            number_plate='DB1 007', amount='10.00', donation_taken=True
        )
        response = self.client.get(
            reverse('admin-unpaid-donation', args=[donation_already_taken.id])
        )
        self.assertEqual(response.status_code, 404)

        donation_no_amount = Donation.objects.create(number_plate='DB1 007')
        response = self.client.get(
            reverse('admin-unpaid-donation', args=[donation_no_amount.id])
        )
        self.assertEqual(response.status_code, 404)

    def test_post(self):
        self.assertEqual(Donation.objects.count(), 1)

        response = self.client.post(
            reverse('admin-unpaid-donation', args=[self.donation.id])
        )
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Donation.objects.count(), 0)


class PaymentCompleteTest(TestCase):
    def setUp(self):
        self.donation = Donation.objects.create(
            number_plate='DB1 007',
            amount=10,
            title=Donation.TitleChoices.MR,
            first_name='Max',
            last_name='Wilkinson',
            address='123 Random Street',
            postal_town='London',
            postcode='AB12 1CD',
            email='test@email.com',
        )

        self.user = User.objects.create_user(username='test', is_staff=True)  # type: ignore
        self.client.force_login(self.user)

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(
            f'/administration/{self.donation.id}/payment-complete/'
        )

        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(
            reverse('admin-payment-complete', args=[self.donation.id])
        )

        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(
            reverse('admin-payment-complete', args=[self.donation.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'worker/payment_complete.html')  # type: ignore

    def test_must_be_authenticated_and_staff(self):
        # Test when not staff.
        self.user.is_staff = False
        self.user.save()

        response = self.client.get(reverse('admin-donations-today'))
        self.assertRedirects(response, expected_url=reverse('admin:login'))  # type: ignore

        # Test when not logged in.
        self.client.logout()

        response = self.client.get(reverse('admin-donations-today'))
        self.assertRedirects(response, expected_url=reverse('admin:login'))  # type: ignore

    def test_donation_taken_cant_view(self):
        self.donation.donation_taken = True
        self.donation.save()

        response = self.client.get(
            reverse('admin-payment-complete', args=[self.donation.id])
        )

        self.assertEqual(response.status_code, 404)

    def test_cash_payment(self):
        response = self.client.get(
            reverse('admin-payment-complete', args=[self.donation.id]) + '?cash=True'
        )

        self.donation.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.donation.card_payment, False)
        self.assertTrue(self.donation.donation_taken)
        self.assertIsNotNone(self.donation.donation_taken_date)
        self.assertEqual(self.donation.transaction_code, '')

    def test_card_payment_success(self):
        response = self.client.get(
            reverse('admin-payment-complete', args=[self.donation.id])
            + '?smp-status=success&smp-tx-code=test'
        )

        self.donation.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.donation.card_payment)
        self.assertTrue(self.donation.donation_taken)
        self.assertIsNotNone(self.donation.donation_taken_date)
        self.assertEqual(self.donation.transaction_code, 'test')

    def test_card_payment_failed(self):
        response = self.client.get(
            reverse('admin-payment-complete', args=[self.donation.id])
            + '?smp-status=failed&smp-tx-code='
        )

        self.donation.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(self.donation.card_payment)
        self.assertFalse(self.donation.donation_taken)
        self.assertIsNone(self.donation.donation_taken_date)
        self.assertEqual(self.donation.transaction_code, '')
