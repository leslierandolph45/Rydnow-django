from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RiderViewSet, BookingViewSet,
    TransactionViewSet, WithdrawalViewSet,
    new_booking_notification, rider_accept_booking
)


router = DefaultRouter()
router.register(r'riders', RiderViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'withdrawals', WithdrawalViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # ✅ Notifications + Auto-Assignment
    path('notifications/new-booking/', new_booking_notification, name='new_booking_notification'),
    
    # ✅ Rider Manual Acceptance
    path('bookings/rider-accept/', rider_accept_booking, name='rider_accept_booking'),
]
