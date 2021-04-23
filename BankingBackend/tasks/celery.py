import os
from django.core.mail import send_mail
from celery.decorators import task
from celery import Celery
from django.conf import settings
from datetime import datetime 

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BankingBackend.settings')

app = Celery('BankingBackend')

app.config_from_object('django.conf:settings')


app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@task(name="send_email_deposit")
def schedule_send_email(email,transaction_type, account_number, amount):
    if transaction_type == "Credit":
        email_subject = "Amount Credited"
    elif transaction_type == "Debit":
        email_subject = "Amount Debited"
    email_message = f'''Your account XXXXXX{ str(account_number)[-4:] } has been 
                 { email_subject[-8:]} with amount {amount} on {datetime.now()}'''
    send_mail(
                email_subject,
                email_message,
                settings.EMAIL_FROM,
                email,
                fail_silently=False,
            )
