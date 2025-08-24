from django.contrib import admin
from .models import Custom_user,Send_email_otp,Product,Cart_item,Payment_model,OrderItems,Address,Coupon,Comment,Size,Watchlist
# Register your models here.
admin.site.register(Custom_user)
admin.site.register(Send_email_otp)

class List_Product(admin.ModelAdmin):
    list_display=['id','name','price','description','image']
    
class cart_item_list(admin.ModelAdmin):
    list_display=['id','user','product','quantity','coupon']
    
class order_item_list(admin.ModelAdmin):
    list_display=['id','user','product','quantity','payment']
    
class Payment_list(admin.ModelAdmin):
    list_display=['id',"user",'transaction_id','total_amount','status']
    
class Address_list(admin.ModelAdmin):
    list_display=['id',"user",'state','city','pincode','address']

class Coupon_list(admin.ModelAdmin):
    list_display=['code','discount','is_active','is_used','valid_to']
class Comment_list(admin.ModelAdmin):
    list_display=['user','product','content','comment_post']


admin.site.register(Product,List_Product)
admin.site.register(Size)
admin.site.register(Watchlist)
admin.site.register(Cart_item,cart_item_list)
admin.site.register(Payment_model,Payment_list)
admin.site.register(OrderItems,order_item_list)
admin.site.register(Address,Address_list)
admin.site.register(Coupon,Coupon_list)
admin.site.register(Comment,Comment_list)
