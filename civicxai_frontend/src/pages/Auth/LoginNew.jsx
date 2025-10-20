import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Checkbox } from '@/components/ui/checkbox';
import { Separator } from '@/components/ui/separator';
import {
  Mail,
  Lock,
  Eye,
  EyeOff,
  LogIn,
  Zap,
  ArrowRight,
  Github,
  Twitter,
  AlertCircle,
  Sparkles
} from 'lucide-react';
import useAuthStore from '@/store/authStore';
import { useToast } from '@/components/ui/use-toast';

const loginSchema = z.object({
  username: z.string().min(1, 'Username is required'),
  password: z.string().min(1, 'Password is required'),
  remember: z.boolean().optional(),
});

const LoginNew = () => {
  const navigate = useNavigate();
  const { login } = useAuthStore();
  const { toast } = useToast();
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
  } = useForm({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      username: '',
      password: '',
      remember: false,
    },
  });

  const onSubmit = async (data) => {
    setIsLoading(true);
    const result = await login({
      username: data.username,
      password: data.password,
    });
    setIsLoading(false);

    if (result.success) {
      toast({
        title: "Welcome back!",
        description: "You've successfully logged in.",
      });
      navigate('/dashboard');
    } else {
      toast({
        variant: "destructive",
        title: "Login failed",
        description: result.error || "Invalid credentials",
      });
    }
  };

  const handleQuickLogin = (username, password) => {
    setValue('username', username);
    setValue('password', password);
    toast({
      title: "Credentials filled",
      description: "Click 'Sign In' to continue",
    });
  };

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4 overflow-hidden relative">
      {/* Animated Background */}
      <div className="absolute inset-0">
        <div className="absolute inset-0 bg-gradient-to-br from-violet-950/20 via-slate-950 to-indigo-950/20" />
        <div className="absolute top-0 left-0 w-96 h-96 bg-violet-600/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl animate-pulse delay-1000" />
      </div>

      {/* Grid Pattern */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImdyaWQiIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHBhdGggZD0iTSAxMCAwIEwgMCAwIDAgMTAiIGZpbGw9Im5vbmUiIHN0cm9rZT0iIzFhMWEyZSIgc3Ryb2tlLXdpZHRoPSIxIi8+PC9wYXR0ZXJuPjwvZGVmcz48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSJ1cmwoI2dyaWQpIi8+PC9zdmc+')] opacity-20" />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative z-10 w-full max-w-lg"
      >
        {/* Logo and Title */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="flex justify-center mb-4"
          >
            <div className="h-20 w-20 bg-gradient-to-br from-violet-600 to-indigo-600 rounded-2xl flex items-center justify-center shadow-2xl shadow-violet-600/20">
              <Zap className="h-10 w-10 text-white" />
            </div>
          </motion.div>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <h1 className="text-4xl font-bold text-white mb-2">Welcome to CivicXAI</h1>
            <p className="text-slate-400">Enter your credentials to access the platform</p>
          </motion.div>
        </div>

        {/* Login Card */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <Card className="border-slate-800 bg-slate-900/50 backdrop-blur-sm shadow-2xl">
            <CardHeader>
              <CardTitle className="text-2xl text-white">Sign In</CardTitle>
              <CardDescription className="text-slate-400">
                Enter your account details to continue
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                {/* Username Field */}
                <div className="space-y-2">
                  <Label htmlFor="username" className="text-slate-300">Username</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                    <Input
                      id="username"
                      type="text"
                      placeholder="Enter your username"
                      className="pl-10 bg-slate-800 border-slate-700 text-white placeholder:text-slate-500 focus:border-violet-600 focus:ring-violet-600/20"
                      {...register('username')}
                    />
                  </div>
                  {errors.username && (
                    <p className="text-xs text-red-400">{errors.username.message}</p>
                  )}
                </div>

                {/* Password Field */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="password" className="text-slate-300">Password</Label>
                    <Link
                      to="/forgot-password"
                      className="text-xs text-violet-400 hover:text-violet-300 transition-colors"
                    >
                      Forgot password?
                    </Link>
                  </div>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                    <Input
                      id="password"
                      type={showPassword ? 'text' : 'password'}
                      placeholder="Enter your password"
                      className="pl-10 pr-10 bg-slate-800 border-slate-700 text-white placeholder:text-slate-500 focus:border-violet-600 focus:ring-violet-600/20"
                      {...register('password')}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white transition-colors"
                    >
                      {showPassword ? (
                        <EyeOff className="h-4 w-4" />
                      ) : (
                        <Eye className="h-4 w-4" />
                      )}
                    </button>
                  </div>
                  {errors.password && (
                    <p className="text-xs text-red-400">{errors.password.message}</p>
                  )}
                </div>

                {/* Remember Me */}
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="remember"
                    className="border-slate-600 data-[state=checked]:bg-violet-600 data-[state=checked]:border-violet-600"
                    {...register('remember')}
                  />
                  <Label
                    htmlFor="remember"
                    className="text-sm text-slate-300 cursor-pointer"
                  >
                    Remember me for 30 days
                  </Label>
                </div>

                {/* Submit Button */}
                <Button
                  type="submit"
                  disabled={isLoading}
                  className="w-full bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700 text-white shadow-lg shadow-violet-600/20"
                >
                  {isLoading ? (
                    <div className="flex items-center gap-2">
                      <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                      Signing in...
                    </div>
                  ) : (
                    <div className="flex items-center gap-2">
                      <LogIn className="h-4 w-4" />
                      Sign In
                    </div>
                  )}
                </Button>
              </form>

              {/* Quick Login Options */}
              <div className="mt-6">
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <Separator className="w-full bg-slate-800" />
                  </div>
                  <div className="relative flex justify-center text-xs">
                    <span className="bg-slate-900 px-2 text-slate-400">Quick login for testing</span>
                  </div>
                </div>

                <div className="mt-4 grid grid-cols-2 gap-3">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => handleQuickLogin('admin', 'admin123')}
                    className="border-slate-700 bg-slate-800/50 text-slate-300 hover:bg-slate-800 hover:text-white"
                  >
                    <Sparkles className="mr-2 h-4 w-4 text-violet-400" />
                    Admin
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => handleQuickLogin('0xkenichi', 'password123')}
                    className="border-slate-700 bg-slate-800/50 text-slate-300 hover:bg-slate-800 hover:text-white"
                  >
                    <Sparkles className="mr-2 h-4 w-4 text-indigo-400" />
                    Contributor
                  </Button>
                </div>
              </div>

              {/* Social Login */}
              <div className="mt-6">
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <Separator className="w-full bg-slate-800" />
                  </div>
                  <div className="relative flex justify-center text-xs">
                    <span className="bg-slate-900 px-2 text-slate-400">Or continue with</span>
                  </div>
                </div>

                <div className="mt-4 grid grid-cols-2 gap-3">
                  <Button
                    type="button"
                    variant="outline"
                    className="border-slate-700 bg-slate-800/50 text-slate-300 hover:bg-slate-800 hover:text-white"
                  >
                    <Github className="mr-2 h-4 w-4" />
                    Github
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    className="border-slate-700 bg-slate-800/50 text-slate-300 hover:bg-slate-800 hover:text-white"
                  >
                    <Twitter className="mr-2 h-4 w-4" />
                    Twitter
                  </Button>
                </div>
              </div>
            </CardContent>
            <CardFooter>
              <p className="text-center text-sm text-slate-400 w-full">
                Don't have an account?{' '}
                <Link to="/register" className="font-medium text-violet-400 hover:text-violet-300 transition-colors">
                  Create account <ArrowRight className="inline-block h-3 w-3" />
                </Link>
              </p>
            </CardFooter>
          </Card>
        </motion.div>

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          className="mt-8 text-center"
        >
          <p className="text-sm text-slate-500">
            &copy; 2025 CivicXAI. All rights reserved. | Powered by AI Governance
          </p>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default LoginNew;
