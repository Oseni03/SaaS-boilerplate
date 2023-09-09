function _3dsec(stripe_publishable_key, client_secret) {
    document.addEventListener("DOMContentLoaded", function(event) {
        var stripe = Stripe(stripe_publishable_key);
        
        stripe.confirmCardPayment(client_secret).then(function(result) {
            if (result.error) {
                $("3ds_result").text("Error!");
                $("3ds_result").addClass("text-danger");
            } else {
                $("3ds_result").text("Payment successful. Check your subscription page for more details");
                $("3ds_result").addClass("text-success");
            }
        });
    });
}