/* eslint-disable @typescript-eslint/no-explicit-any */
import { useEffect } from "react";
import {
  Box,
  Card,
  CardBody,
  CardHeader,
  Text,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  VStack,
  HStack,
  Avatar,
  Divider,
} from "@chakra-ui/react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";
import dayjs from "dayjs";
import { useDashboard } from "../../../hooks/useDashboard";
import Dash from "../../../components/loader/dashboard";

const COLORS = ["#4f46e5", "#10b981", "#f59e0b", "#ef4444"];

const AdminOverview = () => {
  const { admin, fetchAdmin, loading } = useDashboard();

  useEffect(() => {
    fetchAdmin();
  }, [fetchAdmin]);

  if (loading || !admin) {
    return <Dash />;
  }

  // Merge recent bookings + users into timeline
  const timeline = [
    ...admin.recent_activity.bookings.map((b) => ({
      type: "booking",
      id: b.id,
      user: b.user__email,
      facility: b.parking_spot__facility__name,
      time: b.start_time,
    })),
    ...admin.recent_activity.users.map((u) => ({
      type: "user",
      id: u.id,
      email: u.email,
      role: u.role,
      time: u.date_joined,
    })),
  ].sort((a, b) => new Date(b.time).getTime() - new Date(a.time).getTime());

  return (
    <Box className="p-4 md:p-8 space-y-8">
      {/* Top metrics */}
      <Box className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <MetricCard title="Total Users" amount={admin.total_users} />
        <MetricCard title="Total Facilities" amount={admin.total_facilities} />
        <MetricCard title="Total Spots" amount={admin.total_spots} />
        <MetricCard title="Total Bookings" amount={admin.total_bookings} />
      </Box>

      {/* AI Stats */}
      <Box className="grid gap-4 md:grid-cols-2">
        <MetricCard
          title="Prediction Logs"
          amount={admin.ai_stats.prediction_logs}
        />
        <MetricCard
          title="Availability Logs"
          amount={admin.ai_stats.availability_logs}
        />
      </Box>

      {/* Charts in responsive grid */}
      <Box className="grid gap-6 lg:grid-cols-2">
        {/* User breakdown */}
        <Card>
          <CardHeader>
            <Text fontWeight="semibold">User Breakdown</Text>
          </CardHeader>
          <CardBody>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={admin.user_breakdown}
                  dataKey="count"
                  nameKey="role"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label
                >
                  {admin.user_breakdown.map((_entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </CardBody>
        </Card>

        {/* Booking trends */}
        <Card>
          <CardHeader>
            <Text fontWeight="semibold">Booking Trends</Text>
          </CardHeader>
          <CardBody>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart
                data={admin.booking_trends.map((b) => ({
                  date: b.start_time__date,
                  count: b.bookings_count ?? 0,
                }))}
              >
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="count" stroke="#4f46e5" />
              </LineChart>
            </ResponsiveContainer>
          </CardBody>
        </Card>
      </Box>

      {/* Revenue by facility */}
      <Card>
        <CardHeader>
          <Text fontWeight="semibold">Revenue by Facility</Text>
        </CardHeader>
        <CardBody>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart
              data={admin.revenue.by_facility.map((f) => ({
                facility: f.parking_spot__facility__name,
                total: f.total ?? 0,
              }))}
            >
              <XAxis dataKey="facility" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="total" fill="#10b981" />
            </BarChart>
          </ResponsiveContainer>
        </CardBody>
      </Card>

      {/* Timeline */}
      <Card>
        <CardHeader>
          <Text fontWeight="semibold">Recent Activity Timeline</Text>
        </CardHeader>
        <CardBody>
          <VStack align="stretch" spacing={4}>
            {timeline.map((item, idx) => (
              <Box key={idx}>
                <HStack align="start" spacing={3}>
                  <Avatar
                    size="sm"
                    name={item.type === "user" ? (item as any).email : (item as any).user}
                    bg={item.type === "user" ? "blue.500" : "green.500"}
                  />
                  <Box>
                    {item.type === "user" ? (
                      <Text>
                        <b>{(item as any).email}</b> signed up as{" "}
                        <span className="capitalize">{(item as any).role}</span>
                      </Text>
                    ) : (
                      <Text>
                        <b>{(item as any).user}</b> booked a spot at{" "}
                        <b>{(item as any).facility}</b>
                      </Text>
                    )}
                    <Text fontSize="sm" color="gray.500">
                      {dayjs(item.time).format("MMM D, YYYY HH:mm")}
                    </Text>
                  </Box>
                </HStack>
                {idx < timeline.length - 1 && <Divider my={2} />}
              </Box>
            ))}
          </VStack>
        </CardBody>
      </Card>

      {/* Facility metrics */}
      <Card>
        <CardHeader>
          <Text fontWeight="semibold">Facility Metrics</Text>
        </CardHeader>
        <CardBody overflowX="auto">
          <Table size="sm">
            <Thead>
              <Tr>
                <Th>Facility</Th>
                <Th>Total Spots</Th>
                <Th>Occupied Spots</Th>
                <Th>Occupancy Rate</Th>
                <Th>Total Revenue</Th>
              </Tr>
            </Thead>
            <Tbody>
              {admin.facility_metrics.map((f, idx) => (
                <Tr key={idx}>
                  <Td>{f.facility_name}</Td>
                  <Td>{f.total_spots}</Td>
                  <Td>{f.occupied_spots}</Td>
                  <Td>{(f.occupancy_rate * 100).toFixed(1)}%</Td>
                  <Td>${f.total_revenue}</Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </CardBody>
      </Card>
    </Box>
  );
};

export default AdminOverview;

const MetricCard = ({ title, amount }: { title: string; amount: number }) => (
  <Card>
    <CardHeader>
      <Text className="text-sm font-medium">{title}</Text>
    </CardHeader>
    <CardBody>
      <Box className="text-2xl font-bold">{amount}</Box>
    </CardBody>
  </Card>
);
