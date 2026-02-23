import React, { useEffect, useState, useCallback } from 'react';
import { useAuth } from '../../context/AuthContext';
import { dashboardAPI } from '../../utils/api';
import SummaryCards from '../../components/dashboard/SummaryCards';
import DashboardCharts from '../../components/dashboard/DashboardCharts';
import ChildrenTable from '../../components/dashboard/ChildrenTable';
import InterventionsTable from '../../components/dashboard/InterventionsTable';
import UsersTable from '../../components/dashboard/UsersTable';
import ChildGrowthChart from '../../components/dashboard/ChildGrowthChart';

const StateAdminDashboard = () => {
    const { user } = useAuth();

    // Filters
    const [districts, setDistricts] = useState([]);
    const [mandals, setMandals] = useState([]);
    const [selectedDistrict, setSelectedDistrict] = useState('');
    const [selectedMandal, setSelectedMandal] = useState('');

    // Data
    const [summary, setSummary] = useState({});
    const [children, setChildren] = useState([]);
    const [interventions, setInterventions] = useState([]);
    const [users, setUsers] = useState([]);
    const [charts, setCharts] = useState({});

    const [loading, setLoading] = useState(true);
    const [tab, setTab] = useState('analytics');

    // Load districts on mount
    useEffect(() => {
        dashboardAPI.getDistrictsForState()
            .then(res => setDistricts(res.data))
            .catch(err => console.error("Error fetching districts:", err));
    }, []);

    // Load mandals when district changes
    useEffect(() => {
        if (selectedDistrict) {
            dashboardAPI.getMandals(selectedDistrict)
                .then(res => setMandals(res.data))
                .catch(err => console.error("Error fetching mandals:", err));
        } else {
            setMandals([]);
            setSelectedMandal('');
        }
    }, [selectedDistrict]);

    const fetchData = useCallback(async () => {
        setLoading(true);
        const params = {
            district_id: selectedDistrict || undefined,
            mandal_id: selectedMandal || undefined
        };

        try {
            const [s, c, i, u, ch] = await Promise.all([
                dashboardAPI.getSummary(params),
                dashboardAPI.getChildren(params),
                dashboardAPI.getInterventions(params),
                dashboardAPI.getUsers(params),
                dashboardAPI.getCharts(params),
            ]);
            setSummary(s.data || {});
            setChildren(c.data || []);
            setInterventions(i.data || []);
            setUsers(u.data || []);
            setCharts(ch.data || {});
        } catch (err) {
            console.error("Error fetching dashboard data:", err);
        } finally {
            setLoading(false);
        }
    }, [selectedDistrict, selectedMandal]);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    const handleReset = () => {
        setSelectedDistrict('');
        setSelectedMandal('');
    };

    if (loading && !summary.total_children) return (
        <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600" />
        </div>
    );

    const tabs = [
        { id: 'analytics', label: '📊 Analytics' },
        { id: 'children', label: '👶 Children' },
        { id: 'interventions', label: '🏥 Interventions' },
        { id: 'staff', label: '👥 Users & Staff' },
        { id: 'growth', label: '📈 Growth' },
    ];

    const currentScopeLabel = selectedMandal
        ? mandals.find(m => m.mandal_id === parseInt(selectedMandal))?.mandal_name
        : selectedDistrict
            ? districts.find(d => d.district_id === parseInt(selectedDistrict))?.district_name
            : "Entire State";

    return (
        <div className="p-6 space-y-6">
            {/* Header & Global Filters */}
            <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">State Admin Dashboard</h1>
                    <p className="text-sm text-gray-500 mt-1">
                        Welcome, {user?.full_name} — Viewing scope: <span className="font-semibold text-blue-600">{currentScopeLabel}</span>
                    </p>
                </div>

                <div className="flex flex-wrap items-center gap-4">
                    <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-2 text-sm text-red-700 font-medium whitespace-nowrap">
                        System Administration
                    </div>
                    <div className="flex flex-wrap items-center gap-3">
                        <select
                            value={selectedDistrict}
                            onChange={(e) => {
                                setSelectedDistrict(e.target.value);
                                setSelectedMandal('');
                            }}
                            className="text-sm border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 shadow-sm"
                        >
                            <option value="">All Districts</option>
                            {districts.map(d => (
                                <option key={d.district_id} value={d.district_id}>{d.district_name}</option>
                            ))}
                        </select>

                        <select
                            value={selectedMandal}
                            onChange={(e) => setSelectedMandal(e.target.value)}
                            disabled={!selectedDistrict}
                            className="text-sm border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 shadow-sm disabled:bg-gray-50"
                        >
                            <option value="">All Mandals</option>
                            {mandals.map(m => (
                                <option key={m.mandal_id} value={m.mandal_id}>{m.mandal_name}</option>
                            ))}
                        </select>

                        {(selectedDistrict || selectedMandal) && (
                            <button
                                onClick={handleReset}
                                className="text-sm text-gray-500 hover:text-blue-600 font-medium px-2 py-1"
                            >
                                Reset
                            </button>
                        )}
                    </div>
                </div>
            </div>

            <SummaryCards
                data={summary}
                keys={['total_children', 'active_children', 'total_interventions', 'total_assessments', 'total_centers']}
            />

            {/* System health bar */}
            <div className="bg-gradient-to-r from-gray-900 to-gray-800 rounded-xl p-5 text-white flex flex-wrap items-center justify-between gap-4">
                <div>
                    <p className="text-sm text-gray-400">System Status</p>
                    <p className="text-lg font-bold mt-0.5">All Systems Operational</p>
                </div>
                <div className="text-right">
                    <p className="text-sm text-gray-400">Scope</p>
                    <p className="font-medium text-blue-300">{currentScopeLabel}</p>
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

            <div className="border-b border-gray-200">
                <nav className="flex gap-1 flex-wrap">
                    {tabs.map(t => (
                        <button
                            key={t.id}
                            onClick={() => setTab(t.id)}
                            className={`px-4 py-2.5 text-sm font-medium rounded-t-lg transition-colors ${tab === t.id
                                    ? 'bg-blue-600 text-white shadow-sm'
                                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                                }`}
                        >
                            {t.label}
                        </button>
                    ))}
                </nav>
            </div>

            <div className="mt-6">
                {tab === 'analytics' && <DashboardCharts data={charts} />}
                {tab === 'children' && <ChildrenTable data={children} />}
                {tab === 'interventions' && <InterventionsTable data={interventions} />}
                {tab === 'staff' && <UsersTable data={users} />}
                {tab === 'growth' && <ChildGrowthChart children={children} />}
            </div>
        </div>
    );
};

export default StateAdminDashboard;
