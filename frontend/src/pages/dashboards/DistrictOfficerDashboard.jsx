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

const DistrictOfficerDashboard = () => {
    const { user } = useAuth();

    // ── Filter state ────────────────────────────────────────────────────────
    const [mandals, setMandals] = useState([]);
    const [selectedMandal, setSelectedMandal] = useState('');
    const [mandalsLoading, setMandalsLoading] = useState(true);

    // ── Dashboard data ───────────────────────────────────────────────────────
    const [summary, setSummary] = useState({});
    const [children, setChildren] = useState([]);
    const [interventions, setInterventions] = useState([]);
    const [users, setUsers] = useState([]);
    const [charts, setCharts] = useState({});
    const [dataLoading, setDataLoading] = useState(true);

    const [tab, setTab] = useState('charts');

    // ── Load mandal list on mount ────────────────────────────────────────────
    useEffect(() => {
        dashboardAPI.getMandalsForDistrict()
            .then(r => setMandals(r.data))
            .catch(() => { })
            .finally(() => setMandalsLoading(false));
    }, []);

    // ── Fetch dashboard data ─────────────────────────────────────────────────
    const loadData = useCallback((mandalId) => {
        const params = {};
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
        }).catch(() => { })
            .finally(() => setDataLoading(false));
    }, []);

    // Load all district data on mount
    useEffect(() => { loadData(''); }, [loadData]);

    const handleMandalChange = (e) => {
        const mid = e.target.value;
        setSelectedMandal(mid);
        loadData(mid);
    };

    const handleReset = () => {
        setSelectedMandal('');
        loadData('');
    };

    const scopeLabel = mandals.find(m => String(m.mandal_id) === selectedMandal)?.mandal_name || 'All Mandals';

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
                    <h1 className="text-2xl font-bold text-gray-900">District Officer Dashboard</h1>
                    <p className="text-sm text-gray-500 mt-1">
                        Welcome, <span className="font-medium">{user?.full_name}</span>
                        {' '}— <span className="text-blue-600 font-medium">{scopeLabel}</span>
                    </p>
                </div>
            </div>

            {/* Mandal filter bar */}
            <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
                <div className="flex flex-wrap items-end gap-4">
                    <div className="flex flex-col gap-1 min-w-[220px]">
                        <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                            Filter by Mandal
                        </label>
                        {mandalsLoading ? (
                            <div className="h-9 bg-gray-100 rounded-lg animate-pulse" />
                        ) : (
                            <select
                                value={selectedMandal}
                                onChange={handleMandalChange}
                                className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="">All Mandals</option>
                                {mandals.map(m => (
                                    <option key={m.mandal_id} value={m.mandal_id}>{m.mandal_name}</option>
                                ))}
                            </select>
                        )}
                    </div>
                    {selectedMandal && (
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

export default DistrictOfficerDashboard;
