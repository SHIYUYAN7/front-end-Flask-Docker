// store the image id need to change
IMAGEID = "0";


// create nft in seller page
document.getElementById('create_nft').addEventListener('click',function(e){
    // e.preventDefault();
    res = checkInput();
    if(res){
        // package data in a JSON object
        var data_d = {'description': res[0],'token': res[1]};
        
        // SEND DATA TO SERVER VIA jQuery.ajax({})
        jQuery.ajax({
            url: "/processCreateNFT",
            data: data_d,
            type: "POST",
            success:function(retruned_data){
                retruned_data = JSON.parse(retruned_data);
                if(retruned_data.success === 1){
                    var newImage = `
                        <div id="${retruned_data.image_id}" class="item_box">
                            <div class="image_box">
                                <img class="image" src="/static/NFTimages/${retruned_data.image_id}.png" loading="lazy">
                            </div>
                            <div class="info_Box">
                                <div class="description">${retruned_data.description}</div>
                                <div class="price">${retruned_data.token}</div>
                                <div class="button" onclick="onedit('${retruned_data.image_id}')">&nbsp;&nbsp;EDIT</div>
                            </div>
                        </div>`;
                    $('#trade_content').append(newImage);
                }
            },
        });
    }
})

// upload nft in seller page
document.getElementById('upload_nft').addEventListener('click', function(e) {
    e.preventDefault();

    res = checkInput();
    if(res){
        // package data in a JSON object
        var formData = new FormData();
        var file = document.getElementById('image_input').files[0]
        // if file is empty
        if (file !== undefined && file !== null) {
            // add the file to the form data
            formData.append('image', file);
            formData.append('description', res[0]);
            formData.append('token', res[1]);

            //check the contentin formData
            // for (var key of formData.entries()) {
            //     console.log(key[0] + ', ' + key[1]);
            // }

            $.ajax({
                url: '/processUploadNFT',
                type: 'POST',
                data: formData,
                contentType: false,
                processData: false,
                success: function(retruned_data) {
                    retruned_data = JSON.parse(retruned_data);
                    var newImage = `
                        <div id="${retruned_data.image_id}" class="item_box">
                            <div class="image_box">
                                <img class="image" src="/static/NFTimages/${retruned_data.image_id}.png" loading="lazy">
                            </div>
                            <div class="info_Box">
                                <div class="description">${retruned_data.description}</div>
                                <div class="price">${retruned_data.token}</div>
                                <div class="button" onclick="onedit('${retruned_data.image_id}')">&nbsp;&nbsp;EDIT</div>
                            </div>
                        </div>`;
                    $('#trade_content').append(newImage);
                },

            });
        }
        else{
            alert('You should upload a image!')
        }
    }
});


function checkInput(){
    let createDescription = document.getElementById('create_description').value
    let createToken = document.getElementById('token').value

    if(createDescription === '' || createToken === ''){
        alert('The Description and Token cannot be empty!')
        return null
    }
    // if the input is not a number
    else if(isNaN(createToken)){
        alert('The Token should be a number!')
        return null
    }
    else{
        return [createDescription,createToken]
    }
}

function onedit(num){
    document.getElementById('edit_dialog').style.display = 'block';
    // update selected image id
    IMAGEID = num
}


// control the dialog
document.getElementById('dialog_submit').addEventListener('click',function(){
    let des = document.getElementById('edit_description').value;
    let token = document.getElementById('edit_token').value;
    
    // validation
    if(des == '' && token == ''){ alert('No need to Edit'); return}
    if(des == ''){ des = 'unchange'}
    if(token == ''){ token = 'unchange'}
    

    // SEND DATA TO SERVER VIA jQuery.ajax({})
    jQuery.ajax({
        url: "/processEditNFT",
        data: {'des':des,'token':token, 'image_id':IMAGEID},
        type: "POST",
        success:function(retruned_data){
            retruned_data = JSON.parse(retruned_data);
            if(retruned_data.success === 1){
                
                // select the item with id = imageid
                var item = document.getElementById(String(IMAGEID));
                if(des != 'unchange'){
                    // update the description
                    item.getElementsByClassName("description")[0].innerText = des;
                }
                if(token != 'unchange'){
                    // update the price
                    item.getElementsByClassName("price")[0].innerText = token;
                }
                
                closeDialog();
            }
        },
    });


    
})

// cancel button, close dialog
document.getElementById('dialog_cancel').addEventListener('click',function(){
    closeDialog();
})

// close dialog and clean value
function closeDialog(){
    document.getElementById('edit_dialog').style.display = 'none';
    document.getElementById('edit_description').value = '';
    document.getElementById('edit_token').value = '';
    // clear id
    IMAGEID = "0";
}

