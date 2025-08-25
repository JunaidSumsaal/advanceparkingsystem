// src/components/MapsTab.tsx
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { useUserRole } from "../../../hooks/useUserRole";
import {
  Box,
  Text,
  Button,
  Select,
  HStack,
  VStack,
} from "@chakra-ui/react";
import L from "leaflet";
import Dash from "../../../components/loader/dashboard";
import { useNearbySpots } from "../../../hooks/useNearbySpots"; // Use the custom hook

// Fix Leaflet default icon
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
  iconUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
});

const Maps = () => {
  const { role, loading: roleLoading } = useUserRole();
  const {
    spots,
    loading: spotsLoading,
    handleBookSpot,
    setRadius,
    setFilter,
    loaderRef,
  } = useNearbySpots();

  // The hook now manages all state and logic
  const position = spots.length > 0
    ? [spots[0].latitude, spots[0].longitude]
    : [-0.118092, 51.509865];

  if (roleLoading || spotsLoading) {
    return <Dash />;
  }

  return (
    <VStack w="full" h="100vh" spacing={0} align="stretch">
      {/* Filter bar */}
      <HStack p={2} bg="white" shadow="sm" zIndex={2}>
        <Text fontWeight="bold">Filter:</Text>
        <Select maxW="160px" onChange={(e) => setFilter(e.target.value)}>
          <option value="all">All spots</option>
          <option value="available">Available</option>
          <option value="occupied">Occupied</option>
          <option value="public">Public</option>
          <option value="private">Private</option>
        </Select>

        <Text fontWeight="bold" ml={4}>
          Radius:
        </Text>
        <Select
          maxW="120px"
          defaultValue={2}
          onChange={(e) => setRadius(Number(e.target.value))}
        >
          <option value={1}>1 km</option>
          <option value={2}>2 km</option>
          <option value={5}>5 km</option>
          <option value={10}>10 km</option>
        </Select>
      </HStack>

      {/* Map */}
      <Box flex="1" position="relative" zIndex={1}>
        <MapContainer
          key={position.toString()}
          center={position as [number, number]}
          zoom={14}
          style={{ height: "100%", width: "100%", zIndex: 1 }}
        >
          <TileLayer
            attribution="&copy; OpenStreetMap contributors"
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {spots.map((spot) => (
            <Marker key={spot.id} position={[spot.latitude, spot.longitude]}>
              <Popup>
                <strong>{spot.name}</strong>
                <br />
                {spot.is_available ? "✅ Available" : "❌ Occupied"}
                <br />
                {spot.type && (
                  <Text fontSize="xs" color="gray.500">
                    Type: {spot.type}
                  </Text>
                )}
                {role === "driver" && spot.is_available && (
                  <Button
                    mt={2}
                    size="sm"
                    colorScheme="blue"
                    onClick={() => handleBookSpot(spot.id)}
                  >
                    Book Now
                  </Button>
                )}
                {role === "provider" && (
                  <Text mt={2} fontSize="sm" color="gray.500">
                    Manage spot options…
                  </Text>
                )}
              </Popup>
            </Marker>
          ))}
        </MapContainer>
        {/* Infinite scroll loader */}
        {spots.length > 0 && (
          <Box ref={loaderRef} p={3} textAlign="center" bg="whiteAlpha.800">
            <Text fontSize="sm" color="gray.600">
              Loading more spots...
            </Text>
          </Box>
        )}
      </Box>
    </VStack>
  );
};

export default Maps;