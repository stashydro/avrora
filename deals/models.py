from django.db import models
from clients.models import Partner,Our_company
# Create your models here.
class Deal(models.Model):
    client = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name='deals_as_client', limit_choices_to={'type': 'client'}, verbose_name="Клиент")
    client_text = models.CharField(max_length=100)
    client_our_company = models.ForeignKey(Our_company, on_delete=models.CASCADE, related_name='client_our_company',verbose_name='Договор с клиентом от нас')
    transporter = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name='deals_as_transporter', limit_choices_to={'type': 'trans'}, verbose_name="Перевозчик")
    trans_text = models.CharField(max_length=100)
    trans_our_company = models.ForeignKey(Our_company, on_delete=models.CASCADE, related_name='trans_our_company',verbose_name='Договор с перевозчиком от нас')
    income = models.FloatField(verbose_name="Доход")  # Доход от сделки
    outcome = models.FloatField(verbose_name="Расход")  # Расход по сделке
    add_costs = models.FloatField(verbose_name="Дополнительные затраты")  # Дополнительные затраты
    result = models.FloatField(verbose_name="Результат сделки")  # Результат сделки (например, чистая прибыль)
    description = models.TextField(blank=True, null=True, verbose_name="Описание сделки")  # Описание сделки
    complete = models.BooleanField(default=False, verbose_name="Сделка завершена")  # Завершена ли сделка (да/нет)
    client_contract = models.CharField(max_length=50, verbose_name='Номер заявки клиенту')
    trans_contract = models.CharField(max_length=50, verbose_name='Номер заявки перевозчику')
    order_date = models.DateField(verbose_name= "Дата заявки")
    driver = models.CharField(max_length=70, blank=True, null=True, verbose_name='Контакт водителя')
    def __str__(self):
        return f'ID: {self.id}-{self.client.name}: {self.client_contract}'

class Expense(models.Model):
    salary = models.FloatField(verbose_name='Зарплата')
    rent = models.FloatField(verbose_name='Аренда офисов')
    credits = models.FloatField(verbose_name='Кредиты')
    rest = models.FloatField(verbose_name='Остальные расходы')
    date = models.DateField(verbose_name='Дата')
