"use strict";

var img = new Image();
img.src = 'static/empty_board.jpg';

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