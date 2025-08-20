from rest_framework import serializers
from .models import ArchiveReport, ParkingFacility, ParkingSpot, Booking, SpotPriceLog, SpotReview, SpotAvailabilityLog

class ParkingSpotSerializer(serializers.ModelSerializer):
    dynamic_price = serializers.SerializerMethodField()
    class Meta:
        model = ParkingSpot
        fields = '__all__'
        
    def get_dynamic_price(self, obj):
        return obj.dynamic_price_per_hour

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ('user', 'start_time', 'end_time', 'is_active')

class SpotReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpotReview
        fields = '__all__'

class SpotAvailabilityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpotAvailabilityLog
        fields = '__all__'
        
class SpotPredictionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    probability = serializers.FloatField()
    predicted_for_time = serializers.DateTimeField()

class ParkingFacilitySerializer(serializers.ModelSerializer):
    provider = serializers.ReadOnlyField(source='provider.username')

    class Meta:
        model = ParkingFacility
        fields = [
            'id', 'provider', 'name', 'capacity', 'latitude', 'longitude',
            'address', 'attendants', 'created_at', 'is_deleted'
        ]
        read_only_fields = ['id', 'provider', 'created_at', 'is_deleted']

    def validate_capacity(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Capacity cannot be negative.")
        return value

class SpotPriceLogSerializer(serializers.ModelSerializer):
    spot_name = serializers.CharField(source="parking_spot.name", read_only=True)

    class Meta:
        model = SpotPriceLog
        fields = ["id", "spot_name", "old_price", "new_price", "updated_at"]
        
class ArchiveReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArchiveReport
        fields = "__all__"