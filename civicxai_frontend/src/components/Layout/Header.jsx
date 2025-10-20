import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import {
  Menu,
  Search,
  Bell,
  Sun,
  Moon,
  User,
  Settings,
  LogIn,
  LogOut,
  HelpCircle,
  MessageSquare,
  ChevronDown
} from 'lucide-react';
import useAuthStore from '@/store/authStore';

const Header = ({ onMenuClick }) => {
  const { user, logout } = useAuthStore();
  const [darkMode, setDarkMode] = React.useState(true);

  return (
    <header className="flex h-16 items-center justify-between border-b border-slate-800 bg-slate-950/50 backdrop-blur-sm px-4 lg:px-6">
      {/* Left Section */}
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="icon"
          className="lg:hidden"
          onClick={onMenuClick}
        >
          <Menu className="h-5 w-5 text-slate-400" />
        </Button>

        {/* Search */}
        <div className="relative hidden md:block">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <Input
            type="text"
            placeholder="Search anything..."
            className="w-80 bg-slate-900 border-slate-800 pl-10 text-slate-100 placeholder:text-slate-500 focus:border-violet-600 focus:ring-violet-600/20"
          />
        </div>
      </div>

      {/* Right Section */}
      <div className="flex items-center gap-3">
        {/* Quick Actions */}
        <Button
          variant="ghost"
          size="icon"
          className="relative text-slate-400 hover:text-white"
        >
          <MessageSquare className="h-5 w-5" />
        </Button>

        {/* Notifications */}
        <Button
          variant="ghost"
          size="icon"
          className="relative text-slate-400 hover:text-white"
        >
          <Bell className="h-5 w-5" />
          <span className="absolute -top-1 -right-1 h-3 w-3 rounded-full bg-red-500 border-2 border-slate-950 animate-pulse" />
        </Button>

        {/* Theme Toggle */}
        <div className="flex items-center gap-2 px-3">
          <Sun className="h-4 w-4 text-slate-400" />
          <Switch
            checked={darkMode}
            onCheckedChange={setDarkMode}
            className="data-[state=checked]:bg-violet-600"
          />
          <Moon className="h-4 w-4 text-slate-400" />
        </div>

        {/* User Menu / Sign In Button */}
        {user ? (
          <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              className="flex items-center gap-2 px-2 hover:bg-slate-800"
            >
              <Avatar className="h-8 w-8 border-2 border-violet-600/20">
                <AvatarImage src={user?.profile_image} />
                <AvatarFallback className="bg-gradient-to-br from-violet-600 to-indigo-600 text-white text-sm">
                  {user?.username?.[0]?.toUpperCase() || 'U'}
                </AvatarFallback>
              </Avatar>
              <div className="hidden lg:block text-left">
                <p className="text-sm font-medium text-white">{user?.username || 'User'}</p>
                <p className="text-xs text-slate-400">{user?.email || 'user@example.com'}</p>
              </div>
              <ChevronDown className="h-4 w-4 text-slate-400 hidden lg:block" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56 bg-slate-900 border-slate-800">
            <DropdownMenuLabel className="text-slate-300">
              <div className="flex items-center gap-3 py-2">
                <Avatar className="h-10 w-10">
                  <AvatarImage src={user?.profile_image} />
                  <AvatarFallback className="bg-gradient-to-br from-violet-600 to-indigo-600 text-white">
                    {user?.username?.[0]?.toUpperCase() || 'U'}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <p className="font-semibold text-white">{user?.username}</p>
                  <p className="text-xs text-slate-400">{user?.email}</p>
                  <Badge variant="outline" className="mt-1 border-violet-600/30 bg-violet-600/10 text-violet-400 text-xs">
                    {user?.role || 'Contributor'}
                  </Badge>
                </div>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator className="bg-slate-800" />
            
            <DropdownMenuItem className="text-slate-300 focus:bg-slate-800 focus:text-white">
              <User className="mr-2 h-4 w-4" />
              Your Profile
            </DropdownMenuItem>
            <DropdownMenuItem className="text-slate-300 focus:bg-slate-800 focus:text-white">
              <Settings className="mr-2 h-4 w-4" />
              Settings
            </DropdownMenuItem>
            <DropdownMenuItem className="text-slate-300 focus:bg-slate-800 focus:text-white">
              <HelpCircle className="mr-2 h-4 w-4" />
              Help & Support
            </DropdownMenuItem>
            
            <DropdownMenuSeparator className="bg-slate-800" />
            
            <DropdownMenuItem 
              onClick={logout}
              className="text-red-400 focus:bg-red-500/10 focus:text-red-400"
            >
              <LogOut className="mr-2 h-4 w-4" />
              Sign Out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
        ) : (
          <Link to="/login">
            <Button 
              className="bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700 text-white shadow-lg shadow-violet-600/20"
            >
              <LogIn className="h-4 w-4 mr-2" />
              Sign In
            </Button>
          </Link>
        )}
      </div>
    </header>
  );
};

export default Header;
