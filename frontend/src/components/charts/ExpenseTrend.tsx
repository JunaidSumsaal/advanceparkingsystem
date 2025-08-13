import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
} from 'recharts';
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@components/ui/chart";

interface ExpenseTrendProps {
  data: Array<{ day: number; amount: number }>;
}

const ExpenseTrend = ({ data }: ExpenseTrendProps) => {
  return (
    <div className="h-[380px]">
      <ChartContainer
        config={{
          expenses: {
            label: "Daily Expenses",
            theme: {
              light: "#0088FE",
              dark: "#0088FE",
            },
          }
        }}
      >
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={data}
            margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
            <XAxis 
              dataKey="day" 
              tick={{ fontSize: 12 }}
              tickLine={false}
              tickFormatter={(value) => `Day ${value}`} // To show "Day 1", "Day 2", etc.
            />
            <YAxis 
              tick={{ fontSize: 12 }} 
              tickLine={false}
              tickFormatter={(value) => `$${value}`}
            />
            <ChartTooltip content={<ChartTooltipContent />} />
            <Area
              type="monotone"
              dataKey="amount"
              name="expenses"
              stroke="#0088FE"
              fill="#0088FE"
              fillOpacity={0.2}
            />
          </AreaChart>
        </ResponsiveContainer>
      </ChartContainer>
    </div>
  );
};

export default ExpenseTrend;
