"""
Signals for the offers app.

Automatically send notifications when offers are created or updated.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from offers.models import Offer
from notifications.models import Notification
from market.models import PharmacyProductWishList
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Offer)
def notify_wishlist_pharmacies_on_offer_created(sender, instance, created, **kwargs):
    """
    إرسال إشعار للصيدليات التي أضافت المنتج في wishlist عند توفر عرض جديد.
    """
    if created:
        try:
            # البحث عن الصيدليات التي أضافت هذا المنتج في wishlist
            wishlist_items = PharmacyProductWishList.objects.filter(
                product=instance.product
            ).select_related('pharmacy')
            
            if not wishlist_items.exists():
                return
            
            # إنشاء إشعارات جماعية
            notifications = []
            for wishlist_item in wishlist_items:
                notifications.append(
                    Notification(
                        user=wishlist_item.pharmacy,
                        title="✨ منتج متوفر من قائمة الرغبات!",
                        message=f"المنتج '{instance.product.name}' أصبح متوفراً الآن بخصم {instance.selling_discount_percentage}% وسعر {instance.selling_price} جنيه",
                        extra={
                            "type": "wishlist_product_available",
                            "product_id": instance.product.pk,
                            "product_name": instance.product.name,
                            "offer_id": instance.pk,
                            "seller_id": instance.user.pk,
                            "seller_name": instance.user.name,
                            "discount": str(instance.selling_discount_percentage),
                            "price": str(instance.selling_price),
                            "available_amount": instance.remaining_amount,
                        },
                        image_url=""
                    )
                )
            
            if notifications:
                Notification.objects.bulk_create(notifications)
                logger.info(
                    f"Wishlist notifications sent to {len(notifications)} pharmacies "
                    f"for product {instance.product.name} (offer #{instance.pk})"
                )
                
        except Exception as e:
            logger.error(f"Failed to send wishlist notifications for offer #{instance.pk}: {str(e)}")

