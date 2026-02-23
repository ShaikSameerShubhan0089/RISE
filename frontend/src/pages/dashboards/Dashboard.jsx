import React from 'react';
import { useAuth } from '../../context/AuthContext';

import AnganwadiWorkerDashboard from './AnganwadiWorkerDashboard';
import SupervisorDashboard from './SupervisorDashboard';
import DistrictOfficerDashboard from './DistrictOfficerDashboard';
import StateAdminDashboard from './StateAdminDashboard';
import SystemAdminDashboard from './SystemAdminDashboard';
import ParentDashboard from './ParentDashboard';

const DASHBOARDS = {
    anganwadi_worker: AnganwadiWorkerDashboard,
    supervisor: SupervisorDashboard,
    district_officer: DistrictOfficerDashboard,
    state_admin: StateAdminDashboard,
    system_admin: SystemAdminDashboard,
    parent: ParentDashboard,
};

const Dashboard = () => {
    const { user } = useAuth();
    const role = user?.role;
    const RoleDashboard = DASHBOARDS[role];

    if (!RoleDashboard) {
        return (
            <div className="flex flex-col items-center justify-center h-64 text-gray-500">
                <div className="text-4xl mb-3">🚫</div>
                <p className="text-lg font-medium">No dashboard available for role: <strong>{role}</strong></p>
                <p className="text-sm mt-1">Please contact a system administrator.</p>
            </div>
        );
    }

    return <RoleDashboard />;
};

export default Dashboard;
