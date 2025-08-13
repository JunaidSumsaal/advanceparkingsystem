import React, { useState, useEffect } from "react";
import Loader from "./loaders";

export function Loading({ children }: { children: React.ReactNode }) {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setTimeout(() => {
      setLoading(false);
    }, 3000);
  }, []);
  if (!loading) {
    return children;
  } else {
    return <Loader />;
  }
}
