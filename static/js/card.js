function card(stripe_publishable_key, customer_email {
    document.addEventListener("DOMContentLoader", function(event) {
        var stripe = Stripe(stripe_publishable_key);
        var elements = stripe.elements();
        
        var style = {
            base: {
                color: "#32325d",
                fontFamily: "Helvetica Neue", "Helvetica, sans-serif",
                fontSmoothing: "antialiased",
                fontSize: "16px",
                "::placeholder": {
                    color: "#aab7c4"
                }
            },
            invalid: {
                color: "#fa755a",
                iconColor: "#fa755a",
            }
        };
        
        // Create an instance of the card element 
        var card = elements.create("card", {style: style});
        
        card.mount("#card-element");
        
        // Handle real-time error validation 
        card.addEventListener("change", function(event) {
            var displayError = document.getElementById("card-errors");
            
            if (event.error) {
                displayError.textContent = event.error.message;
            } else {
                displayError.textContent = "";
            }
        });
        
        // Handle form submission 
        var form = document.getElementById("payment-form");
        form.addEventListener("submit", function(event) {
            event.preventDefault();
            
            strip.createToken(card).then(function(result) {
                if (result.error) {
                    var errorElement = document.getElementById("card-errors");
                    errorElement.textContent = result.error.message;
                } else {
                    // Create payment method
                    stripe.createPaymemtMethod({
                        type: "card",
                        card: card,
                        billing_details: {
                            email: customer_email,
                        }
                    }).then(function(payment_method_result) {
                        if (payment_method_result.error) {
                            var errorElement = document.getElementById("card-errors");
                            errorElement.textContent = payment_method_result.error.message;
                        } else {
                            var form = document.getElementById('payment-form');
                            var hidden_input = document.createElement("input");
                            
                            hidden_input.setAttribute("type", "hidden");
                            hidden_input.setAttribute("name", "payment_method_name");
                            hidden_input.setAttribute("value", payment_method_result.paymentMethod.id);
                            form.appenChild(hidden_input);
                            form.submit();
                        }
                    })
                }
            })
        })
    })
}) 