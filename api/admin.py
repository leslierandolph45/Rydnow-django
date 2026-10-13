from django.contrib import admin
from .models import Rider, Booking, Transaction, Withdrawal


# Register your models here.


@admin.register(Rider)
class RiderAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'status', 'total_rides', 'total_earnings', 'created_at')
    list_filter = ('status', 'vehicle_type', 'created_at')
    search_fields = ('name', 'phone', 'email', 'vehicle_plate')
    list_per_page = 25




@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('type', 'pickup', 'destination', 'status', 'customer_name', 'rider_name', 'fare', 'created_at')
    list_filter = ('type', 'status', 'created_at')
    search_fields = ('pickup', 'destination', 'customer_name', 'customer_phone', 'rider_name')
    list_per_page = 25
    readonly_fields = ('created_at', 'updated_at')




@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'booking', 'amount', 'status', 'payment_method', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('transaction_id', 'booking__customer_name')
    list_per_page = 25




@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ('rider', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('rider__name', 'bank_name', 'account_number')
    list_per_page = 25
