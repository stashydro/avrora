from django.db import models
from django.db.models import CharField


# Create your clients models here.

# Создал модель для контрагентов, связь с реквизитами
taxes = [
    ('general', 'Общая'),
    ('simp', 'Упрощенная')
]
class Partner(models.Model):
    types = [
        ('client', 'Клиент'),
        ('trans', 'Перевозчик')
    ]

    name = models.CharField(max_length=255, verbose_name='Рабочее название')
    type = models.CharField(max_length=10, choices=types,verbose_name='Тип контрагента')
    tax_system = models.CharField(max_length=100, choices=taxes, verbose_name='Налоговая система')  # система налогообложения контрагента

    def __str__(self):
        type_display = dict(self.types).get(self.type, 'Неизвестный тип')
        return f'ID {self.id}: {type_display}: {self.name}'


class Rekvizity(models.Model):
    company_short = CharField(max_length=100, blank = True, verbose_name='Сокращенное название')
    company_full = CharField(max_length=200, blank = True, verbose_name='Полное название')
    inn = models.CharField(max_length=12, unique=True, verbose_name="ИНН")  # ИНН
    kpp = models.CharField(max_length=9, blank=True, null=True, verbose_name="КПП")  # КПП (не всегда обязателен)
    ogrn = models.CharField(max_length=13, unique=True, verbose_name="ОГРН")  # ОГРН
    okpo = models.CharField(max_length=10, blank=True, null=True, verbose_name="ОКПО")  # ОКПО
    legal_address = models.CharField(max_length=255, verbose_name="Юридический адрес")  # Юридический адрес
    actual_address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Фактический адрес")  # Фактический адрес
    director = models.CharField(max_length=255, verbose_name="ФИО директора")  # ФИО директора
    ati_id = models.IntegerField(null=True,blank=True)
    company = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name='counterparties')
    def __str__(self):
        return f'Реквизиты: {self.company_short}({self.company.name})'

class BankAccount(models.Model):
    rekvizity = models.ForeignKey(Rekvizity, on_delete=models.CASCADE, related_name='bank_accounts', verbose_name="Реквизиты")
    bank_name = models.CharField(max_length=255, verbose_name="Наименование банка")  # Название банка
    bic = models.CharField(max_length=9, verbose_name="БИК")  # Банковский идентификационный код
    correspondent_account = models.CharField(max_length=20, verbose_name="Корреспондентский счет")  # Корреспондентский счет
    checking_account = models.CharField(max_length=20, verbose_name="Расчетный счет")  # Расчетный счет
    def __str__(self):
        return f'Банковские реквизиты: {self.rekvizity.company_short},{self.bank_name}'

class Our_company(models.Model):
    name = models.CharField(max_length=255)
    tax_system = models.CharField(max_length=100, choices=taxes)  # система налогообложения контрагента
    company_short = CharField(max_length=100, blank = True, verbose_name='Сокращенное название')
    company_full = CharField(max_length=200, blank = True, verbose_name='Полное название')
    inn = models.CharField(max_length=12, unique=True, verbose_name="ИНН")  # ИНН
    kpp = models.CharField(max_length=9, blank=True, null=True, verbose_name="КПП")  # КПП (не всегда обязателен)
    ogrn = models.CharField(max_length=13, unique=True, verbose_name="ОГРН")  # ОГРН
    okpo = models.CharField(max_length=10, blank=True, null=True, verbose_name="ОКПО")  # ОКПО
    legal_address = models.CharField(max_length=255, verbose_name="Юридический адрес")  # Юридический адрес
    actual_address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Фактический адрес")  # Фактический адрес
    director = models.CharField(max_length=255, verbose_name="ФИО директора")  # ФИО директора
    bank_name = models.CharField(max_length=255, verbose_name="Наименование банка")  # Название банка
    bic = models.CharField(max_length=9, verbose_name="БИК")  # Банковский идентификационный код
    correspondent_account = models.CharField(max_length=20, verbose_name="Корреспондентский счет")  # Корреспондентский счет
    checking_account = models.CharField(max_length=20, verbose_name="Расчетный счет")  # Расчетный счет
    def __str__(self):
        return self.name


# Создал модель для контактов контрагентов, связь с контактами
class Contact(models.Model):
    positions = [
        ('manager', 'Менеджер'),
        ('director', 'Директор')
    ]
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name='contacts', verbose_name="Контрагент")
    name = models.CharField(max_length=255, verbose_name="ФИО контакта")  # Имя или ФИО контакта
    email = models.EmailField(verbose_name="Email")  # Email контакта
    phone = models.CharField(max_length=20, verbose_name="Телефон")  # Телефон контакта
    position = models.CharField(max_length=50, choices=positions, verbose_name='Должность')
    def __str__(self):
        position_display = dict(self.positions).get(self.position,'')
        return f'ID {self.id}: {self.partner} {position_display}: {self.name}'