var stripe = Stripe(checkout_publick_key);

const buy_btn = document.querySelector('#buy_btn');

buy_btn.addEventListener('click', event => {
    stripe.redirectToCheckout({
        sessionId: checkout_session_id
    }).then(function (result) {
        // If redirectToCheckout fails
    });
});