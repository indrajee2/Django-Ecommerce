$(document).ready(function() {
    
     /*handling the coupon card*/
    $('.coupon-message').hide()
    $('.coupon_btn').click(function(event){
        event.preventDefault()
        coupon=$('#coupon').val()
        $.ajax({
            url:coupon_url,
            method:'POST',
            data:{
                'coupon':coupon,
                'csrfmiddlewaretoken':csrf_token,
            },
            success: function(res){
                if (res.success)
                {
                    $('.coupon-message').show()
                    window.location.reload()
                    $('.coupon-message').html(res.success).delay(3000).fadeOut('slow');
                }
                if (res.error){ 
                    $('.coupon-message').show()
                    $('.coupon-message').html(res.error).delay(3000).fadeOut('slow');
                }
                if (res.login){
                    window.location.href=res.login
                }
            }
        })
    })

    /*allow user to select the address*/

    $('#order-form').submit(function(event){
        var selectaddress=$('input[name="address"]:checked').val()
        $('.selectaddress-alert').hide()
        if (!selectaddress){
            event.preventDefault()
            $('.selectaddress-alert').show()
            $('.selectaddress-alert').html("Please select the delivery address").delay(1000).fadeOut('slow')
            return
        }
         $.ajax({
            url:address_url,
            method:"POST",
            data:{
                'address_id':selectaddress,
                'csrfmiddlewaretoken':csrf_token,
            },
            success:function(response){
                console.log(response.success)
                }
        });
    })

     /* handling the item deleted by the user*/
    $('.delete').click(function(){
        itemid=$(this).data('id')
        size_id=$(this).data('size');
        $.ajax({
            url:delete_item_url,
            method:"POST",
            data:{
                "itemid":itemid,
                'size_id':size_id,
                'csrfmiddlewaretoken':csrf_token,
            },
            success: function(res){
                if (res.success){
                    console.log(res.msg)
                    window.location.reload()
                }
            },
            error: function(xhr){
                if(xhr.error){
                    console.log(xhr.error)
                }
            }
        })
    })

    //=== RAZORPAY CHECKOUT =======
        $('#razorpay').click(function () {
            let selected_address = $('input[name="address"]:checked').val();

            if (!selected_address){
                $('.selectaddress-alert').show()
                $('.selectaddress-alert').html("Please select the delivery address").delay(1000).fadeOut('slow')
                return
            }
            $.ajax({
                url:razorpay_url,
                type: 'POST',
                data: {
                    address_id: selected_address,
                    csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
                },
                success: function (data) {
                    // console.log(data)
                    var options = {
                        "key": data.razorpay_key,
                        "amount": data.amount,
                        "currency": "INR",
                        "name": "product_name",
                        "description": "description for test payment",
                        "order_id": data.razorpay_order_id,
                        "handler": function (response) {
                            $.ajax({
                                url: varify_payment_url,
                                type: 'POST',
                                data: {
                                    razorpay_payment_id: response.razorpay_payment_id,
                                    razorpay_order_id: response.razorpay_order_id,
                                    razorpay_signature: response.razorpay_signature,
                                    csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
                                },
                                success: function (res) {
                            
                                    if (res.success) {
                                        window.location.href = `/cart-order/payment-success/`;
                                    } else {
                                        alert("Payment verification failed");
                                    }
                                }
                            });
                        },
                        "theme": {
                            "color": "#3399cc"
                        }
                    };
                   const rzp1 = new Razorpay(options);
                   rzp1.open();
                //    rzp1.on('payment.failed',function(res){
                //     console.log(response.error)
                //    })
                },
                error: function (xhr) {
                    alert("Something went wrong while initiating Razorpay.");
                }
            });
        }); //RAZORPAY CLOSED
})