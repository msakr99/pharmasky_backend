from decimal import Decimal
from django.db import models
from django.apps import apps
from rest_framework.exceptions import ValidationError

from shop.utils import mark_item_as_sold_out, update_cart_item_offer

get_model = apps.get_model


def deconstuct_offer(offer):
    return {
        "product": offer.product,
        "product_expiry_date": offer.product_expiry_date,
        "operating_number": offer.operating_number,
        "purchase_discount_percentage": offer.purchase_discount_percentage,
        "purchase_price": offer.purchase_price,
        "selling_discount_percentage": offer.selling_discount_percentage,
        "selling_price": offer.selling_price,
    }


def get_selling_data(product, user, purchase_discount_percentage, raise_exception=True):
    user_profile = getattr(user, "profile", None)

    if user_profile is None:
        if raise_exception:
            raise ValidationError({"detail": "User does not have a profile."})
        return None, None

    profit_percentage = user_profile.profit_percentage or Decimal("0.00")
    public_price = product.public_price

    if purchase_discount_percentage < profit_percentage:
        if raise_exception:
            raise ValidationError(
                {"purchase_discount_percentage": f"Purchase discount (%) should be greater than {profit_percentage}."}
            )
        return None, None

    selling_discount_percentage = purchase_discount_percentage - profit_percentage
    selling_price = public_price * (1 - selling_discount_percentage / 100)

    selling_discount_percentage = Decimal(selling_discount_percentage).quantize(Decimal("0.01"))
    selling_price = Decimal(selling_price).quantize(Decimal("0.01"))

    return selling_discount_percentage, selling_price


def affect_offer(operation, invoice_item, old_quantity=None, reset_max=True):
    offer = invoice_item.offer

    if offer is None:
        return

    if operation == "add":
        offer.remaining_amount -= invoice_item.quantity

        if reset_max and offer.remaining_amount == 0:
            calculate_max_offer_from_offer(offer)

    elif operation == "update":
        old_amount = offer.remaining_amount
        if old_quantity is not None:
            offer.remaining_amount += old_quantity - invoice_item.quantity

        if reset_max and (offer.remaining_amount == 0 or old_amount == 0):
            calculate_max_offer_from_offer(offer)

    elif operation == "remove":
        old_amount = offer.remaining_amount
        offer.remaining_amount += invoice_item.quantity

        if reset_max and old_amount == 0:
            calculate_max_offer_from_offer(offer)

    if offer.remaining_amount < 0:
        raise ValidationError({"offer": "Insufficient offer amount."})

    offer.save()

    return offer


def calculate_max_offer(product, affect_carts=True):
    Offer = get_model("offers", "Offer")

    filter_kwargs = {}

    if isinstance(product, str) or isinstance(product, int):
        filter_kwargs["product_id"] = product
    elif isinstance(product, models.Model):
        filter_kwargs["product"] = product

    queryset = Offer.objects.filter(**filter_kwargs)
    queryset.update(is_max=False)

    max_selling_discount = queryset.filter(remaining_amount__gt=0).aggregate(
        max_selling_discount=models.Max("selling_discount_percentage"),
    )["max_selling_discount"]
    queryset.filter(selling_discount_percentage=max_selling_discount).update(is_max=True)

    if affect_carts:
        CartItem = get_model("shop", "CartItem")
        cart_items = CartItem.objects.select_related("cart__user__profile__payment_period").filter(product=product)
        max_offer = queryset.filter(is_max=True).first()

        if max_offer is not None:
            for item in cart_items:
                update_cart_item_offer(item, max_offer)
        else:
            for item in cart_items:
                mark_item_as_sold_out(item)


def update_offer(offer, data, affect_carts=True):
    data.pop("product_code", None)
    data.pop("product", None)
    data.pop("user", None)
    data.pop("purchase_price", None)
    data.pop("selling_price", None)

    calculate_max_offer = False
    purchase_discount_percentage = data.get("purchase_discount_percentage", None)
    selling_discount_percentage = data.get("purchase_discount_percentage", None)

    public_price = offer.product.public_price

    if purchase_discount_percentage is not None and offer.purchase_discount_percentage != purchase_discount_percentage:
        calculate_max_offer = True
        selling_discount_percentage, selling_price = get_selling_data(
            offer.product, offer.user, purchase_discount_percentage
        )
        purchase_price = public_price * (1 - purchase_discount_percentage / 100)
        data["purchase_price"] = Decimal(purchase_price).quantize(Decimal("0.01"))
        data["selling_discount_percentage"] = Decimal(selling_discount_percentage).quantize(Decimal("0.01"))
        data["selling_price"] = Decimal(selling_price).quantize(Decimal("0.01"))

    elif selling_discount_percentage is not None and offer.selling_discount_percentage != selling_discount_percentage:
        calculate_max_offer = True
        selling_price = public_price * (1 - selling_discount_percentage / 100)
        data["selling_price"] = Decimal(selling_price).quantize(Decimal("0.01"))

    for key, value in data.items():
        setattr(offer, key, value)

    offer.save(update_fields=data.keys())

    if calculate_max_offer:
        calculate_max_offer_from_offer(offer, affect_carts=affect_carts)
    else:
        if affect_carts:
            CartItem = get_model("shop", "CartItem")
            cart_items = CartItem.objects.select_related("cart__user__profile__payment_period").filter(offer=offer)
            for item in cart_items:
                update_cart_item_offer(item, offer)

    return offer


def update_offer_product_public_price(product, update_carts=True):
    Offer = get_model("offers", "Offer")
    offers = Offer.objects.select_related("user", "user__profile").filter(product=product)

    if update_carts:
        offers = offers.prefetch_related(
            models.Prefetch(
                "cart_items",
                queryset=get_model("shop", "CartItem").objects.select_related("cart__user__profile__payment_period"),
            )
        )

    public_price = product.public_price

    for offer in offers:
        offer.purchase_price = public_price * (1 - offer.purchase_discount_percentage / 100)
        offer.selling_price = public_price * (1 - offer.selling_discount_percentage / 100)
        offer.save(update_fields=["purchase_price", "selling_price"])

        if update_carts:
            for cart_item in offer.cart_items.all():
                update_cart_item_offer(cart_item, offer)

    # No need to recalculate max offer here, as it is not affected by public price changes (Same Discount Percentage)


def calculate_max_offer_from_offer(offer, affect_carts=True):
    product = offer.product
    calculate_max_offer(product, affect_carts=affect_carts)


def delete_offer(offer, reset_max=True):
    if reset_max:
        is_wholesale = offer.is_wholesale
        product = offer.product
        offer.delete()
        
        if is_wholesale:
            calculate_max_wholesale_offer(product)
        else:
            calculate_max_offer(product)
    else:
        offer.delete()


# دوال خاصة بعروض الجملة
def calculate_max_wholesale_offer(product, affect_carts=False):
    """
    حساب أفضل عرض جملة للمنتج بناءً على أعلى خصم
    عروض الجملة منفصلة تماماً عن العروض العادية
    """
    Offer = get_model("offers", "Offer")

    filter_kwargs = {"is_wholesale": True}

    if isinstance(product, str) or isinstance(product, int):
        filter_kwargs["product_id"] = product
    elif isinstance(product, models.Model):
        filter_kwargs["product"] = product

    # الحصول على جميع عروض الجملة للمنتج
    queryset = Offer.objects.filter(**filter_kwargs)
    queryset.update(is_max_wholesale=False)

    # حساب أعلى خصم في عروض الجملة
    max_selling_discount = queryset.filter(remaining_amount__gt=0).aggregate(
        max_selling_discount=models.Max("selling_discount_percentage"),
    )["max_selling_discount"]

    if max_selling_discount is not None:
        queryset.filter(
            selling_discount_percentage=max_selling_discount,
            remaining_amount__gt=0
        ).update(is_max_wholesale=True)

    # ملاحظة: عروض الجملة لا تؤثر على السلات العادية
    # لأن لها نظام طلب منفصل


def calculate_max_wholesale_offer_from_offer(offer, affect_carts=False):
    """
    حساب أفضل عرض جملة بناءً على عرض محدد
    """
    if not offer.is_wholesale:
        return
    
    product = offer.product
    calculate_max_wholesale_offer(product, affect_carts=affect_carts)


def update_wholesale_offer(offer, data, affect_carts=False):
    """
    تحديث عرض جملة
    مشابه لـ update_offer لكن خاص بالجملة
    """
    data.pop("product_code", None)
    data.pop("product", None)
    data.pop("user", None)
    data.pop("purchase_price", None)
    data.pop("selling_price", None)

    calculate_max = False
    purchase_discount_percentage = data.get("purchase_discount_percentage", None)
    selling_discount_percentage = data.get("purchase_discount_percentage", None)

    public_price = offer.product.public_price

    if purchase_discount_percentage is not None and offer.purchase_discount_percentage != purchase_discount_percentage:
        calculate_max = True
        selling_discount_percentage, selling_price = get_selling_data(
            offer.product, offer.user, purchase_discount_percentage
        )
        purchase_price = public_price * (1 - purchase_discount_percentage / 100)
        data["purchase_price"] = Decimal(purchase_price).quantize(Decimal("0.01"))
        data["selling_discount_percentage"] = Decimal(selling_discount_percentage).quantize(Decimal("0.01"))
        data["selling_price"] = Decimal(selling_price).quantize(Decimal("0.01"))

    elif selling_discount_percentage is not None and offer.selling_discount_percentage != selling_discount_percentage:
        calculate_max = True
        selling_price = public_price * (1 - selling_discount_percentage / 100)
        data["selling_price"] = Decimal(selling_price).quantize(Decimal("0.01"))

    for key, value in data.items():
        setattr(offer, key, value)

    offer.save(update_fields=data.keys())

    if calculate_max:
        calculate_max_wholesale_offer_from_offer(offer, affect_carts=affect_carts)

    return offer
