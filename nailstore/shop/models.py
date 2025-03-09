from django.db import models
from django.contrib.auth.models import User

# item to sell
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    stock = models.PositiveIntegerField()

    def __str__(self):
        return self.name

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
    
    
""" 
class Client(models.Model):
    client_nickname = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.client_nickname

class ClientOrder(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"Order {self.id} - {self.client.client_nickname}" """