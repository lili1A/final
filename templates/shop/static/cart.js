// Persistent cart functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize cart toggle
    const cartSidebar = document.getElementById('cart-sidebar');
    const cartToggle = document.getElementById('cart-toggle');
    
    if (cartToggle) {
        cartToggle.addEventListener('click', function() {
            cartSidebar.classList.add('open');
        });
    }

    // Close sidebar when clicking outside
    document.addEventListener('click', function(event) {
        if (cartSidebar && !cartSidebar.contains(event.target) && event.target !== cartToggle) {
            cartSidebar.classList.remove('open');
        }
    });

    // AJAX add to cart functionality for all "Add to Cart" buttons
    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const form = this.closest('form');
            
            fetch(form.action, {
                method: 'POST',
                body: new FormData(form),
                headers: {
                    'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                if(data.success) {
                    // Update cart count
                    document.querySelector('.cart-count').textContent = data.cart_total_items;
                    // Show notification
                    showNotification(data.message);
                    
                    // Optionally open the cart sidebar
                    if (cartSidebar) {
                        cartSidebar.classList.add('open');
                        // Refresh cart content
                        refreshCartContent();
                    }
                }
            });
        });
    });

    function refreshCartContent() {
        fetch(window.location.href, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const newCart = doc.getElementById('cart-sidebar');
            if (newCart && cartSidebar) {
                cartSidebar.innerHTML = newCart.innerHTML;
            }
        });
    }

    function showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 500);
        }, 3000);
    }
});