/* eslint-disable @typescript-eslint/no-explicit-any */
import type { Paginated } from "../types/context/notification";

export function normalize<T>(data: any): Paginated<T> {
  if (Array.isArray(data)) {
    return {
      results: data,
      count: data.length,
      next: null,
      previous: null,
    };
  }
  // DRF pagination format
  return {
    results: data.results ?? [],
    count: data.count ?? 0,
    next: data.next ?? null,
    previous: data.previous ?? null,
  };
}