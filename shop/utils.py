from decimal import Decimal
from django.db import models
from django.apps import apps

get_model = apps.get_model


# Cart
def affect_cart(cart, operation, item, old_quantity=None, old_price=None):
    if operation == "add":
        cart.total_price += item.sub_total
        cart.items_count += 1
        cart.total_quantity += item.quantity

    elif operation == "update":
        if old_price is not None:
            cart.total_price += item.sub_total - old_price
        if old_quantity is not None:
            cart.total_quantity += item.quantity - old_quantity

    elif operation == "remove":
        cart.total_price -= item.sub_total
        cart.items_count -= 1
        cart.total_quantity -= item.quantity

    cart.save()
    return cart


def reset_cart(cart):
    cart.items_count = 0
    cart.total_quantity = 0
    cart.total_price = Decimal("0.00").quantize(Decimal("0.00"))

    cart.save()
    cart.items.all().delete()

    return cart


def update_user_discount_percentage(cart, delta_user_discount_percentage):
    cart.items.all()

    cart_total_price = Decimal("0.00").quantize(Decimal("0.00"))

    for item in cart.items.all():
        product = item.product
        quantity = item.quantity

        discount_percentage = item.discount_percentage + delta_user_discount_percentage
        price = product.public_price * (1 - discount_percentage / 100)
        sub_total = Decimal(price * quantity).quantize(Decimal("0.00"))

        cart_total_price += sub_total

        item.discount_percentage = discount_percentage
        item.price = price
        item.sub_total = sub_total
        item.save()

    cart.total_price = cart_total_price
    cart.save()
    return cart


# Cart Item
def create_cart_item(data, update_cart=True):
    CartItem = get_model("shop", "CartItem")
    item = CartItem.objects.create(**data)

    if update_cart:
        affect_cart(item.cart, "add", item)

    return item


def update_cart_item(item, data, update_cart=True):
    data.pop("cart", None)
    data.pop("offer", None)
    data.pop("product", None)
    data.pop("price", None)
    data.pop("sub_total", None)

    needs_update = False
    old_quantity = None
    old_price = None

    quantity = data.get("quantity", None)
    discount_percentage = data.get("discount_percentage", None)

    if quantity is not None:
        old_price = item.sub_total
        old_quantity = item.quantity
        data["sub_total"] = Decimal(item.price * quantity).quantize(Decimal("0.00"))
        needs_update = True

    if discount_percentage is not None:
        old_price = item.sub_total
        product = item.product
        price = product.public_price - (product.public_price * discount_percentage / 100)

        data["price"] = price
        sub_total = price * (quantity if quantity is not None else item.quantity)
        data["sub_total"] = Decimal(sub_total).quantize(Decimal("0.00"))

        needs_update = True

    for key, value in data.items():
        setattr(item, key, value)

    item.save()

    if update_cart and needs_update:
        affect_cart(item.cart, "update", item, old_quantity, old_price)

    return item


def delete_cart_item(item, update_cart=True):
    if update_cart:
        affect_cart(item.cart, "remove", item)

    item.delete()

    return item


def mark_item_as_sold_out(item, update_cart=True):
    item.sold_out = True
    item.save()

    if update_cart:
        affect_cart(item.cart, "remove", item)


def update_cart_item_offer(item, offer):
    payment_period = item.cart.user.profile.payment_period
    addition_percentage = payment_period.addition_percentage

    public_price = item.product.public_price

    was_sold_out = item.sold_out
    old_price = item.sub_total

    item.offer = offer
    item.discount_percentage = offer.selling_discount_percentage - addition_percentage
    price = Decimal(public_price * (1 - item.discount_percentage / 100)).quantize(Decimal("0.00"))
    item.price = price
    item.sub_total = Decimal(price * item.quantity).quantize(Decimal("0.00"))
    item.sold_out = False
    item.save()

    if was_sold_out:
        affect_cart(item.cart, "add", item)
    else:
        affect_cart(item.cart, "update", item, old_price=old_price)

    return item
