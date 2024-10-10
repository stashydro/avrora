from datetime import timedelta

from django.db.models import Sum
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone

from .func import result_calc
from django.views.generic import UpdateView, CreateView, ListView, TemplateView
from .forms import DealForm
from django.shortcuts import render
from .models import Deal, Expense
from django.db.models.functions import TruncMonth
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import logout


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
