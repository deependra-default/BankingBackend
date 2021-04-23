import csv
from datetime import datetime

from django.http import StreamingHttpResponse
from rest_framework import generics, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from banking.models import Transaction, Account
from banking.permissions import IsBankManager, IsCustomer, IsEmployee
from banking.serializers import (
    AccountSerializer,
    CreditDebitTransactionSerializer,
    TransactionCSVSerializer,
    TransactionHistorySerializer,
    TransferSerializer,
)


class DebitAmount(generics.CreateAPIView):
    """"""

    queryset = Transaction.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = (IsEmployee,)
    http_method_names = [
        "post",
    ]

    def post(self, request, *args, **kwargs):
        data = request.data
        data["action"] = "Debit"
        serializer = CreditDebitTransactionSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            try:
                data = serializer.validated_data
                transact = Transaction()
                transact.description = {
                    "source": data.get("source"),
                    "added_by": request.user.id,
                }
                transact.reference_number = data.get("reference_number", None)
                transact.transaction_method = data["transaction_method"]
                transact.transaction_type = "Debit"
                transact.amount = data["amount"]
                transact.account_id = data["account"]
                transact.save()

            except Exception as e:
                return Response({"status": "Unable to create Credit transaction"})
            return Response(
                {
                    "status": "Success",
                    "message": f"""{serializer.validated_data.get('amount')} has been credited to account number {request.data.get('account')}""",
                }
            )


class CreditAmount(generics.CreateAPIView):
    """"""

    queryset = Transaction.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = (IsEmployee,)
    http_method_names = [
        "post",
    ]

    def post(self, request, *args, **kwargs):
        data = request.data
        data["action"] = "Debit"
        serializer = CreditDebitTransactionSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            try:
                data = serializer.validated_data
                transact = Transaction()
                transact.description = {
                    "source": data.get("source"),
                    "added_by": request.user.id,
                }
                transact.reference_number = data.get("reference_number", None)
                transact.transaction_method = data["transaction_method"]
                transact.transaction_type = "Credit"
                transact.amount = data["amount"]
                transact.account_id = data["account"]
                transact.save()

            except Exception as e:
                return Response({"status": "Unable to create Credit transaction"})
            return Response(
                {
                    "status": "Success",
                    "message": f"""{serializer.validated_data.get('amount')} has been credited to account number {request.data.get('account')}""",
                }
            )


class CustomerEnquiry(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [
        IsCustomer,
    ]

    def get(self, request, *args, **kwargs):

        account = Account.objects.get(customer__user=request.user)
        serialize = AccountSerializer(account)
        return Response({"content": serialize.data, "status": status.HTTP_200_OK})


class CsvWrite:
    """"""

    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


class TransactionHistoryCsv(APIView):
    """
    Transcion history download api for only BankManager
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsBankManager]

    def post(self, request, *args, **kwargs):
        serializer = TransactionCSVSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.validated_data
            rows_data = [
                [
                    "Transaction ID",
                    "Transaction Type",
                    "Amount",
                    "Account Number",
                    "Transaction Method",
                    "Description",
                    "Reference Number",
                ]
            ]
            transact = Transaction.objects.filter(
                account__account_number__in=data["acc_ids"],
                created_at__gte=data["start_date"],
                created_at__lte=data["end_date"],
            )
            for ts in transact:
                transact_inst = TransactionHistorySerializer(ts)
                rows_data.append([*transact_inst.data.values()])
            rows = (x for x in rows_data)
            pseudo_buffer = CsvWrite()
            writer = csv.writer(pseudo_buffer)
            file = "Transaction_History" + str(datetime.now())
            return StreamingHttpResponse(
                (writer.writerow(row) for row in rows),
                content_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=file"},
            )


class TransferAPI(APIView):
    """
    Transfer api for Customer
    """

    http_method_names = ["post"]
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsCustomer]

    def post(self, request, *args, **kwargs):
        serializer = TransferSerializer(context={"request": request}, data=request.data)
        if serializer.is_valid(raise_exception=True):
            transfer = serializer.save()
            return Response(
                {
                    "content": f"Transaction id {transfer.transaction_id}",
                    "status": status.HTTP_201_CREATED,
                }
            )
