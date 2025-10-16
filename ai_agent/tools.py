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
UserProfile = apps.get_model('profiles', 'UserProfile')
Complaint = apps.get_model('profiles', 'Complaint')
PharmacyProductWishList = apps.get_model('market', 'PharmacyProductWishList')


# Define tools for OpenAI function calling
AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "التحقق من توفر دواء أو منتج بأفضل عرض (أحسن خصم). يبحث بالاسم العربي أو الإنجليزي ويعرض السعر الأصلي ونسبة الخصم. المنصة تجمع عروض من مخازن متعددة وتعرض أفضل سعر.",
            "parameters": {
                "type": "object",
                "properties": {
                    "medicine_name": {
                        "type": "string",
                        "description": "اسم الدواء أو المنتج المطلوب البحث عنه في العروض المتاحة"
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
            "description": "إنشاء طلب شراء جديد بأفضل عرض متاح. يجب التأكد من توفر المنتج في العروض أولاً. يتم خصم الكمية تلقائياً من المتاح ويعرض المبلغ الموفَّر.",
            "parameters": {
                "type": "object",
                "properties": {
                    "medicine_name": {
                        "type": "string",
                        "description": "اسم الدواء أو المنتج من العروض المتاحة"
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
    },
    {
        "type": "function",
        "function": {
            "name": "submit_complaint",
            "description": "تقديم شكوى أو ملاحظة من العميل. استخدمها عندما يكون العميل غير راضي أو لديه مشكلة أو ملاحظة على الخدمة أو المنتجات أو التوصيل.",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                        "description": "عنوان الشكوى (مثال: مشكلة في التوصيل، منتج تالف، تأخير في الطلب)"
                    },
                    "body": {
                        "type": "string",
                        "description": "تفاصيل الشكوى الكاملة"
                    }
                },
                "required": ["subject", "body"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_wishlist",
            "description": "الحصول على قائمة المنتجات المفضلة للعميل (المنتجات اللي العميل مهتم بيها). استخدمها عشان تعرف إيه المنتجات اللي العميل بيدور عليها أو مهتم بيها وتقترح عليه العروض الخاصة عليها.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_to_wishlist",
            "description": "إضافة منتج لقائمة المفضلة للعميل. استخدمها لما العميل يسأل عن منتج مش موجود في العروض حالياً، عشان نخليه يتابعه ونبلغه لما يكون متوفر بعرض حلو.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "اسم المنتج اللي العميل عايزه"
                    }
                },
                "required": ["product_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_order_total",
            "description": "حساب إجمالي الطلبات اللي العميل عملها اليوم. استخدمها لما العميل يسأل 'وصلنا لكام؟' أو 'الفاتورة كام؟' - يعرض مجموع كل الأصناف والسعر الإجمالي.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


# Tool implementation functions
def check_availability(medicine_name: str, user=None) -> dict:
    """
    Check if a medicine/product is available in Max offers
    Returns: availability status, original price, and discount percentage
    Discount percentage = selling_discount_percentage - user.profile.payment_period.addition_percentage
    """
    try:
        # Search in Max offers (is_max=True) with remaining amount > 0
        offers = Offer.objects.filter(
            Q(product__name__icontains=medicine_name) | 
            Q(product__e_name__icontains=medicine_name),
            is_max=True,
            remaining_amount__gt=0
        ).select_related('product')[:5]
        
        if not offers.exists():
            return {
                "available": False,
                "message": f"للأسف '{medicine_name}' مش متوفر في العروض حالياً",
                "offers": []
            }
        
        # Get user's payment period addition percentage
        addition_percentage = 0
        if user and hasattr(user, 'profile'):
            try:
                profile = user.profile
                if profile and hasattr(profile, 'payment_period') and profile.payment_period:
                    addition_percentage = float(profile.payment_period.addition_percentage or 0)
            except Exception:
                # If user has no profile, use default 0
                addition_percentage = 0
        
        offers_data = []
        for offer in offers:
            # Calculate actual discount: selling_discount_percentage - addition_percentage
            actual_discount = float(offer.selling_discount_percentage) - addition_percentage
            
            offers_data.append({
                "name": offer.product.name,
                "available": True,
                "original_price": float(offer.product.public_price),
                "discount_percentage": round(actual_discount, 2)
            })
        
        return {
            "available": True,
            "message": f"تم العثور على {len(offers_data)} عرض متاح بأفضل الأسعار",
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
    Create a sale order for a medicine with best available offer
    Note: is_max=True indicates best offer from multiple warehouses
    """
    try:
        # Find the best offer (is_max=True)
        offer = Offer.objects.filter(
            Q(product__name__icontains=medicine_name) | 
            Q(product__e_name__icontains=medicine_name),
            is_max=True,
            remaining_amount__gt=0
        ).select_related('product').first()
        
        if not offer:
            return {
                "success": False,
                "message": f"لم نجد '{medicine_name}' في العروض المتاحة لإنشاء الطلب",
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
            "message": f"تم إنشاء الطلب بنجاح بأفضل سعر متاح! رقم الطلب: {invoice.id}",
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


def submit_complaint(subject: str, body: str, user) -> dict:
    """
    Submit a complaint from the user
    """
    try:
        if not user:
            return {
                "success": False,
                "message": "المستخدم غير موجود"
            }
        
        # Validate input
        if not subject or not subject.strip():
            return {
                "success": False,
                "message": "من فضلك اكتب عنوان للشكوى"
            }
        
        if not body or not body.strip():
            return {
                "success": False,
                "message": "من فضلك اكتب تفاصيل الشكوى"
            }
        
        # Create complaint
        complaint = Complaint.objects.create(
            user=user,
            subject=subject.strip()[:255],  # Limit to 255 chars
            body=body.strip()[:400]  # Limit to 400 chars as per model
        )
        
        return {
            "success": True,
            "message": "تم تسجيل شكواك بنجاح! هنتابع الموضوع ونتواصل معاك في أقرب وقت. شكراً لتواصلك معانا.",
            "complaint_id": complaint.id,
            "subject": complaint.subject,
            "created_at": complaint.created_at.strftime("%Y-%m-%d %H:%M")
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"حدث خطأ أثناء تسجيل الشكوى: {str(e)}"
        }


def get_wishlist(user) -> dict:
    """
    Get user's wishlist products (products the user is interested in)
    """
    try:
        if not user:
            return {
                "success": False,
                "message": "المستخدم غير موجود",
                "wishlist": []
            }
        
        # Get wishlist items for the user
        wishlist_items = PharmacyProductWishList.objects.filter(
            pharmacy=user
        ).select_related('product', 'product__company')[:20]  # Limit to 20 items
        
        if not wishlist_items.exists():
            return {
                "success": True,
                "message": "مفيش منتجات في قائمة المفضلة حالياً",
                "wishlist": [],
                "count": 0
            }
        
        # Build wishlist data
        wishlist_data = []
        for item in wishlist_items:
            product = item.product
            
            # Check if product is available with best offer (is_max=True)
            in_max_offer = Offer.objects.filter(
                product=product,
                is_max=True,  # Best offer from multiple warehouses
                remaining_amount__gt=0
            ).exists()
            
            wishlist_data.append({
                "product_id": product.id,
                "name": product.name,
                "english_name": product.e_name,
                "price": float(product.public_price),
                "company": product.company.name if product.company else "",
                "effective_material": product.effective_material,
                "shape": product.shape,
                "in_max_offer": in_max_offer,
                "added_at": item.created_at.strftime("%Y-%m-%d")
            })
        
        return {
            "success": True,
            "message": f"لقيت {len(wishlist_data)} منتج في قائمة المفضلة",
            "wishlist": wishlist_data,
            "count": len(wishlist_data)
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"حدث خطأ: {str(e)}",
            "wishlist": []
        }


def add_to_wishlist(product_name: str, user) -> dict:
    """
    Add a product to user's wishlist
    Use when customer asks about a product that is not available in Max offers
    """
    try:
        if not user:
            return {
                "success": False,
                "message": "المستخدم غير موجود"
            }
        
        if not product_name or not product_name.strip():
            return {
                "success": False,
                "message": "من فضلك اكتب اسم المنتج"
            }
        
        # Search for the product
        product = Product.objects.filter(
            Q(name__icontains=product_name) | 
            Q(e_name__icontains=product_name)
        ).first()
        
        if not product:
            return {
                "success": False,
                "message": f"للأسف مش لاقي المنتج '{product_name}' في قاعدة البيانات",
                "suggestion": "ممكن تتأكد من اسم المنتج أو تكتبه بطريقة تانية؟"
            }
        
        # Check if already in wishlist
        already_exists = PharmacyProductWishList.objects.filter(
            pharmacy=user,
            product=product
        ).exists()
        
        if already_exists:
            return {
                "success": True,
                "message": f"المنتج '{product.name}' موجود أصلاً في قائمتك المفضلة!",
                "product": {
                    "name": product.name,
                    "price": float(product.public_price),
                    "company": product.company.name if product.company else ""
                },
                "already_added": True
            }
        
        # Add to wishlist
        PharmacyProductWishList.objects.create(
            pharmacy=user,
            product=product
        )
        
        return {
            "success": True,
            "message": f"تمام! ضفت '{product.name}' لقائمتك المفضلة. هبلغك لما يكون متوفر بعرض حلو! 🔔",
            "product": {
                "id": product.id,
                "name": product.name,
                "english_name": product.e_name,
                "price": float(product.public_price),
                "company": product.company.name if product.company else "",
                "effective_material": product.effective_material
            },
            "already_added": False
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"حدث خطأ أثناء إضافة المنتج: {str(e)}"
        }


def get_order_total(user) -> dict:
    """
    Calculate total of today's orders (when customer asks "وصلنا لكام؟")
    Shows all items ordered today and the grand total
    """
    try:
        if not user:
            return {
                "success": False,
                "message": "المستخدم غير موجود"
            }
        
        # Get today's orders
        from django.utils import timezone
        from datetime import timedelta
        
        # Get orders from last 24 hours
        time_threshold = timezone.now() - timedelta(hours=24)
        
        invoices = SaleInvoice.objects.filter(
            user=user,
            created_at__gte=time_threshold,
            status__in=['PLACED', 'CONFIRMED']  # فقط الطلبات النشطة
        ).prefetch_related('items', 'items__product')
        
        if not invoices.exists():
            return {
                "success": True,
                "message": "مفيش طلبات جديدة اليوم",
                "total": 0,
                "items_count": 0,
                "orders": []
            }
        
        # Calculate totals
        grand_total = 0
        total_items = 0
        orders_summary = []
        all_items = []
        
        for invoice in invoices:
            grand_total += float(invoice.total_price)
            total_items += invoice.items_count
            
            # Get items details
            items_list = []
            for item in invoice.items.all():
                items_list.append({
                    "product": item.product.name,
                    "quantity": item.quantity,
                    "unit_price": float(item.unit_price),
                    "total": float(item.total_price)
                })
                all_items.append(f"{item.product.name} × {item.quantity}")
            
            orders_summary.append({
                "order_id": invoice.id,
                "items": items_list,
                "total": float(invoice.total_price),
                "status": invoice.status
            })
        
        return {
            "success": True,
            "message": f"إجمالي طلباتك اليوم: {grand_total} جنيه",
            "grand_total": grand_total,
            "total_items": total_items,
            "orders_count": len(orders_summary),
            "orders": orders_summary,
            "summary": all_items  # قائمة مبسطة بكل الأصناف
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
            medicine_name = arguments.get("medicine_name", "")
            result = check_availability(medicine_name, user)
        elif function_name == "suggest_alternative":
            medicine_name = arguments.get("medicine_name", "")
            result = suggest_alternative(medicine_name)
        elif function_name == "create_order":
            medicine_name = arguments.get("medicine_name", "")
            quantity = arguments.get("quantity", 0)
            result = create_order(medicine_name, quantity, user)
        elif function_name == "track_order":
            order_id = arguments.get("order_id", 0)
            result = track_order(order_id, user)
        elif function_name == "cancel_order":
            order_id = arguments.get("order_id", 0)
            result = cancel_order(order_id, user)
        elif function_name == "submit_complaint":
            subject = arguments.get("subject", "")
            body = arguments.get("body", "")
            result = submit_complaint(subject, body, user)
        elif function_name == "get_wishlist":
            result = get_wishlist(user)
        elif function_name == "add_to_wishlist":
            product_name = arguments.get("product_name", "")
            result = add_to_wishlist(product_name, user)
        elif function_name == "get_order_total":
            result = get_order_total(user)
        else:
            result = {"error": f"Unknown function: {function_name}"}
        
        return json.dumps(result, ensure_ascii=False)
    
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

