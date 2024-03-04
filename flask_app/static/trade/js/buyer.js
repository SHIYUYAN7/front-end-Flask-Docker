function onbuy(num){
    var item = document.getElementById(String(num));
    var token = item.getElementsByClassName("price")[0].innerText
    
    console.log(typeof token)
    // SEND DATA TO SERVER VIA jQuery.ajax({})
    jQuery.ajax({
        url: "/processBuyNFT",
        data: {'image_id':num,'token':token},
        type: "POST",
        success:function(retruned_data){
            retruned_data = JSON.parse(retruned_data);
            if(retruned_data.success === 1){
                // select the item with id = imageid
                item.remove();
            }
            else{
                alert('Not enough token!')
            }
        },
    });
}