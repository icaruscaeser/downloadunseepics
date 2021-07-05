function download_pics(){
    //Fetch and check url

    let unsee_url = document.getElementById('url_input').value;
    //Use appropriate api
    if(!unsee_url.startsWith('https://')){
        unsee_url = 'https://' + unsee_url;
    }
    let old_unsee_regex = "https://old.unsee.cc/album#[a-zA-Z0-9]{8}";
    let new_unsee_regex = "https://unsee.cc/album#[a-zA-Z0-9]{16}";


    let api = null;
    if(unsee_url.match(old_unsee_regex)){
        api = server_url + '/api/download/old_unsee?url='+encodeURI(unsee_url);
    }
    else if (unsee_url.match(new_unsee_regex)){
        api = server_url + '/api/download/unsee?url=' + encodeURI(unsee_url)
    }
    else{
        alert('invalid url');
        return;
    }

    api = api.replace('#', '%23')
    console.log("encoded" + encodeURI(unsee_url));
    console.log(api);

    let xhr = new XMLHttpRequest();
    xhr.responseType = 'blob';
        xhr.onreadystatechange = function(data){
        //Progress can be sent using yield
        if(xhr.status == 200){
            //Show the downloaded zip file.
            handle_file(this);
        }
        if(xhr.status == 500){
            alert('Error occurred');
        }
    }

    xhr.open('GET', api);
    xhr.send();
}

function handle_file(xhr){
    // ref https://stackoverflow.com/questions/38192854/recieving-a-zip-file-as-response-on-ajax-request
    var resp = xhr.response;
    if(resp == null){
        return;
    }
    console.log(resp);
    let blob = new Blob([xhr.response], {type:'application/zip'});
    let file = URL.createObjectURL(blob);
    let filename = 'unsee.zip';
    let a = document.createElement("a");
    // if `a` element has `download` property
    if ("download" in a) {
      a.href = file;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }
}