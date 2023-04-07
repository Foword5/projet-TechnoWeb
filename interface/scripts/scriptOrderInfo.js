document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('form').addEventListener('submit', function(e) {
      e.preventDefault();
      sendData();
    });
  });
  

function sendData() {
    //mettre a jour la commande avec les infos de livraison
    let orderId = JSON.parse(localStorage.getItem("orderId"));
    var address = document.getElementById("address").value;
    var city = document.getElementById("city").value;
    var province = document.getElementById("province").value;
    var country = document.getElementById("country").value;
    var postal_code = document.getElementById("postal_code").value;
    var email = document.getElementById("email").value;
    var order = {
        "email": email,
        "shipping_information": {
            "country": country,
            "address": address,
            "postal_code": postal_code,
            "city": city,
            "province": province
        }
    };
    //envoyer la commande au serveur et gérer les erreurs si il y en a
    fetch("http://localhost:5000/order/" + orderId, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ "order": order }),
    })
        .then((response) => response.json())
        //si la commande a été créée, on affiche le numéro de commande, sinon on affiche l'erreur
        .then((data) => {
            if (data.id) {
                window.location.href = "orderPay.html";
            } else {
                alert("Erreur : " + data.errors.order.name);
            }
        });   
  }