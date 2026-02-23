import React, { useState } from 'react';
import { Search, Download, ChevronLeft, ChevronRight } from 'lucide-react';

const PAGE_SIZE_OPTIONS = [10, 25, 50, 100];

const statusBadge = (status) => {
    const colors = {
        Active: 'bg-green-100 text-green-800',
        Inactive: 'bg-gray-100 text-gray-600',
        Transferred: 'bg-yellow-100 text-yellow-800',
        Graduated: 'bg-blue-100 text-blue-800',
    };
    return (
        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${colors[status] || 'bg-gray-100 text-gray-600'}`}>
            {status}
        </span>
    );
};

const exportCSV = (rows) => {
    const headers = ['ID', 'First Name', 'Last Name', 'DOB', 'Gender', 'Centre', 'Caregiver', 'Phone', 'Status'];
    const lines = [
        headers.join(','),
        ...rows.map(c =>
            [c.unique_child_code, c.first_name, c.last_name, c.dob, c.gender,
            `"${c.center_name}"`, `"${c.caregiver_name || ''}"`, c.caregiver_phone || '', c.status].join(',')
        ),
    ];
    const blob = new Blob([lines.join('\n')], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'children.csv';
    a.click();
    URL.revokeObjectURL(url);
};

const ChildrenTable = ({ data = [], onSearch, onRowClick }) => {
    const [search, setSearch] = useState('');
    const [statusFilter, setStatusFilter] = useState('all');
    const [page, setPage] = useState(1);
    const [pageSize, setPageSize] = useState(25);

    const handleSearch = (e) => {
        setSearch(e.target.value);
        setPage(1);
        onSearch && onSearch(e.target.value);
    };

    const safeData = Array.isArray(data) ? data : [];

    const filtered = (onSearch
        ? safeData
        : safeData.filter(c => {
            if (!c) return false;

            const fullText = `${c?.first_name || ''} ${c?.last_name || ''} ${c?.unique_child_code || ''}`.toLowerCase();
            return fullText.includes(search.toLowerCase());
        })
    ).filter(c => statusFilter === 'all' || c?.status === statusFilter);
    const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
    const safePage = Math.min(page, totalPages);
    const pageRows = filtered.slice((safePage - 1) * pageSize, safePage * pageSize);

    const statuses = [...new Set(safeData.map(c => c?.status))].filter(Boolean);
    return (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
            {/* Header */}
            <div className="flex flex-wrap items-center justify-between gap-3 p-5 border-b border-gray-100">
                <h2 className="text-lg font-semibold text-gray-900">
                    Children
                    <span className="ml-2 text-sm font-normal text-gray-400">({filtered.length} records)</span>
                </h2>
                <div className="flex flex-wrap items-center gap-2">
                    {/* Status filter */}
                    <select
                        value={statusFilter}
                        onChange={e => { setStatusFilter(e.target.value); setPage(1); }}
                        className="text-sm border border-gray-300 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        <option value="all">All Status</option>
                        {statuses.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                    {/* Search */}
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                        <input
                            type="text"
                            placeholder="Search name or ID..."
                            value={search}
                            onChange={handleSearch}
                            className="pl-9 pr-4 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>
                    {/* CSV export */}
                    <button
                        onClick={() => exportCSV(filtered)}
                        title="Export to CSV"
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
                            {['ID', 'Name', 'DOB', 'Gender', 'Centre', 'Caregiver', 'Phone', 'Status'].map(h => (
                                <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider whitespace-nowrap">{h}</th>
                            ))}
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-50">
                        {pageRows.length === 0 ? (
                            <tr><td colSpan={8} className="text-center py-10 text-gray-400 text-sm">No children found</td></tr>
                        ) : pageRows.map(child => (
                            <tr
                                key={child.child_id}
                                onClick={() => onRowClick && onRowClick(child)}
                                className={`transition-colors ${onRowClick ? 'cursor-pointer hover:bg-green-50' : 'hover:bg-gray-50'}`}
                            >
                                <td className="px-4 py-3 text-xs text-gray-500 font-mono">{child.unique_child_code}</td>
                                <td className="px-4 py-3 text-sm font-medium text-gray-900 whitespace-nowrap">{child.first_name} {child.last_name}</td>
                                <td className="px-4 py-3 text-sm text-gray-600 whitespace-nowrap">{child.dob}</td>
                                <td className="px-4 py-3 text-sm text-gray-600">{child.gender}</td>
                                <td className="px-4 py-3 text-sm text-gray-600">{child.center_name}</td>
                                <td className="px-4 py-3 text-sm text-gray-600">{child.caregiver_name || '—'}</td>
                                <td className="px-4 py-3 text-sm text-gray-600">{child.caregiver_phone || '—'}</td>
                                <td className="px-4 py-3">{statusBadge(child.status)}</td>
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
                        className="border border-gray-300 rounded px-2 py-0.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                    >
                        {PAGE_SIZE_OPTIONS.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                </div>
                <div className="flex items-center gap-3">
                    <span>{filtered.length === 0 ? '0' : `${(safePage - 1) * pageSize + 1}–${Math.min(safePage * pageSize, filtered.length)}`} of {filtered.length}</span>
                    <div className="flex gap-1">
                        <button
                            onClick={() => setPage(p => Math.max(1, p - 1))}
                            disabled={safePage === 1}
                            className="p-1 rounded hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                        >
                            <ChevronLeft className="w-4 h-4" />
                        </button>
                        <span className="px-2 py-0.5">
                            {safePage} / {totalPages}
                        </span>
                        <button
                            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                            disabled={safePage === totalPages}
                            className="p-1 rounded hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                        >
                            <ChevronRight className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ChildrenTable;
