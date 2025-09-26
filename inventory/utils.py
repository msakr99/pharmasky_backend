from decimal import Decimal
from django.apps import apps
from rest_framework.exceptions import ValidationError

from inventory.choices import InventoryTypeChoice

get_model = apps.get_model


# Inventory
def get_or_create_main_inventory(raise_exception=False):
    Inventory = get_model("inventory", "Inventory")
    inventory = Inventory.objects.filter(type=InventoryTypeChoice.MAIN).first()

    if inventory is None and not raise_exception:
        default_name = "Auto created Main Inventory"
        inventory = Inventory.objects.create(
            name=default_name,
            type=InventoryTypeChoice.MAIN,
            total_items=0,
            total_quantity=0,
            total_purchase_price=Decimal("0.00"),
            total_selling_price=Decimal("0.00"),
        )
    elif inventory is None and raise_exception:
        raise ValidationError({"detail": "Main inventory not found."})

    return inventory


def affect_inventory(inventory, operation, item, old_quantity=None, old_purchase_price=None, old_selling_price=None):
    if operation == "add":
        inventory.total_items += 1
        inventory.total_quantity += item.remaining_quantity
        inventory.total_purchase_price += item.purchase_sub_total
        inventory.total_selling_price += item.selling_sub_total

    elif operation == "update":
        if old_purchase_price is not None:
            inventory.total_purchase_price += item.purchase_sub_total - old_purchase_price
        if old_selling_price is not None:
            inventory.total_selling_price += item.selling_sub_total - old_selling_price
        if old_quantity is not None:
            inventory.total_quantity += item.remaining_quantity - old_quantity

    elif operation == "remove":
        inventory.total_items -= 1
        inventory.total_quantity -= item.remaining_quantity
        inventory.total_purchase_price -= item.purchase_sub_total
        inventory.total_selling_price -= item.selling_sub_total

    inventory.save()
    return inventory


def deduct_product_amount(product, quantity, inventory=None):
    if inventory is None:
        inventory = get_or_create_main_inventory()

    items = inventory.items.filter(product=product).order_by("-selling_discount_percentage")
    total_available_quantity = sum(item.remaining_quantity for item in items)

    if total_available_quantity < quantity:
        raise ValidationError({"detail": f"Not enough quantity available for product {product}."})

    remaining_duction_quantity = quantity
    item_index = 0

    while remaining_duction_quantity > 0:
        item = items[item_index]

        if item.remaining_quantity >= remaining_duction_quantity:
            if item.remaining_quantity == remaining_duction_quantity:
                affect_inventory(item.inventory, "remove", item)
                item.delete()

            else:
                old_quantity = item.remaining_quantity
                old_purchase_price = item.purchase_sub_total
                old_selling_price = item.selling_sub_total

                item.remaining_quantity -= remaining_duction_quantity
                item.purchase_sub_total -= Decimal(remaining_duction_quantity * item.purchase_price).quantize(
                    Decimal("0.00")
                )
                item.selling_sub_total -= Decimal(remaining_duction_quantity * item.selling_price).quantize(
                    Decimal("0.00")
                )
                item.save()
                affect_inventory(
                    item.inventory,
                    "update",
                    item,
                    old_quantity=old_quantity,
                    old_purchase_price=old_purchase_price,
                    old_selling_price=old_selling_price,
                )

            remaining_duction_quantity = 0

        else:
            remaining_duction_quantity -= item.remaining_quantity
            affect_inventory(item.inventory, "remove", item)
            item.delete()

        item_index += 1


# Inventory Item
def create_inventory_item(data, raise_exception=False, update_inventory=True):
    InventoryItem = get_model("inventory", "InventoryItem")

    inventory = data.get("inventory", None)
    if inventory is None:
        inventory = get_or_create_main_inventory(raise_exception=raise_exception)

    data["inventory"] = inventory

    inventory_item = InventoryItem.objects.create(**data)

    if update_inventory:
        affect_inventory(inventory, "add", inventory_item)

    return inventory_item


def create_inventory_from_invoice_item(invoice_item, inventory=None, raise_exception=False, update_inventory=True):
    data = {
        "inventory": inventory,
        "product": invoice_item.product,
        "purchase_invoice_item": invoice_item,
        "product_expiry_date": invoice_item.product_expiry_date,
        "operating_number": invoice_item.operating_number,
        "purchase_discount_percentage": invoice_item.purchase_discount_percentage,
        "purchase_price": invoice_item.purchase_price,
        "selling_discount_percentage": invoice_item.selling_discount_percentage,
        "selling_price": invoice_item.selling_price,
        "quantity": invoice_item.quantity,
        "remaining_quantity": invoice_item.quantity,
        "purchase_sub_total": invoice_item.sub_total,
        "selling_sub_total": Decimal(invoice_item.quantity * invoice_item.selling_price).quantize(Decimal("0.00")),
    }

    return create_inventory_item(data, raise_exception=raise_exception, update_inventory=update_inventory)


def update_inventory_item(inventory_item, data, update_inventory=True):
    product = inventory_item.product

    data.pop("inventory", None)
    data.pop("product", None)
    data.pop("purchase_price", None)
    data.pop("selling_price", None)
    data.pop("purchase_sub_total", None)
    data.pop("selling_sub_total", None)
    data.pop("purchase_invoice_item", None)

    purchase_discount_percentage = data.get("purchase_discount_percentage", None)
    selling_discount_percentage = data.get("selling_discount_percentage", None)
    quantity = data.get("quantity", None)
    remaining_quantity = data.get("remaining_quantity", None)

    old_quantity = None
    old_purchase_sub_total = None
    old_selling_sub_total = None
    update_sub_total = False

    if purchase_discount_percentage is not None:
        purchase_price = Decimal(
            product.public_price - (product.public_price * purchase_discount_percentage / 100)
        ).quantize(Decimal("0.00"))
        data["purchase_price"] = purchase_price
        update_sub_total = True

    if selling_discount_percentage is not None:
        selling_price = Decimal(
            product.public_price - (product.public_price * selling_discount_percentage / 100)
        ).quantize(Decimal("0.00"))
        data["selling_price"] = selling_price
        update_sub_total = True

    if quantity is not None and remaining_quantity is None:
        old_quantity = inventory_item.remaining_quantity
        computed_remaining_quantity = remaining_quantity + quantity - inventory_item.quantity

        if computed_remaining_quantity < 0:
            raise ValidationError(
                {
                    "quantity": "Couldn't update quantity, Consumed quantity is more than {quantity}.".format(
                        quantity=quantity
                    )
                }
            )

        data["remaining_quantity"] = computed_remaining_quantity
        update_sub_total = True

    if remaining_quantity is not None:
        old_quantity = inventory_item.remaining_quantity
        update_sub_total = True

    for key, value in data.items():
        setattr(inventory_item, key, value)

    if update_sub_total:
        old_purchase_sub_total = inventory_item.purchase_sub_total
        old_selling_sub_total = inventory_item.selling_sub_total

        purchase_sub_total = Decimal(inventory_item.purchase_price * inventory_item.remaining_quantity).quantize(
            Decimal("0.00")
        )
        selling_sub_total = Decimal(inventory_item.selling_price * inventory_item.remaining_quantity).quantize(
            Decimal("0.00")
        )

        inventory_item.purchase_sub_total = purchase_sub_total
        inventory_item.selling_sub_total = selling_sub_total

    inventory_item.save()

    if update_inventory and update_sub_total:
        affect_inventory(
            inventory_item.inventory,
            "update",
            inventory_item,
            old_quantity,
            old_purchase_sub_total,
            old_selling_sub_total,
        )

    return inventory_item


def delete_inventory_item(inventory_item, update_inventory=True):
    if update_inventory:
        affect_inventory(inventory_item.inventory, "remove", inventory_item)

    inventory_item.delete()


def transfer_inventory_item(inventory_item, new_inventory, update_inventory=True):
    old_inventory = inventory_item.inventory

    if update_inventory:
        affect_inventory(old_inventory, "remove", inventory_item)

    inventory_item.inventory = new_inventory
    inventory_item.save()

    if update_inventory:
        affect_inventory(new_inventory, "add", inventory_item)

    return inventory_item
