from django import forms

from clients.models import Partner,Our_company
from .models import Deal

class PartnerChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        # Возвращаем только имя для выпадающего списка
        return obj.client

class DealForm(forms.ModelForm):
    class Meta:
        model = Deal
        fields = ('client', 'client_our_company', 'transporter', 'trans_our_company','income', 'outcome', 'add_costs',
               'description', 'complete', 'client_contract', 'trans_contract', 'order_date'
              ,'driver')

        widgets = {
            'order_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }
        input_formats = ['%Y-%m-%d', '%d-%m-%Y', '%d/%m%Y', '%d.%m.%Y']

    def __init__(self, *args, **kwargs):
        super(DealForm, self).__init__(*args, **kwargs)
        # Переопределяем отображение партнёра в поле
        self.fields['client'].queryset = Partner.objects.filter(type='client')
        self.fields['client'].label_from_instance = lambda obj: obj.name

        # Поле для перевозчиков
        self.fields['transporter'].queryset = Partner.objects.filter(type='trans')
        self.fields['transporter'].label_from_instance = lambda obj: obj.name

