"use strict";


// window.onload = function() {
//     const nav = document.getElementById("move")
//     // const mainList = document.getElementById("mainList")
//     nav.onsubmit = function(event) {
//         event.preventDefault();
//         console.log("listening");
//         fetch("/sgf_controls", {
//             method: "GET"
//         })
//         .then(response => {
//             console.log(response);
//             // return response.blob();
//         })
//         .then(data => {
//             // let a = document.createElement("a");
//             // a.href = window.URL.createObjectURL(data);
//             // a.download = "numbers.txt";
//             // a.click();
//         })
//         // .then(() => {
//         //     fetch("/process-list", {
//         //         method: "GET"
//         //     })
//         //     .then(response => {
//         //         return response.text();
//         //     })
//         //     .then(html => {
//         //         mainList.innerHTML = html
//         //     })
//         // })
//     }
// }


// var next = document.getElementById("next");
// next.addEventListener('click', function(event) {
//     event.preventDefault();    // prevent page from refreshing
//     console.log(next);
//     fetch('/next', {
//         method: 'POST',
//         body: "",
//     }).then(function(response) {});
// });

var controls = document.getElementById("controls");
controls.addEventListener('click', function(event) {
    event.preventDefault();
    
    const target = event.target.id;
    if(!(["initial", "previous", "next", "last"].includes(target))){
        console.log("not included");
        return;
    }
    console.log(event.target.id);
    fetch('/controls', {
        method: 'POST',
        body: target,
    }).then(function(response) {});
});

var load_form = document.getElementById("load_form");
// const mainList = document.getElementById("mainList")
load_form.addEventListener("submit", function(event) {
    event.preventDefault();    // prevent page from refreshing
    const form_data = new FormData(load_form)
    console.log(load_form);
    fetch('/upload', {
        method: 'POST',
        body: form_data,
    }).then(function(response) {
        console.log("got response");
        console.log(response);
    });
});

    // console.log("listening");
    // fetch("/sgf_controls", {
    //     method: "GET"
    // })
    // .then(response => {
    //     console.log(response);
    //     // return response.blob();
    // })
    // .then(data => {
    //     // let a = document.createElement("a");
    //     // a.href = window.URL.createObjectURL(data);
    //     // a.download = "numbers.txt";
    //     // a.click();
    // })
    // // .then(() => {
    // //     fetch("/process-list", {
    // //         method: "GET"
    // //     })
    // //     .then(response => {
    // //         return response.text();
    // //     })
    // //     .then(html => {
    // //         mainList.innerHTML = html
    // //     })
    // // })
