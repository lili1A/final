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
    liked_by = models.ManyToManyField(User, related_name='liked_reviews', blank=True)  # Tracks users who liked the review

    def __str__(self):
        return f'Review by {self.user.username} on {self.product.name}'
    
    # creators of the site & store
class Creator(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='creator/')