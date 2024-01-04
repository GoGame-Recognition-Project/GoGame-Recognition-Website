"use strict";

const controls = document.getElementById("controls");
const load_form = document.getElementById("load_form");
const image =  document.getElementById("image");
const message = document.getElementById("message");
const start_button =  document.getElementById("start-button");
const stop_button =  document.getElementById("stop-button");
const pause_button =  document.getElementById("pause-button");
var recordLoop = null;
var Data;

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
            update_state()
        }
    });
});

// load_form.addEventListener("submit", function(event) {
//     event.preventDefault();    // prevent page from refreshing
//     const form_data = new FormData(load_form)
//     console.log("loading");
//     fetch('/upload', {
//         method: 'POST',
//         body: form_data,
//     }).then(function(response) {
//         if(response.status == 204){
//             update_state()
//         }
//     });
// });

// undo.addEventListener("submit", function(event) {
//     event.preventDefault();    // prevent page from refreshing
//     fetch('/undo', {
//         method: 'POST',
//     }).then(function(response) {
//         if (response.status === 204) {
//             console.log("Undone");
//         }
//     }).catch(function(error) {
//         console.error('Error:', error);
//     });
// });


start_button.addEventListener('click', function(event) {
    event.preventDefault();
    console.log("start");
    fetch('/open_camera', {
        method: 'POST',
        body: "",
    }).then(function(response){
        if(response.status == 204){
            start_button.disabled = true;
            stop_button.disabled = false;
            pause_button.disabled = false;
            recordLoop = setInterval(update_state, 1000);
        } else if (response.status == 502){
            message.textContent = "The camera was not able to start recording";
        }
    })
});

stop_button.addEventListener('click', function(event) {
    event.preventDefault();
    console.log("stop");
    clearInterval(recordLoop);
    fetch('/close_camera', {
        method: 'POST',
        body: "",
    }).then(function(response){
        if(response.status == 204){
            start_button.disabled = true;
            stop_button.disabled = false;
            pause_button.disabled = false;
        } else {
            message.textContent = "A problem was encountered while closing the camera";
        }
    })
});

pause_button.addEventListener('click', function(event) {
    event.preventDefault();
    console.log("pause");
    clearInterval(recordLoop);
    start_button.disabled = false;
    stop_button.disabled = true;
    pause_button.disabled = true;
});

function update_state(){
    fetch('/update_state').then(function(response){
        response.json().then(function(data){
            image.src = 'data:image/jpeg;base64,' + data.image;
        })
    })
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