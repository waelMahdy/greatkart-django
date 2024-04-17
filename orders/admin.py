from django.contrib import admin

from orders.models import Order, OrderProduct, Payment

# Register your models here.
class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields=('payment', 'user','product','product_price','quantity')
    extra = 0
class OrderAdmin(admin.ModelAdmin):
    list_display=('full_name','order_number','phone','city','order_total','tax','status','is_ordered','created_at')
    list_filter=('is_ordered', 'status')
    search_fields=['order_number','first_name','last_name','phone','email']
    list_per_page=20
    filter_horizontal=()
    inlines= [OrderProductInline]
class PaymentrAdmin(admin.ModelAdmin): 
        search_fields=['Payment_id','currency_code']
   

admin.site.register(Order,OrderAdmin)
admin.site.register(OrderProduct)
admin.site.register(Payment,PaymentrAdmin)
