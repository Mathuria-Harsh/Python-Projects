"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from myapp import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('doctor_index/',views.doctor_index,name='doctor_index'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('patient_doctors/', views.patient_doctors, name='patient_doctors'),
    path('doctor_doctor/', views.doctor_doctor, name='doctor_doctor'),
    path('doctor_details/',views.doctor_details,name='doctor_details'),
    path('otp/', views.otp, name='otp'),
    path('fpass/', views.fpass, name='fpass'),
    path('changepass/', views.changepass, name='changepass'),
    path('newpass/', views.newpass, name='newpass'),
    path('patient_profile/',views.patient_profile,name='patient_profile'),
    path('doctor_profile/',views.doctor_profile,name='doctor_profile'),
    path('product_add/',views.product_add,name='product_add'),
    path('product_view/',views.product_view,name='product_view'),
    path("product_edit/<int:pk>/", views.product_edit, name="product_edit"),
    path("product_delete/<int:pk>/", views.product_delete, name="product_delete"),
    path('delete/<int:pk>',views.delete,name='delete'),
    path('patient_book_appointment/<int:pk>',views.patient_book_appointment,name='patient_book_appointment'),
    path('doctor_other_details/<int:pk>',views.doctor_other_details,name='doctor_other_details'),
    path('patient_doctor_details/<int:pk>',views.patient_doctor_details,name='patient_doctor_details'),
    path('doctor_dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor_accept_appointment/<int:pid>/', views.doctor_accept_appointment, name='doctor_accept_appointment'),
    path('doctor_cancel_appointment/<int:pid>/', views.doctor_cancel_appointment, name='doctor_cancel_appointment'),
    path('patient_my_appointments/', views.patient_my_appointments, name='patient_my_appointments'),
    path('success/', views.success, name='success'),
    path('error/', views.error, name='error'),
    path("patient_payment_history/", views.patient_payment_history, name="patient_payment_history"),
    path("patient_appointment_history/", views.patient_appointment_history, name="patient_appointment_history"),
    path('doctor_earnings/', views.doctor_earnings, name="doctor_earnings"),
    path('patient_buy_product/',views.patient_buy_product,name='patient_buy_product'),
    path('product_details/<int:pk>/',views.product_details,name='product_details'),
    path('product_payment_success/',views.product_payment_success,name='product_payment_success'),
    path('patient_product_history/', views.patient_product_history, name='patient_product_history'),


]