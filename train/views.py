from django.shortcuts import render,redirect, get_object_or_404
# Create your views here.
from .models import Train,Booking,Payment,Refund,profile
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import uuid
from django.contrib.auth import login


def home(request):
    return render(request, 'train/home.html')

@login_required
def book_ticket(request, train_id):
    train = get_object_or_404(Train, id=train_id)

    if request.method == "POST":
        journey_date = request.POST.get("journey_date")
        seats = int(request.POST.get("seats"))
        exists = Booking.objects.filter(
            user=request.user,
            Train=train,
            Journey_Date=journey_date,
            Booking_status='CONFIRMED'
        ).exists()

        if exists:
            messages.error(
                request,
                "You already booked this train for this date"
            )
            return redirect('train:my_bookings')

        if seats > train.Available_seats:
            messages.error(request, "Not enough seats available")
            return redirect('train:train_detail', train_id=train.id)

        with transaction.atomic():
            Booking.objects.create(
                user=request.user,
                Train=train,
                Journey_Date=journey_date,
                Number_of_seats=seats,
                Seat_number="Auto",
                Booking_status='CONFIRMED',
                pnr=generate_pnr()  # your PNR function
            )
            train.Available_seats -= seats
            train.save()

        messages.success(request, "Booking successful")
        return redirect('train:my_bookings')

    return render(request, 'train/book_ticket.html', {'train': train})


#1->train views
def search_train(request):#train_search_view
    if request.method=='POST':
        source=request.GET.get('source','').strip()
        destination=request.GET.get('destination','').strip()
        journey_date=request.GET.get('journey_date')
        trains = Train.objects.all()
        if source:
            trains=trains.filter(Source__icontains=source)
        if destination:
            trains=trains.filter(Destination__icontains=destination)
        return render(request, 'train/train_list.html', {
            'trains': trains,
            'source': source,
            'destination': destination,
            'journey_date': journey_date
        })
    # return render(request, 'train/train_list.html', {'trains': trains})

def train_detail(request,train_id):#train_detail_view
    train = get_object_or_404(Train, id=train_id)
    return render(request, 'train/train_detail.html', {'train': train})

#2->Booking views
@login_required
def create_booking(request, train_id):
    train = get_object_or_404(Train, id=train_id)

    if request.method == 'POST':
        journey_date = request.POST.get('journey_date')
        seats = int(request.POST.get('number_of_seats'))

        if seats > train.Available_seats:
            messages.error(request, 'Not enough seats available')
            return redirect('train:train_detail', train_id=train_id)

        pnr = str(uuid.uuid4()).split('-')[0].upper()

        booking = Booking.objects.create(
            user=request.user,
            Train=train,
            Journey_Date=journey_date,
            Number_of_seats=seats,
            Seat_number="Auto-1",
            Booking_status="Pending",
            pnr=pnr
        )

        train.Available_seats -= seats
        train.save()

        return redirect('train:booking_confirmation', booking_id=booking.id)
    return render(request, 'train/book_ticket.html', {'train': train})


@login_required
def booking_confirmation(request,booking_id):#booking confirmation
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'train/booking_confirmation.html', {'booking': booking})

@login_required
def my_bookings(request): #my_bookings
    bookings=Booking.objects.filter(user=request.user,Booking_status__in=['Pending', 'CONFIRMED'])
    return render(request, 'train/my_bookings.html', {
        'bookings': bookings
    })
    

#3->payment views
@login_required
def payment_page(request,booking_id):#payment page
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    amount=booking.Number_of_seats*450 #example amount
    return render(request,'train/payment.html',{
        'booking':booking,
        'amount':amount
    })

@login_required
def card_payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id,user=request.user)
    return render(request, 'train/card_payment.html', {
        'booking': booking
    })


@login_required
def process_payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    # ✅ Check if payment already exists
    if hasattr(booking, 'payment'):
        return redirect('train:payment_success', payment_id=booking.payment.id)
    amount = booking.Number_of_seats * 450
    payment = Payment.objects.create(
        booking=booking,
        Amount=amount,
        Payment_Status="SUCCESS"
    )
    booking.Booking_status = "CONFIRMED"
    booking.save(update_fields=["Booking_status"])
    return redirect('train:payment_success', payment_id=payment.id)


@login_required
def payment_success(request, payment_id): #payment success
    payment = get_object_or_404(Payment, id=payment_id)
    booking=payment.booking
    return render(request, 'train/payment_success.html', {
        'booking': booking,
        'payment':payment
    })

#Refund views
@login_required
def cancel_booking(request,booking_id):  #cancel booking
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.Booking_status=='CANCELLED':
        messages.warning(request,"Booking already cancelled")
        return redirect('train:my_bookings')
    booking.Booking_status='CANCELLED'
    booking.save(update_fields=["Booking_status"])
    if hasattr(booking, 'payment') and not hasattr(booking, 'refund'):
        Refund.objects.create(
            booking=booking,
            refund_amount=booking.payment.Amount,
            refund_status="PENDING"
        )
    messages.success(
        request,
        "Booking cancelled. Refund will be processed in 3–5 working days."
    )
    return redirect('train:my_bookings')


@login_required
def refund_status(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    refund = get_object_or_404(Refund, booking=booking)

    return render(request, 'train/refund_status.html', {
        'booking': booking,
        'refund': refund
    })

def guest_login(request):
    # create unique guest username
    guest_username = f"guest_{uuid.uuid4().hex[:8]}"

    user = User.objects.create_user(
        username=guest_username,
        password=None
    )

    profile.objects.create(
        user=user,
        is_guest=True
    )
    login(request, user)
    return redirect('train:home')


def guest_restricted(view_func):
    def wrapper(request, *args, **kwargs):
        if hasattr(request.user, 'profile') and request.user.profile.is_guest:
            return redirect('train:train_list')
        return view_func(request, *args, **kwargs)
    return wrapper

