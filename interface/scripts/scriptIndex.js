//récupérer les produits de l'API au chargement de la page index.html
window.onload = function () {
    getProducts();
};

//fonction pour récupérer les produits de l'API
function getProducts() {
    fetch("http://localhost:5000")
        .then((response) => response.json())
        .then((data) => {
            console.log(data);
            displayProducts(data);
        });
}

//fonction pour afficher les produits
function displayProducts(data) {
    let products = data.products;
    let productsTable = document.querySelector("tbody");
    products.forEach((product) => {
        productsTable.innerHTML += `
            <tr class="product">
                <td class="product_name">${product.name}</td>
                <td class="product_price">${product.price}</td>
                <td class="product_description">${product.description}</td>
                <td class="product_type">${product.type}</td>
                <td class="product_weight">${product.weight}</td>
                <td><input type="number" name="quantity" id="quantity${product.id}" min="0" max="100" value=0></td>
                <td><input type="button" id="add${product.id}" value="Ajouter" onclick="addProduct(${product.id},document.querySelector('#quantity${product.id}').value)"></td>
            </tr>
        `;
        if (product.in_stock == false) {
            document.getElementById("quantity" + product.id).disabled = true;
            document.getElementById("add" + product.id).disabled = true;
        }

    });
}

//fonction pour ajouter un produit au panier
function addProduct(productid, quantity) {
    //on vérifie que la quantité est supérieure à 0
    if (quantity <= 0) {
        alert("La quantité doit être supérieure à 0");
        return;
    }
    let productToAdd = {
        id : productid,
        quantity: parseInt(quantity)
    };
    let cart = JSON.parse(localStorage.getItem("cart"));
    if (cart == null) {
        cart = [];
    }
    //on vérifie si le produit est déjà dans le panier
    let productAlreadyInCart = false;
    cart.forEach((product) => {
        if (product.id == productToAdd.id) {
            productAlreadyInCart = true;
            product.quantity += productToAdd.quantity;
        }
    });
    if (!productAlreadyInCart) {
        cart.push(productToAdd);
    }
    localStorage.setItem("cart", JSON.stringify(cart));
    alert("Le produit a bien été ajouté au panier");
}



