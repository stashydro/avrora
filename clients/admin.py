from django.contrib import admin
from clients.models import Our_company,Partner,Contact,Rekvizity,BankAccount
from deals.models import Deal, Expense
from ticket.models import Ticket
# Register your models here.


admin.site.register(Our_company)
admin.site.register(Partner)
admin.site.register(Contact)
admin.site.register(Rekvizity)
admin.site.register(BankAccount)
admin.site.register(Deal)
admin.site.register(Ticket)
admin.site.register(Expense)