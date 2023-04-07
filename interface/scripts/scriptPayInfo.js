document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('form').addEventListener('submit', function(e) {
      e.preventDefault();
      sendData();
    });
  });
  

function sendData() {
    //mettre a jour la commande avec les infos de livraison
    let orderId = JSON.parse(localStorage.getItem("orderId"));
    var card_name = document.getElementById("card_name").value;
    var card_number = document.getElementById("card_number").value;
    var expiration_month = document.getElementById("card_date_month").value;
    var expiration_year = document.getElementById("card_date_year").value;
    var cvv = document.getElementById("card_cvv").value;
    var order = {
        "name": card_name,
        "number": card_number,
        "expiration_month": expiration_month,
        "expiration_year": expiration_year,
        "cvv": cvv
    };
    //envoyer la commande au serveur et récupérer la réponse si il y en a une
    fetch("http://localhost:5000/order/" + orderId, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ "credit_card": order }),
    })
        //si le paiment a été accepté l'api renvoie juste un code 200, sinon on affiche l'erreur
        .then((response) => {
            if (response.status == 202) {
                window.location.href = "order.html";
            } else {
                //on récupère le message d'erreur de l'api
                response.json().then((data) => {
                    alert("Erreur : " + data.errors.order.name);
                });
            }
        });
             
  }