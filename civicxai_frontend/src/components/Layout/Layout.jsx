import React, { useState } from 'react';
import { Link, useLocation, Outlet } from 'react-router-dom';
import { 
  LayoutDashboard, 
  FileText, 
  Users, 
  Briefcase,
  Calendar,
  BarChart3,
  Settings,
  LogOut,
  Menu,
  X,
  ChevronDown,
  Sun,
  Moon
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import useAuthStore from '../../store/authStore';

const Layout = () => {
  const location = useLocation();
  const { user, logout } = useAuthStore();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(true);
  const [profileDropdown, setProfileDropdown] = useState(false);

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Proposals', href: '/proposals', icon: FileText },
    { name: 'Contributors', href: '/contributors', icon: Users },
    { name: 'Workgroups', href: '/workgroups', icon: Briefcase },
    { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  ];

  const isActive = (path) => location.pathname === path;

  const handleLogout = async () => {
    await logout();
  };

  return (
    <div className={`min-h-screen ${darkMode ? 'dark' : ''}`}>
      <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
        {/* Sidebar */}
        <aside className={`${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} fixed inset-y-0 left-0 z-50 w-64 transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0`}>
          <div className="flex h-full flex-col bg-gray-900 dark:bg-black">
            {/* Logo */}
            <div className="flex h-16 items-center justify-between px-4 bg-gray-800 dark:bg-gray-950">
              <div className="flex items-center">
                <div className="h-8 w-8 rounded bg-gradient-to-br from-blue-500 to-purple-600" />
                <span className="ml-3 text-xl font-bold text-white">Governance</span>
              </div>
              <button
                onClick={() => setSidebarOpen(false)}
                className="lg:hidden text-gray-400 hover:text-white"
              >
                <X className="h-6 w-6" />
              </button>
            </div>

            {/* User Info */}
            <div className="px-4 py-4 border-b border-gray-800">
              <div className="flex items-center">
                <div className="h-10 w-10 rounded-full bg-gradient-to-br from-purple-400 to-pink-600 flex items-center justify-center text-white font-semibold">
                  {user?.username?.[0]?.toUpperCase() || 'U'}
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium text-white">{user?.username || 'User'}</p>
                  <p className="text-xs text-gray-400 capitalize">{user?.role || 'Member'}</p>
                </div>
              </div>
              <div className="mt-3 flex items-center justify-between">
                <span className="inline-flex items-center rounded-full bg-purple-900/50 px-2.5 py-0.5 text-xs font-medium text-purple-300">
                  CORE CONTRIBUTOR
                </span>
                <span className="text-xs text-gray-500">Available</span>
              </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 space-y-1 px-2 py-4">
              <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider px-3 mb-2">
                Navigation
              </div>
              {navigation.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`
                      flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors
                      ${isActive(item.href) 
                        ? 'bg-gray-800 text-white' 
                        : 'text-gray-300 hover:bg-gray-800 hover:text-white'}
                    `}
                  >
                    <Icon className="mr-3 h-5 w-5 flex-shrink-0" />
                    {item.name}
                  </Link>
                );
              })}
            </nav>

            {/* Settings */}
            <div className="border-t border-gray-800 p-4">
              <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider px-3 mb-2">
                Settings
              </div>
              <Link
                to="/profile"
                className="flex items-center px-3 py-2 text-sm font-medium rounded-md text-gray-300 hover:bg-gray-800 hover:text-white"
              >
                <Settings className="mr-3 h-5 w-5" />
                Profile
              </Link>
            </div>

            {/* AGIX Price */}
            <div className="border-t border-gray-800 p-4">
              <div className="flex items-center justify-between px-3">
                <span className="text-xs text-gray-400">AGIX Price:</span>
                <span className="text-sm font-semibold text-white">0.28</span>
              </div>
            </div>

            {/* Sign Out */}
            <div className="p-4">
              <button
                onClick={handleLogout}
                className="flex w-full items-center px-3 py-2 text-sm font-medium rounded-md text-gray-300 hover:bg-gray-800 hover:text-white"
              >
                <LogOut className="mr-3 h-5 w-5" />
                Sign Out
              </button>
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <div className="flex flex-1 flex-col overflow-hidden">
          {/* Top Header */}
          <header className="bg-white dark:bg-gray-800 shadow-sm">
            <div className="flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
              <button
                onClick={() => setSidebarOpen(true)}
                className="text-gray-500 focus:outline-none lg:hidden"
              >
                <Menu className="h-6 w-6" />
              </button>

              <div className="flex items-center space-x-4">
                {/* Search */}
                <div className="hidden md:block">
                  <input
                    type="text"
                    placeholder="Search..."
                    className="w-64 px-3 py-1.5 text-sm bg-gray-100 dark:bg-gray-700 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>

                {/* Theme Toggle */}
                <button
                  onClick={() => setDarkMode(!darkMode)}
                  className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                >
                  {darkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
                </button>

                {/* Profile Dropdown */}
                <div className="relative">
                  <button
                    onClick={() => setProfileDropdown(!profileDropdown)}
                    className="flex items-center text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    <div className="h-8 w-8 rounded-full bg-gradient-to-br from-purple-400 to-pink-600 flex items-center justify-center text-white font-semibold">
                      {user?.username?.[0]?.toUpperCase() || 'U'}
                    </div>
                    <ChevronDown className="ml-2 h-4 w-4 text-gray-500" />
                  </button>

                  <AnimatePresence>
                    {profileDropdown && (
                      <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="absolute right-0 mt-2 w-48 rounded-md bg-white dark:bg-gray-800 shadow-lg ring-1 ring-black ring-opacity-5"
                      >
                        <div className="py-1">
                          <Link
                            to="/profile"
                            className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700"
                            onClick={() => setProfileDropdown(false)}
                          >
                            Your Profile
                          </Link>
                          <Link
                            to="/settings"
                            className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700"
                            onClick={() => setProfileDropdown(false)}
                          >
                            Settings
                          </Link>
                          <hr className="my-1 border-gray-200 dark:border-gray-600" />
                          <button
                            onClick={() => {
                              setProfileDropdown(false);
                              handleLogout();
                            }}
                            className="block w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700"
                          >
                            Sign out
                          </button>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </div>
            </div>
          </header>

          {/* Page Content */}
          <main className="flex-1 overflow-y-auto bg-gray-50 dark:bg-gray-900">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
};

export default Layout;
