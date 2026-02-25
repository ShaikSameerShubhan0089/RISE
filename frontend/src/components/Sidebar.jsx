import React from 'react';
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
    Globe
} from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

const Sidebar = () => {
    const { user, logout } = useAuth();
    const { language, setLanguage, t } = useLanguage();
    const location = useLocation();

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
                <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
                        <Activity className="w-6 h-6 text-white" />
                    </div>
                    <div>
                        <h1 className="text-lg font-bold text-gray-900">{t('sidebar.title')}</h1>
                        <p className="text-xs text-gray-500 capitalize">{user?.role?.replace('_', ' ')}</p>
                    </div>
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

            {/* Language Switcher & Logout */}
            <div className="p-4 border-t border-gray-200 space-y-2">
                {/* Language Toggle */}
                <div className="px-4 py-2 border border-gray-200 rounded-lg flex items-center justify-between">
                    <div className="flex items-center gap-2 text-gray-600">
                        <Globe className="w-4 h-4" />
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
                    </select>
                </div>

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
