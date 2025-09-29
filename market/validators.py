import os
import pandas as pd
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
import mimetypes


class StoreProductCodeFileValidator:
    """
    Validator for store product code upload files
    """
    
    ALLOWED_EXTENSIONS = ['.xlsx', '.xls', '.csv']
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    REQUIRED_COLUMNS = ['product_name', 'code']  # Required columns
    OPTIONAL_COLUMNS = ['product_id', 'notes', 'price']  # Optional columns for enhanced validation
    
    def __init__(self, max_size=None, allowed_extensions=None):
        self.max_size = max_size or self.MAX_FILE_SIZE
        self.allowed_extensions = allowed_extensions or self.ALLOWED_EXTENSIONS
    
    def __call__(self, file):
        """
        Validate the uploaded file
        """
        self.validate_file_size(file)
        self.validate_file_extension(file)
        self.validate_file_content(file)
    
    def validate_file_size(self, file):
        """Validate file size"""
        if file.size > self.max_size:
            raise ValidationError(
                _('File size cannot exceed %(max_size)s MB.'),
                params={'max_size': self.max_size // (1024 * 1024)},
                code='file_too_large'
            )
    
    def validate_file_extension(self, file):
        """Validate file extension"""
        file_extension = os.path.splitext(file.name)[1].lower()
        
        if file_extension not in self.allowed_extensions:
            raise ValidationError(
                _('File type "%(extension)s" is not allowed. Allowed types: %(allowed_types)s'),
                params={
                    'extension': file_extension,
                    'allowed_types': ', '.join(self.allowed_extensions)
                },
                code='invalid_extension'
            )
    
    def validate_file_content(self, file):
        """Validate file content structure"""
        try:
            # Reset file pointer
            file.seek(0)
            
            # Read file based on extension
            file_extension = os.path.splitext(file.name)[1].lower()
            
            if file_extension in ['.xlsx', '.xls']:
                df = pd.read_excel(file)
            elif file_extension == '.csv':
                df = pd.read_csv(file)
            else:
                raise ValidationError(
                    _('Unsupported file format'),
                    code='unsupported_format'
                )
            
            # Validate required columns
            missing_columns = []
            for column in self.REQUIRED_COLUMNS:
                if column not in df.columns:
                    missing_columns.append(column)
            
            if missing_columns:
                raise ValidationError(
                    _('Missing required columns: %(missing_columns)s'),
                    params={'missing_columns': ', '.join(missing_columns)},
                    code='missing_columns'
                )
            
            # Validate data types and content
            self.validate_data_content(df)
            
            # Reset file pointer for further processing
            file.seek(0)
            
        except pd.errors.EmptyDataError:
            raise ValidationError(
                _('The uploaded file is empty'),
                code='empty_file'
            )
        except pd.errors.ParserError as e:
            raise ValidationError(
                _('Error parsing file: %(error)s'),
                params={'error': str(e)},
                code='parse_error'
            )
        except Exception as e:
            raise ValidationError(
                _('Error reading file: %(error)s'),
                params={'error': str(e)},
                code='read_error'
            )
    
    def validate_data_content(self, df):
        """Validate the actual data content"""
        # Check if dataframe is empty
        if df.empty:
            raise ValidationError(
                _('The file contains no data rows'),
                code='no_data'
            )
        
        # Check for duplicate codes
        if 'code' in df.columns:
            duplicate_codes = df[df.duplicated(subset=['code'], keep=False)]
            if not duplicate_codes.empty:
                raise ValidationError(
                    _('Duplicate codes found in rows: %(rows)s'),
                    params={'rows': ', '.join(map(str, duplicate_codes.index + 2))},  # +2 for 1-based indexing and header
                    code='duplicate_codes'
                )
        
        # Validate code format (should be numeric)
        if 'code' in df.columns:
            invalid_codes = df[~df['code'].astype(str).str.isdigit()]
            if not invalid_codes.empty:
                raise ValidationError(
                    _('Invalid code format in rows: %(rows)s. Codes must be numeric.'),
                    params={'rows': ', '.join(map(str, invalid_codes.index + 2))},
                    code='invalid_code_format'
                )
        
        # Validate price format (if present, should be numeric)
        if 'price' in df.columns:
            # Remove empty values first
            price_series = df['price'].dropna()
            if not price_series.empty:
                # Convert to string and check if numeric
                price_str = price_series.astype(str)
                invalid_prices = price_series[~price_str.str.replace('.', '').str.replace('-', '').str.isdigit()]
                if not invalid_prices.empty:
                    raise ValidationError(
                        _('Invalid price format in rows: %(rows)s. Prices must be numeric.'),
                        params={'rows': ', '.join(map(str, invalid_prices.index + 2))},
                        code='invalid_price_format'
                    )
        
        # Check for empty required fields
        for column in self.REQUIRED_COLUMNS:
            if column in df.columns:
                empty_rows = df[df[column].isna() | (df[column].astype(str).str.strip() == '')]
                if not empty_rows.empty:
                    raise ValidationError(
                        _('Empty %(column)s values found in rows: %(rows)s'),
                        params={
                            'column': column,
                            'rows': ', '.join(map(str, empty_rows.index + 2))
                        },
                        code='empty_required_field'
                    )


class ProductMatchCacheValidator:
    """
    Validator for ProductMatchCache entries
    """
    
    @staticmethod
    def validate_confidence_score(value):
        """Validate confidence score is between 0 and 1"""
        if not (0 <= value <= 1):
            raise ValidationError(
                _('Confidence score must be between 0 and 1'),
                code='invalid_confidence_score'
            )
    
    @staticmethod
    def validate_search_name(value):
        """Validate search name is not empty and not too long"""
        if not value or not value.strip():
            raise ValidationError(
                _('Search name cannot be empty'),
                code='empty_search_name'
            )
        
        if len(value.strip()) > 200:
            raise ValidationError(
                _('Search name cannot exceed 200 characters'),
                code='search_name_too_long'
            )


# Custom file extension validator
store_product_code_file_validator = FileExtensionValidator(
    allowed_extensions=['xlsx', 'xls', 'csv'],
    message=_('Only Excel (.xlsx, .xls) and CSV (.csv) files are allowed.')
)
