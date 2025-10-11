# Generated manually for wholesale offers feature
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='offer',
            name='is_wholesale',
            field=models.BooleanField(default=False, help_text='هل هذا عرض جملة؟'),
        ),
        migrations.AddField(
            model_name='offer',
            name='wholesale_min_quantity',
            field=models.PositiveIntegerField(default=10, help_text='الحد الأدنى للطلب من الصنف (افتراضي: 10 علب)'),
        ),
        migrations.AddField(
            model_name='offer',
            name='wholesale_increment',
            field=models.PositiveIntegerField(default=5, help_text='مقدار الزيادة المسموح بها (افتراضي: 5 علب)'),
        ),
        migrations.AddField(
            model_name='offer',
            name='is_max_wholesale',
            field=models.BooleanField(default=False, help_text='هل هذا أفضل عرض جملة للمنتج؟'),
        ),
    ]

