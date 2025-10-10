# Generated manually on 2025-10-10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0003_safetransaction'),
    ]

    operations = [
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('monthly', 'Monthly'), ('misc', 'Miscellaneous')], max_length=20, verbose_name='نوع المصروف')),
                ('category', models.CharField(choices=[('salary', 'Salary'), ('rent', 'Rent'), ('profit_share', 'Profit Share'), ('utilities', 'Utilities'), ('stationery', 'Stationery'), ('maintenance', 'Maintenance'), ('transportation', 'Transportation'), ('communication', 'Communication'), ('other', 'Other')], max_length=20, verbose_name='فئة المصروف')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=20, verbose_name='المبلغ')),
                ('description', models.TextField(blank=True, default='', verbose_name='الوصف')),
                ('recipient', models.CharField(blank=True, default='', help_text='اسم الشخص أو الجهة المستلمة', max_length=255, verbose_name='المستلم')),
                ('payment_method', models.CharField(choices=[('ip', 'Instapay'), ('c', 'Cash'), ('w', 'Wallet'), ('p', 'Products')], default='c', max_length=10, verbose_name='طريقة الدفع')),
                ('expense_date', models.DateField(verbose_name='تاريخ المصروف')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ التسجيل')),
            ],
            options={
                'verbose_name': 'مصروف',
                'verbose_name_plural': 'المصاريف',
                'ordering': ['-expense_date', '-created_at'],
                'indexes': [
                    models.Index(fields=['type'], name='finance_exp_type_idx'),
                    models.Index(fields=['category'], name='finance_exp_category_idx'),
                    models.Index(fields=['expense_date'], name='finance_exp_date_idx'),
                ],
            },
        ),
    ]

