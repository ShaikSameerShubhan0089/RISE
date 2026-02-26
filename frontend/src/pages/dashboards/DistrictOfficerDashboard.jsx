import React, { useEffect, useState, useCallback } from 'react';
import { useAuth } from '../../context/AuthContext';
import { dashboardAPI } from '../../utils/api';
import SummaryCards from '../../components/dashboard/SummaryCards';
import DashboardCharts from '../../components/dashboard/DashboardCharts';
import ChildrenTable from '../../components/dashboard/ChildrenTable';
import InterventionsTable from '../../components/dashboard/InterventionsTable';
import UsersTable from '../../components/dashboard/UsersTable';
import ChildGrowthChart from '../../components/dashboard/ChildGrowthChart';
import { RefreshCw, Map } from 'lucide-react';
import VoiceButton from '../../components/common/VoiceButton';
import { useLanguage } from '../../context/LanguageContext';

const DistrictOfficerDashboard = () => {
    const { user } = useAuth();
    const { t } = useLanguage();

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

    const getPageSummary = () => {
        const scope = mandals.find(m => String(m.mandal_id) === selectedMandal)?.mandal_name || 'the entire District';

        let text = t('parent.narration.admin_hello')
            .replace('{name}', user?.full_name || '')
            .replace('{role}', t('user_mgmt.roles.district_officer'))
            .replace('{scope}', scope);

        // Detailed Metrics
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

        // Mandal Performance & Ranking
        const performances = (charts?.mandal_performance || [])
            .sort((a, b) => b.registration_count - a.registration_count);

        if (performances.length > 0) {
            text += " " + t('parent.narration.ranking_intro');
            performances.slice(0, 3).forEach(m => {
                text += " " + t('parent.narration.mandal_stat')
                    .replace('{name}', m.mandal_name)
                    .replace('{count}', m.registration_count);
            });

            // Trend analysis if available
            performances.slice(0, 1).forEach(m => {
                text += " " + t('parent.narration.district_stat')
                    .replace('{name}', m.mandal_name)
                    .replace('{trend}', 'positive'); // Placeholder trend
            });
        }

        return text;
    };

    const handleMandalChange = (e) => {
        const mid = e.target.value;
        setSelectedMandal(mid);
        loadData(mid);
    };

    const handleReset = () => {
        setSelectedMandal('');
        loadData('');
    };

    const scopeLabel = mandals.find(m => String(m.mandal_id) === selectedMandal)?.mandal_name || t('common.all_mandals');

    const tabs = [
        { id: 'charts', label: `📊 ${t('common.analytics')}` },
        { id: 'children', label: `👶 ${t('common.children')}` },
        { id: 'interventions', label: `🏥 ${t('common.interventions')}` },
        { id: 'staff', label: `👥 ${t('common.users')}` },
        { id: 'growth', label: `📈 ${t('common.growth')}` },
    ];

    return (
        <div className="p-6 space-y-6">
            {/* Header */}
            <div className="relative overflow-hidden bg-gradient-to-r from-teal-600 to-emerald-700 rounded-2xl p-6 text-white flex flex-wrap justify-between items-center gap-4">
                <div className="relative z-10">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
                            <Map className="w-6 h-6 text-white" />
                        </div>
                        <div>
                            <div className="flex items-center gap-3">
                                <h1 className="text-2xl font-bold">{t('user_mgmt.roles.district_officer')} Dashboard</h1>
                                <VoiceButton
                                    content={getPageSummary()}
                                    className="bg-white/20 hover:bg-white/30 text-white border border-white/20"
                                />
                            </div>
                            <p className="text-teal-50 text-sm mt-1">
                                {t('common.welcome')}, <span className="font-semibold">{user?.full_name}</span> — {scopeLabel}
                            </p>
                        </div>
                    </div>
                </div>

                {/* Decorative background shapes */}
                <div className="absolute -right-10 -top-10 w-40 h-40 bg-white/10 rounded-full blur-3xl" />
                <div className="absolute -left-10 -bottom-10 w-40 h-40 bg-emerald-400/20 rounded-full blur-3xl" />
            </div>

            {/* Mandal filter bar */}
            <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
                <div className="flex flex-wrap items-end gap-4">
                    <div className="flex flex-col gap-1 min-w-[220px]">
                        <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                            {t('common.select_mandal')}
                        </label>
                        {mandalsLoading ? (
                            <div className="h-9 bg-gray-100 rounded-lg animate-pulse" />
                        ) : (
                            <select
                                value={selectedMandal}
                                onChange={handleMandalChange}
                                className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="">{t('common.all_mandals')}</option>
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
                            <RefreshCw className="w-3.5 h-3.5" /> {t('children.filters.reset')}
                        </button>
                    )}
                    {dataLoading && (
                        <div className="flex items-center gap-2 text-blue-600 text-sm">
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600" />
                            {t('common.loading')}
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
