import os
import zipfile
import razorpay
from django.contrib import messages
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone

from loginregister.models import Profile
from .models import *

# Create your views here.

def home(request):
    name = request.session.get('username')
    normal_type = TemplatesType.objects.get(name='normal')
    normal = Templates.objects.filter(temp_type=normal_type)
    paginator = Paginator(normal, 6)
    try:
        page = int(request.GET.get('page', "1"))
    except:
        page = 1
    try:
        normal = paginator.page(page)
    except (EmptyPage, InvalidPage):
        normal = paginator.page(paginator.num_pages)

    premium_type = TemplatesType.objects.get(name='premium')
    premiums = Templates.objects.all().filter(temp_type=premium_type)
    paginators = Paginator(premiums, 8)
    try:
        pages = int(request.GET.get('page', "1"))
    except:
        pages = 1
    try:
        premiums = paginators.page(pages)
    except (EmptyPage, InvalidPage):
        premiums = paginators.page(paginator.num_pages)
    return render(request,'home.html',{'normal':normal,'premiums':premiums,'name':name})


def temp_view(request, template_card_id):
    try:
        # Get the TemplateCard object by ID
        template_card = Templates.objects.get(id=template_card_id)

        # Extract necessary information from the TemplateCard
        zip_file_path = template_card.temp_file.path
        zip_file_name = os.path.splitext(os.path.basename(zip_file_path))[0]

        # Create a directory to extract the contents of the zip file
        extracted_dir = os.path.join(settings.MEDIA_ROOT, "templates", zip_file_name)
        os.makedirs(extracted_dir, exist_ok=True)

        # Extract the contents of the zip file to the directory
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(extracted_dir)

        # Get the path to the index.html file within the extracted directory
        index_html_path = os.path.join(extracted_dir, "index.html")

        # Read the content of the index.html file
        with open(index_html_path, 'r') as index_file:
            content = index_file.read()

        # Render the content within an HTML template
        return render(request, "frame.html", {"content": content,'template_card':template_card})

    except Templates.DoesNotExist:
        return HttpResponse("Template not found",status=404)



def morePremium(request):
    premium_type = TemplatesType.objects.get(name='premium')
    premium = Templates.objects.all().filter(temp_type=premium_type)
#
#     # paginator = Paginator(premium, 9)
#     # try:
#     #     page = int(request.GET.get('page', "1"))
#     # except ValueError:
#     #     page = 1
#     # try:
#     #     premium = paginator.page(page)
#     # except (EmptyPage, InvalidPage):
#     #     premium = paginator.page(paginator.num_pages)
#
    search = None
    query = None
    if 'q' in request.GET:
        query = request.GET.get('q')
        search = premium.filter(Q(name__contains=query) | Q(category__contains=query))
    return render(request, "morepremium.html", {'premium': premium,'search':search,'query':query})

def moreNormal(request):
    normal_type = TemplatesType.objects.get(name='normal')
    normal = Templates.objects.filter(temp_type=normal_type)
    # paginator = Paginator(normal, 6)
    # try:
    #     page = int(request.GET.get('page', "1"))
    # except:
    #     page = 1
    # try:
    #     normal = paginator.page(page)
    # except (EmptyPage, InvalidPage):
    #     normal = paginator.page(paginator.num_pages)

    search = None
    query = None
    if 'q' in request.GET:
        query = request.GET.get('q')
        search = normal.filter(Q(name__contains=query) | Q(category__contains=query))
    return render(request, "morenormal.html", {'normal':normal,'query':query,'search':search})

def pay(request,template_id):
    temp_card =Templates.objects.get(id=template_id)
    return render(request,'pay/payment.html',{'temp_card':temp_card})

def coupen(request,id):
    template_card = Templates.objects.get(id=id)
    if request.method == 'POST':
        code = request.POST['coupen_code']
        if Coupen_code.objects.filter(code=code).exists():
            coupens = Coupen_code.objects.get(code=code)
            amount = template_card.price
            percentage = coupens.coupen_percentage

            discounts = amount*(percentage/100)
            discount=round(discounts)

            final_price = amount-discount
            request.session['code'] = code
            request.session['percentage'] = percentage
            request.session['final_price'] = final_price

            percentage = request.session.get('percentage')
            final_price = request.session.get('final_price')

            context = {
                'discount':discount,
                'percentage':percentage,
                'temp_card':template_card,
                'final_price':final_price
            }
            return render(request,'pay/payment.html',context)
        else:
            messages.info(request,'Invalid Code')
            return redirect('mainapp:pay',id)

def delcoupen(request,template_id):
    if 'code' in request.session:
        del request.session['code']
        del request.session['percentage']
        del request.session['final_price']
        request.session.save()
        return redirect('mainapp:pay',template_id)

def checkout(request,id):
    template = Templates.objects.get(id=id)
    if request.method == 'POST':
        name = request.session.get('username')
        if name:
            profile_object = Profile.objects.get(name=name)
            email = profile_object.email

            try:
                counter = 1
                while Orders.objects.filter(finder=f"{email} {counter}").exists():
                    counter += 1

                finder = f"{email} {counter}"
                request.session['finder'] =finder
                request.session.save()
            except Orders.DoesNotExist:
                print("no data")

            if request.session.get('final_price',None):
                final_amount = request.session.get('final_price',None)
            else:
                final_amount = int(template.price)


            finder = request.session.get('finder',None)
            code = request.session.get('coupen_code',None)
            orders = Orders(username=name,email=email,template_name=template.name,template_amount=template.price,template_category=template.category,finder=finder,order_date=timezone.now(),final_amount=final_amount,coupen_code=code)
            orders.save()
    client = razorpay.Client(auth=(settings.KEY,settings.SECRET))
    payment = client.order.create({'amount':template.price * 100,'currency':'INR','payment_capture':1})
    finder = request.session.get('finder',None)
    orders_obj = Orders.objects.get(finder=finder)
    orders_obj.razorpay_order_id=payment['id']
    orders_obj.save()
    context = {
        'payment': payment,
        'name': name
    }
    return render(request,"pay/checkout.html",context)

def success(request):
    order_id = request.GET.get('Order_id')
    orders = Orders.objects.get(razorpay_order_id=order_id)
    orders.amount_paid=True
    orders.save()
    return render(request,'pay/paymentsuccess.html')