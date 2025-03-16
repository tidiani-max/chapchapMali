from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class CustomUser(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    image = models.URLField()  # Store the image URL for the category

    def __str__(self):
        return self.name
    
from geopy.geocoders import Nominatim
from django.db import models
from django.conf import settings

class Product(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    location = models.CharField(max_length=255)  # Selected country, city, and neighborhood
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    liked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_products',
        blank=True
    )
    def get_address(self):
        """Convert latitude & longitude to a short, readable address."""
        if self.latitude and self.longitude:
            geolocator = Nominatim(user_agent="my_django_app")
            location = geolocator.reverse((self.latitude, self.longitude), language="en")
            if location:
                address_parts = location.raw.get("address", {})
                city = address_parts.get("city", address_parts.get("town", address_parts.get("village", "")))
                region = address_parts.get("state", "")
                plus_code = address_parts.get("postcode", "")  # Sometimes contains the plus code
                return f"{plus_code} {city}, {region}".strip()
        return "Unknown Location"
    
    # New Fields for Ranking
    views = models.PositiveIntegerField(default=0)  # Track how many times product is viewed
    clicks = models.PositiveIntegerField(default=0)  # Track user interactions (e.g., clicks, inquiries)
    is_sponsored = models.BooleanField(default=False)  # Flag for sponsored products
    priority_score = models.FloatField(default=0.0)  # Store computed ranking score

    def __str__(self):
        return self.name

from django.utils.crypto import get_random_string


class Activity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} on {self.timestamp}"


class Photo(models.Model):
    product = models.ForeignKey(Product, related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_photos/')

class Video(models.Model):
    product = models.ForeignKey(Product, related_name='videos', on_delete=models.CASCADE)
    video = models.FileField(upload_to='product_videos/')

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


from django.db import models
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime, timedelta

class PasswordResetToken(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        expiration_time = self.created_at + timedelta(hours=1)  # Token valid for 1 hour
        return datetime.now() < expiration_time

    def __str__(self):
        return f"Reset Token for {self.user.username}"


