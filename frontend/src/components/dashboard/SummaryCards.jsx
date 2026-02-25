import React from 'react';
import { useLanguage } from '../../context/LanguageContext';

const CARD_CONFIGS = [
    { key: 'total_children', label: 'Total Children', icon: '👶', color: 'from-blue-500 to-blue-600' },
    { key: 'active_children', label: 'Active Children', icon: '✅', color: 'from-green-500 to-green-600' },
    { key: 'total_interventions', label: 'Interventions', icon: '🏥', color: 'from-purple-500 to-purple-600' },
    { key: 'total_assessments', label: 'Assessments', icon: '📋', color: 'from-amber-500 to-amber-600' },
    { key: 'workers', label: 'AWC Workers', icon: '👩‍⚕️', color: 'from-teal-500 to-teal-600' },
    { key: 'supervisors', label: 'Supervisors', icon: '👤', color: 'from-rose-500 to-rose-600' },
    { key: 'total_centers', label: 'Centres', icon: '🏫', color: 'from-indigo-500 to-indigo-600' },
];

const SummaryCards = ({ data = {}, keys }) => {
    const { t } = useLanguage();
    const displayKeys = keys || Object.keys(data);
    const cards = CARD_CONFIGS.filter(c => displayKeys.includes(c.key) || !keys);

    return (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-7 gap-4 mb-6">
            {cards.map(({ key, icon, color }) => (
                data[key] !== undefined && (
                    <div key={key} className={`bg-gradient-to-br ${color} rounded-xl p-4 text-white shadow-lg`}>
                        <div className="text-2xl mb-1">{icon}</div>
                        <div className="text-2xl font-bold">{(data[key] ?? 0).toLocaleString()}</div>
                        <div className="text-xs text-white/80 mt-1 font-medium">
                            {t(`analytics.metrics.${key}`)}
                        </div>
                    </div>
                )
            ))}
        </div>
    );
};

export default SummaryCards;
