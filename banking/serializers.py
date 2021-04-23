from datetime import datetime
from dateutil import parser
from rest_framework import routers, serializers, viewsets
from rest_framework import status

from banking.models import Account, Beneficiary, Transaction

from BankingBackend.constant import ACTIVE
from django.db import transaction


class CreditDebitTransactionSerializer(serializers.ModelSerializer):
    """
    Credit and Debit Transaction
    """

    customer_name = serializers.CharField(max_length=100)
    amount = serializers.DecimalField(max_digits=15, decimal_places=3)
    source = serializers.CharField(max_length=100)
    account = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Transaction
        fields = (
            "transaction_method",
            "account",
            "source",
            "customer_name",
            "amount",
        )

    def validate(self, data):
        """"""
        if not self.initial_data.get("account", None):
            raise serializers.ValidationError("keyword <account> is not found")
        try:
            account = Account.objects.get(
                account_number=self.initial_data.get("account", None)
            )
        except Account.DoesNotExist:
            raise serializers.ValidationError("Account number not found")

        customer_name = account.customer.user.get_full_name()
        if customer_name != self.initial_data["customer_name"]:
            raise serializers.ValidationError("Account Holder name doesn't match")
        data["account"] = account.id
        return data


class AccountSerializer(serializers.ModelSerializer):
    """
    Account Serializer
    """

    pan_card = serializers.SerializerMethodField()
    adhar_card = serializers.SerializerMethodField()
    ifsc_code = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    customer_id = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = [
            "account_number",
            "balance",
            "account_type",
            "pan_card",
            "adhar_card",
            "ifsc_code",
            "name",
            "customer_id",
        ]

    def get_pan_card(self, obj):
        return f"""XXX-XXX-{obj.customer.pan_card_number[-4:]}"""

    def get_adhar_card(self, obj):
        return f"""xxxx-xxxx-{str(obj.customer.aadhar_card_number)[-4:]}"""

    def get_ifsc_code(self, obj):
        return obj.customer.branch.ifsc_code

    def get_name(self, obj):
        return obj.customer.user.get_full_name()

    def get_customer_id(self, obj):
        return obj.customer.customer_id


class TransactionCSVSerializer(serializers.Serializer):
    """
    Make serializer to generate CSV.
    """

    end_date = serializers.DateField(required=False)
    start_date = serializers.DateField(required=False)
    acc_ids = serializers.ListField(child=serializers.IntegerField())

    def validate(self, data):
        """"""
        # if start_date > end_date:
        #     return Response({"message": f"Insufficient account balance", "status": status.HTTP_403_FORBIDDEN})
        if not (end_date := self.initial_data.get("end_date")):
            end_date = datetime.now()
        else:
            end_date = parser.parse(end_date)

        if not (start_date := self.initial_data.get("start_date")):
            start_date = datetime.now().replace(day=1)
        else:
            start_date = parser.parse(start_date)
        if end_date < start_date:
            raise serializers.ValidationError(
                "End Date can not be less then Start Date"
            )
        data["end_date"] = end_date
        data["start_date"] = start_date
        return data


class TransactionHistorySerializer(serializers.ModelSerializer):
    """
    Returns seriallized transaction history of the transaction object.
    """

    account_number = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            "transaction_id",
            "transaction_type",
            "amount",
            "account_number",
            "transaction_method",
            "description",
            "reference_number",
        ]

    def get_account_number(self, obj):
        return obj.account.account_number


class TransferSerializer(serializers.Serializer):
    """
    Create custom Transfer Serializer, it will promise customer to send money to another customer.
    """

    account_number = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=35, decimal_places=3)
    account_holder_name = serializers.CharField()
    contact_number = serializers.CharField()
    remarks = serializers.CharField()
    source = serializers.CharField()
    ifsc_code = serializers.CharField()

    def validate(self, data):
        """
        Add validation
        """
        self.user = self.context["request"].user
        self.sender_account = Account.objects.get(customer__user=self.user)
        self.reciever_account = Account.objects.filter(
            account_number=data["account_number"]
        )
        if self.sender_account.status != ACTIVE:
            raise serializers.ValidationError("Your account is not Active")

        if self.sender_account.balance < data["amount"]:
            raise serializers.ValidationError("Insufficient account balance")

        if not self.reciever_account:
            raise serializers.ValidationError("Account Number not found")

        elif self.reciever_account[0].status != ACTIVE:
            raise serializers.ValidationError("Receiver account is not Active")

        elif (
            self.reciever_account[0].customer.user.get_full_name()
            != data["account_holder_name"]
        ):
            raise serializers.ValidationError(
                "Account/Account Holder Name doesn't match"
            )

        elif self.reciever_account[0].customer.branch.ifsc_code != data["ifsc_code"]:
            raise serializers.ValidationError(
                "Account/Account Holder Name doesn't match"
            )

        return data

    def create(self, validated_data):
        """
        Customize create method to promises to deduct account balance and send it to target account
        """
        with transaction.atomic():
            # Debit amount from sender account
            debit_transact = Transaction()
            debit_transact.transaction_type = "Debit"
            debit_transact.amount = validated_data["amount"]
            debit_transact.account = self.sender_account
            debit_transact.transaction_method = validated_data["source"]
            debit_transact.description = {
                "remarks": validated_data["remarks"],
                "trasferred_to": {
                    "account_number": validated_data["account_number"],
                    "ifsc": validated_data["ifsc_code"],
                },
            }
            debit_transact.save()

            # Credit amount from receiver account
            credit_transact = Transaction()
            credit_transact.transaction_type = "Credit"
            credit_transact.amount = validated_data["amount"]
            credit_transact.account = self.reciever_account[0]
            credit_transact.transaction_method = validated_data["source"]
            credit_transact.description = {
                "remarks": validated_data["remarks"],
                "trasferred_from": {
                    "account_number": str(self.sender_account.account_number)[-6:]
                },
            }
            credit_transact.save()

            return debit_transact
