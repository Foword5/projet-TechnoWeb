window.onload = function () {
    displayCart();
};

//fonction pour afficher le panier
function displayCart() {
    let cart = JSON.parse(localStorage.getItem("cart"));
    let cartTable = document.querySelector("tbody");
    cart.forEach((product) => {
        //récupérer les infos du produit via la requete pour recuperer tous les produits
        fetch("http://localhost:5000")
            .then((response) => response.json())
            .then((data) => {
                //on récupère le produit correspondant à l'id du produit dans le panier
                let productInfo = data.products.find((productInfo) => productInfo.id == product.id);
                //on ajoute les infos du produit au produit dans le panier
                product.name = productInfo.name;
                product.price = productInfo.price;
                product.description = productInfo.description;
                product.type = productInfo.type;
                product.weight = productInfo.weight;
                //on affiche le produit dans le panier
                cartTable.innerHTML += `
                    <tr class="product">
                        <td class="product_name">${product.name}</td>
                        <td class="product_price">${product.price}</td>
                        <td class="product_description">${product.description}</td>
                        <td class="product_type">${product.type}</td>
                        <td class="product_weight">${product.weight}</td>
                        <td class="product_quantity">${product.quantity}</td>
                        <td><input type="button" value="Supprimer" onclick="deleteProduct(${product.id})"></td>
                    </tr>
                `;
            }); 
    });
}

//fonction pour supprimer un produit du panier
function deleteProduct(productid) {
    let cart = JSON.parse(localStorage.getItem("cart"));
    let newCart = cart.filter((product) => product.id != productid);
    localStorage.setItem("cart", JSON.stringify(newCart));
    window.location.reload();
}

//fonction pour créer une commande avec une liste d'ids de produits et de quantité
function createOrder() {
    let cart = JSON.parse(localStorage.getItem("cart"));
    let products = [];
    cart.forEach((product) => {
        products.push({ "id": product.id, "quantity": product.quantity });
    });
    let order = { "products": products };
    //envoyer la commande au serveur et gérer les erreurs si il y en a
    fetch("http://localhost:5000/order", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(order),
    })
        .then((response) => response.json())
        .then((data) => {
            //on enregistre l'id de la commande dans le localstorage
            localStorage.setItem("orderId", data.id);
            //on redirige vers la page de confirmation
            window.location.href = "order.html";
        }
        )
        .catch((error) => {
            alert(error.errors.product.name);      
        });
    
}