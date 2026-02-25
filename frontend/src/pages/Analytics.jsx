import React, { useState, useEffect } from 'react';
import { analyticsAPI } from '../utils/api';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
    PieChart, Pie, Cell, LineChart, Line,
} from 'recharts';
import {
    Users, Baby, BrainCircuit, Building2,
    TrendingUp, UserCheck, UserX, CalendarDays,
    BarChart3,
} from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';
import VoiceButton from '../components/common/VoiceButton';

const getRoleLabels = (t) => ({
    system_admin: t('user_mgmt.roles.system_admin'),
    state_admin: t('user_mgmt.roles.state_admin'),
    district_officer: t('user_mgmt.roles.district_officer'),
    supervisor: t('user_mgmt.roles.supervisor'),
    anganwadi_worker: t('user_mgmt.roles.anganwadi_worker'),
    parent: t('user_mgmt.roles.parent'),
});

const RISK_COLORS = {
    'High Risk': '#ef4444',
    'Low Risk': '#22c55e',
    'Moderate Risk': '#f59e0b',
};

const PIE_COLORS = ['#6366f1', '#22c55e', '#f59e0b', '#ef4444', '#a855f7', '#06b6d4'];

const getPeriodOptions = (t) => [
    { value: 'week', label: t('analytics.periods.week') },
    { value: 'month', label: t('analytics.periods.month') },
    { value: 'year', label: t('analytics.periods.year') },
];

const MetricCard = ({ icon: Icon, label, value, sub, color }) => (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm px-6 py-5 flex items-center gap-4">
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 ${color}`}>
            <Icon className="w-6 h-6 text-white" />
        </div>
        <div>
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">{label}</p>
            <p className="text-3xl font-bold text-gray-900 leading-tight">{value ?? '—'}</p>
            {sub && <p className="text-xs text-gray-400 mt-0.5">{sub}</p>}
        </div>
    </div>
);

const ChartCard = ({ title, children, className = '' }) => (
    <div className={`bg-white rounded-2xl border border-gray-100 shadow-sm p-6 ${className}`}>
        <h3 className="text-sm font-bold text-gray-700 uppercase tracking-wide mb-4">{title}</h3>
        {children}
    </div>
);

const Analytics = () => {
    const { t } = useLanguage();
    const [summary, setSummary] = useState(null);
    const [usersData, setUsersData] = useState([]);
    const [childrenData, setChildrenData] = useState([]);
    const [predictionsData, setPredictionsData] = useState(null);
    const [period, setPeriod] = useState('month');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchAll();
    }, [period]);

    const fetchAll = async () => {
        setLoading(true);
        try {
            const [sumRes, usrRes, chdRes, prdRes] = await Promise.allSettled([
                analyticsAPI.getSummary(),
                analyticsAPI.getUsers(),
                analyticsAPI.getChildren(period),
                analyticsAPI.getPredictions(),
            ]);
            if (sumRes.status === 'fulfilled') setSummary(sumRes.value.data);
            if (usrRes.status === 'fulfilled') setUsersData(usrRes.value.data);
            if (chdRes.status === 'fulfilled') setChildrenData(chdRes.value.data);
            if (prdRes.status === 'fulfilled') setPredictionsData(prdRes.value.data);
        } finally {
            setLoading(false);
        }
    };

    const ROLE_LABELS = getRoleLabels(t);
    const usersChartData = usersData.map(u => ({
        role: ROLE_LABELS[u.role] || u.role,
        Active: u.active,
        Revoked: u.revoked,
    }));

    const riskPieData = (predictionsData?.risk_distribution || []).map(d => ({
        name: d.tier,
        value: d.count,
    }));

    const modelBarData = (predictionsData?.model_usage || []).map(d => ({
        model: d.model || 'Unknown',
        Predictions: d.count,
    }));

    return (
        <div className="p-6 space-y-6">
            {/* Page header + period filter */}
            <div className="flex items-center justify-between flex-wrap gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                        <BarChart3 className="w-6 h-6 text-indigo-600" />
                        {t('analytics.title')}
                    </h1>
                    <p className="text-sm text-gray-500 mt-1">{t('analytics.sub')}</p>
                </div>
                <div className="flex items-center gap-3">
                    <div className="flex items-center gap-1 bg-gray-100 p-1 rounded-xl">
                        {getPeriodOptions(t).map(opt => (
                            <button
                                key={opt.value}
                                onClick={() => setPeriod(opt.value)}
                                className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all ${period === opt.value ? 'bg-white shadow text-indigo-700' : 'text-gray-500 hover:text-gray-700'}`}
                            >
                                {opt.label}
                            </button>
                        ))}
                    </div>
                    <VoiceButton
                        content={`${t('analytics.title')}. ${t('analytics.metrics.total_users')}: ${summary?.total_users || 0}. ${t('analytics.metrics.total_children')}: ${summary?.total_children || 0}. ${t('analytics.metrics.total_predictions')}: ${summary?.total_predictions || 0}. ${t('analytics.metrics.active_centers')}: ${summary?.active_centers || 0}.`}
                    />
                </div>
            </div>

            {loading ? (
                <div className="flex items-center justify-center h-64">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600" />
                </div>
            ) : (
                <>
                    {/* ── Metric Cards ─────────────────────────────────────── */}
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                        <MetricCard icon={Users} label={t('analytics.metrics.total_users')} value={summary?.total_users}
                            sub={`${summary?.new_users_month ?? 0} ${t('analytics.metrics.new_month_sub')}`} color="bg-indigo-500" />
                        <MetricCard icon={Baby} label={t('analytics.metrics.total_children')} value={summary?.total_children}
                            sub={t('analytics.metrics.registered_sub')} color="bg-emerald-500" />
                        <MetricCard icon={BrainCircuit} label={t('analytics.metrics.total_predictions')} value={summary?.total_predictions}
                            sub={t('analytics.metrics.ai_sub')} color="bg-purple-500" />
                        <MetricCard icon={Building2} label={t('analytics.metrics.active_centers')} value={summary?.active_centers}
                            sub={t('analytics.metrics.centers_sub')} color="bg-amber-500" />
                    </div>

                    {/* ── Status strip ─────────────────────────────────────── */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {[
                            { icon: UserCheck, label: t('analytics.metrics.active_users'), value: summary?.active_users, color: 'text-emerald-600 bg-emerald-50' },
                            { icon: UserX, label: t('analytics.metrics.revoked_users'), value: summary?.revoked_users, color: 'text-red-500 bg-red-50' },
                            { icon: CalendarDays, label: t('analytics.metrics.new_week'), value: summary?.new_users_week, color: 'text-indigo-600 bg-indigo-50' },
                            { icon: TrendingUp, label: t('analytics.metrics.new_month'), value: summary?.new_users_month, color: 'text-amber-600 bg-amber-50' },
                        ].map(s => (
                            <div key={s.label} className={`rounded-xl flex items-center gap-3 px-5 py-4 ${s.color}`}>
                                <s.icon className="w-5 h-5 flex-shrink-0" />
                                <div>
                                    <p className="text-xs font-semibold uppercase tracking-wide opacity-70">{s.label}</p>
                                    <p className="text-2xl font-bold">{s.value ?? 0}</p>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* ── Charts Row 1 ─────────────────────────────────────── */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <ChartCard title={t('analytics.charts.users_by_role')}>
                            <ResponsiveContainer width="100%" height={260}>
                                <BarChart data={usersChartData} margin={{ top: 4, right: 10, left: -10, bottom: 40 }}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                                    <XAxis dataKey="role" tick={{ fontSize: 11 }} angle={-25} textAnchor="end" interval={0} />
                                    <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
                                    <Tooltip />
                                    <Legend wrapperStyle={{ paddingTop: 8 }} />
                                    <Bar dataKey="Active" fill="#6366f1" radius={[4, 4, 0, 0]} />
                                    <Bar dataKey="Revoked" fill="#f87171" radius={[4, 4, 0, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        </ChartCard>

                        <ChartCard title={t('analytics.charts.risk_dist')}>
                            {riskPieData.length === 0 ? (
                                <div className="h-60 flex items-center justify-center text-sm text-gray-400">{t('analytics.charts.no_data')}</div>
                            ) : (
                                <ResponsiveContainer width="100%" height={260}>
                                    <PieChart>
                                        <Pie
                                            data={riskPieData}
                                            cx="50%" cy="50%"
                                            innerRadius={60} outerRadius={95}
                                            dataKey="value"
                                            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                                            labelLine={false}
                                        >
                                            {riskPieData.map((entry, index) => (
                                                <Cell key={index} fill={RISK_COLORS[entry.name] || PIE_COLORS[index % PIE_COLORS.length]} />
                                            ))}
                                        </Pie>
                                        <Tooltip />
                                        <Legend />
                                    </PieChart>
                                </ResponsiveContainer>
                            )}
                        </ChartCard>
                    </div>

                    {/* ── Charts Row 2 ─────────────────────────────────────── */}
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        <ChartCard title={t('analytics.charts.registrations')} className="lg:col-span-2">
                            {childrenData.length === 0 ? (
                                <div className="h-60 flex items-center justify-center text-sm text-gray-400">{t('analytics.charts.no_data')}</div>
                            ) : (
                                <ResponsiveContainer width="100%" height={260}>
                                    <LineChart data={childrenData} margin={{ top: 4, right: 10, left: -10, bottom: 0 }}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                                        <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                                        <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
                                        <Tooltip />
                                        <Line type="monotone" dataKey="count" stroke="#6366f1" strokeWidth={2} dot={{ r: 3 }} name="Registrations" />
                                    </LineChart>
                                </ResponsiveContainer>
                            )}
                        </ChartCard>

                        <ChartCard title={t('analytics.charts.model_usage')}>
                            {modelBarData.length === 0 ? (
                                <div className="h-60 flex items-center justify-center text-sm text-gray-400">{t('analytics.charts.no_data')}</div>
                            ) : (
                                <ResponsiveContainer width="100%" height={260}>
                                    <BarChart data={modelBarData} layout="vertical" margin={{ top: 4, right: 16, left: 10, bottom: 0 }}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" horizontal={false} />
                                        <XAxis type="number" tick={{ fontSize: 11 }} allowDecimals={false} />
                                        <YAxis dataKey="model" type="category" tick={{ fontSize: 10 }} width={90} />
                                        <Tooltip />
                                        <Bar dataKey="Predictions" fill="#a855f7" radius={[0, 4, 4, 0]} />
                                    </BarChart>
                                </ResponsiveContainer>
                            )}
                        </ChartCard>
                    </div>
                </>
            )}
        </div>
    );
};

export default Analytics;
