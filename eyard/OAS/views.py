from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages  
from django.contrib.auth.forms import UserCreationForm  
from django.db import reset_queries
from OAS.models import Auction, Bid,Customer,Product,Order,OrderItem,ShippingAddress  # add by me
from .models import *
from stripe.api_resources import country_spec, source
from datetime import datetime, timezone
from django.urls import reverse
from django.conf import settings
import stripe
from django.template import loader

from django.http import JsonResponse
import json
from .utils import cookieCart, cartData, guestOrder

# User Register/login
def register(request):
    form=UserCreationForm
    if request.method=='POST':
        regForm=UserCreationForm(request.POST)
        if regForm.is_valid():
        # login activation permission
            user= regForm.save()
            user.is_active = False
            user.save()
            messages.add_message(request,messages.SUCCESS,
      'Congratulations! You have been registered successfully.Now You can Login after admin permission.')
        else:
         messages.add_message(request,messages.SUCCESS,'Try again! Password should be mixed eight characters')
    return render(request,'registration/register.html',{'form':form})

def home (request):

    products = Auction.objects.all()
    for a in products:
        a.resolve()
        latest_products = products.filter(
        is_active=True).order_by('date_added')
    context = {'products': products}
    return render(request, 'home.html', context)
    
def auctions(request):
    # Get all auctions, newest first
    products = Auction.objects.order_by('-date_added')
    for a in products:
        a.resolve()
        context = {'products': products}
        return render(request, 'home.html', context)
        
def bid(request, auction_id):
    auction = get_object_or_404(Auction, pk=auction_id)
    auction.resolve()
    bid = Bid.objects.filter(bidder=request.user).filter (
        auction=auction).first()

    if not auction.is_active:
        return render( request, 'detail.html', {
            'auction': auction,
            'error_message': "The auction has expired.",
        })
    try:
        bid_amount = request.POST['amount']
        # Prevent user from entering an empty or invalid bid
        if not bid_amount or int(bid_amount) < auction.min_value:
            raise(KeyError)
        if not bid:
            # Create new Bid object if it does not exist
            bid = Bid()
            bid.auction = auction
            bid.bidder = request.user
        bid.amount = bid_amount
        bid.date = datetime.now(timezone.utc)
    except (KeyError):
        # Redisplay the auction details.
        return render(request, 'detail.html', {
            'auction': auction,
            'error_message': "Invalid bid amount.",
        })
    else:
        bid.save()

        return HttpResponseRedirect(reverse('my_bids', args=()))
        
def detail(request, auction_id):
    auction = get_object_or_404(Auction, pk=auction_id)
    auction.resolve()
    already_bid = False
    if request.user.is_authenticated:
        if auction.author == request.user:
            own_auction = True
            return render(request, 'detail.html', {'auction': auction, 'own_auction': own_auction})

        user_bid = Bid.objects.filter(
            bidder=request.user).filter(auction=auction).first()
        if user_bid:
            already_bid = True
            bid_amount = user_bid.amount
            return render(request, 'detail.html', {'auction': auction, 'already_bid': already_bid, 'bid_amount': bid_amount})

    return render(request, 'detail.html', {'auction': auction, 'already_bid': already_bid})
def my_bids(request):
    # Get all bids by user, sorted by date
    my_bids_list = Bid.objects.all().filter(bidder=request.user).order_by('-date')
    for b in my_bids_list:
        b.auction.resolve()

    template = loader.get_template('my_bids.html')
    context = {
        'my_bids_list': my_bids_list,
        'key': settings.STRIPE_SECRET_KEY
    }
    return HttpResponse(template.render(context, request))

def payment(request):
    if request.method == "POST":
        bidid = request.POST.get('bidid')
        bid = Bid.objects.get(id=bidid)
        ch = stripe.Charge.create(
            amount=bid.amount*100,
            currency="usd",
            api_key=settings.STRIPE_PUBLISHABLE_KEY,
            description=bid.auction.desc,
            source=request.POST['stripeToken']
        )
        bid.is_pay = True
        bid.save()
        return HttpResponse("Pay Successfull..!")
        
        
        
        
#======================= For cart ====================        

def store(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	products = Product.objects.all()
	context = {'products':products, 'cartItems':cartItems}
	return render(request, 'store/store.html', context)


def cart(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/cart.html', context)

def checkout(request):
	data = cartData(request)
	
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/checkout.html', context)

def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)

def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
	else:
		customer, order = guestOrder(request, data)

	total = float(data['form']['total'])
	order.transaction_id = transaction_id

	if total == order.get_cart_total:
		order.complete = True
	order.save()

	if order.shipping == True:
		ShippingAddress.objects.create(
		customer=customer,
		order=order,
		address=data['shipping']['address'],
		city=data['shipping']['city'],
		state=data['shipping']['state'],
		zipcode=data['shipping']['zipcode'],
		)

	return JsonResponse('Payment submitted..', safe=False)


