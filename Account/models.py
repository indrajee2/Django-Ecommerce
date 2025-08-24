import uuid
import logging
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager

logger = logging.getLogger(__name__)

class Custom_manager(BaseUserManager):
    def create_user(self, username, email, password=None, **kwargs):
        if not username:
            raise ValueError("Please provide a username.")
        if not email:
            raise ValueError("Please provide an email address.")
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password=None):
        user = self.create_user(username=username, email=self.normalize_email(email), password=password)
        user.is_active = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

class Custom_user(AbstractBaseUser):
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)  # Changed to CharField
    first_name = models.CharField(max_length=30, blank=True)
    middle_name = models.CharField(max_length=20, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    user_image = models.ImageField(upload_to='user_images/', blank=True, null=True)
    stripe_customer_id=models.CharField(max_length=200,unique=True,blank=True,null=True) #for store the customer id
    referral_code = models.CharField(max_length=6, unique=True, blank=True)
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='referrals', null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    joined_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']

    objects = Custom_manager()

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return self.is_superuser

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = str(uuid.uuid4()).replace('-', '')[:6].upper()
        super().save(*args, **kwargs)  # Call the parent class's save method

    def __str__(self):
        return f"{self.username}"


class Send_email_otp(models.Model):
    email=models.EmailField(max_length=50)
    otp=models.CharField(max_length=6)
    created_at=models.DateTimeField(auto_now_add=True)
    objects=models.Manager()
    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=5)

    def __str__(self):
        return self.email


class Size(models.Model):
    name=models.CharField(max_length=30,unique=True)
    def __str__(self):
        return self.name
    
class Product(models.Model):
    name=models.CharField(max_length=50)
    size=models.ManyToManyField(Size,blank=True,related_name='size')
    price=models.DecimalField(max_digits=10,decimal_places=2)
    discounted_price=models.DecimalField(max_digits=10,decimal_places=2)
    description=models.TextField()
    image=models.ImageField(upload_to="products/")
    objects=models.Manager()
    def __str__(self):
        return f"{self.name}"
    def get_discount_price(self):
        marked_price=self.price - self.discounted_price
        discount_percentage=(marked_price/self.price)* 100
        return round(discount_percentage,2)

class Coupon(models.Model):
    user=models.ForeignKey(Custom_user,on_delete=models.CASCADE,blank=True,null=True)
    code = models.CharField(max_length=50)
    quantity=models.PositiveIntegerField()
    discount = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(500)],help_text='Amount value (0 to 500)')
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_to=models.DateTimeField()
    is_used = models.BooleanField(default=False)
    objects=models.Manager()

    def __str__(self):
        return self.code
    
    def used(self):
        if self.quantity>0:
            self.quantity -=1
            if self.quantity==0:
                self.is_active=False
            self.save()


class Cart_item(models.Model):
    user=models.ForeignKey(Custom_user,on_delete=models.CASCADE, blank=True, null=True)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField()
    session_key=models.CharField(max_length=100,blank=True,null=True)
    size=models.ForeignKey(Size,on_delete=models.CASCADE)
    coupon=models.ForeignKey(Coupon,on_delete=models.SET_NULL ,blank=True,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    objects=models.Manager()
    class meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'product','size'], name='unique_cart_items'),
        ]

    def __str__(self):
        return f"{self.user}  {self.product}"

class Payment_model(models.Model):
    payment_status=[("pending","PANDING"),('completed','COMPLETED')]
    user=models.ForeignKey(Custom_user,on_delete=models.CASCADE)
    transaction_id=models.CharField(max_length=200)
    total_amount=models.FloatField()
    status=models.CharField(max_length=50, choices=payment_status)
    payment_date=models.DateTimeField(auto_now_add=True)
    objects=models.Manager()
    def __str__(self):
        return f"{self.user} -- {self.status}"


class Address(models.Model):
    user=models.ForeignKey(Custom_user,on_delete=models.CASCADE)
    state=models.CharField(max_length=100)
    city=models.CharField(max_length=100)
    pincode=models.IntegerField()
    landmark=models.CharField(max_length=100,blank=True,null=True)
    address=models.CharField(max_length=200)
    phone=models.IntegerField()
    objects=models.Manager()

    def __str__(self):
        return f"{self.address}-state-{self.state}-city-{self.city}."

class OrderItems(models.Model):
    order_status=[
        ('ORDER PLACED','ORDER PLACED'),
        ('PACKED','PACKED'),
        ('SHIPPED','SHIPPED'),
        ('DELIVERED','DELIVERED')
    ]
    user=models.ForeignKey(Custom_user ,on_delete=models.CASCADE)
    payment=models.ForeignKey(Payment_model,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField()
    address=models.ForeignKey(Address,on_delete=models.CASCADE)
    size=models.CharField(max_length=5,blank=True)
    coupon_price=models.DecimalField(max_digits=10,decimal_places=2)
    status=models.CharField(max_length=100,choices=order_status,default="ORDER PLACED")
    order_date=models.DateTimeField(auto_now_add=True)
    objects=models.Manager()

class Comment(models.Model):
    content=models.TextField(verbose_name="Comment")
    user=models.ForeignKey(Custom_user,on_delete=models.CASCADE,related_name="commented_by")
    like=models.ManyToManyField(Custom_user,related_name='comment_like',blank=True)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    comment_post=models.DateTimeField(auto_now_add=True)
    objects=models.Manager()

class Watchlist(models.Model):
    user=models.ForeignKey(Custom_user,on_delete=models.CASCADE,related_name='user')
    product=models.ForeignKey(Product,on_delete= models.CASCADE,related_name='product')
    added_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username} product name- {self.product.name}"