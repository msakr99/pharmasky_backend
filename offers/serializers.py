from decimal import Decimal
from accounts.serializers import UserReadSerializer
from core.serializers.abstract_serializers import BaseModelSerializer, BaseUploaderSerializer
from market.serializers import ProductCodeReadSerializer, ProductReadSerializer
from offers.models import Offer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.apps import apps
from django.utils import timezone

from offers.utils import calculate_max_offer, calculate_max_offer_from_offer, get_selling_data, update_offer

get_model = apps.get_model


class OfferReadSerializer(BaseModelSerializer):
    product = ProductReadSerializer()
    user = UserReadSerializer()
    product_code = ProductCodeReadSerializer()
    actual_discount_precentage = serializers.DecimalField(max_digits=4, decimal_places=2, read_only=True)
    actual_offer_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Offer
        fields = [
            "id",
            "product_code",
            "product",
            "user",
            "operating_number",
            "available_amount",
            "remaining_amount",
            "max_amount_per_invoice",
            "product_expiry_date",
            "min_purchase",
            "purchase_discount_percentage",
            "purchase_price",
            "selling_discount_percentage",
            "selling_price",
            "is_max",
            "created_at",
            "actual_discount_precentage",
            "actual_offer_price",
        ]


class OfferCreateSerializer(BaseModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=get_model("accounts", "User").objects.select_related("profile").all(),
        required=False,
        allow_null=True,
        write_only=True
    )
    
    # إضافة حقول بديلة لإنشاء العرض مباشرة
    product_id = serializers.IntegerField(required=False, write_only=True)
    store_id = serializers.IntegerField(required=False, write_only=True)
    code = serializers.IntegerField(required=False, write_only=True)
    
    # تعديل product_code ليقبل code بدلاً من معرف StoreProductCode
    product_code = serializers.IntegerField(required=False, write_only=True, help_text="StoreProductCode code")

    class Meta:
        model = Offer
        fields = [
            "product_code",
            "product_id",
            "store_id", 
            "code",
            "available_amount",
            "purchase_discount_percentage",
            "min_purchase",
            "max_amount_per_invoice",
            "operating_number",
            "product_expiry_date",
            "user",
        ]
        extra_kwargs = {
            "product_code": {
                "queryset": get_model("market", "StoreProductCode")
                .objects.select_related("store", "product")
                .all(),
                "required": False,
                "allow_null": True,
            },
        }

    def validate(self, attrs):
        product_code_value = attrs.get("product_code")  # هذا الآن code وليس معرف
        product_id = attrs.get("product_id")
        store_id = attrs.get("store_id")
        code = attrs.get("code")
        available_amount = attrs.get("available_amount")
        purchase_discount_percentage = attrs.get("purchase_discount_percentage")
        specified_user = attrs.get("user")

        # تحديد المستخدم المستهدف
        request_user = self.context.get('request').user
        
        # تحديد StoreProductCode
        if product_code_value is not None:
            # البحث عن StoreProductCode باستخدام code
            try:
                final_product_code = get_model("market", "StoreProductCode").objects.select_related(
                    "product", "store"
                ).get(code=product_code_value)
                target_user = final_product_code.store
            except get_model("market", "StoreProductCode").DoesNotExist:
                raise ValidationError({
                    "product_code": f"StoreProductCode with code {product_code_value} not found."
                })
        elif product_id is not None and store_id is not None and code is not None:
            # إنشاء StoreProductCode جديد تلقائياً
            try:
                product = get_model("market", "Product").objects.get(id=product_id)
                store = get_model("accounts", "Store").objects.get(id=store_id)
                
                # إنشاء أو الحصول على StoreProductCode
                try:
                    final_product_code = get_model("market", "StoreProductCode").objects.get(
                        product=product,
                        store=store
                    )
                    # إذا كان موجود، تحديث الكود
                    final_product_code.code = code
                    final_product_code.save()
                except get_model("market", "StoreProductCode").DoesNotExist:
                    # إنشاء جديد
                    final_product_code = get_model("market", "StoreProductCode").objects.create(
                        product=product,
                        store=store,
                        code=code
                    )
                
                target_user = store
                
            except get_model("market", "Product").DoesNotExist:
                raise ValidationError({"product_id": "Product not found."})
            except get_model("accounts", "Store").DoesNotExist:
                raise ValidationError({"store_id": "Store not found."})
        else:
            raise ValidationError({
                "product_code": "Either product_code (StoreProductCode code) or (product_id, store_id, code) must be provided."
            })
        
        # تحديد المستخدم النهائي
        if specified_user is not None:
            # إذا تم تحديد مستخدم، تحقق من صلاحيات الادمن
            if request_user.role != 'ADMIN':
                raise ValidationError({"user": "Only admin can specify a user for offer creation."})
            
            # تحقق من أن المستخدم المحدد هو مخزن
            if specified_user.role != 'STORE':
                raise ValidationError({"user": "Specified user must be a store."})
            
            target_user = specified_user

        public_price = final_product_code.product.public_price

        selling_discount_percentage, selling_price = get_selling_data(
            final_product_code.product, target_user, purchase_discount_percentage
        )

        attrs["product_code"] = final_product_code
        attrs["user"] = target_user
        attrs["product"] = final_product_code.product
        attrs["remaining_amount"] = available_amount
        attrs["selling_discount_percentage"] = selling_discount_percentage
        attrs["selling_price"] = selling_price
        attrs["purchase_price"] = public_price * (1 - purchase_discount_percentage / 100)

        return super().validate(attrs)

    def create(self, validated_data):
        with transaction.atomic():
            instance = super().create(validated_data)
            calculate_max_offer_from_offer(instance)

        return instance

    def to_representation(self, instance):
        return OfferReadSerializer(instance, context=self.context).data


class UserOfferCreateSerializer(BaseModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    product = ProductReadSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=get_model("market", "Product").objects.all(), write_only=True, required=True, source="product"
    )

    class Meta:
        model = Offer
        fields = [
            "user",
            "product",
            "product_id",
            "available_amount",
            "purchase_discount_percentage",
            "operating_number",
            "product_expiry_date",
        ]
        extra_kwargs = {
            "purchase_discount_percentage": {
                "min_value": 0,
                "max_value": 99.99,
            },
        }

    def validate(self, attrs):
        user = attrs.get("user")
        product = attrs.get("product")
        available_amount = attrs.get("available_amount")
        purchase_discount_percentage = attrs.get("purchase_discount_percentage")

        public_price = product.public_price

        selling_discount_percentage, selling_price = get_selling_data(product, user, purchase_discount_percentage)

        attrs["remaining_amount"] = available_amount
        attrs["purchase_price"] = public_price * (1 - purchase_discount_percentage / 100)
        attrs["selling_discount_percentage"] = selling_discount_percentage
        attrs["selling_price"] = selling_price

        return super().validate(attrs)

    def create(self, validated_data):
        with transaction.atomic():
            instance = super().create(validated_data)
            calculate_max_offer_from_offer(instance)

        return instance


class OfferUpdateSerializer(BaseModelSerializer):
    product_code = ProductCodeReadSerializer(read_only=True)
    product = ProductReadSerializer(read_only=True)
    user = UserReadSerializer(read_only=True)

    class Meta:
        model = Offer
        fields = [
            "id",
            "product_code",
            "product",
            "user",
            "operating_number",
            "available_amount",
            "remaining_amount",
            "max_amount_per_invoice",
            "product_expiry_date",
            "min_purchase",
            "purchase_discount_percentage",
            "purchase_price",
            "selling_discount_percentage",
            "selling_price",
            "is_max",
            "created_at",
        ]
        read_only_fields = ["purchase_price", "selling_price", "created_at"]

    def update(self, instance, validated_data):
        with transaction.atomic():
            instance = update_offer(instance, validated_data)

        return instance


class OfferExcelReadSerialzier(BaseModelSerializer):
    product_seller_code = serializers.CharField(read_only=True)
    product_name = serializers.CharField(read_only=True)
    public_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    selling_discount_percentage = serializers.DecimalField(max_digits=4, decimal_places=2, read_only=True)

    class Meta:
        model = Offer
        fields = [
            "product_seller_code",
            "product_name",
            "public_price",
            "selling_discount_percentage",
        ]


class OfferPDFReadSerializer(BaseModelSerializer):
    product_name = serializers.CharField(read_only=True)
    public_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    selling_discount_percentage = serializers.DecimalField(max_digits=4, decimal_places=2, read_only=True)

    class Meta:
        model = Offer
        fields = ["product_name", "public_price", "selling_discount_percentage"]


class OfferUploaderSerializer(BaseUploaderSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=get_model("accounts", "User").objects.select_related("profile").all(), required=True, write_only=True
    )
    required_columns = [
        "product_code",
        "available_amount",
        "purchase_discount_percentage",
        "max_amount_per_invoice",
        "min_purchase",
        "product_expiry_date",
        "operating_number",
    ]
    additional_values = [
        "product",
        "user",
        "remaining_amount",
        "selling_discount_percentage",
        "selling_price",
        "purchase_price",
    ]

    def validate_column_product_code(self, value, line_number):
        if value is None or value == "":
            raise serializers.ValidationError(
                _("in line {line_number}, Product code was not specified.").format(line_number=line_number)
            )

        # Convert decimal to integer if needed (handle Excel format like 22.0 -> 22)
        try:
            if isinstance(value, (int, float)):
                code_value = int(value)
            else:
                code_value = int(float(str(value)))
        except (ValueError, TypeError):
            raise serializers.ValidationError(
                _("in line {line_number}, Product code must be a valid number.").format(line_number=line_number)
            )

        # Admin can upload for any store, others can only upload for their own store
        if hasattr(self, 'request_user') and self.request_user.role == 'ADMIN':
            # Admin can upload for any store
            product_code = (
                get_model("market", "StoreProductCode")
                .objects.select_related("product", "store")
                .filter(code=code_value, store_id=self.user.id)
                .first()
            )
        else:
            # Regular users can only upload for their own store
            product_code = (
                get_model("market", "StoreProductCode")
                .objects.select_related("product", "store")
                .filter(code=code_value, store_id=self.user.id)
                .first()
            )

        if product_code is None:
            raise serializers.ValidationError(
                _(
                    "in line {line_number}, Product code {code} was not found, Please add the Code first then try again."
                ).format(line_number=line_number, code=code_value)
            )

        return product_code

    def validate_column_available_amount(self, value, line_number):
        try:
            # Convert decimal to integer if needed (handle Excel format like 100.0 -> 100)
            if isinstance(value, (int, float)):
                validated_value = int(value)
            else:
                validated_value = int(float(str(value)))
        except (ValueError, TypeError):
            err_message = _("in line {line_number}, Available amount should be an Integer postive number.").format(
                line_number=line_number
            )
            raise serializers.ValidationError(err_message)

        if not validated_value > 0:
            err_message = _("in line {line_number}, Available amount should be greater than zero.").format(
                line_number=line_number
            )
            raise serializers.ValidationError(err_message)

        return validated_value

    def validate_column_max_amount_per_invoice(self, value, line_number):
        if value is None:
            return value

        try:
            # Convert decimal to integer if needed (handle Excel format like 50.0 -> 50)
            if isinstance(value, (int, float)):
                validated_value = int(value)
            else:
                validated_value = int(float(str(value)))
        except (ValueError, TypeError):
            err_message = _(
                "in line {line_number}, Max amount per invoice should be an Integer postive number."
            ).format(line_number=line_number)
            raise serializers.ValidationError(err_message)

        if not validated_value > 0:
            err_message = _("in line {line_number}, Max amount per invoice should be greater than zero.").format(
                line_number=line_number
            )
            raise serializers.ValidationError(err_message)

        return validated_value

    def validate_column_purchase_discount_percentage(self, value, line_number):
        if value is None or value == "":
            err_message = _("in line {line_number}, Discount Percentage was not specified.").format(
                line_number=line_number
            )
            raise serializers.ValidationError(err_message)

        else:
            try:
                purchase_discount_percentage = Decimal(value).quantize(Decimal("00.00"))
                profit_percentage = Decimal(self.user_profile.profit_percentage).quantize(Decimal("00.00"))

                if purchase_discount_percentage < profit_percentage:
                    raise serializers.ValidationError(
                        _(
                            "in line {line_number}, Purchase discount percenteage should be greater than or equal to {profit_percentage}."
                        ).format(line_number=line_number, profit_percentage=profit_percentage)
                    )

                if purchase_discount_percentage >= 100 or purchase_discount_percentage < 0:
                    raise serializers.ValidationError(
                        _(
                            "in line {line_number}, Purchase discount percenteage should be between 0 and 99.99."
                        ).format(line_number=line_number)
                    )

            except ValueError:
                raise serializers.ValidationError(
                    _("in line {line_number}, Purchase discount percenteage should be a number.").format(
                        line_number=line_number
                    )
                )

        return purchase_discount_percentage

    def validate_column_min_purchase(self, value, line_number):
        if value is None or value == "":
            return Decimal("0.00")

        try:
            validated_value = Decimal(value).quantize(Decimal("00.00"))
        except (ValueError, TypeError):
            raise serializers.ValidationError(
                _("in line {line_number}, Min purchase should be a number.").format(line_number=line_number)
            )

        if validated_value < 0:
            raise serializers.ValidationError(
                _("in line {line_number}, Min purchase should be greater than or equal to zero.").format(
                    line_number=line_number
                )
            )

        return validated_value

    def validate_column_product_expiry_date(self, value, line_number):
        if value is not None:
            try:
                # Convert string to date if needed
                if isinstance(value, str):
                    from datetime import datetime
                    date_value = datetime.strptime(value, '%Y-%m-%d').date()
                else:
                    date_value = value.date() if hasattr(value, 'date') else value
                
                if date_value < timezone.now().date():
                    raise serializers.ValidationError(
                        _("in line {line_number}, Product expiry date should not be in the past.").format(
                            line_number=line_number
                        )
                    )
            except ValueError:
                raise serializers.ValidationError(
                    _("in line {line_number}, Invalid date format. Use YYYY-MM-DD.").format(
                        line_number=line_number
                    )
                )

    def validate_column_operating_number(self, value, line_number):
        if value is None:
            return ""
        return str(value)

    def get_value_user(self, row_values, validated_row_values, line_number):
        return self.user

    def get_value_product(self, row_values, validated_row_values, line_number):
        product_code = validated_row_values.get("product_code", None)
        return product_code.product

    def get_value_remaining_amount(self, row_values, validated_row_values, line_number):
        return validated_row_values.get("available_amount", None)

    def get_value_purchase_price(self, row_values, validated_row_values, line_number):
        product_code = validated_row_values.get("product_code", None)
        purchase_discount_percentage = validated_row_values.get("purchase_discount_percentage", None)
        public_price = product_code.product.public_price
        purchase_price = Decimal(public_price * (1 - purchase_discount_percentage / 100)).quantize(Decimal("0.00"))
        return purchase_price

    def get_value_selling_discount_percentage(self, row_values, validated_row_values, line_number):
        profit_percentage = Decimal(self.user_profile.profit_percentage).quantize(Decimal("00.00"))
        purchase_discount_percentage = validated_row_values.get("purchase_discount_percentage", None)
        selling_discount_percentage = Decimal(purchase_discount_percentage - profit_percentage).quantize(
            Decimal("00.00")
        )
        return selling_discount_percentage

    def get_value_selling_price(self, row_values, validated_row_values, line_number):
        product_code = validated_row_values.get("product_code", None)
        public_price = product_code.product.public_price
        profit_percentage = Decimal(self.user_profile.profit_percentage).quantize(Decimal("00.00"))
        purchase_discount_percentage = validated_row_values.get("purchase_discount_percentage", None)
        selling_discount_percentage = Decimal(purchase_discount_percentage - profit_percentage).quantize(
            Decimal("00.00")
        )
        selling_price = Decimal(public_price * (1 - selling_discount_percentage / 100)).quantize(Decimal("0.00"))
        return selling_price

    def validate(self, attrs):
        user = attrs.get("user", None)
        user_profile = getattr(user, "profile", None)

        if user_profile is None:
            raise serializers.ValidationError({"detail": _("User has no profile, Please contract support.")})

        self.user = user
        self.user_profile = user_profile
        
        # Store the request user for admin checks
        if hasattr(self.context.get('request'), 'user'):
            self.request_user = self.context['request'].user

        return super().validate(attrs)

    def create(self, validated_data):
        rows = validated_data.get("data")
        user = validated_data.get("user")

        offers_list = []
        products_set = set()

        with transaction.atomic():
            existing_user_offers = Offer.objects.filter(user=user)

            # To ensure that even if the uploaded products doesn't contain any of the existing products,
            # we still calculate the max offer and update the carts
            products_set = set(existing_user_offers.values_list("product_id", flat=True))
            existing_user_offers.delete()

            for row_data in rows:
                print(row_data)
                offer_instance = Offer.objects.create(**row_data)
                offers_list.append(offer_instance)
                products_set.add(row_data.get("product").pk)

            # self.set_max_offers_and_update_carts(products_set)
            for product_id in products_set:
                calculate_max_offer(product_id)

        return offers_list

    def to_representation(self, instance):
        return {}


# def set_max_offers_and_update_carts(self, products_list: set):
#     product_discounts = (
#         market_models.StoreOffer.objects.filter(product_id__in=products_list)
#         .values("product_id")
#         .annotate(max_discount=Max("discount_precentage"))
#     )

#     non_exsiting_product_offers = products_list.difference(
#         set(product_discounts.values_list("product_id", flat=True))
#     )

#     for product_discount in product_discounts:
#         product_id = product_discount["product_id"]
#         max_discount = product_discount["max_discount"]

#         market_models.StoreOffer.objects.filter(product_id=product_id).update(
#             is_max=Case(
#                 When(discount_precentage=max_discount, then=Value(True)),
#                 default=Value(False),
#             )
#         )

#         selected_offer = (
#             market_models.StoreOffer.objects.filter(product=product_id, is_max=True, remaining_amount__gt=0)
#             .order_by("-remaining_amount")
#             .first()
#         )

#         affected_cart_details = market_models.PharmacyCartDetail.objects.select_related(
#             "pharmacy_cart", "pharmacy_cart__pharmacy__pharmacy_profile__payment_period"
#         ).filter(offer_content_type__model="storeoffer", product_id=product_id)

#         for affected_cart_detail in affected_cart_details:
#             pharmacy_cart = affected_cart_detail.pharmacy_cart
#             pharamcy = pharmacy_cart.pharmacy
#             quantity = affected_cart_detail.quantity

#             additional_fees_percentage = _get_payment_period(pharamcy)

#             if (
#                 selected_offer is None
#                 or selected_offer.remaining_amount < affected_cart_detail.quantity
#                 or additional_fees_percentage is None
#             ):
#                 affected_cart_detail.delete()
#                 affect_pharmacy_cart(
#                     pharmacy_cart,
#                     Effect.REMOVE_ITEM,
#                     total_price=affected_cart_detail.total_price,
#                     total_items_count=quantity,
#                 )
#                 continue

#             old_total_price = affected_cart_detail.total_price

#             if affected_cart_detail.offer_object_id == selected_offer.pk:
#                 # If the selected offer is the same as the current offer, skip the update
#                 continue

#             offer_discount_precentage = selected_offer.discount_precentage

#             discount_precentage = offer_discount_precentage - additional_fees_percentage
#             actual_price = selected_offer.product.public_price * (1 - (discount_precentage / 100))
#             total_price = actual_price * quantity

#             affected_cart_detail.offer_object_id = selected_offer.pk
#             affected_cart_detail.offer_discount_percentage = offer_discount_precentage
#             affected_cart_detail.discount_percentage = discount_precentage
#             affected_cart_detail.total_price = total_price

#             affected_cart_detail.save()

#             affect_pharmacy_cart(
#                 pharmacy_cart,
#                 Effect.UPDATE_ITEM,
#                 old_total_items_count=quantity,
#                 total_items_count=quantity,
#                 old_total_price=old_total_price,
#                 total_price=total_price,
#             )

#     for non_exsisting_offer in non_exsiting_product_offers:
#         pharmacy_cart_details = market_models.PharmacyCartDetail.objects.filter(product_id=non_exsisting_offer)
#         for pharmacy_cart_detail in pharmacy_cart_details:
#             pharmacy_cart = pharmacy_cart_detail.pharmacy_cart
#             affect_pharmacy_cart(
#                 pharmacy_cart,
#                 Effect.REMOVE_ITEM,
#                 total_price=pharmacy_cart_detail.total_price,
#                 total_items_count=pharmacy_cart_detail.quantity,
#             )
#             pharmacy_cart_detail.delete()
