import datetime
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from carts.models import CartItem
from greatkart import settings
from orders.form import OrderForm
from orders.models import Order, OrderProduct, Payment
from decimal import Decimal
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from store.models import Product
#email
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
import threading


class EmailThread(threading.Thread):
    def __init__(self,email_message):
        self.email_message=email_message
        threading.Thread.__init__(self)
    def run(self):
        self.email_message.send() 
# Create your views here.

def payments(request):
    body=json.loads(request.body)
    order=Order.objects.get(order_number=body['orderId'],user=request.user,is_ordered=False)
    #STORE TRANSACTION DETAILS INSIDE PAYMENT MODEL
    payment=Payment()
    payment.user = request.user
    payment.payer_name=body['payer']
    payment.payer_email=body['email']
    payment.Payment_id=body['transID']
    payment.payment_method=body['payment_method']
    payment.amount_paid=body['amount']
    payment.currency_code=body['currency_code']
    payment.status=body['status']
    payment.save()
    order.payment=payment
    order.status=body['status']
    order.is_ordered=True
    order.save()
    #move  cart items to order products items 
    cart_items=CartItem.objects.filter(user=request.user)
    for item in  cart_items:
        orderproduct=OrderProduct(
            order_id=order.id,
            payment=payment,
            user_id=request.user.id,
            product_id=item.product.id,
            quantity=item.quantity,
            product_price=item.product.price,
            ordered=True
            )
        orderproduct.save()
        cart_item=CartItem.objects.get(id=item.id)
        product_variations=cart_item.variations.all()
        orderproduct=OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variation.set(product_variations)
        orderproduct.save()

    #reduce quantity of the sold products
        product=Product.objects.get(id=item.product_id)
        product.stock-=item.quantity
        product.save()
   
    #send order received to the customer
    mail_subject='thank you for your order'
    message=render_to_string('orders/order_received_email.html',{
                "user":request.user,
                'order':order ,
                'cart_items':cart_items                             
                })
    email_message=EmailMessage(mail_subject,message,settings.EMAIL_HOST_USER, [request.user.email],)
    EmailThread(email_message).start()
    #and empty the cart.
    CartItem.objects.filter(user=request.user).delete()
    #send order number and transction id back to sendData() method via JasonResponse
    data={
        'order_number':order.order_number,
        'transactionId':payment.Payment_id,
    }
    return  JsonResponse(data)
    
    return  render(request, 'orders/payments.html')
def place_order(request,total=0,quantity=0):
    current_user=request.user
#if cart items is less or equal to 0 redirect to shop
    cart_items=CartItem.objects.filter(user= request.user)
    if len(cart_items) <= 0:
        return redirect('store')
    grand_total = 0   
    tax=0    
    for item in cart_items:
        total+=(item.product.price * item.quantity)
        quantity+=item.quantity
    tax=(2*total)/100
    grand_total=tax + total
    if  request.method == 'POST':
        form=OrderForm(request.POST)
        if form.is_valid():
            #store all the biling information in the form
            data=Order()
            data.user=current_user
            data.first_name=form.cleaned_data['first_name']
            data.last_name =form.cleaned_data['last_name']
            data.email=form.cleaned_data['email']
            data.phone=form.cleaned_data['phone']
            data.postal_code=form.cleaned_data['postal_code']
            data.address_line_1=form.cleaned_data['address_line_1']
            data.address_line_2=form.cleaned_data['address_line_2']
            data.country=form.cleaned_data['country']
            data.state=form.cleaned_data['state']
            data.city=form.cleaned_data['city']
            data.order_note=form.cleaned_data['order_note']

            data.order_total=grand_total
            data.tax=tax
            data.ip=request.META.get("REMOTE_ADDR")
            data.save()
            
            #add order id to each of the cart items and save them 
            yr=int(datetime.date.today().strftime('%Y')) 
            dt=int(datetime.date.today().strftime('%d')) 
            mt=int(datetime.date.today().strftime('%m')) 
            d=datetime.date(yr,mt,dt)
            current_date=d.strftime("%Y%m%d")
            order_number=current_date+str(data.id)
            data.order_number=order_number
            data.save()
            order=Order.objects.get(user=current_user,order_number=order_number,is_ordered =False)
            context={
                'order':order,
                'cart_items':cart_items,
                'total':total,
                'quantity':quantity,
                'tax':tax,
                'grand_total':grand_total,
                }
            return render(request,'orders/payments.html',context)
        

                    
        else:
            return redirect('store')        

            

    return HttpResponse('Ok')

def order_complete(request):
    order_number=request.GET['order_number']
    transaction_id=request.GET['payment_id']
    try:
        order=Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products=OrderProduct.objects.filter(order=order)
        sub_total=0
        for  single_product in ordered_products:
            sub_total+=single_product.product_price*single_product.quantity
        payment=Payment.objects.get(Payment_id=transaction_id)
        context={
            'order':order,
            'ordered_products':ordered_products,
            'payment':payment,
            'sub_total':sub_total,
        }
        save_pdf(transaction_id,order,payment)
        return render(request,'orders/order_complete.html',context)
    except( Order.DoesNotExist,Payment.DoesNotExist):
        return redirect('home')
    
def save_pdf(transaction_id,order,payment):
    try:
            

            # Assuming you've extracted the relevant data
            invoice_number = transaction_id
            invoice_date = order.created_at.strftime("%B %d,%Y")
            invoice_amount = payment.amount_paid
            order_number=order.order_number

            # Create a PDF file
            output_filename = 'templates/pdfs/'+order.order_number+'.pdf'
            c = canvas.Canvas(output_filename, pagesize=letter)
            # Set font and font size
            c.setFont("Helvetica-Bold", 14)  # Bold font for the header

            # Write the header
            c.drawString(300, 750, "Invoice Details")
            # Set font and font size
            c.setFont("Helvetica", 12)
            # Create a table for the invoice details
            table_data = [
                            ["Invoice Number :", invoice_number],
                            ["Invoice Date :", invoice_date],
                            ["Invoice Amount :", "${:.2f}".format(invoice_amount)],
                            ["Order number :", order_number],
                        ]
            # Set table properties
            table_x = 100
            table_y = 660
            row_height = 20
            col_width1 = 120
            col_width2 = 200
            # Draw the table with thicker lines
            c.line(table_x, table_y, table_x + col_width1 + col_width2, table_y)  # Top horizontal line
            # Draw the table
            for row in table_data:
                c.drawString(table_x, table_y - row_height, row[0])
                c.drawString(table_x + col_width1, table_y - row_height, row[1])
                c.line(table_x, table_y - row_height, table_x + col_width1 + col_width2, table_y - row_height)
                #Horizontal lines
                table_y -= row_height

            # Save the PDF
            c.save()

            print(f"Invoice details saved to {output_filename}")
    except  Exception as e:
            print('E',e)
            pass    
