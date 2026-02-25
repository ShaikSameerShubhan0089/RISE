import React, { useEffect, useState, useCallback } from 'react';
import { useAuth } from '../../context/AuthContext';
import { dashboardAPI } from '../../utils/api';
import SummaryCards from '../../components/dashboard/SummaryCards';
import DashboardCharts from '../../components/dashboard/DashboardCharts';
import ChildrenTable from '../../components/dashboard/ChildrenTable';
import InterventionsTable from '../../components/dashboard/InterventionsTable';
import UsersTable from '../../components/dashboard/UsersTable';
import ChildGrowthChart from '../../components/dashboard/ChildGrowthChart';
import { ShieldCheck } from 'lucide-react';
import VoiceButton from '../../components/common/VoiceButton';
import { useLanguage } from '../../context/LanguageContext';

const SystemAdminDashboard = () => {
    const { user } = useAuth();
    const { t } = useLanguage();

    // ── Location filter state ──────────────────────────────────────────────
    const [districts, setDistricts] = useState([]);
    const [mandals, setMandals] = useState([]);
    const [selectedDistrict, setSelectedDistrict] = useState('');   // district_id as string
    const [selectedMandal, setSelectedMandal] = useState('');       // mandal_id as string
    const [districtsLoading, setDistrictsLoading] = useState(true);

    // ── Dashboard data state ───────────────────────────────────────────────
    const [summary, setSummary] = useState({});
    const [children, setChildren] = useState([]);
    const [interventions, setInterventions] = useState([]);
    const [users, setUsers] = useState([]);
    const [charts, setCharts] = useState({});
    const [dataLoading, setDataLoading] = useState(false);
    const [dataLoaded, setDataLoaded] = useState(false);   // true once any district is selected

    const [tab, setTab] = useState('charts');

    // ── Load district list on mount ────────────────────────────────────────
    useEffect(() => {
        dashboardAPI.getDistricts()
            .then(r => setDistricts(r.data))
            .catch(() => { })
            .finally(() => setDistrictsLoading(false));
    }, []);

    // ── Fetch all dashboard data for the current filter ───────────────────
    const loadData = useCallback((districtId, mandalId) => {
        const params = {};
        if (districtId) params.district_id = districtId;
        if (mandalId) params.mandal_id = mandalId;

        setDataLoading(true);
        Promise.all([
            dashboardAPI.getSummary(params),
            dashboardAPI.getChildren(params),
            dashboardAPI.getInterventions(params),
            dashboardAPI.getUsers(params),
            dashboardAPI.getCharts(params),
        ]).then(([s, c, i, u, ch]) => {
            setSummary(s.data);
            setChildren(c.data);
            setInterventions(i.data);
            setUsers(u.data);
            setCharts(ch.data);
            setDataLoaded(true);
        }).catch(() => { })
            .finally(() => setDataLoading(false));
    }, []);

    // ── District change handler ────────────────────────────────────────────
    const handleDistrictChange = (e) => {
        const distId = e.target.value;
        setSelectedDistrict(distId);
        setSelectedMandal('');
        setMandals([]);

        if (!distId) {
            // "All Districts" — reset to global view
            loadData('', '');
            return;
        }

        // Load mandals for the chosen district
        dashboardAPI.getMandals(distId)
            .then(r => setMandals(r.data))
            .catch(() => { });

        loadData(distId, '');
    };

    // ── Mandal change handler ──────────────────────────────────────────────
    const handleMandalChange = (e) => {
        const mandalId = e.target.value;
        setSelectedMandal(mandalId);
        loadData(selectedDistrict, mandalId);
    };

    const getPageSummary = () => {
        const scope = selectedMandal
            ? mandals.find(m => String(m.mandal_id) === selectedMandal)?.mandal_name
            : selectedDistrict
                ? districts.find(d => String(d.district_id) === selectedDistrict)?.district_name
                : "the global System";

        let text = t('parent.narration.admin_hello')
            .replace('{name}', user?.full_name || '')
            .replace('{role}', t('user_mgmt.roles.system_admin'))
            .replace('{scope}', scope);

        // System-wide Metrics
        text += " " + t('parent.narration.metric_card')
            .replace('{label}', t('analytics.metrics.total_children'))
            .replace('{value}', summary.total_children || 0);
        text += " " + t('parent.narration.metric_card')
            .replace('{label}', t('analytics.metrics.active_users'))
            .replace('{value}', summary.active_users || 0);

        if (summary.risk_distribution) {
            text += " " + t('parent.narration.risk_distribution')
                .replace('{high}', summary.risk_distribution.high || 0)
                .replace('{moderate}', (summary.risk_distribution.moderate || 0) + (summary.risk_distribution.mild || 0))
                .replace('{low}', summary.risk_distribution.low || 0);
        }

        // Role Distribution
        const roleCounts = users.reduce((acc, u) => {
            acc[u.role] = (acc[u.role] || 0) + 1;
            return acc;
        }, {});

        if (Object.keys(roleCounts).length > 0) {
            text += " " + t('parent.narration.ranking_intro');
            Object.entries(roleCounts).forEach(([role, count]) => {
                const roleLabel = t(`user_mgmt.roles.${role}`) || role;
                text += ` ${roleLabel}: ${count} total users.`;
            });
        }

        // System Health Audit Detail
        text += " " + t('parent.narration.system_audit')
            .replace('{api}', 'v1.0')
            .replace('{api_status}', 'Healthy')
            .replace('{db}', 'PostgreSQL')
            .replace('{db_status}', 'Connected');

        return text;
    };

    // ── Reset handler ──────────────────────────────────────────────────────
    const handleReset = () => {
        setSelectedDistrict('');
        setSelectedMandal('');
        setMandals([]);
        setDataLoaded(false);
        setSummary({});
        setChildren([]);
        setInterventions([]);
        setUsers([]);
        setCharts({});
    };

    // ── Derive label for system-status bar ────────────────────────────────
    const scopeLabel = (() => {
        if (!selectedDistrict) return 'All Districts';
        const d = districts.find(d => String(d.district_id) === selectedDistrict);
        const dName = d?.district_name || 'District';
        if (!selectedMandal) return dName;
        const m = mandals.find(m => String(m.mandal_id) === selectedMandal);
        return `${dName} › ${m?.mandal_name || 'Mandal'}`;
    })();

    const tabs = [
        { id: 'charts', label: '📊 Analytics' },
        { id: 'children', label: '👶 Children' },
        { id: 'interventions', label: '🏥 Interventions' },
        { id: 'users', label: '👥 All Users' },
        { id: 'growth', label: '📈 Growth' },
    ];

    return (
        <div className="p-6 space-y-6">

            {/* ── Header ───────────────────────────────────────────────── */}
            <div className="flex items-center gap-4">
                <div className="p-3 bg-red-100 rounded-2xl">
                    <ShieldCheck className="w-8 h-8 text-red-600" />
                </div>
                <div>
                    <div className="flex items-center gap-3">
                        <h1 className="text-2xl font-bold text-gray-900">System Admin Dashboard</h1>
                        <VoiceButton
                            content={getPageSummary()}
                            className="bg-red-600 text-white shadow-lg hover:bg-red-700"
                        />
                    </div>
                    <p className="text-sm text-gray-500 mt-1">
                        Welcome, {user?.full_name} — {scopeLabel}
                    </p>
                </div>
            </div>
            <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-2 text-sm text-red-700 font-medium">
                ⚡ System Administration
            </div>
            <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
                <div className="flex flex-wrap items-end gap-4">

                    {/* District selector */}
                    <div className="flex flex-col gap-1 min-w-[220px]">
                        <label htmlFor="districtSelect" className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                            District
                        </label>
                        <select
                            id="districtSelect"
                            value={selectedDistrict}
                            onChange={handleDistrictChange}
                            disabled={districtsLoading}
                            className="border border-gray-300 rounded-lg px-3 py-2 text-sm text-gray-800 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                        >
                            <option value="">— Select District —</option>
                            {districts.map(d => (
                                <option key={d.district_id} value={d.district_id}>
                                    {d.district_name}
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* Mandal selector (visible only after district chosen) */}
                    {selectedDistrict && (
                        <div className="flex flex-col gap-1 min-w-[220px]">
                            <label htmlFor="mandalSelect" className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                                Mandal <span className="text-gray-400 font-normal">(optional)</span>
                            </label>
                            <select
                                id="mandalSelect"
                                value={selectedMandal}
                                onChange={handleMandalChange}
                                className="border border-gray-300 rounded-lg px-3 py-2 text-sm text-gray-800 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="">— All Mandals —</option>
                                {mandals.map(m => (
                                    <option key={m.mandal_id} value={m.mandal_id}>
                                        {m.mandal_name}
                                    </option>
                                ))}
                            </select>
                        </div>
                    )}

                    {/* Reset button */}
                    {dataLoaded && (
                        <button
                            onClick={handleReset}
                            className="px-4 py-2 text-sm font-medium text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                        >
                            🔄 Reset
                        </button>
                    )}

                    {/* Loading indicator */}
                    {dataLoading && (
                        <div className="flex items-center gap-2 text-sm text-blue-600">
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600" />
                            Loading data…
                        </div>
                    )}
                </div>
            </div>

            {/* ── Empty state ───────────────────────────────────────────── */}
            {
                !dataLoaded && !dataLoading && (
                    <div className="rounded-xl border-2 border-dashed border-gray-200 bg-gray-50 py-20 text-center">
                        <span className="text-5xl">🗺️</span>
                        <h2 className="mt-4 text-lg font-semibold text-gray-700">Select a district to view data</h2>
                        <p className="mt-1 text-sm text-gray-500">
                            Use the <strong>District</strong> dropdown above to load children, interventions, and analytics for that district.
                        </p>
                    </div>
                )
            }

            {/* ── Dashboard content (shown only once a district is loaded) ── */}
            {
                dataLoaded && (
                    <>
                        <SummaryCards data={summary} />

                        {/* System health bar */}
                        <div className="bg-gradient-to-r from-gray-900 to-gray-800 rounded-xl p-5 text-white flex flex-wrap items-center justify-between gap-4">
                            <div>
                                <p className="text-sm text-gray-400">System Status</p>
                                <p className="text-lg font-bold mt-0.5">✅ All Systems Operational</p>
                            </div>
                            <div className="text-right">
                                <p className="text-sm text-gray-400">Scope</p>
                                <p className="font-medium text-blue-300">{scopeLabel}</p>
                            </div>
                            <div className="text-right">
                                <p className="text-sm text-gray-400">Backend API</p>
                                <p className="font-medium text-green-400">localhost:8000 — Running</p>
                            </div>
                            <div className="text-right">
                                <p className="text-sm text-gray-400">Database</p>
                                <p className="font-medium text-green-400">PostgreSQL — Connected</p>
                            </div>
                        </div>

                        {/* Tabs */}
                        <div className="border-b border-gray-200">
                            <nav className="flex gap-1">
                                {tabs.map(t => (
                                    <button
                                        key={t.id}
                                        onClick={() => setTab(t.id)}
                                        className={`px-4 py-2.5 text-sm font-medium rounded-t-lg transition-colors ${tab === t.id
                                            ? 'bg-blue-600 text-white'
                                            : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                                            }`}
                                    >
                                        {t.label}
                                    </button>
                                ))}
                            </nav>
                        </div>

                        {tab === 'charts' && <DashboardCharts data={charts} />}
                        {tab === 'children' && <ChildrenTable data={children} />}
                        {tab === 'interventions' && <InterventionsTable data={interventions} />}
                        {tab === 'users' && <UsersTable data={users} />}
                        {tab === 'growth' && <ChildGrowthChart children={children} />}
                    </>
                )
            }
        </div >
    );
};

export default SystemAdminDashboard;
