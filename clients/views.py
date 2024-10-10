from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Rekvizity,BankAccount,Partner,Contact
from .forms import RekvizityForm, BankAccountForm, PartnerForm, ContactForm, ContactAddForm
from dadata import Dadata
import json
from django.contrib.auth.decorators import login_required


# Create your views here.
def index(request):
    return render(request, 'clients/index.html')

@login_required(login_url='login')
def partners(request):
    partners = Partner.objects.all()
    clients = Partner.objects.filter(type='client')
    trans = Partner.objects.filter(type='trans')
    context = {
        'clients': clients,
        'trans': trans
    }
    return render(request,'clients/partners.html', context)

@login_required(login_url='login')
def add_partner(request):
    if request.method == 'POST':
        form = PartnerForm(request.POST)
        if form.is_valid():
            partner = form.save()
            request.session['company_id'] = partner.id
            company_id = partner.id
            if 'save_and_exit' in request.POST:
                return redirect('partners')
            else:
                return redirect('add_rekvizity',company_id=company_id)
    else:
        form = PartnerForm()

    return render(request,'clients/add_partner.html', {'form': form})

@login_required(login_url='login')
def add_rekvizity(request, company_id):
    partner = get_object_or_404(Partner, id=company_id)
    if request.method == 'POST':
        form = RekvizityForm(request.POST)
        if form.is_valid():
            rek = form.save(commit=False)
            rek.company = partner
            rek.save()
            rek_id = rek.id
            if 'save_and_exit' in request.POST:
                return redirect('partner_detail',company_id)
            else:
                return redirect('add_bank',company_id=rek_id)
    else:
        form = RekvizityForm(initial={'rekvizity': company_id})

    return render(request,'clients/add_rekvizity.html', {'form': form})

@login_required(login_url='login')
def get_company_info(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        inn = data.get('inn')

        if inn:
            token = "c8e8c500db8f89179aaec497d7cd964108e09c97"
            dadata = Dadata(token)

            try:
                result = dadata.find_by_id("party", inn)
                if result:
                    company = result[0]['data']
                    response_data = {
                        'success': True,
                        'company_short': company['name']['short_with_opf'],
                        'company_full': company['name']['full_with_opf'],  # Полное название
                        'legal_address': company['address']['value'],  # Юридический адрес
                        'director': company['management']['name'],  # Директор
                        'ogrn': company['ogrn'],  # ОГРН
                        'kpp': company['kpp'],
                        'okpo': company['okpo'],# КПП
                    }
                else:
                    response_data = {'success': False, 'message': 'Компания не найдена'}
            except Exception as e:
                response_data = {'success': False, 'message': str(e)}
        else:
            response_data = {'success': False, 'message': 'ИНН не указан'}

        return JsonResponse(response_data)


@login_required(login_url='login')
def add_bank(request, company_id):
    if request.method == 'POST':
        form = BankAccountForm(request.POST)
        if form.is_valid():
            company_id = company_id
            bank_details = form.save(commit=False)
            company = Rekvizity.objects.get(id = company_id)
            bank_details.rekvizity = company
            bank_details.save()
            if 'save_and_exit' in request.POST:
                return redirect('partners')
            else:
                return redirect('add_contact') # Перенаправляем на страницу успеха
    else:
        form = BankAccountForm()

    return render(request, 'clients/add_bank.html', {'form': form})

@login_required(login_url='login')
def get_bank_info(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        bic = data.get('bic')

        if bic:
            token = "c8e8c500db8f89179aaec497d7cd964108e09c97"
            dadata = Dadata(token)

            try:
                result = dadata.find_by_id("bank", bic)
                if result:
                    response_data = {
                        'success': True,
                        'bank_name': result[0]['value'],
                        'correspondent_account': result[0]['data']['correspondent_account'],
                    }
                else:
                    response_data = {'success': False, 'message': 'Банк не найден'}
            except Exception as e:
                response_data = {'success': False, 'message': str(e)}
        else:
            response_data = {'success': False, 'message': 'БИК не указан'}

        return JsonResponse(response_data)


@login_required(login_url='login')
def add_contact(request):
    partner = request.session.get('company_id')
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            partner_obj = Partner.objects.get(id = partner)
            contact.partner = partner_obj
            contact.save()
            return redirect('success') # Перенаправляем на страницу успеха
    else:
        form = ContactForm()
    return render(request, 'clients/add_contact.html', {'form': form})


@login_required(login_url='login')
def add_contact_ext(request, company_id):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            partner_obj = Partner.objects.get(id = company_id)
            contact.partner = partner_obj
            contact.save()
            return redirect('partner_detail', company_id) # Перенаправляем на страницу успеха
    else:
        form = ContactForm()
    return render(request, 'clients/add_contact_ext.html', {'form': form})


@login_required(login_url='login')
def success(request):
    return render(request, 'clients/done.html')


@login_required(login_url='login')
def partner_detail(request,partner_id):
    partner = get_object_or_404(Partner,pk=partner_id)
    rek = Rekvizity.objects.filter(company=partner).first()
    if rek is not None:
        partner_rek = get_object_or_404(Rekvizity,pk=rek.id)
    else:
        partner_rek = None
    banks = BankAccount.objects.filter(rekvizity=rek) if rek else None

    contacts = Contact.objects.filter(partner=partner)
    context = {
        'partner': partner,
        'partner_rek': partner_rek,
        'partner_banks': banks,
        'partner_contacts': contacts,
        'rek_missing': partner_rek is None,
        'bank_missing': banks is None,
        'contact_missing': contacts is None
    }
    return render(request,'clients/partner_detail.html', context)