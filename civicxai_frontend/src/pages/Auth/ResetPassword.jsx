import React, { useState, useEffect } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Lock,
  Eye,
  EyeOff,
  ArrowLeft,
  Zap,
  CheckCircle,
  AlertCircle,
  Loader2
} from 'lucide-react';
import useAuthStore from '@/store/authStore';

const resetPasswordSchema = z.object({
  password: z.string().min(8, 'Password must be at least 8 characters'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
});

const ResetPassword = () => {
  const { uid, token } = useParams();
  const navigate = useNavigate();
  const { verifyResetToken, resetPassword } = useAuthStore();
  
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isVerifying, setIsVerifying] = useState(true);
  const [isValidToken, setIsValidToken] = useState(false);
  const [userEmail, setUserEmail] = useState('');
  const [resetSuccess, setResetSuccess] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(resetPasswordSchema),
    defaultValues: {
      password: '',
      confirmPassword: '',
    },
  });

  // Verify token on component mount
  useEffect(() => {
    const verifyToken = async () => {
      if (!uid || !token) {
        setIsVerifying(false);
        setIsValidToken(false);
        return;
      }

      const result = await verifyResetToken(uid, token);
      setIsVerifying(false);
      
      if (result.success) {
        setIsValidToken(true);
        setUserEmail(result.data?.email || '');
      } else {
        setIsValidToken(false);
      }
    };

    verifyToken();
  }, [uid, token, verifyResetToken]);

  const onSubmit = async (data) => {
    setIsLoading(true);
    const result = await resetPassword(uid, token, data.password);
    setIsLoading(false);

    if (result.success) {
      setResetSuccess(true);
      // Redirect to login after 3 seconds
      setTimeout(() => {
        navigate('/login');
      }, 3000);
    }
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
            <h1 className="text-4xl font-bold text-white mb-2">Reset Password</h1>
            <p className="text-slate-400">
              {isVerifying 
                ? 'Verifying your reset link...' 
                : resetSuccess
                ? 'Password reset successful!'
                : isValidToken
                ? 'Create your new password'
                : 'Invalid or expired reset link'}
            </p>
          </motion.div>
        </div>

        {/* Reset Password Card */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <Card className="border-slate-800 bg-slate-900/50 backdrop-blur-sm shadow-2xl">
            <CardHeader>
              <CardTitle className="text-2xl text-white">
                {isVerifying ? 'Verifying...' : resetSuccess ? 'Success!' : isValidToken ? 'New Password' : 'Invalid Link'}
              </CardTitle>
              <CardDescription className="text-slate-400">
                {isVerifying 
                  ? 'Please wait while we verify your reset link' 
                  : resetSuccess
                  ? 'Your password has been updated'
                  : isValidToken && userEmail
                  ? `Resetting password for ${userEmail}`
                  : isValidToken
                  ? 'Enter your new password below'
                  : 'This reset link is invalid or has expired'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {isVerifying ? (
                // Verifying state
                <div className="flex flex-col items-center justify-center py-8 space-y-4">
                  <Loader2 className="h-12 w-12 text-violet-500 animate-spin" />
                  <p className="text-slate-400 text-sm">Verifying reset token...</p>
                </div>
              ) : resetSuccess ? (
                // Success state
                <div className="space-y-4">
                  <Alert className="border-green-700 bg-green-900/20">
                    <CheckCircle className="h-4 w-4 text-green-400" />
                    <AlertDescription className="text-slate-300">
                      <p className="font-medium mb-1">Password reset successful!</p>
                      <p className="text-sm">
                        You can now log in with your new password. Redirecting to login page...
                      </p>
                    </AlertDescription>
                  </Alert>
                  
                  <Button
                    asChild
                    className="w-full bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700 text-white shadow-lg shadow-violet-600/20"
                  >
                    <Link to="/login">
                      Go to Login
                    </Link>
                  </Button>
                </div>
              ) : isValidToken ? (
                // Valid token - show password form
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                  {/* New Password */}
                  <div className="space-y-2">
                    <Label htmlFor="password" className="text-slate-300">New Password</Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                      <Input
                        id="password"
                        type={showPassword ? 'text' : 'password'}
                        placeholder="Min. 8 characters"
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

                  {/* Confirm Password */}
                  <div className="space-y-2">
                    <Label htmlFor="confirmPassword" className="text-slate-300">Confirm New Password</Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                      <Input
                        id="confirmPassword"
                        type={showConfirmPassword ? 'text' : 'password'}
                        placeholder="Confirm your password"
                        className="pl-10 pr-10 bg-slate-800 border-slate-700 text-white placeholder:text-slate-500 focus:border-violet-600 focus:ring-violet-600/20"
                        {...register('confirmPassword')}
                      />
                      <button
                        type="button"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white transition-colors"
                      >
                        {showConfirmPassword ? (
                          <EyeOff className="h-4 w-4" />
                        ) : (
                          <Eye className="h-4 w-4" />
                        )}
                      </button>
                    </div>
                    {errors.confirmPassword && (
                      <p className="text-xs text-red-400">{errors.confirmPassword.message}</p>
                    )}
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
                        Resetting Password...
                      </div>
                    ) : (
                      <div className="flex items-center gap-2">
                        <CheckCircle className="h-4 w-4" />
                        Reset Password
                      </div>
                    )}
                  </Button>
                </form>
              ) : (
                // Invalid token
                <div className="space-y-4">
                  <Alert className="border-red-700 bg-red-900/20">
                    <AlertCircle className="h-4 w-4 text-red-400" />
                    <AlertDescription className="text-slate-300">
                      <p className="font-medium mb-1">Invalid or expired reset link</p>
                      <p className="text-sm">
                        This password reset link is no longer valid. Please request a new one.
                      </p>
                    </AlertDescription>
                  </Alert>
                  
                  <Button
                    asChild
                    className="w-full bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700 text-white shadow-lg shadow-violet-600/20"
                  >
                    <Link to="/forgot-password">
                      Request New Reset Link
                    </Link>
                  </Button>
                </div>
              )}
            </CardContent>
            <CardFooter>
              <Link
                to="/login"
                className="text-center text-sm text-slate-400 hover:text-violet-400 transition-colors flex items-center gap-1 mx-auto"
              >
                <ArrowLeft className="h-3 w-3" />
                Back to Login
              </Link>
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

export default ResetPassword;
