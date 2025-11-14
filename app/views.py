from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import requests
from django.contrib.auth.models import User
from .models import Registration
from django.utils.timezone import now
from .forms import ProfileUpdateForm
from django.contrib.auth.views import PasswordResetView
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
import pdfkit
import random, string

from .forms import RegisterForm, EventForm, ContactForm, FestivalForm
from .models import Subscriber, Event, Festival, EventPayment, FestivalCategory
from instamojo_wrapper import Instamojo

# Home page (only future events)
def index(request):
    today = timezone.now().date()
    expire_date = today - timedelta(days=15)  # 15 days ago

    # All upcoming events
    upcoming_events = Event.objects.all().order_by('date')

    # Festivals from last 15 days up to future
    festivals = Festival.objects.filter(date__gte=expire_date).order_by('date')

    return render(request, 'app/index.html', {
        'events': upcoming_events,
        'festivals': festivals,   # send festivals to template
    })

@login_required
def add_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            if request.user.is_authenticated:
                event.created_by = request.user
            event.save()
            return redirect('upcoming_events')  
    else:
        form = EventForm()
    return render(request, 'app/event_form.html', {'form': form})


def upcoming_events(request):
    events = Event.objects.all().order_by('date')
    return render(request, 'app/upcoming_events.html', {'events': events})


@login_required
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.user != event.created_by:
        return redirect('index')  # Or show a permission denied page
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('event_detail', event_id=event.id)
    else:
        form = EventForm(instance=event)
    return render(request, 'app/edit_event.html', {'form': form, 'event': event})

@login_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.user != event.created_by:
        return redirect('index')
    if request.method == 'POST':
        event.delete()
        return redirect('index')
    return render(request, 'app/delete_event.html', {'event': event})

# end this event code 


api = Instamojo(
    api_key=settings.INSTAMOJO_API_KEY,
    auth_token=settings.INSTAMOJO_AUTH_TOKEN,
    endpoint=settings.INSTAMOJO_ENDPOINT
)

@login_required(login_url='login')
def pay_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if event.entry_fee <= 0:
        # Free event – auto-register
        Registration.objects.get_or_create(user=request.user, event=event, status='accepted')
        return redirect('event_detail', event_id=event.id)

    try:
        response = api.payment_request_create(
            amount=str(event.entry_fee),
            purpose=event.title,
            buyer_name=request.user.username,
            email=request.user.email or "test@example.com",
            redirect_url=request.build_absolute_uri(f"/payment-success/{event.id}/"),
            send_email=True,
            allow_repeated_payments=False
        )

        if 'payment_request' in response:
            return redirect(response['payment_request']['longurl'])
        else:
            error_message = response.get('message', 'Could not create payment request.')
            return render(request, "app/pay_event.html", {"event": event, "error": error_message})

    except Exception as e:
        return render(request, "app/pay_event.html", {"event": event, "error": str(e)})


def payment_success(request):
    payment_id = request.GET.get('payment_id')
    payment_request_id = request.GET.get('payment_request_id')

    # Verify payment status
    url = f"https://www.instamojo.com/api/1.1/payment-requests/{payment_request_id}/{payment_id}/"
    headers = {
        "X-Api-Key": "53916a4219d77147ae4044a133bd1059",
        "X-Auth-Token": "96c8fe9d41c94e9f80ef74475b65b002",
    }
    response = requests.get(url, headers=headers)
    payment_details = response.json()

    if payment_details['payment']['status'] == 'Credit':
        # Payment successful
        # Update your database accordingly
        return render(request, 'payment_success.html', {'payment_details': payment_details})
    else:
        # Payment failed
        return render(request, 'payment_failed.html')
    


def contact_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        full_message = f"Message from {name} <{email}>:\n\n{message}"

        try:
            send_mail(
                subject,
                full_message,
                email,
                ["youremail@gmail.com"],
                fail_silently=False,
            )
            messages.success(request, "✅ Your message has been sent successfully!")
            return redirect("contact")
        except Exception as e:
            messages.error(request, f"❌ Error sending message: {e}")

    return render(request, "app/contact.html")


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Ensure normal users are never superusers/staff
            user.is_superuser = False
            user.is_staff = False
            user.save()
            login(request, user)
            return redirect("index")
    else:
        form = RegisterForm()
    return render(request, "app/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            return render(request, "app/login.html", {"error": "Invalid username or password"})
    return render(request, "app/login.html")


@login_required
def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("index")
    return render(request, "app/logout.html")


#def event_detail(request, event_id):
 #   event = get_object_or_404(Event, id=event_id)
  #  return render(request, 'app/event_detail.html', {'event': event})


def subscribe(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if email:
            if Subscriber.objects.filter(email=email).exists():
                messages.warning(request, "You are already subscribed!")
            else:
                Subscriber.objects.create(email=email)
                messages.success(request, "Thank you for subscribing!")
        return redirect("index")
    return redirect("index")


@login_required
def add_festival(request):
    if request.method == 'POST':
        form = FestivalForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('festivals')  
    else:
        form = FestivalForm()
    return render(request, 'app/add_festival.html', {'form': form})

# Display all Festivals
def festivals_view(request):
    today = timezone.now().date()
    expire_date = today - timedelta(days=15)  # 15 days ago

    # Only show festivals whose date is within the last 15 days or in the future
    festivals = Festival.objects.filter(date__gte=expire_date).order_by('date')
    
    return render(request, "app/festivals.html", {"festivals": festivals})


def explore_events(request):
    events = Event.objects.all().order_by('date')
    return render(request, "app/explore_event.html", {"events": events})




@login_required
def dashboard(request):
    # Profile update
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = ProfileUpdateForm(instance=request.user)

    # User's own registrations
    registrations = Registration.objects.filter(user=request.user).select_related("event")

    # All registrations (for this table)
    all_registrations = Registration.objects.select_related("event", "user")

    context = {
        "form": form,
        "registrations": registrations,
        "all_registrations": all_registrations,
    }
    return render(request, "app/dashboard.html", context)



@login_required
def accept_user(request, reg_id):
    reg = get_object_or_404(Registration, id=reg_id)
    reg.status = "accepted"
    reg.save()
    return redirect("dashboard")


@login_required
def reject_user(request, reg_id):
    reg = get_object_or_404(Registration, id=reg_id)
    reg.status = "rejected"
    reg.save()
    return redirect("dashboard")


@login_required
def registration_action(request, registration_id, action):
    registration = get_object_or_404(Registration, id=registration_id, user=request.user)
    
    if action in ['accepted', 'rejected']:
        registration.status = action
        registration.save()
    
    return redirect('dashboard')


@login_required
def join_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # prevent duplicate join
    if Registration.objects.filter(user=request.user, event=event).exists():
        return redirect('dashboard')

    Registration.objects.create(
        user=request.user,
        event=event,
        status='pending',   # default
        created_at=now()
    )
    return redirect('dashboard')

@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    already_joined = Registration.objects.filter(user=request.user, event=event).exists()
    return render(request, "app/event_detail.html", {
        "event": event,
        "already_joined": already_joined,
    })


class CustomPasswordResetView(PasswordResetView):
    template_name = "app/forget_password.html"   # form page template
    email_template_name = "emails/password_reset_email.html"
    subject_template_name = "emails/password_reset_subject.txt"
    success_url = '/password_reset/done/'   # ← remove the comma here



@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect("dashboard")

    users = User.objects.all()
    all_registrations = Registration.objects.select_related("user", "event")

    return render(request, "app/admin_dashboard.html", {
        "users": users,
        "all_registrations": all_registrations,
    })


@login_required
def admin_accept_user(request, reg_id):
    if not request.user.is_staff:
        return redirect("dashboard")

    reg = get_object_or_404(Registration, id=reg_id)
    reg.status = "accepted"
    reg.save()
    return redirect("admin_dashboard")


@login_required
def admin_reject_user(request, reg_id):
    if not request.user.is_staff:
        return redirect("dashboard")

    reg = get_object_or_404(Registration, id=reg_id)
    reg.status = "rejected"
    reg.save()
    return redirect("admin_dashboard")


@login_required
def admin_delete_registration(request, reg_id):
    if not request.user.is_staff:
        return redirect("dashboard")

    reg = get_object_or_404(Registration, id=reg_id)
    reg.delete()
    return redirect("admin_dashboard")


@login_required
def payment_receipt_view(request, registration_id):
    # Get the registration object for the logged-in user
    registration = get_object_or_404(Registration, id=registration_id, user=request.user)
    
    return render(request, "app/payment_receipt.html", {
        "registration": registration
    })


@login_required
def generate_pass_pdf(request, event_id):
    # Get the event
    event = get_object_or_404(Event, id=event_id)

    # Prevent duplicate registration
    registration, created = Registration.objects.get_or_create(
        user=request.user,
        event=event,
        defaults={'status': 'accepted'}
    )

    # Generate a pass code if new
    if created or not registration.pass_code:
        registration.pass_code = get_random_string(length=10).upper()
        registration.save()

    # Render HTML template for PDF
    html = render_to_string('app/pass_pdf.html', {
        'registration': registration,
        'event': event
    })

    # Configure pdfkit with local wkhtmltopdf executable
    path_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

    # PDF options
    options = {
        'enable-local-file-access': None,  # required to load local CSS/images
        'page-size': 'A4',
        'encoding': 'UTF-8',
    }

    # Generate PDF
    pdf = pdfkit.from_string(html, False, configuration=config, options=options)

    # Return PDF as response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="pass_{event.id}_{request.user.username}.pdf"'

    return response