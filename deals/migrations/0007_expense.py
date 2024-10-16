# Generated by Django 5.1.1 on 2024-10-10 04:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deals', '0006_alter_deal_client_our_company_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('salary', models.FloatField(verbose_name='Зарплата')),
                ('rent', models.FloatField(verbose_name='Аренда офисов')),
                ('credits', models.FloatField(verbose_name='Кредиты')),
                ('rest', models.FloatField(verbose_name='Остальные расходы')),
                ('date', models.DateField(verbose_name='Дата')),
            ],
        ),
    ]
