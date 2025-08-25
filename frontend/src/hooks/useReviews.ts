/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState, useEffect, useCallback } from "react";
import { createSpotReview } from "../services/parkingServices";

export const useReviews = (spotId: number) => {
  const [reviews, setReviews] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchReviews = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`/api/parking/spots/${spotId}/reviews/`);
      const data = await res.json();
      setReviews(data.results || []);
    } finally {
      setLoading(false);
    }
  }, [spotId]);

  const handleAddReview = async (rating: number, comment?: string) => {
    await createSpotReview({ spot: spotId, rating, comment });
    fetchReviews();
  };

  useEffect(() => {
    fetchReviews();
  }, [fetchReviews]);

  return { reviews, loading, handleAddReview };
};
