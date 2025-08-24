#pylint:disable=C0303
import stripe.error
import stripe
import razorpay
import json
from django.utils import timezone
from django.shortcuts import render,redirect,get_object_or_404
from django.http import JsonResponse,HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.contrib import messages
from Account import message,forms,models


# Create your views here.
def home_view(request):
    """this function is used to show the product."""
    try:
        product=models.Product.objects.order_by('?').all()
    except models.Product.DoesNotExist: #pylint:disable=no-member
        messages.warning(request,message.error_no_product)
        return redirect('home')
    paginator=Paginator(product,6)
    page_number=request.GET.get('page')
    page_obj=paginator.get_page(page_number)
    return render(request,'home.html',{"product":page_obj})

@login_required(login_url='login')
def product_upload(request):
    """ this function allow only admin to add the product"""
    if request.method=="POST":
        form=forms.ProductUploadForm(request.POST,request.FILES)
        if form.is_valid():
            if request.user.is_superuser:
                form.save()
                messages.success(request,message.success_product_upload)
                return redirect('upload')
            messages.warning(request,message.error_product_permission)
            return redirect('upload')
    form=forms.ProductUploadForm()
    return render(request,"upload_product.html",{'form':form})


def product_detail(request, pk):
    """ This function shows products on the home page """
    try:
        data = models.Product.objects.get(pk=pk)
        exclude_product=models.Product.objects.order_by('?').exclude(pk=pk)
    except models.Product.DoesNotExist:  # pylint:disable=no-member
        messages.error(request, message.error_no_product)    
        return redirect('home')
    watchlist=""
    if request.user.is_authenticated:
        try:
            cart= models.Cart_item.objects.filter(user=request.user,product=data)
        except models.Cart_item.DoesNotExist:
            messages.error(request,message.error_no_cartitem)
            return redirect('product_detail',pk)
        try:
            watchlist=models.Watchlist.objects.filter(user=request.user,product=data)
        except models.Watchlist.DoesNotExist:
            messages.error(request,message.error_watchlist_item)
            return redirect('product_detail',pk)
    else:
        try:
            cart= models.Cart_item.objects.filter(user__isnull=True,product=data)
        except models.Cart_item.DoesNotExist:
            messages.error(request,message.error_no_cartitem)
            return redirect('product_detail',pk)
    comments = models.Comment.objects.filter(product=data).order_by('-comment_post')
    paginator=Paginator(exclude_product,2)
    page_number=request.GET.get('page')
    page_obj=paginator.get_page(page_number)
    print(cart)
    context = {
        "item": data,
        'comment':comments,
        'page_obj':page_obj,
        'cart':cart,
        'watchlist_items':watchlist

    }
    return render(request, "product_detail.html", context)

@csrf_exempt
def add_to_cart_product(request):
    """This function allows users to add the item to the cart."""
    if request.method == "POST":
        item_id = request.POST.get('item')
        quantity = int(request.POST.get('quantity', 1)) 
        size = request.POST.get('size')
        size_ins = get_object_or_404(models.Size, pk=size)
        product = models.Product.objects.get(id=item_id)
        if request.user.is_authenticated:
            user = request.user
            cart_item, created = models.Cart_item.objects.get_or_create(
                user=user,
                product=product,
                size=size_ins,
                defaults={'quantity': quantity}
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            return JsonResponse({'status': 'success', 'message': 'Item added to cart (user)'})
        
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            cart_item, created = models.Cart_item.objects.get_or_create(
                session_key=session_key,
                product=product,
                size=size_ins,
                user=None,
                defaults={'quantity': quantity}
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save()

    return render(request, "product_detail.html")

def product_cart_list(request):
    """This function is used to show the cart_items to guest and authenticated user."""
    session_key = request.session.session_key
    products = []
    final_price = []
    is_coupon=''
    coupon_price=0
    if request.user.is_authenticated:
        cart_item = models.Cart_item.objects.filter(user=request.user)
        for i in cart_item:
            if i.coupon:
                is_coupon=i.coupon.code
                coupon_price=i.coupon.discount
        address=models.Address.objects.filter(user=request.user)
    else:
        cart_item = models.Cart_item.objects.filter(session_key=session_key, user__isnull=True)
        address=''
    for item in cart_item:
        total_price = (item.product.discounted_price * item.quantity)
        final_price.append(total_price)
        products.append({
            "id": item.product.id,
            'image': item.product.image.url,
            "name": item.product.name,
            "price": item.product.price,
            "discounted_price": item.product.discounted_price,
            "size_id":item.size.id,
            "size": item.size.name,
            'total_price': total_price,
            "quantity": item.quantity,
        })
    print("hello",is_coupon)
    context = {
        'product': products,
        'final_price': (sum(final_price))-coupon_price,
        'is_coupon':is_coupon,
        'address':address,
    }
    return render(request, 'cart_items.html', context)

def delete_item(request):
    """This function allows both users to delete the item from the cart."""
    if request.method == "POST":
        itemid = request.POST.get('itemid')
        size_id = request.POST.get('size_id')
        session_key = request.session.session_key
        if request.user.is_authenticated:
            size_instance = get_object_or_404(models.Size, pk=size_id)
            try:
                product = models.Product.objects.get(pk=itemid, size=size_instance)
            except models.Product.DoesNotExist:
                messages.error(request, "Product not found.")
                return redirect('cart_list')
            cart_item = models.Cart_item.objects.filter(user=request.user,
                                    product=product, size=size_instance).first()
            if cart_item:
                cart_item.delete()
                return JsonResponse({"success":True,"msg": message.success_cartitem_delete})
            else:
                return JsonResponse({'error':message.error_no_cartitem})
        else:
            # For guest users
            cart_item = models.Cart_item.objects.filter(session_key=session_key,
                                        product__id=itemid, size__id=size_id).first()
            if cart_item:
                cart_item.delete()
                return JsonResponse({"success":True,"msg": message.success_cartitem_delete})
            else:
                return JsonResponse({'error':message.error_no_cartitem})

    return redirect('cart_list')

stripe.api_key=settings.STRIPE_SECRET_KEY

def get_or_create_stripe_customer(user):
    """this function is used to create the customer id and 
    store in the user model and if user has already customer id then 
    this function retrive the customer from the stripe"""
    if user.stripe_customer_id:
        try:
            customer=stripe.Customer.retrieve(user.stripe_customer_id)
        except stripe.error.InvalidRequestError:
            pass
    else:
        customer=stripe.Customer.create(
            email=user.email,
            name=user.username,
        )
        print(customer.id)
        user.stripe_customer_id=customer.id
        user.save()
    return customer

@login_required(login_url='login')
@csrf_exempt
def payment(request):
    """this function allow authenticated user for buy the product.
    and allow the user to apply th coupon  on the product"""
    user=request.user
    address_id=request.session.get('address_id')

    try:
        cart = models.Cart_item.objects.filter(user=request.user)
    except models.Cart_item.DoesNotExist: #pylint:disable=no-member
        messages.warning(request,message.error_no_cartitem)
        return redirect('cart_list')
    line_cart = []
    total_discounts=1
    for item in cart:
        line_cart.append({
            "price_data": {
                'unit_amount': int(item.product.discounted_price)*100,
                "currency": "inr",
                "product_data": {
                    "description": item.product.description,
                    "name": item.product.name,
                },
            },
            "quantity": item.quantity,
        })
        if item.coupon:
            total_discounts =item.coupon.discount
    stripe_coupon=stripe.Coupon.create(
        amount_off=int(total_discounts)*100,
        currency='inr',
        name="Coupon applied"
    )
    session = stripe.checkout.Session.create(
        customer=get_or_create_stripe_customer(request.user),
        line_items=line_cart,
        metadata={
            "user_id":str(user.id),
            'address_id':str(address_id)
        },
        discounts=[{'coupon':stripe_coupon.id}],
        mode="payment",
        success_url="http://127.0.0.1:8000/shop/product/success/?checkout_id={CHECKOUT_SESSION_ID}",
        cancel_url="http://127.0.0.1:8000/failed/",
    )
    return redirect(session.url, 303)


@login_required(login_url='login')
def comment_on_product(request):
    """this function allow authenticated users to post the
    comment on the different products or same products"""
    if request.method=="POST":
        content=request.POST.get('content')
        product_id=request.POST.get('product_id')
        product=get_object_or_404(models.Product,pk=product_id)
        models.Comment.objects.create(user=request.user,product=product,content=content)
        return JsonResponse({'success':message.success_comment_post})
    return JsonResponse({'error':message.error_invalid})

@login_required(login_url='login')
def remove_comment(request):
    '''this function allow user remove
    their own comment which is posted by the same user'''
    if request.method=="POST":
        comment_id=request.POST.get('id')
        comment=models.Comment.objects.filter(user=request.user,pk=comment_id)
        comment.delete()
        return JsonResponse({'success':'comment deleted.'})
    return JsonResponse({'error':'Invalid request'})
    
# @login_required(login_url='login')

def comment_likes_view(request):
    'this function allow user to like and dislike the comments'
    if request.method == "POST":
        comment_id = request.POST['comment_id']
        comment_like=get_object_or_404(models.Comment,pk=comment_id)
        if request.user in comment_like.like.all():
            comment_like.like.remove(request.user)
        else:
            comment_like.like.add(request.user)
            comment_like.save()
        return JsonResponse({'success':message.success_comment_like}, status=200)
    return JsonResponse({'error': 'Invalid request'},status=200)

def address_select(request):
    """set the address id in the session"""
    if request.method=="POST":
        address_id=request.POST.get('address_id')
        request.session['address_id']=address_id
        print(request.session.get('address_id'))
    return JsonResponse({"succes":"address selected"})

@login_required(login_url='login')
def success_view(request):
    messages.success(request,message.success_payment_complete)
    return redirect('home')

# @login_required(login_url='login')
# def success_view(request):
#     """this function check if the payment is complete or not 
#     if the payment is complete this function retrive the data 
#     from the cart item and load in to orderitems"""
#     session_id=request.GET["checkout_id"]
#     address_id=request.session.get('address_id')
#     checkout_id=stripe.checkout.Session.retrieve(session_id)
#     data=[]
#     if checkout_id['payment_status']=="paid":
#         subject = "payment complete"
#         msg = f"""Hi {request.user.username},
#         Thanks for purchasing items from the store. 
#         Your payment is completed. 😊"""
#         sender = settings.EMAIL_HOST_USER
#         send_mail(subject, msg, sender, [request.user.email])
#         try:
#             data=models.Payment_model.objects.filter(user=request.user).order_by('payment_date').last()
#         except models.Payment_model.DoesNotExist: #pylint:disable=no-member
#             messages.error(request,message.error_payment)
#             return redirect('home')
#         if checkout_id.payment_intent :
#             models.Payment_model.objects.create(user=request.user,
#                     transaction_id=checkout_id.payment_intent,
#                     total_amount=checkout_id['amount_total']/100,status="completed")
#         else:
#             return redirect('orders') 
#         try:
#             address=models.Address.objects.filter(user=request.user,pk=address_id).first()
#         except models.Address.DoesNotExist: #pylint:disable=no-member
#             messages.error(request,message.error_address_exists)
#             return redirect('address')
#         try:
#             cart_item=models.Cart_item.objects.filter(user=request.user)
#         except models.Cart_item.DoesNotExist: #pylint:disable=no-member
#             messages.error(request,message.error_no_cartitem)
#             return redirect('success')
#         used_coupon=set()
#         for item in cart_item:
#             product=item.product
#             quantity=item.quantity
#             if item.coupon and item.coupon.id not in used_coupon:
#                 coupon=item.coupon
#                 if coupon.quantity>0:
#                     coupon.quantity -=1
#                     if coupon.quantity==0:
#                         coupon.is_active=False
#                     coupon.save()
#                     used_coupon.add(coupon.id)
#             if item.coupon:
#                 models.OrderItems.objects.create(user=request.user,product=product,
#                             payment=data,quantity=quantity,status="ORDER PLACED",
#                     coupon_price=item.coupon.discount,size=item.size.name,address=address).save()
#             else:
#                 models.OrderItems.objects.create(user=request.user,product=product,
#                             payment=data,quantity=quantity,status="ORDER PLACED",
#                             coupon_price=0,size=item.size.name,address=address).save()
#         cart_item.delete()
#         # del request.session['items']
#         messages.success(request,message.success_payment_complete)
#         return redirect('home')
#     return render(request,"success.html",{"data":data})

endpoint_secret=settings.STRIPE_ENDPOINT_KEY

@csrf_exempt
def my_webhook_view(request):
    """this webhook function check the event occuer by the stripe and based on 
    the event store the data in database and delete the data from the database"""
    payload = request.body
    event = None
    try:
        event = stripe.Event.construct_from(
        json.loads(payload), stripe.api_key)
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)

    if endpoint_secret:
            sig_header = request.headers.get('stripe-signature')
            try:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, endpoint_secret
                )
            except stripe.error.SignatureVerificationError as e:
                print('Webhook signature verification failed.' + str(e))
                return JsonResponse(success=False)
    if event.type == 'checkout.session.completed':
        checkout_session = event["data"]["object"]
        # print(payment_intent)
        user_id=checkout_session.get('metadata',{}).get('user_id')
        address_id=checkout_session.get('metadata',{}).get('address_id')
        print("from webhook",address_id)
        try:
            user=models.Custom_user.objects.get(id=user_id)
        except models.Custom_user.DoesNotExist:
            messages.success(request,"user not founded.")
            return redirect('home')
        print("hiii,",user)
        models.Payment_model.objects.create(user=user,
                    transaction_id=checkout_session['payment_intent'],
                 total_amount=checkout_session['amount_total']/100,status="completed")
        try:
            address=models.Address.objects.filter(user=user,pk=address_id).first()
        except models.Address.DoesNotExist: #pylint:disable=no-member
            messages.error(request,message.error_address_exists)
            return redirect('address')
        try:
            payment_instance=models.Payment_model.objects.filter(user=user).last()
        except models.Payment_model.DoesNotExist:
            messages.error(request,message.error_payment_Founded)
        try:
            cart_item=models.Cart_item.objects.filter(user=user)
        except models.Cart_item.DoesNotExist: #pylint:disable=no-member
            messages.error(request,message.error_no_cartitem)
            return redirect('success')
        used_coupon=set()
        for item in cart_item:
            product=item.product
            quantity=item.quantity
            if item.coupon and item.coupon.id not in used_coupon:
                coupon=item.coupon
                if coupon.quantity>0:
                    coupon.quantity -=1
                    if coupon.quantity==0:
                        coupon.is_active=False
                    coupon.save()
                    used_coupon.add(coupon.id)
            if item.coupon:
                models.OrderItems.objects.create(user=user,product=product,
                            payment=payment_instance,quantity=quantity,status="ORDER PLACED",
                    coupon_price=item.coupon.discount,size=item.size.name,address=address).save()
            else:
                models.OrderItems.objects.create(user=request.user,product=product,
                            payment=payment_instance,quantity=quantity,status="ORDER PLACED",
                            coupon_price=0,size=item.size.name,address=address).save()
        cart_item.delete()
        subject = "payment complete"
        msg = f"""Hi {request.user.username},
        Thanks for purchasing items from the store. 
        Your payment is completed. 😊"""
        sender = settings.EMAIL_HOST_USER
        send_mail(subject, msg, sender, [request.user.email])
        messages.success(request,message.success_payment_complete)
        return redirect('home')
    else:
        print('Unhandled event type {}'.format(event.type))
    return HttpResponse(status=200)


# @login_required(login_url="login")
# @csrf_exempt
# def direct_buy(request):
#     """this function allow authenticated user to buy the one product 
#     at a time by using buy now"""
#     if request.method == "POST":
#         item_id = request.POST.get('item')
#         quantity = request.POST.get('quantity')
#         try:
#             product = get_object_or_404(models.Product, id=item_id)

#         except models.Product.DoesNotExist: #pylint:disable=no-member
#             messages.error(request, message.error_no_product)
#             return redirect(request.META.get('HTTP_REFERER'))
#         try:
#             cart = models.Cart_item.objects.get(user=request.user, product=product)
#             cart.quantity += int(quantity)
#             cart.save()
#         except models.Cart_item.DoesNotExist: #pylint:disable=no-member
#             models.Cart_item.objects.create(user=request.user, 
#                             product=product, quantity=int(quantity))
#         if not models.Address.objects.filter(user=request.user).last():
#             return JsonResponse({'address':"http://127.0.0.1:8000/address/"})
#         try:
#             customer = stripe.Customer.create(
#                 email=request.user.email,
#                 name=request.user.username,
#             )
#         except stripe.error.StripeError as e:
#             print(f"Stripe error ===>  {str(e)}")
#             messages.error(request, "Error creating Stripe customer.")
#             return redirect(request.META.get('HTTP_REFERER'))
#         try:
#             checkout_session = stripe.checkout.Session.create(
#                 customer=customer.id,
#                 payment_method_types=["card"],
#                 line_items=[{
#                     "price_data": {
#                         'currency': "inr",
#                         'product_data': {
#                             'name': product.name,
#                         },
#                         'unit_amount': int(product.discounted_price) * 100,  # Amount in paise
#                     },
#                     "quantity": int(quantity),
#                 }],
#                 mode="payment",
#                 success_url="http://127.0.0.1:8000/success/?checkout_id={CHECKOUT_SESSION_ID}",
#                 cancel_url="http://127.0.0.1:8000/failed/",
#             )
#         except stripe.error.StripeError as e:
#             print(f"Stripe error during session creation ===>  {str(e)}")
#             messages.error(request, "Error creating Stripe checkout session.")
#             return redirect(request.META.get('HTTP_REFERER'))

#         return JsonResponse({"url":checkout_session.url})
#     return redirect('cart_list')


@login_required(login_url='login')
def cancel_view(request):
    """ this is the cancel function """
    return render(request,"cancel.html")

@login_required(login_url='login')
def order_history(request):
    "showing the ordered product by the user."
    user=request.user
    try:
        orders=models.OrderItems.objects.filter(user=user).order_by("-order_date")
        context={"orders":orders}
        return render(request,"orders.html",context)
    except models.OrderItems.DoesNotExist: #pylint:disable=no-member
        messages.warning(request,message.error_no_orderitem)
        return render(request,"orders.html")

@login_required(login_url='login')
def order_details(request,pk):
    "show the order item details to the user"
    order=get_object_or_404(models.OrderItems,pk=pk)
    discount=order.product.price-order.product.discounted_price
    total_price=order.quantity*order.product.discounted_price
    context={
        'discount':discount,
        'total_price':total_price,
        'order':order
    }
    return render(request,'order_details.html',context)

@login_required(login_url='login')
def transaction_history(request):
    """this function view show the all transactions
    which is purchsed by the user """
    try:
        transaction=models.Payment_model.objects.filter(user=request.user).order_by('-payment_date')
    except models.Payment_model.DoesNotExist: #pylint:disable=no-member
        messages.error(request,message.error_transaction_History)
        return redirect(request.META.get('HTTP_REFERER')) 
    return render(request,'transaction-history.html',{'transaction':transaction})

@login_required(login_url='login')
def apply_coupon(request):
    """This function allows the user to apply a valid coupon on the cart items."""
    if request.method == "POST":
        coupon_code = request.POST.get('coupon')
        now = timezone.now()
        try:
            coupon = models.Coupon.objects.get(
                code__iexact=coupon_code,
                valid_from__lte=now,
                valid_to__gte=now,
                quantity__gt=0,
                user=request.user,
                is_active=True)
            cart_data = models.Cart_item.objects.filter(user=request.user)
            for item in cart_data:
                item.coupon = coupon
                item.save()
            return JsonResponse({"success": "Coupon applied successfully!"})
        except models.Coupon.DoesNotExist:
            try:
                coupon = models.Coupon.objects.get(
                    code__iexact=coupon_code,
                    valid_from__lte=now,
                    valid_to__gte=now,
                    user__isnull=True,
                    is_active=True)
                cart_data = models.Cart_item.objects.filter(user=request.user)
                for item in cart_data:
                    item.coupon = coupon
                    item.save()
                return JsonResponse({"success": message.success_coupon_applied})
            except models.Coupon.DoesNotExist:
                return JsonResponse({"error": message.error_invalid_Coupon})
    return JsonResponse({"error": message.error_invalid_request})

@login_required(login_url='login')
def remove_coupon(request):
    '''this function allow user to remove the coupon from 
    the cart items '''
    cart=models.Cart_item.objects.filter(user=request.user)
    for item in cart:
        if item.coupon:
            item.coupon = None
            item.save()
    return redirect('cart_list')

@login_required(login_url='login')
def shippment_address(request):
    '''allowing users to add delivery address'''
    if request.method == "POST":
        form = forms.AddressForm(request.POST)
        if form.is_valid():
            # Check if this address already exists for this user
            existing_address = models.Address.objects.filter(
                landmark=form.cleaned_data['landmark'],
                address=form.cleaned_data['address'],
                phone=form.cleaned_data['phone'],
                user=request.user).exists()
            if existing_address:
                form.add_error(None, message.error_address_exists)
            else:
                address = form.save(commit=False)
                address.user = request.user
                address.save()
                messages.success(request, message.success_address_added)
                return redirect(request.META.get("HTTP_REFERER", '/'))
    else:
        form = forms.AddressForm()
    return render(request, 'shipping.html', {'form': form})


@login_required(login_url='login')
@csrf_exempt
def add_watchlist(request):
    if request.method=="POST":
        id=request.POST.get('id')
    product=get_object_or_404(models.Product,pk=id)
    watchlist,created =models.Watchlist.objects.get_or_create(user=request.user,product=product)
    if not created:
        watchlist.delete()
        return JsonResponse({'item_remove':"Product removed from watchlist"})
    return JsonResponse({'item_add':" Product added into watchlist"},status=201)


@login_required(login_url='login')
def show_watchlist(request):
    product=models.Watchlist.objects.all()
    return render(request,'watchlist.html',{"product":product})

razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_SECRET_KEY))


def razorpay_gateway(request):
    if request.method == 'POST':
        address_id = request.POST.get('address_id')
        request.session['address_id']=address_id
        print(request.session.get('address_id'))
        cart_items = models.Cart_item.objects.filter(user=request.user)
        if not cart_items.exists():
            return JsonResponse({'error': 'No items in the cart'}, status=400)
        total_amount = round(sum([(items.product.discounted_price)*items.quantity for items in cart_items]))
        print(total_amount)
        # Razorpay order create
        razorpay_order = razorpay_client.order.create({
            'amount': int(total_amount * 100), # in paise
            'currency': 'INR',
            'payment_capture': 1})
        
        return JsonResponse({
            'razorpay_key': settings.RAZOR_KEY_ID,
            'razorpay_order_id': razorpay_order['id'],
            'amount': total_amount * 100,
            'name':request.user.username,
            'email':request.user.username
            })
    return redirect('cart_list')

def verify_razorpay(request):
    print("verify me aaya")
    if request.method == 'POST':
        print("verify post me aaya")
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')

        params = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        try:
            razorpay_client.utility.verify_payment_signature(params)
            return JsonResponse({'success': True})
        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({'success': False})
    return JsonResponse({'success': False})
