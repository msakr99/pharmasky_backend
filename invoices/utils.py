from copy import deepcopy
from decimal import Decimal
from django.apps import apps
from django.db.models import Sum
from numpy import insert
from finance.utils import create_transaction, delete_trasaction, get_transaction, update_transaction
from inventory.utils import (
    create_inventory_from_invoice_item,
    create_inventory_item,
    deduct_product_amount,
    delete_inventory_item,
    get_or_create_main_inventory,
)
from invoices.choices import (
    PurchaseInvoiceItemStatusChoice,
    PurchaseInvoiceStatusChoice,
    PurchaseReturnInvoiceStatusChoice,
    SaleInvoiceItemStatusChoice,
    SaleInvoiceStatusChoice,
    SaleReturnInvoiceStatusChoice,
)
from rest_framework.exceptions import ValidationError

from offers.utils import affect_offer, delete_offer

get_model = apps.get_model


def affect_invoice(invoice, operation, invoice_item, old_price=None, old_quantity=None):
    if operation == "add":
        invoice.total_price += invoice_item.sub_total
        invoice.items_count += 1
        invoice.total_quantity += invoice_item.quantity

    elif operation == "update":
        if old_price is not None:
            invoice.total_price += invoice_item.sub_total - old_price
        if old_quantity is not None:
            invoice.total_quantity += invoice_item.quantity - old_quantity

    elif operation == "remove":
        invoice.total_price -= invoice_item.sub_total
        invoice.items_count -= 1
        invoice.total_quantity -= invoice_item.quantity

    invoice.save()

    return invoice


# PURCHASE INVOICES
def get_purchase_invoice(user):
    PurchaseInvoice = get_model("invoices", "PurchaseInvoice")
    return PurchaseInvoice.objects.filter(user=user, status=PurchaseInvoiceStatusChoice.PLACED).first()


def create_purchase_invoice(data):
    items = data.pop("items", [])
    PurchaseInvoice = get_model("invoices", "PurchaseInvoice")
    invoice = PurchaseInvoice.objects.create(**data)

    for item in items:
        item["invoice"] = invoice
        create_purchase_invoice_item(item, update_invoice=False)

    return invoice


def lock_purchase_invoice(invoice):
    invoice.status = PurchaseInvoiceStatusChoice.LOCKED
    invoice.save()
    return invoice


def unlock_purchase_invoice(invoice):
    prev_status = invoice.status

    if prev_status == PurchaseInvoiceStatusChoice.CLOSED:
        transaction = get_transaction(invoice)

        if transaction is not None:
            delete_trasaction(transaction)

    invoice.status = PurchaseInvoiceStatusChoice.PLACED
    invoice.save()
    return invoice


def close_purchase_invoice(invoice, supplier_invoice_number, update_account=True):
    pending_action_items = invoice.items.exclude(status=PurchaseInvoiceItemStatusChoice.RECEIVED)

    if pending_action_items.exists():
        raise ValidationError({"detail": "Cannot close invoice with pending action items."})

    invoice.status = PurchaseInvoiceStatusChoice.CLOSED
    invoice.supplier_invoice_number = supplier_invoice_number
    invoice.save()

    if update_account:
        create_transaction(invoice.transaction_data)

    return invoice


def open_purchase_invoice(invoice, update_account=True):
    invoice.status = PurchaseInvoiceStatusChoice.LOCKED
    invoice.save()

    if update_account:
        transaction = get_transaction(invoice)

        if transaction is not None:
            delete_trasaction(transaction)

    return invoice


# PURCHASE INVOICE ITEMS
def create_purchase_invoice_item(data, update_invoice=True, update_offer=True):
    PurchaseInvoiceItem = get_model("invoices", "PurchaseInvoiceItem")
    instance = PurchaseInvoiceItem.objects.create(**data)

    if update_invoice:
        affect_invoice(instance.invoice, "add", instance)

    if update_offer:
        affect_offer("add", instance)

    return instance


def update_purchase_invoice_item_state(
    instance, status, update_sale_invoice_item=True, remove_offer=True, update_inventory=True
):
    old_status = instance.status
    instance.status = status
    instance.save()

    if update_sale_invoice_item:
        sale_invoice_item = instance.sale_invoice_item

        if sale_invoice_item is not None:
            if status == PurchaseInvoiceItemStatusChoice.PLACED:
                update_sale_invoice_item_state(instance.sale_invoice_item, SaleInvoiceItemStatusChoice.PLACED)
            elif status == PurchaseInvoiceItemStatusChoice.ACCEPTED:
                update_sale_invoice_item_state(instance.sale_invoice_item, SaleInvoiceItemStatusChoice.ACCEPTED)
            elif status == PurchaseInvoiceItemStatusChoice.REJECTED:
                update_sale_invoice_item_state(instance.sale_invoice_item, SaleInvoiceItemStatusChoice.REJECTED)
            elif status == PurchaseInvoiceItemStatusChoice.RECEIVED:
                update_sale_invoice_item_state(instance.sale_invoice_item, SaleInvoiceItemStatusChoice.RECEIVED)
            elif status == PurchaseInvoiceItemStatusChoice.NOT_RECEIVED:
                update_sale_invoice_item_state(instance.sale_invoice_item, SaleInvoiceItemStatusChoice.NOT_RECEIVED)

    if status == PurchaseInvoiceItemStatusChoice.REJECTED and remove_offer:
        offer = instance.offer

        if offer is not None:
            delete_offer(offer)

    if update_inventory:
        inventory_item = getattr(instance, "inventory_item", None)
        if status == PurchaseInvoiceItemStatusChoice.RECEIVED and inventory_item is None:
            create_inventory_from_invoice_item(instance)
        elif (
            old_status == PurchaseInvoiceItemStatusChoice.RECEIVED
            and status != old_status
            and inventory_item is not None
        ):
            delete_inventory_item(inventory_item)

    return instance


def get_allowed_status_changes(status):
    f_allowed_statuses = []
    b_allowed_statuses = []

    if status == PurchaseInvoiceItemStatusChoice.PLACED:
        f_allowed_statuses = [
            PurchaseInvoiceItemStatusChoice.ACCEPTED,
            PurchaseInvoiceItemStatusChoice.REJECTED,
            PurchaseInvoiceItemStatusChoice.RECEIVED,
            PurchaseInvoiceItemStatusChoice.NOT_RECEIVED,
        ]
    elif status in [PurchaseInvoiceItemStatusChoice.ACCEPTED, PurchaseInvoiceItemStatusChoice.REJECTED]:
        f_allowed_statuses = [
            PurchaseInvoiceItemStatusChoice.RECEIVED,
            PurchaseInvoiceItemStatusChoice.NOT_RECEIVED,
        ]
        b_allowed_statuses = [PurchaseInvoiceItemStatusChoice.PLACED]
    elif status in [
        PurchaseInvoiceItemStatusChoice.RECEIVED,
        PurchaseInvoiceItemStatusChoice.NOT_RECEIVED,
    ]:
        b_allowed_statuses = [PurchaseInvoiceItemStatusChoice.ACCEPTED, PurchaseInvoiceItemStatusChoice.REJECTED]

    return f_allowed_statuses, b_allowed_statuses


def update_purchase_invoice_item(item, data, update_invoice=True, track_quantity_reduction=True):
    product = item.product

    data.pop("invoice", None)
    data.pop("product", None)
    data.pop("offer", None)
    data.pop("status", None)
    data.pop("purchase_price", None)
    data.pop("selling_price", None)
    data.pop("sub_total", None)

    purchase_discount_percentage = data.get("purchase_discount_percentage", None)
    selling_discount_percentage = data.get("selling_discount_percentage", None)
    quantity = data.get("quantity", None)

    old_quantity = None
    old_sub_total = None
    update_sub_total = False

    if selling_discount_percentage is not None:
        selling_price = Decimal(
            product.public_price - (product.public_price * selling_discount_percentage / 100)
        ).quantize(Decimal("0.00"))
        data["selling_price"] = selling_price

    if purchase_discount_percentage is not None:
        purchase_price = Decimal(
            product.public_price - (product.public_price * purchase_discount_percentage / 100)
        ).quantize(Decimal("0.00"))
        data["purchase_price"] = purchase_price
        update_sub_total = True

    if quantity is not None:
        old_quantity = item.quantity
        update_sub_total = True

    for key, value in data.items():
        setattr(item, key, value)

    if update_sub_total:
        old_sub_total = item.sub_total
        sub_total = Decimal(item.selling_price * item.quantity).quantize(Decimal("0.00"))
        item.sub_total = sub_total

    # Track quantity reduction in deleted_items
    if track_quantity_reduction and old_quantity is not None and old_quantity > item.quantity:
        reduced_quantity = old_quantity - item.quantity
        PurchaseInvoiceDeletedItem = get_model("invoices", "PurchaseInvoiceDeletedItem")
        PurchaseInvoiceDeletedItem.objects.create_for_quantity_reduction(item, reduced_quantity)

    item.save()

    if update_invoice and update_sub_total:
        affect_invoice(item.invoice, "update", item, old_sub_total, old_quantity)


def return_purchase_invoice_item(item, quantity):
    if item.remaining_quantity < quantity:
        raise ValidationError({"detail": "Returned quantity exceeds the remaining quantity."})

    item.remaining_quantity -= quantity
    item.save()
    return item


def delete_purchase_invoice_item(item, update_invoice=True):
    if update_invoice:
        affect_invoice(item.invoice, "remove", item)

    PurchaseInvoiceDeletedItem = get_model("invoices", "PurchaseInvoiceDeletedItem")
    deleted_instance = PurchaseInvoiceDeletedItem.objects.create_for_item(item)

    item.delete()

    return deleted_instance


# PURCHASE RETURN INVOICES
def create_purchase_return_invoice(data):
    items = data.pop("items", [])
    PurchaseReturnInvoice = get_model("invoices", "PurchaseReturnInvoice")
    invoice = PurchaseReturnInvoice.objects.create(**data)

    for item in items:
        item["invoice"] = invoice
        create_purchase_return_invoice_item(item, update_invoice=False)

    return invoice


def close_purchase_return_invoice(invoice, update_account=True, update_inventory=True):
    invoice.status = PurchaseReturnInvoiceStatusChoice.CLOSED
    invoice.save()

    if update_account:
        create_transaction(invoice.transaction_data)

    if update_inventory:
        inventory = get_or_create_main_inventory()

        for item in invoice.items.select_related("purchase_invoice_item__product").all():
            deduct_product_amount(item.purchase_invoice_item.product, item.quantity, inventory)

    return invoice


# PURCHASE RETURN INVOICE ITEMS
def create_purchase_return_invoice_item(data, update_invoice=True, update_item=True):
    PurchaseReturnInvoiceItem = get_model("invoices", "PurchaseReturnInvoiceItem")
    instance = PurchaseReturnInvoiceItem.objects.create(**data)

    if update_invoice:
        affect_invoice(instance.invoice, "add", instance)

    if update_item:
        return_purchase_invoice_item(instance.purchase_invoice_item, instance.quantity)

    return instance


def update_purchase_return_invoice_item(item, data, update_invoice=True, update_item=True):
    data.pop("invoice", None)
    data.pop("purchase_invoice_item", None)
    data.pop("sub_total", None)

    quantity = data.get("quantity", None)
    old_quantity = None
    old_sub_total = None

    if quantity is not None:
        old_quantity = item.quantity
        old_sub_total = item.sub_total
        data["sub_total"] = Decimal(item.purchase_invoice_item.purchase_price * quantity).quantize(Decimal("0.00"))

    for key, value in data.items():
        setattr(item, key, value)

    item.save()

    if update_invoice and (old_sub_total is not None or old_quantity is not None):
        affect_invoice(item.invoice, "update", item, old_sub_total, old_quantity)

    if update_item and old_quantity is not None:
        item.purchase_invoice_item.remaining_quantity += old_quantity - quantity
        item.purchase_invoice_item.save()

    return item


def delete_purchase_return_invoice_item(item, update_invoice=True, update_item=True):
    if update_invoice:
        affect_invoice(item.invoice, "remove", item)

    if update_item:
        item.purchase_invoice_item.remaining_quantity += item.quantity
        item.purchase_invoice_item.save()

    item.delete()


# SALE INVOICES
def create_sale_invoice(data):
    items = data.pop("items", [])
    SaleInvoice = get_model("invoices", "SaleInvoice")
    invoice = SaleInvoice.objects.create(**data)

    invoice.user.profile.latest_invoice_date = invoice.created_at
    invoice.user.profile.save()

    for item in items:
        item["invoice"] = invoice
        create_sale_invoice_item(item, update_invoice=False)

    return invoice


def close_sale_invoice(invoice, update_account=True, update_inventory=True):
    # Import here to avoid circular imports
    from inventory.models import InventoryItem
    
    pending_action_items = invoice.items.select_related('product').exclude(
        status=SaleInvoiceItemStatusChoice.RECEIVED
    )

    if pending_action_items.exists():
        # Convert to list to avoid QuerySet re-evaluation
        pending_items_list = list(pending_action_items)
        
        # Build list of pending items
        pending_items_data = []
        
        for item in pending_items_list:
            pending_items_data.append({
                "item_id": item.id,
                "product_name": item.product.name,
                "current_status": item.status,
                "required_status": "received"
            })
        
        raise ValidationError({
            "detail": "Cannot close invoice with pending action items.",
            "pending_items": pending_items_data
        })

    # Check inventory availability before closing
    if update_inventory:
        inventory = get_or_create_main_inventory()
        inventory_issues = []
        
        for item in invoice.items.select_related('product').all():
            available_quantity = InventoryItem.objects.filter(
                inventory=inventory,
                product=item.product
            ).aggregate(total=Sum('remaining_quantity'))['total'] or 0
            
            if available_quantity < item.quantity:
                shortage = item.quantity - available_quantity
                inventory_issues.append({
                    "product_id": item.product.id,
                    "product_name": item.product.name,
                    "required": item.quantity,
                    "available": available_quantity,
                    "shortage": shortage
                })
        
        if inventory_issues:
            raise ValidationError({
                "detail": "Insufficient inventory to close invoice.",
                "inventory_issues": inventory_issues,
                "can_close": False
            })

    old_status = invoice.status
    invoice.status = SaleInvoiceStatusChoice.CLOSED
    invoice.save()

    if update_account and old_status != invoice.status:
        create_transaction(invoice.transaction_data)

    if update_inventory and old_status != invoice.status:
        inventory = get_or_create_main_inventory()
        for item in invoice.items.all():
            deduct_product_amount(item.product, item.quantity, inventory)

    return invoice


def open_sale_invoice(invoice, update_account=True):
    invoice.status = SaleInvoiceStatusChoice.PLACED
    invoice.save()

    if update_account:
        transaction = get_transaction(invoice)

        if transaction is not None:
            delete_trasaction(transaction)

    return invoice


# SALE INVOICE ITEMS
def create_sale_invoice_item(data, update_invoice=True, update_purchase_invoice=True):
    SaleInvoiceItem = get_model("invoices", "SaleInvoiceItem")
    instance = SaleInvoiceItem.objects.create(**data)

    if update_invoice:
        affect_invoice(instance.invoice, "add", instance)

    if update_purchase_invoice:
        offer = instance.offer
        user = offer.user
        purchase_invoice_item_data = deepcopy(data)

        purchase_invoice_item_data.pop("invoice", None)
        purchase_invoice_item_data["sale_invoice_item"] = instance

        purchase_price = offer.purchase_price
        sub_total = Decimal(purchase_price * instance.quantity).quantize(Decimal("0.00"))
        purchase_invoice_item_data["sub_total"] = sub_total
        purchase_invoice = get_purchase_invoice(user)

        if purchase_invoice is None:
            purchase_invoice_data = {
                "user": user,
                "items_count": 1,
                "total_quantity": instance.quantity,
                "total_price": sub_total,
                "items": [purchase_invoice_item_data],
            }
            purchase_invoice = create_purchase_invoice(purchase_invoice_data)

        else:
            purchase_invoice_item_data["invoice"] = purchase_invoice
            create_purchase_invoice_item(purchase_invoice_item_data)

    return instance


def update_sale_invoice_item(item, data, update_invoice=True, track_quantity_reduction=True):
    product = item.product

    data.pop("invoice", None)
    data.pop("product", None)
    data.pop("offer", None)
    data.pop("status", None)
    data.pop("purchase_price", None)
    data.pop("selling_price", None)
    data.pop("sub_total", None)

    purchase_discount_percentage = data.get("purchase_discount_percentage", None)
    selling_discount_percentage = data.get("selling_discount_percentage", None)
    quantity = data.get("quantity", None)

    old_quantity = None
    old_sub_total = None
    needs_update = False

    if purchase_discount_percentage is not None:
        purchase_price = Decimal(
            product.public_price - (product.public_price * purchase_discount_percentage / 100)
        ).quantize(Decimal("0.00"))
        data["purchase_price"] = purchase_price

    if selling_discount_percentage is not None:
        selling_price = Decimal(
            product.public_price - (product.public_price * selling_discount_percentage / 100)
        ).quantize(Decimal("0.00"))
        data["selling_price"] = selling_price
        needs_update = True

    if quantity is not None:
        old_quantity = item.quantity
        needs_update = True

    for key, value in data.items():
        setattr(item, key, value)

    if needs_update:
        old_sub_total = item.sub_total
        sub_total = Decimal(item.selling_price * item.quantity).quantize(Decimal("0.00"))
        item.sub_total = sub_total

    # Track quantity reduction in deleted_items
    if track_quantity_reduction and old_quantity is not None and old_quantity > item.quantity:
        reduced_quantity = old_quantity - item.quantity
        SaleInvoiceDeletedItem = get_model("invoices", "SaleInvoiceDeletedItem")
        SaleInvoiceDeletedItem.objects.create_for_quantity_reduction(item, reduced_quantity)

    item.save()

    if update_invoice and needs_update:
        affect_invoice(item.invoice, "update", item, old_sub_total, old_quantity)

    return item


def return_sale_invoice_item(item, quantity):
    if item.remaining_quantity < quantity:
        raise ValidationError({"detail": "Returned quantity exceeds the remaining quantity."})

    item.remaining_quantity -= quantity
    item.save()
    return item


def delete_sale_invoice_item(item, update_invoice=True):
    if update_invoice:
        affect_invoice(item.invoice, "remove", item)

    SaleInvoiceDeletedItem = get_model("invoices", "SaleInvoiceDeletedItem")
    deleted_instance = SaleInvoiceDeletedItem.objects.create_for_item(item)

    item.delete()

    return deleted_instance


def update_sale_invoice_item_state(instance, status):
    instance.status = status
    instance.save()
    return instance


# SALE RETURN INVOICES
def create_sale_return_invoice(data):
    items = data.pop("items", [])
    SaleReturnInvoice = get_model("invoices", "SaleReturnInvoice")
    invoice = SaleReturnInvoice.objects.create(**data)

    for item in items:
        item["invoice"] = invoice
        create_sale_return_invoice_item(item, update_invoice=False)

    return invoice


def close_sale_return_invoice(invoice, update_account=True, update_inventory=True):
    invoice.status = SaleReturnInvoiceStatusChoice.CLOSED
    invoice.save()

    if update_account:
        create_transaction(invoice.transaction_data)

    if update_inventory:
        inventory = get_or_create_main_inventory()

        for item in invoice.items.select_related("sale_invoice_item__product").all():
            si_item = item.sale_invoice_item
            data = {
                "inventory": inventory,
                "product": si_item.product,
                "purchase_invoice_item": None,
                "product_expiry_date": si_item.product_expiry_date,
                "operating_number": si_item.operating_number,
                "purchase_discount_percentage": si_item.purchase_discount_percentage,
                "purchase_price": si_item.purchase_price,
                "selling_discount_percentage": si_item.selling_discount_percentage,
                "selling_price": si_item.selling_price,
                "quantity": item.quantity,
                "remaining_quantity": item.quantity,
                "purchase_sub_total": Decimal(item.quantity * si_item.purchase_price).quantize(Decimal("0.00")),
                "selling_sub_total": Decimal(item.quantity * si_item.selling_price).quantize(Decimal("0.00")),
            }
            create_inventory_item(data)

    return invoice


# SALE RETURN INVOICE ITEMS
def create_sale_return_invoice_item(data, update_invoice=True, update_item=True):
    SaleReturnInvoiceItem = get_model("invoices", "SaleReturnInvoiceItem")
    item = SaleReturnInvoiceItem.objects.create(**data)

    if update_invoice:
        affect_invoice(item.invoice, "add", item)

    if update_item:
        return_sale_invoice_item(item.sale_invoice_item, item.quantity)

    return item


def update_sale_return_invoice_item(item, data, update_invoice=True, update_item=True):
    data.pop("invoice", None)
    data.pop("sale_invoice_item", None)
    data.pop("sub_total", None)

    quantity = data.get("quantity", None)
    old_quantity = None
    old_sub_total = None

    if quantity is not None:
        old_quantity = item.quantity
        old_sub_total = item.sub_total
        data["sub_total"] = Decimal(item.sale_invoice_item.selling_price * quantity).quantize(Decimal("0.00"))

    for key, value in data.items():
        setattr(item, key, value)

    item.save()

    if update_invoice and (old_sub_total is not None or old_quantity is not None):
        affect_invoice(item.invoice, "update", item, old_sub_total, old_quantity)

    if update_item and old_quantity is not None:
        item.sale_invoice_item.remaining_quantity += old_quantity - quantity
        item.sale_invoice_item.save()

    return item


def delete_sale_return_invoice_item(item, update_invoice=True, update_item=True):
    if update_invoice:
        affect_invoice(item.invoice, "remove", item)

    if update_item:
        item.sale_invoice_item.remaining_quantity += item.quantity
        item.sale_invoice_item.save()

    item.delete()
