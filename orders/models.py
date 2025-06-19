from django.db import models 
from django.utils import timezone
import uuid
from django.conf import settings


class Table(models.Model):
    number = models.PositiveIntegerField(unique=True)
    qr_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    def __str__(self):
        return f"Table {self.number}"

class Order(models.Model):
    ...
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders_created'
    )
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('preparing', 'Preparing'),
        ('served', 'Served'),
        ('delayed', 'Delayed'),
    ]

    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='orders')
    items = models.TextField(help_text="Comma-separated list of items")
    timestamp = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Order #{self.id} - Table {self.table.number}"

    @property
    def delay_status(self):
        """Returns a color code based on prep time delay logic."""
        delta = timezone.now() - self.timestamp
        minutes = delta.total_seconds() / 60
        if minutes < 5:
            return 'green'
        elif minutes < 10:
            return 'yellow'
        else:
            return 'red'