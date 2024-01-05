"use strict";
var board = new Image();
board.src = 'static/empty_board.jpg';

const controls = document.getElementById("controls");
const plot_image = document.getElementById("go-board");
const camera_feed_closed = document.getElementById("camera-feed-closed");

const message = document.getElementById("message");
const start_button = document.getElementById("start-button");
const stop_button = document.getElementById("stop-button");
const pause_button = document.getElementById("pause-button");
const undo_button = document.getElementById("undo");

var context_image = plot_image.getContext("2d");
var updateLoop = null;


var STARTED = false;
var STOPPED = false;
var PAUSED = false;
var QUIT = false;

board.onload = function ()
{
    context_image.drawImage(board, 0, 0);
};


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

undo_button.addEventListener('click', function(event) {
    event.preventDefault();   
    console.log("clicked")
    fetch('/undo', {
        method: 'POST',
    }).then(function(response) {
        if (response.status === 204) {
            console.log("Undone");
            update_state()
        }
        else {
            message.textContent = "There are no moves left";
        }
    });
});


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

var canvas = document.getElementById('canvas');
var context = canvas.getContext('2d');
const video = document.getElementById("videoElement");

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
    console.log("start");
    
    if (navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
        .then(function (stream) {
            video.srcObject = stream;
            video.play();

            fetch('/initialize_new_game').then(function(response){
                if(response.status == 204){
                    console.log("New game was initialized");

                    QUIT = false;       
                    PAUSED = false;

                    start_button.disabled = true;
                    stop_button.disabled = false;
                    pause_button.disabled = false;

                    camera_feed_closed.hidden = true;
                    video.hidden = false;

                    update_state_loop();
                } else {
                    alert("Error initializing new game, please try again");
                }
            })
        })
        .catch(function (error) {
            alert('Video feed failed to start');
        });
    }
});


stop_button.addEventListener('click', function(event) {
    event.preventDefault();
    console.log("stop");
    QUIT = true;
    PAUSED = false;

    video.srcObject.getVideoTracks()[0].stop();

    video.hidden = true;
    camera_feed_closed.hidden = false;

    STOPPED = true;

    pause_button.innerHTML = "Pause";

    start_button.disabled = false;
    stop_button.disabled = true;
    pause_button.disabled = true;
});


pause_button.addEventListener('click', function(event) {
    event.preventDefault();
    console.log("pause");
    if(PAUSED){
        QUIT = false;
        PAUSED = false;
        pause_button.innerHTML = "Pause";

        start_button.disabled = true;
        stop_button.disabled = false;

        video.play();
        update_state_loop();
        
    }else{
        QUIT = true;
        PAUSED = true;
        pause_button.innerHTML = "Resume";

        video.pause();

        start_button.disabled = true;
        stop_button.disabled = false;
    }
});