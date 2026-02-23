import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/dashboards/Dashboard';
import ParentDashboard from './pages/dashboards/ParentDashboard';
import ChildrenManagement from './pages/ChildrenManagement';
import Assessments from './pages/Assessments';
import UserManagement from './pages/UserManagement';
import Analytics from './pages/Analytics';
import Referrals from './pages/Referrals';

function App() {
    return (
        <Routes>
            {/* Public Route */}
            <Route path="/login" element={<Login />} />

            {/* Dashboard */}
            <Route
                path="/dashboard"
                element={
                    <ProtectedRoute>
                        <Layout>
                            <Dashboard />
                        </Layout>
                    </ProtectedRoute>
                }
            />

            {/* Children Management */}
            <Route
                path="/children"
                element={
                    <ProtectedRoute allowedRoles={[
                        'anganwadi_worker',
                        'supervisor',
                        'district_officer',
                        'state_admin',
                        'system_admin'
                    ]}>
                        <Layout>
                            <ChildrenManagement />
                        </Layout>
                    </ProtectedRoute>
                }
            />

            {/* Assessments */}
            <Route
                path="/assessments"
                element={
                    <ProtectedRoute allowedRoles={[
                        'anganwadi_worker',
                        'supervisor',
                        'district_officer',
                        'state_admin',
                        'system_admin'
                    ]}>
                        <Layout>
                            <Assessments />
                        </Layout>
                    </ProtectedRoute>
                }
            />

            {/* Referrals */}
            <Route
                path="/referrals"
                element={
                    <ProtectedRoute allowedRoles={[
                        'anganwadi_worker',
                        'supervisor',
                        'district_officer',
                        'state_admin',
                        'system_admin'
                    ]}>
                        <Layout>
                            <Referrals />
                        </Layout>
                    </ProtectedRoute>
                }
            />

            {/* Analytics */}
            <Route
                path="/analytics"
                element={
                    <ProtectedRoute allowedRoles={[
                        'district_officer',
                        'state_admin',
                        'system_admin'
                    ]}>
                        <Layout>
                            <Analytics />
                        </Layout>
                    </ProtectedRoute>
                }
            />

            {/* User Management */}
            <Route
                path="/users"
                element={
                    <ProtectedRoute allowedRoles={[
                        'system_admin',
                        'state_admin',
                        'district_officer',
                        'supervisor',
                        'anganwadi_worker'
                    ]}>
                        <Layout>
                            <UserManagement />
                        </Layout>
                    </ProtectedRoute>
                }
            />

            {/* Parent Portal */}
            <Route
                path="/my-children"
                element={
                    <ProtectedRoute allowedRoles={['parent']}>
                        <Layout>
                            <ParentDashboard />
                        </Layout>
                    </ProtectedRoute>
                }
            />

            {/* Default Route */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />

            {/* 404 */}
            <Route
                path="*"
                element={
                    <div className="min-h-screen flex items-center justify-center">
                        <div className="text-center">
                            <h1 className="text-4xl font-bold text-gray-900 mb-4">404</h1>
                            <p className="text-gray-600">Page not found</p>
                        </div>
                    </div>
                }
            />
        </Routes>
    );
}

export default App;