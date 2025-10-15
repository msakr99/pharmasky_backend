"""
AI Agent tools/functions that connect to the Django models
"""
from django.apps import apps
from django.db.models import Q
import json

# Get models
Product = apps.get_model('market', 'Product')
SaleInvoice = apps.get_model('invoices', 'SaleInvoice')
SaleInvoiceItem = apps.get_model('invoices', 'SaleInvoiceItem')


# Define tools for OpenAI function calling
AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "التحقق من توفر دواء أو منتج في المخزون. يبحث بالاسم العربي أو الإنجليزي.",
            "parameters": {
                "type": "object",
                "properties": {
                    "medicine_name": {
                        "type": "string",
                        "description": "اسم الدواء أو المنتج المطلوب البحث عنه"
                    }
                },
                "required": ["medicine_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "suggest_alternative",
            "description": "اقتراح بدائل لدواء معين. يعرض أدوية بديلة بنفس المادة الفعالة أو مشابهة.",
            "parameters": {
                "type": "object",
                "properties": {
                    "medicine_name": {
                        "type": "string",
                        "description": "اسم الدواء المطلوب إيجاد بديل له"
                    }
                },
                "required": ["medicine_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_order",
            "description": "إنشاء طلب شراء جديد لدواء أو منتج. يجب التأكد من توفر المنتج أولاً.",
            "parameters": {
                "type": "object",
                "properties": {
                    "medicine_name": {
                        "type": "string",
                        "description": "اسم الدواء أو المنتج"
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "الكمية المطلوبة",
                        "minimum": 1
                    }
                },
                "required": ["medicine_name", "quantity"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "track_order",
            "description": "تتبع حالة طلب موجود باستخدام رقم الطلب.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "integer",
                        "description": "رقم الطلب المراد تتبعه"
                    }
                },
                "required": ["order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_order",
            "description": "إلغاء طلب موجود. يمكن إلغاء الطلبات التي لم يتم شحنها بعد.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "integer",
                        "description": "رقم الطلب المراد إلغاؤه"
                    }
                },
                "required": ["order_id"]
            }
        }
    }
]


# Tool implementation functions
def check_availability(medicine_name: str) -> dict:
    """
    Check if a medicine/product is available in the database
    """
    try:
        # Search in both Arabic and English names
        products = Product.objects.filter(
            Q(name__icontains=medicine_name) | 
            Q(e_name__icontains=medicine_name)
        )[:5]  # Limit to 5 results
        
        if not products.exists():
            return {
                "available": False,
                "message": f"للأسف '{medicine_name}' مش موجود في المخزون حاليًا",
                "products": []
            }
        
        products_data = []
        for product in products:
            products_data.append({
                "id": product.id,
                "name": product.name,
                "english_name": product.e_name,
                "price": float(product.public_price),
                "company": product.company.name if product.company else "",
                "shape": product.shape,
                "effective_material": product.effective_material
            })
        
        return {
            "available": True,
            "message": f"تم العثور على {len(products_data)} منتج",
            "products": products_data
        }
    
    except Exception as e:
        return {
            "available": False,
            "message": f"حدث خطأ أثناء البحث: {str(e)}",
            "products": []
        }


def suggest_alternative(medicine_name: str) -> dict:
    """
    Suggest alternative medicines based on effective material
    """
    try:
        # First, find the original product
        original_product = Product.objects.filter(
            Q(name__icontains=medicine_name) | 
            Q(e_name__icontains=medicine_name)
        ).first()
        
        if not original_product:
            return {
                "found": False,
                "message": f"لم نجد '{medicine_name}' للبحث عن بدائل له",
                "alternatives": []
            }
        
        # Get alternatives from the database
        # First check if there are predefined alternatives
        alternatives = list(original_product.alternatives.all()[:3])
        
        # If no predefined alternatives, search by effective material
        if not alternatives:
            alternatives = Product.objects.filter(
                effective_material=original_product.effective_material
            ).exclude(id=original_product.id)[:3]
        
        alternatives_data = []
        for alt in alternatives:
            alternatives_data.append({
                "id": alt.id,
                "name": alt.name,
                "english_name": alt.e_name,
                "price": float(alt.public_price),
                "company": alt.company.name if alt.company else "",
                "effective_material": alt.effective_material
            })
        
        return {
            "found": True,
            "original_product": original_product.name,
            "message": f"وجدنا {len(alternatives_data)} بديل لـ {original_product.name}",
            "alternatives": alternatives_data
        }
    
    except Exception as e:
        return {
            "found": False,
            "message": f"حدث خطأ: {str(e)}",
            "alternatives": []
        }


def create_order(medicine_name: str, quantity: int, user) -> dict:
    """
    Create a sale order for a medicine
    Note: This is a simplified version. In production, you'd need more details.
    """
    try:
        # Find the product
        product = Product.objects.filter(
            Q(name__icontains=medicine_name) | 
            Q(e_name__icontains=medicine_name)
        ).first()
        
        if not product:
            return {
                "success": False,
                "message": f"لم نجد '{medicine_name}' لإنشاء الطلب",
                "order_id": None
            }
        
        # Calculate total
        total_price = product.public_price * quantity
        
        # Create sale invoice (simplified - in production you'd use the proper serializer)
        invoice = SaleInvoice.objects.create(
            user=user,
            items_count=1,
            total_quantity=quantity,
            total_price=total_price,
            status='PLACED'
        )
        
        # Create invoice item
        SaleInvoiceItem.objects.create(
            invoice=invoice,
            product=product,
            quantity=quantity,
            unit_price=product.public_price,
            total_price=total_price,
            status='PLACED'
        )
        
        return {
            "success": True,
            "message": f"تم إنشاء الطلب بنجاح! رقم الطلب: {invoice.id}",
            "order_id": invoice.id,
            "product": product.name,
            "quantity": quantity,
            "total_price": float(total_price)
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"حدث خطأ أثناء إنشاء الطلب: {str(e)}",
            "order_id": None
        }


def track_order(order_id: int, user) -> dict:
    """
    Track an existing order
    """
    try:
        invoice = SaleInvoice.objects.filter(id=order_id, user=user).first()
        
        if not invoice:
            return {
                "found": False,
                "message": f"لم نجد طلب برقم {order_id}",
                "order": None
            }
        
        # Get invoice items
        items = []
        for item in invoice.items.all():
            items.append({
                "product": item.product.name,
                "quantity": item.quantity,
                "price": float(item.total_price),
                "status": item.status
            })
        
        return {
            "found": True,
            "message": f"تفاصيل الطلب رقم {order_id}",
            "order": {
                "order_id": invoice.id,
                "status": invoice.status,
                "total_price": float(invoice.total_price),
                "items_count": invoice.items_count,
                "created_at": invoice.created_at.strftime("%Y-%m-%d %H:%M"),
                "items": items
            }
        }
    
    except Exception as e:
        return {
            "found": False,
            "message": f"حدث خطأ: {str(e)}",
            "order": None
        }


def cancel_order(order_id: int, user) -> dict:
    """
    Cancel an existing order
    """
    try:
        invoice = SaleInvoice.objects.filter(id=order_id, user=user).first()
        
        if not invoice:
            return {
                "success": False,
                "message": f"لم نجد طلب برقم {order_id}"
            }
        
        # Check if order can be cancelled (only if PLACED or CONFIRMED)
        if invoice.status not in ['PLACED', 'CONFIRMED']:
            return {
                "success": False,
                "message": f"لا يمكن إلغاء الطلب في حالته الحالية ({invoice.status})"
            }
        
        # Cancel the order
        invoice.status = 'CANCELLED'
        invoice.save()
        
        # Cancel all items
        invoice.items.all().update(status='CANCELLED')
        
        return {
            "success": True,
            "message": f"تم إلغاء الطلب رقم {order_id} بنجاح"
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"حدث خطأ: {str(e)}"
        }


# Function router
def execute_tool(function_name: str, arguments: dict, user=None) -> str:
    """
    Execute a tool function and return the result as JSON string
    """
    try:
        if function_name == "check_availability":
            result = check_availability(arguments.get("medicine_name"))
        elif function_name == "suggest_alternative":
            result = suggest_alternative(arguments.get("medicine_name"))
        elif function_name == "create_order":
            result = create_order(
                arguments.get("medicine_name"),
                arguments.get("quantity"),
                user
            )
        elif function_name == "track_order":
            result = track_order(arguments.get("order_id"), user)
        elif function_name == "cancel_order":
            result = cancel_order(arguments.get("order_id"), user)
        else:
            result = {"error": f"Unknown function: {function_name}"}
        
        return json.dumps(result, ensure_ascii=False)
    
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

