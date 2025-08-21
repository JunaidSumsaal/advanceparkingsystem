/* eslint-disable @typescript-eslint/no-explicit-any */
import { useEffect, useState } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import {
  Box,
  Card,
  CardBody,
  CardHeader,
  Text,
  Spinner,
  Center,
  Button,
  HStack,
  useToast,
} from "@chakra-ui/react";
import { useDashboard } from "../../../hooks/useDashboard";

const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"];

const Overview = () => {
  const toast = useToast();
  const { provider, fetchProvider, spotReports, fetchSpotReports, loading } =
    useDashboard();

  // Monthly bookings
  const [monthlyBookings, setMonthlyBookings] = useState<any[]>([]);
  const [bookingsPage, setBookingsPage] = useState(1);
  const [bookingsTotalPages, setBookingsTotalPages] = useState(1);
  const bookingsPerPage = 7; // Show one week per page
  const [paginatedBookings, setPaginatedBookings] = useState<any[]>([]);

  // Spot evaluation reports
  const [reportsPage, setReportsPage] = useState(1);
  const [reportsTotalPages, setReportsTotalPages] = useState(1);
  const reportsPerPage = 5;
  const [paginatedReports, setPaginatedReports] = useState<any[]>([]);

  // Fetch provider metrics and spot reports
  useEffect(() => {
    const fetchData = async () => {
      try {
        await fetchProvider();
        await fetchSpotReports();

        // Null-safe daily bookings
        const dailyBookings = provider?.dailyBookings ?? [];
        const monthlyData = dailyBookings.map((b: any) => ({
          month: new Date(b?.day ?? Date.now()).toLocaleDateString("default", {
            month: "short",
            day: "numeric",
          }),
          bookings: b?.count ?? 0,
        }));
        setMonthlyBookings(monthlyData);

        // Paginate bookings for table/list
        const totalBookingPages =
          Math.ceil(monthlyData.length / bookingsPerPage) || 1;
        setBookingsTotalPages(totalBookingPages);
        const bookingStart = (bookingsPage - 1) * bookingsPerPage;
        const bookingEnd = bookingStart + bookingsPerPage;
        setPaginatedBookings(monthlyData.slice(bookingStart, bookingEnd));

        // Paginate reports
        const totalReportPages =
          Math.ceil((spotReports?.length ?? 0) / reportsPerPage) || 1;
        setReportsTotalPages(totalReportPages);
        const reportStart = (reportsPage - 1) * reportsPerPage;
        const reportEnd = reportStart + reportsPerPage;
        setPaginatedReports((spotReports ?? []).slice(reportStart, reportEnd));
      } catch (err: any) {
        toast({
          title: "Error loading dashboard",
          description: err?.response?.data?.message || "Something went wrong.",
          status: "error",
          duration: 5000,
          isClosable: true,
          position: "top",
        });
      }
    };
    fetchData();
  }, [
    fetchProvider,
    fetchSpotReports,
    provider?.dailyBookings,
    spotReports,
    bookingsPage,
    reportsPage,
    toast,
  ]);

  // Pagination handlers
  const handleBookingsPrev = () =>
    setBookingsPage((prev) => Math.max(prev - 1, 1));
  const handleBookingsNext = () =>
    setBookingsPage((prev) => Math.min(prev + 1, bookingsTotalPages));
  const handleReportsPrev = () =>
    setReportsPage((prev) => Math.max(prev - 1, 1));
  const handleReportsNext = () =>
    setReportsPage((prev) => Math.min(prev + 1, reportsTotalPages));

  if (loading || !provider) {
    return (
      <Center minH="400px">
        <Spinner size="xl" color="primary.400" />
      </Center>
    );
  }

  // Metrics with null-safeguards
  const totalBookings = provider?.totalBookings ?? 0;
  const totalSpots = provider?.spotsCount ?? 0;
  const availableSpots = totalSpots - (totalBookings || 0);
  const managedFacilities = provider?.facilitiesCount ?? 0;

  return (
    <Box className="flex-1 space-y-8 p-8 pt-6">
      {/* Metrics */}
      <Box className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          title="Total Bookings"
          amount={totalBookings}
          progress={70}
        />
        <MetricCard
          title="Available Spots"
          amount={availableSpots}
          progress={totalSpots ? (availableSpots / totalSpots) * 100 : 0}
        />
        <MetricCard
          title="Occupied Spots"
          amount={totalSpots - availableSpots}
          progress={
            totalSpots ? ((totalSpots - availableSpots) / totalSpots) * 100 : 0
          }
        />
        <MetricCard
          title="Managed Facilities"
          amount={managedFacilities}
          progress={80}
        />
      </Box>

      {/* Charts */}
      <Box className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        {/* Monthly Bookings */}
        <Card className="col-span-4">
          <CardHeader>
            <Text>Monthly Booking Trends</Text>
          </CardHeader>
          <CardBody>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={monthlyBookings}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip
                  content={({ active, payload, label }) => {
                    if (active && payload && payload.length) {
                      const index = monthlyBookings.findIndex(
                        (m) => m.month === label
                      );
                      const cumulative = monthlyBookings
                        .slice(0, index + 1)
                        .reduce((sum, m) => sum + (m.bookings ?? 0), 0);
                      return (
                        <Box
                          p={2}
                          bg="white"
                          border="1px solid #ddd"
                          borderRadius="md"
                          boxShadow="md"
                        >
                          <Text fontWeight="bold">{label}</Text>
                          <Text>Bookings: {payload[0].value}</Text>
                          <Text>Cumulative: {cumulative}</Text>
                        </Box>
                      );
                    }
                    return null;
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="bookings"
                  stroke="#0088FE"
                  fill="#0088FE"
                  fillOpacity={0.2}
                  isAnimationActive
                  animationDuration={800}
                />
              </AreaChart>
            </ResponsiveContainer>

            {/* Paginated Bookings Table */}
            <Box mt={4} className="space-y-2">
              {paginatedBookings.map((b, idx) => (
                <Box
                  key={idx}
                  className="flex justify-between border-b py-1 px-2 rounded hover:bg-gray-50 transition"
                >
                  <Text>{b.month}</Text>
                  <Text>{b.bookings}</Text>
                </Box>
              ))}

              {/* Prev/Next Buttons */}
              <Center mt={2}>
                <HStack spacing={4}>
                  <Button
                    size="sm"
                    onClick={handleBookingsPrev}
                    isDisabled={bookingsPage === 1}
                  >
                    Prev
                  </Button>
                  <Text>
                    {bookingsPage} / {bookingsTotalPages}
                  </Text>
                  <Button
                    size="sm"
                    onClick={handleBookingsNext}
                    isDisabled={bookingsPage === bookingsTotalPages}
                  >
                    Next
                  </Button>
                </HStack>
              </Center>
            </Box>
          </CardBody>
        </Card>

        {/* Spot Availability */}
        <Card className="col-span-3">
          <CardHeader>
            <Text>Spot Availability</Text>
          </CardHeader>
          <CardBody>
            <ResponsiveContainer width="100%" height={380}>
              <PieChart>
                <Pie
                  data={[
                    { name: "Available", value: availableSpots },
                    { name: "Occupied", value: totalSpots - availableSpots },
                  ]}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  dataKey="value"
                  label={({ name, percent }) =>
                    `${name} ${((percent ?? 0) * 100).toFixed(0)}%`
                  }
                >
                  {Array.from({ length: 2 }).map((_, idx) => (
                    <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardBody>
        </Card>
      </Box>

      {/* Spot Evaluation Reports */}
      <Box className="grid gap-4">
        <Card>
          <CardHeader>
            <Text>Spot Evaluation Reports</Text>
          </CardHeader>
          <CardBody className="space-y-4">
            {(paginatedReports ?? []).map((report, idx) => (
              <Box key={idx} className="flex justify-between items-center">
                <Text>{report?.spot ?? "Unknown Spot"}</Text>
                <Text>Precision: {report?.precision?.toFixed(2) ?? 0}</Text>
                <Text>Recall: {report?.recall?.toFixed(2) ?? 0}</Text>
                <Text>F1: {report?.f1?.toFixed(2) ?? 0}</Text>
              </Box>
            ))}

            {/* Prev/Next Buttons */}
            <Center mt={4}>
              <HStack spacing={4}>
                <Button
                  size="sm"
                  onClick={handleReportsPrev}
                  isDisabled={reportsPage === 1}
                >
                  Prev
                </Button>
                <Text>
                  {reportsPage} / {reportsTotalPages}
                </Text>
                <Button
                  size="sm"
                  onClick={handleReportsNext}
                  isDisabled={reportsPage === reportsTotalPages}
                >
                  Next
                </Button>
              </HStack>
            </Center>
          </CardBody>
        </Card>
      </Box>
    </Box>
  );
};

export default Overview;

const MetricCard = ({
  title,
  amount,
  progress,
}: {
  title: string;
  amount: number;
  progress: number;
}) => (
  <Card>
    <CardHeader>
      <Text className="text-sm font-medium">{title}</Text>
    </CardHeader>
    <CardBody>
      <Box className="text-2xl font-bold">{amount}</Box>
      <Box className="mt-3 h-1 bg-gray-200 rounded">
        <Box
          className="h-1 bg-primary-400"
          style={{ width: `${progress ?? 0}%` }}
        />
      </Box>
    </CardBody>
  </Card>
);
