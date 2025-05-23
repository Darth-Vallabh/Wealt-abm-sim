import React from 'react';
import Plot from 'react-plotly.js';

const Chart = ({ results }) => {
  if (!results || results.length === 0) return null;

  const time = results.map(r => r.time);

  // --- Wealth by Decile ---
  const decileTraces = Object.keys(results[0].wealth_by_decile).map(decile => ({
    x: time,
    y: results.map(r => r.wealth_by_decile[decile]),
    type: 'scatter',
    mode: 'lines+markers',
    name: `Decile ${decile}`,
    line: { shape: 'spline' }
  }));

  // --- Wealth Share Traces (1st, Bottom 50%, 10th) ---
  const wealthShare1st = results.map(r => r.wealth_share_1st_decile || 0);     // Ensure fallback
  const wealthShare10th = results.map(r => r.wealth_share_10th_decile || 0);   // Ensure fallback
  const wealthShareBottom50 = results.map(r => r.wealth_share_bottom_50 || 0); // Ensure fallback
  const ratio_90_10 = results.map(r => r.wealth_ratio_90_10);
  const ratio_90_50 = results.map(r => r.wealth_ratio_90_50);
   const gini_wealth = results.map(r => r.gini_overall_wealth);
   const totalIncomeTax = results.map(r => r.total_income_tax_collected ?? null);
   const totalCGTax = results.map(r => r.total_cg_tax || 0);
const wealthTaxShare = results.map(r => r.tax_share_wealth ?? 0);
const cgTaxShare = results.map(r => r.tax_share_cg ?? 0);
const incomeTaxShare = results.map(r => r.tax_share_income ?? 0);
const inheritanceTaxShare = results.map(r => r.tax_share_inheritance ?? 0);
   const totalWealthTaxCollected = results.map(r => r.total_wealth_tax_collected ?? 0);
  const gini_income = results.map(r => r.gini_overall_income ?? null);
  const wealthTaxByDecile = {};
  const incomeTaxPerDecile = {};

   const inheritanceTaxByDecile = {};
const totalInheritanceTax = results.map(r => r.total_inheritance_tax ?? 0);

// Fill inheritance tax per decile data
results.forEach((r, t) => {
  if (r.inheritance_tax_by_decile) {
    Object.entries(r.inheritance_tax_by_decile).forEach(([decile, tax]) => {
      if (!inheritanceTaxByDecile[decile]) inheritanceTaxByDecile[decile] = [];
      inheritanceTaxByDecile[decile][t] = tax;
    });
  }
});
const decileHeatmaps = results.map((r, idx) => {
  const matrix = r.decile_transition_matrix?.matrix;
  const rows = Object.keys(matrix || {});
  const cols = rows.length > 0 ? Object.keys(matrix[rows[0]]) : [];

  const z = rows.map(row => cols.map(col => matrix[row]?.[col] || 0));
  const text = z.map(row => row.map(val => `${val.toFixed(1)}%`));

  return (
    <div key={idx}>
      <h4 style={{ textAlign: 'center' }}>Transition Matrix - Time Step {r.time}</h4>
      <Plot
        data={[{
          z,
          x: cols,
          y: rows,
          type: 'heatmap',
          colorscale: 'YlGnBu',
          showscale: true,
          text: text,
          texttemplate: '%{text}',
          hovertemplate: 'From %{y} to %{x}: %{z:.1f}%<extra></extra>',
        }]}
        layout={{
          title: 'Decile Transition Heatmap',
          xaxis: { title: 'Final Decile' },
          yaxis: { title: 'Original Decile' },
          height: 450,
          margin: { l: 60, r: 40, t: 60, b: 60 },
        }}
        config={{ responsive: true }}
      />
    </div>
  );
});
const decileCutoffLines = results.map((r, idx) => {
  const cutoffs = r.decile_cutoffs?.cutoffs || [];

  const data = cutoffs.map(cut => ({
    x: [cut.lower, cut.upper],
    y: [10 - cut.decile + 1, 10 - cut.decile + 1],
    type: 'scatter',
    mode: 'lines+text',
    text: [`${Math.round(cut.lower)}–${Math.round(cut.upper)}`],
    textposition: 'top center',
    name: `Decile ${cut.decile}`
  }));

  return (
    <div key={idx}>
      <h4 style={{ textAlign: 'center' }}>Wealth Cutoffs - Time Step {r.time}</h4>
      <Plot
        data={data}
        layout={{
          title: 'Decile Wealth Cutoff Ranges',
          xaxis: { title: 'Wealth' },
          yaxis: { title: 'Decile', tickvals: Array.from({length: 10}, (_, i) => i + 1).reverse() },
          height: 400,
          margin: { l: 60, r: 40, t: 40, b: 60 }
        }}
      />
    </div>
  );
});
const inheritanceTaxTraces = Object.entries(inheritanceTaxByDecile).map(([decile, taxes]) => ({
  x: time,
  y: taxes,
  type: 'scatter',
  mode: 'lines+markers',
  name: `Decile ${decile}`,
  line: { shape: 'spline' }
}));


results.forEach((r, t) => {
  if (r.tax_per_decile_income) {
    Object.entries(r.tax_per_decile_income).forEach(([decile, tax]) => {
      if (!incomeTaxPerDecile[decile]) incomeTaxPerDecile[decile] = [];
      incomeTaxPerDecile[decile][t] = tax;
    });
  }
});

const incomeTaxTraces = Object.entries(incomeTaxPerDecile).map(([decile, taxes]) => ({
  x: time,
  y: taxes,
  type: 'scatter',
  mode: 'lines+markers',
  name: `Decile ${decile}`,
}));
  const deciles = Object.keys(results[0].cg_tax_by_decile || {});
const cgTaxTraces = deciles.map(decile => ({
  x: time,
  y: results.map(r => r.cg_tax_by_decile[decile] ?? 0),
  type: 'scatter',
  mode: 'lines+markers',
  name: `Decile ${decile}`,
  line: { shape: 'spline' },
}));
results.forEach(r => {
  Object.entries(r.wealth_tax_by_decile || {}).forEach(([decile, tax]) => {
    if (!wealthTaxByDecile[decile]) wealthTaxByDecile[decile] = [];
    wealthTaxByDecile[decile].push(tax);
  });
});

const wealthTaxTraces = Object.entries(wealthTaxByDecile).map(([decile, values]) => ({
  x: time,
  y: values,
  type: 'scatter',
  mode: 'lines+markers',
  name: `Decile ${decile}`,
  line: { shape: 'spline' },
}));
  const shareTraces = [
    {
      x: time,
      y: wealthShare1st,
      type: 'scatter',
      mode: 'lines+markers',
      name: '1st Decile Share',
      line: { color: 'green', shape: 'spline' },
    },
    {
      x: time,
      y: wealthShareBottom50,
      type: 'scatter',
      mode: 'lines+markers',
      name: 'Bottom 50% Share',
      line: { color: 'blue', shape: 'spline' },
    },
    {
      x: time,
      y: wealthShare10th,
      type: 'scatter',
      mode: 'lines+markers',
      name: '10th Decile Share',
      line: { color: 'red', shape: 'spline' },
    },
  ];

  return (
    <div style={{ marginTop: '40px' }}>
        {decileHeatmaps}
{decileCutoffLines}
      {/* Chart 1: Wealth by Decile */}
      <h3 style={{ textAlign: 'center' }}>Wealth by Decile Over Time</h3>
      <Plot
        data={decileTraces}
        layout={{
          autosize: true,
          height: 500,
          margin: { l: 60, r: 40, t: 40, b: 60 },
          xaxis: { title: 'Time Step', tickformat: 'd' },
          yaxis: { title: 'Wealth', rangemode: 'tozero' },
          legend: { orientation: 'h', x: 0, y: -0.3 },
        }}
        config={{ responsive: true }}
      />

      {/* Chart 2: Wealth Share Trends */}
      <h3 style={{ textAlign: 'center', marginTop: '60px' }}>
        Wealth Share Over Time (1st, Bottom 50%, 10th Decile)
      </h3>
      <Plot
        data={shareTraces}
        layout={{
          autosize: true,
          height: 400,
          margin: { l: 60, r: 40, t: 40, b: 60 },
          xaxis: { title: 'Time Step', tickformat: 'd' },
          yaxis: { title: 'Wealth Share', range: [0, 1] },
          legend: { orientation: 'h', x: 0, y: -0.3 },
        }}
        config={{ responsive: true }}
      />
              <h3 style={{ textAlign: 'center', marginTop: '60px' }}>
        Wealth Ratios Over Time (90/10 and 90/50)
      </h3>
      <Plot
        data={[
          {
            x: time,
            y: ratio_90_10,
            type: 'scatter',
            mode: 'lines+markers',
            marker: { color: 'purple' },
            name: '90/10 Ratio',
            line: { shape: 'spline' },
          },
          {
            x: time,
            y: ratio_90_50,
            type: 'scatter',
            mode: 'lines+markers',
            marker: { color: 'blue' },
            name: '90/50 Ratio',
            line: { shape: 'spline' },
          }
        ]}
        layout={{
          height: 450,
          margin: { l: 60, r: 40, t: 40, b: 60 },
          xaxis: { title: 'Time Step' },
          yaxis: { title: 'Wealth Ratio' },
        }}
        config={{ responsive: true }}
      />
        {/* Chart 4: Gini Coefficients */}
      <h3 style={{ textAlign: 'center', marginTop: '60px' }}>Gini Coefficients Over Time</h3>
      <Plot
        data={[
          {
            x: time,
            y: gini_wealth,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Gini (Wealth)',
            line: { color: 'darkorange', shape: 'spline' }
          },
          {
            x: time,
            y: gini_income,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Gini (Income)',
            line: { color: 'blue', shape: 'spline' }
          }
        ]}
        layout={{
          height: 450,
          margin: { l: 60, r: 40, t: 40, b: 60 },
          xaxis: { title: 'Time Step' },
          yaxis: { title: 'Gini Coefficient', range: [0, 1] },
        }}
        config={{ responsive: true }}
      />
        {/* Chart 5: Wealth Tax Collected per Decile */}
<h3 style={{ textAlign: 'center', marginTop: '60px' }}>
  Wealth Tax Collected per Decile Over Time
</h3>
<Plot
  data={wealthTaxTraces}
  layout={{
    autosize: true,
    height: 500,
    margin: { l: 60, r: 40, t: 40, b: 60 },
    xaxis: { title: 'Time Step' },
    yaxis: { title: 'Total Wealth Tax Collected' },
    legend: { orientation: 'h', x: 0, y: -0.3 },
  }}
  config={{ responsive: true }}
/>
        {/* Chart 6: Total Wealth Tax Collected */}
<h3 style={{ textAlign: 'center', marginTop: '60px' }}>
  Total Wealth Tax Collected Over Time
</h3>
<Plot
  data={[
    {
      x: time,
      y: totalWealthTaxCollected,
      type: 'scatter',
      mode: 'lines+markers',
      name: 'Total Wealth Tax',
      line: { color: 'green', shape: 'spline' },
    }
  ]}
  layout={{
    height: 450,
    margin: { l: 60, r: 40, t: 40, b: 60 },
    xaxis: { title: 'Time Step' },
    yaxis: { title: 'Total Wealth Tax Collected' },
  }}
  config={{ responsive: true }}
/>
        {/* Chart 7: CG Tax per Decile Over Time */}
<h3 style={{ textAlign: 'center', marginTop: '60px' }}>
  Total Capital Gains Tax per Decile Over Time
</h3>
<Plot
  data={cgTaxTraces}
  layout={{
    autosize: true,
    height: 450,
    margin: { l: 60, r: 40, t: 40, b: 60 },
    xaxis: { title: 'Time Step' },
    yaxis: { title: 'Total CG Tax' },
    legend: { orientation: 'h', x: 0, y: -0.3 },
  }}
  config={{ responsive: true }}
/>
        <h3 style={{ textAlign: 'center', marginTop: '60px' }}>
  Total Capital Gains Tax Collected Over Time
</h3>
<Plot
  data={[
    {
      x: time,
      y: totalCGTax,
      type: 'scatter',
      mode: 'lines+markers',
      name: 'Total CG Tax',
      marker: { color: 'green' },
      line: { shape: 'spline' },
    },
  ]}
  layout={{
    height: 400,
    margin: { l: 60, r: 40, t: 40, b: 60 },
    xaxis: { title: 'Time Step' },
    yaxis: { title: 'Capital Gains Tax Collected' },
  }}
  config={{ responsive: true }}
/>
        <h3 style={{ textAlign: 'center', marginTop: '60px' }}>Total Income Tax per Decile Over Time</h3>
<Plot
  data={incomeTaxTraces}
  layout={{
    height: 450,
    margin: { l: 60, r: 40, t: 40, b: 60 },
    xaxis: { title: 'Time Step' },
    yaxis: { title: 'Total Income Tax Collected' },
    legend: { orientation: 'h', x: 0, y: -0.3 },
  }}
  config={{ responsive: true }}
/>
        <h3 style={{ textAlign: 'center', marginTop: '60px' }}>Total Income Tax Collected Over Time</h3>
<Plot
  data={[
    {
      x: time,
      y: totalIncomeTax,
      type: 'scatter',
      mode: 'lines+markers',
      name: 'Total Income Tax',
      line: { color: 'green', shape: 'spline' }
    }
  ]}
  layout={{
    height: 450,
    margin: { l: 60, r: 40, t: 40, b: 60 },
    xaxis: { title: 'Time Step' },
    yaxis: { title: 'Total Income Tax Collected' },
    legend: { orientation: 'h', x: 0, y: -0.3 },
  }}
  config={{ responsive: true }}
/>
{/* Chart 9: Inheritance Tax Collected per Decile */}
<h3 style={{ textAlign: 'center', marginTop: '60px' }}>
  Inheritance Tax Collected per Decile Over Time
</h3>
<Plot
  data={inheritanceTaxTraces}
  layout={{
    autosize: true,
    height: 500,
    margin: { l: 60, r: 40, t: 40, b: 60 },
    xaxis: { title: 'Time Step' },
    yaxis: { title: 'Total Inheritance Tax Collected' },
    legend: { orientation: 'h', x: 0, y: -0.3 },
  }}
  config={{ responsive: true }}
/>

{/* Chart 10: Total Inheritance Tax Collected */}
<h3 style={{ textAlign: 'center', marginTop: '60px' }}>
  Total Inheritance Tax Collected Over Time
</h3>
<Plot
  data={[
    {
      x: time,
      y: totalInheritanceTax,
      type: 'scatter',
      mode: 'lines+markers',
      name: 'Total Inheritance Tax',
      line: { color: 'green', shape: 'spline' },
    }
  ]}
  layout={{
    height: 450,
    margin: { l: 60, r: 40, t: 40, b: 60 },
    xaxis: { title: 'Time Step' },
    yaxis: { title: 'Total Inheritance Tax Collected' },
    legend: { orientation: 'h', x: 0, y: -0.3 },
  }}
  config={{ responsive: true }}
/>
        <h3 style={{ textAlign: 'center', marginTop: '60px' }}>
  Total Taxes Collected Across All Deciles Over Time
</h3>
<Plot
  data={[
    {
      x: time,
      y: totalWealthTaxCollected,
      type: 'scatter',
      mode: 'lines+markers',
      name: 'Total Wealth Tax',
      line: { color: 'green', shape: 'spline' },
    },
    {
      x: time,
      y: totalCGTax,
      type: 'scatter',
      mode: 'lines+markers',
      name: 'Total CG Tax',
      line: { color: 'red', shape: 'spline' },
    },
    {
      x: time,
      y: totalIncomeTax,
      type: 'scatter',
      mode: 'lines+markers',
      name: 'Total Income Tax',
      line: { color: 'blue', shape: 'spline' },
    },
    {
      x: time,
      y: totalInheritanceTax,
      type: 'scatter',
      mode: 'lines+markers',
      name: 'Total Inheritance Tax',
      line: { color: 'cyan', shape: 'spline' },
    }
  ]}
  layout={{
    height: 500,
    margin: { l: 60, r: 40, t: 40, b: 60 },
    xaxis: { title: 'Time Step' },
    yaxis: { title: 'Tax Collected (Total)' },
    legend: { orientation: 'h', x: 0, y: -0.3 },
    grid: { rows: 1, columns: 1 },
  }}
  config={{ responsive: true }}
/>
        <h3 style={{ textAlign: 'center', marginTop: '60px' }}>
  Wealth Tax Share Over Time
</h3>
<Plot
  data={[
    {
      x: time,
      y: wealthTaxShare,
      type: 'scatter',
      mode: 'lines+markers',
      name: 'Wealth Tax Share',
      line: { color: 'red', shape: 'spline' }
    }
  ]}
  layout={{
    height: 400,
    margin: { l: 60, r: 40, t: 40, b: 60 },
    xaxis: { title: 'Time Step' },
    yaxis: { title: 'Wealth Tax Share', range: [0, 0.8] },
  }}
  config={{ responsive: true }}
/>

<h3 style={{ textAlign: 'center', marginTop: '60px' }}>
  Capital Gains Tax Share Over Time
</h3>
<Plot
  data={[
    {
      x: time,
      y: cgTaxShare,
      type: 'scatter',
      mode: 'lines+markers',
      name: 'CG Tax Share',
      line: { color: 'blue', shape: 'spline' }
    }
  ]}
  layout={{
    height: 400,
    margin: { l: 60, r: 40, t: 40, b: 60 },
    xaxis: { title: 'Time Step' },
    yaxis: { title: 'CG Tax Share', range: [0, 0.8] },
  }}
  config={{ responsive: true }}
/>

<h3 style={{ textAlign: 'center', marginTop: '60px' }}>
  Income Tax Share Over Time
</h3>
<Plot
  data={[
    {
      x: time,
      y: incomeTaxShare,
      type: 'scatter',
      mode: 'lines+markers',
      name: 'Income Tax Share',
      line: { color: 'green', shape: 'spline' }
    }
  ]}
  layout={{
    height: 400,
    margin: { l: 60, r: 40, t: 40, b: 60 },
    xaxis: { title: 'Time Step' },
    yaxis: { title: 'Income Tax Share', range: [0, 0.8] },
  }}
  config={{ responsive: true }}
/>

<h3 style={{ textAlign: 'center', marginTop: '60px' }}>
  Inheritance Tax Share Over Time
</h3>
<Plot
  data={[
    {
      x: time,
      y: inheritanceTaxShare,
      type: 'scatter',
      mode: 'lines+markers',
      name: 'Inheritance Tax Share',
      line: { color: 'orange', shape: 'spline' }
    }
  ]}
  layout={{
    height: 400,
    margin: { l: 60, r: 40, t: 40, b: 60 },
    xaxis: { title: 'Time Step' },
    yaxis: { title: 'Inheritance Tax Share', range: [0, 0.8] },
  }}
  config={{ responsive: true }}
/>
        <h3 style={{ textAlign: 'center', marginTop: '60px' }}>
  Tax Share Composition Over Time
</h3>
<Plot
  data={[
    {
      x: time,
      y: wealthTaxShare,
      type: 'scatter',
      mode: 'lines+markers',
      name: 'Wealth Tax Share',
      line: { color: 'red', shape: 'spline' }
    },
    {
      x: time,
      y: cgTaxShare,
      type: 'scatter',
      mode: 'lines+markers',
      name: 'CG Tax Share',
      line: { color: 'blue', shape: 'spline' }
    },
    {
      x: time,
      y: incomeTaxShare,
      type: 'scatter',
      mode: 'lines+markers',
      name: 'Income Tax Share',
      line: { color: 'green', shape: 'spline' }
    },
    {
      x: time,
      y: inheritanceTaxShare,
      type: 'scatter',
      mode: 'lines+markers',
      name: 'Inheritance Tax Share',
      line: { color: 'orange', shape: 'spline' }
    }
  ]}
  layout={{
    height: 450,
    margin: { l: 60, r: 40, t: 40, b: 60 },
    xaxis: { title: 'Time Step' },
    yaxis: { title: 'Share of Total Tax', range: [0, 0.8] },
    legend: { orientation: 'h', x: 0, y: -0.3 },
  }}
  config={{ responsive: true }}
/>
    </div>
  );
};

export default Chart;