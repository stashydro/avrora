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
        context['tickets'] = Ticket.objects.all()
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user  # Устанавливаем текущего пользователя
        return super().form_valid(form)
