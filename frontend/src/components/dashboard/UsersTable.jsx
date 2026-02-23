import React, { useState } from 'react';
import { Search, Download, ChevronLeft, ChevronRight, ShieldOff, ShieldCheck, KeyRound, Pencil, Trash2 } from 'lucide-react';

const PAGE_SIZE_OPTIONS = [10, 25, 50, 100];

const roleColors = {
    system_admin: 'bg-red-100 text-red-800',
    state_admin: 'bg-orange-100 text-orange-800',
    district_officer: 'bg-amber-100 text-amber-800',
    supervisor: 'bg-blue-100 text-blue-800',
    anganwadi_worker: 'bg-green-100 text-green-800',
    parent: 'bg-purple-100 text-purple-800',
};

export const roleLabels = {
    system_admin: 'System Admin',
    state_admin: 'State Admin',
    district_officer: 'District Officer',
    supervisor: 'Supervisor',
    anganwadi_worker: 'AWC Worker',
    parent: 'Parent',
};

const exportCSV = (rows) => {
    const headers = ['User ID', 'Full Name', 'Email', 'Role', 'Centre', 'Status'];
    const lines = [
        headers.join(','),
        ...rows.map(u => [
            u.user_id, `"${u.full_name}"`, u.email,
            roleLabels[u.role] || u.role, `"${u.center_name || ''}"`, u.status,
        ].join(','))
    ];
    const blob = new Blob([lines.join('\n')], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = 'users.csv'; a.click();
    URL.revokeObjectURL(url);
};

const UsersTable = ({ data = [], onToggleStatus, onResetPassword, onEdit, onDelete, showActions = false }) => {
    const [search, setSearch] = useState('');
    const [roleFilter, setRoleFilter] = useState('all');
    const [statusFilter, setStatusFilter] = useState('all');
    const [page, setPage] = useState(1);
    const [pageSize, setPageSize] = useState(25);

    const roles = [...new Set(data.map(u => u.role))];

    const filtered = data.filter(u => {
        const matchSearch = `${u.full_name} ${u.email}`.toLowerCase().includes(search.toLowerCase());
        const matchRole = roleFilter === 'all' || u.role === roleFilter;
        const matchStatus = statusFilter === 'all' || u.status === statusFilter;
        return matchSearch && matchRole && matchStatus;
    });

    const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
    const safePage = Math.min(page, totalPages);
    const pageRows = filtered.slice((safePage - 1) * pageSize, safePage * pageSize);

    return (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
            {/* Header */}
            <div className="flex flex-wrap items-center justify-between gap-3 p-5 border-b border-gray-100">
                <h2 className="text-lg font-semibold text-gray-900">
                    Users
                    <span className="ml-2 text-sm font-normal text-gray-400">({filtered.length} records)</span>
                </h2>
                <div className="flex flex-wrap items-center gap-2">
                    <select
                        value={roleFilter}
                        onChange={e => { setRoleFilter(e.target.value); setPage(1); }}
                        className="text-sm border border-gray-300 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    >
                        <option value="all">All Roles</option>
                        {roles.map(r => <option key={r} value={r}>{roleLabels[r] || r}</option>)}
                    </select>
                    <select
                        value={statusFilter}
                        onChange={e => { setStatusFilter(e.target.value); setPage(1); }}
                        className="text-sm border border-gray-300 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    >
                        <option value="all">All Statuses</option>
                        <option value="Active">Active</option>
                        <option value="Revoked">Revoked</option>
                    </select>
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                        <input
                            type="text"
                            placeholder="Search name or email..."
                            value={search}
                            onChange={e => { setSearch(e.target.value); setPage(1); }}
                            className="pl-9 pr-4 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 w-52"
                        />
                    </div>
                    <button
                        onClick={() => exportCSV(filtered)}
                        className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                        <Download className="w-4 h-4" />
                        Export
                    </button>
                </div>
            </div>

            {/* Table */}
            <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-100">
                    <thead className="bg-gray-50">
                        <tr>
                            {['#', 'Name', 'Email', 'Role', 'Centre', 'Status', ...(showActions ? ['Actions'] : [])].map(h => (
                                <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{h}</th>
                            ))}
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-50">
                        {pageRows.length === 0 ? (
                            <tr><td colSpan={showActions ? 7 : 6} className="text-center py-10 text-gray-400 text-sm">No users found</td></tr>
                        ) : pageRows.map(user => (
                            <tr key={user.user_id} className="hover:bg-gray-50 transition-colors">
                                <td className="px-4 py-3 text-xs text-gray-400">{user.user_id}</td>
                                <td className="px-4 py-3 text-sm font-medium text-gray-900">{user.full_name}</td>
                                <td className="px-4 py-3 text-sm text-gray-600">{user.email}</td>
                                <td className="px-4 py-3">
                                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${roleColors[user.role] || 'bg-gray-100 text-gray-600'}`}>
                                        {roleLabels[user.role] || user.role}
                                    </span>
                                </td>
                                <td className="px-4 py-3 text-sm text-gray-600">{user.center_name || '—'}</td>
                                <td className="px-4 py-3">
                                    <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${user.status === 'Active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-700'}`}>
                                        {user.status}
                                    </span>
                                </td>
                                {showActions && (
                                    <td className="px-4 py-3">
                                        <div className="flex items-center gap-1">
                                            {onEdit && (
                                                <button
                                                    onClick={() => onEdit(user)}
                                                    title="Edit user"
                                                    className="p-1.5 rounded-lg text-gray-500 hover:bg-indigo-50 hover:text-indigo-600 transition-colors"
                                                >
                                                    <Pencil className="w-4 h-4" />
                                                </button>
                                            )}
                                            {onToggleStatus && (
                                                <button
                                                    onClick={() => onToggleStatus(user)}
                                                    title={user.status === 'Active' ? 'Revoke access' : 'Activate user'}
                                                    className={`p-1.5 rounded-lg transition-colors ${user.status === 'Active' ? 'text-red-500 hover:bg-red-50' : 'text-green-600 hover:bg-green-50'}`}
                                                >
                                                    {user.status === 'Active' ? <ShieldOff className="w-4 h-4" /> : <ShieldCheck className="w-4 h-4" />}
                                                </button>
                                            )}
                                            {onResetPassword && (
                                                <button
                                                    onClick={() => onResetPassword(user)}
                                                    title="Reset password"
                                                    className="p-1.5 rounded-lg text-amber-500 hover:bg-amber-50 transition-colors"
                                                >
                                                    <KeyRound className="w-4 h-4" />
                                                </button>
                                            )}
                                            {onDelete && (
                                                <button
                                                    onClick={() => onDelete(user)}
                                                    title="Delete user"
                                                    className="p-1.5 rounded-lg text-red-500 hover:bg-red-50 transition-colors"
                                                >
                                                    <Trash2 className="w-4 h-4" />
                                                </button>
                                            )}
                                        </div>
                                    </td>
                                )}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Pagination footer */}
            <div className="flex flex-wrap items-center justify-between gap-3 px-5 py-3 border-t border-gray-100 text-sm text-gray-500">
                <div className="flex items-center gap-2">
                    <span>Rows per page:</span>
                    <select
                        value={pageSize}
                        onChange={e => { setPageSize(Number(e.target.value)); setPage(1); }}
                        className="border border-gray-300 rounded px-2 py-0.5 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500"
                    >
                        {PAGE_SIZE_OPTIONS.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                </div>
                <div className="flex items-center gap-3">
                    <span>{filtered.length === 0 ? '0' : `${(safePage - 1) * pageSize + 1}–${Math.min(safePage * pageSize, filtered.length)}`} of {filtered.length}</span>
                    <div className="flex gap-1">
                        <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={safePage === 1}
                            className="p-1 rounded hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors">
                            <ChevronLeft className="w-4 h-4" />
                        </button>
                        <span className="px-2 py-0.5">{safePage} / {totalPages}</span>
                        <button onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={safePage === totalPages}
                            className="p-1 rounded hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors">
                            <ChevronRight className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default UsersTable;
