from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from carts.models import CartItem
from carts.views import _cart_id
from category.models import Category
from orders.models import OrderProduct
from store.forms import ReviewForm
from store.models import Product, ProductGalary, ReviewRating
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.contrib.auth.decorators import  login_required

# Create your views here.
def store(request,category_slug=None):
    categories=None
    products=None
    if category_slug!=None:
        categories=get_object_or_404(Category,slug=category_slug)
        products=Product.objects.filter(category=categories,is_available=True)
        paginator=Paginator(products,3) 
        page=request.GET.get('page')
        paged_products=paginator.get_page(page)
        product_count=products.count()
    else:
        products=Product.objects.all().filter(is_available=True).order_by('id')
        paginator=Paginator(products,3) 
        page=request.GET.get('page')
        paged_products=paginator.get_page(page)
        product_count=products.count()
    for product in products:
      reviews=ReviewRating.objects.filter(product_id=product.id,status=True) 
    context={
        'Products':paged_products,
        'product_count':product_count,
        'categories':categories,
        'reviews':reviews,
    }
    return render(request,'store/store.html',context)
def product_details(request,category_slug,product_slug):
    try:
        single_product=Product.objects.get(category__slug=category_slug,slug=product_slug)
        in_cart=CartItem.objects.filter(cart__cart_id=_cart_id(request),product=single_product).exists()
        
    except Exception as e:
        raise e
    try:
        if request.user.is_authenticated:
           order_product=OrderProduct.objects.filter(user=request.user,product_id=single_product.id).exists()
        else:
            order_product=None   
    except OrderProduct.DoesNotExist:
        order_product=None  
    reviews=ReviewRating.objects.filter(product_id=single_product.id,status=True) 
    #get the product galary
    product_galary= ProductGalary.objects.filter(product=single_product)    
    context={
        'product':single_product,
        'in_cart':in_cart,
        'order_product':order_product,
        'reviews':reviews,
        'product_galary':product_galary,
    }
    return render(request,'store/product_details.html',context)

def search(request):
    if 'keyword' in request.GET:
        keyword=request.GET['keyword']
        if keyword :
            results = Product.objects.order_by('created_date').filter(Q(product_name__icontains=keyword )| Q(description__icontains=keyword))
        product_count=results.count()    
    context={
        'Products':results,
        'product_count':product_count,
        'keyword':keyword,
    }
    return render(request,'store/store.html',context)

@login_required(login_url='login')
def submit_review(request,pk):
    url=request.META.get('HTTP_REFERER') 
    if request.method=='POST':
        try:
            review=ReviewRating.objects.get(user__id=request.user.id,product__id=pk)
            form=ReviewForm(request.POST,instance=review)
            form.save()
            messages.success(request,'Thank you, your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist: 
            form=ReviewForm(request.POST) 
            if form.is_valid(): 
              
                try: 
                    data=ReviewRating()
                    data.subject=form.cleaned_data['subject']
                    data.rating=form.cleaned_data['rating']
                    data.review=form.cleaned_data['review']
                    data.ip=request.META.get('REMOTE_ADDR')
                    data.product_id=pk
                    data.user_id= request.user.id 
                    data.save()
                    messages.success(request,'Thank you, your review has been submitted.')
                    return redirect(url) 
                except Exception as e:
                    return redirect(url)
            else:
                return redirect(url)
    else:
        raise ValueError("Bad Request")