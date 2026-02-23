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

const ROLE_LABELS = {
    system_admin: 'System Admin',
    state_admin: 'State Admin',
    district_officer: 'District Officer',
    supervisor: 'Supervisor',
    anganwadi_worker: 'AWC Worker',
    parent: 'Parent',
};

const RISK_COLORS = {
    'High Risk': '#ef4444',
    'Low Risk': '#22c55e',
    'Moderate Risk': '#f59e0b',
};

const PIE_COLORS = ['#6366f1', '#22c55e', '#f59e0b', '#ef4444', '#a855f7', '#06b6d4'];

const PERIOD_OPTIONS = [
    { value: 'week', label: 'Last 7 Days' },
    { value: 'month', label: 'Last 30 Days' },
    { value: 'year', label: 'Last 12 Months' },
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
                        System Analytics
                    </h1>
                    <p className="text-sm text-gray-500 mt-1">Real-time insights across users, children, and assessments</p>
                </div>
                <div className="flex items-center gap-1 bg-gray-100 p-1 rounded-xl">
                    {PERIOD_OPTIONS.map(opt => (
                        <button
                            key={opt.value}
                            onClick={() => setPeriod(opt.value)}
                            className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all ${period === opt.value ? 'bg-white shadow text-indigo-700' : 'text-gray-500 hover:text-gray-700'}`}
                        >
                            {opt.label}
                        </button>
                    ))}
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
                        <MetricCard icon={Users} label="Total Users" value={summary?.total_users}
                            sub={`${summary?.new_users_month ?? 0} new this month`} color="bg-indigo-500" />
                        <MetricCard icon={Baby} label="Total Children" value={summary?.total_children}
                            sub="Registered across all centers" color="bg-emerald-500" />
                        <MetricCard icon={BrainCircuit} label="Total Assessments" value={summary?.total_predictions}
                            sub="AI risk predictions made" color="bg-purple-500" />
                        <MetricCard icon={Building2} label="Active Centers" value={summary?.active_centers}
                            sub="Anganwadi centers in system" color="bg-amber-500" />
                    </div>

                    {/* ── Status strip ─────────────────────────────────────── */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {[
                            { icon: UserCheck, label: 'Active Users', value: summary?.active_users, color: 'text-emerald-600 bg-emerald-50' },
                            { icon: UserX, label: 'Revoked Users', value: summary?.revoked_users, color: 'text-red-500 bg-red-50' },
                            { icon: CalendarDays, label: 'New This Week', value: summary?.new_users_week, color: 'text-indigo-600 bg-indigo-50' },
                            { icon: TrendingUp, label: 'New This Month', value: summary?.new_users_month, color: 'text-amber-600 bg-amber-50' },
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
                        <ChartCard title="Users by Role (Active vs Revoked)">
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

                        <ChartCard title="Risk Level Distribution">
                            {riskPieData.length === 0 ? (
                                <div className="h-60 flex items-center justify-center text-sm text-gray-400">No prediction data yet</div>
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
                        <ChartCard title="Children Registrations Over Time" className="lg:col-span-2">
                            {childrenData.length === 0 ? (
                                <div className="h-60 flex items-center justify-center text-sm text-gray-400">No registration data for this period</div>
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

                        <ChartCard title="Model Usage">
                            {modelBarData.length === 0 ? (
                                <div className="h-60 flex items-center justify-center text-sm text-gray-400">No model data yet</div>
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
