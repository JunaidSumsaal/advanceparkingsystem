from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum
from parking.models import Booking, ParkingSpot, ParkingFacility

# Function to get booking trends for the past 30 days
def get_booking_trends(provider=None):
    """
    Get daily booking trends for the last 30 days.
    If a provider is passed, it will filter the bookings for that provider's facilities.
    """
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)

    bookings = Booking.objects.filter(start_time__date__gte=thirty_days_ago)

    if provider:
        facilities = ParkingFacility.objects.filter(provider=provider)
        spots = ParkingSpot.objects.filter(facility__in=facilities)
        bookings = bookings.filter(parking_spot__in=spots)

    # Group bookings by date
    booking_trends = bookings.values('start_time__date')\
        .annotate(bookings_count=Sum('total_price'))\
        .order_by('start_time__date')

    return booking_trends

# Function to get facility metrics such as occupancy rate and revenue
def get_facility_metrics(provider=None):
    """
    Get metrics for parking facilities managed by a provider.
    This will include the total number of spots, total revenue, and occupancy rate.
    """
    if provider:
        facilities = ParkingFacility.objects.filter(provider=provider)
    else:
        facilities = ParkingFacility.objects.all()

    facility_metrics = []
    
    for facility in facilities:
        total_spots = facility.spots.count()
        occupied_spots = facility.spots.filter(is_available=False).count()
        total_revenue = facility.spots.aggregate(revenue=Sum('price_per_hour'))['revenue'] or 0
        occupancy_rate = (occupied_spots / total_spots) * 100 if total_spots else 0

        facility_metrics.append({
            'facility_name': facility.name,
            'total_spots': total_spots,
            'occupied_spots': occupied_spots,
            'total_revenue': total_revenue,
            'occupancy_rate': occupancy_rate,
        })
    
    return facility_metrics
