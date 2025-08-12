from rest_framework import serializers
from .models import ParkingFacility, ParkingSpot, Booking, SpotReview, SpotAvailabilityLog

class ParkingSpotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingSpot
        fields = '__all__'

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
    class Meta:
        model = ParkingFacility
        fields = ['id', 'name', 'latitude', 'longitude', 'address']

    def create(self, validated_data):
        request = self.context['request']
        return ParkingFacility.objects.create(
            provider=request.user,
            **validated_data
        )