# Generated manually for search optimization

from django.contrib.postgres.operations import TrigramExtension
from django.contrib.postgres.indexes import GinIndex
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('market', '0052_rename_market_prod_confide_7g8h9i_idx_market_prod_confide_bbaa49_idx_and_more'),
    ]

    operations = [
        # Enable pg_trgm extension for trigram similarity
        TrigramExtension(),
        
        # Add GIN trigram indexes for fuzzy search
        migrations.AddIndex(
            model_name='product',
            index=GinIndex(
                fields=['name'], 
                name='prod_name_trgm', 
                opclasses=['gin_trgm_ops']
            ),
        ),
        migrations.AddIndex(
            model_name='product',
            index=GinIndex(
                fields=['e_name'], 
                name='prod_ename_trgm', 
                opclasses=['gin_trgm_ops']
            ),
        ),
        migrations.AddIndex(
            model_name='product',
            index=GinIndex(
                fields=['effective_material'], 
                name='prod_effective_material_trgm', 
                opclasses=['gin_trgm_ops']
            ),
        ),
        # Add trigram indexes for related models
        migrations.AddIndex(
            model_name='company',
            index=GinIndex(
                fields=['name'], 
                name='company_name_trgm', 
                opclasses=['gin_trgm_ops']
            ),
        ),
        migrations.AddIndex(
            model_name='category',
            index=GinIndex(
                fields=['name'], 
                name='category_name_trgm', 
                opclasses=['gin_trgm_ops']
            ),
        ),
    ]
