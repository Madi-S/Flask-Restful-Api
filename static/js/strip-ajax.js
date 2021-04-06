const buy_btn = document.querySelector('#buy_btn');

buy_btn.addEventListener('click', event => {
    fetch('/stripe-pay')
    .then((result) => { return result.json(); })
    .then((data) => {
        var stripe = Stripe(data.checkout_publick_key);
        stripe.redirectToCheckout({
            sessionId: data.checkout_session_id
        }).then(function (result) {
            // If redirectToCheckout fails
        });
    })
});