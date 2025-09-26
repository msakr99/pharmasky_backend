from django.db import models
from django.apps import apps
from decimal import Decimal

get_model = apps.get_model


class PurchaseInvoiceItemManager(models.Manager):
    def create_for_sale_invoice_item(self, invoice, sale_invoice_item, sub_total):
        data = {
            "invoice": invoice,
            "product": sale_invoice_item.product,
            "product_expiry_date": sale_invoice_item.product_expiry_date,
            "operating_number": sale_invoice_item.operating_number,
            "purchase_discount_percentage": sale_invoice_item.purchase_discount_percentage,
            "purchase_price": sale_invoice_item.purchase_price,
            "selling_discount_percentage": sale_invoice_item.selling_discount_percentage,
            "selling_price": sale_invoice_item.selling_price,
            "quantity": sale_invoice_item.quantity,
            "sub_total": sub_total,
            "sale_invoice_item": sale_invoice_item,
        }
        return self.create(**data)


class PurchaseInvoiceDeletedItemManager(models.Manager):
    def create_for_item(self, instance):
        data = {
            "invoice": instance.invoice,
            "product": instance.product,
            "offer": instance.offer,
            "product_expiry_date": instance.product_expiry_date,
            "operating_number": instance.operating_number,
            "purchase_discount_percentage": instance.purchase_discount_percentage,
            "purchase_price": instance.purchase_price,
            "selling_discount_percentage": instance.selling_discount_percentage,
            "selling_price": instance.selling_price,
            "quantity": instance.quantity,
            "remaining_quantity": instance.remaining_quantity,
            "sub_total": instance.sub_total,
            "status": instance.status,
            "sale_invoice_item": instance.sale_invoice_item,
        }
        return self.create(**data)


class SaleInvoiceDeletedItemManager(models.Manager):
    def create_for_item(self, instance):
        data = {
            "invoice": instance.invoice,
            "product": instance.product,
            "offer": instance.offer,
            "product_expiry_date": instance.product_expiry_date,
            "operating_number": instance.operating_number,
            "purchase_discount_percentage": instance.purchase_discount_percentage,
            "purchase_price": instance.purchase_price,
            "selling_discount_percentage": instance.selling_discount_percentage,
            "selling_price": instance.selling_price,
            "quantity": instance.quantity,
            "remaining_quantity": instance.remaining_quantity,
            "sub_total": instance.sub_total,
            "status": instance.status,
        }
        return self.create(**data)
