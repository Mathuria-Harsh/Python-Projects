
# Create your views here.
from django.shortcuts import render,redirect
from .models import *
from django.core.mail import send_mail
import random
from django.conf import settings
import json
import razorpay
from django.db.models import Sum
from django.http import HttpResponse    
import csv
from reportlab.pdfgen import canvas
from datetime import date , timedelta 
from datetime import datetime
from django.utils import timezone
from .models import Patient, Product, Doctor, User
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

def index(request):
    
    # if 'email' in request.session:
    #     user = User.objects.get(email=request.session['email'])
    #     doctor = Doctor.objects.get(doctor=user)
    #     return render(request, 'index.html', {'user': user,'doctor':doctor})
    # else:
        return render(request, 'index.html')

def doctor_index(request):
    if 'email' in request.session:
        user = User.objects.get(email=request.session['email'])
        
        return render(request, 'doctor_index.html', {'user': user,})
    else:
        return render(request, 'doctor_index.html')

def signup(request):
    if request.method=="POST":
        email = request.POST['email']
        password = request.POST['password']
        cpassword = request.POST['cpassword']
        usertype = request.POST['usertype']
        try:
            if User.objects.filter(email=email).exists():
                msg = "User with this email already exists!"
            return render(request, 'signup.html', {'msg': msg})
        except:
            if password != cpassword:
                return render(request, 'signup.html', {'msg':"Passwords do not match"})

            new_user = User.objects.create(
                name=request.POST['name'],
                email=email,
                mno=request.POST['mno'],
                password=password,
                image=request.FILES['image'],
                usertype=request.POST['usertype']
            )

            request.session['email'] = new_user.email
            request.session['name'] = new_user.name
            request.session['image'] = str(new_user.image.url) if new_user.image else ""

            if new_user.usertype == "patient":
                return redirect('index')
            else:
                return redirect('doctor_details')
    else:
        return render(request, 'signup.html')
    
@csrf_exempt
def login(request):
    if request.method == "POST":
        try:
            user = User.objects.get(email=request.POST['email'])

            if user.password == request.POST['password']:
                request.session['email'] = user.email
                request.session['name'] = user.name 
                request.session['image'] = user.image.url

                if user.usertype == "patient": 
                    return redirect('index')
                else:
                    return redirect('doctor_index')
            else:
                msg = "Password does not match"
                return render(request, 'login.html', {'msg': msg})
        
        except User.DoesNotExist:
            msg = "User doesn't exist, please signup"
            return render(request, 'login.html', {'msg': msg})
    else:
        return render(request, 'login.html')

def logout(request):
    request.session.flush()  
    return render(request, 'index.html')
        
def fpass(request):
    if request.method=="POST":
        try:
            user = User.objects.get(email=request.POST['email'])
            otp = random.randint(1001,9999)

            subject = "OTP for Password Reset"
            message = f"""
                        Dear {user.name},

                        We received a request to reset your password. Please use the One-Time Password (OTP) below to proceed with resetting your account password:

                        Your OTP: {otp}

                        This OTP is valid for the next 10 minutes. Please do not share this code with anyone for security reasons. If you did not request a password reset, please ignore this email or contact our support team immediately.

                        Thank you,  
                        HealthCare Support Team
                        """
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email]
            
            send_mail(subject, message, email_from, recipient_list)

            request.session['email'] = user.email
            request.session['otp'] = otp
            request.session['usertype'] = user.usertype   # 🔹 store user type
            return render(request, 'otp.html')
        
        except Exception as e:
            print("error",e)
            msg = "Email doesn't exist"
            return render (request, 'fpass.html', {'msg':msg})
    
    else:
        return render (request, 'fpass.html')

def otp(request):
    if request.method=="POST":
        try:
            otp = int(request.session['otp'])
            uotp = int(request.POST['uotp'])

            if otp==uotp:
                del request.session['otp']
                return render(request,'newpass.html')
            else:
                msg = "Invalid Otp!!"
                return render(request,'otp.html',{'msg':msg})       
        except:
            msg = "Something went wrong!"
            return render(request, 'otp.html', {'msg': msg})
    else:
        return render(request,'otp.html')
    
def newpass(request):
    if request.method=="POST":
        try:
            user = User.objects.get(email=request.session['email'])

            if request.POST['npassword']==request.POST['cnpassword']:
                user.password = request.POST['npassword']
                user.save()
                if 'email' in request.session:
                    del request.session['email']
                if 'usertype' in request.session:
                    del request.session['usertype']
                return redirect('login')
            else:
                msg = "Password & confirm password does not match!!"
                return render(request,'newpass.html',{'msg':msg})    
        except Exception as e:
            msg = f"Something went wrong: {e}"
            return render(request, 'newpass.html', {'msg': msg})
    else:
        return render(request,'newpass.html')

def changepass(request):
    if 'email' not in request.session:
        return redirect('login')
    
    if request.method=="POST":
        try:
            user = User.objects.get(email=request.session['email'])
            if user.password == request.POST['opassword']:
                if request.POST['npassword']==request.POST['ncpassword']:
                    user.password = request.POST['npassword']
                    user.save()
                    return redirect('logout')
                
                else:
                    msg = "New password & confirm new password does not match!!"
                    return render(request,'changepass.html',{'msg':msg})
                    
            else:
                msg = "Old password does not match!!"
                return render(request,'changepass.html',{'msg':msg})
            
        except:
            pass

    else:
        return render(request,'changepass.html')
    
def doctor_details(request):
    if 'email' not in request.session:
        return redirect('login')  
    
    user = User.objects.get(email=request.session['email'])
    print("SESSION DATA:", request.session.items())

    if request.method=="POST":
        
        if Doctor.objects.filter(doctor=user).exists():
            msg = "You have already added your details!"
            return render(request, 'doctor_index.html', {'msg': msg}) 
        try:
            
            print("POST DATA:", request.POST)
            Doctor.objects.create(
                doctor = user,              # link this doctor to the logged-in user (from foreign key)
                cchoice = request.POST['cchoice'],
                dname = request.POST.get('dname', ''),
                demail = request.POST.get('demail', ''),
                qfc = request.POST['qfc'],
                charges = request.POST['charges'],
                address = request.POST['address'],
                start_time = request.POST['start_time'],
                end_time = request.POST['end_time'],
                exp = request.POST['exp'],
                dimage=user.image   # signup is image is used
            )

            msg = "Doctor Profile Successfully"
            return render(request, 'doctor_index.html', {'msg':msg})
        
        except Exception as e:
            print("******Error******", e)
            msg = "Something went wrong while adding doctor details."
            return render(request, 'doctor_details.html', {'msg': msg})
    
    else:
        return render(request,'doctor_details.html')

def patient_profile(request):
    user=User.objects.get(email=request.session['email'])

    if request.method=="POST":
        
            user.name = request.POST['name']
            user.mno = request.POST['mno']
            try:
                user.image=request.FILES['image']
                request.session['image']=user.image.url # (session) update profile
                
            except:
                pass
            user.save()
            if user.usertype=="patient":
                return redirect('patient_profile')
            else:
                return redirect('doctor_profile')    
    else:
        if user.usertype=="patient":
            return render(request,'patient_profile.html',{'user':user})
        else:
             return render(request,'doctor_profile.html',{'user':user})

def doctor_profile(request):
    doctor = Doctor.objects.get(demail=request.session['email'])
    
    if request.method=="POST":
        
            doctor.dname = request.POST['name']
            doctor.cchoice = request.POST['cchoice']
            doctor.qfc = request.POST['qfc']
            doctor.exp = request.POST['exp']
            doctor.charges = request.POST['charges']
            doctor.address = request.POST['address']
            doctor.start_time = request.POST['start_time']
            doctor.end_time = request.POST['end_time']
            
            try:
                doctor.dimage=request.FILES['image']
                request.session['image']=doctor.dimage.url # (session) update profile
                
            except:
                pass
            doctor.save()
            return redirect('doctor_profile')          
    else:
        return render(request, 'doctor_profile.html', {'doctor': doctor,})
   

def delete(request, pk):
    user = User.objects.get(email=request.session['email'])
    doctor = Doctor.objects.get(pk=pk)
    doctor.delete()
    return redirect('index')

def patient_doctors(request):
    doctor = Doctor.objects.all()
    return render(request, 'patient_doctors.html', {'doctor':doctor})

def doctor_doctor(request):
    if 'email' not in request.session:
        return redirect('login')
    user = User.objects.get(email=request.session['email'])  


    #  taking out the current doctor records
    try:
        current_doctor = Doctor.objects.get(doctor=user)
    except Doctor.DoesNotExist:
        current_doctor = None

    #  all doctors except current doctor
    if current_doctor:
        doctors = Doctor.objects.exclude(pk=current_doctor.pk)
    else:
        doctors = Doctor.objects.all()
    return render(request, 'doctor_doctor.html', {'doctor': doctors})

def doctor_other_details(request, pk):
    user = User.objects.get(email=request.session['email'])
    doctor = Doctor.objects.get(pk=pk)
    return render(request, 'doctor_other_details.html', {'doctor':doctor,'user': user})

def patient_doctor_details(request, pk):
    user = User.objects.get(email=request.session['email'])
    doctor = Doctor.objects.get(pk=pk)
    return render(request, 'patient_doctor_details.html', {'doctor': doctor, 'user': user})

# book appointment section
def patient_book_appointment(request, pk):
    
    if 'email' not in request.session:
        return redirect('login')  
    
    # Get doctor and logged-in user
    doctor = Doctor.objects.get(pk=pk)
    user = User.objects.get(email=request.session['email'])

    if request.method == "POST":
        # Create a new Patient (appointment) entry
        Patient.objects.create(
            user=user,
            doctor=doctor,
            pname=request.POST['pname'],
            email=request.POST['email'],
            mno=request.POST['mno'],
            paddress=request.POST['paddress'],
            age=request.POST['age'],
            gender=request.POST['gender'],
            date=request.POST['date'],
            time=request.POST['time'],
            symptoms=request.POST['symptoms']
        )

        msg = "Appointment booked successfully!"
        return render(request, 'patient_book_appointment.html', {'doctor': doctor, 'msg': msg, 'pk': pk, 'user': user,})

    # If GET request, show booking page
    return render(request, 'patient_book_appointment.html', {'doctor': doctor, 'pk': pk,'user': user,})

def doctor_dashboard(request):
    if 'email' not in request.session:
        return redirect('login')

    doctor_user = User.objects.get(email=request.session['email'])
    try:
        doctor = Doctor.objects.get(doctor=doctor_user)

    except Doctor.DoesNotExist:
        return redirect('doctor_details')
    
    # Get all appointments for this doctor
    appointments = Patient.objects.filter(doctor=doctor).order_by('date', 'time')

    return render(request, 'doctor_dashboard.html', {'appointments': appointments})

def doctor_accept_appointment(request, pid):
    appointment = Patient.objects.get(id=pid)
    appointment.status = "Accepted"
    appointment.save()
    return redirect('doctor_dashboard')

def doctor_cancel_appointment(request, pid):
    appointment = Patient.objects.get(id=pid)
    appointment.status = "Cancelled"
    appointment.save()
    return redirect('doctor_dashboard')

def patient_my_appointments(request):
    if 'email' not in request.session:
        return redirect('login')
    user = User.objects.get(email=request.session['email'])

    # all appointments of Patient 
    appointments = Patient.objects.filter(user=user).order_by('-date')

    # Get the doctor appointments (not from user)
    if appointments.exists():
        doctor = appointments.first().doctor
        net = doctor.charges
    else:
        doctor = None
        net = 0

    payment = None

    # Only generate payment if doctor & charge exist
    if doctor:
        try:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            payment = client.order.create({
                'amount': net * 100,      # rupees convert
                'currency': 'INR',
                'payment_capture': 1
            })
        except Exception as e:
            print("Razorpay Error:", e)

    return render(request, 'patient_my_appointments.html', {
        'appointments': appointments,
        'doctor': doctor,
        'payment': payment,
        'order_id': payment['id'],
        'user': user
    })

# payment section
def success(request):
    try: 
        if request.method == "POST":    
            payment_id = request.POST.get('razorpay_payment_id')
            order_id = request.POST.get('razorpay_order_id')
            #signature = request.POST.get('razorpay_signature')

            user = User.objects.get(email=request.session['email'])
            patient = Patient.objects.filter(user=user).order_by('-id').first()  # Get the latest booking
     
        # You might want to store the payment_id with the booking
            patient.payment_id = payment_id  # Add this field to your model
            patient.payment_status = True
            patient.status = "Confirmed"
            patient.save()

            subject = 'Appointment Confirmation: Success'
            message = (
                f"Hello {patient.pname},\n\n"
                f"Your appointment with Dr. {patient.doctor.dname} has been successfully confirmed and paid for.\n\n"
                f"Appointment Details:\n"
                f"Date: {patient.date}\n"
                f"Time: {patient.time}\n"
                f"Doctor's Category: {patient.doctor.cchoice}\n\n"
                f"Payment Details:\n"
                f"Transaction ID: {payment_id}\n"
                f"Order ID: {order_id}\n\n"
                f"Thank you for choosing us."
            )
            from_email = settings.EMAIL_HOST_USER 
            recipient_list = [patient.email]

            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            
            return render(request, 'success.html', {'patient': patient, 'order_id': order_id})
        else:
            return redirect("index")

    except Exception as e:
        print("Payment Error:",e)
        return render(request, 'error.html')

def error(request):
    return render(request,"error.html")

def patient_payment_history(request):
    if 'email' not in request.session:
        return redirect('login')
    
    user = User.objects.get(email=request.session['email'])
    payments = Patient.objects.filter(user=user, payment_status=True).order_by('-date')
    products = Product.objects.filter(buyer=user, payment_status=True).order_by('-payment_date')

    return render(request, "patient_payment_history.html", {"payments": payments,"products": products})

def patient_appointment_history(request):
    if 'email' not in request.session:
        return redirect('login')

    user = User.objects.get(email=request.session['email'])
    appointments = Patient.objects.filter(user=user)
    return render(request, 'patient_appointment_history.html', {'appointments': appointments})

# product section
def product_add(request):
    if 'email' not in request.session:
        return redirect('login') 

    email = request.session.get("email")

    try:
        doctor = User.objects.get(email=email)
    except User.DoesNotExist:
        return redirect("login")

    if request.method == "POST":
        Product.objects.create(
            doctor=doctor,
            name=request.POST["name"],
            price=request.POST["price"],
            description=request.POST["description"],
            image=request.FILES["image"],
        )
        return redirect("product_view")

    return render(request, "product_add.html")


def product_view(request):
    if 'email' not in request.session:
        return redirect("login")
    email = request.session.get("email")

    try:
        doctor = User.objects.get(email=email)
    except User.DoesNotExist:
        return redirect("login")

    data = Product.objects.filter(doctor=doctor)
    return render(request, "product_view.html", {"data": data})

def product_edit(request, pk):
    product = Product.objects.get(id=pk)

    if request.method == "POST":
        product.name = request.POST.get("name")
        product.price = request.POST.get("price")
        product.description = request.POST.get("description")

        if request.FILES.get("image"):
            product.image = request.FILES.get("image")
        product.save()
        return redirect("product_view")
    return render(request, "product_edit.html", {"product": product})

def product_delete(request, pk):
    product = Product.objects.get(id=pk)
    product.delete()
    return redirect("product_view")

def doctor_earnings(request):
    doctor_user = request.session.get("email")  
    doctor = User.objects.get(email=doctor_user)
    doc_profile = Doctor.objects.get(doctor=doctor)

    filter_type = request.GET.get("filter", "all")  
    today = timezone.now().date()
    if filter_type == "today":
        start_date = today
    elif filter_type == "month":
        start_date = today - timedelta(days=30)
    elif filter_type == "year":
        start_date = today - timedelta(days=365)
    else:
        start_date = None

    #  Appointment Payments
    app_payments = Patient.objects.filter(doctor=doc_profile,payment_status=True)
    if start_date:
        app_payments = app_payments.filter(date__gte=start_date)

    #  Product Payments
    prod_payments = Product.objects.filter(doctor=doctor,payment_status=True
    )
    if start_date:
        prod_payments = prod_payments.filter(payment_date__gte=start_date)

    #  Combine
    combined = []

    for a in app_payments:
        combined.append({
            "type": "Appointment",
            "name": a.pname,
            "category": a.doctor.cchoice,
            "amount": a.doctor.charges,
            "payment_id": a.payment_id,
            "date": datetime.combine(a.date, datetime.min.time())
        })
    for p in prod_payments:
        combined.append({
            "type": "Product",
            "name": p.name,
            "category": "Product",
            "amount": p.price,
            "payment_id": p.payment_id,
            "date": datetime.combine(p.payment_date, datetime.min.time()) 
        })
    
    # sort by date desc
    combined = sorted(combined, key=lambda x: x["date"], reverse=True)

    # total earnings
    total = sum(item["amount"] for item in combined)

    # CSV Download
    if "download" in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="earnings.csv"'
        writer = csv.writer(response)
        writer.writerow(["Type", "Name", "Category/Product", "Amount", "Payment ID", "Date"])
        for row in combined:
            writer.writerow([row["type"], row["name"], row["category"], row["amount"], row["payment_id"], row["date"]])
        return response
    return render(request, "doctor_earnings.html", {"combined": combined, "total": total, "filter_type": filter_type })

def patient_buy_product(request):
    if 'email' not in request.session:
        return redirect('login')
     
    products = Product.objects.all()
    return render(request,'patient_buy_product.html',{'products': products})

def product_details(request, pk):
    if 'email' not in request.session:
        return redirect('login')

    product = Product.objects.get(id=pk)
    patient = User.objects.get(email=request.session['email'])

    # Razorpay order generate
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    payment = client.order.create({
        'amount': product.price * 100,
        'currency': 'INR',
        'payment_capture': 1
    })

    return render(request, 'product_details.html', {'product': product, 'payment': payment, 'order_id': payment['id'], 'patient': patient })

def product_payment_success(request):
    if request.method == "POST":
        payment_id = request.POST.get("razorpay_payment_id")
        order_id = request.POST.get("razorpay_order_id")
        product_id = request.POST.get("product_id")

        user = User.objects.get(email=request.session["email"])
        product = Product.objects.filter().last()  # latest buy

        product.buyer = user
        product.payment_id = payment_id
        product.payment_status = True
        product.payment_date = date.today()
        product.save()

        return render(request, 'product_payment_success.html', {'product': product,'payment_id': payment_id,
            'order_id': order_id,
            'payment_time': product.payment_date})

    return redirect('patient_buy_product')

def patient_product_history(request):
    user = User.objects.get(email=request.session["email"])
    products = Product.objects.filter(buyer=user).order_by('-payment_date')

    return render(request, "patient_product_history.html", {
        "products": products
    })
