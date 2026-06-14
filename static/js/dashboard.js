async function loadDashboardAnalytics() {
  const res = await fetch('/api/dashboard/analytics');
  const data = await res.json();

  document.getElementById('metricProfit').textContent = '₹' + Number(data.total_profit || 0).toLocaleString('en-IN');
  document.getElementById('metricListings').textContent = data.active_listings || 0;
  document.getElementById('metricOrders').textContent = data.total_orders || 0;

  const insightsList = document.getElementById('insightsList');
  insightsList.innerHTML = (data.insights || []).map(item => `<li>${item}</li>`).join('');

  const sellingCtx = document.getElementById('sellingChart');
  const buyingCtx = document.getElementById('buyingChart');
  const profitCtx = document.getElementById('profitChart');

  if (window.dashboardCharts) {
    window.dashboardCharts.forEach(chart => chart.destroy());
  }

  window.dashboardCharts = [
    new Chart(sellingCtx, {
      type: 'line',
      data: {
        labels: data.labels,
        datasets: [{ label: 'Selling (₹)', data: data.selling_series, borderColor: '#16a34a', backgroundColor: 'rgba(22,163,74,0.12)', fill: true, tension: 0.3 }]
      },
      options: { responsive: true, plugins: { legend: { display: false } } }
    }),
    new Chart(buyingCtx, {
      type: 'bar',
      data: {
        labels: data.labels,
        datasets: [{ label: 'Buying (₹)', data: data.buying_series, backgroundColor: '#2563eb' }]
      },
      options: { responsive: true, plugins: { legend: { display: false } } }
    }),
    new Chart(profitCtx, {
      type: 'bar',
      data: {
        labels: data.profit_labels,
        datasets: [{ label: 'Profit (₹)', data: data.profit_series, backgroundColor: ['#16a34a','#22c55e','#f59e0b','#3b82f6','#a78bfa','#fb7185'] }]
      },
      options: { responsive: true, plugins: { legend: { display: false } } }
    })
  ];
}

async function loadInventory() {
  const res = await fetch('/api/inventory');
  const items = await res.json();
  const mount = document.getElementById('inventoryList');

  if (!items.length) {
    mount.innerHTML = '<article class="order-card"><p class="small">No inventory items yet. Add one to start your shop.</p></article>';
    return;
  }

  mount.innerHTML = items.map(item => `
    <article class="order-card">
      <p class="badge">${item.crop_name}</p>
      <h3>${item.crop_name}</h3>
      <p class="small">Qty: ${item.quantity_quintal} quintal (${item.quantity_kg} kg)</p>
      <p class="small">Price: ₹${Number(item.price_per_quintal || 0).toLocaleString('en-IN')}/quintal</p>
      <p class="small">Location: ${item.location || 'Local market'}</p>
      <p class="small">${item.description || 'Manual inventory entry'}</p>
    </article>
  `).join('');
}

async function addInventory(e) {
  e.preventDefault();
  const token = localStorage.getItem('token');
  if (!token) {
    alert('Please log in to add inventory.');
    return;
  }

  const response = await fetch('/api/inventory', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
    body: JSON.stringify({
      crop_name: document.getElementById('inventoryCrop').value,
      quantity_quintal: Number(document.getElementById('inventoryQty').value || 0),
      price_per_quintal: Number(document.getElementById('inventoryPrice').value || 0),
      location: document.getElementById('inventoryLocation').value,
      description: document.getElementById('inventoryDescription').value,
    }),
  });

  const data = await response.json();
  document.getElementById('inventoryMessage').textContent = data.message || 'Inventory updated';
  document.getElementById('inventoryForm').reset();
  loadInventory();
}

loadDashboardAnalytics();
loadInventory();

document.getElementById('inventoryForm').addEventListener('submit', addInventory);
