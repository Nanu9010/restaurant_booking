"""
Core models - Custom User model with role-based authentication
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model with role-based access
    Roles: ADMIN, OWNER, CUSTOMER
    """

    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('OWNER', 'Restaurant Owner'),
        ('CUSTOMER', 'Customer'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='CUSTOMER'
    )

    phone = models.CharField(max_length=20, blank=True)

    # Profile fields
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == 'ADMIN'

    @property
    def is_owner(self):
        return self.role == 'OWNER'

    @property
    def is_customer(self):
        return self.role == 'CUSTOMER'

    def has_restaurant(self):
        """Check if owner has a restaurant"""
        if self.is_owner:
            return hasattr(self, 'restaurant')
        return False