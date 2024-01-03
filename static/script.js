const startButton = document.getElementById('start-button');
var historique = document.getElementById('historique');


function demarrer(){
    const j1 = window.prompt("Quel est le nom du premier joueur ?");
    const j2 = window.prompt("Quel est le nom du second joueur ?");
    const desc = window.prompt("Description de la partie");
    if (sessionStorage.getItem("longueurHistorique") != null){
        var longueurHistorique = parseInt(sessionStorage.getItem("longueurHistorique"));
    }
    else{
        var longueurHistorique = 0;
    }
    var key1 = longueurHistorique*3;
    var key2 = longueurHistorique*3+1;
    var key3 = longueurHistorique*3+2;
    sessionStorage.setItem(key1.toString(),j1);
    sessionStorage.setItem(key2.toString(),j2);
    sessionStorage.setItem(key3.toString(),desc);
    longueurHistorique++;
    sessionStorage.setItem("longueurHistorique",longueurHistorique.toString());
}

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
    
    
function save(){
    sessionStorage.setItem('key', document.getElementById('historique').innerHTML)
    alert("Sauvegarde effectuée !");    
}
    
function reset(){
    if (window.confirm("Voulez-vous vraiment supprimer la sauvegarde ?")){
        sessionStorage.removeItem('key');
    }
}
    
