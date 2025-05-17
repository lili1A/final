from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from .views import home, register, product_catalog, product_detail, add_review, like_review, about_creator, buy_product, view_cart, add_to_cart, remove_from_cart, update_cart_item, checkout, confirm_order, confirm_order, order_confirmation 

urlpatterns = [
    path('', home, name='home'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'), 
    path('register/', register, name='register'),
    path('catalog/', product_catalog, name='product_catalog'), 
    path('buy/<int:product_id>/', buy_product, name='buy_product'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),
    path('product/<int:product_id>/add_review/', add_review, name='add_review'),
    path('like_review/<int:review_id>/', like_review, name='like_review'),
    path('about-creator/', about_creator, name='about_creator'),
    path('cart/', view_cart, name='view_cart'),
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('update-cart-item/<int:item_id>/', update_cart_item, name='update_cart_item'),
    path('checkout/', checkout, name='checkout'),
    path('checkout/confirm/', confirm_order, name='confirm_order'),
    path('order-confirmation/<int:order_id>/', order_confirmation, name='order_confirmation'),

]
