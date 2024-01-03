


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


var next = document.getElementById("next")
// const mainList = document.getElementById("mainList")
next.addEventListener('click', function(event) {
    event.preventDefault();    // prevent page from refreshing
    console.log(next);
    fetch('/next', {   // assuming the backend is hosted on the same server
        method: 'POST',
        body: "",
    }).then(function(response) {
        // do something with the response if needed.
        // If you want the table to be built only after the backend handles the request and replies, call buildTable() here.
    });
});

// var load = document.getElementById("load_sgf")
// // const mainList = document.getElementById("mainList")
// load.addEventListener('click', function(event) {
//     event.preventDefault();    // prevent page from refreshing
//     console.log(next);
//     fetch('/next', {   // assuming the backend is hosted on the same server
//         method: 'POST',
//         body: "next move",
//     }).then(function(response) {
//         // do something with the response if needed.
//         // If you want the table to be built only after the backend handles the request and replies, call buildTable() here.
//     });
// });

var load_form = document.getElementById("load_form")
// const mainList = document.getElementById("mainList")
load_form.addEventListener("submit", function(event) {
    event.preventDefault();    // prevent page from refreshing
    const form_data = new FormData(load_form)
    console.log(load_form);
    fetch('/upload', {   // assuming the backend is hosted on the same server
        method: 'POST',
        body: form_data,
    }).then(function(response) {
        console.log("got response");
        console.log(response);
        // do something with the response if needed.
        // If you want the table to be built only after the backend handles the request and replies, call buildTable() here.
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
