# 🔍 Advanced Search Implementation

## Overview

This implementation adds PostgreSQL Full Text Search (FTS) and Trigram similarity search to the Product model, providing:

- **Arabic-first search** with English fallback
- **Fuzzy matching** for typos and approximate queries
- **Multi-field search** across name, e_name, effective_material, company, and category
- **Relevance ranking** with configurable weights
- **Performance optimization** with proper indexes
- **Backward compatibility** with existing search

## Files Modified

### 1. Settings (`project/settings/base.py`)
- Added `django.contrib.postgres` to `THIRD_PARTY_APPS`
- Added `SearchPerformanceMiddleware` to `MIDDLEWARE`

### 2. Models (`market/models.py`)
- No changes needed (indexes added via migrations)

### 3. Views (`market/views.py`)
- Enhanced `ProductListAPIView.get_queryset()` with advanced search logic
- Added support for `q`, `search_mode`, `min_similarity` parameters
- Maintained backward compatibility with existing `search` parameter

### 4. Migrations
- `0053_enable_trgm_and_indexes.py`: Enables pg_trgm extension and creates trigram indexes
- `0054_product_fts_index.py`: Creates functional GIN indexes for FTS

### 5. Middleware (`core/middleware/search_performance.py`)
- New middleware to log search performance and slow queries

## New API Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `q` | string | - | Advanced search query |
| `search_mode` | string | `hybrid` | Search mode: `fts`, `trigram`, `hybrid` |
| `min_similarity` | float | `0.2` | Minimum similarity for trigram (0.0-1.0) |

## Search Modes

### FTS Mode (`search_mode=fts`)
- Uses PostgreSQL Full Text Search
- Best for exact phrase matching
- Arabic-first with English fallback
- Weighted fields: name (A), effective_material (B), company (C), e_name (D)

### Trigram Mode (`search_mode=trigram`)
- Uses PostgreSQL trigram similarity
- Best for fuzzy matching and typos
- Handles Arabic and English text
- Configurable similarity threshold

### Hybrid Mode (`search_mode=hybrid`) - Default
- Combines FTS and trigram for best results
- Uses both exact and fuzzy matching
- Calculates combined score: `rank * 1.0 + similarity * 0.7`

## Database Changes

### Extensions Enabled
```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

### Indexes Created
```sql
-- Trigram indexes
CREATE INDEX prod_name_trgm ON market_product USING GIN (name gin_trgm_ops);
CREATE INDEX prod_ename_trgm ON market_product USING GIN (e_name gin_trgm_ops);
CREATE INDEX prod_effective_material_trgm ON market_product USING GIN (effective_material gin_trgm_ops);
CREATE INDEX company_name_trgm ON market_company USING GIN (name gin_trgm_ops);
CREATE INDEX category_name_trgm ON market_category USING GIN (name gin_trgm_ops);

-- FTS indexes
CREATE INDEX prod_fts_idx ON market_product USING GIN (
  to_tsvector('simple', coalesce(name,'') || ' ' || coalesce(e_name,'') || ' ' || coalesce(effective_material,''))
);
CREATE INDEX company_fts_idx ON market_company USING GIN (
  to_tsvector('simple', coalesce(name,'') || ' ' || coalesce(e_name,''))
);
CREATE INDEX category_fts_idx ON market_category USING GIN (
  to_tsvector('simple', coalesce(name,'') || ' ' || coalesce(e_name,''))
);
```

## Usage Examples

### Basic Search
```http
GET /api/v1/market/products/?q=باراسيتامول
```

### FTS Only
```http
GET /api/v1/market/products/?q=باراسيتامول&search_mode=fts
```

### Fuzzy Search
```http
GET /api/v1/market/products/?q=paracetamol&search_mode=trigram&min_similarity=0.3
```

### Hybrid Search (Default)
```http
GET /api/v1/market/products/?q=أسبرين&search_mode=hybrid
```

## Performance Features

### Query Optimization
- `select_related('company', 'category')` for efficient joins
- Prefix matching boost for exact starts-with matches
- Combined scoring for hybrid mode

### Performance Monitoring
- Search timing logged for all queries
- Slow query warnings for queries >1 second
- Query performance metrics in application logs

### Caching Recommendations
- Consider Redis caching for frequent search queries
- Cache search results for 30-60 seconds
- Use cache keys based on query parameters

## Testing

### Manual Testing
```bash
# Run the test script
python test_advanced_search.py
```

### API Testing
```bash
# Test FTS
curl "http://localhost:8000/api/v1/market/products/?q=باراسيتامول&search_mode=fts"

# Test Trigram
curl "http://localhost:8000/api/v1/market/products/?q=paracetamol&search_mode=trigram&min_similarity=0.2"

# Test Hybrid
curl "http://localhost:8000/api/v1/market/products/?q=أسبرين&search_mode=hybrid"
```

## Migration Instructions

### 1. Apply Migrations
```bash
python manage.py migrate
```

### 2. Verify Extensions
```sql
-- Check if pg_trgm is enabled
SELECT * FROM pg_extension WHERE extname = 'pg_trgm';
```

### 3. Test Search
```bash
# Run test script
python test_advanced_search.py
```

## Performance Benchmarks

### Expected Performance
- **FTS**: 10-50ms for typical queries
- **Trigram**: 20-100ms for fuzzy matching
- **Hybrid**: 30-150ms for combined search

### Optimization Tips
1. Use `search_mode=fts` for exact matches (fastest)
2. Use `search_mode=trigram` for fuzzy matching
3. Use `search_mode=hybrid` for best accuracy
4. Adjust `min_similarity` based on data quality
5. Monitor slow queries in logs

## Troubleshooting

### Common Issues

1. **Extension not found**
   ```sql
   CREATE EXTENSION IF NOT EXISTS pg_trgm;
   ```

2. **Index not used**
   - Check if indexes exist: `\d market_product`
   - Analyze query plan: `EXPLAIN ANALYZE`

3. **Slow queries**
   - Check logs for slow query warnings
   - Consider adjusting similarity thresholds
   - Use FTS mode for exact matches

### Debug Commands
```sql
-- Check indexes
\d market_product

-- Analyze query
EXPLAIN ANALYZE SELECT * FROM market_product WHERE name % 'باراسيتامول';

-- Check extensions
SELECT * FROM pg_extension WHERE extname = 'pg_trgm';
```

## Future Enhancements

### Potential Improvements
1. **Search suggestions** based on trigram similarity
2. **Search analytics** with query frequency tracking
3. **Auto-complete** using prefix matching
4. **Search result caching** with Redis
5. **Multi-language support** with language detection

### Advanced Features
1. **Search result highlighting** with matched terms
2. **Search result snippets** with context
3. **Search result ranking** based on user behavior
4. **Search result filtering** by additional criteria

## Monitoring

### Logs to Monitor
- Search performance logs
- Slow query warnings
- Search result counts
- User search patterns

### Metrics to Track
- Average search response time
- Search result relevance
- Most common search queries
- Search success rate

## Conclusion

This implementation provides a robust, scalable search solution that:

- ✅ Supports Arabic-first search with English fallback
- ✅ Handles typos and approximate matching
- ✅ Provides multiple search modes for different use cases
- ✅ Maintains backward compatibility
- ✅ Includes performance monitoring
- ✅ Uses proper database indexes for optimization

The search system is now ready for production use with comprehensive testing and monitoring capabilities.
