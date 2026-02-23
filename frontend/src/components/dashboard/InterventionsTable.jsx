import React, { useState } from 'react';
import { Search, Download, ChevronLeft, ChevronRight } from 'lucide-react';

const PAGE_SIZE_OPTIONS = [10, 25, 50, 100];

const statusColors = {
    'Significant Improvement': 'bg-green-100 text-green-800',
    'Moderate Improvement': 'bg-teal-100 text-teal-800',
    'Minimal Improvement': 'bg-yellow-100 text-yellow-800',
    'No Change': 'bg-gray-100 text-gray-600',
    'Decline': 'bg-red-100 text-red-800',
    'In Progress': 'bg-blue-100 text-blue-800',
};

const categoryColors = {
    'Speech Therapy': 'bg-purple-100 text-purple-800',
    'Occupational Therapy': 'bg-indigo-100 text-indigo-800',
    'Behavioral Therapy': 'bg-pink-100 text-pink-800',
    'Early Intervention': 'bg-orange-100 text-orange-800',
    'Nutritional Support': 'bg-lime-100 text-lime-800',
    'Parental Training': 'bg-amber-100 text-amber-800',
    'Other': 'bg-gray-100 text-gray-600',
};

const exportCSV = (rows) => {
    const headers = ['Intervention ID', 'Child', 'Centre', 'Category', 'Type', 'Start', 'End', 'Sessions Done', 'Sessions Planned', 'Compliance %', 'Status', 'Provider'];
    const lines = [
        headers.join(','),
        ...rows.map(i => [
            i.intervention_id,
            `"${i.child_name}"`, `"${i.center_name}"`, `"${i.intervention_category || ''}"`,
            `"${i.intervention_type}"`, i.start_date || '', i.end_date || 'Ongoing',
            i.sessions_completed ?? '', i.total_sessions_planned ?? '',
            i.compliance_percentage?.toFixed(1) ?? '', `"${i.improvement_status || ''}"`,
            `"${i.provider_name || ''}"`,
        ].join(',')
        ),
    ];
    const blob = new Blob([lines.join('\n')], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = 'interventions.csv'; a.click();
    URL.revokeObjectURL(url);
};

const ComplianceBar = ({ value }) => (
    <div className="flex items-center gap-2">
        <div className="flex-1 bg-gray-200 rounded-full h-1.5">
            <div className="h-1.5 rounded-full bg-blue-500" style={{ width: `${Math.min(value || 0, 100)}%` }} />
        </div>
        <span className="text-xs text-gray-600 w-8">{value?.toFixed(0) ?? '—'}%</span>
    </div>
);

const InterventionsTable = ({ data = [] }) => {
    const [search, setSearch] = useState('');
    const [categoryFilter, setCategoryFilter] = useState('all');
    const [page, setPage] = useState(1);
    const [pageSize, setPageSize] = useState(25);

    const categories = [...new Set(data.map(i => i.intervention_category).filter(Boolean))];

    const filtered = data.filter(i => {
        const matchSearch = `${i.child_name} ${i.intervention_type} ${i.intervention_category || ''}`.toLowerCase().includes(search.toLowerCase());
        const matchCat = categoryFilter === 'all' || i.intervention_category === categoryFilter;
        return matchSearch && matchCat;
    });

    const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
    const safePage = Math.min(page, totalPages);
    const pageRows = filtered.slice((safePage - 1) * pageSize, safePage * pageSize);

    return (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
            {/* Header */}
            <div className="flex flex-wrap items-center justify-between gap-3 p-5 border-b border-gray-100">
                <h2 className="text-lg font-semibold text-gray-900">
                    Interventions
                    <span className="ml-2 text-sm font-normal text-gray-400">({filtered.length} records)</span>
                </h2>
                <div className="flex flex-wrap items-center gap-2">
                    <select
                        value={categoryFilter}
                        onChange={e => { setCategoryFilter(e.target.value); setPage(1); }}
                        className="text-sm border border-gray-300 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        <option value="all">All Categories</option>
                        {categories.map(c => <option key={c} value={c}>{c}</option>)}
                    </select>
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                        <input
                            type="text"
                            placeholder="Search child or type..."
                            value={search}
                            onChange={e => { setSearch(e.target.value); setPage(1); }}
                            className="pl-9 pr-4 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                            {['Child', 'Centre', 'Category', 'Type', 'Start', 'End', 'Sessions', 'Compliance', 'Status', 'Provider'].map(h => (
                                <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider whitespace-nowrap">{h}</th>
                            ))}
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-50">
                        {pageRows.length === 0 ? (
                            <tr><td colSpan={10} className="text-center py-10 text-gray-400 text-sm">No interventions found</td></tr>
                        ) : pageRows.map(i => (
                            <tr key={i.intervention_id} className="hover:bg-gray-50 transition-colors">
                                <td className="px-4 py-3 text-sm font-medium text-gray-900 whitespace-nowrap">{i.child_name}</td>
                                <td className="px-4 py-3 text-xs text-gray-500">{i.center_name}</td>
                                <td className="px-4 py-3">
                                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${categoryColors[i.intervention_category] || 'bg-gray-100 text-gray-600'}`}>
                                        {i.intervention_category || '—'}
                                    </span>
                                </td>
                                <td className="px-4 py-3 text-xs text-gray-600">{i.intervention_type}</td>
                                <td className="px-4 py-3 text-xs text-gray-600 whitespace-nowrap">{i.start_date || '—'}</td>
                                <td className="px-4 py-3 text-xs text-gray-600 whitespace-nowrap">{i.end_date || 'Ongoing'}</td>
                                <td className="px-4 py-3 text-sm text-center text-gray-800">{i.sessions_completed ?? '—'}/{i.total_sessions_planned ?? '—'}</td>
                                <td className="px-4 py-3 min-w-[120px]"><ComplianceBar value={i.compliance_percentage} /></td>
                                <td className="px-4 py-3">
                                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium whitespace-nowrap ${statusColors[i.improvement_status] || 'bg-gray-100 text-gray-600'}`}>
                                        {i.improvement_status || '—'}
                                    </span>
                                </td>
                                <td className="px-4 py-3 text-xs text-gray-600">{i.provider_name || '—'}</td>
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

export default InterventionsTable;
