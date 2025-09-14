import React from "react";
import { ResponsiveContainer, AreaChart, Area, LineChart, Line } from "recharts";

const MiniSparkline = ({ data = [], color = "#2563eb", type = "area" }) => {
  const chartData = (Array.isArray(data) ? data : []).map((v, i) => ({ i, v: Number(v) || 0 }));
  if (!chartData.length) {
    return <div className="h-10" />;
  }
  return (
    <div className="h-10">
      <ResponsiveContainer width="100%" height="100%">
        {type === 'line' ? (
          <LineChart data={chartData} margin={{ top: 4, right: 0, bottom: 0, left: 0 }}>
            <Line type="monotone" dataKey="v" stroke={color} strokeWidth={2} dot={false} isAnimationActive={false} />
          </LineChart>
        ) : (
          <AreaChart data={chartData} margin={{ top: 4, right: 0, bottom: 0, left: 0 }}>
            <defs>
              <linearGradient id="spark" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={color} stopOpacity={0.32} />
                <stop offset="100%" stopColor={color} stopOpacity={0} />
              </linearGradient>
            </defs>
            <Area type="monotone" dataKey="v" stroke={color} fill="url(#spark)" strokeWidth={2} isAnimationActive={false} />
          </AreaChart>
        )}
      </ResponsiveContainer>
    </div>
  );
};

export default MiniSparkline;

