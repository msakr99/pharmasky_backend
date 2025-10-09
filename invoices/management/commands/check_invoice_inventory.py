"""
Django Management Command للتحقق من المخزون
Check Invoice Inventory Command
"""

from django.core.management.base import BaseCommand, CommandError
from invoices.check_inventory import (
    check_invoice_inventory_availability,
    print_inventory_report,
    print_inventory_summary
)


class Command(BaseCommand):
    help = 'فحص كميات المخزون المتاحة لفاتورة معينة | Check inventory availability for an invoice'

    def add_arguments(self, parser):
        parser.add_argument(
            'invoice_id',
            nargs='?',
            type=int,
            help='معرف الفاتورة المراد فحصها | Invoice ID to check'
        )
        
        parser.add_argument(
            '--summary',
            action='store_true',
            help='عرض ملخص المخزون الكامل | Show full inventory summary'
        )
        
        parser.add_argument(
            '--json',
            action='store_true',
            help='إرجاع النتائج بصيغة JSON | Return results in JSON format'
        )

    def handle(self, *args, **options):
        invoice_id = options.get('invoice_id')
        show_summary = options.get('summary')
        json_output = options.get('json')
        
        if show_summary:
            # عرض ملخص المخزون
            print_inventory_summary()
            return
        
        if not invoice_id:
            raise CommandError('يجب تحديد معرف الفاتورة أو استخدام --summary')
        
        # فحص الفاتورة
        if json_output:
            import json
            report = check_invoice_inventory_availability(invoice_id)
            self.stdout.write(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print_inventory_report(invoice_id)

