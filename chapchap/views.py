from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login  # Avoid conflict with custom login
from django.contrib import messages
from chapchap.models import CustomUser
from chat.models import ChatRoom
from .forms import SignupForm

from django.http import JsonResponse
import asyncio

async def async_view(request):
    await asyncio.sleep(2)  # Simulate async task
    return JsonResponse({"message": "Async response!"})

# General Views
from django.shortcuts import render
from .models import Category, Product
from django.db.models import Case, When, Value, IntegerField

def populate_categories():
    categories = [
        {"name": "TRANSPORTS", "image": "https://storage.googleapis.com/a1aa/image/y953sZx9j9rzPV7xYRfj6FOwfYR19FBSt6KlbCwLu1deNVDoA.jpg"},
        {"name": "PROPRIETES", "image": "https://storage.googleapis.com/a1aa/image/3AQpligRBSoiKJRo51yZquNo4VpRAbr90BPfNY0q7eaAnqBUA.jpg"},
        {"name": "MOBILES", "image": "https://storage.googleapis.com/a1aa/image/2eygppWyW3StCqj7cCXyIlTefBm0DLd5c1HnpzuCu8U5NVDoA.jpg"},
        {"name": "ELECTRONIQUES", "image": "https://storage.googleapis.com/a1aa/image/3-Pu1V8Y7VxzAG0p7cfjEMOTcP6APlmbvtTJcIJ6vc8.jpg"},
        {"name": "FASHION", "image": "https://storage.googleapis.com/a1aa/image/VkbZ_vg5ZVbSz_jlYhNtTeLT4axWPvRBCzesiINi6GA.jpg"},
        {"name": "FOURNITURES", "image": "https://storage.googleapis.com/a1aa/image/Lc093OH1ga7a-s3-X1n0CsQNEz_9VPBydajvsh2aYnk.jpg"},
        {"name": "ANIMAUX", "image": "https://images.unsplash.com/photo-1560807707-8cc77767d783"},
    ]
    for category in categories:
        Category.objects.get_or_create(name=category["name"], defaults={"image": category["image"]})



from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.db import models
from django.db.models import Q, FloatField
from geopy.geocoders import GoogleV3, Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import random
from math import radians, cos, sin, asin, sqrt
from .models import Product, Category

def get_location(request):
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')

    if not lat or not lon:
        return JsonResponse({"error": "Latitude and Longitude required"}, status=400)

    try:
        geolocator = GoogleV3(api_key="VOTRE_CLE_API_GOOGLE")
        location = geolocator.reverse((float(lat), float(lon)), exactly_one=True)
        address = location.address if location else "Address not found"
    except (GeocoderTimedOut, GeocoderUnavailable):
        address = "Geocoding service unavailable"
    
    return JsonResponse({"address": address})

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

from django.db.models import F
import random

def home(request):
    user_latitude = request.GET.get('latitude')
    user_longitude = request.GET.get('longitude')

    categories = Category.objects.all()
    products = Product.objects.prefetch_related('photos', 'videos')

    if user_latitude and user_longitude:
        try:
            user_latitude, user_longitude = float(user_latitude), float(user_longitude)
            
            # Get nearest products
            nearest_products = products.exclude(latitude__isnull=True, longitude__isnull=True).annotate(
                distance=models.expressions.RawSQL(
                    """
                    6371 * acos(
                        cos(radians(%s)) * cos(radians(latitude)) * 
                        cos(radians(longitude) - radians(%s)) + 
                        sin(radians(%s)) * sin(radians(latitude))
                    )
                    """, (user_latitude, user_longitude, user_latitude), output_field=FloatField()
                )
            ).order_by('distance')[:50]  # Limit to avoid performance issues

            # Get some random products
            random_products = list(products.order_by('?')[:50])  # Random 50 products

            # Merge and shuffle to mix nearest and random
            products_list = list(nearest_products) + random_products
            random.shuffle(products_list)

        except ValueError:
            products_list = list(products.order_by('?')[:100])  # Random 100 products if no valid coordinates
    else:
        products_list = list(products.order_by('?')[:100])  # Show random products if no location is given

    return render(request, 'home.html', {'products': products_list, 'categories': categories})

def category_products(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    query = request.GET.get('q', '')
    user_latitude = request.GET.get('latitude')
    user_longitude = request.GET.get('longitude')

    products = Product.objects.filter(category=category).prefetch_related('photos', 'videos')

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    if user_latitude and user_longitude:
        try:
            user_latitude, user_longitude = float(user_latitude), float(user_longitude)

            nearest_products = products.exclude(latitude__isnull=True, longitude__isnull=True).annotate(
                distance=models.expressions.RawSQL(
                    """
                    6371 * acos(
                        cos(radians(%s)) * cos(radians(latitude)) * 
                        cos(radians(longitude) - radians(%s)) + 
                        sin(radians(%s)) * sin(radians(latitude))
                    )
                    """, (user_latitude, user_longitude, user_latitude), output_field=FloatField()
                )
            ).order_by('distance')[:50]

            random_products = list(products.order_by('?')[:50])  # Get 50 random category products

            # Mix & shuffle results
            products_list = list(nearest_products) + random_products
            random.shuffle(products_list)

        except ValueError:
            products_list = list(products.order_by('?')[:100])  # If coordinates are invalid, return 100 random category products
    else:
        products_list = list(products.order_by('?')[:100])  # If no location is provided, show random results

    return render(request, 'category_products.html', {'category': category, 'products': products_list, 'query': query})


def research(request):
    query = request.GET.get('q', '')
    user_latitude = request.GET.get('latitude')
    user_longitude = request.GET.get('longitude')
    categories = Category.objects.all()

    products = Product.objects.prefetch_related('photos', 'videos')

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query) | Q(category__name__icontains=query)
        )

    if user_latitude and user_longitude:
        try:
            user_latitude, user_longitude = float(user_latitude), float(user_longitude)

            nearest_products = products.exclude(latitude__isnull=True, longitude__isnull=True).annotate(
                distance=models.expressions.RawSQL(
                    """
                    6371 * acos(
                        cos(radians(%s)) * cos(radians(latitude)) * 
                        cos(radians(longitude) - radians(%s)) + 
                        sin(radians(%s)) * sin(radians(latitude))
                    )
                    """, (user_latitude, user_longitude, user_latitude), output_field=FloatField()
                )
            ).order_by('distance')[:50]

            random_products = list(products.order_by('?')[:50])  # Get 50 random products

            # Mix & shuffle results
            products_list = list(nearest_products) + random_products
            random.shuffle(products_list)

        except ValueError:
            products_list = list(products.order_by('?')[:100])  # If coordinates are invalid, return 100 random products
    else:
        products_list = list(products.order_by('?')[:100])  # If no location is provided, show random results

    return render(request, 'research.html', {'products': products_list, 'categories': categories, 'query': query})

from django.shortcuts import render, get_object_or_404
from .models import Product, Profile

from django.shortcuts import render, get_object_or_404
from .models import Product, Profile

def details(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Get the profile of the product's owner
    profile = Profile.objects.filter(user=product.user).first()

    return render(request, 'details.html', {'product': product, 'profile': profile})




from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model

User = get_user_model()

from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model

User = get_user_model()

User = get_user_model()
from django.shortcuts import render

def room(request, room_name):
    return render(request, 'chat.html', {
        'room_name': room_name
    })

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Product, Profile, Activity
from chat.models import Message, ChatRoom  

@login_required
def user_detail(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    profile = Profile.objects.filter(user=user).first()
    products = Product.objects.filter(user=user)
    activities = Activity.objects.filter(user=user)

    # Fetch chat messages where the user is involved
    sent_messages = Message.objects.filter(sender=user)
    chat_rooms = ChatRoom.objects.filter(users=user)  
    received_messages = Message.objects.filter(chat_room__in=chat_rooms)
    chat_messages = sent_messages | received_messages

    # Search functionality
    query = request.GET.get('q', '')
    if query:
        products = products.filter(name__icontains=query)  # Search in product names
        # from django.contrib.postgres.search import SearchVector
        # products = Product.objects.annotate(search=SearchVector('name', 'description')).filter(search=query)
        activities = activities.filter(action__icontains=query)  # ✅ Assuming 'action' is the correct field
        chat_messages = chat_messages.filter(content__icontains=query)  # Search in chat messages

    return render(request, 'user_detail.html', {
        'user': user,
        'profile': profile,
        'products': products,
        'activities': activities,
        'chat_messages': chat_messages,
        'query': query,  # Pass the search query to keep it in the input field
    })

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Product, Activity, Profile

@login_required
def dashboard(request):
    # Fetch all users, products, activities, and profiles
    users = CustomUser.objects.all()
    products = Product.objects.all()
    activities = Activity.objects.all()
    profiles = Profile.objects.all()

    # Get the search query from the URL (if provided)
    query = request.GET.get('q', '')
    
    # If there's a search query, filter the lists accordingly
    if query:
        # from django.contrib.postgres.search import SearchVector
        # products = Product.objects.annotate(search=SearchVector('name', 'description')).filter(search=query)
        users = users.filter(username__icontains=query)  # Search by username
        products = products.filter(name__icontains=query)  # Search by product name
        activities = activities.filter(description__icontains=query)  # Search by activity description
        profiles = profiles.filter(user__username__icontains=query)  # Search by username in profiles

    return render(request, 'dashboard.html', {
        'users': users,
        'products': products,
        'activities': activities,
        'profiles': profiles,
        'query': query,  # Pass the search query to the template
    })


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Photo, Video, Category

from decimal import Decimal, InvalidOperation

from decimal import Decimal, InvalidOperation

@login_required
def add_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")
        price = request.POST.get('price')
        description = request.POST.get('description')
        photos = request.FILES.getlist('photos')
        videos = request.FILES.getlist('videos')
        category_id = request.POST.get('category')

        # Validate required fields
        if not name or not phone or not latitude or not longitude or not price or not description or not category_id:
            messages.error(request, "All fields are required!")
            return redirect('add_product')

        try:
            # Ensure price is properly formatted (replace commas with dots if necessary)
            price = Decimal(price.replace(",", "."))  
        except (InvalidOperation, AttributeError):
            messages.error(request, "Invalid price format! Please enter a valid number.")
            return redirect('add_product')

        category = Category.objects.get(id=category_id)
        location = f"{latitude}, {longitude}"  # Store lat/lon as location

        product = Product.objects.create(
            user=request.user,
            name=name,
            phone=phone,
            location=location,
            latitude=latitude,
            longitude=longitude,
            price=price,
            description=description,
            category=category
        )

        for photo in photos:
            Photo.objects.create(product=product, image=photo)
        for video in videos:
            Video.objects.create(product=product, video=video)

        messages.success(request, "Produit ajouter avec success!")
        return redirect('/')

    categories = Category.objects.all()
    return render(request, 'add_product.html', {'categories': categories})





from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Product

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Profile  # Import Profile model

@login_required
def account(request):
    # Get the search query from the URL (if present)
    query = request.GET.get('q', '')  # Default is an empty string if no query is provided
    
    # Fetch products for the logged-in user
    products = Product.objects.filter(user=request.user).prefetch_related('photos', 'videos')
    
    # If there's a search query, filter products by name
    if query:
        # from django.contrib.postgres.search import SearchVector
        # products = Product.objects.annotate(search=SearchVector('name', 'description')).filter(search=query)
        products = products.filter(name__icontains=query)  # Case-insensitive search for product names

    # Ensure the profile exists
    profile, created = Profile.objects.get_or_create(user=request.user)

    return render(request, 'account.html', {
        'products': products,
        'user': request.user,
        'profile': profile,
        'query': query  # Pass the query back to the template to maintain the search term in the input field
    })

from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def delete_account(request):
    if request.method == "POST":
        user = request.user
        user.delete()  # Deletes the user from the database
        logout(request)  # Logs out the user
        messages.success(request, "Votre compte a été supprimé avec succès.")
        return redirect('home')  # Redirect to the home page (change if needed)
    
    return redirect('profile')  # Redirect to profile page if accessed without POST


from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re

# List of common disposable email domains
DISPOSABLE_EMAIL_DOMAINS = [
    "tempmail.com", "10minutemail.com", "fakeinbox.com",
    "mailinator.com", "guerrillamail.com", "yopmail.com"
]

def is_valid_email(email):
    """ Check if email is valid and not disposable. """
    try:
        validate_email(email)  # Django's built-in email validator
        domain = email.split('@')[-1]
        if domain in DISPOSABLE_EMAIL_DOMAINS:
            return False  # Reject disposable email
        return True
    except ValidationError:
        return False

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        email = request.POST.get('email').strip()
        password = request.POST.get('password').strip()

        # Check if the email is valid
        if not is_valid_email(email):
            messages.error(request, "Please enter a valid, non-disposable email.")
            return redirect('signup')

        # Prevent duplicate email
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already in use. Try another one.")
            return redirect('signup')

        # Prevent duplicate username
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken. Choose another one.")
            return redirect('signup')

        # Create and login the user
        user = User.objects.create_user(username=username, email=email, password=password)
        auth_login(request, user)
        messages.success(request, "Enregister avec success! Bienvenu.")
        return redirect('add_product')  # Redirect to add product page

    return render(request, 'signup.html')

def user_login(request):  # Renamed to avoid conflict
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Log the user in
            auth_login(request, user)
            return redirect('add_product')  # Replace 'add_product' with your desired redirect URL
        else:
            # Display an error message if authentication fails
            messages.error(request, "Invalid username or password")
    
    return render(request, 'login.html')

def rules(request):
    return render(request, 'rules.html')

from django.shortcuts import render
from .models import Product

def media_gallery(request):
    products = Product.objects.prefetch_related('photos', 'videos').all()
    return render(request, 'media-gallery.html', {'products': products})

from django.shortcuts import get_object_or_404, render
from .models import Product

from django.contrib.auth.decorators import login_required

@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    return render(request, 'product_detail.html', {
        'product': product,
        'request_user': request.user  # Pass request.user explicitly
    })


from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product

@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, user=request.user)

    if request.method == 'POST':
        # Update basic product fields
        product.name = request.POST.get('name')
        product.phone = request.POST.get('phone')
        product.location = request.POST.get('location')
        product.price = request.POST.get('price')
        product.description = request.POST.get('description')
        
        # Handle new images
        new_photos = request.FILES.getlist('photos')
        for photo in new_photos:
            product.photos.create(image=photo)
        
        # Handle new videos
        new_videos = request.FILES.getlist('videos')
        for video in new_videos:
            product.videos.create(video=video)
        
        # Save changes
        if not all([product.name, product.phone, product.location, product.price, product.description]):
            messages.error(request, "All fields are required!")
        else:
            product.save()
            messages.success(request, "Produit modifier avec success!")
            return redirect('home')

    return render(request, 'edit_product.html', {'product': product})

from django.shortcuts import render
from django.urls import reverse
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from .models import PasswordResetToken

User = get_user_model()

def request_password_reset(request):
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            token_obj = PasswordResetToken.objects.create(user=user)  # UUID is auto-generated
            reset_url = request.build_absolute_uri(reverse('reset_password') + f'?token={token_obj.token}')
            send_mail(
                'Password Reset Request',
                f'Click the link to reset your password: {reset_url}',
                'diawaracheicktidiani@gmail.com',
                [email],
                fail_silently=False,
            )
            messages.success(request, "A password reset link has been sent to your email.")
        except User.DoesNotExist:
            messages.error(request, "No account found with this email.")
    
    return render(request, 'password_reset_request.html')


from django.contrib.auth.hashers import make_password

def reset_password(request):
    token = request.GET.get('token')
    if not token:
        messages.error(request, "Invalid or expired reset link.")
        return redirect('login')

    try:
        reset_entry = PasswordResetToken.objects.get(token=token)
    except PasswordResetToken.DoesNotExist:
        messages.error(request, "Invalid or expired reset link.")
        return redirect('login')

    if request.method == "POST":
        new_password = request.POST.get('password')
        reset_entry.user.password = make_password(new_password)
        reset_entry.user.save()
        reset_entry.delete()
        messages.success(request, "Mots de passe supprimer avec success.")
        return redirect('login')

    return render(request, 'password_reset_form.html', {'token': token})


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile

@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        profile_picture = request.FILES.get("profile_picture")  # Get uploaded image

        # Update user info
        request.user.username = username
        request.user.email = email
        request.user.save()

        # Update or add profile picture
        if profile_picture:
            profile.profile_picture = profile_picture
            profile.save()

        return redirect('account')  # Redirect back to account page

    return render(request, 'edit_profile.html', {'user': request.user, 'profile': profile})


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile

@login_required
def add_profile_photo(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        profile_picture = request.FILES.get("profile_picture")  # Get uploaded image

        if profile_picture:
            profile.profile_picture = profile_picture
            profile.save()

        return redirect('account')  # Redirect back to profile page

    return render(request, 'add_profile_photo.html', {'profile': profile})


@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, user=request.user)  # Ensure the user owns the product
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Produit supprimer avec success!")
        return redirect('account')
    return render(request, 'confirm_delete.html', {'product': product})

from django.contrib.auth import logout
from django.shortcuts import redirect

def custom_logout(request):
    logout(request)
    return redirect('login')  # Redirect to login page after logout


@login_required
def delete_photo(request, photo_id):
    # Fetch the photo object while ensuring it belongs to the logged-in user
    photo = get_object_or_404(Photo, id=photo_id, product__user=request.user)
    photo.delete()  # Delete the photo
    messages.success(request, "Photo supprimer avec success!")
    return redirect(request.META.get('HTTP_REFERER', 'edit_product'))

@login_required
def delete_video(request, video_id):
   # Fetch the photo object while ensuring it belongs to the logged-in user
    video = get_object_or_404(Video, id=video_id, product__user=request.user)
    video.delete()  # Delete the photo
    messages.success(request, "video supprimer avec success!")
    return redirect(request.META.get('HTTP_REFERER', 'edit_product'))

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import Product

@login_required
def toggle_like(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user in product.liked_by.all():
        product.liked_by.remove(request.user)
    else:
        product.liked_by.add(request.user)
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def myadds(request):
    liked_products = request.user.liked_products.all()
    return render(request, 'myadds.html', {'liked_products': liked_products})






