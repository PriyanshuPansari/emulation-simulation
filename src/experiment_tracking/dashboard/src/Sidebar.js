import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Home, PlusCircle, Menu, X } from 'lucide-react';

const Sidebar = () => {
  const [isOpen, setIsOpen] = useState(true);
  const location = useLocation();

  const toggleSidebar = () => setIsOpen(!isOpen);

  const NavItem = ({ to, icon: Icon, label }) => {
    const isActive = location.pathname === to;
    return (
      <Link
        to={to}
        className={`flex items-center space-x-4 p-2 rounded-lg transition-colors duration-200
          ${isActive 
            ? 'bg-blue-600 text-white' 
            : 'text-gray-300 hover:bg-gray-700'
          }`}
      >
        <Icon size={20} />
        {isOpen && <span>{label}</span>}
      </Link>
    );
  };

  return (
    <div 
      className={`fixed top-0 left-0 h-screen bg-gray-900 text-white transition-all duration-300 
        ${isOpen ? 'w-64' : 'w-16'} flex flex-col`}
    >
      <button 
        onClick={toggleSidebar}
        className="absolute top-4 right-4 text-gray-300 hover:text-white"
      >
        {isOpen ? <X size={20} /> : <Menu size={20} />}
      </button>
      <div className="flex items-center justify-center h-16 bg-gray-800">
        {isOpen && <span className="text-xl font-bold">Dashboard</span>}
      </div>
      <nav className="flex flex-col space-y-2 mt-8 px-4">
        <NavItem to="/" icon={Home} label="Overview" />
        <NavItem to="/new-page" icon={PlusCircle} label="CHIP-8 Emulator" />
        <NavItem to="/PastRuns" icon={PlusCircle} label="Past Runs" />
      </nav>
    </div>
  );
};

export default Sidebar;