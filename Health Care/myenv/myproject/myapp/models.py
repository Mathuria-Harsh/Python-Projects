from django.db import models
from django.contrib.auth.models import User   



# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    mno = models.BigIntegerField(unique=True)           # mobile number
    password = models.CharField(max_length=20)
    image = models.ImageField(default="")
    usertype = models.CharField(max_length=20, default="patient")   

    def __str__(self):
        return f"{self.name}" 


class Doctor(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)      # doctor belongs to a User

    category = (
            ("Dermatologist", "Dermatologist"),
            ("Neurologist", "Neurologist"),
            ("Surgeon", "Surgeon"),
            ("Immunology", "Immunology")
        )
    
    cchoice = models.CharField(max_length=20, choices=category)
    dname = models.CharField(max_length=20)
    demail = models.EmailField(unique=True)
    qfc = models.CharField(max_length=40)
    charges = models.IntegerField()
    address = models.TextField()
    start_time = models.TimeField(auto_now=False, auto_now_add=False)
    end_time = models.TimeField(auto_now=False, auto_now_add=False)
    exp = models.IntegerField()
    dimage = models.ImageField(upload_to='doctor/', null=True, blank=True) 

    def __str__(self):
        return f"{self.dname}"
    

class Patient(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)

    pname = models.CharField(max_length=30)
    email = models.EmailField()    
    mno = models.BigIntegerField()
    paddress = models.TextField()
    age = models.PositiveIntegerField()
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date = models.DateField()
    time = models.TimeField(auto_now=False, auto_now_add=False)
    category_choices = (
            ("Dermatologist", "Dermatologist"),
            ("Neurologist", "Neurologist"),
            ("Surgeon", "Surgeon"),
            ("Immunology", "Immunology")
        )
    category = models.CharField(max_length=20, choices=category_choices, default="Dermatologist")
    symptoms = models.CharField(max_length=200)

    # 🔹 New field for doctor approval
    status = models.CharField(
    max_length=20,
    choices=[("Pending", "Pending"), ("Accepted", "Accepted"), ("Cancelled", "Cancelled"), ("Confirmed", "Confirmed")],
    default="Pending"
)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    payment_status = models.BooleanField(default=False)
    

    def __str__(self):
        return f"{self.pname}"
    
class Product(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    price = models.FloatField()
    description = models.TextField()
    image = models.ImageField(upload_to="products/")
    created_at = models.DateTimeField(auto_now_add=True)

    buyer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="product_buyer")
    payment_id = models.CharField(max_length=200, null=True, blank=True)
    payment_status = models.BooleanField(default=False)
    payment_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name
