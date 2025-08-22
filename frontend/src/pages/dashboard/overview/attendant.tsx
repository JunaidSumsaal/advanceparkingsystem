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

const DriverDashboard = () => {
  const { driver, fetchDriver, loading } = useDashboard();
  const [page, setPage] = useState(1);

  useEffect(() => {
    fetchDriver();
  }, [fetchDriver]);

  if (loading || !driver) {
    return <Dash />;
  }

  const recentBookings = driver.recent_activity;
  const totalSpending = driver.total_spending;

  return (
    <Box className="p-8 space-y-6">
      {/* Metrics */}
      <Box className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <MetricCard title="Active Bookings" amount={driver.active_bookings} />
        <MetricCard title="Past Bookings" amount={driver.past_bookings} />
        <MetricCard title="Total Spending" amount={`$${totalSpending}`} />
      </Box>

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
                  isDisabled={page === recentBookings.length}
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
}: {
  title: string;
  amount: number | string;
}) => (
  <Card>
    <CardHeader>
      <Text className="text-sm font-medium">{title}</Text>
    </CardHeader>
    <CardBody>
      <Box className="text-2xl font-bold">{amount}</Box>
    </CardBody>
  </Card>
);
