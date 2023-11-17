from django.contrib import messages, auth
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from mainapp.models import *
from loginregister.models import *


# Create your views here.

def adminLogin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username,password=password)
        if user is not None:
            if user.is_superuser:
                login(request, user)
                return redirect('customadmin:adminhome')
            else:
                messages.info(request,"only admins can login")
        else:
            messages.info(request, 'Invalid Details')
            return redirect('customadmin:adminlogin')
    return render(request, "cuadmin/signin.html")

def adminLogout(request):
    auth.logout(request)
    return redirect('mainapp:home')

def adminHome(request):
    user = User.objects.all()
    if request.method == "POST":
        username = request.POST['username']
        firstname = request.POST['firstname']
        email = request.POST['email']
        password = request.POST['password']
        password1 = request.POST['password1']

        if password == password:
            if User.objects.filter(username=username).exists():
                messages.info(request, 'Username Already Taken')
                return redirect('customadmin:adminhome')
            elif User.objects.filter(email=email).exists():
                messages.info(request, 'Email Already Taken')
                return redirect('customadmin:adminhome')
            else:
                user = User.objects.create_user(username=username, password=password1, email=email,first_name=firstname)
                user.save();
        else:
            messages.info(request, 'Password not matched')
            return redirect('customadmin:adminhome')
        return redirect('customadmin:adminhome')
    return render(request,'cuadmin/index.html',{'user':user})

def adminWidget(request):
    return render(request,"cuadmin/widget.html")

def adminProfile(request):
    users = Profile.objects.all()
    search = None
    query = None
    if 'q' in request.GET:
        query = request.GET.get('q')
        search = Profile.objects.filter(Q(name__contains=query) | Q(phone__contains=query))
    return render(request,"cuadmin/adminprofile.html",{'users':users,'search':search,'query':query})

def adminTable(request):
    normal_type = TemplatesType.objects.get(name='normal')
    normal = Templates.objects.filter(temp_type=normal_type)
    search = None
    query = None
    if 'q' in request.GET:
        query = request.GET.get('q')
        search = normal.filter(Q(name__contains=query) | Q(category__contains=query))
    return render(request,"cuadmin/normaltable.html",{'normal': normal, 'query': query, 'search': search})

def delete_normal_temp(request, normal_id):
    normal = Templates.objects.get(id=normal_id)
    if request.method == 'POST':
        normal.delete()
        return redirect('customadmin:admintable')
    return render(request, 'cuadmin/normaltable.html')

def update_normal(request, card_id):
    # Templates = get_object_or_404(Templates, id=card_id)
    if request.method == 'POST':
        category = request.POST['category']
        type = request.POST['type']
        # price = request.POST['price']
        temp_type = TemplatesType.objects.get(name=type)
        if temp_type == 'normal':
            n = 199
        else:
            n = 399
        Templates.objects.filter(id=card_id).update(category=category,temp_type=temp_type,price=n)
        return redirect('customadmin:admintable')

def adminTableP(request):
    premium_type = TemplatesType.objects.get(name='premium')
    premium = Templates.objects.all().filter(temp_type=premium_type)
    search = None
    query = None
    if 'q' in request.GET:
        query = request.GET.get('q')
        search = premium.filter(Q(name__contains=query) | Q(category__contains=query))
    return render(request,'cuadmin/premiumtable.html',{'premium':premium, 'query': query, 'search': search})

def delete_premium_temp(request, premium_id):
    premium = Templates.objects.get(id=premium_id)
    if request.method == 'POST':
        premium.delete()
        return redirect('customadmin:admintablep')
    return render(request, 'cuadmin/premiumtable.html')

def update_premium(request, card_id):
    # Templates = get_object_or_404(Templates, id=card_id)
    if request.method == 'POST':
        category = request.POST['category']
        type = request.POST['type']
        # price = request.POST['price']
        temp_type = TemplatesType.objects.get(name=type)
        if temp_type == 'premium':
            n = 399
        else:
            n = 199
        Templates.objects.filter(id=card_id).update(category=category,temp_type=temp_type,price=n)
        return redirect('customadmin:admintablep')

def adminForm(request):
    normal = TemplatesType.objects.all()
    if request.method == 'POST':
        temp_img = request.FILES.get('temp_img')
        temp_file = request.FILES.get('temp_file')
        name = request.POST['name']
        find = request.POST['find']
        category = request.POST['category']
        temp_type_normal = request.POST['temp_type']
        price = request.POST['price']
        temp_type = TemplatesType.objects.get(name=temp_type_normal)
        card = Templates(temp_img=temp_img,temp_file=temp_file,name=name,find=find,temp_type=temp_type,price=price,category=category)
        card.save()
        return redirect('customadmin:admintable')
    return render(request,"cuadmin/normalform.html",{'normal':normal})

def adminFormP(request):
    if request.method == 'POST':
        temp_img = request.FILES.get('temp_img')
        temp_file = request.FILES.get('temp_file')
        name = request.POST['name']
        find = request.POST['find']
        category = request.POST['category']
        temp_type_premium = request.POST['temp_type']
        price = request.POST['price']
        temp_type = TemplatesType.objects.get(name=temp_type_premium)
        card = Templates(temp_img=temp_img, temp_file=temp_file, name=name, find=find,temp_type=temp_type, price=price,category=category)
        card.save()
        return redirect('customadmin:admintablep')
    return render(request,"cuadmin/premiumform.html")

