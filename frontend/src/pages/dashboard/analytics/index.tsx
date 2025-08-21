/* eslint-disable @typescript-eslint/no-explicit-any */
import { useEffect, useState } from "react";
import {
  Box,
  Card,
  CardBody,
  CardHeader,
  Text,
  Spinner,
  Center,
} from "@chakra-ui/react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { useDashboard } from "../../../hooks/useDashboard";
import type { ProviderDashboard } from "../../../types/context/dashboard";

const Analytics = () => {
  const [spotComparison, setSpotComparison] = useState<any[]>([]);
  const [monthlyBookings, setMonthlyBookings] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const { provider } = useDashboard();

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const data = provider as ProviderDashboard;

        const formattedSpotStats = (data.spot_stats ?? []).map((s: any) => ({
          name: s?.name ?? "Unknown Spot",
          totalSpots: 1, // Each spot counts as 1
          booked: s?.booked ?? 0,
        }));
        setSpotComparison(formattedSpotStats);

        const formattedMonthly = Object.entries(data.monthly_bookings ?? {}).map(
          ([month, count]: any) => ({
            name: month,
            bookings: count ?? 0,
          })
        );
        setMonthlyBookings(formattedMonthly);
      } catch (err) {
        console.error("Error fetching analytics:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [provider]);

  if (loading) {
    return (
      <Center minH="400px">
        <Spinner size="xl" color="primary.400" />
      </Center>
    );
  }

  const totalBookings = monthlyBookings.reduce(
    (acc, month) => acc + (month.bookings ?? 0),
    0
  );
  const averageMonthlyBookings =
    monthlyBookings.length > 0
      ? (totalBookings / monthlyBookings.length).toFixed(0)
      : "0";
  const mostBookedSpot =
    spotComparison.length > 0
      ? spotComparison.sort((a, b) => (b.booked ?? 0) - (a.booked ?? 0))[0]
      : null;

  return (
    <Box className="flex-1 space-y-8 p-8 pt-6">
      {/* Spot Bookings */}
      <Box className="grid gap-4 grid-cols-1">
        <Card>
          <CardHeader>
            <Text as="h1">Spot Availability vs Bookings</Text>
          </CardHeader>
          <CardBody>
            <Box className="h-[400px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={spotComparison}
                  margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="totalSpots" name="Total Spots" fill="#8884d8" />
                  <Bar dataKey="booked" name="Booked" fill="#82ca9d" />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </CardBody>
        </Card>
      </Box>

      {/* Monthly Bookings & YTD Summary */}
      <Box className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <Text as="h1">Monthly Booking Trends</Text>
          </CardHeader>
          <CardBody>
            <Box className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={monthlyBookings}
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip
                    formatter={(value: any) => [value, "Bookings"]}
                    labelFormatter={(label: any) => `Month: ${label}`}
                  />
                  <Bar dataKey="bookings" name="Bookings" fill="#82ca9d" />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <Text as="h1">Year-to-Date Summary</Text>
          </CardHeader>
          <CardBody>
            <Box className="space-y-6">
              <Box>
                <Text className="text-sm font-medium">Total Bookings</Text>
                <Text className="text-2xl font-bold">{totalBookings}</Text>
              </Box>
              <Box>
                <Text className="text-sm font-medium">Average Monthly Bookings</Text>
                <Text className="text-2xl font-bold">{averageMonthlyBookings}</Text>
              </Box>
              {mostBookedSpot && mostBookedSpot.name && (
                <Box>
                  <Text className="text-sm font-medium">Most Booked Spot</Text>
                  <Text className="text-2xl font-bold">
                    {mostBookedSpot.name} - {mostBookedSpot.booked ?? 0} bookings
                  </Text>
                </Box>
              )}
            </Box>
          </CardBody>
        </Card>
      </Box>
    </Box>
  );
};

export default Analytics;
