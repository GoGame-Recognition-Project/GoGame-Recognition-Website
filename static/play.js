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

