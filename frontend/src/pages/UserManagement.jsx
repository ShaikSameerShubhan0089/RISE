import React, { useState, useEffect } from 'react';
import { usersAPI, dashboardAPI } from '../utils/api';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import UsersTable from '../components/dashboard/UsersTable';
import VoiceButton from '../components/common/VoiceButton';
import {
    UserPlus, X, Eye, EyeOff, AlertCircle, CheckCircle2,
    Users, ChevronDown
} from 'lucide-react';

const getRoles = (t) => [
    { value: 'state_admin', label: t('user_mgmt.roles.state_admin') },
    { value: 'district_officer', label: t('user_mgmt.roles.district_officer') },
    { value: 'supervisor', label: t('user_mgmt.roles.supervisor') },
    { value: 'anganwadi_worker', label: t('user_mgmt.roles.anganwadi_worker') },
    { value: 'parent', label: t('user_mgmt.roles.parent') },
];

const generatePassword = () => {
    const chars = 'ABCDEFGHJKMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789@#!';
    return Array.from({ length: 12 }, () => chars[Math.floor(Math.random() * chars.length)]).join('');
};

const InputField = ({ label, required, children }) => (
    <div className="space-y-1">
        <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
            {label}{required && <span className="text-red-500 ml-0.5">*</span>}
        </label>
        {children}
    </div>
);

const UserManagement = () => {
    const { user } = useAuth();
    const { t } = useLanguage();
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [editingUser, setEditingUser] = useState(null);
    const [toast, setToast] = useState(null);

    // Location options
    const [districts, setDistricts] = useState([]);
    const [mandals, setMandals] = useState([]);
    const [centers, setCenters] = useState([]);

    // Table Filter Location options
    const [filterMandals, setFilterMandals] = useState([]);
    const [filterCenters, setFilterCenters] = useState([]);

    // Reset password modal
    const [resetModal, setResetModal] = useState(null); // { user }
    const [newPassword, setNewPassword] = useState('');
    const [showPwd, setShowPwd] = useState(false);

    // Form state
    const emptyForm = {
        full_name: '', email: '', role: 'anganwadi_worker',
        password: '', state_id: null, district_id: null, mandal_id: null, center_id: null,
    };
    const [form, setForm] = useState(emptyForm);
    const [formError, setFormError] = useState('');
    const [saving, setSaving] = useState(false);

    const ROLES_LIST = getRoles(t);
    const availableRoles = ROLES_LIST.filter(r => {
        if (user?.role === 'state_admin') {
            return ['district_officer', 'supervisor', 'anganwadi_worker', 'parent'].includes(r.value);
        }
        if (user?.role === 'district_officer') {
            return ['supervisor', 'anganwadi_worker', 'parent'].includes(r.value);
        }
        if (user?.role === 'supervisor') {
            return ['anganwadi_worker', 'parent'].includes(r.value);
        }
        if (user?.role === 'anganwadi_worker') {
            return ['parent'].includes(r.value);
        }
        return true; // system_admin can see all
    });

    const needsDistrict = ['district_officer', 'supervisor', 'anganwadi_worker', 'parent'].includes(form.role);
    const needsMandal = ['supervisor', 'anganwadi_worker', 'parent'].includes(form.role);
    const needsCenter = ['anganwadi_worker', 'parent'].includes(form.role);

    useEffect(() => {
        fetchUsers();
        const fetchLocationData = async () => {
            try {
                // Fetch districts ONLY if user has permission
                if (user?.role === 'system_admin') {
                    const res = await dashboardAPI.getDistricts();
                    setDistricts(res.data);
                } else if (user?.role === 'state_admin') {
                    const res = await dashboardAPI.getDistrictsForState();
                    setDistricts(res.data);
                }

                // If district_officer, pre-fetch mandals for their district
                if (user?.role === 'district_officer' && user.district_id) {
                    const mRes = await dashboardAPI.getMandals(user.district_id);
                    setMandals(mRes.data);
                    setFilterMandals(mRes.data); // Initialize filter list
                }

                // If supervisor, pre-fetch centers for their mandal
                if (user?.role === 'supervisor' && user.mandal_id) {
                    const cRes = await dashboardAPI.getCentersForMandal(user.mandal_id);
                    setCenters(cRes.data);
                    setFilterCenters(cRes.data); // Initialize filter list
                }
            } catch (err) {
                console.error("Failed to fetch location data:", err);
            }
        };
        fetchLocationData();
    }, [user]);

    const fetchUsers = async () => {
        setLoading(true);
        try {
            const res = await usersAPI.list({});
            setUsers(res.data);
        } catch (e) {
            showToast('Failed to load users', 'error');
        } finally {
            setLoading(false);
        }
    };

    const showToast = (message, type = 'success') => {
        setToast({ message, type });
        setTimeout(() => setToast(null), 3500);
    };

    const handleRoleChange = (role) => {
        setForm(f => {
            const newState = { ...f, role };
            // Reset fields that are NOT fixed by the current login user's role
            if (user?.role === 'system_admin') {
                newState.district_id = null;
                newState.mandal_id = null;
                newState.center_id = null;
            } else if (user?.role === 'state_admin') {
                newState.district_id = null;
                newState.mandal_id = null;
                newState.center_id = null;
            } else if (user?.role === 'district_officer') {
                newState.mandal_id = null;
                newState.center_id = null;
            } else if (user?.role === 'supervisor') {
                newState.center_id = null;
            }
            return newState;
        });

        // Re-fetch or clear sub-location lists
        if (user?.role === 'system_admin' || user?.role === 'state_admin') {
            setMandals([]);
            setCenters([]);
        } else if (user?.role === 'district_officer') {
            setCenters([]);
        }
    };

    const handleDistrictChange = async (districtId) => {
        setForm(f => ({ ...f, district_id: districtId, mandal_id: null, center_id: null }));
        setCenters([]);
        if (districtId) {
            try {
                const res = await dashboardAPI.getMandals(districtId);
                setMandals(res.data);
            } catch { }
        }
    };

    const handleMandalChange = async (mandalId) => {
        setForm(f => ({ ...f, mandal_id: mandalId, center_id: null }));
        if (mandalId) {
            try {
                // Fetch centers by mandal
                const res = await dashboardAPI.getCentersForMandal(mandalId);
                setCenters(res.data);
            } catch { }
        }
    };

    const handleFilterDistrictChange = async (districtId) => {
        setFilterCenters([]);
        if (districtId) {
            try {
                const res = await dashboardAPI.getMandals(districtId);
                setFilterMandals(res.data);
            } catch { }
        } else {
            setFilterMandals([]);
        }
    };

    const handleFilterMandalChange = async (mandalId) => {
        if (mandalId) {
            try {
                const res = await dashboardAPI.getCentersForMandal(mandalId);
                setFilterCenters(res.data);
            } catch { }
        } else {
            setFilterCenters([]);
        }
    };

    const openAddForm = () => {
        setEditingUser(null);
        let defaultState = null;
        let defaultDistrict = null;
        let defaultMandal = null;
        let defaultCenter = null;
        let defaultRole = 'anganwadi_worker';

        if (user?.role === 'state_admin') {
            defaultState = user.state_id;
            defaultRole = 'district_officer';
        } else if (user?.role === 'district_officer') {
            defaultState = user.state_id;
            defaultDistrict = user.district_id;
            defaultRole = 'supervisor';
        } else if (user?.role === 'supervisor') {
            defaultState = user.state_id;
            defaultDistrict = user.district_id;
            defaultMandal = user.mandal_id;
            defaultRole = 'anganwadi_worker';
        } else if (user?.role === 'anganwadi_worker') {
            defaultState = user.state_id;
            defaultDistrict = user.district_id;
            defaultMandal = user.mandal_id;
            defaultCenter = user.center_id;
            defaultRole = 'parent';
        }

        setForm({
            ...emptyForm,
            password: generatePassword(),
            state_id: defaultState,
            district_id: defaultDistrict,
            mandal_id: defaultMandal,
            center_id: defaultCenter,
            role: defaultRole
        });
        setFormError('');
        setShowForm(true);
    };

    const openEditForm = (u) => {
        setEditingUser(u);
        setForm({
            full_name: u.full_name || '',
            email: u.email || '',
            role: u.role || 'anganwadi_worker',
            password: '',
            state_id: u.state_id || null,
            district_id: u.district_id || null,
            mandal_id: u.mandal_id || null,
            center_id: u.center_id || null,
        });
        setFormError('');
        setShowForm(true);
    };

    const handleSave = async (e) => {
        e.preventDefault();
        if (!form.full_name || !form.email) {
            setFormError('Full Name and Email are required.');
            return;
        }
        if (!editingUser && !form.password) {
            setFormError('Password is required.');
            return;
        }
        setSaving(true);
        setFormError('');
        try {
            if (editingUser) {
                // Remove password if empty to avoid validation error or accidental reset
                const updatePayload = { ...form };
                if (!updatePayload.password) {
                    delete updatePayload.password;
                }
                await usersAPI.update(editingUser.user_id, updatePayload);
                showToast(`${form.full_name} updated successfully`);
            } else {
                await usersAPI.create(form);
                showToast(`${form.full_name} created successfully`);
            }
            setShowForm(false);
            fetchUsers();
        } catch (err) {
            setFormError(err.response?.data?.detail || 'Failed to save user.');
        } finally {
            setSaving(false);
        }
    };

    const handleToggleStatus = async (u) => {
        try {
            await usersAPI.toggleStatus(u.user_id);
            const newStatus = u.status === 'Active' ? 'Revoked' : 'Active';
            showToast(`${u.full_name} is now ${newStatus}`);
            fetchUsers();
        } catch (err) {
            showToast(err.response?.data?.detail || 'Failed to update status', 'error');
        }
    };

    const handleDelete = async (u) => {
        if (!window.confirm(`Are you sure you want to permanently DELETE ${u.full_name}? This action cannot be undone.`)) return;
        try {
            await usersAPI.delete(u.user_id);
            showToast(`${u.full_name} deleted successfully`);
            fetchUsers();
        } catch (err) {
            showToast(err.response?.data?.detail || 'Failed to delete user', 'error');
        }
    };

    const openResetModal = (u) => {
        setResetModal({ user: u });
        setNewPassword(generatePassword());
        setShowPwd(false);
    };

    const handleResetPassword = async () => {
        if (!newPassword || newPassword.length < 8) {
            showToast('Password must be at least 8 characters', 'error');
            return;
        }
        try {
            await usersAPI.resetPassword(resetModal.user.user_id, newPassword);
            showToast(`Password reset for ${resetModal.user.full_name}`);
            setResetModal(null);
        } catch (err) {
            showToast(err.response?.data?.detail || 'Failed to reset password', 'error');
        }
    };


    return (
        <div className="p-6 space-y-6">
            {/* Toast */}
            {toast && (
                <div className={`fixed top-5 right-5 z-50 flex items-center gap-3 px-5 py-3.5 rounded-xl shadow-lg text-sm font-medium transition-all
                    ${toast.type === 'error' ? 'bg-red-600 text-white' : 'bg-emerald-600 text-white'}`}>
                    {toast.type === 'error' ? <AlertCircle className="w-4 h-4 flex-shrink-0" /> : <CheckCircle2 className="w-4 h-4 flex-shrink-0" />}
                    {toast.message}
                </div>
            )}

            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                    <div className="p-3 bg-primary-100 rounded-xl">
                        <Users className="w-6 h-6 text-primary-600" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900">{t('user_mgmt.title')}</h1>
                        <p className="text-sm text-gray-500">{t('user_mgmt.sub')}</p>
                    </div>
                    <VoiceButton content={`${t('user_mgmt.title')}. ${availableRoles.length} ${t('user_mgmt.stats.revoked').toLowerCase()} roles available. ${t('user_mgmt.fields.full_name')}`} />
                </div>
                {!showForm && (
                    <button
                        onClick={() => { setEditingUser(null); setForm(emptyForm); setShowForm(true); }}
                        className="flex items-center justify-center gap-2 px-4 py-2.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition shadow-md"
                    >
                        <UserPlus className="w-4 h-4" />
                        <span className="font-medium">{t('user_mgmt.add_user')}</span>
                    </button>
                )}
            </div>

            {/* Stats strip */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                    { label: t('user_mgmt.stats.total'), value: users.length, color: 'text-indigo-600' },
                    { label: t('user_mgmt.stats.active'), value: users.filter(u => u.status === 'Active').length, color: 'text-emerald-600' },
                    { label: t('user_mgmt.stats.revoked'), value: users.filter(u => u.status === 'Revoked').length, color: 'text-red-500' },
                    { label: t('user_mgmt.stats.awc'), value: users.filter(u => u.role === 'anganwadi_worker').length, color: 'text-green-600' },
                ].map(stat => (
                    <div key={stat.label} className="bg-white rounded-xl border border-gray-200 px-5 py-4">
                        <p className="text-xs font-semibold text-gray-500 uppercase">{stat.label}</p>
                        <p className={`text-3xl font-bold mt-1 ${stat.color}`}>{stat.value}</p>
                    </div>
                ))}
            </div>

            {/* Users Table */}
            {loading ? (
                <div className="flex items-center justify-center h-48">
                    <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600" />
                </div>
            ) : (
                <UsersTable
                    data={users}
                    showActions
                    onEdit={openEditForm}
                    onToggleStatus={handleToggleStatus}
                    onResetPassword={openResetModal}
                    onDelete={handleDelete}
                    districts={districts}
                    mandals={filterMandals}
                    centers={filterCenters}
                    onDistrictFilterChange={handleFilterDistrictChange}
                    onMandalFilterChange={handleFilterMandalChange}
                    currentUser={user}
                />
            )}

            {/* ── Add / Edit User Slide-in Panel ─────────────────────────── */}
            {showForm && (
                <div className="fixed inset-0 z-40 flex">
                    <div className="flex-1 bg-black/40" onClick={() => setShowForm(false)} />
                    <div className="w-full max-w-lg bg-white shadow-2xl flex flex-col overflow-y-auto">
                        {/* Panel header */}
                        <div className="flex items-center justify-between px-6 py-5 border-b border-gray-100 bg-white sticky top-0 z-10">
                            <h3 className="text-lg font-semibold text-gray-900">
                                {editingUser ? t('user_mgmt.edit_user') : t('user_mgmt.add_user')}
                            </h3>
                            <button onClick={() => setShowForm(false)} className="p-2 rounded-lg hover:bg-gray-100 transition-colors">
                                <X className="w-5 h-5 text-gray-500" />
                            </button>
                        </div>

                        <form onSubmit={handleSave} className="flex flex-col gap-5 px-6 py-6 flex-1">
                            {formError && (
                                <div className="flex items-start gap-2 bg-red-50 text-red-700 border border-red-200 rounded-lg px-4 py-3 text-sm">
                                    <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                                    {formError}
                                </div>
                            )}

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <InputField label={t('user_mgmt.fields.full_name')} required>
                                    <input
                                        type="text"
                                        required
                                        value={form.full_name}
                                        onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
                                        placeholder={t('user_mgmt.fields.full_name_placeholder')}
                                    />
                                </InputField>

                                <InputField label={t('user_mgmt.fields.email')} required>
                                    <input
                                        type="email"
                                        required
                                        value={form.email}
                                        onChange={(e) => setForm({ ...form, email: e.target.value })}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
                                        placeholder={t('user_mgmt.fields.email_placeholder')}
                                    />
                                </InputField>
                            </div>

                            <InputField label={t('user_mgmt.fields.role')} required>
                                <div className="relative">
                                    <select
                                        value={form.role}
                                        onChange={(e) => handleRoleChange(e.target.value)}
                                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm appearance-none focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                    >
                                        {availableRoles.map(r => <option key={r.value} value={r.value}>{r.label}</option>)}
                                    </select>
                                    <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                                </div>
                            </InputField>

                            {/* Conditional location dropdowns */}
                            {user?.role === 'system_admin' && form.role === 'state_admin' && (
                                <InputField label="State">
                                    <input value="Andhra Pradesh" readOnly
                                        className="w-full border border-gray-200 bg-gray-50 rounded-lg px-3 py-2 text-sm text-gray-500" />
                                </InputField>
                            )}

                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                {needsDistrict && (
                                    <InputField label={t('user_mgmt.fields.district')} required>
                                        <div className="relative">
                                            <select
                                                value={form.district_id || ''}
                                                onChange={e => handleDistrictChange(e.target.value ? Number(e.target.value) : null)}
                                                disabled={['district_officer', 'supervisor', 'anganwadi_worker'].includes(user?.role)}
                                                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm appearance-none focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-50 disabled:text-gray-500">
                                                <option value="">{t('common.select_district')}</option>
                                                {districts.map(d => <option key={d.district_id} value={d.district_id}>{d.district_name}</option>)}
                                            </select>
                                            {!['district_officer', 'supervisor', 'anganwadi_worker'].includes(user?.role) && (
                                                <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                                            )}
                                        </div>
                                    </InputField>
                                )}

                                {needsMandal && (
                                    <InputField label={t('user_mgmt.fields.mandal')} required>
                                        <div className="relative">
                                            <select
                                                value={form.mandal_id || ''}
                                                onChange={e => handleMandalChange(e.target.value ? Number(e.target.value) : null)}
                                                disabled={!mandals.length || ['supervisor', 'anganwadi_worker'].includes(user?.role)}
                                                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm appearance-none focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-50 disabled:text-gray-500">
                                                <option value="">{t('common.select_mandal')}</option>
                                                {mandals.map(m => <option key={m.mandal_id} value={m.mandal_id}>{m.mandal_name}</option>)}
                                            </select>
                                            {!['supervisor', 'anganwadi_worker'].includes(user?.role) && (
                                                <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                                            )}
                                        </div>
                                    </InputField>
                                )}

                                {needsCenter && (
                                    <InputField label={t('user_mgmt.fields.center')} required>
                                        <div className="relative">
                                            <select
                                                value={form.center_id || ''}
                                                onChange={e => setForm(f => ({ ...f, center_id: e.target.value ? Number(e.target.value) : null }))}
                                                disabled={!centers.length || user?.role === 'anganwadi_worker'}
                                                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm appearance-none focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-50 disabled:text-gray-500">
                                                <option value="">{t('common.select_center')}</option>
                                                {centers.map(c => <option key={c.center_id} value={c.center_id}>{c.center_name}</option>)}
                                            </select>
                                            {user?.role !== 'anganwadi_worker' && (
                                                <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                                            )}
                                        </div>
                                    </InputField>
                                )}
                            </div>

                            <InputField label={editingUser ? t('user_mgmt.fields.new_password') : t('user_mgmt.fields.password')} required={!editingUser}>
                                <div className="relative">
                                    <input
                                        type={showPwd ? 'text' : 'password'}
                                        value={form.password}
                                        onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
                                        placeholder={editingUser ? t('user_mgmt.fields.leave_blank_password') : t('user_mgmt.fields.min_8_chars')}
                                        className="w-full border border-gray-300 rounded-lg px-3 py-2 pr-20 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                    />
                                    <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
                                        <button type="button" onClick={() => setForm(f => ({ ...f, password: generatePassword() }))}
                                            className="text-xs text-indigo-600 hover:text-indigo-800 font-medium px-1">{t('user_mgmt.fields.auto_generate')}</button>
                                        <button type="button" onClick={() => setShowPwd(v => !v)}
                                            className="p-1 text-gray-400 hover:text-gray-600">
                                            {showPwd ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                        </button>
                                    </div>
                                </div>
                            </InputField>

                            <div className="flex gap-3 mt-2">
                                <button type="button" onClick={() => setShowForm(false)}
                                    className="flex-1 border border-gray-300 text-gray-600 font-semibold text-sm py-2.5 rounded-xl hover:bg-gray-50 transition-colors">
                                    {t('common.cancel')}
                                </button>
                                <button type="submit" disabled={saving}
                                    className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-sm py-2.5 rounded-xl transition-colors disabled:opacity-60">
                                    {saving ? t('common.loading') : editingUser ? t('common.save') : t('common.submit')}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* ── Reset Password Modal ─────────────────────────────────────── */}
            {resetModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
                    <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6 space-y-4">
                        <div className="flex items-center justify-between">
                            <h2 className="text-lg font-bold text-gray-900">{t('user_mgmt.reset_modal.title')}</h2>
                            <button onClick={() => setResetModal(null)} className="p-1.5 rounded-lg hover:bg-gray-100">
                                <X className="w-5 h-5 text-gray-500" />
                            </button>
                        </div>
                        <p className="text-sm text-gray-500">
                            {t('user_mgmt.reset_modal.sub', { name: resetModal.user.full_name })}
                        </p>
                        <div className="relative">
                            <input
                                type={showPwd ? 'text' : 'password'}
                                value={newPassword}
                                onChange={e => setNewPassword(e.target.value)}
                                className="w-full border border-gray-300 rounded-lg px-3 py-2 pr-20 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                            />
                            <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
                                <button type="button" onClick={() => setNewPassword(generatePassword())}
                                    className="text-xs text-indigo-600 font-medium px-1">Auto</button>
                                <button type="button" onClick={() => setShowPwd(v => !v)}
                                    className="p-1 text-gray-400">
                                    {showPwd ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                </button>
                            </div>
                        </div>
                        <div className="flex gap-3">
                            <button onClick={() => setResetModal(null)}
                                className="flex-1 border border-gray-300 text-gray-600 font-semibold text-sm py-2 rounded-xl hover:bg-gray-50">
                                {t('common.cancel')}
                            </button>
                            <button onClick={handleResetPassword}
                                className="flex-1 bg-amber-500 hover:bg-amber-600 text-white font-semibold text-sm py-2 rounded-xl transition-colors">
                                {t('user_mgmt.reset_modal.btn')}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default UserManagement;
