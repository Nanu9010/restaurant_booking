"""
Core utilities for the platform
"""

import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
import base64


def generate_qr_code(data, size=10, border=4):
    """
    Generate QR code image from data

    Args:
        data: URL or text to encode
        size: Size of the QR code
        border: Border size

    Returns:
        Base64 encoded image string
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to base64 for easy transmission
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    return base64.b64encode(buffer.getvalue()).decode()


def generate_restaurant_qr(restaurant):
    """
    Generate QR code for a restaurant's booking page

    Args:
        restaurant: Restaurant model instance

    Returns:
        Base64 encoded QR code image
    """
    # In production, use full domain
    # For now, use relative path
    booking_url = f"http://localhost:8000/r/{restaurant.qr_code_id}/book"
    return generate_qr_code(booking_url)


def format_time_slot(time_obj):
    """
    Format time object to readable string

    Args:
        time_obj: datetime.time object

    Returns:
        Formatted string like "02:30 PM"
    """
    return time_obj.strftime("%I:%M %p")


def generate_time_slots(start_time, end_time, interval_minutes=30):
    """
    Generate available time slots between start and end time

    Args:
        start_time: Opening time
        end_time: Closing time
        interval_minutes: Interval between slots

    Returns:
        List of time objects
    """
    from datetime import datetime, timedelta

    slots = []
    current = datetime.combine(datetime.today(), start_time)
    end = datetime.combine(datetime.today(), end_time)

    while current < end:
        slots.append(current.time())
        current += timedelta(minutes=interval_minutes)

    return slots
