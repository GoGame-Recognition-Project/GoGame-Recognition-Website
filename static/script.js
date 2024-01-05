"use strict";

const controls = document.getElementById("controls");
const load_form = document.getElementById("load_form");
const plot_image =  document.getElementById("plot-image");
const camera_feed_closed = document.getElementById("camera-feed-closed");

var camera_feed = null;

const message = document.getElementById("message");
const start_button =  document.getElementById("start-button");
const stop_button =  document.getElementById("stop-button");
const pause_button =  document.getElementById("pause-button");
const undo_button = document.getElementById("undo");
var updateLoop = null;
var Data;

var RECORDING = false;
var STARTED = false;
var STOPPED = false;
var PAUSED = false;
var QUIT = false;

// fetch("/get_config").then(function(response){
//     response.json().then(function(data){
//         STARTED = data.STARTED;
//         STOPPED = data.STOPPED;
//         if(STOPPED){
//             update_state();
//             start_button.disabled = false;
//             stop_button.disabled = true;
//             pause_button.disabled = true;
//             camera_feed_closed.hidden = false;
//         } else if (STARTED) {
//             start_button.disabled = true;
//             stop_button.disabled = false;
//             pause_button.disabled = false;

//             camera_feed_closed.hidden = true;

//             camera_feed = document.createElement('img');
//             camera_feed.classList.add(...camera_feed_closed.classList);
//             camera_feed.id = 'camera-feed';
//             camera_feed.alt = "Camera Feed";
//             camera_feed.src = '/video_feed';

//             camera_feed_closed.parentNode.insertBefore(camera_feed, camera_feed_closed.nextSibling);

//             recordLoop = setInterval(update_state, 2000);
//         }
//     })
// })


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

// start_button.addEventListener('click', function(event) {
//     event.preventDefault();
//     console.log("start");
//     fetch('/open_camera', {
//         method: 'POST',
//         body: "",
//     }).then(function(response){
//         if(response.status == 204){
//             STARTED = true;

//             start_button.disabled = true;
//             stop_button.disabled = false;
//             pause_button.disabled = false;

//             camera_feed_closed.hidden = true;

//             if(camera_feed == null){
//                 camera_feed = document.createElement('img');
//                 camera_feed.classList.add(...camera_feed_closed.classList);
//                 camera_feed.id = 'camera-feed';
//                 camera_feed.alt = "Camera Feed";
//                 camera_feed.src = '/video_feed';

//                 camera_feed_closed.parentNode.insertBefore(camera_feed, camera_feed_closed.nextSibling);
//             } else {
//                 camera_feed.hidden = false;
//             }


//             recordLoop = setInterval(update_state, 2000);
//         } else if (response.status == 502){
//             message.textContent = "The camera was not able to start recording";
//         }
//     })
// });

// stop_button.addEventListener('click', function(event) {
//     event.preventDefault();
//     console.log("stop");
//     clearInterval(recordLoop);
//     fetch('/close_camera', {
//         method: 'POST',
//         body: JSON.stringify(true),
//     }).then(function(response){
//         if(response.status == 204){
//             STOPPED = true;

//             start_button.disabled = false;
//             stop_button.disabled = true;
//             pause_button.disabled = true;
//             camera_feed_closed.hidden = false;

//             camera_feed.hidden = true;
//         } else {
//             message.textContent = "A problem was encountered while closing the camera";
//         }
//     })
// });

pause_button.addEventListener('click', function(event) {
    event.preventDefault();
    console.log("pause");
    clearInterval(updateLoop);

    start_button.disabled = true;
    stop_button.disabled = true;
    pause_button.disabled = true;
});

// function update_state(){
//     fetch('/update_state').then(function(response){
//         response.json().then(function(data){
//             plot_image.src = 'data:image/jpeg;base64,' + data.image;
//             message.textContent = data.message;
//         })
//     })
// }

// window.onbeforeunload = function(event) {
//     var s = "You have unsaved changes. Really leave?";
//     if(recordLoop != null){
//         clearInterval(recordLoop);
//     }
//     fetch('/close_camera', {
//         method: 'POST',
//         body: JSON.stringify(false),
//     }).then(function(){})
    
// }

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

var canvas = document.getElementById('canvas');
var context = canvas.getContext('2d');
const video = document.getElementById("videoElement");


// function initiate_video(){
//     if (navigator.mediaDevices.getUserMedia) {
//         navigator.mediaDevices.getUserMedia({ video: true })
//         .then(function (stream) {
//             video.srcObject = stream;
//             video.play();
//         })
//         .catch(function (err0r) {
//             alert('Video feed failed to start');
//         });
//     }
// }


// function plot_stream(){
//     const FPS = 6;
//     setInterval(() => {
//         var video_height = video.videoHeight;
//         var video_width = video.videoWidth;
//         var width = video_width;
//         var height = video_height;
//         canvas.width = video_width;
//         canvas.height = video_height;
//         context.drawImage(video, 0, 0, width, height);
//         var data = canvas.toDataURL('image/jpeg', 1);
//         context.clearRect(0, 0, width, height);
//         // socket.emit('image', data);
//     }, 1000/FPS);
// }

async function update_state(){
    var video_height = video.videoHeight;
    var video_width = video.videoWidth;
    var width = video_width;
    var height = video_height;
    canvas.width = video_width;
    canvas.height = video_height;
    context.drawImage(video, 0, 0, width, height);
    var data = canvas.toDataURL('image/jpeg', 0.5);
    context.clearRect(0, 0, width, height);

    var response = await fetch('/update_state', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify({ image: data }),
                            })

    if(response.status == 502){
        console.log('Update failed');
        return;
    }

    var data = await response.json();
    plot_image.src = 'data:image/jpeg;base64,' + data.image;
    message.textContent = data.message;
}

function update_state_loop() {
    update_state().then(() => {
        // Schedule the next execution after the asynchronous operation is complete
        if(!QUIT){
            updateLoop = setTimeout(update_state_loop, 0); // Adjust the interval as needed
        }
    });
}

start_button.addEventListener('click', function(event) {
    event.preventDefault();
    QUIT = false
    console.log("start");
    if (navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
        .then(function (stream) {
            video.srcObject = stream;
            video.play();

            start_button.disabled = true;
            stop_button.disabled = false;
            pause_button.disabled = false;

            camera_feed_closed.hidden = true;
            video.hidden = false;

            fetch('/initialize_new_game').then(function(response){
                if(response.status == 204){
                    console.log("New game was initialized");
                    update_state_loop();
                } else {
                    alert("Error initializing new game, please try again");
                }
            })

        })
        .catch(function (err0r) {
            alert('Video feed failed to start');
        });
    }
});


stop_button.addEventListener('click', function(event) {
    event.preventDefault();
    console.log("stop");
    clearTimeout(updateLoop);
    QUIT = true;
    video.srcObject.getVideoTracks()[0].stop();

    video.hidden = true;
    camera_feed_closed.hidden = false;

    STOPPED = true;

    start_button.disabled = false;
    stop_button.disabled = true;
    pause_button.disabled = true;
});
