$(document).ready(function() {
    let productsize=null
    $(".watchlist-msg").hide()
    $('.selectsize-alert').hide()
    $('.size-btn').click(function(){
        $(this).css('background-color', 'green');
        let size=$(this).data('id');
        productsize=size
    })
 
    /* comment Post */
    $(".comment").click(function(){
        let itemid=$(this).data('id')
        let content=$('.content').val()
        if (content ==""){
            alert('Empty comment cannot be posted.')
            return
        }
        $.ajax({
            url:commentpost_url,
            method:"POST",
            data:{
                'product_id':itemid,
                'content':content,
                'csrfmiddlewaretoken':csrf_token,
            },
            success:function(response){
                if(response.success){
                   
                    window.location.reload()
                }
                if(response.error){
                    alert(response.error)
                } 
            }
        })
        
    })

    /*remove comment*/

    $('.remove').click(function(){
        let comment_id=$(this).data('id');
        $.ajax({
            url:commentremove_url,
            method:"POST",
            data:{
                'id':comment_id,
                'csrfmiddlewaretoken':csrf_token,
            },
            success:function(response){
                if(response.success){
                    window.location.reload()
                }
            },
            error:function(xhr){
                console.log(xhr)
            }

        })
    })

    $('.like-btn').click(function(){
        let comment_id=$(this).data('id');
        $.ajax({
            url:commentlike_url,
            type:"POST",
            data:{
                'comment_id':comment_id,
                'csrfmiddlewaretoken':csrf_token
            },
            success:function(response){
                window.location.reload()
            },
            

        })
    })


   /* add to card*/

    $(".plus-btn").click(function() {
        let itemId = $(this).data("id");
        let quantityElement = $(".item-quantity[data-id='" + itemId + "']");
        let currentQuantity = parseInt(quantityElement.text());
        quantityElement.text(currentQuantity + 1);
    });

    $(".minus-btn").click(function() {
        let itemId = $(this).data("id");
        let quantityElement = $(".item-quantity[data-id='" + itemId + "']");
        let currentQuantity = parseInt(quantityElement.text());
        
        if (currentQuantity > 1) {
            quantityElement.text(currentQuantity - 1);
        }
    });

    /*
    $(".buy_now").click(function(){

        let itemid= $(this).data('id');
        let quantity = $(".item-quantity[data-id='" + itemid + "']").text();
        if(!productsize){
            alert("select the size")
            return
        }
        
        $.ajax({
            url:buynow_url,
            method:"POST",
            data:{
                'item':itemid,
                'quantity':quantity,
                'csrfmiddlewaretoken':csrf_token,
            },
            success: function(response){
                if (response.url){
                    window.location.href=response.url
                }
                if (response.address){
                    window.location.href=response.address
                }
            }
        })
    })
        */
    

    $(".add_cart").click(function() {
        let itemId = $(this).data("id");
        let quantity = $(".item-quantity[data-id='" + itemId + "']").text();
        let size=productsize;
        console.log(size)
            if(!productsize){
                $('.selectsize-alert').show()
                $('.selectsize-alert').html("Please select the size.").delay(1000).fadeOut('slow')
                return
            }
            
        $.ajax({
            url:add_to_cart_url,
            method:"POST",
            data:{
                "item":itemId,
                "quantity":quantity,
                "size":size,
                'csrfmiddlewaretoken':csrf_token,
            },
            success: function(res){
                $('.add_cart').html("Go to Cart")
                window.location.href="/shop/product/cart-list/"
            }
        })
    });


   /* adding the item in to watchlist by the user*/

    $('.watchlist').click(function(e){
        product_id=$(this).data('id')
        console.log(product_id)
         $.ajax({
            url:watchlist_url,
            method:"POST",
            data:{
                'id':product_id,
                'csrfmiddlewaretoken':csrf_token,
            },
            success:function(response){
                if(response.item_add){
                    $(".watchlist-msg").show()
                    // $(".watchlist-msg").html(response.item_add).delay(3000).fadeOut('slow');
                    window.location.reload()
                }
                if(response.item_remove){
                    $(".watchlist-msg").show()
                    window.location.reload()

                    // $(".watchlist-msg").html(response.item_remove).delay(3000).fadeOut('slow');
                }
            },
            error:function(xhr){
                console.log(xhr.responseJSON)
            }
        })
    })


    
  
})