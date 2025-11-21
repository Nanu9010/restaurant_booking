"""
Enhanced Booking model with customer tracking
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone
from datetime import timedelta
from restaurants.models import Restaurant, Table


class Booking(models.Model):
    """
    Booking model - represents a table reservation
    Can be linked to a customer account or guest booking
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('no_show', 'No Show'),
    ]

    # Relationships
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    table = models.ForeignKey(
        Table,
        on_delete=models.CASCADE,
        related_name='bookings'
    )

    # Customer (optional - for registered customers)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='bookings',
        null=True,
        blank=True,
        limit_choices_to={'role': 'CUSTOMER'}
    )

    # Guest Information (for non-registered users)
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)

    # Booking Details
    party_size = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Number of people"
    )

    booking_date = models.DateField()
    booking_time = models.TimeField()

    duration_hours = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=2.0,
        help_text="Booking duration in hours"
    )

    special_requests = models.TextField(blank=True)

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # Confirmation tracking
    confirmation_sent = models.BooleanField(default=False)
    confirmation_sent_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-booking_date', '-booking_time']
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        indexes = [
            models.Index(fields=['table', 'booking_date', 'status']),
            models.Index(fields=['restaurant', 'booking_date']),
            models.Index(fields=['customer', 'booking_date']),
        ]

    def __str__(self):
        return f"{self.customer_name} - {self.restaurant.name} - {self.booking_date}"

    @property
    def booking_datetime(self):
        """Combine date and time"""
        return timezone.make_aware(
            timezone.datetime.combine(self.booking_date, self.booking_time)
        )

    @property
    def end_datetime(self):
        """Calculate end time"""
        return self.booking_datetime + timedelta(hours=float(self.duration_hours))

    @property
    def is_past(self):
        """Check if booking is in the past"""
        return self.end_datetime < timezone.now()

    @property
    def is_today(self):
        """Check if booking is today"""
        return self.booking_date == timezone.now().date()

    @property
    def is_upcoming(self):
        """Check if booking is upcoming"""
        return self.booking_datetime > timezone.now()

    def can_cancel(self):
        """Check if booking can be cancelled"""
        return self.status in ['pending', 'confirmed'] and not self.is_past

    def cancel(self):
        """Cancel the booking"""
        if self.can_cancel():
            self.status = 'cancelled'
            self.save()
            return True
        return False

    def confirm(self):
        """Confirm the booking"""
        if self.status == 'pending':
            self.status = 'confirmed'
            self.save()
            return True
        return False