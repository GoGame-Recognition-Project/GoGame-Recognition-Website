"use strict";

var board = new Image();
board.src = 'static/empty_board.jpg';

const turn = document.getElementById("turn");
const resign = document.getElementById("resign");
const start = document.getElementById("start-game");
const canvas = document.getElementById('go-board');
var winner;
var context = canvas.getContext("2d");


board.onload = function ()
{
    context.drawImage(board, 0, 0);
};

start.addEventListener('click', function(event) {
    event.preventDefault();   
    fetch('/start_play', {
        method: 'POST',
    }).then(function(response){
        if(response.status == 204){
            turn.textContent = "Game started! BLACK to play"
        }
    });
});



resign.addEventListener('click', function(event) {
    event.preventDefault();   
    fetch('/resign', {
        method: 'POST',
    }).then(function(response){
        if(response.status == 204){
            if(winner == "BLACK"){
                turn.textContent = "WHITE resigned. BLACK wins.";
            }
            else{
                turn.textContent = "BLACK resigned. WHITE wins.";
            }
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
                console.log("played")
                update_state();
                console.log("updated")

            }
    });
});

function update_state(){
    fetch('/update_state').then(function(response){
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
function get_winner(){ 
    fetch('/win', {
        method: 'GET',
    }).then(function(response) {
        response.json().then(function(data){
            winner = data;
        })
    });
}