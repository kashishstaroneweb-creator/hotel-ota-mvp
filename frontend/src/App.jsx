import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  BarChart3,
  BedDouble,
  CalendarPlus,
  IndianRupee,
  RefreshCw,
  Signal,
  TrendingUp,
} from "lucide-react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const HOTEL_ID = 1;

const formatCurrency = (value) =>
  new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value);

const signalTypes = [
  { label: "Local Event", value: "local_event" },
  { label: "Search Demand", value: "search_demand" },
  { label: "Competitor Rate", value: "competitor_rate" },
  { label: "Pickup", value: "pickup" },
  { label: "Seasonality", value: "seasonality" },
];

function Kpi({ icon: Icon, label, value, detail }) {
  return (
    <section className="kpi">
      <div className="kpiIcon">
        <Icon size={18} />
      </div>
      <div>
        <p>{label}</p>
        <strong>{value}</strong>
        <span>{detail}</span>
      </div>
    </section>
  );
}

function App() {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    signal_type: "local_event",
    label: "",
    strength: 65,
    impact: "up",
    note: "",
  });

  const recommendationsByRoom = useMemo(() => {
    if (!dashboard) return [];
    return dashboard.hotel.room_types.map((room) => ({
      room,
      recommendations: dashboard.recommendations.filter(
        (item) => item.room_type_id === room.id,
      ),
    }));
  }, [dashboard]);

  async function loadDashboard() {
    setLoading(true);
    setError("");
    try {
      const response = await fetch(`${API_BASE}/api/hotels/${HOTEL_ID}/dashboard`);
      if (!response.ok) throw new Error("Unable to load dashboard");
      setDashboard(await response.json());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function addSignal(event) {
    event.preventDefault();
    if (!form.label.trim()) return;

    setSaving(true);
    setError("");
    try {
      const response = await fetch(`${API_BASE}/api/hotels/${HOTEL_ID}/demand-signals`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...form,
          label: form.label.trim(),
          strength: Number(form.strength),
          note: form.note.trim() || null,
        }),
      });
      if (!response.ok) throw new Error("Unable to add demand signal");
      setDashboard(await response.json());
      setForm((current) => ({ ...current, label: "", note: "" }));
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  useEffect(() => {
    loadDashboard();
  }, []);

  if (loading && !dashboard) {
    return (
      <main className="appShell centerState">
        <RefreshCw className="spin" />
        <p>Loading revenue dashboard...</p>
      </main>
    );
  }

  if (error && !dashboard) {
    return (
      <main className="appShell centerState">
        <p>{error}</p>
        <button onClick={loadDashboard}>Retry</button>
      </main>
    );
  }

  const { hotel, kpis, report } = dashboard;

  return (
    <main className="appShell">
      <header className="topbar">
        <div className="heroCopy">
          <p className="eyebrow">OTA & Revenue Management</p>
          <h1>{hotel.name}</h1>
          <span>{hotel.location}</span>
          <div className="heroPills">
            <b>{hotel.total_rooms} rooms</b>
            <b>{hotel.ota_listings.length} channels</b>
            <b>{report.month}</b>
          </div>
        </div>
        <button className="iconButton" onClick={loadDashboard} title="Refresh dashboard">
          <RefreshCw size={18} className={loading ? "spin" : ""} />
        </button>
      </header>

      {error ? <div className="notice">{error}</div> : null}

      <section className="kpiGrid">
        <Kpi
          icon={IndianRupee}
          label="Optimized ADR"
          value={formatCurrency(kpis.adr)}
          detail={`Baseline ${formatCurrency(report.baseline_adr)}`}
        />
        <Kpi
          icon={TrendingUp}
          label="Revenue Uplift"
          value={formatCurrency(kpis.revenue_uplift)}
          detail={`${report.uplift_percent}% projected lift`}
        />
        <Kpi
          icon={BedDouble}
          label="Occupancy"
          value={`${kpis.occupancy}%`}
          detail={`${kpis.rooms_sold} sold, ${kpis.available_inventory} open`}
        />
        <Kpi
          icon={Activity}
          label="OTA Health"
          value={`${kpis.healthy_channels}/${hotel.ota_listings.length}`}
          detail="Channels healthy"
        />
      </section>

      <section className="mainGrid">
        <div className="panel wide">
          <div className="panelHeader">
            <div>
              <p className="eyebrow">AI Pricing</p>
              <h2>Rate Recommendations</h2>
            </div>
            <BarChart3 size={20} />
          </div>

          <div className="recommendationStack">
            {recommendationsByRoom.map(({ room, recommendations }) => (
              <article key={room.id} className="roomBlock">
                <div className="roomHeader">
                  <div>
                    <h3>{room.name}</h3>
                    <span>
                      {room.sold_rooms}/{room.total_rooms} rooms sold
                    </span>
                  </div>
                  <strong>{formatCurrency(room.base_rate)}</strong>
                </div>

                <div className="rateTable">
                  <div className="rateRow rateHead">
                    <span>Channel</span>
                    <span>Current</span>
                    <span>Suggested</span>
                    <span>Move</span>
                  </div>
                  {recommendations.map((item) => (
                    <div className="rateRow" key={`${room.id}-${item.channel}`}>
                      <span>{item.channel}</span>
                      <span>{formatCurrency(item.current_rate)}</span>
                      <strong>{formatCurrency(item.recommended_rate)}</strong>
                      <em className={item.change_percent >= 0 ? "positive" : "negative"}>
                        {item.change_percent > 0 ? "+" : ""}
                        {item.change_percent}%
                      </em>
                    </div>
                  ))}
                </div>
              </article>
            ))}
          </div>
        </div>

        <aside className="panel">
          <div className="panelHeader">
            <div>
              <p className="eyebrow">Demand</p>
              <h2>Signals</h2>
            </div>
            <Signal size={20} />
          </div>

          <div className="signalList">
            {hotel.demand_signals.map((signal) => (
              <div className="signalItem" key={signal.id}>
                <div>
                  <strong>{signal.label}</strong>
                  <span>{signal.signal_type.replace("_", " ")}</span>
                </div>
                <b className={signal.impact}>{signal.strength}</b>
              </div>
            ))}
          </div>

          <form className="signalForm" onSubmit={addSignal}>
            <label>
              Type
              <select
                value={form.signal_type}
                onChange={(event) =>
                  setForm((current) => ({ ...current, signal_type: event.target.value }))
                }
              >
                {signalTypes.map((type) => (
                  <option value={type.value} key={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Label
              <input
                value={form.label}
                onChange={(event) =>
                  setForm((current) => ({ ...current, label: event.target.value }))
                }
                placeholder="Example: Long weekend demand"
              />
            </label>
            <label>
              Strength: {form.strength}
              <input
                type="range"
                min="1"
                max="100"
                value={form.strength}
                onChange={(event) =>
                  setForm((current) => ({ ...current, strength: event.target.value }))
                }
              />
            </label>
            <label>
              Impact
              <select
                value={form.impact}
                onChange={(event) =>
                  setForm((current) => ({ ...current, impact: event.target.value }))
                }
              >
                <option value="up">Up</option>
                <option value="down">Down</option>
                <option value="neutral">Neutral</option>
              </select>
            </label>
            <label>
              Note
              <textarea
                value={form.note}
                onChange={(event) =>
                  setForm((current) => ({ ...current, note: event.target.value }))
                }
                placeholder="Optional context"
              />
            </label>
            <button className="primaryButton" disabled={saving || !form.label.trim()}>
              <CalendarPlus size={16} />
              {saving ? "Adding..." : "Add Signal"}
            </button>
          </form>
        </aside>
      </section>

      <section className="bottomGrid">
        <div className="panel">
          <div className="panelHeader">
            <div>
              <p className="eyebrow">OTA Listings</p>
              <h2>Channel Control</h2>
            </div>
          </div>
          <div className="otaList">
            {hotel.ota_listings.map((listing) => (
              <div className="otaRow" key={listing.channel}>
                <div>
                  <strong>{listing.channel}</strong>
                  <span>{listing.last_synced}</span>
                </div>
                <span className={`status ${listing.status}`}>{listing.status.replace("_", " ")}</span>
                <b>{formatCurrency(listing.current_rate)}</b>
                <em>{listing.available_rooms} rooms</em>
              </div>
            ))}
          </div>
        </div>

        <div className="panel reportPanel">
          <div className="panelHeader">
            <div>
              <p className="eyebrow">{report.month}</p>
              <h2>Revenue Report</h2>
            </div>
          </div>
          <div className="reportBars">
            <div>
              <span>Before</span>
              <strong>{formatCurrency(report.baseline_revenue)}</strong>
              <i style={{ width: "74%" }} />
            </div>
            <div>
              <span>After</span>
              <strong>{formatCurrency(report.optimized_revenue)}</strong>
              <i style={{ width: "92%" }} />
            </div>
          </div>
          <div className="commissionBox">
            <span>15% uplift commission estimate</span>
            <strong>{formatCurrency(report.commission_model_estimate)}</strong>
          </div>
        </div>
      </section>
    </main>
  );
}

export default App;
