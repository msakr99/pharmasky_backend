"""
Django management command to export data for RAG (Retrieval Augmented Generation)
Usage: python manage.py export_rag_data
"""
import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from market.models import Product, Company, Category
from market.ai_serializers import DrugDetailSerializer


class Command(BaseCommand):
    help = 'Export drug catalog and policies for RAG ingestion'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default='rag_data',
            help='Output directory for exported files (default: rag_data/)'
        )
        parser.add_argument(
            '--format',
            type=str,
            default='json',
            choices=['json', 'jsonl'],
            help='Output format: json or jsonl (default: json)'
        )
    
    def handle(self, *args, **options):
        output_dir = options['output_dir']
        output_format = options['format']
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        self.stdout.write(self.style.SUCCESS(f'Exporting data to {output_dir}/'))
        
        # Export drugs catalog
        self.export_drugs(output_dir, output_format)
        
        # Export sales policies
        self.export_policies(output_dir)
        
        # Export companies and categories
        self.export_metadata(output_dir)
        
        self.stdout.write(self.style.SUCCESS('✓ Export completed successfully!'))
    
    def export_drugs(self, output_dir, output_format):
        """Export all drugs/products to JSON"""
        self.stdout.write('Exporting drugs catalog...')
        
        products = Product.objects.select_related('company', 'category').all()
        serializer = DrugDetailSerializer(products, many=True)
        
        output_file = os.path.join(output_dir, f'drugs.{output_format}')
        
        if output_format == 'json':
            # Standard JSON array
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(serializer.data, f, ensure_ascii=False, indent=2)
        else:
            # JSON Lines format (one JSON object per line)
            with open(output_file, 'w', encoding='utf-8') as f:
                for item in serializer.data:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        self.stdout.write(
            self.style.SUCCESS(f'  ✓ Exported {len(serializer.data)} products to {output_file}')
        )
    
    def export_policies(self, output_dir):
        """Export sales policies and business rules"""
        self.stdout.write('Exporting sales policies...')
        
        policies = {
            "sales_policies": [
                {
                    "policy": "minimum_order",
                    "description": "الحد الأدنى للطلب هو 1000 جنيه",
                    "description_english": "Minimum order amount is 1000 EGP",
                    "value": 1000
                },
                {
                    "policy": "payment_terms",
                    "description": "الدفع نقدي أو آجل لمدة 30 يوم للعملاء المعتمدين",
                    "description_english": "Payment: Cash or 30-day credit for approved customers"
                },
                {
                    "policy": "delivery",
                    "description": "التوصيل مجاني للطلبات أكثر من 5000 جنيه",
                    "description_english": "Free delivery for orders above 5000 EGP",
                    "threshold": 5000
                },
                {
                    "policy": "returns",
                    "description": "يمكن إرجاع المنتجات خلال 7 أيام من تاريخ الاستلام",
                    "description_english": "Products can be returned within 7 days of delivery",
                    "days": 7
                },
                {
                    "policy": "discounts",
                    "description": "خصومات تصل إلى 15% للطلبات الكبيرة",
                    "description_english": "Discounts up to 15% for bulk orders",
                    "max_discount": 15
                }
            ],
            "order_rules": [
                {
                    "rule": "stock_availability",
                    "description": "يجب التحقق من توفر المنتج قبل تأكيد الطلب",
                    "description_english": "Stock availability must be checked before confirming order"
                },
                {
                    "rule": "pharmacy_verification",
                    "description": "يجب التحقق من بيانات الصيدلية المسجلة",
                    "description_english": "Pharmacy details must be verified"
                },
                {
                    "rule": "pricing",
                    "description": "الأسعار تشمل ضريبة القيمة المضافة",
                    "description_english": "Prices include VAT"
                }
            ],
            "product_categories": {
                "prescription_required": [
                    "المضادات الحيوية",
                    "أدوية القلب",
                    "الأدوية النفسية",
                    "المسكنات القوية"
                ],
                "otc": [
                    "الفيتامينات",
                    "مسكنات الألم البسيطة",
                    "أدوية البرد والإنفلونزا",
                    "المكملات الغذائية"
                ]
            }
        }
        
        output_file = os.path.join(output_dir, 'policies.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(policies, f, ensure_ascii=False, indent=2)
        
        self.stdout.write(
            self.style.SUCCESS(f'  ✓ Exported sales policies to {output_file}')
        )
        
        # Also create a text version for easier RAG consumption
        text_file = os.path.join(output_dir, 'policies.txt')
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write("سياسات البيع والشراء\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("سياسات البيع:\n")
            f.write("-" * 30 + "\n")
            for policy in policies['sales_policies']:
                f.write(f"- {policy['description']}\n")
                f.write(f"  ({policy['description_english']})\n\n")
            
            f.write("\nقواعد الطلبات:\n")
            f.write("-" * 30 + "\n")
            for rule in policies['order_rules']:
                f.write(f"- {rule['description']}\n")
                f.write(f"  ({rule['description_english']})\n\n")
            
            f.write("\nفئات المنتجات:\n")
            f.write("-" * 30 + "\n")
            f.write("أدوية تتطلب وصفة طبية:\n")
            for cat in policies['product_categories']['prescription_required']:
                f.write(f"  - {cat}\n")
            f.write("\nأدوية بدون وصفة طبية:\n")
            for cat in policies['product_categories']['otc']:
                f.write(f"  - {cat}\n")
        
        self.stdout.write(
            self.style.SUCCESS(f'  ✓ Exported text version to {text_file}')
        )
    
    def export_metadata(self, output_dir):
        """Export companies and categories for reference"""
        self.stdout.write('Exporting metadata (companies & categories)...')
        
        # Companies
        companies = list(Company.objects.values('id', 'name', 'e_name'))
        companies_file = os.path.join(output_dir, 'companies.json')
        with open(companies_file, 'w', encoding='utf-8') as f:
            json.dump(companies, f, ensure_ascii=False, indent=2)
        
        self.stdout.write(
            self.style.SUCCESS(f'  ✓ Exported {len(companies)} companies to {companies_file}')
        )
        
        # Categories
        categories = list(Category.objects.values('id', 'name', 'e_name'))
        categories_file = os.path.join(output_dir, 'categories.json')
        with open(categories_file, 'w', encoding='utf-8') as f:
            json.dump(categories, f, ensure_ascii=False, indent=2)
        
        self.stdout.write(
            self.style.SUCCESS(f'  ✓ Exported {len(categories)} categories to {categories_file}')
        )

