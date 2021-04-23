from accounts.models import User
from banking.models import *
from datetime import datetime
import random
from django.core.management.base import BaseCommand
from decimal import Decimal
from faker import Faker

fake = Faker()

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


class Load_data:
    def __init__(self, count):
        self.count = count

    def load(self):
        for _ in range(self.count):
            user = User.objects.create(
                username=fake.user_name(),
                email=fake.email(),
                user_type=random.choice(user_type),
                contact_number=fake.phone_number(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
            )
            user.set_password("admin")
            user.save()

            branch = Branch.objects.create(
                name=fake.name(),
                city=fake.city(),
                ifsc_code=fake.pystr(11),
                micr_code=fake.pystr(11),
            )

            cust = Customer.objects.create(
                user_id=user.id,
                customer_id=fake.pyint(),
                date_of_birth=fake.date_time(),
                address=fake.address(),
                pan_card_number=fake.pystr(10),
                aadhar_card_number=fake.pyint(),
                occupation=fake.job(),
                branch_id=branch.id,
            )

            acc = Account.objects.create(
                account_number=fake.pyint(10),
                balance=fake.pydecimal(
                    min_value=1000,
                ),
                customer_id=cust.id,
                account_type=random.choice(account_type),
                status=random.choice(account_status),
            )
            txn = Transaction.objects.create(
                transaction_type=random.choice(transaction_type),
                amount=fake.pydecimal(min_value=10, max_value=100),
                account_id=acc.id,
                transaction_method=random.choice(transaction_method),
                description={},
                reference_number=fake.pystr(10),
            )


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "total", type=int, help="Indicates the number of data to be created"
        )

    def handle(self, *args, **kwargs):
        load = Load_data(kwargs.get("total"))
        load.load()
