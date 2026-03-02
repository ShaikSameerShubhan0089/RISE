/**
 * ChildGrowthChart.jsx
 * 
 * Shows longitudinal DQ scores across assessment cycles for a selected child.
 * Powered by GET /api/dashboard/child-growth/{child_id}
 * 
 * Usage:
 *   <ChildGrowthChart children={childrenArray} />
 *   where childrenArray is the same data returned by /dashboard/children
 */
import React, { useState } from 'react';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid,
    Tooltip, Legend, ResponsiveContainer, ReferenceLine,
} from 'recharts';
import { dashboardAPI } from '../../utils/api';
import { useLanguage } from '../../context/LanguageContext';
import { Download, TrendingUp } from 'lucide-react';

const DQ_LINES = [
    { key: 'composite_dq', label: 'Composite DQ', color: '#6366f1' },
    { key: 'gross_motor_dq', label: 'Gross Motor', color: '#22c55e' },
    { key: 'fine_motor_dq', label: 'Fine Motor', color: '#f59e0b' },
    { key: 'language_dq', label: 'Language', color: '#ef4444' },
    { key: 'cognitive_dq', label: 'Cognitive', color: '#14b8a6' },
    { key: 'socio_emotional_dq', label: 'Socio-Emotional', color: '#a855f7' },
];

const exportGrowthCSV = (childName, datapoints, t) => {
    const headers = [
        t('growth.csv_headers.cycle'),
        t('growth.csv_headers.date'),
        t('growth.csv_headers.age'),
        t('growth.csv_headers.comp_dq'),
        t('growth.csv_headers.gross'),
        t('growth.csv_headers.fine'),
        t('growth.csv_headers.lang'),
        t('growth.csv_headers.cog'),
        t('growth.csv_headers.socio'),
        t('growth.csv_headers.delayed'),
    ];
    const lines = [
        headers.join(','),
        ...datapoints.map(d => [
            d.cycle, d.assessment_date || '', d.age_months,
            d.composite_dq ?? '', d.gross_motor_dq ?? '', d.fine_motor_dq ?? '',
            d.language_dq ?? '', d.cognitive_dq ?? '', d.socio_emotional_dq ?? '',
            d.delayed_domains ?? '',
        ].join(',')
        ),
    ];
    const blob = new Blob([lines.join('\n')], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `growth_${childName.replace(/\s+/g, '_')}.csv`;
    a.click();
    URL.revokeObjectURL(url);
};

const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload?.length) return null;
    return (
        <div className="bg-white border border-gray-200 rounded-lg shadow-lg px-3 py-2 text-xs">
            <div className="font-semibold text-gray-800 mb-1">Cycle {label}</div>
            {payload.map(p => (
                <div key={p.dataKey} className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full inline-block" style={{ background: p.color }} />
                    <span className="text-gray-600">{p.name}:</span>
                    <span className="font-medium text-gray-900">{p.value?.toFixed(1) ?? '—'}</span>
                </div>
            ))}
        </div>
    );
};

const ChildGrowthChart = ({ children = [] }) => {
    const { t } = useLanguage();
    const [selectedChildId, setSelectedChildId] = useState('');
    const [growthData, setGrowthData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [visibleLines, setVisibleLines] = useState(
        Object.fromEntries(DQ_LINES.map(l => [l.key, true]))
    );

    const handleChildSelect = (e) => {
        const childId = e.target.value;
        setSelectedChildId(childId);
        setGrowthData(null);
        if (!childId) return;

        setLoading(true);
        dashboardAPI.getChildGrowth(childId)
            .then(r => setGrowthData(r.data))
            .catch(() => setGrowthData({ error: true }))
            .finally(() => setLoading(false));
    };

    const toggleLine = (key) => {
        setVisibleLines(prev => ({ ...prev, [key]: !prev[key] }));
    };

    const datapoints = growthData?.datapoints || [];
    const chartData = datapoints.map(d => ({ ...d, label: `C${d.cycle}` }));

    return (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
            {/* Header */}
            <div className="flex flex-wrap items-center justify-between gap-3 p-5 border-b border-gray-100">
                <div className="flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-indigo-500" />
                    <h3 className="text-base font-semibold text-gray-900">{t('growth.title')}</h3>
                    {growthData && !growthData.error && (
                        <span className="text-sm text-gray-500">— {growthData.child_name}</span>
                    )}
                </div>
                <div className="flex items-center gap-2">
                    {/* Child selector */}
                    <select
                        id="childGrowthSelect"
                        value={selectedChildId}
                        onChange={handleChildSelect}
                        className="text-sm border border-gray-300 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-indigo-500 min-w-[220px]"
                    >
                        <option value="">{t('growth.select_child_instruction')}</option>
                        {children.map(c => (
                            <option key={c.child_id} value={c.child_id}>
                                {c.first_name} {c.last_name} ({c.unique_child_code})
                            </option>
                        ))}
                    </select>
                    {/* CSV export (only when data loaded) */}
                    {growthData && !growthData.error && datapoints.length > 0 && (
                        <button
                            onClick={() => exportGrowthCSV(growthData.child_name, datapoints, t)}
                            className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                        >
                            <Download className="w-4 h-4" />
                            {t('growth.export')}
                        </button>
                    )}
                </div>
            </div>

            {/* Body */}
            <div className="p-5">
                {/* Empty state */}
                {!selectedChildId && !loading && (
                    <div className="flex flex-col items-center justify-center h-48 text-gray-400">
                        <TrendingUp className="w-8 h-8 mb-2 opacity-40" />
                        <p className="text-sm">{t('growth.select_child_instruction')}</p>
                    </div>
                )}

                {/* Loading */}
                {loading && (
                    <div className="flex items-center justify-center h-48 gap-2 text-blue-600 text-sm">
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600" />
                        {t('growth.loading')}
                    </div>
                )}

                {/* Error */}
                {growthData?.error && (
                    <div className="flex items-center justify-center h-48 text-red-500 text-sm">
                        {t('growth.error')}
                    </div>
                )}

                {/* No assessments */}
                {growthData && !growthData.error && datapoints.length === 0 && (
                    <div className="flex items-center justify-center h-48 text-gray-400 text-sm">
                        {t('growth.no_assessments')}
                    </div>
                )}

                {/* Chart */}
                {growthData && !growthData.error && datapoints.length > 0 && (
                    <>
                        {/* DQ domain toggles */}
                        <div className="flex flex-wrap gap-2 mb-4">
                            {DQ_LINES.map(l => (
                                <button
                                    key={l.key}
                                    onClick={() => toggleLine(l.key)}
                                    className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border transition-all ${visibleLines[l.key]
                                            ? 'text-white border-transparent'
                                            : 'bg-white text-gray-500 border-gray-300'
                                        }`}
                                    style={visibleLines[l.key] ? { background: l.color, borderColor: l.color } : {}}
                                >
                                    <span className="w-2 h-2 rounded-full" style={{ background: l.color }} />
                                    {l.label}
                                </button>
                            ))}
                        </div>

                        <ResponsiveContainer width="100%" height={320}>
                            <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                                <XAxis
                                    dataKey="label"
                                    tick={{ fontSize: 11 }}
                                    label={{ value: 'Assessment Cycle', position: 'insideBottom', offset: -2, fontSize: 11, fill: '#9ca3af' }}
                                />
                                <YAxis
                                    domain={[0, 100]}
                                    tick={{ fontSize: 11 }}
                                    label={{ value: 'DQ Score', angle: -90, position: 'insideLeft', fontSize: 11, fill: '#9ca3af' }}
                                />
                                {/* Typical development reference line at 85 */}
                                <ReferenceLine y={85} stroke="#d1d5db" strokeDasharray="4 4"
                                    label={{ value: 'Typical (85)', position: 'right', fontSize: 10, fill: '#9ca3af' }} />
                                <Tooltip content={<CustomTooltip />} />
                                <Legend
                                    formatter={(value) => <span className="text-xs text-gray-700">{value}</span>}
                                    iconSize={8}
                                />
                                {DQ_LINES.map(l => visibleLines[l.key] && (
                                    <Line
                                        key={l.key}
                                        type="monotone"
                                        dataKey={l.key}
                                        name={l.label}
                                        stroke={l.color}
                                        strokeWidth={2}
                                        dot={{ r: 4, fill: l.color }}
                                        activeDot={{ r: 6 }}
                                        connectNulls
                                    />
                                ))}
                            </LineChart>
                        </ResponsiveContainer>

                        {/* Summary row */}
                        <div className="mt-4 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
                            {DQ_LINES.map(l => {
                                const lastVal = [...datapoints].reverse().find(d => d[l.key] != null)?.[l.key];
                                const firstVal = datapoints.find(d => d[l.key] != null)?.[l.key];
                                const delta = lastVal != null && firstVal != null ? lastVal - firstVal : null;
                                return (
                                    <div key={l.key} className="rounded-lg border border-gray-100 p-3 text-center">
                                        <div className="text-xs text-gray-500 mb-1">{l.label}</div>
                                        <div className="text-lg font-bold" style={{ color: l.color }}>
                                            {lastVal?.toFixed(1) ?? '—'}
                                        </div>
                                        {delta != null && (
                                            <div className={`text-xs mt-0.5 ${delta >= 0 ? 'text-green-600' : 'text-red-500'}`}>
                                                {delta >= 0 ? '↑' : '↓'} {Math.abs(delta).toFixed(1)}
                                            </div>
                                        )}
                                    </div>
                                );
                            })}
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

export default ChildGrowthChart;
