var historique = document.getElementById('historique');
if (sessionStorage.getItem("key") != null){
    document.getElementById("historique").innerHTML = sessionStorage.getItem('key');
    historique = document.getElementById('historique');
}
var urls = [];

var longueurHistorique = sessionStorage.getItem("longueurHistorique");
var nbParties = document.getElementById("nbParties");
nbParties.textContent = longueurHistorique;
creation();

function ajout(texte1,texte2,texte3) {
    var table = document.getElementById("historique").getElementsByTagName('tbody')[0];
    var newRow = table.insertRow(longueurHistorique);

    var dateCell = newRow.insertCell(0);
    var text1Cell = newRow.insertCell(1);
    var text2Cell = newRow.insertCell(2);
    var text3Cell = newRow.insertCell(3);
    var actionCell = newRow.insertCell(4);

    var currentDate = new Date();
    dateCell.innerHTML = currentDate.toLocaleDateString();

    text1Cell.innerHTML = texte1;
    text2Cell.innerHTML = texte2;
    text3Cell.innerHTML = texte3;
    urls.push("https://www.example1.com");
    var linkButton = document.createElement("button");
            linkButton.innerHTML = "Détails";
            linkButton.onclick = function () {
                // Obtenir l'indice de la ligne pour déterminer l'URL correspondante
                var rowIndex = newRow.rowIndex - 1; // Soustrayez 1 pour gérer l'en-tête
                if (rowIndex >= 0 && rowIndex < urls.length) {
                    var newTab = window.open(urls[rowIndex], "_blank"); // Ouvre dans un nouvel onglet
                    newTab.focus();
                }
            };
    actionCell.appendChild(linkButton);
    var longueurHistorique = document.getElementById("historique").getElementsByTagName('tbody')[0].rows.length;
    var nbParties = document.getElementById("nbParties");
    nbParties.textContent = longueurHistorique;
    sessionStorage.setItem("longueurHistorique",longueurHistorique.toString());
}

function creation() {
    var longueurTab = document.getElementById("historique").getElementsByTagName('tbody')[0].rows.length;
    for (i=0; i<longueurTab; i++) {
        supprimerLigne(0);
    }
    var longueurHistorique = sessionStorage.getItem("longueurHistorique");
    for (var i = parseInt(longueurHistorique)-1; i>=0 ; i--) {
        var table = document.getElementById("historique").getElementsByTagName('tbody')[0];
        var newRow = table.insertRow(parseInt(longueurHistorique)-1-i);
        var dateCell = newRow.insertCell(0);
        var text1Cell = newRow.insertCell(1);
        var text2Cell = newRow.insertCell(2);
        var text3Cell = newRow.insertCell(3);
        var actionCell1 = newRow.insertCell(4);
        var actionCell2 = newRow.insertCell(5);
        var currentDate = new Date();
        dateCell.innerHTML = currentDate.toLocaleDateString();
        var i1 = 3*i;
        var i2 = 3*i+1;
        var i3 = 3*i+2;
        text1Cell.innerHTML = sessionStorage.getItem(i1.toString());
        text2Cell.innerHTML = sessionStorage.getItem(i2.toString());
        text3Cell.innerHTML = sessionStorage.getItem(i3.toString());
        urls.push("https://www.example1.com");
        var linkButton1 = document.createElement("button");
        linkButton1.innerHTML = "Détails";
        var linkButton2 = document.createElement("button");
        linkButton2.innerHTML = "Modifier";
        linkButton1.onclick = function () {
            // Obtenir l'indice de la ligne pour déterminer l'URL correspondante
            var rowIndex = newRow.rowIndex - 1; // Soustrayez 1 pour gérer l'en-tête
            if (rowIndex >= 0 && rowIndex < urls.length) {
                var newTab = window.open(urls[rowIndex], "_blank"); // Ouvre dans un nouvel onglet
                newTab.focus();
            }
        };
        linkButton2.onclick = function (index) {
            return function () {
                modifier(index);
            };
        }(i);        
        actionCell1.appendChild(linkButton1);
        actionCell2.appendChild(linkButton2);
        var longueurHistorique = sessionStorage.getItem("longueurHistorique")
        var nbParties = document.getElementById("nbParties");
        nbParties.textContent = longueurHistorique;
    }
}

function actualiser(){
    let montantr = document.getElementById("montanthtml").value;
    if (window.confirm("Effectuer une opération de régularisation ?")){
        let différence = montantr - montant;
        let newRow = historique.insertRow(0);
        let newCell0 = newRow.insertCell(0);
        let newCell1 = newRow.insertCell(1);
        let newCell2 = newRow.insertCell(2);
        let newCell3 = newRow.insertCell(3);
        let newCell4 = newRow.insertCell(4);
        today = new Date();
        newCell0.appendChild(document.createTextNode((today.toLocaleDateString())));
        newCell1.appendChild(document.createTextNode("-"));
        newCell2.appendChild(document.createTextNode("Régularisation"));
        tab_montant.push(différence);
        newCell3.appendChild(document.createTextNode(différence));
        newCell4.appendChild(document.createTextNode("non"));
    }    
}

function modifier(k){
    const j1 = window.prompt("Quel est le nom du premier joueur ?");
    const j2 = window.prompt("Quel est le nom du second joueur ?");
    const desc = window.prompt("Description de la partie");
    var key1 = k*3;
    var key2 = k*3+1;
    var key3 = k*3+2;
    sessionStorage.setItem(key1.toString(),j1);
    sessionStorage.setItem(key2.toString(),j2);
    sessionStorage.setItem(key3.toString(),desc);
    creation();
    supprimerLigne(0);
}

function supprimerLigne(i){
    historique.deleteRow(i);
}


function save(){
    sessionStorage.setItem('key', document.getElementById('historique').innerHTML)
    alert("Sauvegarde effectuée !");

}

function reset(){
    if (window.confirm("Voulez-vous vraiment supprimer la sauvegarde ?")){
        longueurHistorique = sessionStorage.getItem("longueurHistorique");
        for (var i = 0; i<3*parseInt(longueurHistorique); i++) {
            sessionStorage.removeItem(i.toString());
        };
        sessionStorage.setItem("longueurHistorique", "0");
        creation();
    }
}
