import { useEffect, useState } from "react";
import {
  Box,
  Card,
  CardBody,
  CardHeader,
  Text,
  Center,
  HStack,
  Button,
} from "@chakra-ui/react";
import { useDashboard } from "../../../hooks/useDashboard";
import Dash from "../../../components/loader/dashboard";

const AttendantDashboard = () => {
  const { attendant, fetchAttendant, loading } = useDashboard();
  const [page, setPage] = useState(1);

  useEffect(() => {
    fetchAttendant();
  }, [fetchAttendant]);

  if (loading || !attendant) {
    return <Dash />;
  }

  const recentBookings = attendant.recent_bookings;

  return (
    <Box className="p-8 space-y-6">
      {/* Metrics */}
      <Box className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          title="Managed Facilities"
          amount={attendant.managed_facilities_count}
        />
        <MetricCard title="Active Spots" amount={attendant.active_spots} />
        <MetricCard title="Occupied Spots" amount={attendant.occupied_spots} />
      </Box>

      {/* Facility Metrics */}
      <Card>
        <CardHeader>
          <Text>Facility Metrics</Text>
        </CardHeader>
        <CardBody>
          <Box className="space-y-4">
            {attendant.facility_metrics.map((facility, idx) => (
              <Box key={idx} className="flex justify-between items-center">
                <Text>{facility.facility_name}</Text>
                <Text>{`Total Spot: ${facility.total_spots}`}</Text>
                <Text>{`Occupied Spot: ${facility.occupied_spots}`}</Text>
                <Text>{`Occupancy Rate: ${facility.occupancy_rate.toFixed(
                  2
                )}%`}</Text>
                <Text>{`Revenue: $${facility.revenue.toFixed(2)}`}</Text>
              </Box>
            ))}
          </Box>
        </CardBody>
      </Card>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <Text>Recent Activity</Text>
        </CardHeader>
        <CardBody>
          <Box className="space-y-4">
            {recentBookings?.map((activity) => (
              <Box
                key={activity.id}
                className="flex justify-between items-center"
              >
                <Text>{activity.user__email}</Text> {/* Display user email */}
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
                  isDisabled={page === attendant.recent_bookings.length}
                >
                  Next
                </Button>
              </HStack>
            </Center>
          </Box>
        </CardBody>
      </Card>
    </Box>
  );
};

export default AttendantDashboard;

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
