from django.urls import path
from . import views
urlpatterns = [
    path('add_deal', views.CreateDeal.as_view(), name='add_deal'),
    path('', views.home, name='deals'),
    path('deal_details/<int:deal_id>', views.deal_details, name='deal_details'),
    path('login', views.LoginInterfaceView.as_view(), name='login'),
    path('logout/', views.LogoutInterfaceView.as_view(), name='logout'),
    path('result/', views.FinancialResultView.as_view(), name='result'),
    path('new_order/', views.new_order, name='new_order'),
    path('check_inn', views.check_inn, name='check_inn'),
    path('fill_template', views.fill_template, name='fill_template'),
    path('process_bank', views.process_bank, name='process_bank'),
    path('gpt_process', views.gpt_process, name='gpt_process'),
]