from urllib.parse import urlencode
from django.shortcuts import render, redirect
from django.http import JsonResponse 
import json
import datetime
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from django.core.mail import send_mail
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from .forms import *
from .decorators import *
from django.contrib.auth.models import Group
from django.views.generic import ListView, DetailView, CreateView

# Create your views here.

def home(request):
    restaurants = Restaurant.objects.all()
    return render(request, 'store/home.html', {'restaurants': restaurants})

#sign in for all users
@unauthenticated_user
def signin(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if request.user.is_customer==True:
                return redirect('home')
            if request.user.is_admin==True:
                return redirect('adminpage')
            if request.user.is_restaurant==True:
                return redirect('restOwner')
        else:
            registeredUser = RegisteredUser.objects.filter(email=form.data['username']).first()

            if registeredUser is not None and not registeredUser.is_active:
                registeredUser.is_active = True
                registeredUser.save()
                if authenticate(request, email=form.data['username'], password=form.data['password']):
                    print("valid")
                    login(request, registeredUser, backend='django.contrib.auth.backends.ModelBackend')
                    base_url = reverse('home')
                    query_string = urlencode({'control': 'True'})
                    url = '{}?{}'.format(base_url, query_string)
                    return redirect(url)
                else:
                    error_message = "* Wrong Email or Password."
                    registeredUser.is_active = False
                    registeredUser.save()
            else:
                error_message = "* Wrong Email or Password."
    else:
        error_message = ""
        form = AuthenticationForm()
    return render(request, 'store/signin.html', {'form': form, 'error_message': error_message, })

#customer sign up
@unauthenticated_user
def signup(request):
    if request.method == 'POST':
        form = CustomerCreationForm(request.POST)
        if form.is_valid():
            form.save()
            user = RegisteredUser.objects.filter(email=form.cleaned_data['email']).first()
            user.is_customer = True
            user.save()
            customer = Customer(userEmail=user)
            customer.name=form.cleaned_data.get('name')
            customer.surname=form.cleaned_data.get('surname')
            customer.city=form.cleaned_data.get('city')
            customer.address=form.cleaned_data.get('address')
            customer.phone=form.cleaned_data.get('phone')
            customer.save()
            group = Group.objects.get(name='customer')
            user.groups.add(group)
            return redirect('/')
    else:
        form = CustomerCreationForm()
    return render(request, 'store/signup.html', {'form': form})

def signout(request):
    logout(request)
    return redirect('signin')

#restaurant registration
@unauthenticated_user
def registration(request):
    context = {}
    return render(request, 'store/registration.html')

#restaurant registration - send form via email to register restaurant
@unauthenticated_user
def application(request):
    if request.method == "POST":
        restaurantName = request.POST['restaurantName']
        restaurantCity = request.POST['restaurantCity']
        restaurantPhone = request.POST['restaurantPhone']
        restaurantOwnerName = request.POST['restaurantOwnerName']
        restaurantOwnerSurname = request.POST['restaurantOwnerSurname']
        restaurantOwnerEmail = request.POST['restaurantOwnerEmail']
        restaurantOwnerPhone = request.POST['restaurantOwnerPhone']
        workingDaysFrom = request.POST['workingDaysFrom']
        workingDaysTo = request.POST['workingDaysTo']
        workingHoursFrom = request.POST['workingHoursFrom']
        workingHoursTo = request.POST['workingHoursTo']

        message = 'Restaurant Name: ' + str(restaurantName) + '\nRestaurant City: ' + str(restaurantCity) + '\nRestaurant Phone: ' + str(restaurantPhone) + '\nRestaurant Owner Name: ' + str(restaurantOwnerName) + '\nRestaurant Owner Surname: ' + str(restaurantOwnerSurname) + '\nRestaurant Owner Email: ' + str(restaurantOwnerEmail) + '\nRestaurant Owners Phone: ' + str(restaurantOwnerPhone) + '\nWorking Days: ' + '\nFrom: ' + str(workingDaysFrom) + ' To: ' + str(workingDaysTo) + '\nWorking Hours:' + '\nFrom: ' + str(workingHoursFrom) + ' To: ' + str(workingHoursTo)

        send_mail(
            'Restaurant Registration Request: ' + restaurantName, # subject
            message, # message
            restaurantOwnerEmail,  # from email
            ['ezgi.ggurkan@gmail.com'], # to email
            )

        context={'restaurantCity': restaurantCity, 'workingDaysFrom': workingDaysFrom, 
        'workingDaysTo': workingDaysTo, 'workingHoursFrom': workingHoursFrom,
        'workingHoursTo': workingHoursTo, 'restaurantOwnerName': restaurantOwnerName}

        return render(request, 'store/application.html', context)
    else:
        return render(request, 'store/registration.html', {})

#admin main page
@allowed_users(allowed_roles=['admin'])
def adminDashboard(request):
    restaurants=Restaurant.objects.all()
    context={'restaurants': restaurants}
    return render(request, 'store/admin-dashboard.html', context)

#admin creates restaurant owner's account
@allowed_users(allowed_roles=['admin'])
def createRestaurantUser(request):
    form1=RestaurantForm1()
    if request.method=='POST':
        form1=RestaurantForm1(request.POST, request.FILES)
        if form1.is_valid():    
           form1.save()
           return redirect('create_restaurant')
       
    context={'form1': form1}
    return render(request, 'store/restaurantformfirst.html', context)

#admin creates and adds restaurant to the database
@allowed_users(allowed_roles=['admin'])
def createRestaurant(request):
    form2=RestaurantForm2()
    if request.method=='POST':
        form2=RestaurantForm2(request.POST, request.FILES)
        if form2.is_valid():    
            form2.save()
            restaurant = Restaurant(userEmail=user)
            restaurant.tag=form.cleaned_data.get('tag')
            restaurant.city=form.cleaned_data.get('city')
            restaurant.restname=form.cleaned_data.get('restname')
            restaurant.hone=form.cleaned_data.get('phone')
            restaurant.phone=form.cleaned_data.get('phone')
            restaurant.address=form.cleaned_data.get('address')
            restaurant.rate=form.cleaned_data.get('rate')
            restaurant.rateCount=form.cleaned_data.get('rateCount')
            restaurant.image1=form.cleaned_data.get('image1')
            restaurant.image2=form.cleaned_data.get('image2')
            restaurant.image3=form.cleaned_data.get('image3')
            restaurant.image4=form.cleaned_data.get('image4')
            restaurant.image5=form.cleaned_data.get('image5')
            restaurant.logo=form.cleaned_data.get('logo')
            restaurant.workingHoursFrom=form.cleaned_data.get('workingHoursFrom')
            restaurant.workingHoursTo=form.cleaned_data.get('workingHoursTo')
            restaurant.workingDaysFrom=form.cleaned_data.get('workingDaysFrom')
            restaurant.workingDaysTo=form.cleaned_data.get('workingDaysTo')
            restaurant.save()
            group = Group.objects.get(name='restaurant')
            user.groups.add(group)
            return redirect('adminpage')
    context={'form2': form2}
    return render(request, 'store/restaurantformsecond.html', context)

#admin deletes a restaurant
@allowed_users(allowed_roles=['admin'])
def deleteRestaurant(request, pk):
    restaurant=Restaurant.objects.get(userEmail_id=pk)
    if request.method=='POST':
        restaurant.delete()
        return redirect('adminpage')

    context={'item': restaurant, 'restaurant': restaurant}
    return render(request, 'store/delete-restaurant.html', context)

#customer's view of a restaurant page
@canorder(allowed_roles=['customer'])
def store(request):

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items 
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping': False}
        
    products = Product.objects.all()
    starters=Product.objects.filter(category='Starter')
    salads=Product.objects.filter(category='Salad')
    specialties=Product.objects.filter(category='Specialty')
    desserts=Product.objects.filter(category='Dessert')
    drinks=Product.objects.filter(category='Drink')
    posts =Post.objects.all()
    details = Post.objects.all()

    context={'products': products, 'cartItems': cartItems, 'starters': starters, 'salads': salads, 'specialties': specialties, 'desserts': desserts, 'drinks': drinks,'posts':posts, 'details':details}
    return render(request, 'store/store.html', context)

#customer's cart
@canorder(allowed_roles=['customer'])
def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items # we'll set that to the logged in user 
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0,'shipping': False}

    context = {'items':items, 'order':order, 'cartItems': cartItems} #and we need to pass that in
    return render(request, 'store/cart.html', context)

#customer checkout
@canorder(allowed_roles=['customer'])
def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items # we'll set that to the logged in user 
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping': False}

    context = {'items':items, 'order':order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)

#update order items in cart
@canorder(allowed_roles=['customer'])
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

    return JsonResponse('Item was added',  safe=False)

#payment
@canorder(allowed_roles=['customer'])
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
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
    else:
        print('User is not logged in')

    return JsonResponse('Payment submitted..', safe=False)

#customer account settings
@login_required(login_url='signin')
@allowed_users(allowed_roles=['customer'])
def accountSettings(request):
    customer = request.user.customer
    form = CustomerCreationForm(instance=customer)

    if request.method == 'POST':
        form = CustomerCreationForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()

    context = {'form':form}
    return render(request, 'store/account_settings.html', context)

#customer deletes their profile

@allowed_users(allowed_roles=['customer'])
def deleteProfile(request, pk):
    user = User.objects.get(id=pk)
    if request.method == "POST":
        user.delete()
        return redirect('home', id=pk)

    context = {'user': user}
    return render(request, 'store/delete_profile.html', context)

#restaurant owner main page

@allowed_users(allowed_roles=['restaurant'])
def restaurantOwnerDashboard(request):
    restaurant = request.user.restaurant

    #to display restaurant's products
    products=restaurant.products.all()

    #to display restaurant's orders
    orders=Order.objects.filter(restaurant=restaurant)

    context={'restaurant': restaurant,  'products': products, 'orders': orders}
    return render(request, 'store/restaurant-owner-dashboard.html', context)

#restaurant owner adds a new product to his restaurant
@allowed_users(allowed_roles=['restaurant'])
def createProduct(request):
    restaurant_instance = request.user.restaurant
    form=ProductForm()
    if request.method=='POST':
        form=ProductForm(request.POST, request.FILES)
        if form.is_valid():     
            p = form.save()
            p.restaurant = restaurant_instance
            p.save()
            return redirect('restOwner')

    context={ 'restaurant_instance': restaurant_instance, 'form': form}
    return render(request, 'store/productform.html', context)

#restaurant owner updates a product from his restaurant
@allowed_users(allowed_roles=['restaurant'])
def updateProduct(request, pk):
    product=Product.objects.get(id=pk)
    form=ProductForm(instance=product)

    if request.method=='POST':
        form=ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():     
            form.save()
            return redirect('restOwner')

    context={'form': form}
    return render(request, 'store/productform.html', context)

#restaurant owner deletes a product from his restaurant
@allowed_users(allowed_roles=['restaurant'])
def deleteProduct(request, pk):
    product=Product.objects.get(id=pk)
    if request.method=='POST':
        product.delete()
        return redirect('restOwner')

    context={'item': product}
    return render(request, 'store/delete.html', context)

#review
class StoreView(ListView):
    model = Post 
    template_name = 'store/store.html' #sadece önüne store ekledim???

#review
class CommentDetailView(DetailView):
    model = Post
    template_name = 'store/details.html'

#review
class AddPostView(CreateView):
    model = Post
    template_name = 'store/add_post.html'
    fields = '__all__'

def notAuthorized(request):
    context = {}
    return render(request, 'store/not_authorized.html')

def cannotOrder(request):
    context = {}
    return render(request, 'store/cannotorder.html')
