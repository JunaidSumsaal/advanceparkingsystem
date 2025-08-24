/* eslint-disable @typescript-eslint/no-explicit-any */
import { useEffect, useState } from "react";
import {
  Box,
  Card,
  CardBody,
  CardHeader,
  Text,
  Center,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  HStack,
  Button,
} from "@chakra-ui/react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip as RechartsTooltip,
} from "recharts";
import { useDashboard } from "../../../hooks/useDashboard";
import Dash from "../../../components/loader/dashboard";

const ProviderDashboard = () => {
  const { provider, fetchProvider, loading } = useDashboard();
  const [page, setPage] = useState(1);

  useEffect(() => {
    fetchProvider();
  }, [fetchProvider]);

  if (loading || !provider) {
    return <Dash />;
  }

  return (
    <Box className="p-4 md:p-8 space-y-8">
      {/* Top Metrics */}
      <Box className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          title="Total Facilities"
          amount={provider.facilities_count}
        />
        <MetricCard title="Total Spots" amount={provider.spots_count} />
        <MetricCard title="Total Bookings" amount={provider.total_bookings} />
        <MetricCard title="Avg. Price" amount={`$${provider.avg_price.toFixed(2)}`} />
      </Box>

      {/* Booking Trends */}
      {provider.booking_trends && (
        <Card>
          <CardHeader>
            <Text fontWeight="semibold">Booking Trends</Text>
          </CardHeader>
          <CardBody>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={provider.booking_trends}>
                <XAxis dataKey="day" />
                <YAxis />
                <RechartsTooltip />
                <Line type="monotone" dataKey="count" stroke="#4f46e5" />
              </LineChart>
            </ResponsiveContainer>
          </CardBody>
        </Card>
      )}

      {/* Facility Metrics */}
      {provider.facility_metrics && (
        <Card>
          <CardHeader>
            <Text fontWeight="semibold">Facility Performance</Text>
          </CardHeader>
          <CardBody>
            <Table size="sm">
              <Thead>
                <Tr>
                  <Th>Facility</Th>
                  <Th>Total Spots</Th>
                  <Th>Occupied</Th>
                  <Th>Revenue</Th>
                  <Th>Occupancy Rate</Th>
                </Tr>
              </Thead>
              <Tbody>
                {provider.facility_metrics.map((facility, idx) => (
                  <Tr key={idx}>
                    <Td>{facility.facility_name}</Td>
                    <Td>{facility.total_spots}</Td>
                    <Td>{facility.occupied_spots}</Td>
                    <Td>{facility.total_revenue}</Td>
                    <Td>{facility.occupancy_rate}%</Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
          </CardBody>
        </Card>
      )}

      {/* Occupied Spots */}
      <Card>
        <CardHeader>
          <Text fontWeight="semibold">Occupied Spots</Text>
        </CardHeader>
        <CardBody>
          <Text>{provider.occupied_spots}</Text>
        </CardBody>
      </Card>

      {/* Recent Activity */}
      {provider.recent_activity && (
        <Card>
          <CardHeader>
            <Text>Recent Activity</Text>
          </CardHeader>
          <CardBody>
            <Box className="space-y-4">
              {provider.recent_activity?.map((activity) => (
                <Box
                  key={activity.id}
                  className="flex justify-between items-center"
                >
                  <Text>{activity.user__email}</Text>
                  <Text>{activity.parking_spot__facility__name}</Text>
                  <Text>{new Date(activity.start_time).toLocaleString()}</Text>
                </Box>
              ))}

              {/* Pagination */}
              <Center mt={4}>
                <HStack spacing={4}>
                  <Button
                    size="sm"
                    onClick={() => setPage(page - 1)}
                    isDisabled={page === 1}
                  >
                    Prev
                  </Button>
                  <Text>{page}</Text>
                  <Button
                    size="sm"
                    onClick={() => setPage(page + 1)}
                    isDisabled={page === provider.recent_activity.length}
                  >
                    Next
                  </Button>
                </HStack>
              </Center>
            </Box>
          </CardBody>
        </Card>
      )}
    </Box>
  );
};

export default ProviderDashboard;

const MetricCard = ({ title, amount }: { title: string; amount: any }) => (
  <Card>
    <CardHeader>
      <Text className="text-sm font-medium">{title}</Text>
    </CardHeader>
    <CardBody>
      <Box className="text-2xl font-bold">{amount}</Box>
    </CardBody>
  </Card>
);
