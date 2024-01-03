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


async function update_state(){
    const response = await fetch('/update_state');
    data = await response.json();
    image.src = 'data:image/jpeg;base64,' + data.image;
    console.log(image);
}