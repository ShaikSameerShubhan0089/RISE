import React, { useEffect, useState, useCallback } from 'react';
import { useAuth } from '../../context/AuthContext';
import { dashboardAPI } from '../../utils/api';
import SummaryCards from '../../components/dashboard/SummaryCards';
import DashboardCharts from '../../components/dashboard/DashboardCharts';
import ChildrenTable from '../../components/dashboard/ChildrenTable';
import InterventionsTable from '../../components/dashboard/InterventionsTable';
import UsersTable from '../../components/dashboard/UsersTable';
import ChildGrowthChart from '../../components/dashboard/ChildGrowthChart';
import { RefreshCw, LayoutDashboard } from 'lucide-react';
import VoiceButton from '../../components/common/VoiceButton';
import { useLanguage } from '../../context/LanguageContext';

const SupervisorDashboard = () => {
    const { user } = useAuth();
    const { t } = useLanguage();

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

    const getPageSummary = () => {
        const scope = centers.find(c => String(c.center_id) === selectedCenter)?.center_name || 'the entire Mandal';

        let text = t('parent.narration.admin_hello')
            .replace('{name}', user?.full_name || '')
            .replace('{role}', t('user_mgmt.roles.supervisor'))
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

        // Center Performance & Ranking
        const performances = (charts?.center_performance || [])
            .sort((a, b) => b.total_registrations - a.total_registrations);

        if (performances.length > 0) {
            text += " " + t('parent.narration.ranking_intro');
            performances.slice(0, 3).forEach(p => {
                text += " " + t('parent.narration.performance_item')
                    .replace('{name}', p.center_name)
                    .replace('{count}', p.total_registrations);
            });

            const bottleneck = performances.filter(p => (p.pending_referrals || 0) > 5);
            if (bottleneck.length > 0) {
                bottleneck.slice(0, 2).forEach(p => {
                    text += " " + t('parent.narration.center_bottleneck')
                        .replace('{name}', p.center_name)
                        .replace('{count}', p.pending_referrals);
                });
            }
        }

        return text;
    };

    const handleCenterChange = (e) => {
        const cid = e.target.value;
        setSelectedCenter(cid);
        loadData(cid);
    };

    const handleReset = () => {
        setSelectedCenter('');
        loadData('');
    };

    const scopeLabel = centers.find(c => String(c.center_id) === selectedCenter)?.center_name || t('common.all_centers');

    const tabs = [
        { id: 'charts', label: `📊 ${t('common.analytics')}` },
        { id: 'children', label: `👶 ${t('common.children')}` },
        { id: 'interventions', label: `🏥 ${t('common.interventions') || 'Interventions'}` },
        { id: 'staff', label: `👥 ${t('common.users') || 'Staff'}` },
        { id: 'growth', label: `📈 ${t('common.growth') || 'Growth'}` },
    ];

    return (
        <div className="p-6 space-y-6">
            {/* Header */}
            <div className="relative overflow-hidden bg-gradient-to-r from-blue-600/90 to-indigo-700/90 rounded-2xl p-6 text-white flex flex-wrap justify-between items-center gap-4">
                <div className="relative z-10">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
                            <LayoutDashboard className="w-6 h-6 text-white" />
                        </div>
                        <div>
                            <div className="flex items-center gap-3">
                                <h1 className="text-2xl font-bold">{t('user_mgmt.roles.supervisor')} {t('common.dashboard')}</h1>
                                <VoiceButton
                                    content={getPageSummary()}
                                    className="bg-white/20 hover:bg-white/30 text-white border border-white/20"
                                />
                            </div>
                            <p className="text-blue-100 text-sm mt-1">
                                {t('common.welcome')}, <span className="font-semibold">{user?.full_name}</span> — {scopeLabel}
                            </p>
                        </div>
                    </div>
                </div>

                {/* Decorative background shapes */}
                <div className="absolute -right-10 -top-10 w-40 h-40 bg-white/10 rounded-full blur-3xl" />
                <div className="absolute -left-10 -bottom-10 w-40 h-40 bg-indigo-400/20 rounded-full blur-3xl" />
            </div>

            {/* AWC Center filter bar */}
            <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
                <div className="flex flex-wrap items-end gap-4">
                    <div className="flex flex-col gap-1 min-w-[240px]">
                        <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                            {t('common.select_center')}
                        </label>
                        {centersLoading ? (
                            <div className="h-9 bg-gray-100 rounded-lg animate-pulse" />
                        ) : (
                            <select
                                value={selectedCenter}
                                onChange={handleCenterChange}
                                className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="">{t('common.all_centers')}</option>
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
                            <RefreshCw className="w-3.5 h-3.5" /> {t('children.filters.reset')}
                        </button>
                    )}
                    {dataLoading && (
                        <div className="flex items-center gap-2 text-blue-600 text-sm">
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600" />
                            {t('common.loading')}
                        </div>
                    )}
                    {!centersLoading && centers.length > 0 && (
                        <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                            {centers.length} {t('common.all_centers').toLowerCase()}
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
