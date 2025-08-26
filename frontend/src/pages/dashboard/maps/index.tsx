import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  useMapEvents,
} from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { useEffect, useState } from "react";
import { useUserRole } from "../../../hooks/useUserRole";
import {
  getNearbySpots,
  createBooking,
  createSpot,
} from "../../../services/parkingServices";
import {
  Box,
  Text,
  Button,
  useToast,
  Select,
  HStack,
  VStack,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
  Input,
  FormControl,
  FormLabel,
  useDisclosure,
} from "@chakra-ui/react";
import L from "leaflet";
import Dash from "../../../components/loader/dashboard";

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

interface Spot {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  is_available: boolean;
  type?: "public" | "private";
  price_per_hour?: number;
}

const Maps = () => {
  const { role, loading } = useUserRole();
  const [spots, setSpots] = useState<Spot[]>([]);
  const [position, setPosition] = useState<[number, number] | null>(null);
  const [filter, setFilter] = useState<string>("all");
  const [newSpotCoords, setNewSpotCoords] = useState<[number, number] | null>(
    null
  );
  const toast = useToast();

  const { isOpen, onOpen, onClose } = useDisclosure();
  const [formData, setFormData] = useState({
    name: "",
    type: "public",
    price: "",
  });

  // Get user geolocation
  useEffect(() => {
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        (pos) => setPosition([pos.coords.latitude, pos.coords.longitude]),
        () => setPosition([51.509865, -0.118092]) // fallback London
      );
    } else {
      setPosition([51.509865, -0.118092]); // fallback London
    }
  }, []);

  // Fetch nearby spots
  useEffect(() => {
    const fetchSpots = async () => {
      if (position) {
        try {
          const data = await getNearbySpots({
            lat: position[0],
            lng: position[1],
          });
          const fetched = data.results || data;
          setSpots(fetched);
          if (!fetched || fetched.length === 0) {
            toast({
              title: "No available spots",
              description: "There are no parking spots near your location.",
              status: "info",
              duration: 4000,
              isClosable: true,
              position: "top",
            });
          }
        } catch {
          toast({
            title: "Error",
            description: "Could not fetch nearby spots.",
            status: "error",
            duration: 4000,
            isClosable: true,
            position: "top",
          });
        }
      }
    };
    fetchSpots();
  }, [position, toast]);

  // Booking handler
  const handleBookSpot = async (spotId: number) => {
    try {
      await createBooking(spotId);
      toast({
        title: "Booking confirmed 🎉",
        description: "Your parking spot has been reserved.",
        status: "success",
        duration: 4000,
        isClosable: true,
        position: "top",
      });
      setSpots((prev) =>
        prev.map((s) => (s.id === spotId ? { ...s, is_available: false } : s))
      );
    } catch {
      toast({
        title: "Booking failed",
        description: "Something went wrong. Try again.",
        status: "error",
        duration: 4000,
        isClosable: true,
        position: "top",
      });
    }
  };

  // Add spot handler
  const handleAddSpot = async () => {
    if (!newSpotCoords) return;
    try {
      await createSpot({
        name: formData.name,
        type: formData.type,
        price_per_hour: Number(formData.price),
        latitude: newSpotCoords[0],
        longitude: newSpotCoords[1],
      });
      toast({
        title: "Facility added ✅",
        description: "Your parking spot has been added successfully.",
        status: "success",
        duration: 4000,
        isClosable: true,
        position: "top",
      });
      onClose();
    } catch {
      toast({
        title: "Failed to add spot",
        description: "Please try again.",
        status: "error",
        duration: 4000,
        isClosable: true,
        position: "top",
      });
    }
  };

  // Map click handler for providers
  const MapClickHandler = () => {
    useMapEvents({
      click(e) {
        if (role === "provider") {
          setNewSpotCoords([e.latlng.lat, e.latlng.lng]);
          onOpen();
        }
      },
    });
    return null;
  };

  // Filter spots
  const filteredSpots = spots.filter((s) => {
    if (filter === "all") return true;
    if (filter === "available") return s.is_available;
    if (filter === "occupied") return !s.is_available;
    if (filter === "public") return s.type === "public";
    if (filter === "private") return s.type === "private";
    return true;
  });

  const isLoading = loading || !position;
  if (isLoading) return <Dash />;

  return (
    <VStack w="full" h="100vh" spacing={0} align="stretch">
      {/* Filter bar */}
      <HStack p={2} bg="white" shadow="sm" zIndex={1}>
        <Text fontWeight="bold">Filter:</Text>
        <Select
          maxW="200px"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        >
          <option value="all">All spots</option>
          <option value="available">Available</option>
          <option value="occupied">Occupied</option>
          <option value="public">Public</option>
          <option value="private">Private</option>
        </Select>
      </HStack>

      {/* Map */}
      <Box flex="1" position="relative" zIndex={1}>
        <MapContainer
          key={position?.toString()}
          center={position as [number, number]}
          zoom={14}
          style={{ height: "100%", width: "100%" }}
        >
          <TileLayer
            attribution="&copy; OpenStreetMap contributors"
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {role === "provider" && <MapClickHandler />}

          {filteredSpots.map((spot) => (
            <Marker key={spot.id} position={[spot.latitude, spot.longitude]}>
              <Popup>
                <strong>{spot.name}</strong>
                <br />
                {spot.is_available ? "✅ Available" : "❌ Occupied"}
                <br />
                {spot.type && <Text fontSize="xs">Type: {spot.type}</Text>}
                {spot.price_per_hour && (
                  <Text fontSize="xs">Price: {spot.price_per_hour} KES/hr</Text>
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
                  <Text mt={2} fontSize="sm">
                    Manage spot options…
                  </Text>
                )}
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </Box>

      {/* Modal for adding facility */}
      <Modal isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Add Parking Spot</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <FormControl mb={3}>
              <FormLabel>Name</FormLabel>
              <Input
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
              />
            </FormControl>
            <FormControl mb={3}>
              <FormLabel>Type</FormLabel>
              <Select
                value={formData.type}
                onChange={(e) =>
                  setFormData({ ...formData, type: e.target.value })
                }
              >
                <option value="public">Public</option>
                <option value="private">Private</option>
              </Select>
            </FormControl>
            <FormControl>
              <FormLabel>Price per hour</FormLabel>
              <Input
                type="number"
                value={formData.price}
                onChange={(e) =>
                  setFormData({ ...formData, price: e.target.value })
                }
              />
            </FormControl>
          </ModalBody>
          <ModalFooter>
            <Button colorScheme="blue" onClick={handleAddSpot}>
              Add Spot
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </VStack>
  );
};

export default Maps;
