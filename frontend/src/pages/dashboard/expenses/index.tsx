import { useEffect, useState } from 'react';
import { Plus, Download } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@components/ui/card";
import MetricsCards from '@components/dashboard/MetricsCards';
import ExpenseTrend from '@components/charts/ExpenseTrend';
import CategoryBreakdown from '@components/charts/CategoryBreakdown';
import RecentExpenses from '@components/dashboard/RecentExpenses';
import { Box, Button, useDisclosure, useToast } from '@chakra-ui/react';
import CreateExpenseModal from '@components/modals/CreateExpenseModal';
import CreateBudgetModal from '@components/modals/CreateBudgetModal';
import { downloadReport } from '@services/reportService';
import { getExpenses } from "@services/expenseService";

const Expenses = () => {
  const { isOpen: isExpenseOpen, onOpen: onExpenseOpen, onClose: onExpenseClose } = useDisclosure();
  const { isOpen: isBudgetOpen, onOpen: onBudgetOpen, onClose: onBudgetClose } = useDisclosure();
  const toast = useToast();
  const [refreshKey, setRefreshKey] = useState(0);
  const [expenseInfo, setExpenseInfo] = useState<any[]>([]);
  const [categoryInfo, setCategoryInfo] = useState<any[]>([]);

  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1);
  };

  
    // Fetch expenses from the backend
    useEffect(() => {
      const fetchAnalytics = async () => {
        try {
          const today = new Date();
          const currentMonth = today.toISOString().slice(0, 7);
          const res = await getExpenses({
            month: currentMonth,
            page: 1,
            limit: 5,
          });
  
          // Extract expenses by day
          const dailyExpenses = res.data.reduce((acc: any, expense: any) => {
            const expenseDate = new Date(expense.date);
            const day = expenseDate.getDate();
            if (!acc[day]) {
              acc[day] = 0;
            }
            acc[day] += expense.amount;
            return acc;
          }, {});
  
          // Convert the daily expense data into an array of objects
          const expenseData = Object.keys(dailyExpenses).map((day) => ({
            day: parseInt(day, 10),
            amount: dailyExpenses[day],
          }));
  
          // Aggregate expenses by category
          const categoryAggregation = res.data.reduce((acc: any, expense: any) => {
            const category = expense.category;
            if (!acc[category]) {
              acc[category] = 0;
            }
            acc[category] += expense.amount;
            return acc;
          }, {});
  
          // Convert category data into the format needed for the chart
          const categoryData = Object.keys(categoryAggregation).map((category) => ({
            name: category,
            value: categoryAggregation[category],
          }));
  
          setExpenseInfo(expenseData);
          setCategoryInfo(categoryData);
  
        } catch (error) {
          console.error("Failed to fetch analytics", error);
        }
      };
      fetchAnalytics();
    }, []);

  const handleDownload = async () => {
    try {
      const today = new Date();
      const currentMonth = today.toISOString().slice(0, 7);
  
      const blob = await downloadReport(currentMonth, 'pdf');
  
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `expense_report_${currentMonth}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();
  
      toast({
        title: "Report Downloaded",
        description: `Successfully downloaded report for ${currentMonth}`,
        status: "success",
        duration: 3000,
        isClosable: true,
        position: 'top'
      });
  
    } catch (error: any) {
      console.error(error);
      toast({
        title: "Error downloading report",
        description: error.response?.data?.message || "Something went wrong.",
        status: "error",
        duration: 3000,
        isClosable: true,
        position: 'top'
      });
    }
  };
  return (
    <Box as='div' className="flex-1 space-y-8 p-8 pt-6">
      <Box as='div' className="flex items-center justify-between gap-4">
        <Box as='div'className="flex items-center justify-start gap-4">
          <Button onClick={onExpenseOpen} bg={'primary.300'} color={'#fff'} _hover={{ bg: 'primary.400' }}>
            <Plus className="mr-2 h-4 w-4" /> Expense
          </Button>
          <Button onClick={onBudgetOpen} bg={'primary.300'} color={'#fff'} _hover={{ bg: 'primary.400' }}>
            <Plus className="mr-2 h-4 w-4" /> Budget
          </Button>
        </Box>

        <Button
          bg={'primary.300'}
          color={'#ffff'}
          _hover={{
            bg: 'primary.400'
          }}
          onClick={handleDownload}
        >
          <Download className="mr-2 h-4 w-4" />
          Report
        </Button>
      </Box>

      <CreateExpenseModal isOpen={isExpenseOpen} onClose={onExpenseClose} onSuccess={handleRefresh} />
      <CreateBudgetModal isOpen={isBudgetOpen} onClose={onBudgetClose} onSuccess={handleRefresh} />


      <MetricsCards refreshKey={refreshKey} />

      <Box as='div' className="grid gap-4 md:grid-cols-7">
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Daily Trend</CardTitle>
          </CardHeader>
          <CardContent>
            <ExpenseTrend data={expenseInfo} />
          </CardContent>
        </Card>
        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Expense Categories</CardTitle>
          </CardHeader>
          <CardContent>
            <CategoryBreakdown data={categoryInfo} />
          </CardContent>
        </Card>
      </Box>

      <RecentExpenses refreshKey={refreshKey} />
    </Box>
  );
};

export default Expenses;