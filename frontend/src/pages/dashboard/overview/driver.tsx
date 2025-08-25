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
import { CircleQuestionMark } from "lucide-react";

const DriverDashboard = () => {
  const { driver, fetchDriver, loading } = useDashboard();
  const [page, setPage] = useState(1);

  useEffect(() => {
    fetchDriver();
  }, [fetchDriver]);

  if (loading || !driver) {
    return <Dash />;
  }

  const {
    active_bookings,
    past_bookings,
    total_spending,
    recent_activity,
    upcoming_bookings,
  } = driver;

  return (
    <Box className="p-8 space-y-6">
      {/* Metrics */}
      <Box className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 p-2">
        <MetricCard title="Active Bookings" count={active_bookings} />
        <MetricCard title="Past Bookings" count={past_bookings} />
        <MetricCard title="Total Spending" amount={total_spending} />
      </Box>

      {/* Upcoming Bookings */}
      <Card>
        <CardHeader>
          <Text>Upcoming Bookings</Text>
        </CardHeader>
        <CardBody>
          <Box className="space-y-4">
            {upcoming_bookings.map((booking, idx) => (
              <Box key={idx} className="flex justify-between items-center">
                <Text>{booking.parking_spot__facility__name}</Text>
                <Text>{new Date(booking.start_time).toLocaleString()}</Text>
              </Box>
            ))}
            {upcoming_bookings.length === 0 && (
              <Box color={'primary.400'} className="flex flex-col justify-between items-center gap-4 pb-4">
                <CircleQuestionMark size={46} />
                <Text>No Upcoming Event</Text>
              </Box>
            )}
          </Box>
        </CardBody>
      </Card>

      {/* Google Maps Navigation */}
      <Card>
        <CardHeader>
          <Text>Navigate to Spot</Text>
        </CardHeader>
        <CardBody>
          <Box>
            {upcoming_bookings.map((booking, idx) => (
              <Button
                key={idx}
                onClick={() =>
                  window.open(
                    `https://www.google.com/maps/dir/?api=1&destination=${booking.parking_spot.latitude},${booking.parking_spot.longitude}`,
                    "_blank"
                  )
                }
                colorScheme="teal"
              >
                Navigate to {booking.parking_spot__facility__name}
              </Button>
            ))}
            {upcoming_bookings.length === 0 && (
              <Box color={'primary.400'} className="flex flex-col justify-between items-center gap-4 pb-4">
                <CircleQuestionMark size={46} />
                <Text>No Spots To Navigate to the Moment</Text>
              </Box>
            )}
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
            {recent_activity.map((activity) => (
              <Box
                key={activity.id}
                className="flex justify-between items-center"
              >
                <Text>{activity.parking_spot__facility__name}</Text>
                <Text>{new Date(activity.start_time).toLocaleString()}</Text>
              </Box>
            ))}
            {recent_activity.length === 0 && (
              <Box color={'primary.400'} className="flex flex-col justify-between items-center gap-4 pb-4">
                <CircleQuestionMark size={46} />
                <Text>No Recent activity</Text>
              </Box>
            )}

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
                  isDisabled={page === driver.recent_activity.length}
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

export default DriverDashboard;

const MetricCard = ({
  title,
  amount,
  count,
}: {
  title: string;
  amount?: number | 0;
  count?: number | 0;
}) => (
  <Card>
    <CardHeader>
      <Text className="text-sm font-medium">{title}</Text>
    </CardHeader>
    <CardBody className="text-2xl font-bold">
      {amount && <Text>{`$${amount}`}</Text>}
      {count && <Text>{count}</Text>}
    </CardBody>
  </Card>
);
