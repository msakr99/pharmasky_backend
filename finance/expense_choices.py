from django.db import models
from django.utils.translation import gettext_lazy as _


class ExpenseTypeChoice(models.TextChoices):
    """نوع المصروف"""
    MONTHLY = "monthly", _("Monthly")  # مصاريف شهرية
    MISCELLANEOUS = "misc", _("Miscellaneous")  # مصاريف نثرية


class ExpenseCategoryChoice(models.TextChoices):
    """فئة المصروف"""
    # مصاريف شهرية
    SALARY = "salary", _("Salary")  # مرتبات
    RENT = "rent", _("Rent")  # إيجار
    PROFIT_SHARE = "profit_share", _("Profit Share")  # أرباح شركاء
    UTILITIES = "utilities", _("Utilities")  # مرافق (كهرباء، مياه، إلخ)
    
    # مصاريف نثرية
    STATIONERY = "stationery", _("Stationery")  # قرطاسية (ورق، دفاتر)
    MAINTENANCE = "maintenance", _("Maintenance")  # صيانة
    TRANSPORTATION = "transportation", _("Transportation")  # مواصلات
    COMMUNICATION = "communication", _("Communication")  # اتصالات
    OTHER = "other", _("Other")  # أخرى

