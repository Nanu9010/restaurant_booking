"""
Restaurant and Table models
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
import uuid


class Restaurant(models.Model):
    """
    Restaurant model - linked to User with OWNER role
    """
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='restaurant',
        limit_choices_to={'role': 'OWNER'}
    )

    # Basic Information
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Contact & Location
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)

    # Images
    logo = models.ImageField(upload_to='restaurants/logos/', null=True, blank=True)
    cover_image = models.ImageField(upload_to='restaurants/covers/', null=True, blank=True)

    # QR Code - unique ID for booking URL
    qr_code_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    # Operating Hours
    opening_time = models.TimeField(default='09:00:00')
    closing_time = models.TimeField(default='22:00:00')

    # Status
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Restaurant'
        verbose_name_plural = 'Restaurants'

    def __str__(self):
        return self.name

    @property
    def booking_url(self):
        """Generate the booking page URL"""
        return f"/r/{self.qr_code_id}/book/"

    @property
    def qr_code_url(self):
        """Generate QR code API URL"""
        return f"/api/restaurants/public/{self.qr_code_id}/qr/"


class Table(models.Model):
    """
    Table model - represents physical tables in the restaurant
    """
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='tables'
    )

    # Table identification
    table_number = models.CharField(max_length=50)

    # Capacity
    capacity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Maximum number of people"
    )

    # Optional details
    description = models.CharField(
        max_length=200,
        blank=True,
        help_text="e.g., 'Window seat', 'Outdoor patio'"
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Inactive tables won't appear in bookings"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['table_number']
        verbose_name = 'Table'
        verbose_name_plural = 'Tables'
        unique_together = ['restaurant', 'table_number']

    def __str__(self):
        return f"{self.restaurant.name} - Table {self.table_number}"