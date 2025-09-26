from django.apps import apps

from offers.utils import update_offer_product_public_price

get_model = apps.get_model


def update_product(product, data, affect_offers=True, update_carts=True):

    public_price = data.get("public_price", None)
    need_update = public_price is not None and product.public_price != public_price

    for key, value in data.items():
        setattr(product, key, value)

    product.save(update_fields=data.keys())

    if need_update and affect_offers:
        update_offer_product_public_price(product, update_carts=update_carts)

    return product
