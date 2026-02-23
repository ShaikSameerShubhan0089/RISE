import React, { useEffect, useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { dashboardAPI } from '../../utils/api';
import SummaryCards from '../../components/dashboard/SummaryCards';
import ChildrenTable from '../../components/dashboard/ChildrenTable';
import InterventionsTable from '../../components/dashboard/InterventionsTable';
import UsersTable from '../../components/dashboard/UsersTable';
import ChildGrowthChart from '../../components/dashboard/ChildGrowthChart';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, Cell,
    PieChart, Pie, ResponsiveContainer,
} from 'recharts';
import { Plus, UserPlus, ClipboardList, X, Eye, EyeOff, AlertCircle, CheckCircle2 } from 'lucide-react';
import { usersAPI } from '../../utils/api';
import ChildRegistrationForm from '../../components/dashboard/ChildRegistrationForm';
/* ── colour palette ──────────────────────────────────────────────────────── */
const GENDER_COLORS = { Male: '#3b82f6', Female: '#ec4899', Other: '#8b5cf6' };
const RISK_COLORS = {
    'Low Risk': '#22c55e',
    'Mild Concern': '#f59e0b',
    'Moderate Risk': '#f97316',
    'High Risk': '#ef4444',
    'No Assessment': '#94a3b8',
};

/* ── helpers ─────────────────────────────────────────────────────────────── */
const ageGroup = (dob) => {
    if (!dob) return 'Unknown';
    const months = Math.floor((Date.now() - new Date(dob)) / (1000 * 60 * 60 * 24 * 30.44));
    if (months < 12) return '0–12 mo';
    if (months < 24) return '1–2 yr';
    if (months < 36) return '2–3 yr';
    if (months < 48) return '3–4 yr';
    return '4+ yr';
};

const AGE_ORDER = ['0–12 mo', '1–2 yr', '2–3 yr', '3–4 yr', '4+ yr'];

const buildAgeGenderData = (children) => {
    const map = {};
    children.forEach(c => {
        const grp = ageGroup(c.dob);
        if (!map[grp]) map[grp] = { group: grp, Male: 0, Female: 0, Other: 0 };
        map[grp][c.gender] = (map[grp][c.gender] || 0) + 1;
    });
    return AGE_ORDER.filter(g => map[g]).map(g => map[g]);
};

const buildRiskData = (charts) =>
    (charts?.improvement_status || []).map(r => ({ name: r.status, value: r.count }));

const buildGenderData = (charts) =>
    (charts?.gender_distribution || []).map(g => ({
        name: g.gender,
        value: g.count,
    }));

/* ── custom tooltip ──────────────────────────────────────────────────────── */
const PieLabel = ({ cx, cy, midAngle, outerRadius, percent, name }) => {
    if (percent < 0.05) return null;
    const RADIAN = Math.PI / 180;
    const r = outerRadius + 22;
    const x = cx + r * Math.cos(-midAngle * RADIAN);
    const y = cy + r * Math.sin(-midAngle * RADIAN);
    return (
        <text x={x} y={y} fill="#374151" textAnchor={x > cx ? 'start' : 'end'} dominantBaseline="central" fontSize={11}>
            {name} ({(percent * 100).toFixed(0)}%)
        </text>
    );
};

/* ══════════════════════════════════════════════════════════════════════════ */
const AnganwadiWorkerDashboard = () => {
    const { user } = useAuth();

    const [summary, setSummary] = useState({});
    const [children, setChildren] = useState([]);
    const [interventions, setInterventions] = useState([]);
    const [users, setUsers] = useState([]);
    const [charts, setCharts] = useState({});
    const [loading, setLoading] = useState(true);
    const [tab, setTab] = useState('analytics');

    const [showRegister, setShowRegister] = useState(false);
    const [showAssessment, setShowAssessment] = useState(false);
    const [showUserForm, setShowUserForm] = useState(false);
    const [editingUser, setEditingUser] = useState(null);
    const [resetModal, setResetModal] = useState(null);
    const [newPassword, setNewPassword] = useState('');
    const [showPwd, setShowPwd] = useState(false);
    const [toast, setToast] = useState(null);
    const [formError, setFormError] = useState('');
    const [saving, setSaving] = useState(false);

    const [userForm, setUserForm] = useState({
        full_name: '', email: '', role: 'parent', password: '',
        state_id: user?.state_id, district_id: user?.district_id,
        mandal_id: user?.mandal_id, center_id: user?.center_id
    });

    const showToast = (message, type = 'success') => {
        setToast({ message, type });
        setTimeout(() => setToast(null), 3500);
    };

    const generatePass = () => {
        const chars = 'ABCDEFGHJKMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789@#!';
        return Array.from({ length: 12 }, () => chars[Math.floor(Math.random() * chars.length)]).join('');
    };

    /* load on mount -------------------------------------------------------- */
    const fetchData = () => {
        setLoading(true);
        Promise.all([
            dashboardAPI.getSummary(),
            dashboardAPI.getChildren(),
            dashboardAPI.getInterventions(),
            dashboardAPI.getUsers(),
            dashboardAPI.getCharts(),
        ]).then(([s, c, i, u, ch]) => {
            setSummary(s.data);
            setChildren(c.data);
            setInterventions(i.data);
            setUsers(u.data);
            setCharts(ch.data);
        }).catch(() => { })
            .finally(() => setLoading(false));
    };

    useEffect(() => {
        fetchData();
    }, []);

    /* handlers ------------------------------------------------------------- */
    const openAddUser = () => {
        setEditingUser(null);
        setUserForm({
            full_name: '', email: '', role: 'parent', password: generatePass(),
            state_id: user?.state_id, district_id: user?.district_id,
            mandal_id: user?.mandal_id, center_id: user?.center_id
        });
        setFormError('');
        setShowUserForm(true);
    };

    const openEditUser = (u) => {
        setEditingUser(u);
        setUserForm({
            full_name: u.full_name, email: u.email, role: u.role, password: '',
            state_id: u.state_id, district_id: u.district_id,
            mandal_id: u.mandal_id, center_id: u.center_id
        });
        setFormError('');
        setShowUserForm(true);
    };

    const handleSaveUser = async (e) => {
        e.preventDefault();
        setSaving(true);
        try {
            if (editingUser) {
                await usersAPI.update(editingUser.user_id, userForm);
                showToast('User updated successfully');
            } else {
                await usersAPI.create(userForm);
                showToast('User created successfully');
            }
            setShowUserForm(false);
            fetchData();
        } catch (err) {
            setFormError(err.response?.data?.detail || 'Failed to save user');
        } finally {
            setSaving(false);
        }
    };

    const handleDeleteUser = async (u) => {
        if (!window.confirm(`Delete ${u.full_name}?`)) return;
        try {
            await usersAPI.delete(u.user_id);
            showToast('User deleted');
            fetchData();
        } catch (err) {
            showToast(err.response?.data?.detail || 'Failed to delete', 'error');
        }
    };

    const handleToggleStatus = async (u) => {
        try {
            await usersAPI.toggleStatus(u.user_id);
            showToast('Status updated');
            fetchData();
        } catch (err) {
            showToast('Failed to toggle status', 'error');
        }
    };

    const handleResetPassword = async () => {
        try {
            await usersAPI.resetPassword(resetModal.user_id, newPassword);
            showToast('Password reset successful');
            setResetModal(null);
        } catch {
            showToast('Failed to reset password', 'error');
        }
    };

    if (loading) return (
        <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-green-600" />
        </div>
    );

    /* derived chart data --------------------------------------------------- */
    const ageGenderData = buildAgeGenderData(children);
    const riskPieData = buildRiskData(charts);
    const genderData = buildGenderData(charts);

    const tabs = [
        { id: 'analytics', label: '📊 Analytics' },
        { id: 'children', label: '👶 Children' },
        { id: 'assessments', label: '📋 Assessments' },
        { id: 'interventions', label: '🏥 Interventions' },
        { id: 'staff', label: '👥 Parents & Staff' },
        { id: 'growth', label: '📈 Growth' },
    ];

    return (
        <div className="p-6 space-y-6">
            {toast && (
                <div className={`fixed top-5 right-5 z-50 flex items-center gap-3 px-5 py-3.5 rounded-xl shadow-lg text-sm font-medium transition-all
                    ${toast.type === 'error' ? 'bg-red-600 text-white' : 'bg-emerald-600 text-white'}`}>
                    {toast.type === 'error' ? <AlertCircle className="w-4 h-4" /> : <CheckCircle2 className="w-4 h-4" />}
                    {toast.message}
                </div>
            )}

            {/* Header */}
            <div className="bg-gradient-to-r from-green-600 to-teal-600 rounded-2xl p-6 text-white flex flex-wrap justify-between items-center gap-4">
                <div>
                    <h1 className="text-2xl font-bold">Welcome, {user?.full_name}! 👋</h1>
                    <p className="text-green-100 mt-1 text-sm">
                        Anganwadi Worker — {user?.center_name || 'your centre overview'}
                    </p>
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={() => setShowRegister(true)}
                        className="bg-white/20 hover:bg-white/30 backdrop-blur-sm px-4 py-2 rounded-xl text-sm font-bold transition-all flex items-center gap-2"
                    >
                        <UserPlus className="w-4 h-4" />
                        Register Child
                    </button>
                    <button
                        onClick={() => setShowAssessment(true)}
                        className="bg-white px-4 py-2 rounded-xl text-green-700 text-sm font-bold shadow-lg hover:bg-green-50 transition-all flex items-center gap-2"
                    >
                        <ClipboardList className="w-4 h-4" />
                        New Assessment
                    </button>
                </div>
            </div>

            {/* Summary cards */}
            <SummaryCards
                data={summary}
                keys={['total_children', 'active_children', 'total_interventions', 'active_interventions', 'total_assessments', 'total_centers']}
            />

            {/* Tabs */}
            <div className="border-b border-gray-200">
                <nav className="flex gap-1 flex-wrap">
                    {tabs.map(t => (
                        <button
                            key={t.id}
                            onClick={() => setTab(t.id)}
                            className={`px-4 py-2.5 text-sm font-medium rounded-t-lg transition-colors ${tab === t.id ? 'bg-green-600 text-white' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                                }`}
                        >
                            {t.label}
                        </button>
                    ))}
                </nav>
            </div>

            {/* ── Analytics tab ───────────────────────────────────────────── */}
            {tab === 'analytics' && (
                <div className="space-y-6">

                    {/* Row 1: Age-Gender Bar + Risk Pie */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                        {/* Bar chart: children by age group & gender */}
                        <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
                            <h3 className="text-sm font-semibold text-gray-700 mb-4">Children by Age Group & Gender</h3>
                            {ageGenderData.length === 0 ? (
                                <p className="text-gray-400 text-sm text-center py-10">No data</p>
                            ) : (
                                <ResponsiveContainer width="100%" height={240}>
                                    <BarChart data={ageGenderData} margin={{ top: 5, right: 10, bottom: 5, left: 0 }}>
                                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
                                        <XAxis dataKey="group" tick={{ fontSize: 11 }} />
                                        <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
                                        <Tooltip />
                                        <Legend iconSize={10} wrapperStyle={{ fontSize: 11 }} />
                                        <Bar dataKey="Male" fill={GENDER_COLORS.Male} radius={[4, 4, 0, 0]} />
                                        <Bar dataKey="Female" fill={GENDER_COLORS.Female} radius={[4, 4, 0, 0]} />
                                        <Bar dataKey="Other" fill={GENDER_COLORS.Other} radius={[4, 4, 0, 0]} />
                                    </BarChart>
                                </ResponsiveContainer>
                            )}
                        </div>

                        {/* Pie chart: risk levels */}
                        <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
                            <h3 className="text-sm font-semibold text-gray-700 mb-4">Risk Level Distribution</h3>
                            {genderData.length === 0 && riskPieData.length === 0 ? (
                                <p className="text-gray-400 text-sm text-center py-10">No risk data</p>
                            ) : (
                                <ResponsiveContainer width="100%" height={240}>
                                    <PieChart>
                                        <Pie
                                            data={riskPieData.length ? riskPieData : genderData}
                                            cx="50%" cy="50%"
                                            outerRadius={85}
                                            dataKey="value"
                                            labelLine={false}
                                            label={<PieLabel />}
                                        >
                                            {(riskPieData.length ? riskPieData : genderData).map((entry, i) => (
                                                <Cell key={i} fill={
                                                    RISK_COLORS[entry.name] ||
                                                    GENDER_COLORS[entry.name] ||
                                                    ['#6366f1', '#22c55e', '#f59e0b', '#ef4444'][i % 4]
                                                } />
                                            ))}
                                        </Pie>
                                        <Tooltip />
                                    </PieChart>
                                </ResponsiveContainer>
                            )}
                        </div>
                    </div>

                    {/* Row 2: Intervention categories bar */}
                    {charts?.intervention_categories?.length > 0 && (
                        <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
                            <h3 className="text-sm font-semibold text-gray-700 mb-4">Interventions by Category</h3>
                            <ResponsiveContainer width="100%" height={200}>
                                <BarChart data={charts.intervention_categories} layout="vertical"
                                    margin={{ top: 0, right: 20, bottom: 0, left: 120 }}>
                                    <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f3f4f6" />
                                    <XAxis type="number" tick={{ fontSize: 11 }} allowDecimals={false} />
                                    <YAxis dataKey="category" type="category" tick={{ fontSize: 11 }} width={120} />
                                    <Tooltip />
                                    <Bar dataKey="count" name="Count" fill="#22c55e" radius={[0, 4, 4, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    )}

                    {/* Quick stats row */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {[
                            { label: 'Total Children', value: summary.total_children ?? 0, color: 'text-blue-600' },
                            { label: 'Active Children', value: summary.active_children ?? 0, color: 'text-green-600' },
                            { label: 'Total Assessments', value: summary.total_assessments ?? 0, color: 'text-purple-600' },
                            { label: 'Active Interventions', value: summary.active_interventions ?? 0, color: 'text-orange-600' },
                        ].map(s => (
                            <div key={s.label} className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm text-center">
                                <p className={`text-2xl font-bold ${s.color}`}>{s.value}</p>
                                <p className="text-xs text-gray-500 mt-1">{s.label}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {tab === 'children' && (
                <div className="space-y-4">
                    <div className="flex justify-end">
                        <button
                            onClick={() => setShowRegister(true)}
                            className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-green-700 transition-all flex items-center gap-2"
                        >
                            <Plus className="w-4 h-4" /> Register New Child
                        </button>
                    </div>
                    <ChildrenTable data={children} />
                </div>
            )}
            {tab === 'assessments' && (
                <div className="bg-white rounded-2xl border border-gray-100 p-12 text-center space-y-4 shadow-sm">
                    <div className="w-20 h-20 bg-green-50 rounded-full flex items-center justify-center mx-auto">
                        <ClipboardList className="w-10 h-10 text-green-600" />
                    </div>
                    <h2 className="text-xl font-bold text-gray-900">Digital Assessments Portal</h2>
                    <p className="text-gray-500 max-w-sm mx-auto">
                        Run real-time AI risk screening or escalation predictions for children in your centre.
                    </p>
                    <button
                        onClick={() => setShowAssessment(true)}
                        className="bg-green-600 text-white px-8 py-3 rounded-2xl font-bold hover:bg-green-700 transition-all shadow-xl shadow-green-100"
                    >
                        Start New Assessment
                    </button>
                </div>
            )}
            {tab === 'interventions' && <InterventionsTable data={interventions} />}
            {tab === 'staff' && (
                <div className="space-y-4">
                    <div className="flex justify-end">
                        <button
                            onClick={openAddUser}
                            className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-green-700 transition-all flex items-center gap-2"
                        >
                            <UserPlus className="w-4 h-4" /> Add Parent Account
                        </button>
                    </div>
                    <UsersTable
                        data={users}
                        showActions
                        onEdit={openEditUser}
                        onToggleStatus={handleToggleStatus}
                        onDelete={handleDeleteUser}
                        onResetPassword={(u) => {
                            setResetModal(u);
                            setNewPassword(generatePass());
                        }}
                    />
                </div>
            )}
            {tab === 'growth' && <ChildGrowthChart children={children} />}

            {/* Modals */}
            {showRegister && (
                <ChildRegistrationForm
                    user={user}
                    onClose={() => setShowRegister(false)}
                    onSuccess={fetchData}
                />
            )}
            {showAssessment && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
                    <div className="bg-white rounded-2xl p-8 max-w-md text-center space-y-4 shadow-2xl">
                        <ClipboardList className="w-12 h-12 text-green-600 mx-auto" />
                        <h2 className="text-xl font-bold">Assessments</h2>
                        <p className="text-gray-500">The assessment form is being updated. Please use the sidebar 'Assessments' link for now.</p>
                        <button onClick={() => setShowAssessment(false)} className="bg-green-600 text-white px-6 py-2 rounded-xl font-bold">Close</button>
                    </div>
                </div>
            )}

            {/* User Form Panel */}
            {showUserForm && (
                <div className="fixed inset-0 z-50 flex">
                    <div className="flex-1 bg-black/40" onClick={() => setShowUserForm(false)} />
                    <div className="w-full max-w-lg bg-white shadow-2xl flex flex-col p-6 overflow-y-auto">
                        <div className="flex justify-between items-center mb-6">
                            <h2 className="text-xl font-bold">{editingUser ? 'Edit Parent' : 'Add Parent'}</h2>
                            <button onClick={() => setShowUserForm(false)}><X className="w-6 h-6 text-gray-400" /></button>
                        </div>
                        <form onSubmit={handleSaveUser} className="space-y-4">
                            {formError && <div className="p-3 bg-red-50 text-red-600 text-sm rounded-lg">{formError}</div>}
                            <div className="space-y-1">
                                <label className="text-xs font-bold text-gray-500 uppercase">Full Name</label>
                                <input
                                    value={userForm.full_name}
                                    onChange={e => setUserForm(f => ({ ...f, full_name: e.target.value }))}
                                    className="w-full border rounded-lg px-3 py-2 text-sm"
                                    required
                                />
                            </div>
                            <div className="space-y-1">
                                <label className="text-xs font-bold text-gray-500 uppercase">Email</label>
                                <input
                                    type="email"
                                    value={userForm.email}
                                    onChange={e => setUserForm(f => ({ ...f, email: e.target.value }))}
                                    className="w-full border rounded-lg px-3 py-2 text-sm"
                                    required
                                />
                            </div>
                            <div className="space-y-1">
                                <label className="text-xs font-bold text-gray-500 uppercase">Password</label>
                                <div className="flex gap-2">
                                    <input
                                        type={showPwd ? 'text' : 'password'}
                                        value={userForm.password}
                                        onChange={e => setUserForm(f => ({ ...f, password: e.target.value }))}
                                        className="w-full border rounded-lg px-3 py-2 text-sm"
                                        placeholder={editingUser ? '(Leave blank to keep)' : ''}
                                        required={!editingUser}
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowPwd(!showPwd)}
                                        className="p-2 border rounded-lg text-gray-400"
                                    >
                                        {showPwd ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                    </button>
                                </div>
                            </div>
                            <button
                                type="submit"
                                disabled={saving}
                                className="w-full bg-green-600 text-white py-2.5 rounded-xl font-bold mt-4 disabled:opacity-50"
                            >
                                {saving ? 'Saving...' : editingUser ? 'Update Parent' : 'Create Parent'}
                            </button>
                        </form>
                    </div>
                </div>
            )}

            {/* Reset Password Modal */}
            {resetModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
                    <div className="bg-white rounded-2xl p-6 w-full max-w-sm space-y-4 shadow-2xl">
                        <h2 className="text-lg font-bold">Reset Password</h2>
                        <p className="text-sm text-gray-500">New password for {resetModal.full_name}:</p>
                        <input
                            type="text"
                            value={newPassword}
                            onChange={e => setNewPassword(e.target.value)}
                            className="w-full border rounded-lg px-3 py-2 font-mono text-sm"
                        />
                        <div className="flex gap-3">
                            <button onClick={() => setResetModal(null)} className="flex-1 py-2 text-sm font-bold text-gray-500">Cancel</button>
                            <button onClick={handleResetPassword} className="flex-1 py-2 text-sm font-bold bg-amber-500 text-white rounded-lg">Reset</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AnganwadiWorkerDashboard;
