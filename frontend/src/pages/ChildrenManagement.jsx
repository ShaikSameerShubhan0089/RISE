import React, { useState, useEffect } from 'react';
import { childrenAPI } from '../utils/api';
import ChildrenTable from '../components/dashboard/ChildrenTable';
import ChildRegistrationForm from '../components/dashboard/ChildRegistrationForm';
import ChildDetailsModal from '../components/dashboard/ChildDetailsModal';
import { Plus, Search, Filter, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import VoiceButton from '../components/common/VoiceButton';

const ChildrenManagement = () => {
    const { user } = useAuth();
    const { t } = useLanguage();
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
                        {t('children.title')}
                    </h1>
                    <p className="text-gray-500 text-sm">
                        {t('children.sub')}
                    </p>
                </div>

                <div className="flex items-center gap-3">
                    <button
                        onClick={() => setShowRegister(true)}
                        className="bg-green-600 text-white px-4 py-2.5 rounded-xl font-bold hover:bg-green-700 transition-all flex items-center justify-center gap-2 shadow-lg shadow-green-100"
                    >
                        <Plus className="w-5 h-5" />
                        {t('children.register')}
                    </button>
                    <VoiceButton
                        content={`${t('children.title')}. ${t('children.sub')}. ${children.length} ${t('common.children')} ${t('common.at')} ${t('common.total')}.`}
                    />
                </div>
            </div>

            {(user?.role === 'district_officer' ||
                user?.role === 'state_admin' ||
                user?.role === 'system_admin') && (
                    <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 flex items-center gap-3 text-blue-700 text-sm">
                        <AlertCircle className="w-5 h-5 shrink-0" />
                        <p>
                            <strong>{t('common.note') || 'Note'}:</strong> {t('children.note_admin')}
                        </p>
                    </div>
                )}

            {/* Filters */}
            <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4 items-end">

                <div className="space-y-1">
                    <label className="text-xs font-bold text-gray-500 uppercase flex items-center gap-1">
                        <Search className="w-3 h-3" /> {t('children.filters.search')}
                    </label>
                    <input
                        name="search"
                        value={filters.search}
                        onChange={handleFilterChange}
                        placeholder={t('children.filters.search_placeholder')}
                        className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none transition-all text-sm"
                    />
                </div>

                <div className="space-y-1">
                    <label className="text-xs font-bold text-gray-500 uppercase flex items-center gap-1">
                        <AlertCircle className="w-3 h-3" /> {t('children.filters.risk_tier')}
                    </label>
                    <select
                        name="risk_tier"
                        value={filters.risk_tier}
                        onChange={handleFilterChange}
                        className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none transition-all text-sm"
                    >
                        <option value="">{t('children.filters.all_tiers')}</option>
                        <option value="High Risk">{t('common.risk_tiers.high')}</option>
                        <option value="Moderate Risk">{t('common.risk_tiers.moderate')}</option>
                        <option value="Mild Concern">{t('common.risk_tiers.mild')}</option>
                        <option value="Low Risk">{t('common.risk_tiers.low')}</option>
                    </select>
                </div>

                <div className="space-y-1">
                    <label className="text-xs font-bold text-gray-500 uppercase flex items-center gap-1">
                        <Filter className="w-3 h-3" /> {t('children.filters.status')}
                    </label>
                    <select
                        name="status_filter"
                        value={filters.status_filter}
                        onChange={handleFilterChange}
                        className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none transition-all text-sm"
                    >
                        <option value="">{t('children.filters.all_status')}</option>
                        <option value="Active">{t('children.status.active')}</option>
                        <option value="Inactive">{t('children.status.inactive')}</option>
                        <option value="Transferred">{t('children.status.transferred')}</option>
                        <option value="Graduated">{t('children.status.graduated')}</option>
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
                    {t('children.filters.reset')}
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