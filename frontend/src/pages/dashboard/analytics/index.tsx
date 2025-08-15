import { useEffect, useState } from "react";
import { Box, Card, CardBody, CardHeader, Text, Spinner, Center, useToast } from "@chakra-ui/react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { getComparisonData, getTrendsData } from "../../../services/dashboardService";

const Analytics = () => {
  const [comparisonData, setComparisonData] = useState<any[]>([]);
  const [trendsData, setTrendsData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const toast = useToast();

  const today = new Date();
  const currentMonth = today.toISOString().slice(0, 7);
  const currentYear = today.getFullYear().toString();
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [comparison, trends] = await Promise.all([
          getComparisonData(currentMonth),
          getTrendsData(currentYear)
        ]);

        // Prepare comparison (Budget vs Expenses) chart
        const formattedComparison = Object.entries(comparison).map(([category, values]: any) => ({
          name: category,
          budget: isNaN(values.budgeted) ? 0 : values.budgeted,
          expenses: isNaN(values.spent) ? 0 : values.spent,
        }));

        setComparisonData(formattedComparison);

        // Prepare trends data (Monthly expenses)
        const formattedTrends = Object.entries(trends.trends).map(([month, amount]: any) => ({
          name: month,
          expenses: isNaN(amount) ? 0 : amount
        }));

        setTrendsData(formattedTrends);

      } catch (error: any) {
        toast({
          title: "Error loading analytics",
          description: error.response?.data?.message || "Something went wrong.",
          status: "error",
          duration: 5000,
          isClosable: true,
          position: 'top'
        });
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [toast]);

  if (loading || !comparisonData.length || !trendsData.length) {
    return (
      <Center minH="400px">
        <Spinner size="xl" color="primary.400" />
      </Center>
    );
  }

  // Calculate Year-to-Date Stats
  const totalSpending = trendsData.reduce((acc, month) => acc + (month.expenses || 0), 0);
  const averageMonthly = trendsData.length > 0 ? (totalSpending / trendsData.length).toFixed(2) : '0.00';

  const biggestCategory = comparisonData.sort((a, b) => b.expenses - a.expenses)[0];

  return (
    <Box className="flex-1 space-y-8 p-8 pt-6">
      {/* Budget vs Expenses */}
      <Box className="grid gap-4 grid-cols-1">
        <Card>
          <CardHeader>
            <Text as='h1'>Budget vs. Expenses</Text>
          </CardHeader>
          <CardBody>
            <Box className="h-[400px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={comparisonData}
                  margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip formatter={(value) => `$${value}`} />
                  <Legend />
                  <Bar dataKey="budget" name="Budget" fill="#8884d8" />
                  <Bar dataKey="expenses" name="Expenses" fill="#82ca9d" />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </CardBody>
        </Card>
      </Box>

      {/* Monthly Trends and Year-to-Date Summary */}
      <Box className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <Text as='h1'>Monthly Trends</Text>
          </CardHeader>
          <CardBody>
            <Box className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={trendsData}
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip formatter={(value) => `$${value}`} />
                  <Bar dataKey="expenses" name="Expenses" fill="#82ca9d" />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <Text as='h1'>Year-to-Date Summary</Text>
          </CardHeader>
          <CardBody>
            <Box className="space-y-6">
              <Box>
                <Text className="text-sm font-medium">Total Spending</Text>
                <Text className="text-2xl font-bold">${totalSpending.toFixed(2)}</Text>
                <Text className="text-xs text-muted-foreground mt-1">Calculated from all months</Text>
              </Box>
              <Box>
                <Text className="text-sm font-medium">Average Monthly Spending</Text>
                <Text className="text-2xl font-bold">${averageMonthly}</Text>
                <Text className="text-xs text-muted-foreground mt-1">Auto-calculated</Text>
              </Box>
              {biggestCategory && biggestCategory.name ? (
                <Box>
                  <Text className="text-sm font-medium">Biggest Expense Category</Text>
                  <Text className="text-2xl font-bold">{biggestCategory.name} - ${biggestCategory.expenses.toFixed(2)}</Text>
                  <Text className="text-xs text-muted-foreground mt-1">From Budget vs Expense</Text>
                </Box>
              ) : (
                <Text>No data available for the biggest category.</Text>
              )}
            </Box>
          </CardBody>
        </Card>
      </Box>
    </Box>
  );
};

export default Analytics;
