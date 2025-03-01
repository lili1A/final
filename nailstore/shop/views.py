from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserRegisterForm
from django.contrib.auth import login, logout 
from .models import Product, Creator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Review
from .forms import ReviewForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

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
@login_required
def product_catalog(request):
    products = Product.objects.all()  
    return render(request, 'shop/product_catalog.html', {'products': products})

#  buy item 
def buy_product(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)     
        if product.stock > 0:
            product.stock -= 1  
            product.save()
            messages.success(request, f'You have successfully purchased {product.name}!')
        else:
            messages.error(request, f'Sorry, {product.name} is out of stock.')
        
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