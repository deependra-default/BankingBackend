from django.test import TestCase
from banking.models import Branch
from banking.tests.test_data import *
import datetime
import json
import random
from faker import Faker
from rest_framework.test import force_authenticate, APIRequestFactory
from django.urls import reverse

from rest_framework.test import APIClient

from banking.models import Account, Customer
from accounts.models import User
from BankingBackend.constant import (
    ACCOUNT_CHOICES,
    ACCOUNT_STATUS_CHOICES,
    TRANSACTION_METHOD,
    TRANSACTION_TYPE,
    USER_CHOICES,
    ACTIVE,
    INACTIVE
)

user_type = [choice[0] for choice in USER_CHOICES]
account_type = [choice[0] for choice in ACCOUNT_CHOICES]
account_status = [choice[0] for choice in ACCOUNT_STATUS_CHOICES]
transaction_type = [choice[0] for choice in TRANSACTION_TYPE]
transaction_method = [choice[0] for choice in TRANSACTION_METHOD]

factory = APIRequestFactory()
client = APIClient()

fake = Faker()


class BranchTestCase(TestCase):
    """
    Test case for User model
    """

    def setUp(self):
        self.user = UserFactory()

    def test_create_branch(self):
        self.assertIsInstance(self.user.email, str)
        self.assertIsInstance(self.user.user_type, str)
        self.assertIsInstance(self.user.contact_number, str)
        self.assertIsInstance(self.user.date_joined, datetime.datetime)
        self.assertIsInstance(self.user.first_name, str)
        self.assertIsInstance(self.user.last_name, str)
        self.assertIsInstance(self.user.username, str)

    def test_update_user(self):
        self.user.email = fake.email()
        self.user.user_type = "EM"
        self.user.contact_number = fake.phone_number()
        self.user.date_joined = fake.date_time()
        self.user.last_name = fake.last_name()
        self.user.first_name = fake.first_name()
        self.user.username = fake.user_name()

        self.user.save()

        self.assertIsInstance(self.user.email, str)
        self.assertIsInstance(self.user.user_type, str)
        self.assertIsInstance(self.user.contact_number, str)
        self.assertIsInstance(self.user.date_joined, datetime.datetime)
        self.assertIsInstance(self.user.first_name, str)
        self.assertIsInstance(self.user.last_name, str)
        self.assertIsInstance(self.user.username, str)


class TokenTestCase(TestCase):
    """
    Test case for obtaining authentication token for the api.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.user_password = fake.password()
        self.user.set_password(self.user_password)
        self.user.save()
        self.data = {"username": self.user.username, "password": self.user_password}

    def test_obtain_token_auth(self):
        request = self.client.post(reverse("token"), format="json", data=self.data)
        self.assertEqual(request.status_code, 200)
        self.assertIsNotNone(json.loads(request.content).get("token", None))

    def test_obtain_token_auth_fail(self):
        self.data["password"] = fake.password()
        request = self.client.post(reverse("token"), format="json", data=self.data)
        self.assertEqual(request.status_code, 400)
        self.assertEqual(
            json.loads(request.content)["non_field_errors"][0],
            "Unable to log in with provided credentials.",
        )


class DebitAmountTestCase(TestCase):
    """
    Test case for crediting amount in the customers account.
    """

    def setUp(self):
        """
        Set up for testing credit amount API.
        """
        self.client = APIClient()
        self.url = reverse("credit_amount")
        self.user = UserFactory()
        self.user.user_type = user_type[1]
        self.user.save()
        self.client.force_authenticate(user=self.user)

        self.branch = BranchFactory()
        self.customer = CustomerFactory()
        self.customer.user = self.user
        self.customer.branch = self.branch
        self.customer.save()
        self.account = AccountFactory()
        self.account.customer = self.customer
        self.account.save()

        self.data = {
            "transaction_method": random.choice(transaction_method),
            "source": fake.pystr(),
            "customer_name": self.user.get_full_name(),
            "amount": fake.pyint(max_value=100),
            "account": self.account.account_number,
        }

    def test_credit_amount_auth(self):
        """
        User authenticated as Customer can not perform this action.
        """
        self.user.user_type = user_type[2]  # Updated user as bank employee
        self.user.save()
        request = self.client.post(self.url, format="json", data=self.data)
        self.assertEqual(request.status_code, 403)
        self.assertEqual(
            json.loads(request.content)["detail"],
            "You do not have permission to perform this action.",
        )

    def test_credit_amount(self):
        """
        Test if the amount can be credited/deposited in the customer account by the employee/manage of the bank.
        """
        request = self.client.post(self.url, format="json", data=self.data)
        self.assertEqual(request.status_code, 200)
        self.assertEqual(json.loads(request.content)["status"], "Success")

    def test_credit_amount_incomplete_data(self):
        data = self.data
        del data["transaction_method"]
        request = self.client.post(self.url, format="json", data=data)
        self.assertEqual(request.status_code, 400)
        self.assertEqual(
            [*json.loads(request.content).values()][0][0], "This field is required."
        )

    def test_credit_amount_incorrect_data(self):
        data = self.data
        method_choice = fake.pystr()
        data["transaction_method"] = method_choice
        request = self.client.post(self.url, format="json", data=self.data)
        self.assertEqual(request.status_code, 400)
        self.assertEqual(
            json.loads(request.content)["transaction_method"][0],
            f'"{method_choice}" is not a valid choice.',
        )


class CreditAmountTestCase(TestCase):
    """
    Test case for debiting amount in the customers account.
    """

    def setUp(self):
        """
        Set up for testing debit amount API.
        """
        self.client = APIClient()
        self.url = reverse("debit_amount")
        self.user = UserFactory()
        self.user.user_type = user_type[1]
        self.user.save()
        self.client.force_authenticate(user=self.user)

        self.branch = BranchFactory()
        self.customer = CustomerFactory()
        self.customer.user = self.user
        self.customer.branch = self.branch
        self.customer.save()
        self.account = AccountFactory()
        self.account.customer = self.customer
        self.account.save()

        self.data = {
            "transaction_method": random.choice(transaction_method),
            "source": fake.pystr(),
            "customer_name": self.user.get_full_name(),
            "amount": fake.pyint(max_value=100),
            "account": self.account.account_number,
        }

    def test_debit_amount_auth(self):
        """
        User authenticated as Customer can not perform this action.
        """
        self.user.user_type = user_type[2]  # Updated user as bank employee
        self.user.save()
        request = self.client.post(self.url, format="json", data=self.data)
        self.assertEqual(request.status_code, 403)
        self.assertEqual(
            json.loads(request.content)["detail"],
            "You do not have permission to perform this action.",
        )

    def test_debit_amount(self):
        """
        Test if the amount can be credited/deposited in the customer account by the employee/manage of the bank.
        """
        request = self.client.post(self.url, format="json", data=self.data)
        self.assertEqual(request.status_code, 200)
        self.assertEqual(json.loads(request.content)["status"], "Success")

    def test_debit_amount_incomplete_data(self):
        data = self.data
        del data["transaction_method"]
        request = self.client.post(self.url, format="json", data=data)
        self.assertEqual(request.status_code, 400)
        self.assertEqual(
            [*json.loads(request.content).values()][0][0], "This field is required."
        )

    def test_debit_amount_incorrect_data(self):
        data = self.data
        method_choice = fake.pystr()
        data["transaction_method"] = method_choice
        request = self.client.post(self.url, format="json", data=self.data)
        self.assertEqual(request.status_code, 400)
        self.assertEqual(
            json.loads(request.content)["transaction_method"][0],
            f'"{method_choice}" is not a valid choice.',
        )


class CustomerEnquiryTestCase(TestCase):
    """
    Test case for crediting amount in the customers account.
    """
    def setUp(self):
        """
        Set up for testing credit amount API.
        """
        self.client = APIClient()
        self.url = reverse("enquiry")
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)
        self.branch = BranchFactory()
        self.customer = CustomerFactory()
        self.customer.user = self.user
        self.customer.branch = self.branch
        self.customer.save()
        self.account = AccountFactory()
        self.account.customer = self.customer
        self.account.save()
        self.user.user_type = user_type[2]
        self.user.save()

    def test_account_enquiry(self):
        """
        Test response on customr request for account enquiry. 
        """
        request = self.client.get(self.url)
        self.assertEqual(request.status_code, 200)


class TransferAPITestCase(TestCase):
    """
    Test case for crediting amount in the customers account.
    """
    def setUp(self):
        """
        Set up for testing credit amount API.
        """
        self.client = APIClient()
        self.url = reverse('transfer')

        self.user = UserFactory()

        self.branch = BranchFactory()

        self.customer = CustomerFactory()
        self.customer.user = self.user
        self.customer.branch = self.branch
        self.customer.save()

        self.account = AccountFactory()
        self.account.customer = self.customer
        self.account.save()


        self.user2 = User.objects.create(
                email = fake.email(),
                user_type = user_type[2],
                contact_number = fake.phone_number(),
                date_joined = fake.date_time(),
                first_name = fake.first_name(),
                last_name = fake.last_name(),
                username = fake.user_name(),
            )

        self.customer2 = Customer.objects.create(
                user = self.user2,
                customer_id = fake.pyint(),
                date_of_birth = fake.date_time(),
                pan_card_number = fake.pystr(),
                aadhar_card_number = fake.pyint(),
                occupation = fake.pystr(),
                branch = self.branch,
                address = fake.pystr(),
            )

        self.account2 = Account.objects.create(
                account_number = fake.pyint(min_value=1000),
                balance = fake.pydecimal(min_value=1000, max_value=100000),
                customer = self.customer2,
                account_type = random.choice(account_type),
                status = random.choice(account_status),
            )

        self.client.force_authenticate(user=self.user2)

        self.data ={
                    "account_number": self.account.account_number,
                    "amount" : fake.pyint(min_value=1, max_value=10),
                    "account_holder_name" : self.user.get_full_name(),
                    "contact_number" : fake.phone_number(),
                    "ifsc_code" : self.branch.ifsc_code,
                    "remarks" :fake.pystr(),
                    "source" :fake.pystr(),
                }

    def test_amount_transfer(self):
        """
        Test response on customr request for account enquiry. 
        """
        self.account2.status = ACTIVE
        self.account.status = ACTIVE
        self.account2.save()
        self.account.save()
        request = self.client.post(self.url, format='json', data=self.data)
        self.assertEqual(request.status_code, 200)

    def test_amount_transfer_inactive_account_sender(self):
        self.account2.status = INACTIVE
        self.account2.save()
        request = self.client.post(self.url, format='json', data=self.data)
        self.assertEqual(request.status_code, 400)
        self.assertEqual([*json.loads(request.content).values()][0][0], 'Your account is not Active')

    def test_amount_transfer_inactive_account_reciever(self):
        self.account2.status = ACTIVE
        self.account2.save()
        self.account.status = INACTIVE
        self.account.save()
        request = self.client.post(self.url, format='json', data=self.data)
        self.assertEqual(request.status_code, 400)
        self.assertEqual([*json.loads(request.content).values()][0][0], 'Receiver account is not Active')

    def test_amount_transfer_insufficient_amount(self):
        self.account2.status = ACTIVE
        self.account2.save()
        self.account.status = ACTIVE
        self.account.save()
        self.data["amount"] = round(self.account2.balance + fake.pydecimal(min_value=10, max_value=100),3) 
        request = self.client.post(self.url, format='json', data=self.data)
        self.assertEqual(request.status_code, 400)
        self.assertEqual([*json.loads(request.content).values()][0][0], 'Insufficient account balance')
