'use stric';



export default class DataLoader {

    constructor(){
        console.log('in the class');
    }

    LoadData(endpoint,cb){
        var cb = cb;
        console.log(endpoint);
        $.ajax({
            url:endpoint,
            method:'GET',
            contentType: 'text/plain',
            success:function(response){
                console.log(cb);
                if(cb && typeof cb === "function"){
                    console.log(response);
                    cb(response);
                }
            },
            error:function(textStatus){
                console.error(textStatus);
            }
        })
    }
}

export const dataloader = new DataLoader();
