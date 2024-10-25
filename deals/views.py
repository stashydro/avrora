import json
from datetime import timedelta
import os
import openai
from django.db.models import Sum
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone

from clients.models import BankAccount
from clients.views import partners
from .func import result_calc
from django.views.generic import UpdateView, CreateView, ListView, TemplateView
from .forms import DealForm
from django.shortcuts import render
from clients.models import Rekvizity, Our_company, Partner, Contact
from .models import Deal, Expense
from django.db.models.functions import TruncMonth
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import logout

from openai import OpenAI
# # Create your views here.
# def home(request):
#     deals = Deal.objects.all()
#     incomplete_deals = Deal.objects.filter(complete=False)
#     context = {
#         'incomplete_deals' : incomplete_deals,
#         'deals' : deals
#     }
#     return render(request,'deals/deals.html',context)


class LogoutInterfaceView(LogoutView):
    template_name = 'deals/logout.html'


class LoginInterfaceView(LoginView):
    template_name = 'deals/login.html'



MONTHS_TRANSLATION = {
    'January': 'Январь',
    'February': 'Февраль',
    'March': 'Март',
    'April': 'Апрель',
    'May': 'Май',
    'June': 'Июнь',
    'July': 'Июль',
    'August': 'Август',
    'September': 'Сентябрь',
    'October': 'Октябрь',
    'November': 'Ноябрь',
    'December': 'Декабрь',
}

@login_required(login_url='login')
def home(request):
    deals = Deal.objects.annotate(month=TruncMonth('order_date')).order_by('month')
    grouped_deals = {}
    incomplete_deals = Deal.objects.filter(complete=False)
    for deal in deals:
        # Получаем месяц и год
        month_english = deal.order_date.strftime('%B')  # Месяц на английском
        year = deal.order_date.strftime('%Y')  # Год

        # Переводим месяц
        month_russian = MONTHS_TRANSLATION.get(month_english, month_english)
        month_year = f'{month_russian} {year}'  # Формируем строку "Месяц Год"

        if month_year not in grouped_deals:
            grouped_deals[month_year] = []
        grouped_deals[month_year].append(deal)

    context = {'grouped_deals': grouped_deals, 'incomplete_deals':incomplete_deals}  # Формируем контекст
    return render(request, 'deals/deals.html', context)


class CreateDeal(LoginRequiredMixin,CreateView):
    login_url = 'login'
    model = Deal
    form_class = DealForm
    success_url = reverse_lazy('deals')
    def form_valid(self, form):
        current_month = timezone.now().replace(day=1)
        if not Expense.objects.filter(date__year=current_month.year, date__month=current_month.month).exists():
            previous_month = current_month - timedelta(days=1)
            previous_month_expense = Expense.objects.filter(date__year=previous_month.year,
                                                            date__month=previous_month.month).first()
            if previous_month_expense:
                Expense.objects.create(
                    date=current_month,
                    salary=previous_month_expense.salary,
                    rent=previous_month_expense.rent,
                    credits=previous_month_expense.credits,
                    rest=previous_month_expense.rest

                )
        obj = form.save(commit=False)
        obj.client_text = obj.client.name
        obj.trans_text = obj.transporter.name
        client2us = obj.client_our_company
        trans2us = obj.trans_our_company
        income = obj.income
        outcome = obj.outcome
        add_costs = obj.add_costs
        obj.result = result_calc(client2us,trans2us,income,outcome,add_costs)
        obj.save()
        return super().form_valid(form)

@login_required(login_url='login')
def deal_details(request, deal_id):
    deal = get_object_or_404(Deal,pk=deal_id)
    if request.method == 'POST':
        deal.complete = True
        deal.save()
        return redirect(home)

    return render(request,'deals/deal_details.html',{'deal': deal})


class FinancialResultView(LoginRequiredMixin,TemplateView):
    template_name = 'deals/result.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Группировка сделок по месяцам с подсчетом валовой выручки и чистой прибыли
        monthly_results = Deal.objects.values('order_date__year', 'order_date__month').annotate(
            total_income=Sum('income'),
            total_profit=Sum('result')
        ).order_by('order_date__year', 'order_date__month')

        monthly_expenses = Expense.objects.values('date__year', 'date__month').annotate(
            current_salary = Sum('salary'),
            current_rent = Sum('rent'),
            current_credits = Sum('credits'),
            current_rest = Sum('rest'),
            total_expenses = Sum('salary') + Sum('rent') + Sum('credits') + Sum('rest')

        ).order_by('date__year', 'date__month')
        expense_dict = {f"{expense['date__month']:02d}-{expense['date__year']}": expense['total_expenses']
                        for expense in monthly_expenses}

        # Преобразуем в удобный формат
        financial_data = []
        for result in monthly_results:
            month_year = f"{result['order_date__month']:02d}-{result['order_date__year']}"
            total_expenses = expense_dict.get(month_year, 0)  # Расходы за месяц
            net_profit = result['total_profit'] - total_expenses
            financial_data.append({
                'month': month_year,
                'total_income': result['total_income'],
                'total_profit': result['total_profit'],
                'net_profit': net_profit,
            })

        context['financial_data'] = financial_data
        return context

def new_order(request):
    our_companies = Our_company.objects.all()
    return render(request, 'deals/new_order.html',{'our_companies': our_companies})


def check_inn(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        inn = data.get('inn')
        our_id =data.get('id')
        partner = Rekvizity.objects.filter(inn=inn).first()
        partner_banks = BankAccount.objects.filter(rekvizity=partner)
        if partner_banks:
            bank_check = 'yes'
            banks= [{'bank_name': partner_bank.bank_name, 'account': partner_bank.checking_account,
                     'id': partner_bank.id} for partner_bank in partner_banks]
        else:
            bank_check = 'no'
            banks = False
        if partner:
            partner_short = partner.company_short
            partner_type = partner.company.get_type_display()
            contact_id = partner.company.id
            contacts = Contact.objects.filter(partner=contact_id)
            cont_data = [{'id': contact.id, 'name': contact.name, 'phone': contact.phone} for contact in contacts]
            if len(cont_data) > 0:
                return JsonResponse({
                    'bank_check': bank_check,
                    'banks': banks,
                    'found': True,
                    'contact_received': True,
                    'transporter_name': partner.company.name,
                    'type': partner_type,
                    'id': partner.id,
                    'our_id': our_id,
                    'partner_short': partner_short,
                    'contacts': cont_data
                } )
            else:
                return JsonResponse({
                    'bank_check': bank_check,
                    'banks': banks,
                    'found': True,
                    'contact_received': False,
                    'transporter_name': partner.company.name,
                    'type': partner_type,
                    'id': partner.id,
                    'our_id': our_id,
                    'partner_short': partner_short,
                } )
        else:
            print('не найдено')
            return JsonResponse({'found': False, 'inn': inn})
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)

def fill_template(request):
    if request.method == 'POST':
        partner_id = request.POST.get('partner_id')
        a = request.POST.get('transporter_cont')
        if a:
            if a == 'other':
                partner_rek = Rekvizity.objects.get(pk=partner_id)
                partner = partner_rek.company
                new_contact = Contact.objects.create(
                    name=request.POST.get('other_contact'),
                    phone=request.POST.get('other_phone'),
                    position=request.POST.get('other_position'),
                    email=request.POST.get('other_email'),
                    partner=partner
                )
                transporter_cont = new_contact
            else:
                transporter_cont = Contact.objects.get(pk=a)
        else:
            phone = request.POST.get('new_phone')
            contact_existing_check = Contact.objects.filter(phone=phone)
            if contact_existing_check:
                print(True)
                contact = Contact.objects.get(phone=phone)
                transporter_cont = contact
                print(transporter_cont)
            else:
                partner_rek = Rekvizity.objects.get(pk=partner_id)
                partner = partner_rek.company
                new_contact = Contact.objects.create(
                    name=request.POST.get('new_contact'),
                    phone=request.POST.get('new_phone'),
                    position=request.POST.get('new_position'),
                    email=request.POST.get('new_email'),
                    partner=partner
                )
                transporter_cont = new_contact
        our_id = request.POST.get('our_id')
        banks = BankAccount.objects.filter(rekvizity=partner_id).first()
        ours = Our_company.objects.filter(pk=our_id).first()
        partners = Rekvizity.objects.filter(pk=partner_id).first()
        contact_id = partners.company.id
        contact = Contact.objects.filter(partner = contact_id).first()
        context = {
            'contact': contact,
            'banks': banks,
            'ours': ours,
            'transporter_cont': transporter_cont,
            'partners': partners,
            'order_date': request.POST.get('order_date'),
            'order_num': request.POST.get('order_num'),
            'transporter': request.POST.get('transporter'),
            'sender': request.POST.get('sender'),
            'receiver': request.POST.get('receiver'),
            'address_from': request.POST.get('address_from'),
            'address_to': request.POST.get('address_to'),
            'date_load': request.POST.get('date_load'),
            'date_unload': request.POST.get('date_unload'),
            'contact_send': request.POST.get('contact_send'),
            'contact_receive': request.POST.get('contact_receive'),
            'driver': request.POST.get('driver'),
            'passport_num': request.POST.get('passport_num'),
            'passport_issue': request.POST.get('passport_issue'),
            'vehicle': request.POST.get('vehicle'),
            'vehicle_num': request.POST.get('vehicle_num'),
            'phone': request.POST.get('phone'),
            'cargo': request.POST.get('cargo'),
            'quantity': request.POST.get('quantity'),
            'weight': request.POST.get('weight'),
            'volume': request.POST.get('volume'),
            'type_pack': request.POST.get('type_pack'),
            'add_info': request.POST.get('add_info'),
            'price': request.POST.get('price'),
            'conditions': request.POST.get('conditions')
        }
        print('Vse ok',transporter_cont.name, transporter_cont.position)
        return render(request, 'deals/order_template.html', context)

def process_bank(request):
    if request.method == 'POST':
        id = request.POST.get('rek_id')
        return redirect('add_bank', company_id=id)


def gpt_process(request):
    if request.method == 'POST':
        receive = json.loads(request.body)
        data = receive.get('data')
        print(f'Получили данные:{data}')
    api_key = os.getenv("OPENAI_API_KEY")
    print(api_key)
    client = OpenAI(api_key=api_key)
    completion = client.beta.chat.completions.parse(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Ты менеджер по логистике со стажем в 5 лет и опытом в различных вариантах клиентских запросов"},
            {
                "role": "user",
                "content": f"Извлеки данные о грузе и верни ответ в формате чистый json("
                           f"где cargo-тип груза,load_place-место погрузки включая город и адрес,"
                           f"unload_place-место выгрузки включая город и адрес,"
                           f"weight - вес, quantity - количество, volume-объем,load_date-дата погрузки,unload_date-дата выгрузки."
                           f"load_place и unload_place не дели по городу и адресу а запиши в одно поле).Также пожалуйста указывай единицы измерений где применимо:{data}"
            }
        ],
        temperature = 0.2
    )
    print('Получили ответ от GPT')
    result=completion.json()
    result_2 = json.loads(result)
    print(f'вот такое вот пока получилось:{result_2}')
    result_3 = result_2['choices'][0]['message']['content']
    print(f'Потом такое: {result_3}')
    cleaned_string = result_3.strip('```')
    print(f'Без кавычек: {cleaned_string}')

    cleaned_string = cleaned_string.strip("json")
    data_dict = json.loads(cleaned_string)
    response = {
            'success': True,
            'cargo': data_dict['cargo'],
            'quantity': data_dict['quantity'],
            'load_place': data_dict['load_place'],
            'unload_place': data_dict['unload_place'],
            'weight': data_dict['weight'],
            'volume': data_dict['volume'],
            'load_date': data_dict['load_date'],
            'unload_date': data_dict['unload_date']
    }
    print(response)
    return JsonResponse(response)


