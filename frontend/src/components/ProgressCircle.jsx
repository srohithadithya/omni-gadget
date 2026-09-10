import React from 'react';
import { PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';
import '../index.css';

const ProgressCircle = ({ value, size = 100, strokeWidth = 8, label }) => {
  const percent = Math.min(Math.max(value, 0), 100);
  const backgroundColor = 'var(--border)';
  let strokeColor = 'var(--success)';
  if (percent < 50) strokeColor = 'var(--error)';
  else if (percent < 80) strokeColor = 'var(--warning)';

  return (
    <div style={{ width: size, height: size }}>
      <PieChart width={size} height={size}>
        <Pie
          data={[
            { name: 'filled', value: percent },
            { name: 'empty', value: 100 - percent },
          ]}
          cx={size / 2}
          cy={size / 2}
          innerRadius={size / 2 - strokeWidth}
          outerRadius={size / 2}
          labelLine={false}
          label={false}
        >
          <Cell fill={backgroundColor} />
          <Cell fill={strokeColor} />
        </Pie>
        <Tooltip formatter={(value) => `${value}%`} />
        <Legend verticalAlign="bottom" height={36} />
      </PieChart>
      <div style={{
        position: 'relative',
        top: -size,
        left: 0,
        width: size,
        height: size,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}>
        <div style={{
          fontWeight: 600,
          fontSize: size * 0.15,
          color: 'var(--text)',
        }}>
          {label ?? `${percent}%`}
        </div>
      </div>
    </div>
  );
};

export default ProgressCircle;