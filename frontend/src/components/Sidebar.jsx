import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
    LayoutDashboard,
    Users,
    ClipboardList,
    TrendingUp,
    UserCog,
    FileText,
    LogOut,
    Activity,
    Globe,
    Volume2,
    ChevronDown
} from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';
import logo from '../../../logo/logo.png';

const Sidebar = () => {
    const { user, logout } = useAuth();
    const { language, setLanguage, t, speak } = useLanguage();
    const location = useLocation();
    const [availableVoices, setAvailableVoices] = useState([]);
    const [selectedVoice, setSelectedVoice] = useState('default');
    const [showVoiceDropdown, setShowVoiceDropdown] = useState(false);

    // Load available voices
    useEffect(() => {
        const loadVoices = () => {
            const voices = window.speechSynthesis?.getVoices() || [];
            const langVoices = voices.filter(v => v.lang.startsWith(language));
            setAvailableVoices(langVoices);
        };

        loadVoices();
        window.speechSynthesis?.addEventListener('voiceschanged', loadVoices);
        return () => window.speechSynthesis?.removeEventListener('voiceschanged', loadVoices);
    }, [language]);

    const getRoleBasedNavigation = () => {
        const commonItems = [
            { path: '/dashboard', icon: LayoutDashboard, label: t('common.dashboard') },
        ];

        const roleSpecificItems = {
            system_admin: [
                { path: '/users', icon: UserCog, label: t('common.users') },
                { path: '/referrals', icon: ClipboardList, label: t('common.referrals') },
                { path: '/analytics', icon: TrendingUp, label: t('common.analytics') },
            ],
            state_admin: [
                { path: '/users', icon: UserCog, label: t('common.users') },
                { path: '/children', icon: Users, label: t('common.children') },
                { path: '/referrals', icon: ClipboardList, label: t('common.referrals') },
                { path: '/analytics', icon: TrendingUp, label: t('common.analytics') },
            ],
            district_officer: [
                { path: '/users', icon: UserCog, label: t('common.users') },
                { path: '/children', icon: Users, label: t('common.children') },
                { path: '/referrals', icon: ClipboardList, label: t('common.referrals') },
                { path: '/analytics', icon: TrendingUp, label: t('common.analytics') },
            ],
            supervisor: [
                { path: '/users', icon: UserCog, label: t('common.users') },
                { path: '/children', icon: Users, label: t('common.children') },
                { path: '/assessments', icon: ClipboardList, label: t('common.assessments') },
                { path: '/referrals', icon: FileText, label: t('common.referrals') },
            ],
            anganwadi_worker: [
                { path: '/users', icon: UserCog, label: t('common.users') },
                { path: '/children', icon: Users, label: t('common.children') },
                { path: '/assessments', icon: ClipboardList, label: t('common.assessments') },
                { path: '/referrals', icon: FileText, label: t('common.referrals') },
            ],
            parent: [
                { path: '/my-children', icon: Users, label: t('common.children') },
            ],
        };

        return [...commonItems, ...(roleSpecificItems[user?.role] || [])];
    };

    const navItems = getRoleBasedNavigation();

    const isActive = (path) => location.pathname === path;

    return (
        <div className="h-screen w-64 bg-white border-r border-gray-200 flex flex-col">
            {/* Logo */}
            <div className="p-6 border-b border-gray-200">
                <div className="flex flex-col items-center">
                    <div className="w-50 h-50 flex items-center justify-center">
                        <img src={logo} alt="RISE" className="max-w-full max-h-full object-contain" />
                    </div>
                    <p className="text-xs text-gray-500 capitalize mt-2">{user?.role?.replace('_', ' ')}</p>
                </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 p-4 space-y-1 overflow-y-auto custom-scrollbar">
                {navItems.map((item) => {
                    const Icon = item.icon;
                    const active = isActive(item.path);

                    return (
                        <Link
                            key={item.path}
                            to={item.path}
                            className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition ${active
                                ? 'bg-primary-50 text-primary-700 font-medium'
                                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                                }`}
                        >
                            <Icon className="w-5 h-5" />
                            <span>{item.label}</span>
                        </Link>
                    );
                })}
            </nav>

            {/* Language Switcher & Voice Control */}
            <div className="p-4 border-t border-gray-200 space-y-2">
                {/* Language Toggle */}
                <div className="px-4 py-2 border border-gray-200 rounded-lg flex items-center justify-between">
                    <div className="flex items-center gap-2 text-gray-600">
                        {/* use project logo in place of globe icon for language selector */}
                        <img src={logo} alt="logo" className="w-4 h-4 object-contain" />
                        <span className="text-xs font-semibold uppercase">{t('sidebar.language')}</span>
                    </div>
                    <select
                        value={language}
                        onChange={(e) => setLanguage(e.target.value)}
                        className="text-xs font-medium border-none bg-transparent focus:ring-0 cursor-pointer text-primary-600 outline-none"
                    >
                        <option value="en">English</option>
                        <option value="te">తెలుగు</option>
                        <option value="hi">हिन्दी</option>
                        <option value="kn">ಕನ್ನಡ</option>
                        <option value="ur">اردو</option>
                        <option value="ta">தமிழ்</option>
                    </select>
                </div>

                {/* Voice Selector */}
                <div className="relative">
                    <button
                        onClick={() => setShowVoiceDropdown(!showVoiceDropdown)}
                        className="w-full px-4 py-2 border border-gray-200 rounded-lg flex items-center justify-between hover:bg-gray-50 transition"
                    >
                        <div className="flex items-center gap-2 text-gray-600">
                            <Volume2 className="w-4 h-4" />
                            <span className="text-xs font-semibold uppercase">Voice</span>
                        </div>
                        <ChevronDown className={`w-3 h-3 text-gray-400 transition ${showVoiceDropdown ? 'rotate-180' : ''}`} />
                    </button>
                    {showVoiceDropdown && availableVoices.length > 0 && (
                        <div className="absolute bottom-full left-0 right-0 mb-2 bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-48 overflow-y-auto">
                            <button
                                onClick={() => {
                                    speak('Hello, system voice test');
                                    setShowVoiceDropdown(false);
                                }}
                                className="w-full text-left px-3 py-2 text-xs hover:bg-blue-50 text-gray-700 border-b border-gray-100"
                            >
                                🔊 System Default
                            </button>
                            {availableVoices.slice(0, 8).map((voice, idx) => (
                                <button
                                    key={idx}
                                    onClick={() => {
                                        speak('Voice test');
                                        setShowVoiceDropdown(false);
                                    }}
                                    className="w-full text-left px-3 py-2 text-xs hover:bg-blue-50 text-gray-700 border-t border-gray-100 truncate"
                                    title={voice.name}
                                >
                                    {voice.name.substring(0, 28)}...
                                </button>
                            ))}
                        </div>
                    )}
                </div>

                {/* Test Voice Button */}
                <button
                    onClick={() => speak(`${t('common.welcome')}!`)}
                    className="w-full px-3 py-2 bg-blue-50 text-blue-600 hover:bg-blue-100 rounded-lg transition text-xs font-semibold flex items-center justify-center gap-2"
                >
                    <Volume2 className="w-3 h-3" />
                    Test Voice
                </button>

                <div className="mb-3 px-4 py-2 bg-gray-50 rounded-lg">
                    <p className="text-sm font-medium text-gray-900">{user?.full_name}</p>
                    <p className="text-xs text-gray-500 truncate">{user?.email}</p>
                </div>
                <button
                    onClick={logout}
                    className="w-full flex items-center justify-center space-x-2 px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition"
                >
                    <LogOut className="w-5 h-5" />
                    <span>{t('common.logout')}</span>
                </button>
            </div>
        </div>
    );
};

export default Sidebar;
