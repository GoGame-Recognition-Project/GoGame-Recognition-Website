"use strict";

var board = new Image();
board.src = 'static/empty_board.jpg';

const controls = document.getElementById("controls");

const turn = document.getElementById("turn");
const resign_button = document.getElementById("resign");
const start_button = document.getElementById("start-game");
const undo_button = document.getElementById("undo");
const download_sgf_button = document.getElementById("download-sgf");

const canvas = document.getElementById('go-board');
var context = canvas.getContext("2d");
var winner;

// undo_button.disabled = true;
// resign_button.disabled = true;
// download_sgf_button.disabled = true;

board.onload = function (){
    context.drawImage(board, 0, 0);
};

start_button.addEventListener('click', function(event) {
    event.preventDefault();   
    fetch('/start_play', {
        method: 'POST',
    }).then(function(response){
        if(response.status == 204){
            turn.textContent = "Game started! BLACK to play"
            board.src = 'static/empty_board.jpg';
            context.drawImage(board, 0, 0);
            undo_button.disabled = false;
            resign_button.disabled = false;
            download_sgf_button.disabled = false;
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
            update_state()
            update_turn()
            console.log("Undone");
        }
        else {
            message.textContent = "There are no moves left";
        }
    });
});

resign_button.addEventListener('click', function(event) {
    event.preventDefault();   
    fetch('/resign', {
        method: 'POST',
    }).then(function(response){
        if(response.status == 204){
            update_turn()
            undo_button.disabled = true;
        }
    });
});

canvas.addEventListener('mousedown', function(event) {
    event.preventDefault();   
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    // Calculate the board coordinates
    const boardX = Math.round((x / rect.width) * 20);
    const boardY = Math.round((y / rect.height) * 20);
    
    fetch(`/play_stone?x=${boardX}&y=${boardY}`, {
        method: 'POST',
        }).then(function(response){
            if(response.status == 204){
                update_state();
                update_turn();
            }
    });
});

controls.addEventListener('click', function(event) {
    event.preventDefault();
    const target = event.target.id;
    if(!(["initial", "previous", "next", "last"].includes(target))){
        return;
    }
    fetch('/controls', {
        method: 'POST',
        body: target,
    }).then(function(response) {
        if(response.status == 204){
            update_state()
        }
    });
});

function update_state(){

    fetch('/update_state', {
        method: 'POST',
        headers: {'Content-Type': 'application/json',},
        body: JSON.stringify({}),
    }).then(function(response){
        response.json().then(function(data){
            board.src = 'data:image/jpeg;base64,' + data.image;
            board.onload = function () {
                context.drawImage(board, 0, 0);
            };
        })
    })
}

function update_turn(){ 
    fetch('/turn', {
        method: 'GET',
    }).then(function(response) {
        response.json().then(function(data){
            turn.textContent = data.turn;
        })
    });
}
async function get_winner(){ 
    fetch('/win', {
        method: 'GET',
    }).then(function(response) {
        response.json().then(function(data){
            winner = data.winner;
            console.log("winner function", winner)
        })
    });
}

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