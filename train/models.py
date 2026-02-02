from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Train(models.Model):
    Train_number=models.IntegerField(unique=True)
    Train_name=models.CharField(max_length=50)
    Source=models.CharField(max_length=50)
    Destination=models.CharField(max_length=50)
    Departure_Time=models.DateTimeField()
    Arrival_Time=models.DateTimeField()
    Total_seats=models.IntegerField()
    Available_seats=models.IntegerField()
    def __str__(self):
        return f"{self.Train_number} - {self.Train_name}"

class Booking(models.Model):
    STATUS_CHOICES=[
        ('Pending', 'Pending'),
        ('CONFIRMED','Confirmed'),
        ('CANCELLED','Cancelled'),
    ]
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    Train=models.ForeignKey(Train,on_delete=models.CASCADE)
    Journey_Date=models.DateField()
    Number_of_seats=models.IntegerField()
    Seat_number=models.CharField(max_length=20)
    Booking_status=models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )
    Booking_date=models.DateTimeField(auto_now_add=True)
    pnr=models.CharField(max_length=20,unique=True)
    def __str__(self):
        return f"Booking {self.pnr} - {self.user.username}"

class Payment(models.Model):
    PAYMENT_STATUS=[
        ('SUCCESS','Success'),
        ('FAILED','Failed'),
        ('PENDING','Pending'),
    ]
    booking=models.OneToOneField(Booking,on_delete=models.CASCADE)
    Amount=models.IntegerField()
    Payment_Status=models.CharField(
        max_length=50,
        choices=PAYMENT_STATUS,
        default='PENDING'
    )
    payment_date=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"payment for booking {self.booking.pnr}"
    
class Refund(models.Model):
    REFUND_STATUS = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    refund_amount = models.IntegerField()
    refund_status = models.CharField(
        max_length=20,
        choices=REFUND_STATUS,
        default='PENDING'
    )
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Refund for {self.booking.pnr}"



