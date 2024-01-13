"use strict";

var board = new Image();
board.src = 'static/empty_board.jpg';

const controls = document.getElementById("controls");

const turn = document.getElementById("turn");
const resign_button = document.getElementById("resign");
const start_button = document.getElementById("start-game");
const undo_button = document.getElementById("undo");
const download_sgf_button = document.getElementById("download-sgf");

const board_canvas = document.getElementById('go-board');
const board_context = board_canvas.getContext("2d");
const hover_canvas = document.getElementById("hover-canvas");
const hover_context = hover_canvas.getContext("2d");

hover_canvas.width = board_canvas.offsetWidth;
hover_canvas.height = board_canvas.offsetHeight;
// board_canvas.onresize = function(event){
//     hover_canvas.width = board_canvas.offsetWidth;
//     hover_canvas.height = board_canvas.offsetHeight;
// }
window.addEventListener("resize", (event) => {
    hover_canvas.width = board_canvas.offsetWidth;
    hover_canvas.height = board_canvas.offsetHeight;
});

var winner;
var selectedStone = {x: null, y:null, posx: null, posy: null};

// undo_button.disabled = true;
// resign_button.disabled = true;
// download_sgf_button.disabled = true;

board.onload = function (){
    board_context.drawImage(board, 0, 0);
};

start_button.addEventListener('click', function(event) {
    event.preventDefault();   
    fetch('/start_play', {
        method: 'POST',
    }).then(function(response){
        if(response.status == 204){
            turn.textContent = "Game started! BLACK to play"
            board.src = 'static/empty_board.jpg';
            board_context.drawImage(board, 0, 0);
            undo_button.disabled = false;
            resign_button.disabled = false;
            download_sgf_button.disabled = false;
        }
    });
});


undo_button.addEventListener('click', function(event) {
    event.preventDefault();
    fetch('/undo', {
        method: 'POST',
    }).then(function(response) {
        if (response.status === 204) {
            update_state()
            update_turn()
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

hover_canvas.addEventListener('mousedown', function(event) {
    event.preventDefault();   
    const rect = board_canvas.getBoundingClientRect();
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
            board_context.drawImage(board, 0, 0);
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

// download_sgf_button.addEventListener("click", function() {
//     var xhr = new XMLHttpRequest();
//     xhr.open('GET', '/get_sgf_txt', true);
//     xhr.onreadystatechange = function () {
//         if (xhr.readyState == 4 && xhr.status == 200) {
//             var blob = new Blob([xhr.responseText], { type: 'text/plain' });
            
//             saveAs(blob, 'game.sgf');
//         } else {
//         }
//     };
//     xhr.send();
// })

download_sgf_button.addEventListener("click", function() {
    fetch('/get_sgf_txt', {
        method: 'GET',
    }).then(function(response){
        response.json().then(function(data){
            var blob = new Blob([data.sgf], { type: 'text/plain' });
            if(window.navigator.msSaveOrOpenBlob) {
                window.navigator.msSaveBlob(blob, "game.sgf");
            }
            else{
                const elem = window.document.createElement('a');
                elem.href = window.URL.createObjectURL(blob);
                elem.download = "game.sgf";        
                document.body.appendChild(elem);
                elem.click();        
                document.body.removeChild(elem);
            }
        })
    })
})



hover_canvas.addEventListener('mousemove', function(event) {
    event.preventDefault();
    var x, y, posx, posy;
    [x, y, posx, posy] = get_closest_intersection(event.clientX, event.clientY);

    draw_hover(posx, posy);
});


function draw_hover(x, y){
    const square_size = hover_canvas.width / 20;
    hover_context.clearRect(0, 0, hover_canvas.width, hover_canvas.height);
    hover_context.fillStyle = 'rgba(252, 107, 3, 0.5)';
    hover_context.lineWidth = 3;

    if(x % 600 != 0 & y % 600 != 0){
        hover_context.beginPath();
        hover_context.arc(x, y, square_size / 2 + 4, 0, 2 * Math.PI);
        hover_context.fill();
    }
}

function get_closest_intersection(x, y){
    const rect = hover_canvas.getBoundingClientRect();
    const square_size = hover_canvas.width / 20;

    const scaleX = hover_canvas.width / rect.width;
    const scaleY = hover_canvas.height / rect.height;  

    var x = (x - rect.left) * scaleX;
    var y = (y - rect.top) * scaleY;

    var posx = Math.round(x / square_size) * square_size;
    var posy = Math.round(y / square_size) * square_size;

    var stonex = Math.round((posx / rect.width) * 20);
    var stoney = Math.round((posy / rect.height) * 20);

    return [stonex, stoney, posx, posy];
}