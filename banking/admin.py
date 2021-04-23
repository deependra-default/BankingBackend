from django.contrib import admin
from banking.models import Customer, Account, Transaction, Beneficiary, Branch


admin.site.register(Customer) 
admin.site.register(Account) 
admin.site.register(Transaction) 
admin.site.register(Beneficiary) 
admin.site.register(Branch) 
