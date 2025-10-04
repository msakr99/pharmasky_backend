# Simple Store Product Code Upload API

## Overview
This API endpoint allows you to upload Excel files containing store product codes with a simple format: `product_id`, `store_id`, and `code`.

## Endpoint
```
POST /api/market/store-product-codes/simple-upload/
```

## Request Format
- **Method**: POST
- **Content-Type**: multipart/form-data
- **Authentication**: Required (All authenticated users)

### Parameters
- `store_id` (integer, required): The ID of the store
- `file` (file, required): Excel file (.xlsx or .xls) containing the data

## Excel File Format
The Excel file must contain the following columns:

| Column Name | Type | Description | Required |
|-------------|------|-------------|----------|
| product_id  | Integer | Product ID from the database | Yes |
| store_id    | Integer | Store ID from the database | Yes |
| code        | Integer | Product code for this store | Yes |

### Example Excel Content:
```
product_id | store_id | code
-----------|----------|-----
1          | 1        | 1001
2          | 1        | 1002
3          | 1        | 1003
4          | 1        | 1004
5          | 1        | 1005
```

## Sample File Download
You can download a sample Excel template from:
```
GET /api/market/upload/simple-sample/
```

## Response Format

### Success Response (201 Created)
```json
{
    "success": true,
    "message": "تم رفع الملف بنجاح ومعالجته",
    "upload_id": 123,
    "status": "completed",
    "store": "Store Name",
    "file_name": "uploaded_file.xlsx",
    "uploaded_at": "2024-01-15T10:30:00Z",
    "total_rows": 5,
    "successful_rows": 4,
    "failed_rows": 1,
    "success_rate": 80.0,
    "error_log": "Row 3: Product with ID 999 not found"
}
```

### Error Response (400 Bad Request)
```json
{
    "store_id": ["Store not found"],
    "file": ["Only Excel files (.xlsx, .xls) are allowed"]
}
```

## Processing
- The file is processed synchronously (immediately)
- Results are returned in the same response
- The system will create new StoreProductCode records or update existing ones
- Duplicate product-store combinations will be updated with the new code

## Validation Rules
1. **File Format**: Only .xlsx and .xls files are accepted
2. **File Size**: Maximum 10MB
3. **Required Columns**: product_id, store_id, code must be present
4. **Data Types**: All values must be valid integers
5. **Product Validation**: product_id must exist in the database
6. **Store Validation**: store_id must exist in the database
7. **Code Validation**: code must be a positive integer

## Error Handling
- Missing columns will cause the entire upload to fail
- Invalid product_id or store_id will cause individual rows to fail
- Invalid code values (non-positive) will cause individual rows to fail
- The system will continue processing other valid rows even if some fail

## Usage Example

### cURL
```bash
curl -X POST \
  http://your-domain.com/api/market/store-product-codes/simple-upload/ \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -F 'store_id=1' \
  -F 'file=@your_file.xlsx'
```

### JavaScript (Fetch)
```javascript
const formData = new FormData();
formData.append('store_id', '1');
formData.append('file', fileInput.files[0]);

fetch('/api/market/store-product-codes/simple-upload/', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer YOUR_TOKEN'
    },
    body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

### Python (Requests)
```python
import requests

url = 'http://your-domain.com/api/market/store-product-codes/simple-upload/'
files = {'file': open('your_file.xlsx', 'rb')}
data = {'store_id': 1}
headers = {'Authorization': 'Bearer YOUR_TOKEN'}

response = requests.post(url, files=files, data=data, headers=headers)
print(response.json())
```

## Notes
- This endpoint is designed for simple, direct uploads with known product and store IDs
- For more complex uploads with product name matching, use the existing bulk upload endpoints
- The upload is processed synchronously, so results are returned immediately in the response
- No need to check status separately - all results are in the initial response
