"""
Script للتحقق من كميات المخزون للفواتير
Inventory Stock Checker for Invoices
"""

from django.db.models import Sum
from invoices.models import SaleInvoice
from inventory.models import InventoryItem, Inventory
from inventory.utils import get_or_create_main_inventory


def check_invoice_inventory_availability(invoice_id):
    """
    تحقق من توفر الكميات في المخزون لفاتورة معينة
    Check inventory availability for a specific invoice
    
    Args:
        invoice_id: معرف الفاتورة
        
    Returns:
        dict: تقرير مفصل عن حالة المخزون
    """
    try:
        invoice = SaleInvoice.objects.prefetch_related('items__product').get(id=invoice_id)
    except SaleInvoice.DoesNotExist:
        return {
            "success": False,
            "error": f"Invoice with ID {invoice_id} not found"
        }
    
    inventory = get_or_create_main_inventory()
    
    results = {
        "invoice_id": invoice_id,
        "invoice_status": invoice.status,
        "total_items": invoice.items_count,
        "can_close": True,
        "items": [],
        "warnings": [],
        "errors": []
    }
    
    for item in invoice.items.all():
        product = item.product
        required_quantity = item.quantity
        
        # حساب الكمية المتاحة في المخزون
        available_items = InventoryItem.objects.filter(
            inventory=inventory,
            product=product
        )
        
        available_quantity = available_items.aggregate(
            total=Sum('remaining_quantity')
        )['total'] or 0
        
        is_sufficient = available_quantity >= required_quantity
        difference = available_quantity - required_quantity
        
        item_info = {
            "item_id": item.id,
            "product_id": product.id,
            "product_name": product.name,
            "product_e_name": product.e_name,
            "required_quantity": required_quantity,
            "available_quantity": available_quantity,
            "is_sufficient": is_sufficient,
            "difference": difference,
            "status": item.status
        }
        
        results["items"].append(item_info)
        
        if not is_sufficient:
            results["can_close"] = False
            results["errors"].append(
                f"❌ {product.name}: يحتاج {required_quantity} لكن متوفر فقط {available_quantity} (نقص: {abs(difference)})"
            )
        elif difference < 10:
            results["warnings"].append(
                f"⚠️ {product.name}: الكمية المتبقية بعد البيع قليلة ({difference} وحدة فقط)"
            )
    
    return results


def print_inventory_report(invoice_id):
    """
    طباعة تقرير مفصل عن حالة المخزون
    Print detailed inventory report
    """
    report = check_invoice_inventory_availability(invoice_id)
    
    if not report.get("success", True):
        print(f"\n❌ خطأ: {report.get('error')}")
        return
    
    print("\n" + "="*80)
    print(f"📋 تقرير المخزون لفاتورة البيع رقم: {report['invoice_id']}")
    print(f"📊 حالة الفاتورة: {report['invoice_status']}")
    print(f"📦 عدد الأصناف: {report['total_items']}")
    print("="*80)
    
    print("\n📊 تفاصيل الأصناف:")
    print("-" * 80)
    
    for item in report['items']:
        status_emoji = "✅" if item['is_sufficient'] else "❌"
        
        print(f"\n{status_emoji} الصنف: {item['product_name']}")
        print(f"   ID: {item['product_id']} | حالة العنصر: {item['status']}")
        print(f"   المطلوب: {item['required_quantity']} وحدة")
        print(f"   المتوفر: {item['available_quantity']} وحدة")
        
        if item['is_sufficient']:
            print(f"   ✓ متوفر (الفائض: {item['difference']})")
        else:
            print(f"   ✗ غير كافي (النقص: {abs(item['difference'])})")
    
    print("\n" + "-" * 80)
    
    # التحذيرات
    if report['warnings']:
        print("\n⚠️  تحذيرات:")
        for warning in report['warnings']:
            print(f"   {warning}")
    
    # الأخطاء
    if report['errors']:
        print("\n❌ أخطاء (يجب حلها قبل الإغلاق):")
        for error in report['errors']:
            print(f"   {error}")
    
    # الخلاصة
    print("\n" + "="*80)
    if report['can_close']:
        print("✅ يمكن إغلاق الفاتورة - جميع الكميات متوفرة في المخزون")
    else:
        print("❌ لا يمكن إغلاق الفاتورة - هناك نقص في المخزون")
    print("="*80 + "\n")
    
    return report


def get_inventory_summary():
    """
    الحصول على ملخص المخزون الرئيسي
    Get main inventory summary
    """
    inventory = get_or_create_main_inventory()
    
    items = InventoryItem.objects.filter(inventory=inventory).select_related('product')
    
    summary = {
        "inventory_name": inventory.name,
        "total_items": inventory.total_items,
        "total_quantity": inventory.total_quantity,
        "products": []
    }
    
    # تجميع حسب المنتج
    from collections import defaultdict
    products_dict = defaultdict(int)
    
    for item in items:
        products_dict[item.product] += item.remaining_quantity
    
    for product, quantity in products_dict.items():
        summary["products"].append({
            "product_id": product.id,
            "product_name": product.name,
            "available_quantity": quantity
        })
    
    return summary


def print_inventory_summary():
    """
    طباعة ملخص المخزون
    Print inventory summary
    """
    summary = get_inventory_summary()
    
    print("\n" + "="*80)
    print(f"📦 ملخص المخزون: {summary['inventory_name']}")
    print("="*80)
    print(f"إجمالي الأصناف: {summary['total_items']}")
    print(f"إجمالي الكمية: {summary['total_quantity']}")
    print("-" * 80)
    
    if summary['products']:
        print("\n📊 المنتجات المتوفرة:")
        for product in summary['products']:
            print(f"   • {product['product_name']}: {product['available_quantity']} وحدة")
    else:
        print("\n⚠️  المخزون فارغ!")
    
    print("\n" + "="*80 + "\n")


# دوال سريعة للاستخدام المباشر
def check_invoice_1():
    """فحص الفاتورة رقم 1"""
    return print_inventory_report(1)


def check_invoice(invoice_id):
    """فحص أي فاتورة"""
    return print_inventory_report(invoice_id)


if __name__ == "__main__":
    # مثال على الاستخدام
    print("🔍 فحص المخزون للفاتورة رقم 1...")
    check_invoice_1()
    
    print("\n📦 ملخص المخزون الكامل:")
    print_inventory_summary()

