import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../utils/api';

const AuthContext = createContext(null);

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within AuthProvider');
    }
    return context;
};

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(null);
    const [loading, setLoading] = useState(true);

    // Initialize auth state from localStorage
useEffect(() => {
    try {
        const storedToken = localStorage.getItem('token');
        const storedUser = localStorage.getItem('user');

        if (storedToken && storedUser && storedUser !== "undefined") {
            setToken(storedToken);
            setUser(JSON.parse(storedUser));
        } else {
            localStorage.removeItem('user');
        }
    } catch (error) {
        console.error("Error parsing stored user:", error);
        localStorage.removeItem('user');
        localStorage.removeItem('token');
    }

    setLoading(false);
}, []);

    const login = async (email, password) => {
        try {
            const response = await authAPI.login({ email, password });
            const { access_token, user: userData } = response.data;

            setToken(access_token);
            setUser(userData);

            localStorage.setItem('token', access_token);
            localStorage.setItem('user', JSON.stringify(userData));

            return { success: true };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.detail || 'Login failed',
            };
        }
    };

    const logout = () => {
        setToken(null);
        setUser(null);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
    };

    const hasRole = (allowedRoles) => {
        if (!user) return false;
        return allowedRoles.includes(user.role);
    };

    const value = {
        user,
        token,
        loading,
        login,
        logout,
        hasRole,
        isAuthenticated: !!token,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
