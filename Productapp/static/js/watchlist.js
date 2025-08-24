$(document).ready(function(){
    $('.remove-btn').click(function(){
        let id=$(this).data('id');
        $.ajax({
            url:remove_watchlist_item_url,
            method:"POST",
            data:{
                'id':id,
                'csrfmiddlewaretoken':'{{csrf_token}}',
            },
            success:function(response){
                if(response.item_remove){
                    window.location.reload()
                }
            },
            error:function(xhr){
                console.log(xhr.responseJSON)
            }

        })
    })
  
})