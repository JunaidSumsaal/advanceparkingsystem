import { Card, CardContent, CardHeader, CardTitle } from "@components/ui/card";
import { getExpenses } from "@services/expenseService";
import { useEffect, useState } from "react";
import { Spinner } from "@chakra-ui/react";

const RecentExpenses = ({ refreshKey }: { refreshKey: number }) => {
  const [expenses, setExpenses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const today = new Date();
  const currentMonth = today.toISOString().slice(0, 7);

  useEffect(() => {
    const fetchExpenses = async () => {
      setLoading(true);
      try {
        const res = await getExpenses({ month: currentMonth, page: 1, limit: 5 });
        setExpenses(res.data);
      } catch (error) {
        console.error("Error fetching expenses", error);
      } finally {
        setLoading(false);
      }
    };

    fetchExpenses();
  }, [currentMonth, refreshKey]);
  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Expenses</CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex justify-center p-4">
            <Spinner size="md" />
          </div>
        ) : expenses.length > 0 ? (
          <div className="space-y-8">
            {expenses.map((item, i) => (
              <div key={item._id} className="flex items-center justify-between">
                <div className="space-y-1">
                  <p className="text-sm font-medium leading-none">{item.category}</p>
                  <p className="text-xs text-muted-foreground">
                    {new Date(item.date).toLocaleDateString()} • {item.category}
                  </p>
                </div>
                <div className="font-medium">${item.amount.toFixed(2)}</div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-center text-sm text-muted-foreground">No expenses found for this month.</p>
        )}
      </CardContent>
    </Card>
  );
};

export default RecentExpenses;
