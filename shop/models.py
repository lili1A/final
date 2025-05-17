from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

# item to sell
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    stock = models.PositiveIntegerField()

    def decrease_stock(self, amount=1):
        """Decrease product stock by given amount"""
        if self.stock >= amount:
            self.stock -= amount
            self.save()
            return True
        return False
    
    def increase_stock(self, amount=1):
        """Increase product stock by given amount"""
        self.stock += amount
        self.save()
        return True


# reviews on items 
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.PositiveIntegerField(default=0)
    liked_by = models.ManyToManyField(User, related_name='liked_reviews', blank=True)  #users who liked the review

    def __str__(self):
        return f'Review by {self.user.username} on {self.product.name}'
    
    # creators of the site & store
class Creator(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='creator/')



class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.username}"
    
    def total_price(self):
        return sum(item.total_price() for item in self.items.all())
    
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} in cart"
    
    def total_price(self):
        return self.product.price * self.quantity
    


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Changed from total_amount to total_price
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ], default='pending')
    shipping_address = models.TextField(default='')
    email = models.EmailField(default='')
    first_name = models.CharField(max_length=100, default='')
    last_name = models.CharField(max_length=100, default='')
    phone = models.CharField(max_length=20, default='')
    country = models.CharField(max_length=100, default='Unknown')  # Added default
    city = models.CharField(max_length=100, default='Unknown')    # Added default
    payment_method = models.CharField(max_length=50, default='cash_on_delivery')

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name} (${self.price})"
    
# admin notification 

class Notification(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
