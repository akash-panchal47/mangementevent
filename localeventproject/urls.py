from django.contrib import admin
from django.urls import path
from app import views   # your app
from django.conf import settings
from django.conf.urls.static import static

from app.views import CustomPasswordResetView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index, name="index"),
    path("add-event/", views.add_event, name="add_event"),

    path('upcoming-events/', views.upcoming_events, name='upcoming_events'),
    
    path('event/<int:event_id>/edit/', views.edit_event, name='edit_event'),
    path('event/<int:event_id>/delete/', views.delete_event, name='delete_event'),

    path('event/<int:event_id>/pay/', views.pay_event, name='pay_event'),
    path('payment-success/<int:event_id>/', views.payment_success, name="payment_success"),
   

    path("explore-events/", views.explore_events, name="explore_events"),
     path('event/<int:event_id>/', views.event_detail, name='event_detail'), 

    path("contact/", views.contact_view, name="contact"),

    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),

    
    path("subscribe/", views.subscribe, name="subscribe"),

    path('add-festival/', views.add_festival, name='add_festival'),
    path('festivals/', views.festivals_view, name="festivals"),
    
    path("dashboard/", views.dashboard, name="dashboard"),
    path("accept/<int:reg_id>/", views.accept_user, name="accept_user"),
    path("reject/<int:reg_id>/", views.reject_user, name="reject_user"),


    path("event/<int:event_id>/", views.event_detail, name="event_detail"),
    path("event/<int:event_id>/join/", views.join_event, name="join_event"),
  
    path('registration/<int:registration_id>/<str:action>/', views.registration_action, name='registration_action'),
 path('generate-pass/<int:event_id>/', views.generate_pass_pdf, name='generate_pass_pdf'),


    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
    template_name='app/password_reset_done.html'
), name='password_reset_done'),
path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
    template_name='app/password_reset_confirm.html'
), name='password_reset_confirm'),
path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
    template_name='app/password_reset_complete.html'
), name='password_reset_complete'),



   path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-dashboard/accept/<int:reg_id>/", views.admin_accept_user, name="admin_accept_user"),
    path("admin-dashboard/reject/<int:reg_id>/", views.admin_reject_user, name="admin_reject_user"),
    path("admin-dashboard/delete/<int:reg_id>/", views.admin_delete_registration, name="admin_delete_registration"),

     path('payment-receipt/<int:registration_id>/', views.payment_receipt_view, name='payment_receipt'),
      # Option 2: change the URL name to match the function

]

if settings.DEBUG:  
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
