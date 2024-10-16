# Generated by Django 5.1.1 on 2024-10-04 11:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clients', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Deal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('income', models.FloatField(verbose_name='Доход')),
                ('outcome', models.FloatField(verbose_name='Расход')),
                ('add_costs', models.FloatField(verbose_name='Дополнительные затраты')),
                ('result', models.FloatField(verbose_name='Результат сделки')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание сделки')),
                ('complete', models.BooleanField(default=False, verbose_name='Сделка завершена')),
                ('client', models.ForeignKey(limit_choices_to={'type': 'client'}, on_delete=django.db.models.deletion.CASCADE, related_name='deals_as_client', to='clients.partner', verbose_name='Клиент')),
                ('transporter', models.ForeignKey(limit_choices_to={'type': 'trans'}, on_delete=django.db.models.deletion.CASCADE, related_name='deals_as_transporter', to='clients.partner', verbose_name='Перевозчик')),
            ],
        ),
    ]
