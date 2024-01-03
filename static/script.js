


window.onload = function() {
    const mainForm = document.getElementById("mainForm")
    const mainList = document.getElementById("mainList")
    mainForm.onsubmit = function(event) {
        event.preventDefault();
        fetch("/process", {
            method: "GET"
        })
        .then(response => {
            return response.blob();
        })
        .then(data => {
            let a = document.createElement("a");
            a.href = window.URL.createObjectURL(data);
            a.download = "numbers.txt";
            a.click();
        })
        .then(() => {
            fetch("/process-list", {
                method: "GET"
            })
            .then(response => {
                return response.text();
            })
            .then(html => {
                mainList.innerHTML = html
            })
        })
    }
}