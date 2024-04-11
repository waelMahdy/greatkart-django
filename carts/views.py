from django.http import  HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.core.exceptions import ObjectDoesNotExist

from carts.models import Cart, CartItem
from store.models import Product, Variation
from django.contrib import messages
from django.contrib.auth.decorators import  login_required
# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        # cart=request.session.create
        request.session['cart'] = cart
    return cart    

def add_cart(request,product_id):
    current_user=request.user
    product=Product.objects.get(id=product_id)
    if current_user.is_authenticated:
        product_variation=[]
        if request.method=='POST':
          for item in request.POST:
            key=item
            value=request.POST[key]
            
            try:
                variation=Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                product_variation.append(variation)
            except: 
                pass  
        

        is_cart_item_exist= CartItem.objects.filter(user=current_user,product=product).exists() 

        if is_cart_item_exist:
            cart_item=CartItem.objects.filter(user=current_user,product=product)   
            ex_var_list=[]
            id=[]
            for item in cart_item:
                existing_variations=item.variations.all()
                ex_var_list.append(list(existing_variations))
                id.append(item.id)

            if product_variation in ex_var_list:  #increase the cart item quantity +1
                index=ex_var_list.index(product_variation)
                item.id=id[index]
                item=CartItem.objects.get(product=product,id=item.id)
                item.quantity+=1
                item.save()
            else:                                 #create new cart item  
                item=CartItem.objects.create(user=current_user,product=product,quantity=1)
                if len(product_variation) >0:
                  item.variations.clear()
                  item.variations.add(*product_variation)                                
                  item.save()
        else:
            cart_item=CartItem.objects.create(user=current_user,product=product,quantity=1)
            if len(product_variation) >0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        
        return redirect('cart')
        
    else:     #if user is not authenticated      
        product_variation=[]
        if request.method=='POST':
          for item in request.POST:
            key=item
            value=request.POST[key]
            
            try:
                variation=Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                product_variation.append(variation)
            except: 
                pass  
        
        try:
            cart=Cart.objects.get(cart_id=_cart_id(request))    #get  the cart of this user present in the session
        except Cart.DoesNotExist:
            cart=Cart.objects.create(cart_id=_cart_id(request))   #if there is no cart for this user then create a
            cart.save()

        is_cart_item_exist= CartItem.objects.filter(cart=cart,product=product).exists() 

        if is_cart_item_exist:
            cart_item=CartItem.objects.filter(cart=cart,product=product)   #get the item with this product and cart
            

            #existing variations ->db
            #current variations -> product_variation

            ex_var_list=[]
            id=[]
            for item in cart_item:
                existing_variations=item.variations.all()
                ex_var_list.append(list(existing_variations))
                id.append(item.id)

            if product_variation in ex_var_list:  #increase the cart item quantity +1
                index=ex_var_list.index(product_variation)
                item.id=id[index]
                item=CartItem.objects.get(product=product,id=item.id)
                item.quantity+=1
                item.save()
            else:                                 #create new cart item  
                item=CartItem.objects.create(cart=cart,product=product,quantity=1)
                if len(product_variation) >0:
                  item.variations.clear()
                  item.variations.add(*product_variation)                                
                  item.save()
        else:
            cart_item=CartItem.objects.create(cart=cart,product=product,quantity=1)
            if len(product_variation) >0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        
        return redirect('cart')        

def remove_cart(request,product_id,cart_item_id):
    product=get_object_or_404(Product,id=product_id)
    if request.user.is_authenticated :
        cart_item=CartItem.objects.get(id=cart_item_id,user=request.user,product=product)
    else:
        cart=Cart.objects.get(cart_id=_cart_id(request))
        cart_item=CartItem.objects.get(id=cart_item_id,cart=cart,product=product)

    if cart_item.quantity > 1:
        cart_item.quantity-=1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect("cart")
def remove_cart_item(request,product_id,cart_item_id):    
    product=get_object_or_404(Product,id=product_id)
    if request.user.is_authenticated:
        cart_item=CartItem.objects.get(id=cart_item_id,user=request.user,product=product)
    else:
        cart=Cart.objects.get(cart_id=_cart_id(request))
        cart_item=CartItem.objects.get(id=cart_item_id,cart=cart,product=product)
    cart_item.delete() 
    return redirect("cart")

def cart(request,total=0,quantity=0,cart_items=None):
    tax=0
    grand_total=0
    try:
        if request.user.is_authenticated:
            cart_items=CartItem.objects.filter(user=request.user,is_active=True).all()
        else:
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_items=CartItem.objects.filter(cart=cart,is_active=True).all()
        
        for item in cart_items:
            total+=item.product.price*item.quantity
            quantity+=item.quantity
        tax=(2*total)/100
        grand_total=tax+total 

    except ObjectDoesNotExist:
        pass
  
        
    context={
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total
    }
    return render(request,'store/cart.html',context)

@login_required(login_url='login')
def checkout(request,total=0,quantity=0,cart_items=None):
    if  request.method=='POST':
        return HttpResponse('Ok')
    tax=0
    grand_total=0
    try:
        if request.user.is_authenticated:
            cart_items=CartItem.objects.filter(user=request.user,is_active=True).all()
        else:
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_items=CartItem.objects.filter(cart=cart,is_active=True).all()
        for item in cart_items:
            total+=item.product.price*item.quantity
            quantity+=item.quantity
        tax=(2*total)/100
        grand_total=tax+total 

    except ObjectDoesNotExist:
        pass
  
        
    context={
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total
    }
    return render(request,"store/checkout.html",context)