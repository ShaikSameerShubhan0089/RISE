import React, { useState, useEffect } from 'react';
import { X, User, Home, Calendar, Phone, Activity, TrendingUp, ClipboardList, AlertCircle } from 'lucide-react';
import { childrenAPI, dashboardAPI } from '../../utils/api';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';

const ChildDetailsModal = ({ child, onClose }) => {
    const [assessments, setAssessments] = useState([]);
    const [growthData, setGrowthData] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!child) return;
        const fetchData = async () => {
            setLoading(true);
            try {
                const [assessRes, growthRes] = await Promise.all([
                    childrenAPI.getAssessments(child.child_id),
                    dashboardAPI.getChildGrowth(child.child_id)
                ]);
                setAssessments(assessRes.data);
                setGrowthData(growthRes.data?.history || []);
            } catch (err) {
                console.error('Failed to fetch child details', err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [child]);

    if (!child) return null;

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-3xl shadow-2xl w-full max-w-4xl overflow-hidden animate-in fade-in zoom-in duration-200 flex flex-col max-h-[90vh]">
                {/* Header */}
                <div className="flex items-center justify-between p-6 bg-gray-50 border-b border-gray-100">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
                            <User className="w-6 h-6 text-green-600" />
                        </div>
                        <div>
                            <h2 className="text-xl font-bold text-gray-900">{child.first_name} {child.last_name}</h2>
                            <p className="text-sm font-mono text-gray-500">{child.unique_child_code}</p>
                        </div>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-gray-200 rounded-full transition-colors">
                        <X className="w-5 h-5 text-gray-500" />
                    </button>
                </div>

                <div className="overflow-y-auto p-6 space-y-8">
                    {/* Basic Info & Caregiver Info */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <div className="space-y-4">
                            <h3 className="text-sm font-black text-gray-400 uppercase tracking-widest flex items-center gap-2">
                                <Activity className="w-4 h-4" /> Personal Details
                            </h3>
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-1">
                                    <p className="text-[10px] text-gray-400 font-bold uppercase">DOB</p>
                                    <p className="text-sm font-medium">{new Date(child.dob).toLocaleDateString()}</p>
                                </div>
                                <div className="space-y-1">
                                    <p className="text-[10px] text-gray-400 font-bold uppercase">Gender</p>
                                    <p className="text-sm font-medium">{child.gender}</p>
                                </div>
                                <div className="space-y-1">
                                    <p className="text-[10px] text-gray-400 font-bold uppercase">Status</p>
                                    <span className="px-2 py-0.5 bg-green-100 text-green-800 rounded-full text-[10px] font-black uppercase">
                                        {child.status}
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div className="space-y-4">
                            <h3 className="text-sm font-black text-gray-400 uppercase tracking-widest flex items-center gap-2">
                                <Home className="w-4 h-4" /> Caregiver Info
                            </h3>
                            <div className="space-y-3">
                                <div>
                                    <p className="text-sm font-bold">{child.caregiver_name}</p>
                                    <p className="text-xs text-gray-500">{child.caregiver_relationship}</p>
                                </div>
                                <div className="flex gap-4">
                                    {child.caregiver_phone && (
                                        <div className="flex items-center gap-1.5 text-xs text-gray-600">
                                            <Phone className="w-3.5 h-3.5 text-gray-400" />
                                            {child.caregiver_phone}
                                        </div>
                                    )}
                                    {child.caregiver_email && (
                                        <div className="flex items-center gap-1.5 text-xs text-gray-600">
                                            <TrendingUp className="w-3.5 h-3.5 text-gray-400" />
                                            {child.caregiver_email}
                                        </div>
                                    )}
                                </div>
                                {child.caregiver_additional_info && (
                                    <div className="p-3 bg-gray-50 rounded-xl border border-gray-100 italic text-[11px] text-gray-600">
                                        {child.caregiver_additional_info}
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Risk Trends Chart */}
                    <div className="space-y-4">
                        <h3 className="text-sm font-black text-gray-400 uppercase tracking-widest flex items-center gap-2">
                            <TrendingUp className="w-4 h-4" /> Risk Score Trends
                        </h3>
                        <div className="bg-white border border-gray-100 rounded-2xl p-4 h-64">
                            {loading ? (
                                <div className="h-full flex items-center justify-center">
                                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600" />
                                </div>
                            ) : growthData.length > 0 ? (
                                <ResponsiveContainer width="100%" height="100%">
                                    <LineChart data={growthData}>
                                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                                        <XAxis
                                            dataKey="date"
                                            tick={{ fontSize: 10 }}
                                            tickFormatter={(val) => new Date(val).toLocaleDateString()}
                                        />
                                        <YAxis domain={[0, 1]} tick={{ fontSize: 10 }} />
                                        <Tooltip
                                            labelFormatter={(val) => new Date(val).toLocaleDateString()}
                                            contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                                        />
                                        <Line
                                            type="monotone"
                                            dataKey="risk_score"
                                            stroke="#ef4444"
                                            strokeWidth={3}
                                            dot={{ r: 4, fill: '#ef4444' }}
                                            activeDot={{ r: 6 }}
                                            name="Risk Probability"
                                        />
                                    </LineChart>
                                </ResponsiveContainer>
                            ) : (
                                <div className="h-full flex flex-col items-center justify-center text-gray-400 gap-2">
                                    <AlertCircle className="w-8 h-8 opacity-20" />
                                    <p className="text-sm font-medium">Insufficient data for trend analysis</p>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Assessment History Table */}
                    <div className="space-y-4">
                        <h3 className="text-sm font-black text-gray-400 uppercase tracking-widest flex items-center gap-2">
                            <ClipboardList className="w-4 h-4" /> Assessment History
                        </h3>
                        <div className="border border-gray-100 rounded-2xl overflow-hidden">
                            <table className="min-w-full divide-y divide-gray-100 text-sm">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th className="px-4 py-3 text-left text-xs font-bold text-gray-500 uppercase">Cycle</th>
                                        <th className="px-4 py-3 text-left text-xs font-bold text-gray-500 uppercase">Date</th>
                                        <th className="px-4 py-3 text-left text-xs font-bold text-gray-500 uppercase">Age (mo)</th>
                                        <th className="px-4 py-3 text-left text-xs font-bold text-gray-500 uppercase">Composite DQ</th>
                                        <th className="px-4 py-3 text-left text-xs font-bold text-gray-500 uppercase">Risk Tier</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-50">
                                    {assessments.length === 0 ? (
                                        <tr><td colSpan={5} className="py-8 text-center text-gray-400 italic">No assessments yet</td></tr>
                                    ) : (
                                        assessments.map((a, idx) => (
                                            <tr key={idx} className="hover:bg-gray-50">
                                                <td className="px-4 py-3 font-medium">#{a.assessment_cycle}</td>
                                                <td className="px-4 py-3">{new Date(a.assessment_date).toLocaleDateString()}</td>
                                                <td className="px-4 py-3">{a.age_months}</td>
                                                <td className="px-4 py-3 font-bold text-primary-600">{a.composite_dq}</td>
                                                <td className="px-4 py-3">
                                                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-black uppercase ${a.latest_prediction?.risk_tier === 'High Risk' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
                                                        }`}>
                                                        {a.latest_prediction?.risk_tier || 'N/A'}
                                                    </span>
                                                </td>
                                            </tr>
                                        ))
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <div className="p-4 bg-gray-50 border-t border-gray-100 flex justify-end">
                    <button
                        onClick={onClose}
                        className="px-6 py-2 bg-gray-900 text-white font-bold rounded-xl hover:bg-black transition-all"
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ChildDetailsModal;
