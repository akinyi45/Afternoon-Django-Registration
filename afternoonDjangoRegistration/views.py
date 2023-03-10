from __future__ import unicode_literals
from django_daraja.mpesa import utils
from django.http import HttpResponse, JsonResponse
from django.views.generic import View
from django_daraja.mpesa.core import MpesaClient
from decouple import config
from datetime import datetime

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import UserRegistrationForm
from django.contrib.auth.decorators import login_required
from .models import Product, Supplier


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data.get("username")
            form.save()
            messages.success(request, f'Account created for{username}')
            return redirect('user-registration')
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})


@login_required
def home(request):
    return render(request, "home.html")


@login_required
def add_product(request):
    if request.method == "POST":
        product_name = request.POST.get('p-name')
        product_price = request.POST.get('p-price')
        product_quantity = request.POST.get('p-quantity')
        # save data into the database
        product = Product(prod_name=product_name,
                          prod_price=product_price,
                          prod_quantity=product_quantity, )
        product.save()
        messages.success(request, "Data saved successfully")
        return redirect("my-add_product")

    return render(request, "add product.html")


@login_required
def view_products(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, "products.html", context)


def delete_product(request, id):
    product = Product.objects.get(id=id)
    product.delete()
    messages.success(request, "Data saved successfully")
    return redirect("products")


@login_required
def update_products(request, id):
    if request.method == "POST":
        # Receive the data from the form
        product_name = request.POST.get("p_name")
        product_price = request.POST.get("p_price")
        product_quantity = request.POST.get("p_quantity")

        # Select the product you want to update
        product = Product.objects.get(id=id)

        # Update the product
        product.prod_name = product_name
        product.prod_price = product_price
        product.prod_quantity = product_quantity

        # Return the update values back to the database
        product.save()
        messages.success(request, "Product updated successfully")
        return redirect("products")

    product = Product.objects.get(id=id)
    return render(request, "update.html", {'product': product})


@login_required
def add_supplier(request):
    # Check if the form submitted has a method post
    if request.method == "POST":
        # Receive the data from the form
        name = request.POST.get('s_name')
        email = request.POST.get('s_email')
        phone = request.POST.get('s_phone')
        product = request.POST.get('s_product')

        # Finally save the data into suppliers table
        supplier = Supplier(sup_name=name, sup_email=email,
                            sup_phone=phone, sup_product=product)
        supplier.save()
        # redirect back to supplier page with success message
        messages.success(request, "supplier added successfully")
        return redirect('add-supplier')
    return render(request, 'add-supplier.html')


@login_required
def view_supplier(request):
    suppliers = Supplier.objects.all()
    context = {'suppliers': suppliers}
    return render(request, "suppliers.html", context)


@login_required
def delete_supplier(request, id):
    supplier = Supplier.objects.get(id=id)
    supplier.delete()
    messages.success(request, "Supplier deleted successfully")
    return redirect('suppliers')


@login_required
def update_supplier(request, id):
    if request.method == "POST":
        # Receive the data from the form
        supplier_name = request.POST.get("s_name")
        supplier_email = request.POST.get("s_email")
        supplier_phone = request.POST.get("s_phone")

        # Select the product you want to update
        supplier = Supplier.objects.get(id=id)

        # Update the product
        supplier.sup_name = supplier_name
        supplier.sup_email = supplier_email
        supplier.sup_phone = supplier_phone

        # Return the update values back to the database
        supplier.save()
        messages.success(request, "Supplier updated successfully")
        return redirect('supplier')

    supplier = Supplier.objects.get(id=id)
    return render(request, "updates.html", {'supplier': supplier})


# Instantiate the MpesaClient
cl = MpesaClient()
# Prepare transaction callbacks
stk_callback_url = 'https://api.darajambli.comcom/express-payment'
b2c_callback_url = 'https://api.darajambli.comcom/b2c/result'


# Prepare a function to generate transaction with taken
def auth_success(request):
    token = cl.access_token()
    return JsonResponse(token, safe=False)


@login_required
def pay(request, id):
    # Select the product being paid for
    product = Product.objects.get(id=id)
    if request.method == "POST":
        phone_number = request.POST.get('nambari')
        amount = request.POST.get("pesa")
        amount = int(amount)
        account_ref = "Akinyi"
        transaction_desc = "payment for goods"
        transaction = cl.stk_push(phone_number, amount, account_ref,
                                  transaction_desc, stk_callback_url)
        return JsonResponse(transaction.response_description, safe=False)
    return render(request, 'payment.html', {'product': product})
