from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from banking.views import (DebitAmount, CreditAmount, CustomerEnquiry,
                           TransactionHistoryCsv, TransferAPI)

urlpatterns = [
    path("obtain-token/", obtain_auth_token, name='token'),
    path("credit-amount/", CreditAmount.as_view(), name= 'credit_amount'),
    path("debit-amount/", DebitAmount.as_view(), name= 'debit_amount'),
    path("customer-enquiry/", CustomerEnquiry.as_view(),name='enquiry'),
    path("transaction-csv/", TransactionHistoryCsv.as_view(),name='history'),
    path("transfer/", TransferAPI.as_view(), name='transfer'),
]
