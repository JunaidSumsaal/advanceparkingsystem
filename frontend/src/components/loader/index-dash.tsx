import React, { useState, useEffect } from "react";
import LoaderDash from "./loaders-dashboard";

export function LoadingDash({ children }: { children: React.ReactNode }) {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setTimeout(() => {
      setLoading(false);
    }, 3000);
  }, []);
  if (!loading) {
    return children;
  } else {
    return <LoaderDash />;
  }
}
