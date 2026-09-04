import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

const TrendBarChart = ({ data, maxValue }) => {
  if (!data || data.length === 0) return null;

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" tick={{ fontSize: 12, fill: 'var(--text-muted)' }} />
        <YAxis 
          domain={[0, Math.ceil(maxValue * 1.2)]}
          tick={{ fontSize: 12, fill: 'var(--text-muted)' }}
        />
        <Tooltip 
          formatter={(value) => value.toFixed(1)} 
          wrapperStyle={{ borderRadius: 4, padding: 8 }}
          labelStyle={{ fontSize: 12 }}
          valueStyle={{ fontSize: 14, fontWeight: 600 }}
        />
        <Legend 
          verticalAlign="top" 
          height={36} 
          formatter={(value) => `Decision Index`}
        />
        <Bar 
          dataKey="value" 
          barSize={24} 
          fill="#d97706" 
          radius={[6, 6, 0, 0]} 
        />
      </BarChart>
    </ResponsiveContainer>
  );
};

export default TrendBarChart;