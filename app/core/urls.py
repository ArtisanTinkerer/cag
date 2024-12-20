from django.urls import path

from . import views

urlpatterns = [
    path(
        '',
        views.Step1View.as_view(),
        name='step-1-enter-registration',
    ),
    path(
        'step-2/donation/<uuid:pk>/',
        views.Step2View.as_view(),
        name='step-2-donation-amount',
    ),
    path(
        'step-3/gift-aid/<uuid:pk>/',
        views.Step3View.as_view(),
        name='step-3-customer-details',
    ),

    path(
        'step-4/customer-search',
        views.SearchResults.as_view(), # display results of the search
        name='step-4-customer-search',
    ),



    path(
        'step-3/are-you-sure/<uuid:pk>/', #how does it know to get here
        views.Step3BView.as_view(),
        name='step-3-are-you-sure',
    ),
    path(
        'step-4/email/<uuid:pk>/',
        views.Step4View.as_view(),
        name='step-4-customer-email',
    ),
    path(
        'step-5/complete/<uuid:pk>/',
        views.Step5View.as_view(),
        name='step-5-complete',
    ),
    path(
        'administration/',
        views.DonationsTodayView.as_view(),
        name='admin-donations-today',
    ),
    path(
        'administration/<uuid:pk>/',
        views.UnpaidDonationView.as_view(),
        name='admin-unpaid-donation',
    ),
    path(
        'administration/<uuid:pk>/payment-complete/',
        views.payment_complete,
        name='admin-payment-complete',
    ),

    path('search/', views.search, name='search'),
]
