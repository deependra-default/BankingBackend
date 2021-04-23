# BankingBackend #
BankingBackend is a an application whic provides API to for performing basic banking operation such as deposit, withdraw and transfer amount including retriving  accounts transactions  as csv.

Minimum requirements:
Python == 3.8.x
django == 3.2


Getting Started

1. Create a Python virtual environment for your Django project.
	python3.8  -m  venv env 

2. Activate the environement.
	source env/bin/activate

3. Install dependency.
	python3.8 -m pip install requirement.txt.

4. Create database schema.
   python 3.8 manage.py migrate

5. (Optional) Run custom management command for creating initial sample record
   python3.8 manage.py createsamplerecords 5
   (replace 5 with desired number of records)
6. Start developement server.
	python3.8 manage.py runserver


API Docs:-
1. https://127.0.0.1/banking/obtain-token/"
	Info:- A registered user can send a post request to obtain auth token.
2. https://127.0.0.1/banking/credit-amount/"
	Info:- A bank employee or manager can send a post request to deposit amount in customer account.
3. https://127.0.0.1/banking/debit-amount/"
	Info:  bank employee or manager can send a post request to deduct amount from customer account.
4. https://127.0.0.1/banking/customer-enquiry/"
	Info:  A customer can send dend a get request to get his/her account information.
5. https://127.0.0.1/banking/transaction-csv/"
	Info: The bank manage can send a post request to download customer/s transaction for a date range.
6. https://127.0.0.1/banking/transfer/"
	Info:- A customer can send a post request to transfer funds from his/her account to another customer's account.
