import React, { useState, useEffect } from 'react';
import { childrenAPI, dashboardAPI } from '../utils/api';
import {
    ClipboardList,
    User,
    BrainCircuit,
    ChevronRight,
    AlertTriangle,
    CheckCircle2,
    Info,
    ArrowRight,
    FileText,
    Activity,
    TrendingUp
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import VoiceButton from '../components/common/VoiceButton';

const Assessments = () => {
    const { user } = useAuth();
    const { t } = useLanguage();
    const [children, setChildren] = useState([]);
    const [selectedChildId, setSelectedChildId] = useState('');
    const [modelType, setModelType] = useState('Model A');
    const [formData, setFormData] = useState({});
    const [loading, setLoading] = useState(false);
    const [prediction, setPrediction] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchChildren = async () => {
            try {
                const res = await childrenAPI.list({ status_filter: 'Active' });
                setChildren(res.data);
            } catch (err) {
                console.error('Failed to fetch children', err);
            }
        };
        fetchChildren();
    }, []);

    const handleInputChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : (type === 'number' ? parseFloat(value) : value)
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setPrediction(null);

        try {
            const payload = {
                child_id: parseInt(selectedChildId),
                model_type: modelType,
                inputs: formData
            };
            const res = await dashboardAPI.runRealtimePrediction(payload);
            setPrediction(res.data);
        } catch (err) {
            setError(err.response?.data?.detail || 'Prediction failed. Please check inputs.');
        } finally {
            setLoading(false);
        }
    };

    const renderModelAForm = () => (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
                <h3 className="font-bold text-gray-700 border-b pb-2 flex items-center gap-2">
                    <BrainCircuit className="w-4 h-4 text-primary-600" />
                    {t('assessments.form.dq')}
                </h3>
                <div className="grid grid-cols-2 gap-4">
                    {['gross_motor_dq', 'fine_motor_dq', 'language_dq', 'cognitive_dq', 'socio_emotional_dq', 'composite_dq'].map(field => (
                        <div key={field} className="space-y-1">
                            <label className="text-xs font-bold text-gray-500 uppercase">{t(`parent.dq_labels.${field}`)}*</label>
                            <input
                                required
                                type="number"
                                name={field}
                                value={formData[field] || ''}
                                onChange={handleInputChange}
                                min="0" max="200" step="any"
                                className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 outline-none transition-all text-sm"
                            />
                        </div>
                    ))}
                </div>

                <h3 className="font-bold text-gray-700 border-b pb-2 pt-4 flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-orange-500" />
                    {t('assessments.form.risks')}
                </h3>
                <div className="flex flex-wrap gap-4 pt-2">
                    {['adhd_risk', 'behavior_risk'].map(field => (
                        <label key={field} className="flex items-center gap-2 cursor-pointer group">
                            <input
                                type="checkbox"
                                name={field}
                                checked={formData[field] || false}
                                onChange={handleInputChange}
                                className="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                            />
                            <span className="text-sm font-medium text-gray-700 group-hover:text-gray-900 capitalize">{t(`assessments.form.${field}`)}</span>
                        </label>
                    ))}
                </div>
            </div>

            <div className="space-y-4">
                <h3 className="font-bold text-gray-700 border-b pb-2 flex items-center gap-2">
                    <Info className="w-4 h-4 text-blue-500" />
                    {t('assessments.form.env')}
                </h3>
                <div className="grid grid-cols-1 gap-4">
                    {[
                        { key: 'caregiver_engagement_score', label: t('assessments.form.caregiver_engagement') },
                        { key: 'stimulation_score', label: t('assessments.form.stimulation') },
                        { key: 'language_exposure_score', label: t('assessments.form.language_exposure') }
                    ].map(field => (
                        <div key={field.key} className="space-y-1">
                            <label className="text-xs font-bold text-gray-500 uppercase tracking-tighter">{field.label}</label>
                            <input
                                type="number"
                                name={field.key}
                                value={formData[field.key] || ''}
                                onChange={handleInputChange}
                                min="0" max="200" step="any"
                                className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 outline-none transition-all text-sm"
                            />
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );

    const renderModelBForm = () => (
        <div className="bg-orange-50 p-6 rounded-2xl border border-orange-100 space-y-4 text-center">
            <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mx-auto shadow-sm">
                <AlertTriangle className="w-8 h-8 text-orange-500" />
            </div>
            <h3 className="text-lg font-bold text-orange-900">Model B: {t('analytics.charts.ai_sub')}</h3>
            <p className="text-orange-800 text-sm max-w-md mx-auto">
                {t('assessments.model_b_desc')}
            </p>
            <div className="bg-white p-4 rounded-xl text-left space-y-4 shadow-sm">
                <p className="text-xs font-bold text-gray-400 uppercase">{t('assessments.input_reqs')}</p>
                <p className="text-sm text-gray-600">
                    {t('assessments.form.baseline')}
                </p>
                {renderModelAForm()} {/* Reusing fields since Model B also uses current DQ scores */}
            </div>
        </div>
    );

    return (
        <div className="p-6 space-y-6 max-w-5xl mx-auto">
            <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center">
                    <ClipboardList className="w-6 h-6 text-primary-600" />
                </div>
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">{t('assessments.title')}</h1>
                    <p className="text-gray-500 text-sm">{t('assessments.sub')}</p>
                </div>
            </div>

            {!prediction ? (
                <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
                    <div className="p-6 bg-gray-50 border-b border-gray-200 grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-1">
                            <label className="text-xs font-bold text-gray-500 uppercase flex items-center gap-1">
                                <User className="w-3 h-3" /> {t('assessments.select_child')}
                            </label>
                            <select
                                required
                                value={selectedChildId}
                                onChange={(e) => setSelectedChildId(e.target.value)}
                                className="w-full px-4 py-2.5 bg-white border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 outline-none transition-all font-medium"
                            >
                                <option value="">{t('assessments.choose_child')}</option>
                                {children.map(c => (
                                    <option key={c.child_id} value={c.child_id}>
                                        {c.first_name} {c.last_name} ({c.unique_child_code})
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div className="space-y-1">
                            <label className="text-xs font-bold text-gray-500 uppercase flex items-center gap-1">
                                <BrainCircuit className="w-3 h-3" /> {t('assessments.model')}
                            </label>
                            <div className="flex bg-white p-1 rounded-xl border border-gray-200">
                                {['Model A', 'Model B'].map(m => (
                                    <button
                                        key={m}
                                        type="button"
                                        onClick={() => setModelType(m)}
                                        className={`flex-1 py-1.5 rounded-lg text-sm font-bold transition-all ${modelType === m
                                            ? 'bg-primary-600 text-white shadow-md'
                                            : 'text-gray-500 hover:bg-gray-50'
                                            }`}
                                    >
                                        {m}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>

                    <form onSubmit={handleSubmit} className="p-6 space-y-8">
                        {selectedChildId ? (
                            <>
                                {modelType === 'Model A' ? renderModelAForm() : renderModelBForm()}

                                <div className="pt-6 border-t flex justify-end">
                                    <button
                                        disabled={loading}
                                        type="submit"
                                        className="bg-primary-600 text-white px-8 py-3 rounded-2xl font-bold hover:bg-primary-700 transition-all flex items-center gap-2 shadow-xl shadow-primary-100 disabled:opacity-50"
                                    >
                                        {loading ? (
                                            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
                                        ) : (
                                            <ArrowRight className="w-5 h-5" />
                                        )}
                                        {t('assessments.run').replace('{model}', modelType)}
                                    </button>
                                </div>
                            </>
                        ) : (
                            <div className="py-20 text-center space-y-4">
                                <div className="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mx-auto">
                                    <User className="w-8 h-8 text-gray-300" />
                                </div>
                                <p className="text-gray-500 font-medium">{t('assessments.select_child_msg')}</p>
                            </div>
                        )}

                        {error && (
                            <div className="p-4 bg-red-50 border border-red-100 rounded-xl flex items-center gap-3 text-red-700">
                                <AlertTriangle className="w-5 h-5 flex-shrink-0" />
                                <p className="text-sm font-medium">{error}</p>
                            </div>
                        )}
                    </form>
                </div>
            ) : (
                /* Prediction Result View */
                <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                    <div className="bg-white rounded-3xl border border-gray-200 shadow-xl overflow-hidden">
                        <div className={`p-8 text-white ${prediction.risk_tier.includes('High') ? 'bg-gradient-to-r from-red-600 to-orange-600' : 'bg-gradient-to-r from-green-600 to-teal-600'}`}>
                            <div className="flex justify-between items-start">
                                <div>
                                    <p className="text-white/80 font-bold uppercase text-xs tracking-wider mb-1">{t('assessments.result_title')}</p>
                                    <h2 className="text-4xl font-black">{prediction.risk_tier}</h2>
                                    <div className="flex items-center gap-2 mt-2 bg-white/20 backdrop-blur-sm px-3 py-1 rounded-full text-sm font-bold w-fit">
                                        <BrainCircuit className="w-4 h-4" />
                                        <span>{t('assessments.probability')}: {(prediction.combined_high_probability * 100).toFixed(1)}%</span>
                                    </div>
                                </div>
                                <div className="flex items-center gap-3">
                                    <VoiceButton
                                        content={`${t('assessments.result_title')}: ${prediction.risk_tier}. ${t('assessments.probability')}: ${(prediction.combined_high_probability * 100).toFixed(1)} percent. ${prediction.clinical_summary}`}
                                    />
                                    <div className="bg-white/20 p-4 rounded-2xl backdrop-blur-md">
                                        <CheckCircle2 className="w-12 h-12 text-white" />
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="p-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
                            <div className="lg:col-span-2 space-y-6">
                                <div className="space-y-2">
                                    <h3 className="font-bold text-gray-900 flex items-center gap-2">
                                        <FileText className="w-5 h-5 text-gray-400" />
                                        {t('assessments.summary')}
                                    </h3>
                                    <p className="text-gray-700 leading-relaxed bg-gray-50 p-4 rounded-2xl border border-gray-100">
                                        {prediction.clinical_summary}
                                    </p>
                                </div>

                                <div className="space-y-4">
                                    <h3 className="font-bold text-gray-900 flex items-center gap-2">
                                        <TrendingUp className="w-5 h-5 text-gray-400" />
                                        {t('assessments.drivers')}
                                    </h3>
                                    <div className="space-y-3">
                                        {prediction.top_features.map((feat, idx) => (
                                            <div key={idx} className="flex items-center justify-between group">
                                                <div className="flex-1">
                                                    <div className="flex justify-between mb-1 px-1">
                                                        <span className="text-sm font-bold text-gray-700 capitalize">{t(`parent.dq_labels.${feat.feature_name}`) || feat.feature_name.replace(/_/g, ' ')}</span>
                                                        <span className={`text-xs font-bold ${feat.shap_value > 0 ? 'text-red-500' : 'text-green-500'}`}>
                                                            {feat.shap_value > 0 ? '+' : ''}{feat.shap_value.toFixed(3)}
                                                        </span>
                                                    </div>
                                                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                                                        <div
                                                            className={`h-full rounded-full ${feat.impact_direction === 'Positive' ? 'bg-red-500' : 'bg-green-500'}`}
                                                            style={{ width: `${Math.min(100, Math.abs(feat.shap_value) * 100)}%` }}
                                                        />
                                                    </div>
                                                    <p className="text-[10px] text-gray-500 mt-1 italic px-1">{feat.interpretation}</p>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>

                            <div className="space-y-6">
                                <div className="bg-primary-50 rounded-2xl p-6 border border-primary-100">
                                    <h3 className="font-bold text-primary-900 mb-4 flex items-center gap-2">
                                        <Activity className="w-5 h-5" />
                                        {t('assessments.actions')}
                                    </h3>
                                    <div className="space-y-4">
                                        {prediction.recommendations.map((rec, idx) => (
                                            <div key={idx} className="bg-white p-4 rounded-xl shadow-sm border border-primary-100">
                                                <div className="flex justify-between items-start mb-1">
                                                    <span className="text-[10px] font-black text-primary-500 uppercase tracking-widest">{rec.category}</span>
                                                    <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${rec.priority === 'High' ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'
                                                        }`}>
                                                        {rec.priority}
                                                    </span>
                                                </div>
                                                <p className="text-sm font-bold text-gray-800 leading-tight">{rec.action_plan}</p>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                <div className="p-4 bg-gray-50 rounded-2xl border border-gray-100">
                                    <p className="text-[10px] text-gray-400 uppercase font-bold mb-2">{t('assessments.disclaimer_label')}</p>
                                    <p className="text-[10px] text-gray-500 leading-tight italic">
                                        {prediction.disclaimer}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="flex justify-center pt-4">
                        <button
                            onClick={() => { setPrediction(null); setFormData({}); }}
                            className="bg-gray-900 text-white px-8 py-3 rounded-2xl font-bold hover:bg-black transition-all shadow-lg"
                        >
                            {t('assessments.new_assessment')}
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};



export default Assessments;
