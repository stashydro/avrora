from django.shortcuts import get_object_or_404
from clients.models import Our_company


def result_calc( client2us,trans2us,income,outcome,add_costs):
    tax_rates = {
        'simp': 1.07,
        'general': 1.2
    }
    if client2us == trans2us:
        result = (income - outcome)/tax_rates[f'{client2us.tax_system}']-add_costs
        return result
    else:
        if trans2us.tax_system == 'general':
            result = (income/1.07)-(outcome/1.2)-add_costs
            return result
        else:
            result = income/tax_rates[f'{client2us.tax_system}']-(outcome+add_costs)
            return result