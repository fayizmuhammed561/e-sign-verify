from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('patient/register/', views.patient_register, name="patient_register"),
    path('doctor/register/', views.doctor_register, name="doctor_register"),
    path('login/', views.signin, name="login"),
    path('verify/otp/', views.verify_otp, name="verify_otp"),
    path('signout/', views.signout, name="signout"),
    path('forget_password/', views.forget_password, name="forget_password"),

    path('list_donars/', views.list_donars, name="list_donars"),

    # path('collectors/', views.collectors, name="collectors"),
    # path('add_collector/', views.add_collector, name="add_collector"),
    # path('delete_collector/<int:id>/', views.delete_collector, name="delete_collector"),

    path('organ-donation/', views.organ_donation_consent, name="organ_donation"),
    path('organ-donation/success/', views.consent_success, name="consent_success"),
    path('my_organ_history/', views.my_organ_history, name="my_organ_history"),
    path('patient_organ_history/', views.patient_organ_history, name="patient_organ_history"),

    path("doctor/organ-requests/", views.organ_request_list, name="organ_request_list"),
    path("doctor/organ-requests/add/", views.add_organ_request, name="add_organ_request"),
    path("doctor/organ-requests/edit/<int:id>/", views.edit_organ_request, name="edit_organ_request"),
    path("doctor/organ-requests/delete/<int:id>/", views.delete_organ_request, name="delete_organ_request"),
    path("organ-request/<int:request_id>/collected/", views.mark_collected, name="mark_collected"),


    path('profile/', views.profile, name="profile"),
    path('edit_profile/<int:id>/', views.edit_profile, name="edit_profile"),
    
    
    path('list_collectors/', views.list_collectors, name='list_collectors'),
    path('list_receivers/', views.list_receivers, name='list_receivers'),
    
    path('collector_chat/<int:id>/', views.collector_chat, name='collector_chat'),

    path('feedback/', views.feedback, name='feedback'),
    path('view_feedback/', views.view_feedback, name='view_feedback'),

    path('list_receiver/', views.list_receiver, name='list_receiver'),
    path('delete_receiver/<int:id>/', views.delete_receiver, name='delete_receiver'),

    path('verify_document/', views.verify_document, name='verify_document'),
    path('doctor/consents/<int:id>/verify/', views.verify_consent_signature, name='verify_consent_signature'),

    path('list_patient', views.list_patient, name='list_patient'),
    path('delete_patient/<int:id>/', views.delete_patient, name="delete_patient"),

    path('list_doctor', views.list_doctor, name='list_doctor'),
    path('delete_doctor/<int:id>/', views.delete_doctor, name="delete_doctor"),





]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)