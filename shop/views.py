from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserRegisterForm
from django.contrib.auth import login, logout 
from .models import Product, Creator, Notification
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Review
from .forms import ReviewForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Cart, CartItem, Order, OrderItem
from django.http import HttpResponseRedirect
from django.contrib import messages
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import FileResponse
import io
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os
import requests
# from django.core.mail import send_mail
# from django.template.loader import render_to_string




# logging in 
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home') 

# logging out
def logout_view(request):
    logout(request)
    return redirect('home') 

# home redirect
def home(request):
    return render(request, 'shop/home.html')  


# registration new user
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  
            return redirect('home')  
    else:
        form = UserRegisterForm()
    return render(request, 'shop/register.html', {'form': form})

# transfer to catalog 
def product_catalog(request):
    products = Product.objects.all()
    cart = None
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'shop/product_catalog.html', {
        'products': products,
        'cart': cart
    })

#  buy item 
@login_required
def buy_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if product.stock <= 0:
        messages.error(request, f"Sorry, {product.name} is currently out of stock.")
        return redirect('product_catalog')

    cart, created = Cart.objects.get_or_create(user=request.user)

    # Check if adding would exceed available stock
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )

    if not created:
        if cart_item.quantity >= product.stock:
            messages.error(request, f"Cannot add more {product.name} - only {product.stock} available!")
            return redirect('product_catalog')
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f"{product.name} added to your cart!")
    return redirect('product_catalog')


# add rewies under product 
@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return redirect('product_detail', product_id=product.id)
    else:
        form = ReviewForm()
    
    return render(request, 'shop/add_review.html', {'form': form, 'product': product})

# transfer to specific product detail page 
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product)
    return render(request, 'shop/product_detail.html', {'product': product, 'reviews': reviews})

# like/unlike review
@csrf_exempt
@require_POST
def like_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    user = request.user

    if user in review.liked_by.all():
        # User has already liked the review, so unlike it
        review.liked_by.remove(user)
        review.likes -= 1
        action = 'unliked'
        message = 'Review unliked!'
    else:
        # User has not liked the review, so like it
        review.liked_by.add(user)
        review.likes += 1
        action = 'liked'
        message = 'Review liked!'

    review.save()
    return JsonResponse({
        'success': True,
        'likes': review.likes,
        'action': action,
        'message': message,
    })
# abt creator page 
def about_creator(request):
    creator = Creator.objects.first()  
    return render(request, 'shop/about_creator.html', {'creator': creator})

# cart 



@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'shop/cart.html', {'cart': cart})

from django.http import JsonResponse

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Check if product is available
    if product.stock <= 0:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f"Sorry, {product.name} is out of stock!",
            }, status=400)
        messages.error(request, f"Sorry, {product.name} is out of stock!")
        return redirect('product_catalog')
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Check if adding this item would exceed available stock
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        if cart_item.quantity >= product.stock:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': f"Cannot add more {product.name} - only {product.stock} available!",
                }, status=400)
            messages.error(request, f"Cannot add more {product.name} - only {product.stock} available!")
            return redirect('product_catalog')
        cart_item.quantity += 1
        cart_item.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f"{product.name} added to your cart!",
            'cart_total_items': cart.total_items()
        })
    
    messages.success(request, f"{product.name} added to your cart!")
    return redirect('product_catalog')
  

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product = cart_item.product
    amount_removed = cart_item.quantity
    
    cart_item.delete()
    
    # Return the stock
    product.increase_stock(amount_removed)
    
    messages.success(request, "Item removed from your cart.")
    return redirect('view_cart')

@login_required
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product = cart_item.product
    
    if request.method == 'POST':
        new_quantity = int(request.POST.get('quantity', 1))
        
        if new_quantity > product.stock:
            messages.error(request, f"Only {product.stock} available!")
            return redirect('view_cart')
            
        if new_quantity > 0:
            # Calculate the difference
            difference = new_quantity - cart_item.quantity
            if product.stock < difference:
                messages.error(request, "Not enough stock available!")
                return redirect('view_cart')
                
            # Return the old quantity to stock and deduct the new quantity
            product.increase_stock(cart_item.quantity)
            if not product.decrease_stock(new_quantity):
                messages.error(request, "Not enough stock available!")
                return redirect('view_cart')
                
            cart_item.quantity = new_quantity
            cart_item.save()
            messages.success(request, "Cart updated!")
        else:
            # Return the stock when item is removed
            product.increase_stock(cart_item.quantity)
            cart_item.delete()
            messages.success(request, "Item removed from cart.")
    
    return redirect('view_cart')



# checkout 
@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    
    if not cart.items.exists():
        messages.error(request, "Your cart is empty!")
        return redirect('view_cart')  
    
    # Calculate total
    total = cart.total_price()
    
    
    
    return render(request, 'shop/checkout.html', {
        'cart': cart,
        'total': total,
    })

@login_required
def confirm_order(request):
    if request.method == 'POST':
        try:
            cart = get_object_or_404(Cart, user=request.user)
            
            if not cart.items.exists():
                messages.error(request, "Your cart is empty!")
                return redirect('view_cart')
            
            # First validate stock for all items before creating the order
            for cart_item in cart.items.all():
                if cart_item.quantity > cart_item.product.stock:
                    messages.error(request, f"Sorry, only {cart_item.product.stock} of {cart_item.product.name} available!")
                    return redirect('view_cart')
            
            # Create the order
            order = Order.objects.create(
                user=request.user,
                total_price=cart.total_price(),
                shipping_address=request.POST.get('shipping_address', ''),
                email=request.POST.get('email', request.user.email),
                first_name=request.POST.get('first_name', request.user.first_name),
                last_name=request.POST.get('last_name', request.user.last_name),
                phone=request.POST.get('phone', ''),
                country=request.POST.get('country', ''),
                city=request.POST.get('city', ''),
                payment_method=request.POST.get('payment_method', 'cash_on_delivery')
            )
            
            # Create order items and decrease stock
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
                # Decrease stock - this will use the decrease_stock method we defined
                if not cart_item.product.decrease_stock(cart_item.quantity):
                    # If we get here, something went wrong with stock decrease
                    order.delete()  # Rollback the order
                    messages.error(request, f"Insufficient stock for {cart_item.product.name}!")
                    return redirect('view_cart')

            # Clear the cart only after everything succeeded
            cart.items.all().delete()

            # Prepare item summary for notification (use order items now)
            item_summary = "\n".join([
                f"{item.quantity} x {item.product.name}" for item in order.items.all()
            ])
            
            # Create admin notification
            Notification.objects.create(
                title=f"New Order #{order.id}",
                message=f"Customer: {order.first_name} {order.last_name}\n"
                f"Total: ${order.total_price}\n"
                f"Items:\n{item_summary}"
            )

            # 🎨 Create styled PDF receipt
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)
            width, height = letter

            # Title section
            p.setFillColor(colors.darkblue)
            p.setFont("Helvetica-Bold", 20)
            p.drawString(170, 750, f"Order Confirmation")

            # Header box
            p.setFillColor(colors.lightgrey)
            p.rect(40, 710, 520, 25, fill=True, stroke=False)
            p.setFillColor(colors.black)
            p.setFont("Helvetica", 12)
            p.drawString(50, 715, f"Order #{order.id} | {order.first_name} {order.last_name}")

            y = 680
            
            # Shipping Information
            p.setFont("Helvetica-Bold", 14)
            p.drawString(50, y, "Your Shipping Information:")
            y -= 20
            p.setFont("Helvetica", 12)
            p.drawString(60, y, f"Address: {order.shipping_address}")
            y -= 15
            p.drawString(60, y, f"City: {order.city}, Country: {order.country}")
            y -= 15
            p.drawString(60, y, f"Email: {order.email}")
            y -= 25

            # Items Ordered
            p.setFont("Helvetica-Bold", 14)
            p.drawString(50, y, "Items Ordered:")
            y -= 20
            p.setFont("Helvetica", 12)
            for item in order.items.all():
                p.drawString(60, y, f"{item.quantity} x {item.product.name} - ${item.price} each")
                y -= 15
                if y < 100:  # Handle page breaks
                    p.showPage()
                    y = 750
                    p.setFont("Helvetica", 12)  # Reset font after page break

            y -= 20
            p.setFont("Helvetica-Bold", 14)
            p.drawString(50, y, f"Total Amount: ${order.total_price}")
            
            y -= 40
            p.setFont("Helvetica-Oblique", 10)
            p.setFillColor(colors.gray)
            p.drawString(50, y, "Thank you for shopping with us! If you have any inquiries or wish to change/cancel your order, please contact us @afire.nails")

            p.showPage()
            p.save()
            buffer.seek(0)

            # Add success message
            messages.success(request, "Order confirmed! Your receipt is downloading.")
            return FileResponse(buffer, as_attachment=True, filename=f'order_{order.id}_confirmation.pdf')

        except Exception as e:
            messages.error(request, f"An error occurred while processing your order: {str(e)}")
            return redirect('checkout')

    return redirect('checkout')

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'shop/order_confirmation.html', {'order': order})






