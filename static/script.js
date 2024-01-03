


window.onload = function() {
    const navigation1 = document.getElementById("navigation1")
    // const mainList = document.getElementById("mainList")
    navigation1.onsubmit = function(event) {
        event.preventDefault();
        fetch("/sgf_controls", {
            method: "GET"
        })
        .then(response => {
            // return response.blob();
        })
        .then(data => {
            // let a = document.createElement("a");
            // a.href = window.URL.createObjectURL(data);
            // a.download = "numbers.txt";
            // a.click();
        })
        // .then(() => {
        //     fetch("/process-list", {
        //         method: "GET"
        //     })
        //     .then(response => {
        //         return response.text();
        //     })
        //     .then(html => {
        //         mainList.innerHTML = html
        //     })
        // })
    }
}