from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from .views import home, register, product_catalog, buy_product, product_detail, add_review, like_review, about_creator

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
]
