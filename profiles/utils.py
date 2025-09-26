from shop.utils import update_user_discount_percentage


def update_user_profile(profile, data, update_cart=True):
    data.pop("user", None)
    payment_period = data.get("payment_period", None)
    delta_user_discount_percentage = None

    if payment_period is not None:
        old_payment_period = getattr(profile, "payment_period", None)

        if old_payment_period is None:
            delta_user_discount_percentage = payment_period.addition_percentage
        else:
            delta_user_discount_percentage = (
                payment_period.addition_percentage - old_payment_period.addition_percentage
            )

    for key, value in data.items():
        setattr(profile, key, value)

    profile.save()

    if update_cart and (delta_user_discount_percentage is not None or delta_user_discount_percentage != 0):
        cart = getattr(profile.user, "cart", None)
        if cart is not None:
            update_user_discount_percentage(cart, delta_user_discount_percentage)

    return profile
