import React, { useEffect, useState, useCallback } from 'react';
import { useAuth } from '../../context/AuthContext';
import { dashboardAPI } from '../../utils/api';
import SummaryCards from '../../components/dashboard/SummaryCards';
import DashboardCharts from '../../components/dashboard/DashboardCharts';
import ChildrenTable from '../../components/dashboard/ChildrenTable';
import InterventionsTable from '../../components/dashboard/InterventionsTable';
import UsersTable from '../../components/dashboard/UsersTable';
import ChildGrowthChart from '../../components/dashboard/ChildGrowthChart';
import { RefreshCw } from 'lucide-react';

const SupervisorDashboard = () => {
    const { user } = useAuth();

    // ── Filter state ─────────────────────────────────────────────────────────
    const [centers, setCenters] = useState([]);
    const [selectedCenter, setSelectedCenter] = useState('');
    const [centersLoading, setCentersLoading] = useState(true);

    // ── Dashboard data ────────────────────────────────────────────────────────
    const [summary, setSummary] = useState({});
    const [children, setChildren] = useState([]);
    const [interventions, setInterventions] = useState([]);
    const [users, setUsers] = useState([]);
    const [charts, setCharts] = useState({});
    const [dataLoading, setDataLoading] = useState(true);

    const [tab, setTab] = useState('charts');

    // ── Load center list on mount ─────────────────────────────────────────────
    useEffect(() => {
        dashboardAPI.getCentersForMandal()
            .then(r => setCenters(r.data))
            .catch(() => { })
            .finally(() => setCentersLoading(false));
    }, []);

    // ── Fetch dashboard data ──────────────────────────────────────────────────
    const loadData = useCallback((centerId) => {
        const params = {};
        if (centerId) params.center_id = centerId;
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
        }).catch(() => { })
            .finally(() => setDataLoading(false));
    }, []);

    // Load all mandal data on mount
    useEffect(() => { loadData(''); }, [loadData]);

    const handleCenterChange = (e) => {
        const cid = e.target.value;
        setSelectedCenter(cid);
        loadData(cid);
    };

    const handleReset = () => {
        setSelectedCenter('');
        loadData('');
    };

    const scopeLabel = centers.find(c => String(c.center_id) === selectedCenter)?.center_name || 'All Centers';

    const tabs = [
        { id: 'charts', label: '📊 Analytics' },
        { id: 'children', label: '👶 Children' },
        { id: 'interventions', label: '🏥 Interventions' },
        { id: 'staff', label: '👥 Staff' },
        { id: 'growth', label: '📈 Growth' },
    ];

    return (
        <div className="p-6 space-y-6">
            {/* Header */}
            <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Supervisor Dashboard</h1>
                    <p className="text-sm text-gray-500 mt-1">
                        Welcome, <span className="font-medium">{user?.full_name}</span>
                        {' '}— <span className="text-blue-600 font-medium">{scopeLabel}</span>
                    </p>
                </div>
            </div>

            {/* AWC Center filter bar */}
            <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
                <div className="flex flex-wrap items-end gap-4">
                    <div className="flex flex-col gap-1 min-w-[240px]">
                        <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                            Filter by AWC Center
                        </label>
                        {centersLoading ? (
                            <div className="h-9 bg-gray-100 rounded-lg animate-pulse" />
                        ) : (
                            <select
                                value={selectedCenter}
                                onChange={handleCenterChange}
                                className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="">All Centers (Whole Mandal)</option>
                                {centers.map(c => (
                                    <option key={c.center_id} value={c.center_id}>
                                        {c.center_name} ({c.center_code})
                                    </option>
                                ))}
                            </select>
                        )}
                    </div>
                    {selectedCenter && (
                        <button
                            onClick={handleReset}
                            className="flex items-center gap-1.5 px-3 py-2 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                        >
                            <RefreshCw className="w-3.5 h-3.5" /> Reset
                        </button>
                    )}
                    {dataLoading && (
                        <div className="flex items-center gap-2 text-blue-600 text-sm">
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600" />
                            Loading…
                        </div>
                    )}
                    {/* Center count badge */}
                    {!centersLoading && centers.length > 0 && (
                        <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                            {centers.length} centers in your mandal
                        </span>
                    )}
                </div>
            </div>

            {/* Summary cards */}
            <SummaryCards data={summary} />

            {/* Tabs */}
            <div className="border-b border-gray-200">
                <nav className="flex gap-1">
                    {tabs.map(t => (
                        <button
                            key={t.id}
                            onClick={() => setTab(t.id)}
                            className={`px-4 py-2.5 text-sm font-medium rounded-t-lg transition-colors ${tab === t.id ? 'bg-blue-600 text-white' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                                }`}
                        >
                            {t.label}
                        </button>
                    ))}
                </nav>
            </div>

            {/* Tab content */}
            <div>
                {tab === 'charts' && <DashboardCharts data={charts} />}
                {tab === 'children' && <ChildrenTable data={children} />}
                {tab === 'interventions' && <InterventionsTable data={interventions} />}
                {tab === 'staff' && <UsersTable data={users} />}
                {tab === 'growth' && <ChildGrowthChart children={children} />}
            </div>
        </div>
    );
};

export default SupervisorDashboard;
