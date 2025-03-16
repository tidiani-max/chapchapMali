from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Product, Photo, Video, Profile

# Register CustomUser
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    pass

# Register Profile
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile_picture')  # Show user and profile picture in the admin panel
    search_fields = ('user__username',)  # Allow searching by username

# Register Product with inline Photos & Videos
class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1  # Number of empty forms to display

class VideoInline(admin.TabularInline):
    model = Video
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'price', 'location','latitude','longitude','date_posted')  # Fields to display in the product list
    search_fields = ('name', 'location', 'user__username')  # Search by name, location, and user
    list_filter = ('location',)  # Filter by location
    inlines = [PhotoInline, VideoInline]  # Include photos and videos inline

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('product', 'image')  # Display the product and image file
    search_fields = ('product__name',)  # Allow searching by product name

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('product', 'video')  # Display the product and video file
    search_fields = ('product__name',)  # Allow searching by product name

from .models import Activity

class ActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp')  # Fields to display in the list
    search_fields = ('user__username', 'action')  # Make 'user' and 'action' searchable
    list_filter = ('timestamp',)  # Filter by timestamp

admin.site.register(Activity, ActivityAdmin)

from django.contrib import admin
from .models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'image')  # Display category name and image URL
    search_fields = ('name',)  # Add search functionality by name

# If you have other models to register, do it here as well


from django.contrib import admin
from .models import PasswordResetToken

@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at')
    search_fields = ('user__email', 'token')
    list_filter = ('created_at',)

