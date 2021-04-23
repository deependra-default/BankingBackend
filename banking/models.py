import random
import string
import uuid
from django.db import models
from decimal import Decimal
from django.forms.models import model_to_dict

from jsonfield import JSONField

from accounts.models import User
from BankingBackend.tasks.celery import schedule_send_email

from BankingBackend.constant import (
    ACCOUNT_CHOICES,
    ACCOUNT_STATUS_CHOICES,
    TRANSACTION_METHOD,
    TRANSACTION_TYPE,
)


def uuid_str():
    """
    Generate UUID
    """
    return str(uuid.uuid4())


def get_default_account():
    """
    Create account number
    """
    num = "".join(random.choices(string.digits, k=12))
    if not Account.objects.filter(account_number=num).exists():
        return int(num)
    get_default_account()


def generate_txn_id():
    """
    Generate Transction ID for the Transaction table
    """
    txn_id = "".join(random.choices(string.digits, k=12))
    if not Transaction.objects.filter(transaction_id="txn" + txn_id).exists():
        return "txn" + str(txn_id)
    generate_txn_id()


class BaseModelClass(models.Model):
    """
    Create Base Medel for all models.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(null=True, default=False)

    class Meta:
        abstract = True


class Branch(BaseModelClass):
    """
    Create Bank Branch
    """

    id = models.CharField(primary_key=True, default=uuid_str, max_length=100)
    name = models.CharField(max_length=200, db_index=True)
    city = models.CharField(max_length=50)
    ifsc_code = models.CharField(max_length=11, unique=True)
    micr_code = models.CharField(max_length=9, unique=True)
    state = models.CharField(max_length=50)
    address = models.CharField(max_length=200)

    def __str__(self):
        return str(self.name)

    class Meta:
        unique_together = ("name", "city")


class Customer(BaseModelClass):
    """
    Create customer table
    """

    id = models.CharField(primary_key=True, default=uuid_str, max_length=100)
    user = models.OneToOneField(
        User,
        related_name="user_customer",
        on_delete=models.PROTECT,
        null=True,
    )
    customer_id = models.IntegerField(unique=True, editable=False)
    date_of_birth = models.DateField()
    pan_card_number = models.CharField(max_length=10, null=True, blank=True)
    aadhar_card_number = models.IntegerField()
    occupation = models.CharField(max_length=200)
    branch = models.ForeignKey(
        Branch, on_delete=models.PROTECT, null=True, related_name="branch_customers"
    )
    address = models.TextField(max_length=400)

    def __str__(self):
        return self.user.get_full_name()


class StateMaster(BaseModelClass):
    """
    State table will store state information
    """

    id = models.CharField(primary_key=True, default=uuid_str, max_length=100)
    name = models.CharField(max_length=200)


class CityMaster(BaseModelClass):
    """
    City table will store city details
    """

    id = models.CharField(primary_key=True, default=uuid_str, max_length=100)
    name = models.CharField(max_length=200)
    state = models.ForeignKey(
        StateMaster, related_name="cities", on_delete=models.PROTECT
    )


class Address(BaseModelClass):
    """
    Address
    """

    id = models.CharField(primary_key=True, default=uuid_str, max_length=100)
    address_line_one = models.CharField(max_length=200)
    address_line_two = models.CharField(max_length=200, null=True, blank=True)
    city = models.ForeignKey(
        CityMaster, related_name="city_addresses", on_delete=models.PROTECT
    )
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="customer_address"
    )

    def __str__(self):
        return f"{self.address_line1}_{self.city}"


class Account(BaseModelClass):
    """
    Customer bank account table
    """

    id = models.CharField(primary_key=True, default=uuid_str, max_length=100)
    account_number = models.IntegerField(
        default=get_default_account, unique=True, editable=False
    )
    balance = models.DecimalField(
        max_digits=20, decimal_places=3, default=Decimal("0.000")
    )

    # here I'm assuming only for saving account
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        related_name="customer_account",
        null=True,
    )
    account_type = models.CharField(max_length=2, choices=ACCOUNT_CHOICES)
    status = models.CharField(max_length=2, choices=ACCOUNT_STATUS_CHOICES)

    def __str__(self):
        return f"{self.account_number} - {self.customer.user.get_full_name()}"

    def get_account_balance(self):
        return self.balance


class Transaction(BaseModelClass):
    """
    Customer bank transaction table
    """

    id = models.CharField(primary_key=True, default=uuid_str, max_length=100)
    transaction_id = models.CharField(
        default=generate_txn_id, editable=False, max_length=100
    )

    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE)
    amount = models.DecimalField(
        max_digits=20, decimal_places=3, default=Decimal("0.000")
    )
    account = models.ForeignKey(
        Account,
        related_name="account_transaction",
        on_delete=models.PROTECT,
        null=True,
    )
    transaction_method = models.CharField(max_length=8, choices=TRANSACTION_METHOD)
    description = JSONField(default=dict)
    reference_number = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.transaction_id

    def save(self, *args, **kwargs):
        """
        Overide save method where amount will be Credit or Deibit from customer account
        """
        account = self.account
        if self.transaction_type == "Credit":
            account.balance = round(account.balance + self.amount, 3)
        elif self.transaction_type == "Debit":
            account.balance = round(account.balance - self.amount, 3)
        account.save()
        super(Transaction, self).save(*args, **kwargs)
        
        parmas = {
            "email":[account.customer.user.email],
            "transaction_type": self.transaction_type, 
            "account_number":account.account_number, 
            "amount": self.amount
        }
        schedule_send_email.delay(**parmas)


# TODO: we are not using benificiary account for the transfer for now but will use it
class Beneficiary(BaseModelClass):
    """"""

    id = models.CharField(primary_key=True, default=uuid_str, max_length=100)
    account_number = models.IntegerField()
    ifsc_code = models.CharField(max_length=11)
    contact_number = models.CharField(max_length=16)
    customer = models.ForeignKey(
        Customer, related_name="beneficiary", on_delete=models.PROTECT
    )

    def __str__(self):
        return f"{self.name} - {self.customer.user.get_full_name()}"
