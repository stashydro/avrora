from django.urls import path
from .views import index
from .forms import RekvizityForm,BankAccountForm,PartnerForm,ContactForm
from . import views

urlpatterns = [
    # path('', index, name='index'),
    path('add_partner', views.add_partner, name='add_partner'),
    path('add_rekvizity/<int:company_id>/', views.add_rekvizity, name='add_rekvizity'),
    path('add_bank/<int:company_id>/', views.add_bank, name='add_bank'),
    path('add_contact', views.add_contact, name='add_contact'),
    path('add_contact_ext/<int:company_id>/', views.add_contact_ext, name='add_contact_ext'),
    path('get_company_info', views.get_company_info, name='get_company_info'),
    path('get_bank_info', views.get_bank_info, name='get_bank_info'),
    path('success', views.success, name='success'),
    path('partners', views.partners, name='partners'),
    path('partner_detail/<int:partner_id>/', views.partner_detail, name='partner_detail'),
    path('newTransporterFromOrder', views.newTransporterFromOrder, name='newTransporterFromOrder'),

    ]