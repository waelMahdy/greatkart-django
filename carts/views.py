from django.http import  HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.core.exceptions import ObjectDoesNotExist

from carts.models import Cart, CartItem
from store.models import Product, Variation
from django.contrib import messages
# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        # cart=request.session.create
        request.session['cart'] = cart
    return cart    

def add_cart(request,product_id):
    product=Product.objects.get(id=product_id)   
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
    cart=Cart.objects.get(cart_id=_cart_id(request))
    product=get_object_or_404(Product,id=product_id)
    try:
        cart_item=CartItem.objects.get(cart=cart,id=cart_item_id,product=product)
        if cart_item.quantity > 1:
           cart_item.quantity-=1
           cart_item.save()
        else:
          cart_item.delete()
    except:
        pass      
    
    return redirect("cart")
def remove_cart_item(request,product_id,cart_item_id):
    cart=Cart.objects.get(cart_id=_cart_id(request))
    product=get_object_or_404(Product,id=product_id)
    try:
       cart_item=CartItem.objects.get(cart=cart,id=cart_item_id,product=product)
       cart_item.delete()
    except:
        pass  
    return redirect("cart")



def cart(request,total=0,quantity=0,cart_items=None):
    tax=0
    grand_total=0
    try:
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
