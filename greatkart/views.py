from django.http import HttpResponse
from django.shortcuts import render
from store.models import  Product, Category, ReviewRating



def home(request):
    products=Product.objects.all().filter(is_available=True).order_by('created_date')
    reviews=None
    try:
        for product in products:

          reviews=ReviewRating.objects.filter(product_id=product.id,status=True)
    except:
        reviews=None   
         
             
    context={
        'Products':products,
        "reviews":reviews,
    }
    return render(request, 'home.html',context)