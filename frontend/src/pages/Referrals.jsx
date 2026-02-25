import React, { useState, useEffect } from 'react';
import { referralsAPI } from '../utils/api';
import { useAuth } from '../context/AuthContext';
import {
    ClipboardList, Search, Filter, Calendar,
    Building2, Stethoscope, User, AlertCircle, CheckCircle2,
    MoreVertical, ArrowRight, ExternalLink, RefreshCw,
    X
} from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';
import VoiceButton from '../components/common/VoiceButton';

const STATUS_COLORS = {
    'Pending': 'bg-amber-100 text-amber-700 border-amber-200',
    'Scheduled': 'bg-blue-100 text-blue-700 border-blue-200',
    'Completed': 'bg-emerald-100 text-emerald-700 border-emerald-200',
    'Cancelled': 'bg-gray-100 text-gray-700 border-gray-200',
};

const Referrals = () => {
    const { user } = useAuth();
    const { t } = useLanguage();
    const [referrals, setReferrals] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchText, setSearchText] = useState('');
    const [statusFilter, setStatusFilter] = useState('All');
    const [updating, setUpdating] = useState(null); // { referral_id, status, outcome_summary }
    const [toast, setToast] = useState(null);

    useEffect(() => {
        fetchReferrals();
    }, [statusFilter]);

    const fetchReferrals = async () => {
        setLoading(true);
        try {
            const filter = statusFilter === 'All' ? undefined : statusFilter;
            const res = await referralsAPI.list(filter);
            setReferrals(res.data);
        } catch (err) {
            showToast(t('referrals.toasts.load_failed'), 'error');
        } finally {
            setLoading(false);
        }
    };

    const handleUpdateStatus = async (id, status, outcome = '') => {
        try {
            await referralsAPI.update(id, {
                status,
                outcome_summary: outcome,
                completion_date: status === 'Completed' ? new Date().toISOString().split('T')[0] : undefined
            });
            showToast(t('referrals.toasts.update_success'));
            setUpdating(null);
            fetchReferrals();
        } catch (err) {
            showToast(t('referrals.toasts.update_failed'), 'error');
        }
    };

    const showToast = (message, type = 'success') => {
        setToast({ message, type });
        setTimeout(() => setToast(null), 3000);
    };

    const getLocalizedStatus = (status) => {
        const key = status?.toLowerCase();
        return t(`referrals.status.${key}`) || status;
    };

    const filteredReferrals = referrals.filter(r =>
        (r.child_name || '').toLowerCase().includes(searchText.toLowerCase()) ||
        (r.referred_to || '').toLowerCase().includes(searchText.toLowerCase()) ||
        (r.facility_name || '').toLowerCase().includes(searchText.toLowerCase())
    );

    const filterOptions = [
        { label: t('referrals.status.all'), value: 'All' },
        { label: t('referrals.status.pending'), value: 'Pending' },
        { label: t('referrals.status.scheduled'), value: 'Scheduled' },
        { label: t('referrals.status.completed'), value: 'Completed' },
        { label: t('referrals.status.cancelled'), value: 'Cancelled' }
    ];

    return (
        <div className="p-6 space-y-6">
            {/* Toast */}
            {toast && (
                <div className={`fixed top-5 right-5 z-50 flex items-center gap-3 px-5 py-3 rounded-xl shadow-lg text-sm font-medium transition-all
                    ${toast.type === 'error' ? 'bg-red-600 text-white' : 'bg-emerald-600 text-white'}`}>
                    {toast.type === 'error' ? <AlertCircle className="w-4 h-4" /> : <CheckCircle2 className="w-4 h-4" />}
                    {toast.message}
                </div>
            )}

            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                        <Stethoscope className="w-6 h-6 text-indigo-600" />
                        {t('referrals.title')}
                    </h1>
                    <p className="text-sm text-gray-500 mt-1">{t('referrals.sub')}</p>
                </div>

                <div className="flex items-center gap-2">
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                        <input
                            type="text"
                            placeholder={t('referrals.search_placeholder')}
                            value={searchText}
                            onChange={(e) => setSearchText(e.target.value)}
                            className="pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 w-64"
                        />
                    </div>
                    <VoiceButton
                        content={`${t('referrals.title')}. ${t('referrals.sub')}. ${referrals.length} ${t('common.referrals')} ${t('common.at')} ${t('common.total')}.`}
                    />
                    <button
                        onClick={fetchReferrals}
                        className="p-2 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 text-gray-600"
                    >
                        <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                    </button>
                </div>
            </div>

            {/* Filters */}
            <div className="flex items-center gap-2 overflow-x-auto pb-1">
                {filterOptions.map(option => (
                    <button
                        key={option.value}
                        onClick={() => setStatusFilter(option.value)}
                        className={`px-4 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition-all border
                            ${statusFilter === option.value
                                ? 'bg-indigo-600 text-white border-indigo-600 shadow-md shadow-indigo-100'
                                : 'bg-white text-gray-600 border-gray-200 hover:border-indigo-300'}`}
                    >
                        {option.label}
                    </button>
                ))}
            </div>

            {/* Grid */}
            {loading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {[1, 2, 3].map(i => (
                        <div key={i} className="bg-white border border-gray-100 rounded-2xl h-64 animate-pulse" />
                    ))}
                </div>
            ) : filteredReferrals.length === 0 ? (
                <div className="bg-white border border-gray-200 rounded-3xl p-12 text-center">
                    <div className="bg-gray-50 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4">
                        <ClipboardList className="w-8 h-8 text-gray-300" />
                    </div>
                    <h3 className="text-lg font-bold text-gray-900">{t('referrals.no_referrals')}</h3>
                    <p className="text-gray-500 text-sm mt-1">{t('children.filters.reset')}</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {filteredReferrals.map(referral => (
                        <div key={referral.referral_id} className="bg-white border border-gray-200 rounded-3xl p-5 hover:shadow-xl hover:shadow-indigo-50/50 transition-all group">
                            <div className="flex justify-between items-start mb-4">
                                <span className={`px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider border ${STATUS_COLORS[referral.status] || 'bg-gray-100 text-gray-600'}`}>
                                    {getLocalizedStatus(referral.status)}
                                </span>
                                <div className="text-right">
                                    <p className="text-[10px] text-gray-400 font-medium uppercase">{t('referrals.fields.date')}</p>
                                    <p className="text-xs font-bold text-gray-700">{new Date(referral.referral_date).toLocaleDateString()}</p>
                                </div>
                            </div>

                            <div className="space-y-4">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-xl bg-indigo-50 flex items-center justify-center text-indigo-600 shrink-0">
                                        <User className="w-5 h-5" />
                                    </div>
                                    <div>
                                        <h3 className="font-bold text-gray-900 leading-tight">{referral.child_name || `${t('common.child')} #${referral.child_id}`}</h3>
                                        <p className="text-xs text-gray-500">{t('referrals.fields.risk')}: <span className="text-red-500 font-semibold">{referral.risk_level_at_referral}</span></p>
                                    </div>
                                </div>

                                <div className="bg-gray-50 rounded-2xl p-3 space-y-2">
                                    <div className="flex items-start gap-2">
                                        <Building2 className="w-3.5 h-3.5 text-gray-400 mt-0.5 shrink-0" />
                                        <div className="min-w-0">
                                            <p className="text-[10px] text-gray-400 font-medium uppercase leading-none">{t('referrals.fields.to')}</p>
                                            <p className="text-xs font-bold text-gray-700 truncate mt-1">{referral.referred_to || t('common.not_specified')}</p>
                                            <p className="text-[10px] text-gray-500 mt-0.5">{referral.facility_name}</p>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-2 border-t border-gray-100 pt-2">
                                        <Calendar className="w-3.5 h-3.5 text-gray-400 shrink-0" />
                                        <div>
                                            <p className="text-[10px] text-gray-400 font-medium uppercase leading-none">{t('referrals.fields.by')}</p>
                                            <p className="text-xs font-bold text-gray-700 mt-1">{referral.expected_completion_date ? new Date(referral.expected_completion_date).toLocaleDateString() : t('common.tbd')}</p>
                                        </div>
                                    </div>
                                </div>

                                <div className="pt-2 flex items-center justify-between">
                                    <div className="flex items-center gap-1 text-[10px] text-gray-400">
                                        <AlertCircle className="w-3 h-3" />
                                        <span>ID: {referral.referral_id}</span>
                                    </div>

                                    <div className="flex gap-2">
                                        {referral.status === 'Pending' && (
                                            <button
                                                onClick={() => handleUpdateStatus(referral.referral_id, 'Scheduled')}
                                                className="px-3 py-1.5 rounded-xl bg-blue-50 text-blue-600 text-xs font-bold hover:bg-blue-100 transition-colors"
                                            >
                                                {t('referrals.actions.schedule')}
                                            </button>
                                        )}
                                        {['Pending', 'Scheduled'].includes(referral.status) && (
                                            <button
                                                onClick={() => setUpdating(referral)}
                                                className="px-3 py-1.5 rounded-xl bg-emerald-50 text-emerald-600 text-xs font-bold hover:bg-emerald-100 transition-colors"
                                            >
                                                {t('referrals.actions.complete')}
                                            </button>
                                        )}
                                        {referral.status === 'Completed' && (
                                            <div className="flex items-center gap-1 text-emerald-600 font-bold text-[10px]">
                                                <CheckCircle2 className="w-3 h-3" />
                                                {t('referrals.actions.done')}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Update Modal */}
            {updating && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
                    <div className="bg-white rounded-[32px] shadow-2xl w-full max-w-md p-8 animate-in fade-in zoom-in duration-200">
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-xl font-black text-gray-900">{t('referrals.complete_title')}</h2>
                            <button onClick={() => setUpdating(null)} className="p-2 hover:bg-gray-100 rounded-2xl transition-colors">
                                <X className="w-5 h-5 text-gray-500" />
                            </button>
                        </div>

                        <div className="space-y-6">
                            <div>
                                <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-2">{t('referrals.outcome')}</label>
                                <textarea
                                    className="w-full bg-gray-50 border-none rounded-2xl p-4 text-sm focus:ring-2 focus:ring-indigo-500 h-32"
                                    placeholder={t('referrals.outcome_placeholder')}
                                    id="outcome-summary"
                                />
                            </div>

                            <div className="flex gap-3">
                                <button
                                    onClick={() => setUpdating(null)}
                                    className="flex-1 px-6 py-3.5 bg-gray-100 text-gray-600 font-bold rounded-2xl hover:bg-gray-200 transition-all"
                                >
                                    {t('common.cancel')}
                                </button>
                                <button
                                    onClick={() => {
                                        const outcome = document.getElementById('outcome-summary').value;
                                        handleUpdateStatus(updating.referral_id, 'Completed', outcome);
                                    }}
                                    className="flex-1 px-6 py-3.5 bg-indigo-600 text-white font-bold rounded-2xl hover:bg-indigo-700 shadow-lg shadow-indigo-200 transition-all"
                                >
                                    {t('common.submit')}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};



export default Referrals;
