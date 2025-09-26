from django.db import models
from django.db.models import OuterRef, Case, When, F, Count, Q, Value, Subquery
from django.db.models.functions import Greatest
from django.apps import apps
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from accounts.choices import Role

# from market.choices import PharmacyInvoiceIconClassChoice, PharmacyInvoiceStatusChoice, PharmacyInvoiceStyleClassChoice

get_model = apps.get_model


class ProductQuerySet(models.QuerySet):
    def with_max_offer_discount_percentage(self):
        # store_offer_subquery = get_model("market", "StoreOffer").objects.filter(is_max=True, product=OuterRef("pk"))[
        #     :1
        # ]
        # pharmacy_offer_subquery = get_model("market", "PharmacyOffer").objects.filter(
        #     remaining_amount__gt=0, is_max=True, product=OuterRef("pk")
        # )[:1]
        # return self.annotate(
        #     max_store_offer=Subquery(store_offer_subquery.values("discount_precentage")),
        #     max_pharmacy_offer=Subquery(pharmacy_offer_subquery.values("discount_precentage")),
        #     max_offer_discount_percentage=Case(
        #         When(max_pharmacy_offer__gt=F("max_store_offer"), then=F("max_pharmacy_offer")),
        #         default=F("max_store_offer"),
        #         output_field=models.DecimalField(),
        #     ),
        #     max_offer_id=Case(
        #         When(max_pharmacy_offer__gt=F("max_store_offer"), then=Subquery(pharmacy_offer_subquery.values("id"))),
        #         default=Subquery(store_offer_subquery.values("id")),
        #         output_field=models.PositiveBigIntegerField(),
        #     ),
        #     max_offer_type=Case(
        #         When(max_pharmacy_offer__gt=F("max_store_offer"), then=Value("pharmacyoffer")),
        #         default=Value("storeoffer"),
        #         output_field=models.CharField(),
        #     ),
        # )
        return self

    def with_has_image(self):
        return self.annotate(
            has_image=Case(
                When(image="", then=False),
                default=True,
                output_field=models.BooleanField(),
            )
        )

    def with_frequently_purchased(self, pharmacy):
        return self.annotate(
            purchased_count=Count(
                "pharmacy_invoice_details",
                filter=Q(pharmacy_invoice_details__pharmacy_invoice__pharmacy=pharmacy),
            )
        )


class ProductManager(models.Manager):
    pass


class PharmacyInvoiceQuerySet(models.QuerySet):
    def with_pharmacy_invoice_details_count(self):
        return self.annotate(
            pharmacy_invoice_details_count=Count("pharmacy_invoice_details", distinct=True),
            rejected_pharmacy_invoice_details_count=Count(
                "pharmacy_invoice_details",
                filter=Q(pharmacy_invoice_details__seller_invoice_detail__is_accepted=False),
                distinct=True,
            ),
        )


class PharmacyInvoiceManager(models.Manager):
    pass


class PharmacyInvoiceDetailQuerySet(models.QuerySet):
    def with_status(self):
        PENDING_ACCEPTANCE = force_str(_("Pending Acceptance"))
        REJECTED = force_str(_("Rejected"))
        PENDING_RECIEPTION = force_str(_("Pending recieption from seller"))
        RECIEVED = force_str(_("Recieved from seller"))
        SHIPPED = force_str(_("Shipped"))
        DELIVERED = force_str(_("Delivered"))

        return self.annotate(
            status=Case(
                When(
                    Q(seller_invoice_detail__is_accepted=False),
                    then=Value(REJECTED),
                ),
                When(
                    Q(seller_invoice_detail__is_accepted__isnull=True),
                    then=Value(PENDING_ACCEPTANCE),
                ),
                When(
                    Q(seller_invoice_detail__is_recieved__isnull=True),
                    then=Value(PENDING_RECIEPTION),
                ),
                When(
                    Q(is_shipped=False),
                    then=Value(RECIEVED),
                ),
                When(
                    Q(is_delivered=False),
                    then=Value(SHIPPED),
                ),
                default=Value(DELIVERED),
                output_field=models.CharField(),
            )
        )


class PharmacyInvoiceDetailManager(models.Manager):
    pass


class PharmacyInvoiceStatusManager(models.Manager):
    def create_statuses(self, pharmacy_invoice):
        choices = PharmacyInvoiceStatusChoice.choices
        icon_class_choices = PharmacyInvoiceIconClassChoice.choices
        style_class_choices = PharmacyInvoiceStyleClassChoice.choices

        lst = []

        for idx, choice in enumerate(choices):
            status_value, sl = choice
            icon_class_value, icl = icon_class_choices[idx]
            style_class_value, scl = style_class_choices[idx]

            instance = get_model("market", "PharmacyInvoiceStatus")(
                pharmacy_invoice=pharmacy_invoice,
                index=idx,
                status=status_value,
                icon_class=icon_class_value,
                style_class=style_class_value,
            )

            lst.append(instance)

        return self.bulk_create(lst)


class PharmacyOfferQuerySet(models.QuerySet):
    pass


class PharmacyOfferManager(models.Manager):
    pass


class SellerInvoiceQuerySet(models.QuerySet):
    def with_seller_profile(self):
        store_profile_subquery = get_model("accounts", "StoreProfile").objects.filter(
            store__pk=OuterRef("seller_object_id")
        )
        pharmacy_profile_subquery = get_model("accounts", "PharmacyProfile").objects.filter(
            pharmacy__pk=OuterRef("seller_object_id")
        )
        return self.annotate(
            seller_data_entry=Case(
                When(
                    seller_content_type__model="store",
                    then=Subquery(store_profile_subquery.values("data_entry__pk")),
                ),
                When(
                    seller_content_type__model="pharmacy",
                    then=Subquery(pharmacy_profile_subquery.values("data_entry__pk")),
                ),
                default=None,
                output_field=models.PositiveBigIntegerField(null=True),
            )
        )

    def with_seller_type(self):
        return self.select_related("seller_content_type").annotate(seller_type=F("seller_content_type__model"))

    def with_seller_invoice_details_count(self):
        return self.annotate(seller_invoice_details_count=Count("seller_invoice_details", distinct=True))

    def with_accepted_total_price(self, user):
        total_price = F("total_price")
        sum_filters = Q(seller_invoice_details__is_accepted=True)

        if user.role == Role.AREA_MANAGER and not user.is_superuser:
            sum_filters &= Q(
                seller_invoice_details__pharmacy_invoice_detail__pharmacy_invoice__pharmacy__pharmacy_profile__area_manager=user
            )
            total_price = models.Sum(
                "seller_invoice_details__total_price",
                filter=Q(
                    seller_invoice_details__pharmacy_invoice_detail__pharmacy_invoice__pharmacy__pharmacy_profile__area_manager=user
                ),
            )

        return self.annotate(
            accepted_total_price=models.Sum(
                "seller_invoice_details__total_price",
                filter=sum_filters,
            ),
            annotated_total_price=total_price,
        )


class SellerInvoiceManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related(
                models.Prefetch("seller_object", queryset=get_user_model().objects.all(), to_attr="related_seller"),
            )
        )


class SellerInvoiceDetailQuerySet(models.QuerySet):
    def with_status(self):
        return self.annotate(
            status=Case(
                When(
                    Q(is_accepted__isnull=True),
                    then=Value("Pending Acceptance"),
                ),
                When(
                    Q(is_accepted=False),
                    then=Value("Rejected"),
                ),
                When(
                    Q(is_recieved__isnull=True),
                    then=Value("Pending recieption"),
                ),
                When(
                    Q(is_recieved=False),
                    then=Value("Not recieved"),
                ),
                default=Value("Recieved"),
                output_field=models.CharField(),
            )
        )

    def with_seller_profile(self):
        store_profile_subquery = get_model("accounts", "StoreProfile").objects.filter(
            store__pk=OuterRef("seller_invoice__seller_object_id")
        )
        pharmacy_profile_subquery = get_model("accounts", "PharmacyProfile").objects.filter(
            pharmacy__pk=OuterRef("seller_invoice__seller_object_id")
        )
        return self.annotate(
            seller_data_entry=Case(
                When(
                    seller_invoice__seller_content_type__model="store",
                    then=Subquery(store_profile_subquery.values("data_entry__pk")),
                ),
                When(
                    seller_invoice__seller_content_type__model="pharmacy",
                    then=Subquery(pharmacy_profile_subquery.values("data_entry__pk")),
                ),
                default=None,
                output_field=models.PositiveBigIntegerField(null=True),
            )
        )

    def with_seller_data(self):
        store_profile_subquery = get_model("accounts", "User").objects.filter(
            pk=OuterRef("seller_invoice__seller_object_id")
        )
        return self.annotate(
            seller_name=Subquery(
                store_profile_subquery.values("name"),
                default=None,
                output_field=models.CharField(),
            ),
            seller_username=Subquery(
                store_profile_subquery.values("username"),
                default=None,
                output_field=models.CharField(),
            ),
        )


class SellerInvoiceDetailManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .with_status()
            .prefetch_related(
                models.Prefetch(
                    "seller_invoice__seller_object", queryset=get_user_model().objects.all(), to_attr="related_seller"
                )
            )
        )


class DeletedSellerInvoiceDetailManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related(
                models.Prefetch(
                    "seller_invoice__seller_object", queryset=get_user_model().objects.all(), to_attr="related_seller"
                )
            )
        )


class PharmacyCartQuerySet(models.QuerySet):
    def with_total_price(self):
        return self.annotate(
            total_price=models.Sum(
                "pharmacy_cart_details__total_price", filter=Q(pharmacy_cart_details__is_offer_removed=False)
            )
        )


class PharmacyCartManager(models.Manager):
    pass


class PharmacyCartDetailQuerySet(models.QuerySet):
    pass


class PharmacyCartDetailManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related(
                models.Prefetch(
                    "offer_object",
                    queryset=get_model("market", "PharmacyOffer").objects.all(),
                    to_attr="related_pharmacy_offer",
                ),
                models.Prefetch(
                    "offer_object",
                    queryset=get_model("market", "StoreOffer").objects.all(),
                    to_attr="related_store_offer",
                ),
            )
        )
