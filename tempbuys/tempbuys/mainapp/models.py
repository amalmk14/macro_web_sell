from django.db import models

# Create your models here.

class TemplatesType(models.Model):
    name = models.CharField(max_length=40)
    slug = models.SlugField(max_length=40,unique=True)

    def __str__(self):
        return self.name

class Templates(models.Model):
    name = models.CharField(max_length=50,unique=True)
    find = models.CharField(max_length=40)
    category = models.TextField(blank=True)
    temp_img = models.ImageField(upload_to="temp_meadia")
    temp_file = models.FileField(upload_to="templates")
    temp_type = models.ForeignKey(TemplatesType,on_delete=models.CASCADE)
    price = models.IntegerField()

    def __str__(self):
        return self.find

class Coupen_code(models.Model):
    code = models.CharField(max_length=10,unique=True,blank=True)
    coupen_percentage = models.IntegerField()
    is_active = models.BooleanField(default=True)
    coupen_used = models.IntegerField(default=0)
    used_user = models.CharField(max_length=100,blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

class Orders(models.Model):
    order_id = models.AutoField(primary_key=True)
    order_date = models.DateTimeField(auto_now_add=True)
    template_name = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    razorpay_order_id = models.CharField(max_length=100,blank=True)
    razorpay_payment = models.CharField(max_length=100,blank=True)
    finder = models.CharField(max_length=100,blank=True)
    template_category = models.TextField(blank=True)
    template_amount = models.TextField()
    coupen_code = models.CharField(blank=True,max_length=20,null=True)
    final_amount = models.IntegerField(default=0)
    plan = models.CharField(max_length=20,blank=True,default=True)

    amount_paid = models.BooleanField(default=False)

    def __str__(self):
        return self.email