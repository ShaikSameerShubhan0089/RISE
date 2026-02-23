import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';   // ✅ THIS WAS MISSING

const ProtectedRoute = ({ children, allowedRoles }) => {
    const { user, token, loading } = useAuth();

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            </div>
        );
    }

    if (!user || !token) {
        return <Navigate to="/login" replace />;
    }

    if (allowedRoles && !allowedRoles.includes(user.role)) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="text-center">
                    <h1 className="text-4xl font-bold text-gray-900 mb-4">
                        Access Denied
                    </h1>
                    <p className="text-gray-600">
                        You do not have permission to view this page.
                    </p>
                </div>
            </div>
        );
    }

    return children;
};

export default ProtectedRoute;