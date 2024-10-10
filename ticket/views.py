from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import UpdateView,CreateView,ListView
from .models import Ticket
from .forms import TicketForm
# Create your views here.

class TicketView(CreateView,ListView):
    model = Ticket
    form_class = TicketForm
    template_name = 'ticket/tickets.html'  # Укажите имя вашего шаблона
    success_url = reverse_lazy('tickets')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tickets'] = self.get_queryset()
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user  # Устанавливаем текущего пользователя
        return super().form_valid(form)

    def get_queryset(self):
        if self.request.user.is_staff:  # Проверка, является ли пользователь администратором
            return Ticket.objects.all()  # Администратор видит все тикеты
        else:
            return Ticket.objects.filter(user=self.request.user)  # Обычный пользователь видит только свои тикеты