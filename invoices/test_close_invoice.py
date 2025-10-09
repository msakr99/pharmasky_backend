"""
Simple test script to debug close_sale_invoice errors
"""

def test_close_invoice(invoice_id):
    """
    Test closing an invoice and catch any errors
    """
    from invoices.models import SaleInvoice
    from invoices.utils import close_sale_invoice
    from rest_framework.exceptions import ValidationError
    
    try:
        print(f"\n🔍 Testing invoice {invoice_id}...")
        
        # Get invoice
        invoice = SaleInvoice.objects.prefetch_related('items__product').get(id=invoice_id)
        print(f"✅ Invoice found: {invoice}")
        print(f"   Status: {invoice.status}")
        print(f"   Items count: {invoice.items_count}")
        
        # Check items status
        print(f"\n📦 Checking items status...")
        for item in invoice.items.all():
            print(f"   - {item.product.name}: {item.status}")
        
        # Try to close
        print(f"\n🔒 Attempting to close invoice...")
        closed_invoice = close_sale_invoice(invoice)
        
        print(f"✅ SUCCESS! Invoice closed successfully")
        print(f"   New status: {closed_invoice.status}")
        
        return True
        
    except ValidationError as e:
        print(f"\n❌ ValidationError caught:")
        print(f"   Detail: {e.detail}")
        if hasattr(e, 'detail') and isinstance(e.detail, dict):
            for key, value in e.detail.items():
                print(f"   {key}: {value}")
        return False
        
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR:")
        print(f"   Type: {type(e).__name__}")
        print(f"   Message: {str(e)}")
        
        import traceback
        print(f"\n📋 Full traceback:")
        traceback.print_exc()
        
        return False


if __name__ == "__main__":
    # Test invoice 1
    test_close_invoice(1)

