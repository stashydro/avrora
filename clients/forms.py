from django import forms

from .models import Partner,Contact,Rekvizity, BankAccount

class RekvizityForm(forms.ModelForm):
    class Meta:
        model = Rekvizity
        fields = ('company_short','company_full','inn','kpp',
                  'ogrn','okpo','legal_address','actual_address',
                  'director','ati_id')
        widgets = {
            'inn': forms.TextInput(attrs={'placeholder': 'Введите ИНН'}),
        }

class BankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = ('bank_name','bic','correspondent_account','checking_account')
        widgets = {
            'bic': forms.TextInput(attrs={'placeholder': 'Введите БИК'}),
        }
class PartnerForm(forms.ModelForm):
    class Meta:
        model = Partner
        fields = ('name','type','tax_system')

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('name','email','phone','position')
class ContactAddForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('partner','name','email','phone','position')
