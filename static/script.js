"use strict";
var board = new Image();
board.src = 'static/empty_board.jpg';

const controls = document.getElementById("controls");
const start_button = document.getElementById("start-button");
const stop_button = document.getElementById("stop-button");
const pause_button = document.getElementById("pause-button");
const undo_button = document.getElementById("undo");
const resign_button = document.getElementById("resign");
const download_sgf_button = document.getElementById("download-sgf");
const rules_button = document.getElementById("flexSwitchCheckDefault");

const video = document.getElementById("videoElement");

var video_canvas = document.getElementById('canvas');
var video_context = video_canvas.getContext('2d');
const plot_canvas = document.getElementById("go-board");
const plot_context = plot_canvas.getContext("2d");
const camera_feed_closed = document.getElementById("camera-feed-closed");
const message = document.getElementById("message");

var updateLoop = null;

var STARTED = false;
var STOPPED = false;
var PAUSED = false;
var QUIT = false;

board.onload = function (){
    plot_context.drawImage(board, 0, 0);
};

window.onbeforeunload = function(event) {
    fetch('/set_config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({STARTED: STARTED, STOPPED: STOPPED, PAUSED: PAUSED, QUIT: QUIT}),
    }).then(function(response){
        console.log("failed setting config");
    })
}

fetch("/get_config").then(function(response){
    response.json().then(function(data){
        STARTED = data.STARTED;
        STOPPED = data.STOPPED;
        PAUSED = data.PAUSED;
        QUIT = data.QUIT;        
        if(STOPPED){
            console.log("stopped");
            update_state();
            start_button.disabled = false;
            stop_button.disabled = true;
            pause_button.disabled = true;

            resign_button.disabled = true;
            undo_button.disabled = true;

            camera_feed_closed.hidden = false;
        } else if (STARTED) {
            console.log("started");
            if (navigator.mediaDevices.getUserMedia) {
                navigator.mediaDevices.getUserMedia({ video: true })
                .then(function (stream) {
                    video.srcObject = stream;
                    video.play();

                    resign_button.disabled = false;
                    undo_button.disabled = false;

                    video.hidden = false;
                    camera_feed_closed.hidden = true;
                    if(PAUSED){
                        console.log("pause");
                        update_state();
                        start_button.disabled = true;
                        stop_button.disabled = false;
                        pause_button.disabled = false;

                        pause_button.innerHTML = "Resume";
                        // video.pause();
                    } else {
                        console.log("continue");
                        update_state_loop();
                        start_button.disabled = true;
                        stop_button.disabled = false;
                        pause_button.disabled = false;
                    }
                })
            }
        }
    })
})

async function update_state(){
    var video_height = video.videoHeight;
    var video_width = video.videoWidth;
    var width = video_width;
    var height = video_height;
    video_canvas.width = video_width;
    video_canvas.height = video_height;
    video_context.drawImage(video, 0, 0, width, height);
    var data = video_canvas.toDataURL('image/jpeg', 0.5);
    video_context.clearRect(0, 0, width, height);

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
    fetch('/undo', {
        method: 'POST',
    }).then(function(response) {
        if (response.status === 204) {
            console.log("Undone");
            update_state()
        }
        else {
            message.textContent = "There are no moves left";
            console.log("There are no moves left");
        }
    });
});

resign_button.addEventListener('click', function(event) {
    event.preventDefault();   
    fetch('/resign', {
        method: 'POST',
    }).then(function(response){
        if(response.status == 204){
            undo_button.disabled = true;
        } else {
            console.log("Cannot resign");
        }
    });
});

rules_button.addEventListener("change", function(){
    if (rules_button.checked) {
        fetch('/set_rules', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({TRANSPARENT_MODE: false}),
        }).then(function(response){
            if(response.status == 204){
                undo_button.disabled = false;
                resign_button.disabled = false;
                download_sgf_button.disabled = false;
            } else {
                console.log("Cannot set rules");
            }
        });
    } else {
        fetch('/set_rules', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({TRANSPARENT_MODE: true}),
        }).then(function(response){
            if(response.status == 204){
                undo_button.disabled = true;
                resign_button.disabled = true;
                download_sgf_button.disabled = true;
            } else {
                console.log("Cannot remove rules");
            }
        });
    }
})


download_sgf_button.addEventListener("click", function() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/get_sgf_txt', true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
            var blob = new Blob([xhr.responseText], { type: 'text/plain' });
            
            saveAs(blob, 'game.sgf');
        } else {
            console.log("The Sgf file is empty")
        }
    };
    xhr.send();
})


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
                    STARTED = true;
                    STOPPED = false;

                    resign_button.disabled = false;
                    undo_button.disabled = false;

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
    STOPPED = true;

    video.srcObject.getVideoTracks()[0].stop();

    video.hidden = true;
    camera_feed_closed.hidden = false;

    STOPPED = true;

    pause_button.innerHTML = "Pause";

    resign_button.disabled = true;
    undo_button.disabled = true;

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