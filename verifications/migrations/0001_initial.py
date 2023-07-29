# Generated by Django 4.2.1 on 2023-07-29 10:14

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AppID',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('app_id', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=100, null=True)),
                ('last_name', models.CharField(blank=True, max_length=100, null=True)),
                ('middle_name', models.CharField(blank=True, max_length=100, null=True)),
                ('is_verify', models.BooleanField(default=False)),
                ('bvn', models.CharField(blank=True, max_length=11, null=True)),
                ('phone', models.CharField(max_length=26)),
                ('email', models.EmailField(blank=True, max_length=254, null=True, unique=True)),
                ('address', models.CharField(blank=True, max_length=500, null=True)),
                ('marital_status', models.CharField(blank=True, max_length=20, null=True)),
                ('photo_id', models.CharField(blank=True, max_length=500, null=True)),
                ('dob', models.CharField(blank=True, max_length=15, null=True)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female')], default='M', max_length=20)),
                ('nationality', models.CharField(blank=True, max_length=100, null=True)),
                ('borrower_id', models.CharField(max_length=200, null=True)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('APPROVE', 'Approve'), ('REJECT', 'Reject'), ('INVITED', 'INVITED')], default='INVITED', max_length=20)),
                ('is_invited', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=datetime.datetime.utcnow, null=True)),
                ('residential_address', models.CharField(max_length=200)),
                ('residential_type', models.CharField(choices=[('OWNED', 'OWNED'), ('RENT', 'RENT'), ('INHERITED', 'INHERITED')], max_length=20)),
                ('lga_origin', models.CharField(max_length=100, null=True)),
                ('lga_residence', models.CharField(max_length=100, null=True)),
                ('nin', models.CharField(max_length=15, null=True)),
                ('watchlist', models.CharField(default='No', max_length=20)),
                ('app_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='verifications.appid')),
            ],
        ),
        migrations.CreateModel(
            name='RiskThreshold',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_balance', models.DecimalField(decimal_places=2, max_digits=16)),
                ('employed', models.BooleanField()),
                ('minimum_monthly_salary', models.DecimalField(decimal_places=2, max_digits=16)),
                ('country', models.CharField(choices=[('NIGERIA', 'Pending'), ('INDIA', 'Approve'), ('INDONESIA', 'Reject')], max_length=10, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='CustomerIncomeData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('average_monthly_income', models.DecimalField(decimal_places=2, max_digits=16)),
                ('total_money_received', models.DecimalField(decimal_places=2, max_digits=16)),
                ('total_money_spent', models.DecimalField(decimal_places=2, max_digits=16)),
                ('eligibility_amount', models.DecimalField(decimal_places=2, max_digits=20)),
                ('debt_to_income', models.CharField(max_length=20, null=True)),
                ('debt_to_income_reason', models.CharField(max_length=200, null=True)),
                ('institution_name', models.CharField(max_length=30)),
                ('bank_code', models.IntegerField()),
                ('type', models.CharField(max_length=100)),
                ('balance', models.DecimalField(decimal_places=2, max_digits=10)),
                ('account_number', models.CharField(max_length=14)),
                ('customer', models.ManyToManyField(to='verifications.customer')),
            ],
        ),
        migrations.AddField(
            model_name='customer',
            name='risk_country_threshold',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='verifications.riskthreshold'),
        ),
    ]
