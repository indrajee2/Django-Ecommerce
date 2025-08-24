from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    #user 
    path('register/',views.user_register_view,name='register'),
    path('varify_otp/',views.varification_view,name="verify"),
    path('login/',views.user_login_view,name="login"),
    path('logout/',views.logout_view,name="logout"),
    path('forget-password/',views.forget_password_view,name="forget"),
    path('varify-forget-password/<str:otp>/',views.forget_password,name='forget_link'),
    path('Change_Password/',views.change_password,name="Change_Password"),
    path('profile/',views.user_profile,name='profile'),
    path('profile-edit/',views.user_profile_update,name='profie_edit'),
    path('profile-image-change/',views.profile_image_change,name='profile_image'),
    #login through google
    path('google/login/',views.google_login,name='google_login'),
    path('google/callback/',views.google_callback,name="google_callback"),

    #product
    # path('',views.home_view,name="home"),
    # path('upload-product/',views.product_upload,name='upload'),
    
    # path('add-to-cart/',views.add_to_cart_product,name="add_to_cart"),
    # path('cart-list/',views.product_cart_list,name="cart_list"),
    
   



] +  static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)