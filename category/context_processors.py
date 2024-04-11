

from carts.models import CartItem,Cart
from carts.views import _cart_id
from category.models import Category


def menu_links(request):
    links=Category.objects.all()
    return  {'links':links}

def get_cart_items(request):
    items_count=0
    if 'admin' in request.path:
        return {}
    else:     
        try:
            cart=Cart.objects.filter(cart_id=_cart_id(request))
            if request.user.is_authenticated:
                cart_items=CartItem.objects.all().filter(user=request.user)
            else:    
               cart_items=CartItem.objects.all().filter(cart = cart[:1])
            for  item in cart_items:
                items_count+=item.quantity
        except Cart.DoesNotExist:
            items_count=0
    return {'cart_count':items_count}