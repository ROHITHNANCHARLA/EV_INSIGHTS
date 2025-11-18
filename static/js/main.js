// main.js (poseify helpers) — currently small helper functions
console.log("EV Insight Poseify theme loaded.");
document.getElementById('k_total').innerText = data.total_units.toLocaleString();
document.getElementById('k_state').innerText = data.top_state;
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
console.log("⚡ EV Insight | Advanced Analytics Loaded");

// Wait for button click
document.getElementById('applyFilters').addEventListener('click', (e) => {
  e.preventDefault();

  const payload = {
    year: document.getElementById('f_year').value,
    state: document.getElementById('f_state').value,
    vehicle_type: document.getElementById('f_type').value
  };

  fetch('/api/filter', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
    .then(res => res.json())
    .then(data => {
      // ✅ KPIs
      document.getElementById('k_total').innerText = data.kpi.total_units.toLocaleString();
      document.getElementById('k_state').innerText = data.kpi.top_state;
      document.getElementById('k_type').innerText = data.kpi.top_type;
      document.getElementById('k_rows').innerText = data.kpi.rows;

      // ✅ Sales by State
      Plotly.newPlot('chart_state', [{
        x: data.charts.by_state.map(d => d.State),
        y: data.charts.by_state.map(d => d.EV_Sales_Quantity),
        type: 'bar',
        marker: { color: '#00eaff' }
      }], {
        title: 'Sales by State',
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: { color: '#eaf6ff' }
      });

      // ✅ Sales by Vehicle Type
      Plotly.newPlot('chart_type', [{
        labels: data.charts.by_type.map(d => d.Vehicle_Type),
        values: data.charts.by_type.map(d => d.EV_Sales_Quantity),
        type: 'pie',
        hole: 0.4
      }], {
        title: 'Sales by Vehicle Type',
        paper_bgcolor: 'transparent',
        font: { color: '#eaf6ff' }
      });

      // ✅ Manufacturer Performance
      Plotly.newPlot('chart_manufacturer', [{
        x: data.charts.by_manufacturer.map(d => d.Manufacturer),
        y: data.charts.by_manufacturer.map(d => d.EV_Sales_Quantity),
        type: 'bar',
        marker: { color: '#0077ff' }
      }], {
        title: 'Manufacturer Performance',
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: { color: '#eaf6ff' }
      });

      // ✅ Monthly Trend
      Plotly.newPlot('chart_month', [{
        x: data.charts.by_month.map(d => d.Month_Name),
        y: data.charts.by_month.map(d => d.EV_Sales_Quantity),
        mode: 'lines+markers',
        line: { color: '#00bfff' },
        marker: { size: 6 }
      }], {
        title: 'Monthly Sales Trend',
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: { color: '#eaf6ff' }
      });
    })
    .catch(err => console.error('❌ Filter API error:', err));
});

