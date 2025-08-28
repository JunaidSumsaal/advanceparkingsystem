import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  useMapEvents,
} from "react-leaflet";
import "leaflet/dist/leaflet.css";
import Cookies from "js-cookie";
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
  Slider,
  SliderTrack,
  SliderFilledTrack,
  SliderThumb,
} from "@chakra-ui/react";
import L from "leaflet";
import Dash from "../../../components/loader/dashboard";
import { wsUrl } from "../../../services/constants";

// Fix Leaflet default icon
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
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
  id: number | string;
  name: string;
  latitude: number;
  longitude: number;
  is_available?: boolean;
  spot_type?: "public" | "private";
  price_per_hour?: number;
  source?: string;
}

const Maps = () => {
  const { role, loading } = useUserRole();
  const [spots, setSpots] = useState<Spot[]>([]);
  const [position, setPosition] = useState<[number, number] | null>(null);
  const [filter, setFilter] = useState<string>("all");
  const [radius, setRadius] = useState<number>(500);
  const [searchQuery, setSearchQuery] = useState<string>("");
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

  // custom blue marker for current user
  const userIcon = new L.Icon({
    iconUrl: "https://maps.gstatic.com/mapfiles/ms2/micons/blue-dot.png",
    iconSize: [32, 32],
    iconAnchor: [16, 32],
  });

  // Get user geolocation
  useEffect(() => {
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        (pos) => setPosition([pos.coords.latitude, pos.coords.longitude]),
        () => setPosition([51.509865, -0.118092]) // fallback London
      );
    } else {
      setPosition([51.509865, -0.118092]);
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
            radius,
            limit: 60,
            offset: 0,
          });

          const fetched = data.results || [];
          setSpots(fetched);

          if (!fetched || fetched.length === 0) {
            toast({
              title: "No available spots",
              description: `No parking spots within ${data.radius || radius}m`,
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
  }, [position, radius, toast]);

  // WebSocket subscription for live updates
  useEffect(() => {
    const token = Cookies.get("token");
    if (!token) return;
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const wsUrls = `${protocol}://${wsUrl}/ws/parking`;

    const ws = new WebSocket(wsUrls + `/?token=${token}`);

    ws.onmessage = (evt) => {
      try {
        const payload = JSON.parse(evt.data);
        setSpots((prev) => {
          const idx = prev.findIndex((s) => s.id === payload.id);
          if (idx >= 0) {
            const copy = [...prev];
            copy[idx] = { ...copy[idx], ...payload };
            return copy;
          }
          return [...prev, payload];
        });
      } catch (e) {
        console.warn("WS parse error", e);
      }
    };

    ws.onerror = () => console.warn("WebSocket error");
    ws.onclose = () => console.log("WebSocket closed");

    return () => ws.close();
  }, []);

  // Search handler
  const handleSearch = async () => {
    if (!searchQuery) return;
    try {
      const res = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(
          searchQuery
        )}`
      );
      const data = await res.json();
      if (data && data.length > 0) {
        const { lat, lon } = data[0];
        setPosition([parseFloat(lat), parseFloat(lon)]);
      } else {
        toast({
          title: "Not found",
          description: "Could not locate that place.",
          status: "warning",
          duration: 3000,
          isClosable: true,
          position: "top",
        });
      }
    } catch {
      toast({
        title: "Error",
        description: "Location search failed.",
        status: "error",
        duration: 3000,
        isClosable: true,
        position: "top",
      });
    }
  };

  // Booking handler
  const handleBookSpot = async (spotId: number | string) => {
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

  // Map click handler (provider add spot)
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

  // Filter logic
  const filteredSpots = spots.filter((s) => {
    if (filter === "all") return true;
    if (filter === "available") return s.is_available;
    if (filter === "occupied") return !s.is_available;
    if (filter === "public") return s.spot_type === "public";
    if (filter === "private") return s.spot_type === "private";
    return true;
  });

  const isLoading = loading || !position;
  if (isLoading) return <Dash />;

  return (
    <VStack w="full" h="100vh" spacing={0} align="stretch" pt={6}>
      {/* Top bar */}
      {role && (
        <HStack p={2} bg="white" shadow="sm" zIndex={1} spacing={3}>
          <Input
            placeholder="Search location..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            maxW="250px"
          />
          <Button size="sm" colorScheme="blue" onClick={handleSearch}>
            Search
          </Button>

          {/* 🎚️ Radius slider */}
          <HStack ml={4}>
            <Text fontSize="sm">Radius: {radius} km</Text>
            <Box w="200px">
              <Slider min={1} max={500} step={1} value={radius} onChange={setRadius}>
                <SliderTrack>
                  <SliderFilledTrack />
                </SliderTrack>
                <SliderThumb />
              </Slider>
            </Box>
          </HStack>

          {/* Filter dropdown */}
          <Select
            maxW="150px"
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
      )}

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
          {(role === "provider" || role === "admin") && <MapClickHandler />}

          {/* user marker */}
          {position && <Marker position={position} icon={userIcon}></Marker>}

          {filteredSpots.map((spot) => (
            <Marker
              key={spot.id}
              position={[
                parseFloat(String(spot.latitude)),
                parseFloat(String(spot.longitude)),
              ]}
            >
              <Popup>
                <strong>{spot.name}</strong>
                <br />
                {spot.is_available ? "✅ Available" : "❌ Occupied"}
                <br />
                {spot.spot_type && (
                  <Text fontSize="xs">Type: {spot.spot_type}</Text>
                )}
                {spot.price_per_hour && (
                  <Text fontSize="xs">Price: ${spot.price_per_hour}</Text>
                )}
                {/* Get Directions */}
                {role && (
                  <Button
                    as="a"
                    href={`https://www.google.com/maps/dir/?api=1&destination=${spot.latitude},${spot.longitude}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    mt={2}
                    size="sm"
                    bg="primary.400"
                    _hover={{
                      bg: "primary.600",
                    }}
                  >
                    Get Directions
                  </Button>
                )}
                {(role === "driver" || role === "admin") && spot.is_available && (
                  <Button
                    mt={2}
                    size="sm"
                    colorScheme="blue"
                    onClick={() => handleBookSpot(spot.id)}
                  >
                    Book Now
                  </Button>
                )}
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </Box>

      {/* Modal */}
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
