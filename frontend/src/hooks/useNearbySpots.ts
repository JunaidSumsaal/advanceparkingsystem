/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState, useEffect, useCallback, useRef } from "react";
import { getNearbySpots, createBooking } from "../services/parkingServices";
import { useToast } from "@chakra-ui/react";
import type { Spot } from "../types/context/parking";

export const useNearbySpots = () => {
  const [loading, setLoading] = useState<boolean>(true);
  const [spots, setSpots] = useState<Spot[]>([]);
  const [position, setPosition] = useState<[number, number] | null>(null);
  const [filter, setFilter] = useState<string>("all");
  const [radius, setRadius] = useState<number>(2); // km
  const [page, setPage] = useState<number>(0);
  const [hasMore, setHasMore] = useState<boolean>(true);
  const loaderRef = useRef<HTMLDivElement | null>(null);
  const toast = useToast();

  // 1. Get user geolocation and handle loading
  useEffect(() => {
    if (!("geolocation" in navigator)) {
      setPosition([-0.118092, 51.509865]); // fallback London
      setLoading(false);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setPosition([pos.coords.latitude, pos.coords.longitude]);
      },
      (err) => {
        console.error("Geolocation Error: ", err);
        setPosition([-0.118092, 51.509865]); // fallback London
        setLoading(false);
      }
    );
  }, []);

  // 2. Fetch spots logic as a useCallback to prevent re-creation
  const fetchSpots = useCallback(
    async (reset = false) => {
      setLoading(true);
      if (!position) return;

      try {
        const data = await getNearbySpots({
          lat: position[0],
          lng: position[1],
          radius,
          limit: 20,
          offset: reset ? 0 : page * 20,
        });

        const fetched = data.results || [];

        if (reset) {
          setSpots(fetched);
          setPage(1);
        } else {
          setSpots((prev) => [...prev, ...fetched]);
          setPage((prev) => prev + 1);
        }

        setHasMore(fetched.length > 0);

        if ((!fetched || fetched.length === 0) && reset) {
          toast({
            title: "No available spots",
            description: data.message || "Try widening your search radius.",
            status: "info",
            duration: 4000,
            isClosable: true,
            position: "top",
          });
        }
      } catch (err) {
        console.error("Error fetching spots", err);
        toast({
          title: "Error",
          description: "Could not fetch nearby spots.",
          status: "error",
          duration: 4000,
          isClosable: true,
          position: "top",
        });
      } finally {
        setLoading(false);
      }
    },
    [position, radius, page, toast]
  );

  // 3. Trigger initial fetch and refetch on position/radius change
  useEffect(() => {
    if (position) {
      fetchSpots(true);
    }
  }, [position, radius, fetchSpots]);

  // 4. Infinite scroll observer
  useEffect(() => {
    if (!loaderRef.current || !hasMore || loading) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          fetchSpots();
        }
      },
      { threshold: 1 }
    );

    observer.observe(loaderRef.current);
    
    return () => {
      // eslint-disable-next-line react-hooks/exhaustive-deps
      if (loaderRef.current) observer.unobserve(loaderRef.current);
    };
  }, [hasMore, loading, fetchSpots]);

  // 5. Booking handler
  const handleBookSpot = async (spotId: number) => {
    setLoading(true);
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
    } catch (error) {
      console.error("Booking error", error);
      toast({
        title: "Booking failed",
        description: "Something went wrong. Try again.",
        status: "error",
        duration: 4000,
        isClosable: true,
        position: "top",
      });
    } finally {
      setLoading(false);
    }
  };

  // 6. Apply filter
  const filteredSpots = spots.filter((s) => {
    if (filter === "all") return true;
    if (filter === "available") return s.is_available;
    if (filter === "occupied") return !s.is_available;
    if (s.type) {
      if (filter === "public") return s.type === "public";
      if (filter === "private") return s.type === "private";
    }
    return true;
  });

  return {
    spots: filteredSpots,
    loading,
    handleBookSpot,
    setRadius,
    setFilter,
    loaderRef,
  };
};