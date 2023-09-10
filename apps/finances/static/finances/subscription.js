function makeSubscription(stripe_publishable_key, price_amount, price_id, redirect_url) {
    document.addEventListener("DOMContentLoader", function(event) {
        const stripe = Stripe(stripe_publishable_key);
        
        const options = {
          mode: 'subscription',
          amount: price_amount,
          currency: 'usd',
          // Fully customizable with appearance API.
          appearance: {/*...*/},
        };
        
        // Set up Stripe.js and Elements to use in checkout form
        const elements = stripe.elements(options);
        
        // Create and mount the Payment Element
        const paymentElement = elements.create('payment');
        paymentElement.mount('#payment-element');
        
        const form = document.getElementById('payment-form');
        const submitBtn = document.getElementById('submit_btn');
        
        const handleError = (error) => {
          const messageContainer = document.querySelector('#stripe-error_msg');
          messageContainer.textContent = error.message;
          submitBtn.disabled = false;
        }
        
        form.addEventListener('submit', async (event) => {
          // We don't want to let default form submission happen here,
          // which would refresh the page.
          event.preventDefault();
        
          // Prevent multiple form submissions
          if (submitBtn.disabled) {
            return;
          }
        
          // Disable form submission while loading
          submitBtn.disabled = true;
        
          // Trigger form validation and wallet collection
          const {error: submitError} = await elements.submit();
          if (submitError) {
            handleError(submitError);
            return;
          }
        
          // Create the subscription
          const res = await fetch('/pricing/'+price_id+'/payment/', {
            method: "POST",
          });
          const data = await res.json();
          const type = data["type"]
          const clientSecret = data["clientSecret"]
          const confirmIntent = type === "setup" ? stripe.confirmSetup : stripe.confirmPayment;
        
          // Confirm the Intent using the details collected by the Payment Element
          const {error} = await confirmIntent({
            elements,
            clientSecret,
            confirmParams: {
              return_url: redirect_url,
            },
          });
        
          if (error) {
            // This point is only reached if there's an immediate error when confirming the Intent.
            // Show the error to your customer (for example, "payment details incomplete").
            handleError(error);
          } else {
            // Your customer is redirected to your `return_url`. For some payment
            // methods like iDEAL, your customer is redirected to an intermediate
            // site first to authorize the payment, then redirected to the `return_url`.
            
            // If 3D security is not handle, should retrieve the payment intent clientSecret then pass it to stripe.confirmCardPayment(client_secret)
            
            // Retrieve the PaymentIntent
            stripe.retrievePaymentIntent(clientSecret).then(({paymentIntent}) => {
              const message = document.querySelector('#message')
            
              // Inspect the PaymentIntent `status` to indicate the status of the payment
              // to your customer.
              //
              // Some payment methods will [immediately succeed or fail][0] upon
              // confirmation, while others will first enter a `processing` state.
              //
              // [0]: https://stripe.com/docs/payments/payment-methods#payment-notification
              switch (paymentIntent.status) {
            
                case 'processing':
                  handleError({message: "Payment processing. We'll update you when payment is received."});
                  break;
            
                case 'requires_payment_method':
                  handleError({message: "Payment failed. Please try another payment method."});
                  // Redirect your user back to your payment page to attempt collecting
                  // payment again
                  break;
            
                case 'requires_action':
                    stripe.confirmCardPayment(clientSecret).then(function(result) {
                        if (result.error) {
                            handleError(result.error);
                            break
                        }
                    });
        
                default:
                  handleError({message: "Something went wrong."});
                  break;
              }
            });
          }
        });
        
    })
}) 