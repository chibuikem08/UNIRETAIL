from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('pay/<int:order_pk>/',         views.initiate_payment,    name='initiate'),
    path('verify/<str:reference>/',     views.verify_payment,      name='verify'),
    path('history/',                    views.payment_history,     name='history'),
    path('bank-account/',               views.vendor_bank_account, name='vendor_bank_account'),
]
