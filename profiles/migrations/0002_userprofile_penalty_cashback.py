# Generated manually

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='late_payment_penalty_percentage',
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal('0.20'),
                help_text='Daily penalty percentage for late payments (default 0.20%)',
                max_digits=4
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='early_payment_cashback_percentage',
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal('0.10'),
                help_text='Daily cashback percentage for early payments (default 0.10%)',
                max_digits=4
            ),
        ),
    ]

