"use client";

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";

interface EgfrTrendChartProps {
  data: Array<{ date: string; egfr: number }>;
}

export default function EgfrTrendChart({ data }: EgfrTrendChartProps) {
  const chartData = data.map((d) => ({
    date: new Date(d.date).toLocaleDateString(),
    egfr: d.egfr,
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis label={{ value: "eGFR (mL/min/1.73m²)", angle: -90, position: "insideLeft" }} />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="egfr" stroke="#3b82f6" strokeWidth={2} dot={{ r: 4 }} />
        <Line
          type="monotone"
          dataKey={() => 90}
          stroke="#10b981"
          strokeDasharray="5 5"
          name="Normal (90)"
          dot={false}
        />
        <Line
          type="monotone"
          dataKey={() => 60}
          stroke="#f59e0b"
          strokeDasharray="5 5"
          name="Stage 2 (60)"
          dot={false}
        />
        <Line
          type="monotone"
          dataKey={() => 30}
          stroke="#ef4444"
          strokeDasharray="5 5"
          name="Stage 3 (30)"
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
