from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import math


from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny  # ✅ Added AllowAny
from .models import Rider, Booking, Transaction, Withdrawal
from .serializers import (
    RiderSerializer, BookingSerializer,
    TransactionSerializer, WithdrawalSerializer
)




class RiderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Rider.objects.all()
    serializer_class = RiderSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]




class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all().order_by('-created_at')
    serializer_class = BookingSerializer
    permission_classes = [AllowAny]  # ✅ Changed from IsAuthenticatedOrReadOnly — public can create bookings


    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        booking = self.get_object()
        booking.status = 'accepted'
        if 'rider' in request.data:
            booking.rider_id = request.data['rider']
        booking.save()
        return Response({'status': 'booking accepted'})


    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        booking = self.get_object()
        booking.status = request.data.get('status', booking.status)
        booking.save()
        return Response({'status': f'booking status set to {booking.status}'})




class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Transaction.objects.all().order_by('-created_at')
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]




class WithdrawalViewSet(viewsets.ModelViewSet):
    queryset = Withdrawal.objects.all().order_by('-created_at')
    serializer_class = WithdrawalSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]




# ─────────────────────────────────────────────
# 🤖 AUTO-ASSIGNMENT SYSTEM — NEW CODE BELOW
# ─────────────────────────────────────────────




def calculate_distance(lat1, lng1, lat2, lng2):
    """Haversine formula — calculate distance between two points in km"""
    R = 6371  # Earth radius in km
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = math.sin(d_lat / 2)**2 + math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * math.sin(d_lng / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c




def find_best_rider(booking):
    """
    🎯 Find the BEST rider for this booking:
    1. Same service type ✅
    2. Online ✅
    3. Closest one wins 📍
    """
    # Map booking type → rider service type
    type_mapping = {
        'okada': 'okada',
        'rider': 'dispatch',
        'parcel': 'dispatch',
        'eco': 'eco',
        'waste-bin': 'waste',
    }


    rider_service = type_mapping.get(booking.type, 'okada')


    # Get ALL online riders of the correct type
    candidates = Rider.objects.filter(
        status='online',
        service_type=rider_service
    ).exclude(
        current_lat__isnull=True,
        current_lng__isnull=True
    )


    if not candidates.exists():
        print(f"⏳ No online riders found for {rider_service}")
        return None


    # Find the CLOSEST rider to pickup location
    best_rider = None
    closest_distance = float('inf')


    pickup_lat = getattr(booking, 'pickup_lat', None)
    pickup_lng = getattr(booking, 'pickup_lng', None)


    if pickup_lat and pickup_lng:
        for rider in candidates:
            dist = calculate_distance(
                pickup_lat, pickup_lng,
                rider.current_lat, rider.current_lng
            )
            if dist < closest_distance:
                closest_distance = dist
                best_rider = rider
    else:
        # No coordinates yet — pick highest rated rider of the right type
        best_rider = candidates.order_by('-rating').first()
        closest_distance = 0


    if best_rider:
        print(f"✅ Best rider: {best_rider.name} — {closest_distance:.2f}km away")


    return best_rider




def auto_assign_booking(booking):
    """Try to auto-assign a booking. Returns True if successful."""
    if booking.status not in ['searching_rider', 'pending']:
        return False  # Already assigned


    best_rider = find_best_rider(booking)


    if best_rider:
        booking.rider = best_rider
        booking.status = 'auto_assigned'
        booking.assignment_method = 'auto'
        booking.rider_name = best_rider.name
        booking.rider_phone = best_rider.phone
        booking.save()
        print(f"🤖 AUTO-ASSIGNED: Booking → {best_rider.name}")
        return True


    print(f"⏳ No rider available — waiting for manual acceptance")
    return False




@csrf_exempt
@require_POST
def new_booking_notification(request):
    try:
        data = json.loads(request.body)
        booking_id = data.get('booking_id')
        print(f"🔔 New booking notification! ID: {booking_id}")


        # Try to find the booking and auto-assign
        try:
            booking = Booking.objects.get(id=booking_id)
            assigned = auto_assign_booking(booking)


            if assigned:
                return JsonResponse({
                    "status": "success",
                    "message": "Booking created and rider auto-assigned",
                    "assignment_method": "auto",
                    "rider_name": booking.rider.name if booking.rider else None
                })
            else:
                return JsonResponse({
                    "status": "pending",
                    "message": "Booking created — searching for rider",
                    "assignment_method": "manual"
                })
        except Booking.DoesNotExist:
            # Booking not found yet — still return success for frontend
            return JsonResponse({
                "status": "success",
                "message": "Notification received"
            })


    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)




@csrf_exempt
@require_POST
def rider_accept_booking(request):
    """Fallback: Rider manually accepts a booking if auto-assign missed it"""
    try:
        data = json.loads(request.body)
        booking_id = data.get('booking_id')
        rider_id = data.get('rider_id')


        try:
            booking = Booking.objects.get(id=booking_id)
            rider = Rider.objects.get(id=rider_id)
        except Booking.DoesNotExist:
            return JsonResponse({"error": "Booking not found"}, status=404)
        except Rider.DoesNotExist:
            return JsonResponse({"error": "Rider not found"}, status=404)


        # Only allow if still searching OR already assigned to this rider
        if booking.status not in ['searching_rider', 'pending', 'auto_assigned']:
            return JsonResponse({"error": "Booking no longer available"}, status=400)


        # Prevent double-booking
        if booking.rider and booking.rider.id != rider.id:
            return JsonResponse({"error": "Booking already assigned to another rider"}, status=400)


        booking.rider = rider
        booking.status = 'rider_accepted'
        booking.assignment_method = 'manual'
        booking.save()


        print(f"✋ MANUAL ACCEPT: Booking {booking_id} → Rider {rider.name}")


        return JsonResponse({
            "status": "success",
            "message": "Booking accepted",
            "rider_name": rider.name
        })


    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RiderViewSet, BookingViewSet,
    TransactionViewSet, WithdrawalViewSet,
    new_booking_notification, rider_accept_booking,
    create_admin
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
    
    # ✅ Create admin user (visit ONCE then remove this line!)
    path('create-admin/', create_admin, name='create-admin'),
    
    # ✅ Notifications + Auto-Assignment
    path('notifications/new-booking/', new_booking_notification, name='new_booking_notification'),
    
    # ✅ Rider Manual Acceptance
    path('bookings/rider-accept/', rider_accept_booking, name='rider_accept_booking'),
]


# Auto-create superuser on startup
from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def create_default_admin(sender, **kwargs):
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='a****@***********',
            password='Admin123!'
        )
