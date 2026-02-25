import React, { useState } from 'react';
import { X, User, Calendar, Phone, Mail, Home, ShieldCheck } from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';

const ChildRegistrationForm = ({ onClose, onSuccess, user }) => {
    const { t } = useLanguage();
    const [formData, setFormData] = useState({
        first_name: '',
        last_name: '',
        dob: '',
        gender: 'Male',
        center_id: user?.center_id || '',
        caregiver_name: '',
        caregiver_relationship: 'Mother',
        caregiver_phone: '',
        caregiver_email: '',
        caregiver_additional_info: '',
        create_parent_account: true,
        parent_password: ''
    });

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            // Import childrenAPI from utils/api
            const { childrenAPI } = await import('../../utils/api');
            await childrenAPI.create(formData);
            onSuccess && onSuccess();
            onClose();
        } catch (err) {
            setError(err.response?.data?.detail || t('children.registration.failed'));
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
                <div className="flex items-center justify-between p-6 bg-green-50 border-b border-green-100">
                    <div>
                        <h2 className="text-xl font-bold text-green-900">{t('children.registration.title')}</h2>
                        <p className="text-sm text-green-700">
                            {t('children.registration.sub').replace('{center}', user?.center_name || t('user_mgmt.fields.center'))}
                        </p>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-green-100 rounded-full transition-colors">
                        <X className="w-5 h-5 text-green-700" />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="p-6 space-y-6 max-h-[80vh] overflow-y-auto">
                    {error && (
                        <div className="bg-red-50 text-red-700 p-3 rounded-lg text-sm border border-red-100">
                            ⚠️ {error}
                        </div>
                    )}

                    {/* Child Info Section */}
                    <div className="space-y-4">
                        <div className="flex items-center gap-2 text-green-800 font-semibold border-b border-green-50 pb-2">
                            <User className="w-4 h-4" />
                            <span>{t('children.info_section')}</span>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-1">
                                <label className="text-xs font-bold text-gray-500 uppercase">{t('children.registration.first_name')}</label>
                                <input
                                    required
                                    name="first_name"
                                    value={formData.first_name}
                                    onChange={handleChange}
                                    className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none transition-all"
                                />
                            </div>
                            <div className="space-y-1">
                                <label className="text-xs font-bold text-gray-500 uppercase">{t('children.registration.last_name')}</label>
                                <input
                                    name="last_name"
                                    value={formData.last_name}
                                    onChange={handleChange}
                                    className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none transition-all"
                                />
                            </div>
                            <div className="space-y-1">
                                <label className="text-xs font-bold text-gray-500 uppercase">{t('children.registration.dob')}</label>
                                <div className="relative">
                                    <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                                    <input
                                        required
                                        type="date"
                                        name="dob"
                                        value={formData.dob}
                                        onChange={handleChange}
                                        className="w-full pl-10 pr-3 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none transition-all"
                                    />
                                </div>
                            </div>
                            <div className="space-y-1">
                                <label className="text-xs font-bold text-gray-500 uppercase">{t('children.registration.gender')}</label>
                                <select
                                    name="gender"
                                    value={formData.gender}
                                    onChange={handleChange}
                                    className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none transition-all"
                                >
                                    <option value="Male">{t('children.genders.male')}</option>
                                    <option value="Female">{t('children.genders.female')}</option>
                                    <option value="Other">{t('children.genders.other')}</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    {/* Caregiver Section */}
                    <div className="space-y-4">
                        <div className="flex items-center gap-2 text-green-800 font-semibold border-b border-green-50 pb-2">
                            <Home className="w-4 h-4" />
                            <span>{t('children.caregiver_section')}</span>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-1">
                                <label className="text-xs font-bold text-gray-500 uppercase">{t('children.registration.caregiver_name')}</label>
                                <input
                                    required
                                    name="caregiver_name"
                                    value={formData.caregiver_name}
                                    onChange={handleChange}
                                    className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none transition-all"
                                />
                            </div>
                            <div className="space-y-1">
                                <label className="text-xs font-bold text-gray-500 uppercase">{t('children.registration.relationship')}</label>
                                <select
                                    name="caregiver_relationship"
                                    value={formData.caregiver_relationship}
                                    onChange={handleChange}
                                    className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none transition-all"
                                >
                                    <option value="Mother">{t('children.relationships.mother')}</option>
                                    <option value="Father">{t('children.relationships.father')}</option>
                                    <option value="Grandparent">{t('children.relationships.grandparent')}</option>
                                    <option value="Guardian">{t('children.relationships.guardian')}</option>
                                </select>
                            </div>
                            <div className="space-y-1">
                                <label className="text-xs font-bold text-gray-500 uppercase">{t('children.registration.phone')}</label>
                                <div className="relative">
                                    <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                                    <input
                                        name="caregiver_phone"
                                        value={formData.caregiver_phone}
                                        onChange={handleChange}
                                        className="w-full pl-10 pr-3 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none transition-all"
                                    />
                                </div>
                            </div>
                            <div className="space-y-1">
                                <label className="text-xs font-bold text-gray-500 uppercase">{t('children.registration.email')}</label>
                                <div className="relative">
                                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                                    <input
                                        required
                                        type="email"
                                        name="caregiver_email"
                                        value={formData.caregiver_email}
                                        onChange={handleChange}
                                        className="w-full pl-10 pr-3 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none transition-all"
                                    />
                                </div>
                            </div>
                            <div className="space-y-1 md:col-span-2">
                                <label className="text-xs font-bold text-gray-500 uppercase">{t('children.registration.additional')}</label>
                                <textarea
                                    name="caregiver_additional_info"
                                    value={formData.caregiver_additional_info}
                                    onChange={handleChange}
                                    placeholder={t('children.registration.additional_placeholder')}
                                    className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none transition-all h-20"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Account Section */}
                    <div className="bg-blue-50 p-4 rounded-xl border border-blue-100 space-y-4">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2 text-blue-800 font-semibold">
                                <ShieldCheck className="w-4 h-4" />
                                <span>{t('children.account_section.title')}</span>
                            </div>
                            <input
                                type="checkbox"
                                name="create_parent_account"
                                checked={formData.create_parent_account}
                                onChange={handleChange}
                                className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                            />
                        </div>
                        {formData.create_parent_account && (
                            <div className="space-y-1 animate-in slide-in-from-top-2 duration-300">
                                <label className="text-xs font-bold text-blue-500 uppercase">{t('children.account_section.pwd_label')}</label>
                                <input
                                    required
                                    type="password"
                                    name="parent_password"
                                    value={formData.parent_password}
                                    onChange={handleChange}
                                    placeholder={t('user_mgmt.fields.min_8_chars')}
                                    className="w-full px-3 py-2 bg-white border border-blue-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none transition-all"
                                />
                                <p className="text-[10px] text-blue-400">{t('children.account_section.pwd_sub')}</p>
                            </div>
                        )}
                    </div>

                    <div className="flex gap-3 pt-4">
                        <button
                            type="button"
                            onClick={onClose}
                            className="flex-1 px-4 py-2.5 bg-gray-100 text-gray-700 font-bold rounded-xl hover:bg-gray-200 transition-all uppercase text-sm"
                        >
                            {t('common.cancel')}
                        </button>
                        <button
                            disabled={loading}
                            type="submit"
                            className="flex-[2] px-4 py-2.5 bg-green-600 text-white font-bold rounded-xl hover:bg-green-700 shadow-lg shadow-green-200 transition-all disabled:opacity-50 uppercase text-sm flex items-center justify-center gap-2"
                        >
                            {loading && <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />}
                            {t('children.registration.btn')}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default ChildRegistrationForm;

