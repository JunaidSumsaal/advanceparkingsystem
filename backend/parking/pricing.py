from .models import SpotPriceLog
from django.utils import timezone
from .models import ParkingSpot
from accounts.utils import log_action

def calculate_dynamic_price(spot: ParkingSpot) -> float:
    now = timezone.now()
    weekday = now.weekday()
    hour = now.hour

    price = float(spot.base_price)

    total = spot.facility.spots.count()
    booked = spot.facility.spots.filter(is_available=False).count()
    occupancy = booked / total if total else 0

    if occupancy >= 0.8:
        price *= 1.3
    elif occupancy >= 0.5:
        price *= 1.15
    else:
        price *= 0.9

    if hour in range(7, 10) or hour in range(16, 20):
        price *= 1.2

    if weekday >= 5:
        price *= 0.95

    return round(price, 2)


def update_dynamic_prices(user=None):
    updated = 0
    for spot in ParkingSpot.objects.select_related("facility").all():
        new_price = calculate_dynamic_price(spot)
        if new_price != float(spot.price_per_hour):
            SpotPriceLog.objects.create(
                parking_spot=spot,
                old_price=spot.price_per_hour,
                new_price=new_price
            )
            spot.price_per_hour = new_price
            spot.save(update_fields=["price_per_hour"])
            updated += 1
            log_action(user, "dynamic_price_update", f"Spot {spot.id} new price={new_price}", None)
    return updated

