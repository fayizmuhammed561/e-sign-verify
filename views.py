from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password

import random
from .forms import *
import base64
from django.core.files.base import ContentFile
from .crypto import *


# Create your views here.
import pycurl
from urllib.parse import urlencode

def sends_mail(mail, msg):
    crl = pycurl.Curl()
    crl.setopt(crl.URL, 'https://thinkersstemhub.com/gateway.php?')
    data = {'email': mail, 'msg': msg}
    pf = urlencode(data)
    crl.setopt(crl.POSTFIELDS, pf)
    crl.perform()
    crl.close()


def generate_otp():
    return str(random.randint(1000, 9999))
    

def home(request):
    return render(request, 'home.html')


def patient_register(request):
    if request.method == "POST":
        fullname = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        image = request.FILES.get('image')
        password = request.POST.get('pass1')
        confirm_password = request.POST.get('pass2')

        if User.objects.filter(email=email).exists():
            messages.error(request, "email already exits")
            return redirect('patient_register')
        
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('patient_register')

        result = User.objects.create(fullname=fullname,email=email,phone=phone,
                                     address=address,profile=image,role="patient",password=make_password(password))
        result.save()
        messages.success(request, "Donar registered successfully.")
        return redirect('login')
    return render(request, 'register.html')


def doctor_register(request):
    if request.method == "POST":
        fullname = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        image = request.FILES.get('image')
        password = request.POST.get('pass1')
        confirm_password = request.POST.get('pass2')

        if User.objects.filter(email=email).exists():
            messages.error(request, "email already exits")
            return redirect('doctor_register')
        
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('doctor_register')

        result = User.objects.create(fullname=fullname,email=email,phone=phone,
                                     profile=image,role="doctor",password=make_password(password))
        result.save()
        messages.success(request, "Doctor registered successfully.")
        return redirect('login')
    return render(request, 'doctor_register.html')


def signin(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(email=email, password=password)

        if user is not None:
            if user.is_superuser:
                login(request, user)
                return redirect('home')

            # DO NOT LOGIN HERE
            request.session['pre_auth_user_id'] = user.id

            otp = generate_otp()
            print("otpppp",otp)
            request.session['otp'] = otp
            request.session['otp_email'] = email

            sends_mail(email, f"Your OTP is {otp}")
            messages.success(request, "OTP sent successfully.")
            return redirect('verify_otp')

        else:
            messages.error(request, "Invalid Email or Password")

    return render(request, 'login.html')



def verify_otp(request):
    if request.method == "POST":
        user_otp = request.POST.get("otp")
        original_otp = request.session.get("otp")

        if user_otp == original_otp:
            
            user_id = request.session.get("pre_auth_user_id")

            from django.contrib.auth import get_user_model
            User = get_user_model()

            try:
                user = User.objects.get(id=user_id)
                login(request, user)  # ✅ Login happens here after OTP success
            except User.DoesNotExist:
                messages.error(request, "Session expired. Please login again.")
                return redirect("signin")

            # Clear OTP session data
            request.session.pop('otp', None)
            request.session.pop('otp_email', None)
            request.session.pop('pre_auth_user_id', None)

            messages.success(request, "OTP Verified Successfully!")
            return redirect('home')
        else:
            messages.error(request, "Invalid OTP")

    return render(request, 'verify_otp.html')



def forget_password(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not User.objects.filter(email=email).exists():
            messages.error(request, "email doesn't exits")
            return redirect('forget_password')
        
        user = User.objects.get(email=email)
        user.password = make_password(password)
        user.save()
        messages.success(request,"password changed successfully.")
        return redirect('login')

    return render(request, 'forget_password.html')


def signout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home')


def list_donars(request):
    result = User.objects.filter(role="donar")
    return render(request, 'list_donars.html', {'result': result})





# def collectors(request):
#     result = User.objects.filter(role="collector")
#     return render(request, 'list_collectors.html', {'result': result})


# def add_collector(request):
#     if request.method == "POST":
#         fullname = request.POST.get('name')
#         email = request.POST.get('email')
#         phone = request.POST.get('phone')
#         image = request.FILES.get('image')
#         password = request.POST.get('pass1')
#         confirm_password = request.POST.get('pass2')

#         if User.objects.filter(email=email).exists():
#             messages.error(request, "email already exits")
#             return redirect('add_collector')
        
#         if password != confirm_password:
#             messages.error(request, "Passwords do not match.")
#             return redirect('add_collector')

#         result = User.objects.create(fullname=fullname,email=email,phone=phone,
#                                      profile=image,role="collector",password=make_password(password))
#         result.save()
#         messages.success(request, "Add Collector successfully.")
#         return redirect('collectors')
#     return render(request, "add_collector.html")


# def delete_collector(request, id):
#     user = get_object_or_404(User, id=id)
#     user.delete()
#     return redirect('collectors')


def profile(request):
    profile = request.user
    return render(request, 'profile.html', {'profile':profile})


def edit_profile(request, id):
    profile = get_object_or_404(User, id=id)

    if request.method == "POST":
        fullname = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        if request.user.role == "donar":
            address = request.POST.get('address')
        image = request.FILES.get('image')

        if User.objects.filter(email=email).exclude(id=profile.id).exists():
            messages.error(request, "email already exits")
            return redirect('edit_profile',id=id)
        
        if image:
            profile.profile = image
            profile.save()

        profile.fullname=fullname
        profile.email=email
        profile.phone=phone
        profile.save()
        if request.user.role == "donar":
            if address:
                profile.address=address
                profile.save()
        return redirect('profile')
        
    return render(request, 'edit_profile.html', {'profile': profile})


# ensure keys exist on server startup (safe to call each request - it will no-op if exists)
ensure_keys()

def organ_donation_consent(request):
    if request.method == "POST":
        full_name = request.POST.get('full_name')
        age = request.POST.get('age')
        blood_group = request.POST.get('blood_group')
        address = request.POST.get('address')
        organ = request.POST.get('organ')

        emergency_contact_name = request.POST.get('emergency_contact_name')
        emergency_contact_phone = request.POST.get('emergency_contact_phone')
        consent = True if request.POST.get('consent') == 'on' else False

        signature_data = request.POST.get('signature_data')  # dataURL from SignaturePad

        consent_obj = OrganDonationConsent.objects.create(
            user=request.user,
            full_name=full_name,
            age=age,
            blood_group=blood_group,
            address=address,
            organs=organ,
            emergency_contact_name=emergency_contact_name,
            emergency_contact_phone=emergency_contact_phone,
            consent=consent
        )

        # Saving signature image + create RSA signature of the raw image bytes
        if signature_data:
            # split "data:image/png;base64,...."
            format, imgstr = signature_data.split(';base64,')
            ext = format.split('/')[-1]  # typically 'png'
            img_bytes = base64.b64decode(imgstr)

            # Save image file to ImageField
            file_name = f"signature_{consent_obj.id}.{ext}"
            django_file = ContentFile(img_bytes, name=file_name)
            consent_obj.signature = django_file
            consent_obj.save()  # save to get file stored and path set

            # Now sign the raw image bytes using server private key
            signature_bytes = sign_bytes(img_bytes)
            consent_obj.signature_rsa = signature_bytes
            # optional key id/version
            consent_obj.signature_key_id = "v1" 
            consent_obj.save()

        return redirect('consent_success')

    return render(request, "organ_donation_form.html")



# def organ_donation_consent(request):
#     if request.method == "POST":
#         full_name = request.POST.get('full_name')
#         age = request.POST.get('age')
#         blood_group = request.POST.get('blood_group')
#         address = request.POST.get('address')
#         organ = request.POST.get('organ')

#         emergency_contact_name = request.POST.get('emergency_contact_name')
#         emergency_contact_phone = request.POST.get('emergency_contact_phone')
#         consent = True if request.POST.get('consent') == 'on' else False

#         signature_data = request.POST.get('signature_data')

#         consent_obj = OrganDonationConsent.objects.create(
#             user=request.user,
#             full_name=full_name,
#             age=age,
#             blood_group=blood_group,
#             address=address,
#             organs=organ,
#             emergency_contact_name=emergency_contact_name,
#             emergency_contact_phone=emergency_contact_phone,
#             consent=consent
#         )

#         # Saving signature image
#         if signature_data:
#             format, imgstr = signature_data.split(';base64,')
#             ext = format.split('/')[-1]
#             file_data = ContentFile(base64.b64decode(imgstr), name=f"signature.{ext}")
#             consent_obj.signature = file_data
#             consent_obj.save()

#         return redirect('consent_success')

#     return render(request, "organ_donation_form.html")


def consent_success(request):
    return render(request, "consent_success.html")


def my_organ_history(request):
    result = OrganDonationConsent.objects.filter(user=request.user).order_by("-created_at")

    return render(request, "my_organ_history.html", {'result': result})


#---------------------------------------------  Doctor  ----------------------------------------------------


def add_organ_request(request):
    if request.method == "POST":
        patient_name = request.POST.get("patient_name")
        patient_age = request.POST.get("patient_age")
        organ_needed = request.POST.get("organ_needed")
        urgency = request.POST.get("urgency")
        reason = request.POST.get("reason")

        OrganRequest.objects.create(
            patient_name=patient_name,
            patient_age=patient_age,
            organ_needed=organ_needed,
            urgency=urgency,
            reason=reason,
            doctor=request.user,
        )
        return redirect("organ_request_list")

    return render(request, "add_organ_request.html")


def organ_request_list(request):
    requests = OrganRequest.objects.all().order_by('-created_at')
    return render(request, "organ_request_list.html", {"requests": requests})


def mark_collected(request, request_id):
    organ_request = OrganRequest.objects.get(id=request_id)
    organ_request.is_collected = True
    organ_request.save()
    return redirect('organ_request_list')


def edit_organ_request(request, id):
    req = get_object_or_404(OrganRequest, id=id)

    if request.method == "POST":
        req.patient_name = request.POST.get("patient_name")
        req.patient_age = request.POST.get("patient_age")
        req.organ_needed = request.POST.get("organ_needed")
        req.urgency = request.POST.get("urgency")
        req.reason = request.POST.get("reason")
        req.save()

        return redirect("organ_request_list")

    return render(request, "edit_organ_request.html", {"req": req})


def delete_organ_request(request, id):
    req = get_object_or_404(OrganRequest, id=id)
    req.delete()
    return redirect("organ_request_list")


def patient_organ_history(request):
    result = OrganDonationConsent.objects.all().order_by("-created_at")

    return render(request, "patient_organ_history.html", {'result': result})



#--------------------------------------------  Admin  ---------------------------------------


def verify_document(request):
    result = OrganDonationConsent.objects.all().order_by("-created_at")
    return render(request, 'verify_document.html', {'result': result})


def verify_consent_signature(request, id):
    obj = get_object_or_404(OrganDonationConsent, id=id)

    # Read signature image bytes (from file storage)
    if not obj.signature:
        message = "No signature image to verify."
        verified = False
    elif not obj.signature_rsa:
        message = "No RSA signature found for this form."
        verified = False
    else:
        # get raw bytes from file
        storage = obj.signature.storage
        sig_path = obj.signature.name
        with storage.open(sig_path, 'rb') as f:
            img_bytes = f.read()

        verified = verify_bytes(img_bytes, bytes(obj.signature_rsa))
        message = "Signature verified (OK)." if verified else "Signature verification FAILED."

    return render(request, "verify_signature.html", {
        "obj": obj,
        "verified": verified,
        "message": message,
    })


def list_patient(request):
    result = User.objects.filter(role="patient")
    return render(request, "list_patient.html", {'result': result})


def delete_patient(request, id):
    user = get_object_or_404(User, id=id)
    user.delete()
    return redirect('list_patient')


def list_doctor(request):
    result = User.objects.filter(role="doctor")
    return render(request, "list_doctor.html", {'result': result})


def delete_doctor(request, id):
    user = get_object_or_404(User, id=id)
    user.delete()
    return redirect('list_doctor')


#-----------------------------------------------------------------------------------------------------------------------



# receiver side list all collectors for chat.
def list_collectors(request):
    result = User.objects.filter(role="collector")
    return render(request, 'list_all_collectors.html', {'result': result})


def collector_chat(request, id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    sender = request.user
    receiver = get_object_or_404(User, id=id)
    receiver_id = receiver.id
    print(receiver_id)

    # Fetch chat messages between these users
    messages = ChatMessage.objects.filter(
        (models.Q(sender=sender, receiver=receiver_id) |
         models.Q(sender=receiver_id, receiver=sender))
    ).order_by('timestamp')

    if request.method == "POST":
        message_content = request.POST.get("message")

        if message_content:
            # Create and save a new chat message
            ChatMessage.objects.create(
                sender=sender, receiver=receiver, message=message_content
            )
            return redirect('collector_chat', id=id)

    return render(request, 'chat.html', {"messages": messages, "receiver": receiver})


def list_receivers(request):
    result = User.objects.filter(role="receiver")
    return render(request, 'list_all_receivers.html', {'result': result})


def view_feedback(request):
    result = Feedback.objects.all()
    return render(request, 'view_feedback.html', {'result': result})


def feedback(request):
    if request.method == "POST":
        feedback = request.POST.get('feedback')
        result = Feedback.objects.create(user=request.user, feedback=feedback)
        result.save()
        messages.success(request, 'Successfully added feedback.')
        return redirect('feedback')
    return render(request, 'feedback.html')


def list_receiver(request):
    result = User.objects.filter(role="receiver")
    return render(request, 'list_receiver.html', {'result': result})


def delete_receiver(request, id):
    user = get_object_or_404(User, id=id)
    user.delete()
    return redirect('list_receiver')