from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from .views import category_products, custom_logout  # Import the custom logout function
from django.contrib.auth import views as auth_views
from .views import get_location

urlpatterns = [

    
    path('', views.home, name='home'),
    path('research/', views.research, name='research'),
    path('get-location/', get_location, name='get_location'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),  # Updated to use `user_login`
    path('rules/', views.rules, name='rules'),  # Updated to use `user_login`
    path('reset-password/', views.request_password_reset, name='request_password_reset'),
    path('reset-password-form/', views.reset_password, name='reset_password'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('account/', views.account, name='account'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('add-profile/', views.add_profile_photo, name='add_profile_photo'),
    path('delete-account/', views.delete_account, name='delete_account'),

    path('add_product/', views.add_product, name='add_product'),
    path('category/<int:category_id>/', category_products, name='category_products'),
    path('product/<int:product_id>/like/', views.toggle_like, name='toggle_like'),
    path('myadds/', views.myadds, name='myadds'),
    path('media-gallery/', views.media_gallery, name='media_gallery'),
    path('product/<int:product_id>/', views.details, name='details'),
    path('product/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('product/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('photo/<int:photo_id>/delete/', views.delete_photo, name='delete_photo'),
    path('video/<int:video_id>/delete/', views.delete_video, name='delete_video'),

    path('user/<int:user_id>/', views.user_detail, name='user_detail'),
    path('logout/', custom_logout, name='logout'),  # Logout route
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


