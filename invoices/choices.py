from http.client import ACCEPTED
from django.db import models


class PurchaseInvoiceStatusChoice(models.TextChoices):
    PLACED = "placed", "Placed"
    LOCKED = "locked", "Locked"
    CLOSED = "closed", "Closed"


class PurchaseInvoiceItemStatusChoice(models.TextChoices):
    PLACED = "placed", "Placed"
    ACCEPTED = "accepted", "Accepted"
    REJECTED = "rejected", "Rejected"
    RECEIVED = "received", "Received"
    NOT_RECEIVED = "not_received", "Not Received"


class SaleInvoiceStatusChoice(models.TextChoices):
    PLACED = "placed", "Placed"
    CLOSED = "closed", "Closed"


class SaleInvoiceItemStatusChoice(models.TextChoices):
    PLACED = "placed", "Placed"
    ACCEPTED = "accepted", "Accepted"
    REJECTED = "rejected", "Rejected"
    RECEIVED = "received", "Received"
    NOT_RECEIVED = "not_received", "Not Received"


class SaleReturnInvoiceStatusChoice(models.TextChoices):
    PLACED = "placed", "Placed"
    CLOSED = "closed", "Closed"


class PurchaseReturnInvoiceStatusChoice(models.TextChoices):
    PLACED = "placed", "Placed"
    CLOSED = "closed", "Closed"
