"use strict";

var img = new Image();
img.src = 'static/empty_board.jpg';

const turn = document.getElementById("turn");
const resign = document.getElementById("resign");
const canvas = document.getElementById('go-board');
var winner;
var context = canvas.getContext("2d");


img.onload = function ()
{
    console.log("Image loaded successfully.");
    context.drawImage(img, 0, 0);
};

// turn.addEventListener('click', function(event) {
//     event.preventDefault();   
//     fetch('/turn', {
//         method: 'GET',
//     }).then(function(data) {
//         turn.textContent = data.turn
//     });
// });

// winner.addEventListener(function(event) {
//     event.preventDefault();   
//     fetch('/win', {
//         method: 'GET',
//     }).then(function(response) {
//         response.json().then(function(data){
//             winner = data;
//         })
//     });
// });

// resign.addEventListener(function(event) {
//     event.preventDefault();   
//     fetch('/resign', {
//         method: 'POST',
//     }).then(function(response){
//         if(response.status == 204){
//             if(winner == "BLACK"){
//                 turn.textContent = "WHITE resigned. BLACK wins."
//             }
//             else{
//                 turn.textContent = "BLACK resigned. WHITE wins."
//             }
//         }
//     });
// });


canvas.addEventListener('mousedown', function(event) {
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    // Calculate the board coordinates
    const boardX = Math.floor((x / rect.width) * 20);
    const boardY = Math.floor((y / rect.height) * 20);

    console.log(`Clicked on Go board at (${boardX}, ${boardY})`);
    
//      // Send the click coordinates to the Flask backend
//      fetch(`/play_stone?x=${boardX}&y=${boardY}`, { method: 'POST' })
//      .then(response => response.json())
//      .then(data => {
//          // Update the board based on the response from the backend
//          // You may need to implement this part based on your go library
//          console.log(data);
//      });

// // Draw your initial empty board or load it from an image
// // You can use the ctx.fillStyle and ctx.fillRect() methods for this
});
