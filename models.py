from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.timezone import now


# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


# Custom user model
class User(AbstractUser):
    email = models.EmailField(unique=True)  
    phone = models.CharField(max_length=15, null=True, blank=True)
    fullname = models.CharField(max_length=100, null=True, blank=True)
    address = models.TextField()
    profile = models.ImageField(upload_to="profile/")
    role = models.CharField(max_length=100, null=True, blank=True)
    username = None

    objects = CustomUserManager()

    class Meta:
        db_table = 'user'

    def __str__(self):
        return self.fullname

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []


class OrganDonationConsent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    full_name = models.CharField(max_length=200)
    age = models.IntegerField()
    blood_group = models.CharField(max_length=10)
    address = models.TextField()

    organs = models.TextField()  # list or single organ
    emergency_contact_name = models.CharField(max_length=200)
    emergency_contact_phone = models.CharField(max_length=15)
    signature = models.ImageField(upload_to='signatures/', null=True, blank=True)

    # The RSA signature of the signature image bytes
    signature_rsa = models.BinaryField(null=True, blank=True)

    # Optionally store which key id/version was used to sign (string)
    signature_key_id = models.CharField(max_length=100, null=True, blank=True)

    consent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Organ Donation Consent - {self.full_name}"


class OrganRequest(models.Model):
    ORGAN_CHOICES = [
        ('heart', 'Heart'),
        ('kidney', 'Kidney'),
        ('liver', 'Liver'),
        ('lungs', 'Lungs'),
        ('pancreas', 'Pancreas'),
        ('cornea', 'Cornea'),
    ]

    URGENCY_LEVEL = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    patient_name = models.CharField(max_length=200)
    patient_age = models.PositiveIntegerField()
    organ_needed = models.CharField(max_length=20, choices=ORGAN_CHOICES)
    urgency = models.CharField(max_length=10, choices=URGENCY_LEVEL)
    reason = models.TextField()
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_collected = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.organ_needed} needed for {self.patient_name}"

# class Category(models.Model):
#     name = models.CharField(max_length=100)
#     created_at = models.DateField(auto_now_add=True)


# class Donation(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
#     name = models.CharField(max_length=100)
#     category = models.ForeignKey(Category, on_delete=models.CASCADE)
#     quantity = models.CharField(max_length=100)
#     status = models.CharField(max_length=100, null=True, blank=True)
#     points = models.IntegerField(default=0)  # New field for points
#     created_at = models.DateField(auto_now_add=True)


# class Firm(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
#     name = models.CharField(max_length=100)
#     place = models.CharField(max_length=100)
#     created_at = models.DateField(auto_now_add=True)


# class Inventory(models.Model):
#     receiver = models.ForeignKey(Firm, on_delete=models.CASCADE, null=True)
#     category = models.ForeignKey(Category, on_delete=models.CASCADE)
#     collected_quantity = models.CharField(max_length=100, default=0)
#     required_quantity = models.CharField(max_length=100)
#     created_at = models.DateField(auto_now_add=True, null=True)
#     is_donated = models.BooleanField(default=False)


# class PointSystem(models.Model):
#     points = models.PositiveIntegerField(default=0)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)


# class ReceiverInventory(models.Model):
#     inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
#     date = models.DateTimeField(auto_now_add=True)


class ChatMessage(models.Model):
    id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(default=now)

    class Meta:
        db_table = 'chat_message'
        ordering = ['timestamp'] 

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} at {self.timestamp}"
    

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    feedback = models.CharField(max_length=150, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)