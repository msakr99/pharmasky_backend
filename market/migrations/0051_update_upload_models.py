# Generated manually for updating upload models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0018_remove_city_country_remove_city_delivery_and_more'),
        ('market', '0050_codechangelog_productmatchcache_and_more'),
        migrations.swappable_dependency('accounts.user'),
    ]

    operations = [
        # Add new fields to StoreProductCodeUpload
        migrations.AddField(
            model_name='storeproductcodeupload',
            name='uploaded_by',
            field=models.ForeignKey(
                blank=True, 
                null=True, 
                on_delete=django.db.models.deletion.SET_NULL, 
                related_name='uploaded_product_codes', 
                to='accounts.user'
            ),
        ),
        migrations.AddField(
            model_name='storeproductcodeupload',
            name='file_size',
            field=models.BigIntegerField(blank=True, help_text='File size in bytes', null=True),
        ),
        migrations.AddField(
            model_name='storeproductcodeupload',
            name='file_name',
            field=models.CharField(blank=True, help_text='Original file name', max_length=255),
        ),
        
        # Add new fields to ProductMatchCache
        migrations.AddField(
            model_name='productmatchcache',
            name='last_accessed',
            field=models.DateTimeField(auto_now=True, help_text='Last time this cache entry was used'),
        ),
        migrations.AddField(
            model_name='productmatchcache',
            name='access_count',
            field=models.PositiveIntegerField(default=0, help_text='Number of times this cache was accessed'),
        ),
        
        # Add new indexes
        migrations.AddIndex(
            model_name='storeproductcodeupload',
            index=models.Index(fields=['store', 'status'], name='market_stor_store_i_8a2b3c_idx'),
        ),
        migrations.AddIndex(
            model_name='storeproductcodeupload',
            index=models.Index(fields=['uploaded_at'], name='market_stor_uploade_9d4e5f_idx'),
        ),
        migrations.AddIndex(
            model_name='storeproductcodeupload',
            index=models.Index(fields=['status'], name='market_stor_status_1a2b3c_idx'),
        ),
        migrations.AddIndex(
            model_name='productmatchcache',
            index=models.Index(fields=['confidence_score'], name='market_prod_confide_7g8h9i_idx'),
        ),
        migrations.AddIndex(
            model_name='productmatchcache',
            index=models.Index(fields=['last_accessed'], name='market_prod_last_ac_j1k2l3_idx'),
        ),
        
        # Update verbose names
        migrations.AlterModelOptions(
            name='storeproductcodeupload',
            options={'ordering': ['-uploaded_at'], 'verbose_name': 'Store Product Code Upload', 'verbose_name_plural': 'Store Product Code Uploads'},
        ),
        migrations.AlterModelOptions(
            name='productmatchcache',
            options={'ordering': ['-confidence_score', '-created_at'], 'verbose_name': 'Product Match Cache', 'verbose_name_plural': 'Product Match Caches'},
        ),
    ]
