import React from 'react';
import {
    BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
    PieChart, Pie, Cell, Legend
} from 'recharts';

const COLORS = ['#6366f1', '#22c55e', '#f59e0b', '#ef4444', '#14b8a6', '#a855f7', '#f97316'];

const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
        return (
            <div className="bg-white border border-gray-200 rounded-lg shadow-lg px-3 py-2 text-sm">
                <div className="font-medium text-gray-900">{label || payload[0].name}</div>
                <div className="text-gray-600">{payload[0].value.toLocaleString()}</div>
            </div>
        );
    }
    return null;
};

const DashboardCharts = ({ data = {} }) => {
    const {
        children_per_center = [],
        intervention_categories = [],
        improvement_status = [],
        gender_distribution = [],
    } = data;

    return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Children per Centre */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
                <h3 className="text-base font-semibold text-gray-900 mb-4">Children per Centre</h3>
                {children_per_center.length === 0 ? (
                    <div className="flex items-center justify-center h-48 text-gray-400 text-sm">No data</div>
                ) : (
                    <ResponsiveContainer width="100%" height={260}>
                        <BarChart data={children_per_center} margin={{ top: 5, right: 5, bottom: 60, left: 0 }}>
                            <XAxis
                                dataKey="center"
                                tick={{ fontSize: 10 }}
                                angle={-40}
                                textAnchor="end"
                                interval={0}
                            />
                            <YAxis tick={{ fontSize: 11 }} />
                            <Tooltip content={<CustomTooltip />} />
                            <Bar dataKey="count" fill="#6366f1" radius={[4, 4, 0, 0]} label={false} />
                        </BarChart>
                    </ResponsiveContainer>
                )}
            </div>

            {/* Intervention Categories */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
                <h3 className="text-base font-semibold text-gray-900 mb-4">Intervention Categories</h3>
                {intervention_categories.length === 0 ? (
                    <div className="flex items-center justify-center h-48 text-gray-400 text-sm">No data</div>
                ) : (
                    <ResponsiveContainer width="100%" height={260}>
                        <PieChart>
                            <Pie
                                data={intervention_categories}
                                dataKey="count"
                                nameKey="category"
                                outerRadius={90}
                                label={({ category, percent }) => `${(percent * 100).toFixed(0)}%`}
                                labelLine={false}
                            >
                                {intervention_categories.map((_, i) => (
                                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                                ))}
                            </Pie>
                            <Legend
                                formatter={(value) => <span className="text-xs text-gray-700">{value}</span>}
                                iconSize={10}
                            />
                            <Tooltip formatter={(v) => v.toLocaleString()} />
                        </PieChart>
                    </ResponsiveContainer>
                )}
            </div>

            {/* Improvement Status */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
                <h3 className="text-base font-semibold text-gray-900 mb-4">Improvement Status</h3>
                {improvement_status.length === 0 ? (
                    <div className="flex items-center justify-center h-48 text-gray-400 text-sm">No data</div>
                ) : (
                    <ResponsiveContainer width="100%" height={200}>
                        <BarChart data={improvement_status} layout="vertical" margin={{ top: 0, right: 20, bottom: 0, left: 120 }}>
                            <XAxis type="number" tick={{ fontSize: 11 }} />
                            <YAxis dataKey="status" type="category" tick={{ fontSize: 11 }} width={115} />
                            <Tooltip content={<CustomTooltip />} />
                            <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                                {improvement_status.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                )}
            </div>

            {/* Gender Distribution */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
                <h3 className="text-base font-semibold text-gray-900 mb-4">Gender Distribution</h3>
                {gender_distribution.length === 0 ? (
                    <div className="flex items-center justify-center h-48 text-gray-400 text-sm">No data</div>
                ) : (
                    <ResponsiveContainer width="100%" height={200}>
                        <PieChart>
                            <Pie
                                data={gender_distribution}
                                dataKey="count"
                                nameKey="gender"
                                outerRadius={80}
                                label={({ gender, percent }) => `${gender} ${(percent * 100).toFixed(0)}%`}
                            >
                                {gender_distribution.map((_, i) => (
                                    <Cell key={i} fill={['#6366f1', '#ec4899', '#14b8a6'][i % 3]} />
                                ))}
                            </Pie>
                            <Tooltip formatter={(v) => v.toLocaleString()} />
                        </PieChart>
                    </ResponsiveContainer>
                )}
            </div>
        </div>
    );
};

export default DashboardCharts;
