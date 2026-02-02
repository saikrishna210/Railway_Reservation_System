from django.contrib import admin

# Register your models here.
from .models import Train,Booking,Payment,Refund

admin.site.register(Train)
admin.site.register(Booking)
admin.site.register(Payment)
admin.site.register(Refund)
