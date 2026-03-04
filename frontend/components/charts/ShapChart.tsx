"use client";

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

interface ShapChartProps {
  features: Array<{ feature: string; importance: number }>;
}

export default function ShapChart({ features }: ShapChartProps) {
  const data = features.map((f) => ({
    name: f.feature.replace(/_/g, " "),
    importance: f.importance,
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} layout="vertical">
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis type="number" />
        <YAxis dataKey="name" type="category" width={120} />
        <Tooltip />
        <Bar dataKey="importance" fill="#3b82f6" />
      </BarChart>
    </ResponsiveContainer>
  );
}
