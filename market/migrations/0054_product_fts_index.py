# Generated manually for Full Text Search optimization

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('market', '0053_enable_trgm_and_indexes'),
    ]

    operations = [
        # Create functional GIN index for Full Text Search
        migrations.RunSQL(
            sql=(
                "CREATE INDEX IF NOT EXISTS prod_fts_idx ON market_product USING GIN ("
                "to_tsvector('simple', coalesce(name,'') || ' ' || coalesce(e_name,'') || ' ' || coalesce(effective_material,''))"
                ");"
            ),
            reverse_sql="DROP INDEX IF EXISTS prod_fts_idx;",
        ),
        # Create FTS index for company names
        migrations.RunSQL(
            sql=(
                "CREATE INDEX IF NOT EXISTS company_fts_idx ON market_company USING GIN ("
                "to_tsvector('simple', coalesce(name,'') || ' ' || coalesce(e_name,''))"
                ");"
            ),
            reverse_sql="DROP INDEX IF EXISTS company_fts_idx;",
        ),
        # Create FTS index for category names
        migrations.RunSQL(
            sql=(
                "CREATE INDEX IF NOT EXISTS category_fts_idx ON market_category USING GIN ("
                "to_tsvector('simple', coalesce(name,'') || ' ' || coalesce(e_name,''))"
                ");"
            ),
            reverse_sql="DROP INDEX IF EXISTS category_fts_idx;",
        ),
    ]
