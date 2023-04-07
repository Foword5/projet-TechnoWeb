//AU CHARGEMENT DE LA PAGE
window.onload = function () {
// Récupération de l'ID de la commande depuis le localStorage
const orderId = localStorage.getItem("orderId");

// Requête GET vers l'API pour récupérer les informations de la commande
    fetch(`http://localhost:5000/order/${orderId}`)
    .then(response => response.json())
    .then(data => {
            // Création des éléments HTML pour afficher les informations de la commande
            const orderInfo = document.getElementById("order-info");

            const orderIdElement = document.createElement("p");
            orderIdElement.textContent = `Numéro de commande: ${data.id}`;
            orderInfo.appendChild(orderIdElement);

            const paidElement = document.createElement("p");
            paidElement.textContent = `Payé: ${data.paid ? "Oui" : "Non"}`;
            orderInfo.appendChild(paidElement);

            const shippingInfoElement = document.createElement("div");
            const shippingAddressElement = document.createElement("p");
            shippingAddressElement.textContent = `Adresse de livraison: ${data.shipping_information.address}, ${data.shipping_information.postal_code}, ${data.shipping_information.city}, ${data.shipping_information.province}, ${data.shipping_information.country}`;
            shippingInfoElement.appendChild(shippingAddressElement);
            orderInfo.appendChild(shippingInfoElement);

            const shippingPriceElement = document.createElement("p");
            shippingPriceElement.textContent = `Coût avec livraison: ${data.shipping_price} $`;
            orderInfo.appendChild(shippingPriceElement);

            const totalPriceElement = document.createElement("p");
            totalPriceElement.textContent = `Total: ${data.total_price} $`;
            orderInfo.appendChild(totalPriceElement);

            const transactionElement = document.createElement("div");
            const amountChargedElement = document.createElement("p");
            amountChargedElement.textContent = `Montant facturé: ${data.transaction.amount_charged} $`;
            transactionElement.appendChild(amountChargedElement);
            const successElement = document.createElement("p");
            successElement.textContent = `Succès de la transaction: ${data.transaction.success ? "Oui" : "Non"}`;
            transactionElement.appendChild(successElement);
            orderInfo.appendChild(transactionElement);

            const productsElement = document.createElement("div");
            const productsTitleElement = document.createElement("h2");
            productsTitleElement.textContent = "Produits:";
            productsElement.appendChild(productsTitleElement);
            const productListElement = document.createElement("ul");
            data.products.forEach(product => {
                const productItemElement = document.createElement("li");
                productItemElement.textContent = `ID du produit: ${product.id}, Quantité: ${product.quantity}`;
                productListElement.appendChild(productItemElement);
            });
            productsElement.appendChild(productListElement);
            orderInfo.appendChild(productsElement);
    });
};