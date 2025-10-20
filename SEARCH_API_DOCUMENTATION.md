# 🔍 Advanced Search API Documentation

## Enhanced Product Search Endpoint

The `/api/v1/market/products/` endpoint now supports advanced PostgreSQL-based search with Full Text Search (FTS) and Trigram similarity.

## New Query Parameters

### Search Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `q` | string | - | Advanced search query (replaces `search` for new functionality) |
| `search_mode` | string | `hybrid` | Search mode: `fts`, `trigram`, or `hybrid` |
| `min_similarity` | float | `0.2` | Minimum similarity threshold for trigram search (0.0-1.0) |
| `fields` | string | - | Comma-separated field list to search in |

### Search Modes

#### 1. FTS Mode (`search_mode=fts`)
- Uses PostgreSQL Full Text Search
- Best for exact phrase matching
- Arabic-first with English fallback
- Weighted fields: name (A), effective_material (B), company (C), e_name (D)

#### 2. Trigram Mode (`search_mode=trigram`)
- Uses PostgreSQL trigram similarity
- Best for fuzzy matching and typos
- Handles Arabic and English text
- Configurable similarity threshold

#### 3. Hybrid Mode (`search_mode=hybrid`) - Default
- Combines FTS and trigram for best results
- Uses both exact and fuzzy matching
- Calculates combined score: `rank * 1.0 + similarity * 0.7`

## API Examples

### Basic Search
```http
GET /api/v1/market/products/?q=باراسيتامول
```

### FTS Only Search
```http
GET /api/v1/market/products/?q=باراسيتامول&search_mode=fts
```

### Fuzzy Search with Custom Threshold
```http
GET /api/v1/market/products/?q=paracetamol&search_mode=trigram&min_similarity=0.3
```

### Hybrid Search (Default)
```http
GET /api/v1/market/products/?q=أسبرين&search_mode=hybrid
```

### Search with Field Filtering
```http
GET /api/v1/market/products/?q=نوفارتس&fields=company,name
```

## Response Format

The response includes additional fields for search ranking:

```json
{
  "count": 25,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "باراسيتامول 500 مجم",
      "e_name": "Paracetamol 500mg",
      "company": "نوفارتس",
      "category": "مسكنات",
      "effective_material": "باراسيتامول",
      "public_price": "15.50",
      "rank": 0.8,        // FTS ranking (when using FTS/hybrid)
      "sim": 0.95,        // Trigram similarity (when using trigram/hybrid)
      "score": 0.85,      // Combined score (hybrid mode)
      "starts": 1         // Prefix match boost
    }
  ]
}
```

## Search Field Weights

### FTS Weights
- **name**: Weight A (highest priority)
- **effective_material**: Weight B
- **company__name**: Weight C
- **e_name**: Weight D (lowest priority)

### Trigram Weights
- **name**: 1.0 (100%)
- **effective_material**: 0.8 (80%)
- **company__name**: 0.6 (60%)
- **e_name**: 0.4 (40%)

## Performance Features

### Indexes Created
- GIN trigram indexes on: `name`, `e_name`, `effective_material`
- GIN trigram indexes on related models: `company.name`, `category.name`
- Functional GIN FTS indexes for combined text search

### Query Optimization
- `select_related('company', 'category')` for efficient joins
- Prefix matching boost for exact starts-with matches
- Combined scoring for hybrid mode

### Performance Monitoring
- Search timing logged for queries >1 second
- Query performance metrics available in logs
- Slow query warnings for optimization

## Backward Compatibility

- Original `?search=` parameter still works
- Existing filters and pagination unchanged
- No breaking changes to current API consumers

## Migration Requirements

### Database Extensions
```sql
-- Enable pg_trgm extension
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

### Indexes
```sql
-- Trigram indexes
CREATE INDEX prod_name_trgm ON market_product USING GIN (name gin_trgm_ops);
CREATE INDEX prod_ename_trgm ON market_product USING GIN (e_name gin_trgm_ops);
CREATE INDEX prod_effective_material_trgm ON market_product USING GIN (effective_material gin_trgm_ops);

-- FTS indexes
CREATE INDEX prod_fts_idx ON market_product USING GIN (
  to_tsvector('simple', coalesce(name,'') || ' ' || coalesce(e_name,'') || ' ' || coalesce(effective_material,''))
);
```

## Usage Tips

### For Arabic Text
- Use `search_mode=fts` for exact Arabic phrase matching
- Use `search_mode=hybrid` for best Arabic results with typo tolerance

### For English Text
- Use `search_mode=trigram` for English fuzzy matching
- Use `search_mode=hybrid` for mixed Arabic/English content

### For Typo Tolerance
- Use `search_mode=trigram` with `min_similarity=0.2-0.4`
- Lower values = more tolerance, higher values = stricter matching

### For Performance
- Use `fields` parameter to limit search scope
- FTS mode is generally faster than trigram for large datasets
- Hybrid mode provides best accuracy but may be slower

## Error Handling

- Invalid `search_mode` values default to `hybrid`
- Invalid `min_similarity` values default to `0.2`
- Empty `q` parameter falls back to original search behavior
- Search errors are logged for debugging

## Monitoring and Analytics

Search performance is automatically logged with:
- Query text
- Response time
- Search mode used
- Result count
- Slow query warnings (>1 second)

Check application logs for search performance metrics.
