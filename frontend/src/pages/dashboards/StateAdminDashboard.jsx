import React, { useEffect, useState, useCallback } from 'react';
import { useAuth } from '../../context/AuthContext';
import { dashboardAPI } from '../../utils/api';
import SummaryCards from '../../components/dashboard/SummaryCards';
import DashboardCharts from '../../components/dashboard/DashboardCharts';
import ChildrenTable from '../../components/dashboard/ChildrenTable';
import InterventionsTable from '../../components/dashboard/InterventionsTable';
import UsersTable from '../../components/dashboard/UsersTable';
import ChildGrowthChart from '../../components/dashboard/ChildGrowthChart';
import { Globe } from 'lucide-react';
import VoiceButton from '../../components/common/VoiceButton';
import { useLanguage } from '../../context/LanguageContext';

const StateAdminDashboard = () => {
    const { user } = useAuth();
    const { t } = useLanguage();

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

    const getPageSummary = () => {
        const scope = selectedMandal
            ? mandals.find(m => m.mandal_id === parseInt(selectedMandal))?.mandal_name
            : selectedDistrict
                ? districts.find(d => d.district_id === parseInt(selectedDistrict))?.district_name
                : "the entire State";

        let text = t('parent.narration.admin_hello')
            .replace('{name}', user?.full_name || '')
            .replace('{role}', t('user_mgmt.roles.state_admin'))
            .replace('{scope}', scope);

        // State-wide Metrics
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

        // District Performance Summary
        const districtScores = (charts?.district_performance || [])
            .sort((a, b) => b.registration_count - a.registration_count);

        if (districtScores.length > 0) {
            text += " " + t('parent.narration.ranking_intro');
            districtScores.slice(0, 3).forEach(d => {
                text += " " + t('parent.narration.performance_item')
                    .replace('{name}', d.district_name)
                    .replace('{count}', d.registration_count);
            });
        }

        return text;
    };

    const handleReset = () => {
        setSelectedDistrict('');
        setSelectedMandal('');
    };

    const currentScopeLabel = selectedMandal
        ? mandals.find(m => m.mandal_id === parseInt(selectedMandal))?.mandal_name
        : selectedDistrict
            ? districts.find(d => d.district_id === parseInt(selectedDistrict))?.district_name
            : "Entire State";

    return (
        <div className="p-6 space-y-6">
            {/* Header & Global Filters */}
            <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                <div className="flex items-center gap-4">
                    <div className="p-3 bg-blue-50 rounded-2xl">
                        <Globe className="w-8 h-8 text-blue-600" />
                    </div>
                    <div>
                        <div className="flex items-center gap-3">
                            <h1 className="text-2xl font-bold text-gray-900">State Admin Dashboard</h1>
                            <VoiceButton
                                content={getPageSummary()}
                                className="bg-blue-600 text-white shadow-lg hover:bg-blue-700"
                            />
                        </div>
                        <p className="text-sm text-gray-500 mt-1">
                            {t('common.welcome')}, {user?.full_name} — Viewing scope: <span className="font-semibold text-blue-600">{currentScopeLabel}</span>
                        </p>
                    </div>
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
