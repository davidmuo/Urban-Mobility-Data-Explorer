var chartInstances = {};

var CHART_COLORS = {
    green: '#b8e468',
    greenBg: 'rgba(184,228,104,0.5)',
    coral: '#f0a898',
    coralBg: 'rgba(240,168,152,0.4)',
    lavender: '#d4c8f0',
    lavenderBg: 'rgba(212,200,240,0.4)',
    mint: '#c8edd8',
    mintBg: 'rgba(200,237,216,0.4)',
    pink: '#f4c6d7',
    pinkBg: 'rgba(244,198,215,0.4)',
    yellow: '#f5e6a3',
    yellowBg: 'rgba(245,230,163,0.4)',
    peach: '#f5d4b8',
    peachBg: 'rgba(245,212,184,0.4)',
    text: '#1a1a1a',
    text2: '#6b6560',
    text3: '#a09890',
    grid: 'rgba(0,0,0,0.04)'
};

var CHART_FONT = { family: 'Plus Jakarta Sans', size: 11, weight: '500' };
var MONO_FONT = { family: 'JetBrains Mono', size: 10 };

function destroyChart(key) {
    if (chartInstances[key]) {
        chartInstances[key].destroy();
        chartInstances[key] = null;
    }
}
function renderSpeedChart(data) {
    destroyChart('speed');
    const ctx = document.getElementById('speedChartCanvas');
    if (!ctx) return;

    const speeds = data.map(t => t.trip_speed_mph || t.speed_kmh || 0).filter(s => s > 0 && s < 80);
    const bins = Array(16).fill(0);
    speeds.forEach(s => {
        const idx = Math.min(Math.floor(s / 5), 15);
        bins[idx]++;
    });
    const labels = bins.map((_, i) => `${i * 5}-${i * 5 + 5}`);

    chartInstances.speed = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Trips',
                data: bins,
                backgroundColor: CHART_COLORS.greenBg,
                borderColor: CHART_COLORS.green,
                borderWidth: 1.5,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: {
                    title: { display: true, text: 'Speed (mph)', color: CHART_COLORS.text3, font: MONO_FONT },
                    ticks: { color: CHART_COLORS.text3, font: MONO_FONT },
                    grid: { color: CHART_COLORS.grid }
                },
                y: {
                    title: { display: true, text: 'Trips', color: CHART_COLORS.text3, font: MONO_FONT },
                    ticks: { color: CHART_COLORS.text3, font: MONO_FONT },
                    grid: { color: CHART_COLORS.grid }
                }
            }
        }
    });
}
function renderDurationChart(data) {
    destroyChart('duration');
    const ctx = document.getElementById('durationChartCanvas');
    if (!ctx) return;

    const durations = data.map(t => t.trip_duration_minutes || t.duration_minutes || 0).filter(d => d > 0 && d < 120);
    const bins = Array(12).fill(0);
    durations.forEach(d => {
        const idx = Math.min(Math.floor(d / 10), 11);
        bins[idx]++;
    });
    const labels = bins.map((_, i) => `${i * 10}-${i * 10 + 10}`);

    chartInstances.duration = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Trips',
                data: bins,
                backgroundColor: CHART_COLORS.lavenderBg,
                borderColor: CHART_COLORS.lavender,
                borderWidth: 1.5,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: {
                    title: { display: true, text: 'Duration (min)', color: CHART_COLORS.text3, font: MONO_FONT },
                    ticks: { color: CHART_COLORS.text3, font: MONO_FONT },
                    grid: { color: CHART_COLORS.grid }
                },
                y: {
                    title: { display: true, text: 'Trips', color: CHART_COLORS.text3, font: MONO_FONT },
                    ticks: { color: CHART_COLORS.text3, font: MONO_FONT },
                    grid: { color: CHART_COLORS.grid }
                }
            }
        }
    });
}
function renderSpeedDistanceChart(data) {
    destroyChart('speedDist');
    const ctx = document.getElementById('speedDistanceChartCanvas');
    if (!ctx) return;

    const sample = data.filter(() => Math.random() < 0.3).slice(0, 500);
    const points = sample.map(t => ({
        x: t.trip_distance || t.distance_km || 0,
        y: t.trip_speed_mph || t.speed_kmh || 0
    })).filter(p => p.x > 0 && p.x < 30 && p.y > 0 && p.y < 60);

    chartInstances.speedDist = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                data: points,
                backgroundColor: CHART_COLORS.coralBg,
                borderColor: CHART_COLORS.coral,
                borderWidth: 1,
                pointRadius: 3.5,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: {
                    title: { display: true, text: 'Distance (mi)', color: CHART_COLORS.text3, font: MONO_FONT },
                    ticks: { color: CHART_COLORS.text3, font: MONO_FONT },
                    grid: { color: CHART_COLORS.grid }
                },
                y: {
                    title: { display: true, text: 'Speed (mph)', color: CHART_COLORS.text3, font: MONO_FONT },
                    ticks: { color: CHART_COLORS.text3, font: MONO_FONT },
                    grid: { color: CHART_COLORS.grid }
                }
            }
        }
    });
}
function renderBoroughChart(data, zones) {
    destroyChart('borough');
    const ctx = document.getElementById('boroughChartCanvas');
    if (!ctx) return;

    const counts = {};
    data.forEach(t => {
        let borough = 'Unknown';
        if (zones && zones[t.pulocation_id]) {
            borough = zones[t.pulocation_id].borough || 'Unknown';
        }
        counts[borough] = (counts[borough] || 0) + 1;
    });

    const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, 6);
    const colors = [CHART_COLORS.green, CHART_COLORS.lavender, CHART_COLORS.peach, CHART_COLORS.pink, CHART_COLORS.yellow, CHART_COLORS.mint];

    chartInstances.borough = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sorted.map(s => s[0]),
            datasets: [{ data: sorted.map(s => s[1]), backgroundColor: colors.slice(0, sorted.length), borderRadius: 8 }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: CHART_COLORS.text3, font: MONO_FONT }, grid: { color: CHART_COLORS.grid } },
                y: { ticks: { color: CHART_COLORS.text2, font: { ...CHART_FONT, size: 12 } }, grid: { display: false } }
            }
        }
    });
}
function renderPaymentChart(data) {
    destroyChart('payment');
    const ctx = document.getElementById('paymentChartCanvas');
    if (!ctx) return;

    const paymentMap = { 1: 'Credit Card', 2: 'Cash', 3: 'No Charge', 4: 'Dispute', 5: 'Unknown', 6: 'Voided' };
    const counts = {};
    data.forEach(t => {
        const label = paymentMap[t.payment_type] || 'Other';
        counts[label] = (counts[label] || 0) + 1;
    });

    const labels = Object.keys(counts);
    const values = Object.values(counts);
    const colorMap = { 'Credit Card': CHART_COLORS.lavender, 'Cash': CHART_COLORS.mint, 'No Charge': '#e8e4dd', 'Dispute': CHART_COLORS.coral, 'Unknown': CHART_COLORS.peach, 'Other': CHART_COLORS.yellow };

    chartInstances.payment = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{ data: values, backgroundColor: labels.map(l => colorMap[l] || '#ccc'), borderWidth: 0 }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '62%',
            plugins: {
                legend: { position: 'bottom', labels: { color: CHART_COLORS.text2, font: CHART_FONT, usePointStyle: true, padding: 14 } }
            }
        }
    });
}
function renderHourlyChart(data) {
    destroyChart('hourly');
    const ctx = document.getElementById('hourlyChartCanvas');
    if (!ctx) return;

    const counts = Array(24).fill(0);
    const fares = Array(24).fill(0);

    data.forEach(t => {
        const dt = t.pickup_datetime;
        if (!dt) return;
        const hour = new Date(dt).getHours();
        if (!isNaN(hour)) {
            counts[hour]++;
            fares[hour] += (t.fare_amount || 0);
        }
    });

    const avgFares = counts.map((c, i) => c > 0 ? fares[i] / c : 0);

    chartInstances.hourly = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Array.from({ length: 24 }, (_, i) => i.toString().padStart(2, '0') + ':00'),
            datasets: [
                { label: 'Trips', data: counts, backgroundColor: CHART_COLORS.green, borderRadius: 6, yAxisID: 'y', order: 2 },
                { label: 'Avg Fare', data: avgFares, type: 'line', borderColor: CHART_COLORS.coral, borderWidth: 2.5, pointRadius: 0, tension: 0.4, yAxisID: 'y1', order: 1 }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { labels: { color: CHART_COLORS.text2, font: CHART_FONT, usePointStyle: true, pointStyleWidth: 8, padding: 16 } } },
            scales: {
                x: { ticks: { color: CHART_COLORS.text3, font: MONO_FONT }, grid: { color: CHART_COLORS.grid } },
                y: { position: 'left', ticks: { color: CHART_COLORS.text3, font: MONO_FONT }, grid: { color: CHART_COLORS.grid } },
                y1: { position: 'right', ticks: { color: CHART_COLORS.coral, font: MONO_FONT }, grid: { display: false } }
            }
        }
    });
}
function renderFareDistanceChart(data) {
    destroyChart('fareDist');
    const ctx = document.getElementById('fareDistanceChartCanvas');
    if (!ctx) return;

    const sample = data.filter(() => Math.random() < 0.3).slice(0, 400);
    const points = sample.map(t => ({
        x: t.trip_distance || t.distance_km || 0,
        y: t.fare_amount || 0
    })).filter(p => p.x > 0 && p.x < 30 && p.y > 0 && p.y < 100);

    chartInstances.fareDist = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                data: points,
                backgroundColor: CHART_COLORS.yellowBg,
                borderColor: '#d4c44a',
                borderWidth: 1,
                pointRadius: 3.5,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: {
                    title: { display: true, text: 'Distance (mi)', color: CHART_COLORS.text3, font: MONO_FONT },
                    ticks: { color: CHART_COLORS.text3, font: MONO_FONT },
                    grid: { color: CHART_COLORS.grid }
                },
                y: {
                    title: { display: true, text: 'Fare ($)', color: CHART_COLORS.text3, font: MONO_FONT },
                    ticks: { color: CHART_COLORS.text3, font: MONO_FONT },
                    grid: { color: CHART_COLORS.grid }
                }
            }
        }
    });
}
function renderHeatmap(data) {
    const container = document.getElementById('heatmapContainer');
    if (!container) return;

    const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const grid = Array.from({ length: 7 }, () => Array(24).fill(0));

    data.forEach(t => {
        const dt = t.pickup_datetime;
        if (!dt) return;
        const d = new Date(dt);
        const dow = d.getDay() === 0 ? 6 : d.getDay() - 1;
        const hour = d.getHours();
        if (!isNaN(dow) && !isNaN(hour)) grid[dow][hour]++;
    });

    const maxVal = Math.max(...grid.flat(), 1);
    container.innerHTML = '';

    container.appendChild(document.createElement('div'));
    for (let h = 0; h < 24; h++) {
        const el = document.createElement('div');
        el.className = 'hm-hour';
        el.textContent = h.toString().padStart(2, '0');
        container.appendChild(el);
    }

    for (let d = 0; d < 7; d++) {
        const label = document.createElement('div');
        label.className = 'hm-label';
        label.textContent = DAYS[d];
        container.appendChild(label);

        for (let h = 0; h < 24; h++) {
            const cell = document.createElement('div');
            cell.className = 'hm-cell';
            const pct = grid[d][h] / maxVal;
            const r = Math.round(184 * pct + 240 * (1 - pct));
            const g = Math.round(228 * pct + 236 * (1 - pct));
            const b = Math.round(104 * pct + 230 * (1 - pct));
            cell.style.background = `rgb(${r},${g},${b})`;

            const tip = document.createElement('div');
            tip.className = 'hm-tip';
            tip.textContent = `${DAYS[d]} ${h}:00 â€” ${grid[d][h]} trips`;
            cell.appendChild(tip);
            container.appendChild(cell);
        }
    }
}
function downloadCSV(data) {
    if (!data || data.length === 0) {
        alert('No data to export.');
        return;
    }

    const headers = Object.keys(data[0]);
    const rows = data.map(row =>
        headers.map(h => {
            let val = row[h];
            if (val === null || val === undefined) val = '';
            val = String(val).replace(/"/g, '""');
            return `"${val}"`;
        }).join(',')
    );

    const csv = [headers.join(','), ...rows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'nyc_taxi_trips_export.csv';
    link.click();
    URL.revokeObjectURL(url);
}
