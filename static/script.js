"use strict";

const controls = document.getElementById("controls");
const load_form = document.getElementById("load_form");
const image =  document.getElementById("image");
var data;

controls.addEventListener('click', function(event) {
    event.preventDefault();
    const target = event.target.id;
    if(!(["initial", "previous", "next", "last"].includes(target))){
        return;
    }
    console.log("controls");
    fetch('/controls', {
        method: 'POST',
        body: target,
    }).then(function(response) {
        if(response.status == 204){
            update_state().then(
                console.log("Updated State")
            );
        }
    });
});

load_form.addEventListener("submit", function(event) {
    event.preventDefault();    // prevent page from refreshing
    const form_data = new FormData(load_form)
    console.log("loading");
    fetch('/upload', {
        method: 'POST',
        body: form_data,
    }).then(function(response) {
        if(response.status == 204){
            update_state().then(
                console.log("Updated State")
            );
        }
    });
});

undo.addEventListener("submit", function(event) {
    event.preventDefault();    // prevent page from refreshing
    fetch('/undo', {
        method: 'POST',
    }).then(function(response) {
        if (response.status === 204) {
            console.log("Undone");
        }
    }).catch(function(error) {
        console.error('Error:', error);
    });
});


async function update_state(){
    const response = await fetch('/update_state');
    data = await response.json();
    image.src = 'data:image/jpeg;base64,' + data.image;
    console.log(image);
}

function updateMessage() {
    $.get('/update', function(data) {
        $('#message').text(data.message);
        $('#image img').attr('src', 'data:image/jpeg;base64,' + data.image); 
    });
}

function downloadFile() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/get_sgf_txt', true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
            var blob = new Blob([xhr.responseText], { type: 'text/plain' });
            
            saveAs(blob, 'game.sgf');
        }
    };
    xhr.send();
}