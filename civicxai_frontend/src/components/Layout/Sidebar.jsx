import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import {
  LayoutDashboard,
  FileText,
  Users,
  Briefcase,
  BarChart3,
  Settings,
  LogOut,
  ChevronRight,
  Activity,
  Target,
  Globe,
  Zap
} from 'lucide-react';
import useAuthStore from '@/store/authStore';

const Sidebar = () => {
  const location = useLocation();
  const { user, logout } = useAuthStore();

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Proposals', href: '/proposals', icon: FileText },
    { name: 'Contributors', href: '/contributors', icon: Users },
    { name: 'Workgroups', href: '/workgroups', icon: Briefcase },
    { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  ];

  const bottomNav = [
    { name: 'Settings', href: '/settings', icon: Settings },
  ];

  return (
    <div className="flex h-full w-64 flex-col bg-slate-950 border-r border-slate-800">
      {/* Logo */}
      <div className="flex h-16 items-center gap-3 px-4 border-b border-slate-800">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-violet-600 to-indigo-600">
          <Zap className="h-6 w-6 text-white" />
        </div>
        <div>
          <h1 className="text-lg font-semibold text-white">CivicXAI</h1>
          <p className="text-xs text-slate-400">Governance Platform</p>
        </div>
      </div>

      {/* User Info */}
      <div className="px-4 py-4 border-b border-slate-800">
        {user ? (
          <>
            <div className="flex items-center gap-3">
              <Avatar className="h-10 w-10 border-2 border-violet-600/20">
                <AvatarImage src={user?.profile_image} />
                <AvatarFallback className="bg-gradient-to-br from-violet-600 to-indigo-600 text-white">
                  {user?.username?.[0]?.toUpperCase() || 'U'}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1">
                <p className="text-sm font-medium text-white">{user?.username || 'User'}</p>
                <p className="text-xs text-slate-400 capitalize">{user?.role || 'Member'}</p>
              </div>
              <Badge variant="outline" className="border-green-500/30 bg-green-500/10 text-green-400">
                Online
              </Badge>
            </div>
            <div className="mt-3 flex items-center justify-between">
              <Badge className="bg-violet-600/20 text-violet-400 hover:bg-violet-600/30">
                Core Contributor
              </Badge>
              <div className="flex items-center gap-1">
                <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                <span className="text-xs text-slate-400">Available</span>
              </div>
            </div>
          </>
        ) : (
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <Avatar className="h-10 w-10 border-2 border-slate-600">
                <AvatarFallback className="bg-slate-800 text-slate-400">
                  G
                </AvatarFallback>
              </Avatar>
              <div className="flex-1">
                <p className="text-sm font-medium text-white">Guest User</p>
                <p className="text-xs text-slate-400">Browsing Mode</p>
              </div>
            </div>
            <Link to="/login">
              <Button 
                variant="outline" 
                className="w-full border-violet-600/30 bg-violet-600/10 text-violet-400 hover:bg-violet-600/20 hover:text-violet-300"
              >
                <LogOut className="h-4 w-4 mr-2 rotate-180" />
                Sign In
              </Button>
            </Link>
          </div>
        )}
      </div>

      {/* Navigation */}
      <ScrollArea className="flex-1 px-2 py-4">
        <div className="space-y-1">
          <p className="px-3 text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
            Navigation
          </p>
          {navigation.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.href;
            return (
              <Link key={item.name} to={item.href}>
                <Button
                  variant={isActive ? "secondary" : "ghost"}
                  className={cn(
                    "w-full justify-start gap-3",
                    isActive 
                      ? "bg-violet-600/20 text-violet-400 hover:bg-violet-600/30" 
                      : "text-slate-300 hover:text-white hover:bg-slate-800/50"
                  )}
                >
                  <Icon className="h-5 w-5" />
                  {item.name}
                  {isActive && (
                    <ChevronRight className="ml-auto h-4 w-4" />
                  )}
                </Button>
              </Link>
            );
          })}
        </div>

        {/* Quick Stats */}
        <div className="mt-6 space-y-3 px-3">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Quick Stats
          </p>
          <div className="space-y-2">
            <div className="flex items-center justify-between rounded-lg bg-slate-800/50 px-3 py-2">
              <div className="flex items-center gap-2">
                <Activity className="h-4 w-4 text-green-400" />
                <span className="text-xs text-slate-300">Active Proposals</span>
              </div>
              <span className="text-xs font-semibold text-white">21</span>
            </div>
            <div className="flex items-center justify-between rounded-lg bg-slate-800/50 px-3 py-2">
              <div className="flex items-center gap-2">
                <Target className="h-4 w-4 text-blue-400" />
                <span className="text-xs text-slate-300">Pending Votes</span>
              </div>
              <span className="text-xs font-semibold text-white">3</span>
            </div>
            <div className="flex items-center justify-between rounded-lg bg-slate-800/50 px-3 py-2">
              <div className="flex items-center gap-2">
                <Globe className="h-4 w-4 text-violet-400" />
                <span className="text-xs text-slate-300">Online Members</span>
              </div>
              <span className="text-xs font-semibold text-white">61</span>
            </div>
          </div>
        </div>
      </ScrollArea>

      {/* Bottom Section */}
      <div className="border-t border-slate-800 p-2">
        {bottomNav.map((item) => {
          const Icon = item.icon;
          return (
            <Link key={item.name} to={item.href}>
              <Button
                variant="ghost"
                className="w-full justify-start gap-3 text-slate-300 hover:text-white hover:bg-slate-800/50"
              >
                <Icon className="h-5 w-5" />
                {item.name}
              </Button>
            </Link>
          );
        })}
        
        {/* AGIX Price */}
        <div className="mx-3 my-3 rounded-lg bg-gradient-to-r from-violet-600/20 to-indigo-600/20 p-3 border border-violet-600/30">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400">AGIX Price</span>
            <span className="text-sm font-bold text-white">$0.28</span>
          </div>
          <div className="mt-1 flex items-center gap-1">
            <div className="h-1.5 flex-1 rounded-full bg-slate-700">
              <div className="h-full w-3/4 rounded-full bg-gradient-to-r from-violet-600 to-indigo-600" />
            </div>
            <span className="text-xs text-green-400">+5.2%</span>
          </div>
        </div>

        {/* Sign Out - Only show when authenticated */}
        {user && (
          <Button
            onClick={logout}
            variant="ghost"
            className="w-full justify-start gap-3 text-slate-300 hover:text-red-400 hover:bg-red-500/10"
          >
            <LogOut className="h-5 w-5" />
            Sign Out
          </Button>
        )}
      </div>
    </div>
  );
};

export default Sidebar;
