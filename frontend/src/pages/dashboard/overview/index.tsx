import { useEffect, useState } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Box, Card, CardBody, CardHeader, Text, Spinner, Center, useToast } from "@chakra-ui/react";
import { getAnalyticsOverview, getExpenseTrends, getCategoryBreakdown, getRecentExpenses, getfetchSuggestions } from '../../../services/dashboardService';
import { Progress } from "../../../components/ui/progress";
import Pagination from '../../../components/dashboard/pagination';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

const Overview = () => {
  const [overview, setOverview] = useState<any>(null);
  const [monthlyExpenses, setMonthlyExpenses] = useState<any[]>([]);
  const [categorySpending, setCategorySpending] = useState<any[]>([]);
  const [recentExpenses, setRecentExpenses] = useState<any[]>([]);
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [suggestionsPage, setSuggestionsPage] = useState(1);
  const [suggestionsTotalPages, setSuggestionsTotalPages] = useState(1);
  const toast = useToast();
  const today = new Date();
  const currentMonth = today.toISOString().slice(0, 7);
  const currentYear = today.getFullYear().toString();

  const handleSuggestionsPageChange = async (page: number) => {
    try {
      setLoading(true);
      const suggestionsData = await getfetchSuggestions({
        month: currentMonth,
        page: page,
        limit: 5,
      });
  
      setSuggestions(suggestionsData.suggestions);
      setSuggestionsPage(page);
      setSuggestionsTotalPages(suggestionsData.totalPages || 1);
    } catch (error: any) {
      toast({
        title: "Error loading suggestions",
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
  

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [analytics, trends, breakdown, recent, suggestionsData] = await Promise.all([
          getAnalyticsOverview(currentMonth),
          getExpenseTrends(currentYear),
          getCategoryBreakdown(currentMonth),
          getRecentExpenses(1, 3),
          getfetchSuggestions({
            month: currentMonth,
            page: suggestionsPage,
            limit: 5,
          })
        ]);

        setSuggestions(suggestionsData.suggestions);

        // Calculate Metrics
        const totalBudget = analytics.summary.reduce((sum: number, item: any) => sum + item.budgeted, 0);
        const totalExpenses = analytics.summary.reduce((sum: number, item: any) => sum + item.spent, 0);
        const savings = totalBudget - totalExpenses;
        const activeBudgets = analytics.summary.length;

        setOverview({
          totalBudget,
          totalExpenses,
          savings,
          activeBudgets
        });

        // Prepare monthly expenses for AreaChart
        const monthlyExpensesData = Object.entries(trends.trends).map(([month, amount]) => ({
          month,
          amount
        }));

        setMonthlyExpenses(monthlyExpensesData);

        // Prepare category breakdown for PieChart
        const categoryData = Object.entries(breakdown).map(([name, value]) => ({
          name,
          value
        }));

        setCategorySpending(categoryData);

        // Recent Expenses
        setRecentExpenses(recent.data);

      } catch (error: any) {
        toast({
          title: "Error loading dashboard",
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

  if (loading) {
    return (
      <Center minH="400px">
        <Spinner size="xl" color="primary.400" />
      </Center>
    );
  }

  return (
    <Box className="flex-1 space-y-8 p-8 pt-6">
      {/* Metrics */}
      <Box className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <MetricCard title="Total Expenses" amount={`$${overview.totalExpenses}`} change="+20% from last month" progress={70} />
        <MetricCard title="Total Budget" amount={`$${overview.totalBudget}`} change="Remaining Budget" progress={(overview.totalBudget - overview.totalExpenses) / overview.totalBudget * 100} />
        <MetricCard title="Savings" amount={`$${overview.savings}`} change="+5% from last week" progress={(overview.savings / overview.totalBudget) * 100} />
        <MetricCard title="Active Budgets" amount={overview.activeBudgets} change="Active Categories" progress={80} />
      </Box>

      {/* Charts */}
      <Box className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4">
          <CardHeader><Text>Expense Overview</Text></CardHeader>
          <CardBody>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={monthlyExpenses}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                <XAxis dataKey="month" />
                <YAxis tickFormatter={(value) => `$${value}`} />
                <Tooltip />
                <Area type="monotone" dataKey="amount" stroke="#0088FE" fill="#0088FE" fillOpacity={0.2} />
              </AreaChart>
            </ResponsiveContainer>
          </CardBody>
        </Card>

        <Card className="col-span-3">
          <CardHeader><Text>Spending by Category</Text></CardHeader>
          <CardBody>
            <ResponsiveContainer width="100%" height={380}>
              <PieChart>
                <Pie
                  data={categorySpending}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {categorySpending.map((_, idx) => (
                    <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `$${value}`} />
              </PieChart>
            </ResponsiveContainer>
          </CardBody>
        </Card>
      </Box>

      {/* Recent Activity */}
      <Box className="grid gap-4">
        <Card>
          <CardHeader><Text>Recent Activity</Text></CardHeader>
          <CardBody>
            <Box className="space-y-8">
              {recentExpenses.map((item: any, idx: number) => (
                <Box key={idx} className="flex items-center justify-between">
                  <Box className="space-y-1">
                    <Text className="text-sm font-medium leading-none">{item.category}</Text>
                    <Text className="text-xs text-muted-foreground">
                      {new Date(item.date).toLocaleDateString()}
                    </Text>
                  </Box>
                  <Box className="font-medium">{`$${item.amount}`}</Box>
                </Box>
              ))}
            </Box>
          </CardBody>
        </Card>
      </Box>

      {/* Suggestions */}
      <Box className="grid gap-4">
        <Card>
          <CardHeader><Text>Suggestions</Text></CardHeader>
          <CardBody>
            <Box className="space-y-4">
              {suggestions.map((item: any, idx: number) => (
                <Box key={idx} className="flex items-center justify-between">
                  <Box className="flex flex-col items-start">
                    <Text className="text-lg font-medium">{item.category}</Text>
                    <Text className="text-sm">{item.advice}</Text>
                    <Text className={`text-xs text-muted-foreground ${item.status === 'Over Budget' ? 'text-red-500' : ''}`}>
                      {item.status}
                    </Text>
                  </Box>

                  {/* Educational Resource Links */}
                    {item.category && (
                      <Box className="space-y-2 mt-4 flex flex-col items-end">
                        <Text className="text-sm font-semibold">Learn More</Text>
                        {item.resourceLinks.map((resource: any, resourceIdx: any) => (
                          <Box key={resourceIdx} className="text-blue-600">
                            <a href={resource.link} target="_blank" rel="noopener noreferrer">
                              {resource.title}
                            </a>
                          </Box>
                        ))}
                      </Box>
                    )}
                </Box>
              ))}
              {/* Add Pagination here */}
              <Center mt={4}>
                <Pagination
                  currentPage={suggestionsPage}
                  totalPages={suggestionsTotalPages}
                  handlePageChange={handleSuggestionsPageChange}
                />
              </Center>
            </Box>
          </CardBody>
        </Card>
      </Box>
    </Box>
  );
};

export default Overview;

// Helper Metric Card
const MetricCard = ({ title, amount, change, progress }: { title: string; amount: string | number; change: string; progress: number }) => (
  <Card>
    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
      <Text className="text-sm font-medium">{title}</Text>
    </CardHeader>
    <CardBody>
      <Box className="text-2xl font-bold">{amount}</Box>
      <p className="text-xs text-muted-foreground">{change}</p>
      <Progress value={progress} className="mt-3 h-1" />
    </CardBody>
  </Card>
);
