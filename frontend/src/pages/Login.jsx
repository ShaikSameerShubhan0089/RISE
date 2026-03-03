import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { Activity, Globe } from 'lucide-react';
import logo from '../../../logo/logo.png';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const { login } = useAuth();
    const { language, setLanguage, t } = useLanguage();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        const result = await login(email, password);

        if (result.success) {
            navigate('/dashboard');
        } else {
            setError(result.error);
        }

        setLoading(false);
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 flex items-center justify-center px-4">
            <div className="max-w-md w-full">
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-50 h-40 p-2 bg-white mb-2 shadow-2xl">
                        <img src={logo} alt="RISE" className="w-full h-full object-contain" />
                    </div>
                    
                    {/* logo only - no additional text */}
                </div>

                <div className="bg-white rounded-3xl shadow-2xl p-8 border-2 border-primary-100">
                    <div className="flex justify-between items-center mb-8">
                        <h2 className="text-2xl font-bold text-gray-800">{t('common.sign_in')}</h2>
                        <div className="flex items-center gap-2 px-3 py-1.5 bg-gradient-to-r from-primary-50 to-primary-100 rounded-full border border-primary-200">
                            {/* use project logo as language toggle icon instead of globe */}
                        <img src={logo} alt="logo" className="w-4 h-4 object-contain" />
                            <select
                                value={language}
                                onChange={(e) => setLanguage(e.target.value)}
                                className="text-xs font-bold bg-transparent border-none focus:ring-0 cursor-pointer text-primary-600 outline-none p-0"
                            >
                                <option value="en">English</option>
                                <option value="te">తెలుగు</option>
                                <option value="hi">हिन्दी</option>
                                <option value="kn">ಕನ್ನಡ</option>
                                <option value="ta">தமிழ்</option>
                                <option value="ur">اردو</option>
                            </select>
                        </div>
                    </div>

                    {error && (
                        <div className="mb-6 p-4 bg-red-100 border-2 border-red-300 rounded-2xl">
                            <p className="text-sm font-semibold text-red-700">⚠️ {error}</p>
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-5">
                        <div>
                            <label htmlFor="email" className="block text-sm font-bold text-gray-700 mb-2">
                                📧 {t('common.email')}
                            </label>
                            <input
                                id="email"
                                type="email"
                                required
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="w-full px-4 py-3 border-2 border-gray-300 rounded-2xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition font-semibold text-gray-800"
                                placeholder={t('common.email_placeholder')}
                            />
                        </div>

                        <div>
                            <label htmlFor="password" className="block text-sm font-bold text-gray-700 mb-2">
                                🔐 {t('common.password')}
                            </label>
                            <input
                                id="password"
                                type="password"
                                required
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full px-4 py-3 border-2 border-gray-300 rounded-2xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition font-semibold"
                                placeholder="••••••••"
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 text-white font-bold py-3 px-4 rounded-2xl transition disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl transform hover:scale-105 transition"
                        >
                            {loading ? t('common.signing_in') : `🚀 ${t('common.sign_in')}`}
                        </button>
                    </form>

                    {language === 'en' && (
                        <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-2xl border-2 border-blue-200">
                            <p className="text-xs font-bold text-gray-700 mb-3">👥 {t('common.test_creds')}:</p>
                            <div className="text-xs text-gray-600 space-y-2">
                                <p><strong className="text-primary-600">👨‍💼 {t('common.test_creds_admin')}:</strong> admin@cdss.gov.in / admin123</p>
                                <p><strong className="text-primary-600">👩‍💼 {t('common.test_creds_worker')}:</strong> worker@awc001.gov.in / worker123</p>
                            </div>
                        </div>
                    )}
                </div>

                <div className="mt-6 text-center">
                    <p className="text-xs text-gray-500">
                        ⚠️ {t('common.disclaimer_text')}
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Login;