import { useCallback, useEffect, useState } from "react";
import {
  LayoutDashboard, ShieldAlert, Search, History, BarChart3, Settings,
  Bell, ShieldCheck, Activity, AlertTriangle, Menu, X, RefreshCw,
} from "lucide-react";
import {
  ResponsiveContainer, PieChart, Pie, Cell, Tooltip, BarChart, Bar,
  XAxis, YAxis, CartesianGrid,
} from "recharts";
import {
  getDashboardStatistics, getFraudDistribution, getRiskDistribution,
  getRecentActivity, analyzeFraudMessage, getFraudCases, getHistory,
} from "./api";
import "./App.css";

const riskColors = { Critical: "#dc2626", High: "#f97316", Medium: "#eab308", Low: "#16a34a" };
const navigation = [
  { label: "Dashboard", icon: LayoutDashboard },
  { label: "Analyze Message", icon: Search },
  { label: "Fraud Cases", icon: ShieldAlert },
  { label: "History", icon: History },
  { label: "Analytics", icon: BarChart3 },
];

function formatDate(value) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "—";
  return date.toLocaleString("en-IN", {
    timeZone: "Asia/Kolkata", day: "2-digit", month: "short", year: "numeric",
    hour: "2-digit", minute: "2-digit", hour12: true,
  });
}

function RiskBadge({ level }) {
  const value = level || "Unknown";
  return <span className={`risk-badge ${value.toLowerCase()}`}>{value}</span>;
}

function EmptyState({ text }) {
  return <div className="empty-state">{text}</div>;
}

function App() {
  const [activePage, setActivePage] = useState("Dashboard");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [stats, setStats] = useState(null);
  const [fraudData, setFraudData] = useState([]);
  const [riskData, setRiskData] = useState([]);
  const [activities, setActivities] = useState([]);
  const [fraudCases, setFraudCases] = useState([]);
  const [historyRecords, setHistoryRecords] = useState([]);
  const [historyTotal, setHistoryTotal] = useState(0);
  const [historyPage, setHistoryPage] = useState(1);
  const [historySearch, setHistorySearch] = useState("");
  const [historyRisk, setHistoryRisk] = useState("");
  const [caseSearch, setCaseSearch] = useState("");
  const [message, setMessage] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [loadingPage, setLoadingPage] = useState(false);
  const [error, setError] = useState("");

  const loadDashboard = useCallback(async () => {
    try {
      setError("");
      const [statistics, fraudDistribution, riskDistribution, recentActivity] = await Promise.all([
        getDashboardStatistics(), getFraudDistribution(), getRiskDistribution(), getRecentActivity(5),
      ]);
      setStats(statistics);
      setFraudData(fraudDistribution);
      setRiskData(riskDistribution);
      setActivities(recentActivity);
    } catch (err) {
      console.error("Dashboard loading failed:", err);
      setError(err.message || "Dashboard data could not be loaded. Check the backend and database.");
    }
  }, []);

  const loadFraudCases = useCallback(async () => {
    setLoadingPage(true);
    try {
      setError("");
      setFraudCases(await getFraudCases(caseSearch));
    } catch (err) {
      console.error("Fraud cases loading failed:", err);
      setError(err.message || "Could not load fraud cases.");
    } finally {
      setLoadingPage(false);
    }
  }, [caseSearch]);

  const loadHistory = useCallback(async () => {
    setLoadingPage(true);
    try {
      setError("");
      const data = await getHistory({
        page: historyPage, limit: 10, search: historySearch, risk_level: historyRisk,
      });
      setHistoryRecords(data.records || []);
      setHistoryTotal(data.total || 0);
    } catch (err) {
      console.error("History loading failed:", err);
      setError(err.message || "Could not load analysis history.");
    } finally {
      setLoadingPage(false);
    }
  }, [historyPage, historyRisk, historySearch]);

  useEffect(() => { loadDashboard(); }, [loadDashboard]);
  useEffect(() => { if (activePage === "Fraud Cases") loadFraudCases(); }, [activePage, loadFraudCases]);
  useEffect(() => { if (activePage === "History") loadHistory(); }, [activePage, loadHistory]);

  function navigateTo(label) {
    setActivePage(label);
    setSidebarOpen(false);
    setError("");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function handleAnalyze(event) {
    event.preventDefault();
    if (message.trim().length < 5) {
      setError("Please enter a message containing at least 5 characters.");
      return;
    }
    try {
      setAnalyzing(true);
      setError("");
      setAnalysis(null);
      const result = await analyzeFraudMessage(message.trim());
      setAnalysis(result);
      await loadDashboard();
    } catch (err) {
      console.error("Message analysis failed:", err);
      setError(err.message || "Message analysis failed. Please try again.");
    } finally {
      setAnalyzing(false);
    }
  }

  const statCards = [
    { title: "Total Analyses", value: stats?.total_analyses ?? "—", icon: Activity, color: "blue" },
    { title: "Suspicious Cases", value: stats?.suspicious_cases ?? "—", icon: AlertTriangle, color: "orange" },
    { title: "Critical Cases", value: stats?.critical_cases ?? "—", icon: ShieldAlert, color: "red" },
    { title: "Suspicious Rate", value: stats == null ? "—" : `${stats.suspicious_percentage}%`, icon: BarChart3, color: "green" },
  ];

  const visibleCases = fraudCases.filter((item) => {
    const text = `${item.name || ""} ${item.category || ""} ${item.description || ""}`.toLowerCase();
    return text.includes(caseSearch.toLowerCase());
  });
  const totalPages = Math.max(1, Math.ceil(historyTotal / 10));

  return (
    <div className="app-shell">
      {sidebarOpen && <button className="mobile-overlay" aria-label="Close navigation" onClick={() => setSidebarOpen(false)} />}
      <aside className={`sidebar ${sidebarOpen ? "sidebar-open" : ""}`}>
        <div className="brand">
          <div className="brand-icon"><ShieldCheck size={25} /></div>
          <div><h2>CyberRakshak</h2><span>AI SECURITY PLATFORM</span></div>
          <button className="mobile-close" aria-label="Close menu" onClick={() => setSidebarOpen(false)}><X size={21} /></button>
        </div>
        <div className="nav-caption">WORKSPACE</div>
        <nav className="sidebar-nav">
          {navigation.map(({ label, icon: Icon }) => (
            <button key={label} className={`nav-item ${activePage === label ? "nav-active" : ""}`} onClick={() => navigateTo(label)}>
              <Icon size={19} /><span>{label}</span>
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="protection-card"><ShieldCheck size={23} /><h3>Stay Protected</h3><p>Verify suspicious messages before sharing personal or financial information.</p></div>
          <button className={`nav-item settings-item ${activePage === "Settings" ? "nav-active" : ""}`} onClick={() => navigateTo("Settings")}><Settings size={19} /><span>Settings</span></button>
          <div className="sidebar-footer"><span className="online-dot" />Backend connection is checked when loading data</div>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="topbar-left">
            <button className="mobile-menu" aria-label="Open navigation" onClick={() => setSidebarOpen(true)}><Menu size={23} /></button>
            <div className="breadcrumb">Workspace <span>/</span> <strong>{activePage}</strong></div>
          </div>
          <div className="topbar-right">
            <div className="system-status"><span className="online-dot" />Security Dashboard</div>
            <button className="icon-button" aria-label="Notifications" title="Notifications"><Bell size={19} /></button>
            <div className="profile-avatar">CR</div>
          </div>
        </header>

        <div className="page-content">
          {error && <div className="error-banner" role="alert"><AlertTriangle size={19} /><span>{error}</span><button onClick={() => activePage === "Fraud Cases" ? loadFraudCases() : activePage === "History" ? loadHistory() : loadDashboard()}>Retry</button></div>}

          {activePage === "Dashboard" && (
            <>
              <PageHeading title="Security Overview" subtitle="Detect suspicious messages, understand risks, and make safer decisions online." action={<button className="primary-button" onClick={() => navigateTo("Analyze Message")}><Search size={18} />Analyze Message</button>} />
              <StatsGrid cards={statCards} />
              <ChartsGrid fraudData={fraudData} riskData={riskData} />
              <ActivityTable activities={activities} onRefresh={loadDashboard} />
            </>
          )}

          {activePage === "Analyze Message" && (
            <>
              <PageHeading title="Analyze a Suspicious Message" subtitle="Paste suspicious SMS, WhatsApp, or email text to check for known fraud indicators." />
              <section className="panel analyzer-panel">
                <div className="panel-heading"><div><div className="eyebrow"><ShieldCheck size={15} />MESSAGE SECURITY CHECK</div><h2>Message Analysis</h2><p>Analysis is based on known fraud patterns and keyword indicators.</p></div></div>
                <form onSubmit={handleAnalyze}>
                  <label htmlFor="message-input">Message content</label>
                  <textarea id="message-input" value={message} onChange={(event) => setMessage(event.target.value)} placeholder="Example: Your bank account will be blocked today. Share your OTP immediately..." rows={6} maxLength={10000} />
                  <div className="analyzer-actions"><span>{message.length}/10000 characters</span><button type="submit" className="primary-button" disabled={analyzing}>{analyzing ? "Analyzing..." : <><Search size={18} />Analyze Message</>}</button></div>
                </form>
                {analysis && <AnalysisResult analysis={analysis} />}
              </section>
            </>
          )}

          {activePage === "Fraud Cases" && (
            <>
              <PageHeading title="Fraud Cases Library" subtitle="Browse known cyber-fraud patterns, warning signs, and prevention guidance." action={<button className="secondary-button" onClick={loadFraudCases}><RefreshCw size={14} /> Refresh</button>} />
              <section className="panel">
                <div className="page-toolbar"><label htmlFor="case-search">Search fraud cases</label><input id="case-search" value={caseSearch} onChange={(event) => setCaseSearch(event.target.value)} placeholder="Search name, category or description..." /></div>
                {loadingPage ? <EmptyState text="Loading fraud cases..." /> : visibleCases.length ? <div className="case-grid">
                  {visibleCases.map((item) => <article className="case-card" key={item.id}>
                    <div className="case-card-top"><span className="case-category">{item.category}</span><RiskBadge level={item.risk_level} /></div>
                    <h3>{item.name}</h3><p>{item.description}</p>
                    {item.keywords && <div className="case-detail"><strong>Indicators / keywords</strong><p>{item.keywords}</p></div>}
                    {item.warning_signs && <div className="case-detail"><strong>Warning signs</strong><p>{item.warning_signs}</p></div>}
                    {item.prevention && <div className="case-detail"><strong>Prevention</strong><p>{item.prevention}</p></div>}
                    {item.what_to_do && <div className="case-detail"><strong>What to do</strong><p>{item.what_to_do}</p></div>}
                  </article>)}
                </div> : <EmptyState text="No fraud cases found. Check that fraud data has been seeded into the database." />}
              </section>
            </>
          )}

          {activePage === "History" && (
            <>
              <PageHeading title="Analysis History" subtitle="Review previously analyzed messages, detected patterns, risk levels, and timestamps." action={<button className="secondary-button" onClick={loadHistory}><RefreshCw size={14} /> Refresh</button>} />
              <section className="panel">
                <div className="history-filters">
                  <div><label htmlFor="history-search">Search history</label><input id="history-search" value={historySearch} onChange={(event) => { setHistoryPage(1); setHistorySearch(event.target.value); }} placeholder="Search message or fraud..." /></div>
                  <div><label htmlFor="history-risk">Risk level</label><select id="history-risk" value={historyRisk} onChange={(event) => { setHistoryPage(1); setHistoryRisk(event.target.value); }}><option value="">All levels</option><option>Critical</option><option>High</option><option>Medium</option><option>Low</option></select></div>
                </div>
                {loadingPage ? <EmptyState text="Loading analysis history..." /> : historyRecords.length ? <>
                  <div className="table-wrapper"><table><thead><tr><th>Message</th><th>Detected Fraud</th><th>Risk</th><th>Score</th><th>Confidence</th><th>Date (IST)</th></tr></thead><tbody>
                    {historyRecords.map((item) => <tr key={item.id}><td className="message-cell">{item.message}</td><td>{item.matched_fraud || "Not identified"}</td><td><RiskBadge level={item.risk_level} /></td><td>{item.score}</td><td>{item.confidence}%</td><td>{formatDate(item.created_at)}</td></tr>)}
                  </tbody></table></div>
                  <div className="pagination"><span>{historyTotal} record(s) · Page {historyPage} of {totalPages}</span><div><button className="secondary-button" disabled={historyPage <= 1} onClick={() => setHistoryPage((page) => Math.max(1, page - 1))}>Previous</button><button className="secondary-button" disabled={historyPage >= totalPages} onClick={() => setHistoryPage((page) => Math.min(totalPages, page + 1))}>Next</button></div></div>
                </> : <EmptyState text="No analysis history found. Analyze a message to create the first record." />}
              </section>
            </>
          )}

          {activePage === "Analytics" && (
            <>
              <PageHeading title="Security Analytics" subtitle="Explore fraud detection trends and risk levels from saved message analyses." action={<button className="secondary-button" onClick={loadDashboard}><RefreshCw size={14} /> Refresh analytics</button>} />
              <StatsGrid cards={statCards} />
              <ChartsGrid fraudData={fraudData} riskData={riskData} />
              <section className="panel"><div className="panel-heading"><div><h2>Risk Summary</h2><p>Count of saved analyses in each risk category</p></div></div>
                {riskData.length ? <div className="analytics-risk-list">{riskData.map((item) => <div className="analytics-risk-row" key={item.risk_level}><span className="legend-dot" style={{ backgroundColor: riskColors[item.risk_level] || "#64748b" }} /><strong>{item.risk_level}</strong><div className="analytics-track"><span style={{ width: `${Math.max(0, Math.min(100, (item.count / Math.max(1, ...riskData.map((x) => x.count))) * 100))}%`, backgroundColor: riskColors[item.risk_level] || "#64748b" }} /></div><b>{item.count}</b></div>)}</div> : <EmptyState text="Analytics will appear after messages have been analyzed." />}
              </section>
            </>
          )}

          {activePage === "Settings" && (
            <>
              <PageHeading title="Settings" subtitle="Basic application and safety information." />
              <section className="panel settings-panel"><h2>CyberRakshak AI</h2><p>This project screens submitted messages for known fraud indicators and provides safety guidance. It does not contact banks or law-enforcement agencies.</p><div className="settings-note"><ShieldCheck size={20} /><span>Never share OTPs, UPI PINs, passwords, or remote access to your device. If money has been lost to cyber fraud in India, contact your bank and report promptly through official channels such as helpline 1930.</span></div></section>
            </>
          )}

          <footer className="page-footer"><span><ShieldCheck size={16} />CyberRakshak AI</span><span>Stay alert. Verify before you trust.</span></footer>
        </div>
      </main>
    </div>
  );
}

function PageHeading({ title, subtitle, action }) {
  return <section className="welcome-section"><div><div className="eyebrow"><ShieldCheck size={15} />YOUR DIGITAL SAFETY COMPANION</div><h1>{title}</h1><p>{subtitle}</p></div>{action}</section>;
}

function StatsGrid({ cards }) {
  return <section className="stats-grid">{cards.map(({ title, value, icon: Icon, color }) => <article className="stat-card" key={title}><div className="stat-top"><span className="stat-title">{title}</span><div className={`stat-icon ${color}`}><Icon size={21} /></div></div><div className="stat-value">{value}</div><div className="stat-description">Based on saved analysis history</div></article>)}</section>;
}

function ChartsGrid({ fraudData, riskData }) {
  return <section className="charts-grid">
    <article className="panel"><div className="panel-heading"><div><h2>Fraud Distribution</h2><p>Most frequently detected fraud patterns</p></div><div className="heading-icon"><BarChart3 size={19} /></div></div>
      {fraudData.length ? <ResponsiveContainer width="100%" height={280}><BarChart data={fraudData.slice(0, 8)} margin={{ top: 12, right: 8, left: -18, bottom: 50 }}><CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e9eef5" /><XAxis dataKey="fraud_name" interval={0} angle={-25} textAnchor="end" tick={{ fontSize: 10, fill: "#64748b" }} /><YAxis allowDecimals={false} tick={{ fontSize: 11, fill: "#64748b" }} /><Tooltip /><Bar dataKey="count" name="Detections" fill="#0d9488" radius={[5, 5, 0, 0]} /></BarChart></ResponsiveContainer> : <EmptyState text="No fraud detection data available yet." />}
    </article>
    <article className="panel"><div className="panel-heading"><div><h2>Risk Distribution</h2><p>Risk levels across analyzed messages</p></div><div className="heading-icon"><ShieldAlert size={19} /></div></div>
      {riskData.length ? <><ResponsiveContainer width="100%" height={210}><PieChart><Pie data={riskData.map((item) => ({ ...item, fill: riskColors[item.risk_level] || "#64748b" }))} dataKey="count" nameKey="risk_level" cx="50%" cy="50%" innerRadius={55} outerRadius={82} paddingAngle={3}>{riskData.map((item) => <Cell key={item.risk_level} fill={riskColors[item.risk_level] || "#64748b"} />)}</Pie><Tooltip /></PieChart></ResponsiveContainer><div className="risk-legend">{riskData.map((item) => <div className="risk-legend-item" key={item.risk_level}><span className="legend-dot" style={{ backgroundColor: riskColors[item.risk_level] || "#64748b" }} /><span>{item.risk_level}</span><strong>{item.count}</strong></div>)}</div></> : <EmptyState text="Risk distribution will appear after analyses are saved." />}
    </article>
  </section>;
}

function ActivityTable({ activities, onRefresh }) {
  return <section className="panel activity-panel"><div className="panel-heading"><div><h2>Recent Activity</h2><p>Your latest message analysis records</p></div><button className="secondary-button" onClick={onRefresh}><RefreshCw size={14} /> Refresh</button></div>
    {activities.length ? <div className="table-wrapper"><table><thead><tr><th>Message</th><th>Detected Fraud</th><th>Risk Level</th><th>Date (IST)</th></tr></thead><tbody>{activities.map((item) => <tr key={item.id}><td className="message-cell">{item.message}</td><td>{item.matched_fraud || "Not identified"}</td><td><RiskBadge level={item.risk_level} /></td><td>{formatDate(item.created_at)}</td></tr>)}</tbody></table></div> : <EmptyState text="No analysis history available yet." />}
  </section>;
}

function AnalysisResult({ analysis }) {
  return <div className={`analysis-result ${analysis.is_suspicious ? "result-warning" : "result-safe"}`} aria-live="polite">
    <div className="result-header">{analysis.is_suspicious ? <AlertTriangle size={23} /> : <ShieldCheck size={23} />}<div><h3>{analysis.is_suspicious ? "Potential Fraud Indicators Detected" : "No Significant Fraud Indicators Detected"}</h3><p>Risk level: <strong>{analysis.risk_level}</strong></p></div></div>
    <div className="result-metrics"><div><span>Confidence</span><strong>{analysis.confidence}%</strong></div><div><span>Risk score</span><strong>{analysis.score}</strong></div><div><span>Possible fraud</span><strong>{analysis.matched_fraud || "Not identified"}</strong></div></div>
    <p className="result-summary">{analysis.analysis_summary}</p>
    {analysis.matched_keywords?.length > 0 && <div className="matched-keywords"><strong>Matched indicators:</strong>{analysis.matched_keywords.map((keyword) => <span key={keyword}>{keyword}</span>)}</div>}
    {analysis.warning_signs && <div className="advice-block"><strong>Warning signs</strong><p>{analysis.warning_signs}</p></div>}
    {analysis.prevention && <div className="advice-block"><strong>Prevention</strong><p>{analysis.prevention}</p></div>}
    {analysis.what_to_do && <div className="advice-block"><strong>What to do next</strong><p>{analysis.what_to_do}</p></div>}
    <p className="disclaimer">This is an automated screening result, not a guarantee that a message is safe or fraudulent. Never share OTPs, PINs, or passwords.</p>
  </div>;
}

export default App;
