import React from 'react';
import Sidebar from './Sidebar';

const Layout = ({ children }) => {
    return (
        <div className="flex h-screen overflow-hidden">
            <Sidebar />
            <main className="flex-1 overflow-y-auto bg-gray-50 custom-scrollbar">
                {children}
            </main>
        </div>
    );
};

export default Layout;
