"use strict";


var img = new Image();
img.src = './empty_board.jpg';
const canvas = document.getElementById('go-board');
var context = canvas.getContext("2d");

img.onload = function ()
{
    console.log("Image loaded successfully.");
    context.drawImage(img, 0, 0);
};

img.onerror = function () {
    console.error("Error loading image.");
};
const controls = document.getElementById("controls");
const load_form = document.getElementById("load_form");
const plot_image =  document.getElementById("plot-image");
const camera_feed_closed = document.getElementById("camera-feed-closed");

var camera_feed = null;

const message = document.getElementById("message");
const start_button =  document.getElementById("start-button");
const stop_button =  document.getElementById("stop-button");
const pause_button =  document.getElementById("pause-button");
const undo_button = document.getElementById("undo")
var recordLoop = null;
var Data;

var RECORDING = false;
var STARTED = false;
var STOPPED = false;
var PAUSED = false;

fetch("/get_config").then(function(response){
    response.json().then(function(data){
        STARTED = data.STARTED;
        STOPPED = data.STOPPED;
        if(STOPPED){
            update_state();
            start_button.disabled = false;
            stop_button.disabled = true;
            pause_button.disabled = true;
            camera_feed_closed.hidden = false;
        } else if (STARTED) {
            start_button.disabled = true;
            stop_button.disabled = false;
            pause_button.disabled = false;

            camera_feed_closed.hidden = true;

            camera_feed = document.createElement('img');
            camera_feed.classList.add(...camera_feed_closed.classList);
            camera_feed.id = 'camera-feed';
            camera_feed.alt = "Camera Feed";
            camera_feed.src = '/video_feed';

            camera_feed_closed.parentNode.insertBefore(camera_feed, camera_feed_closed.nextSibling);

            recordLoop = setInterval(update_state, 2000);
        }
    })
})


canvas.addEventListener('click', function(event) {
    
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    // Calculate the board coordinates
    const boardX = Math.floor((x / canvas.width) * 19) + 1;
    const boardY = Math.floor((y / canvas.height) * 19) + 1;

    console.log(`Clicked on Go board at (${boardX}, ${boardY})`);
    
     // Send the click coordinates to the Flask backend
     fetch(`/play_stone?x=${boardX}&y=${boardY}`, { method: 'POST' })
     .then(response => response.json())
     .then(data => {
         // Update the board based on the response from the backend
         // You may need to implement this part based on your go library
         console.log(data);
     });

// Draw your initial empty board or load it from an image
// You can use the ctx.fillStyle and ctx.fillRect() methods for this
});

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

undo_button.addEventListener('click', function(event) {
    event.preventDefault();   
    console.log("clicked")
    fetch('/undo', {
        method: 'POST',
    }).then(function(response) {
        if (response.status === 204) {
            console.log("Undone");
        }
        else {
            message.textContent = "There are no moves left";
        }
    });
});

start_button.addEventListener('click', function(event) {
    event.preventDefault();
    console.log("start");
    fetch('/open_camera', {
        method: 'POST',
        body: "",
    }).then(function(response){
        if(response.status == 204){
            STARTED = true;

            start_button.disabled = true;
            stop_button.disabled = false;
            pause_button.disabled = false;

            camera_feed_closed.hidden = true;

            if(camera_feed == null){
                camera_feed = document.createElement('img');
                camera_feed.classList.add(...camera_feed_closed.classList);
                camera_feed.id = 'camera-feed';
                camera_feed.alt = "Camera Feed";
                camera_feed.src = '/video_feed';

                camera_feed_closed.parentNode.insertBefore(camera_feed, camera_feed_closed.nextSibling);
            } else {
                camera_feed.hidden = false;
            }


            recordLoop = setInterval(update_state, 2000);
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
        body: JSON.stringify(true),
    }).then(function(response){
        if(response.status == 204){
            STOPPED = true;

            start_button.disabled = false;
            stop_button.disabled = true;
            pause_button.disabled = true;
            camera_feed_closed.hidden = false;

            camera_feed.hidden = true;
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
            plot_image.src = 'data:image/jpeg;base64,' + data.image;
            message.textContent = data.message;
        })
    })
}

window.onbeforeunload = function(event) {
    var s = "You have unsaved changes. Really leave?";
    if(recordLoop != null){
        clearInterval(recordLoop);
    }
    fetch('/close_camera', {
        method: 'POST',
        body: JSON.stringify(false),
    }).then(function(){})
    
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