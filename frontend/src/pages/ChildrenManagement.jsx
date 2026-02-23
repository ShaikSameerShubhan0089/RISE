import React, { useState, useEffect } from 'react';
import { childrenAPI } from '../utils/api';
import ChildrenTable from '../components/dashboard/ChildrenTable';
import ChildRegistrationForm from '../components/dashboard/ChildRegistrationForm';
import ChildDetailsModal from '../components/dashboard/ChildDetailsModal';
import { Plus, Search, Filter, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const ChildrenManagement = () => {
    const { user } = useAuth();
    const [children, setChildren] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showRegister, setShowRegister] = useState(false);
    const [selectedChild, setSelectedChild] = useState(null);
    const [filters, setFilters] = useState({
        search: '',
        risk_tier: '',
        status_filter: 'Active'
    });

    const fetchChildren = async () => {
        setLoading(true);
        try {
            const res = await childrenAPI.list(filters);

            // ✅ SAFE DATA HANDLING (Prevents crash + logout issue)
            const childrenData = Array.isArray(res?.data)
                ? res.data
                : res?.data?.children || [];

            setChildren(childrenData);

        } catch (err) {
            console.error('Failed to fetch children', err);
            setChildren([]); // prevent undefined state crash
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        const timer = setTimeout(() => {
            fetchChildren();
        }, 500);
        return () => clearTimeout(timer);
    }, [filters]);

    const handleFilterChange = (e) => {
        const { name, value } = e.target;
        setFilters(prev => ({ ...prev, [name]: value }));
    };

    return (
        <div className="p-6 space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">
                        Children Management
                    </h1>
                    <p className="text-gray-500 text-sm">
                        Register, search, and monitor children risk status
                    </p>
                </div>

                <button
                    onClick={() => setShowRegister(true)}
                    className="bg-green-600 text-white px-4 py-2.5 rounded-xl font-bold hover:bg-green-700 transition-all flex items-center justify-center gap-2 shadow-lg shadow-green-100"
                >
                    <Plus className="w-5 h-5" />
                    Register New Child
                </button>
            </div>

            {(user?.role === 'district_officer' ||
                user?.role === 'state_admin' ||
                user?.role === 'system_admin') && (
                    <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 flex items-center gap-3 text-blue-700 text-sm">
                        <AlertCircle className="w-5 h-5 shrink-0" />
                        <p>
                            <strong>Note:</strong> Showing the most recent 200
                            registered children in your jurisdiction.
                            Use search or filters to find specific records.
                        </p>
                    </div>
                )}

            {/* Filters */}
            <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4 items-end">

                <div className="space-y-1">
                    <label className="text-xs font-bold text-gray-500 uppercase flex items-center gap-1">
                        <Search className="w-3 h-3" /> Search
                    </label>
                    <input
                        name="search"
                        value={filters.search}
                        onChange={handleFilterChange}
                        placeholder="Name or Unique ID..."
                        className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none transition-all text-sm"
                    />
                </div>

                <div className="space-y-1">
                    <label className="text-xs font-bold text-gray-500 uppercase flex items-center gap-1">
                        <AlertCircle className="w-3 h-3" /> Risk Tier
                    </label>
                    <select
                        name="risk_tier"
                        value={filters.risk_tier}
                        onChange={handleFilterChange}
                        className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none transition-all text-sm"
                    >
                        <option value="">All Tiers</option>
                        <option value="High Risk">High Risk</option>
                        <option value="Moderate Risk">Moderate Risk</option>
                        <option value="Mild Concern">Mild Concern</option>
                        <option value="Low Risk">Low Risk</option>
                    </select>
                </div>

                <div className="space-y-1">
                    <label className="text-xs font-bold text-gray-500 uppercase flex items-center gap-1">
                        <Filter className="w-3 h-3" /> Status
                    </label>
                    <select
                        name="status_filter"
                        value={filters.status_filter}
                        onChange={handleFilterChange}
                        className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none transition-all text-sm"
                    >
                        <option value="">All Status</option>
                        <option value="Active">Active</option>
                        <option value="Inactive">Inactive</option>
                        <option value="Transferred">Transferred</option>
                        <option value="Graduated">Graduated</option>
                    </select>
                </div>

                <button
                    onClick={() =>
                        setFilters({
                            search: '',
                            risk_tier: '',
                            status_filter: 'Active'
                        })
                    }
                    className="text-xs font-bold text-gray-400 hover:text-red-500 transition-colors uppercase h-9"
                >
                    Reset Filters
                </button>
            </div>

            {loading ? (
                <div className="flex items-center justify-center h-64">
                    <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-green-600" />
                </div>
            ) : (
                <ChildrenTable
                    data={children}
                    onSearch={null}
                    onRowClick={(child) => setSelectedChild(child)}
                />
            )}

            {showRegister && (
                <ChildRegistrationForm
                    user={user}
                    onClose={() => setShowRegister(false)}
                    onSuccess={fetchChildren}
                />
            )}

            {selectedChild && (
                <ChildDetailsModal
                    child={selectedChild}
                    onClose={() => setSelectedChild(null)}
                />
            )}
        </div>
    );
};

export default ChildrenManagement;