/* eslint-disable @typescript-eslint/no-explicit-any */
import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Progress } from "../ui/progress";
import { getExpenses } from "../../services/expenseService";
import { Text } from "@chakra-ui/react";

const MetricsCards = ({ refreshKey }: { refreshKey: number }) => {
  const [analytics, setAnalytics] = useState<any[]>([]);

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
        setAnalytics(res.data || []);
      } catch (error) {
        console.error("Failed to fetch analytics", error);
      }
    };
    fetchAnalytics();
  }, [refreshKey]);

  const totalAmount = analytics.reduce(
    (sum, item) => sum + (Number(item.amount) || 0),
    0,
  );
  const activeCategories = analytics.length;

  const budgetUsedPercent = totalAmount ? (1) * 100 : 0;
  const budgetRemainingPercent = 100 - budgetUsedPercent;

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {/* Monthly Expenses */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">
            Monthly Expenses
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">${totalAmount.toFixed(2)}</div>
          <Text fontSize="xs" color="gray.500">
            +{budgetUsedPercent.toFixed(1)}% of budget spent
          </Text>
          <Progress value={budgetUsedPercent} className="mt-3 h-1" />
        </CardContent>
      </Card>

      {/* Monthly Budget */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Monthly Budget</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">${totalAmount.toFixed(2)}</div>
          <Text fontSize="xs" color="gray.500">
            {budgetRemainingPercent.toFixed(1)}% remaining
          </Text>
          <Progress value={budgetRemainingPercent} className="mt-3 h-1" />
        </CardContent>
      </Card>

      {/* Active Categories */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">
            Active Categories
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{activeCategories}</div>
          <Text fontSize="xs" color="gray.500">
            {analytics.length > 0 ? analytics[0].category : "N/A"} leading
          </Text>
          <Progress value={80} className="mt-3 h-1" />
        </CardContent>
      </Card>
    </div>
  );
};

export default MetricsCards;
