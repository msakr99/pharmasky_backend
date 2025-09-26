try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False

from django.core.validators import RegexValidator, FileExtensionValidator
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

PDF_VALIDATOR = FileExtensionValidator(["pdf"])
TXT_VALIDATOR = FileExtensionValidator(["txt"])
EXCEL_VALIDATOR = FileExtensionValidator(["xlsx", "xls"])
IMAGE_VALIDATOR = FileExtensionValidator(["jpg", "jpeg", "png"])


def validate_excel_extension(file):
    if not MAGIC_AVAILABLE:
        # Fallback to file extension validation
        EXCEL_VALIDATOR(file)
        return
    
    accept = [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel",
    ]
    file_mime_type = magic.from_buffer(file.read(2048), mime=True)
    if file_mime_type not in accept:
        raise ValidationError(_("Only MS Excel files are supported [*.xlsx, *.xls]."))


def validate_pdf_extension(file):
    if not MAGIC_AVAILABLE:
        # Fallback to file extension validation
        PDF_VALIDATOR(file)
        return
    
    accept = ["application/pdf"]
    file_mime_type = magic.from_buffer(file.read(1024), mime=True)
    if file_mime_type not in accept:
        raise ValidationError(_("Only PDF files are supported [*.pdf]."))


def validate_image_extension(file):
    if not MAGIC_AVAILABLE:
        # Fallback to file extension validation
        IMAGE_VALIDATOR(file)
        return
    
    accept = ["image/png", "image/jpeg"]
    file_mime_type = magic.from_buffer(file.read(1024), mime=True)
    if file_mime_type not in accept:
        raise ValidationError(_("Only Image files are supported."))


def validate_pdf_or_image_extension(file):
    if not MAGIC_AVAILABLE:
        # Fallback to file extension validation
        from django.core.validators import FileExtensionValidator
        validator = FileExtensionValidator(["pdf", "jpg", "jpeg", "png"])
        validator(file)
        return
    
    accept = ["image/png", "image/jpeg", "application/pdf"]
    file_mime_type = magic.from_buffer(file.read(1024), mime=True)
    if file_mime_type not in accept:
        raise ValidationError(_("Only PDF or Image files are Supported."))
