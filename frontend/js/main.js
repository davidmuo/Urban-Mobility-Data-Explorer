let allTrips = [];

async function fetchTrips() {
    try {
        const response = await fetch(`${API_BASE}/api/trips/?per_page=10000`);
        allTrips = await response.json();
        if (allTrips.trips) allTrips = allTrips.trips;
        renderDashboard(allTrips);
    } catch (error) {
        console.error("Failed to fetch trips:", error);
    }
}

function applyFilters() {
    const vendor = document.getElementById("vendorSelect").value;
    const passengers = document.getElementById("passengerSelect").value;
    const startDate = document.getElementById("startDate").value;
    const endDate = document.getElementById("endDate").value;

    return allTrips.filter(trip => {
        if (vendor !== "all" && trip.vendor_id != vendor) return false;
        if (passengers !== "all") {
            if (passengers === "6" && trip.passenger_count < 6) return false;
            if (passengers !== "6" && trip.passenger_count != passengers) return false;
        }
        if (startDate && new Date(trip.pickup_datetime) < new Date(startDate)) return false;
        if (endDate && new Date(trip.pickup_datetime) > new Date(endDate)) return false;
        return true;
    });
}

function renderDashboard(data) {
    updateSummaryMetrics(data);
    renderSpeedChart(data);
    renderDurationChart(data);
    renderSpeedDistanceChart(data);
    renderLongestTrips(data);
}

function animateCounter(el, target, decimals) {
    let current = 0;
    const step = target / 40;
    const interval = setInterval(() => {
        current += step;
        if (current >= target) {
            current = target;
            clearInterval(interval);
        }
        el.innerText = decimals > 0 ? current.toFixed(decimals) : Math.round(current);
    }, 20);
}

function updateSummaryMetrics(data) {
    const totalEl = document.getElementById("metricTotalTrips");
    const speedEl = document.getElementById("metricAvgSpeed");
    const durEl = document.getElementById("metricAvgDuration");
    const distEl = document.getElementById("metricAvgDistance");

    if (data.length === 0) {
        totalEl.innerText = 0;
        speedEl.innerText = 0;
        durEl.innerText = 0;
        distEl.innerText = 0;
        return;
    }

    const avgSpeed = parseFloat((data.reduce((sum, t) => sum + (t.trip_speed_mph || t.speed_kmh || 0), 0) / data.length).toFixed(1));
    const avgDuration = parseFloat((data.reduce((sum, t) => sum + (t.trip_duration_minutes || t.duration_minutes || 0), 0) / data.length).toFixed(1));
    const avgDistance = parseFloat((data.reduce((sum, t) => sum + (t.trip_distance || t.distance_km || 0), 0) / data.length).toFixed(1));

    animateCounter(totalEl, data.length, 0);
    animateCounter(speedEl, avgSpeed, 1);
    animateCounter(durEl, avgDuration, 1);
    animateCounter(distEl, avgDistance, 1);

    const pill = document.getElementById("tripCountPill");
    if (pill) pill.textContent = data.length.toLocaleString() + " trips";
}

function renderLongestTrips(data) {
    const tableBody = document.querySelector("#longestTripsTable tbody");
    const emptyMessage = document.getElementById("emptyStateMessage");
    tableBody.innerHTML = "";

    if (data.length === 0) {
        emptyMessage.style.display = "block";
        return;
    }
    emptyMessage.style.display = "none";

    const longestTrips = [...data]
        .sort((a, b) => (b.trip_duration_minutes || b.duration_minutes || 0) - (a.trip_duration_minutes || a.duration_minutes || 0))
        .slice(0, 5);

    longestTrips.forEach(trip => {
        const duration = (trip.trip_duration_minutes || trip.duration_minutes || 0).toFixed(1);
        const distance = (trip.trip_distance || trip.distance_km || 0).toFixed(2);
        const speed = (trip.trip_speed_mph || trip.speed_kmh || 0).toFixed(1);
        const row = `
            <tr>
                <td>${trip.id || '-'}</td>
                <td>${duration} min</td>
                <td>${distance} mi</td>
                <td>${speed} mph</td>
                <td>${trip.passenger_count}</td>
                <td>${trip.vendor_id}</td>
            </tr>
        `;
        tableBody.innerHTML += row;
    });
}

document.getElementById("applyFiltersBtn").addEventListener("click", () => {
    const filteredTrips = applyFilters();
    renderDashboard(filteredTrips);
    renderExtraCharts(filteredTrips);
    showToast(`Filters applied â€” ${filteredTrips.length} trips shown`);
});

document.getElementById("resetFiltersBtn").addEventListener("click", () => {
    document.getElementById("vendorSelect").value = "all";
    document.getElementById("passengerSelect").value = "all";
    document.getElementById("startDate").value = "";
    document.getElementById("endDate").value = "";
    renderDashboard(allTrips);
    renderExtraCharts(allTrips);
    showToast("Filters reset");
});

document.getElementById("exportCsvBtn").addEventListener("click", () => {
    const filteredTrips = applyFilters();
    downloadCSV(filteredTrips);
    showToast(`Exported ${filteredTrips.length} trips to CSV`);
});

const API_BASE = (() => {
    const h = window.location.hostname;
    return (h === 'localhost' || h === '127.0.0.1')
        ? 'http://127.0.0.1:5000'
        : 'https://urban-mobility-data-explorer-y6h6.onrender.com';
})();
let zonesMap = {};

async function fetchZones() {
    try {
        const res = await fetch(`${API_BASE}/api/zones/`);
        const data = await res.json();
        if (data.zones) {
            data.zones.forEach(z => { zonesMap[z.location_id] = z; });
        }
    } catch (err) {
        console.warn('Could not fetch zones:', err);
    }
}

function renderExtraCharts(data) {
    renderBoroughChart(data, zonesMap);
    renderPaymentChart(data);
    renderHourlyChart(data);
    renderFareDistanceChart(data);
    renderHeatmap(data);
}

function showToast(message) {
    const toast = document.getElementById("toast");
    toast.innerHTML = `<span class="toast-icon">âœ“</span> ${message}`;
    toast.classList.add("show");
    setTimeout(() => toast.classList.remove("show"), 3000);
}

function hideLoading() {
    const screen = document.getElementById("loadingScreen");
    if (screen) screen.classList.add("hidden");
}

function setupScrollSpy() {
    const sections = document.querySelectorAll("[id]");
    const navLinks = document.querySelectorAll(".nav-link");

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const id = entry.target.id;
                navLinks.forEach(link => {
                    link.classList.toggle("active", link.getAttribute("data-section") === id);
                });
            }
        });
    }, { rootMargin: "-20% 0px -70% 0px" });

    sections.forEach(section => {
        if (section.id && document.querySelector(`[data-section="${section.id}"]`)) {
            observer.observe(section);
        }
    });
}

function setupSearch() {
    const input = document.getElementById("globalSearch");
    const dropdown = document.getElementById("searchResults");

    const searchTargets = [
        { label: "Dashboard", desc: "KPI cards and overview", href: "#hero" },
        { label: "Speed Distribution", desc: "Speed histogram chart", href: "#core-charts" },
        { label: "Trip Duration", desc: "Duration distribution chart", href: "#core-charts" },
        { label: "Speed vs Distance", desc: "Scatter plot correlation", href: "#core-charts" },
        { label: "Trips by Borough", desc: "Manhattan, Brooklyn, Queens...", href: "#borough-anchor" },
        { label: "Payment Methods", desc: "Credit card vs cash split", href: "#fare-anchor" },
        { label: "Hourly Volume", desc: "24-hour trip patterns", href: "#extra-charts-anchor" },
        { label: "Fare vs Distance", desc: "Fare correlation analysis", href: "#extra-charts-anchor" },
        { label: "Heatmap", desc: "Day x Hour trip density", href: "#heatmap-anchor" },
        { label: "Longest Trips", desc: "Top 5 by duration table", href: "#data-section-anchor" },
        { label: "Manhattan", desc: "Borough â€” highest trip volume", href: "#borough-anchor" },
        { label: "Brooklyn", desc: "Borough â€” outer borough trips", href: "#borough-anchor" },
        { label: "Queens", desc: "Borough â€” airport connections", href: "#borough-anchor" },
        { label: "Bronx", desc: "Borough â€” northern NYC", href: "#borough-anchor" },
        { label: "Rush Hour", desc: "Insight â€” PM fare premium", href: "#extra-charts-anchor" },
        { label: "Weekend", desc: "Insight â€” night surge patterns", href: "#heatmap-anchor" },
        { label: "Export CSV", desc: "Download filtered trip data", href: "#" },
        { label: "Filters", desc: "Vendor, passengers, date range", href: "#hero" },
    ];

    input.addEventListener("input", () => {
        const query = input.value.toLowerCase().trim();
        if (query.length < 2) {
            dropdown.classList.remove("open");
            return;
        }

        const matches = searchTargets.filter(t =>
            t.label.toLowerCase().includes(query) || t.desc.toLowerCase().includes(query)
        );

        if (matches.length === 0) {
            dropdown.innerHTML = '<div class="search-no-results">No results found</div>';
        } else {
            dropdown.innerHTML = matches.map(m => `
                <div class="search-item" data-href="${m.href}">
                    <div class="search-label">${m.label}</div>
                    <div class="search-meta">${m.desc}</div>
                </div>
            `).join("");
        }
        dropdown.classList.add("open");
    });

    dropdown.addEventListener("click", (e) => {
        const item = e.target.closest(".search-item");
        if (!item) return;
        const href = item.getAttribute("data-href");
        if (href && href !== "#") {
            document.querySelector(href)?.scrollIntoView({ behavior: "smooth" });
        }
        if (href === "#" && item.textContent.includes("Export")) {
            document.getElementById("exportCsvBtn").click();
        }
        dropdown.classList.remove("open");
        input.value = "";
    });

    document.addEventListener("click", (e) => {
        if (!e.target.closest(".search-container")) {
            dropdown.classList.remove("open");
        }
    });
}

async function initDashboard() {
    try {
        await fetchZones();
        const res = await fetch(`${API_BASE}/api/trips/?per_page=10000`);
        const data = await res.json();

        if (data.trips && data.trips.length > 0) {
            allTrips = data.trips;
            renderDashboard(allTrips);
            renderExtraCharts(allTrips);
            hideLoading();
            showToast(`Loaded ${allTrips.length.toLocaleString()} trips`);
            return;
        }
    } catch (err) {
        console.warn('API fetch failed, trying original endpoint:', err);
    }

    await fetchTrips();
    hideLoading();
    if (allTrips.length > 0) {
        renderExtraCharts(allTrips);
        showToast(`Loaded ${allTrips.length.toLocaleString()} trips`);
    }
}

setupScrollSpy();
setupSearch();
initDashboard();
