from django.contrib import admin
from .models import Event, Subscriber, Festival, EventPayment, FestivalCategory, Registration


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "location", "entry_fee", "created_by")
    search_fields = ("title", "location", "created_by__username")
    list_filter = ("date", "location")


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "subscribed_at")
    search_fields = ("email",)


@admin.register(Festival)
class FestivalAdmin(admin.ModelAdmin):
    list_display = ("name", "date", "location", "organizer")
    search_fields = ("name", "location", "organizer")
    list_filter = ("date",)


@admin.register(EventPayment)
class EventPaymentAdmin(admin.ModelAdmin):
    list_display = ("user", "event", "amount", "status", "payment_id", "created_at")
    search_fields = ("payment_id", "user__username", "event__title")
    list_filter = ("status", "created_at")


@admin.register(FestivalCategory)
class FestivalCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "icon", "description")
    search_fields = ("name",)


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("user", "event", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "event__title")
