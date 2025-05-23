import React from 'react';
import Plot from 'react-plotly.js';

const WealthShareChart = ({ results }) => {
  if (!results || results.length === 0) return null;

  const timeSteps = results.map(r => r.time);

  // Extract wealth shares
  const share1st = results.map(r =>
    r.wealth_by_decile?.['1'] && r.total_wealth
      ? r.wealth_by_decile['1'] / r.total_wealth
      : 0
  );

  const share10th = results.map(r =>
    r.wealth_by_decile?.['10'] && r.total_wealth
      ? r.wealth_by_decile['10'] / r.total_wealth
      : 0
  );

  const shareBottom50 = results.map(r => {
    const total = r.total_wealth || 1;
    const bottom_half = ['1', '2', '3', '4', '5'].reduce((sum, decile) => {
      return sum + (r.wealth_by_decile?.[decile] || 0);
    }, 0);
    return bottom_half / total;
  });

  return (
    <div style={{ marginTop: '40px' }}>
      <h3 style={{ textAlign: 'center' }}>Wealth Share Over Time</h3>
      <Plot
        data={[
          {
            x: timeSteps,
            y: share1st,
            type: 'scatter',
            mode: 'lines+markers',
            name: '1st Decile',
            line: { color: 'green' },
          },
          {
            x: timeSteps,
            y: shareBottom50,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Bottom 50%',
            line: { color: 'blue' },
          },
          {
            x: timeSteps,
            y: share10th,
            type: 'scatter',
            mode: 'lines+markers',
            name: '10th Decile',
            line: { color: 'red' },
          },
        ]}
        layout={{
          autosize: true,
          height: 500,
          xaxis: { title: 'Time Step', tickformat: 'd' },
          yaxis: {
            title: 'Wealth Share',
            range: [0, 1],
            tickformat: '.0%',
          },
          margin: { l: 60, r: 40, t: 40, b: 60 },
          legend: { orientation: 'h', x: 0, y: -0.3 },
        }}
        config={{ responsive: true }}
      />
    </div>
  );
};

export default WealthShareChart;