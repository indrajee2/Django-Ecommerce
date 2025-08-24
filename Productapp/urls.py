from django.urls import path
from Productapp import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    #user 
    path('',views.home_view,name="home"),
    path('upload-product/',views.product_upload,name='upload'),
    path('product_detail/<int:pk>/',views.product_detail,name='product_detail'),
    path('add-to-cart/',views.add_to_cart_product,name="add_to_cart"),
    path('cart-list/',views.product_cart_list,name="cart_list"),
    path('delete/',views.delete_item,name="delete_item"),
    path('payment/',views.payment,name="payment"),
    path('webhook/',views.my_webhook_view,name="webhook"),

    # path('direct-buy/',views.direct_buy,name="buy"),
    path('address/',views.shippment_address,name='address'),
    path('address_select/',views.address_select,name='address_select'),
    path('orders/',views.order_history,name="orders"),
    path('success/',views.success_view,name="success"),
    path('transaction/',views.transaction_history,name='transaction'),
    path('cancel/',views.cancel_view,name="cancel"),
    path('coupon/',views.apply_coupon,name='coupon'),
    path('remove-coupon/',views.remove_coupon,name='remove_coupon'),
    path('comment/',views.comment_on_product,name='comment'),
    path('comment-remove/',views.remove_comment,name='comment_remove'),
    path('like-comment/',views.comment_likes_view,name='like_comment'),
    path('order-details/<int:pk>/',views.order_details,name="order_details"),
    path('watchlist/',views.add_watchlist,name='watchlist'),
    path('show-watchlist/',views.show_watchlist,name="show_watchlist"),
    path('paymenthandler/', views.razorpay_gateway, name='razorpay_handler'),
    path('varify-payment/',views.verify_razorpay,name="verify_razorpay"),

]+  static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 