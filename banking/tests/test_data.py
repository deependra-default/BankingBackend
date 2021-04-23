import random
from faker import Faker
from factory.django import DjangoModelFactory

from BankingBackend.constant import (
    ACCOUNT_CHOICES,
    ACCOUNT_STATUS_CHOICES,
    TRANSACTION_METHOD,
    TRANSACTION_TYPE,
    USER_CHOICES,
)

user_type = [choice[0] for choice in USER_CHOICES]
account_type = [choice[0] for choice in ACCOUNT_CHOICES]
account_status = [choice[0] for choice in ACCOUNT_STATUS_CHOICES]
transaction_type = [choice[0] for choice in TRANSACTION_TYPE]
transaction_method = [choice[0] for choice in TRANSACTION_METHOD]

fake = Faker()


class UserFactory(DjangoModelFactory):
    """
    User Factory
    """

    email = fake.email()
    user_type = random.choice(user_type)
    contact_number = fake.phone_number()
    date_joined = fake.date_time()
    first_name = fake.first_name()
    last_name = fake.last_name()
    username = fake.user_name()

    class Meta:
        model = "accounts.User"


class BranchFactory(DjangoModelFactory):
    """
    Branch Factory
    """

    name = fake.pystr()
    city = fake.pystr()
    ifsc_code = fake.pystr()
    micr_code = fake.pystr()
    state = fake.pystr()
    address = fake.pystr()

    class Meta:
        model = "banking.Branch"


class CustomerFactory(DjangoModelFactory):
    """
    Customer Factory
    """

    user = UserFactory()
    customer_id = fake.pyint()
    date_of_birth = fake.date_time()
    pan_card_number = fake.pystr()
    aadhar_card_number = fake.pyint()
    occupation = fake.pystr()
    branch = BranchFactory()
    address = fake.pystr()

    class Meta:
        model = "banking.Customer"


class AccountFactory(DjangoModelFactory):
    """
    Account Factory
    """

    account_number = fake.pyint()
    balance = fake.pydecimal()
    customer = CustomerFactory()
    account_type = random.choice(account_type)
    status = random.choice(account_status)

    class Meta:
        model = "banking.Account"

class TransactionFactory(DjangoModelFactory):
    """
    Account Factory
    """
    transaction_id = fake.pystr()
    transaction_type = random.choice(transaction_type)
    amount = fake.pydecimal(min_value=0)
    account = AccountFactory()
    transaction_method = random.choice(transaction_method)
    description =  fake.pydict()
    reference_number = fake.pystr()
    class Meta:
        model = "banking.Transaction"
