from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from Account.models import Custom_user,Coupon,Cart_item
from django.utils import timezone


@receiver(user_logged_in)
def merge_cart_items(sender, request, user, **kwargs):
    session_key = request.session.get('user_session')
    if not session_key:
        return 
   
    guest_cart=Cart_item.objects.filter(session_key=session_key)
    for item in guest_cart:
        existing_item = Cart_item.objects.filter(user=user, product=item.product,size=item.size).first()
        if existing_item:
            existing_item.quantity += item.quantity
            existing_item.save()
            item.delete()
        else:
            item.user = user
            item.session_key=None
            item.save()
    

@receiver(post_save,sender=Custom_user)
def handle_referral(sender,instance,created,**kwargs):
    if created and instance.referred_by:
        coupon,created=Coupon.objects.get_or_create(user=instance.referred_by,
                        code="FLAT100",defaults={
                                    'discount':100,
                                    'quantity':1,
                                    'valid_from':timezone.now(),
                                    'valid_to':timezone.now()+timezone.timedelta(days=10),
                                    'is_active':True
                                })
        if not created:
            coupon.quantity +=1
            coupon.is_active=True
            coupon.save()
