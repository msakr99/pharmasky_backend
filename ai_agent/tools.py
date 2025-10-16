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
Offer = apps.get_model('offers', 'Offer')


# Define tools for OpenAI function calling
AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "التحقق من توفر دواء أو منتج في عروض ماكس. يبحث بالاسم العربي أو الإنجليزي ويعرض السعر الأصلي وسعر العرض والخصم والكمية المتاحة.",
            "parameters": {
                "type": "object",
                "properties": {
                    "medicine_name": {
                        "type": "string",
                        "description": "اسم الدواء أو المنتج المطلوب البحث عنه في عروض ماكس"
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
            "description": "إنشاء طلب شراء جديد من عروض ماكس. يجب التأكد من توفر المنتج في العروض أولاً. يتم خصم الكمية تلقائياً من المتاح ويعرض المبلغ الموفَّر.",
            "parameters": {
                "type": "object",
                "properties": {
                    "medicine_name": {
                        "type": "string",
                        "description": "اسم الدواء أو المنتج من عروض ماكس"
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
    Check if a medicine/product is available in Max offers
    """
    try:
        # Search in Max offers (is_max=True) with remaining amount > 0
        offers = Offer.objects.filter(
            Q(product__name__icontains=medicine_name) | 
            Q(product__e_name__icontains=medicine_name),
            is_max=True,
            remaining_amount__gt=0
        ).select_related('product', 'product__company', 'product_code')[:5]
        
        if not offers.exists():
            return {
                "available": False,
                "message": f"للأسف '{medicine_name}' مش موجود في عروض ماكس حاليًا",
                "offers": []
            }
        
        offers_data = []
        for offer in offers:
            offers_data.append({
                "id": offer.id,
                "product_id": offer.product.id,
                "name": offer.product.name,
                "english_name": offer.product.e_name,
                "original_price": float(offer.product.public_price),
                "offer_price": float(offer.selling_price),
                "discount_percentage": float(offer.selling_discount_percentage),
                "remaining_amount": offer.remaining_amount,
                "company": offer.product.company.name if offer.product.company else "",
                "shape": offer.product.shape,
                "effective_material": offer.product.effective_material,
                "product_code": str(offer.product_code) if offer.product_code else "",
                "expiry_date": offer.product_expiry_date.strftime("%Y-%m-%d") if offer.product_expiry_date else None
            })
        
        return {
            "available": True,
            "message": f"تم العثور على {len(offers_data)} عرض من ماكس",
            "offers": offers_data
        }
    
    except Exception as e:
        return {
            "available": False,
            "message": f"حدث خطأ أثناء البحث: {str(e)}",
            "offers": []
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
    Create a sale order for a medicine from Max offers
    Note: This is a simplified version. In production, you'd need more details.
    """
    try:
        # Find the offer
        offer = Offer.objects.filter(
            Q(product__name__icontains=medicine_name) | 
            Q(product__e_name__icontains=medicine_name),
            is_max=True,
            remaining_amount__gt=0
        ).select_related('product').first()
        
        if not offer:
            return {
                "success": False,
                "message": f"لم نجد '{medicine_name}' في عروض ماكس لإنشاء الطلب",
                "order_id": None
            }
        
        # Check if requested quantity is available
        if quantity > offer.remaining_amount:
            return {
                "success": False,
                "message": f"الكمية المتاحة فقط {offer.remaining_amount} من {offer.product.name}",
                "order_id": None
            }
        
        # Calculate total
        total_price = offer.selling_price * quantity
        
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
            product=offer.product,
            quantity=quantity,
            unit_price=offer.selling_price,
            total_price=total_price,
            status='PLACED'
        )
        
        # Update remaining amount in offer
        offer.remaining_amount -= quantity
        offer.save()
        
        discount_saved = (offer.product.public_price - offer.selling_price) * quantity
        
        return {
            "success": True,
            "message": f"تم إنشاء الطلب بنجاح من عروض ماكس! رقم الطلب: {invoice.id}",
            "order_id": invoice.id,
            "product": offer.product.name,
            "quantity": quantity,
            "unit_price": float(offer.selling_price),
            "total_price": float(total_price),
            "discount_percentage": float(offer.selling_discount_percentage),
            "amount_saved": float(discount_saved)
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

