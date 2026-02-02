from django.urls import path

from .import views
app_name='train'

urlpatterns=[
   path('',views.home,name='home'),
   path('search/',views.search_train,name='search_train'),
   path('train/<int:train_id>/', views.train_detail, name='train_detail'),

   path('train/<int:train_id>/book/',views.create_booking,name='create_booking'),
   path('booking/<int:booking_id>/confirmation/',views.booking_confirmation,name='booking_confirmation'),
   path('my-bookings/',views.my_bookings,name='my_bookings'),


   path('booking/<int:booking_id>/payment/',views.payment_page,name='payment_page'),
   
   path('booking/<int:booking_id>/card-payment/', views.card_payment, name='card_payment'),

   path('booking/<int:booking_id>/process_payment/',views.process_payment,name='process_payment'),
   path('payment/<int:payment_id>/success/',views.payment_success,name='payment_success'),

   path('booking/<int:booking_id>/cancel/',views.cancel_booking,name='cancel_booking'),
   path('booking/<int:booking_id>/refund/', views.refund_status, name='refund_status'),
]
