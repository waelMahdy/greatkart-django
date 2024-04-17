from django.db import models

from accounts.models import Account
from store.models import Product, Variation

# Create your models here.
class Payment(models.Model):
    user=models.ForeignKey(Account,on_delete=models.CASCADE)
    Payment_id=models.CharField(max_length=200)
    payment_method=models.CharField(max_length=100)
    amount_paid=models.DecimalField(max_digits=8,decimal_places=2)
    currency_code=models.CharField(max_length=5,default='USD')  # US Dollar is the default Currency Code
    status=models.CharField(max_length=100)
    created_at=models.DateField(auto_now_add=True)
    payer_name=models.CharField(max_length=100,default=None,null=True)
    payer_email=models.EmailField(default=None,null=True)

    def __str__(self):
        return  self.Payment_id
    
class Order(models.Model):
    STATUS={'New':'New','Accepted':'Accepted','Completed': 'Completed','Cancelled':'Cancelled'}
    user=models.ForeignKey(Account,on_delete=models.CASCADE)
    payment=models.ForeignKey(Payment,on_delete=models.SET_NULL,blank=True,null=True)
    order_number=models.CharField(max_length=50)
    first_name=models.CharField(max_length=30)
    last_name=models.CharField(max_length=30)
    phone=models.CharField(max_length=15)
    postal_code=models.CharField(max_length=15,blank=True,null=True)
    email=models.EmailField()
    address_line_1=models.CharField(max_length=100)
    address_line_2=models.CharField(max_length=100,blank=True)
    country=models.CharField(max_length=50)
    state=models.CharField(max_length=50)
    city=models.CharField(max_length=50)
    order_note=models.CharField(max_length=200,blank=True,null=True)
    order_total=models.FloatField()
    tax=models.FloatField(default=0.0)
    status=models.CharField(max_length=10,choices=STATUS.items(),default='New')
    ip=models.CharField(blank=True,max_length=40)
    is_ordered = models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.first_name
    def full_name(self):
        return f"{self.first_name} {self.last_name}" 
    def full_address(self):
        return f"{self.address_line_1}, {self.address_line_2}" 

class OrderProduct(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE)
    user=models.ForeignKey(Account, on_delete=models.CASCADE)
    payment=models.ForeignKey(Payment,on_delete=models.SET_NULL,null=True, blank=True)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    variation=models.ManyToManyField(Variation,blank=True)
    quantity=models.IntegerField()
    product_price=models.FloatField()
    ordered=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    def order_product_items_price(self):
        return self.product.price * self.quantity
    def __str__(self):
        return self.product.product_name
    

    



