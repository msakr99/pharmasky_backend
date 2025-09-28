"""
Market-related choices and constants
"""

# Product shape choices (moved from models.py for better organization)
SHAPE_CHOICES = [
    ("افلام", "افلام"),
    ("شراب", "شراب"),
    ("اسبراي", "اسبراي"),
    ("استحلاب", "استحلاب"),
    ("اقراص", "اقراص"),
    ("اقماع", "اقماع"),
    ("اكياس", "اكياس"),
    ("امبولات", "امبولات"),
    ("برطمان", "برطمان"),
    ("بلسم", "بلسم"),
    ("بودرة", "بودرة"),
    ("جل", "جل"),
    ("حبيبات فوار", "حبيبات فوار"),
    ("زيت", "زيت"),
    ("زيت شعر", "زيت شعر"),
    ("سرنجة معبأه", "سرنجة معبأه"),
    ("سيرم", "سيرم"),
    ("شامبو", "شامبو"),
    ("صابون", "صابون"),
    ("غسول فم", "غسول فم"),
    ("غسول مهبلي", "غسول مهبلي"),
    ("غسول وجه", "غسول وجه"),
    ("فوم", "فوم"),
    ("فيال", "فيال"),
    ("قطرة أذن", "قطرة أذن"),
    ("قطرة للعين", "قطرة للعين"),
    ("قلم معبأ", "قلم معبأ"),
    ("قطعة", "قطعة"),
    ("كبسولات", "كبسولات"),
    ("كريم", "كريم"),
    ("لوشن", "لوشن"),
    ("محلول", "محلول"),
    ("محلول استنشاق", "محلول استنشاق"),
    ("مرهم", "مرهم"),
    ("مرهم للعين", "مرهم للعين"),
    ("مس", "مس"),
    ("معلق", "معلق"),
    ("نقط عين", "نقط عين"),
    ("نقط فم", "نقط فم"),
]

# Alphabet choices for product categorization
LETTER_CHOICES = [(chr(i), chr(i)) for i in range(ord('A'), ord('Z') + 1)]

# Upload status choices for batch operations
UPLOAD_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('processing', 'Processing'),
    ('completed', 'Completed'),
    ('failed', 'Failed')
]

# Action choices for change log
ACTION_CHOICES = [
    ('create', 'Create'),
    ('update', 'Update'),
    ('deactivate', 'Deactivate'),
    ('reactivate', 'Reactivate'),
]
