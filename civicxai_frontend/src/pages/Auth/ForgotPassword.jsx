import React, { useState } from 'react';
import { Link } from 'react-router-dom';
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
  Mail,
  ArrowLeft,
  Zap,
  CheckCircle,
  Info
} from 'lucide-react';
import useAuthStore from '@/store/authStore';

const forgotPasswordSchema = z.object({
  email: z.string().email('Invalid email address'),
});

const ForgotPassword = () => {
  const { requestPasswordReset } = useAuthStore();
  const [isLoading, setIsLoading] = useState(false);
  const [emailSent, setEmailSent] = useState(false);
  const [resetLink, setResetLink] = useState(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: {
      email: '',
    },
  });

  const onSubmit = async (data) => {
    setIsLoading(true);
    const result = await requestPasswordReset(data.email);
    setIsLoading(false);

    if (result.success) {
      setEmailSent(true);
      // For development - show the reset link
      if (result.data?.reset_link) {
        setResetLink(result.data.reset_link);
      }
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
              {emailSent ? 'Check your email' : 'Enter your email to receive a reset link'}
            </p>
          </motion.div>
        </div>

        {/* Forgot Password Card */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <Card className="border-slate-800 bg-slate-900/50 backdrop-blur-sm shadow-2xl">
            <CardHeader>
              <CardTitle className="text-2xl text-white">Forgot Password</CardTitle>
              <CardDescription className="text-slate-400">
                {emailSent 
                  ? "We've sent you a password reset link" 
                  : "Enter your email and we'll send you a reset link"}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {!emailSent ? (
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                  {/* Email Field */}
                  <div className="space-y-2">
                    <Label htmlFor="email" className="text-slate-300">Email Address</Label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                      <Input
                        id="email"
                        type="email"
                        placeholder="Enter your email address"
                        className="pl-10 bg-slate-800 border-slate-700 text-white placeholder:text-slate-500 focus:border-violet-600 focus:ring-violet-600/20"
                        {...register('email')}
                      />
                    </div>
                    {errors.email && (
                      <p className="text-xs text-red-400">{errors.email.message}</p>
                    )}
                  </div>

                  {/* Info Alert */}
                  <Alert className="border-slate-700 bg-slate-800/50">
                    <Info className="h-4 w-4 text-violet-400" />
                    <AlertDescription className="text-slate-300 text-sm">
                      You'll receive an email with instructions to reset your password. The link will expire in 24 hours.
                    </AlertDescription>
                  </Alert>

                  {/* Submit Button */}
                  <Button
                    type="submit"
                    disabled={isLoading}
                    className="w-full bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700 text-white shadow-lg shadow-violet-600/20"
                  >
                    {isLoading ? (
                      <div className="flex items-center gap-2">
                        <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                        Sending...
                      </div>
                    ) : (
                      <div className="flex items-center gap-2">
                        <Mail className="h-4 w-4" />
                        Send Reset Link
                      </div>
                    )}
                  </Button>
                </form>
              ) : (
                <div className="space-y-4">
                  {/* Success Message */}
                  <Alert className="border-green-700 bg-green-900/20">
                    <CheckCircle className="h-4 w-4 text-green-400" />
                    <AlertDescription className="text-slate-300">
                      <p className="font-medium mb-1">Email sent successfully!</p>
                      <p className="text-sm">
                        Check your inbox for password reset instructions. If you don't see it, check your spam folder.
                      </p>
                    </AlertDescription>
                  </Alert>

                  {/* Development only - show reset link */}
                  {resetLink && (
                    <Alert className="border-violet-700 bg-violet-900/20">
                      <Info className="h-4 w-4 text-violet-400" />
                      <AlertDescription className="text-slate-300">
                        <p className="font-medium mb-2 text-sm">Development Mode - Reset Link:</p>
                        <a
                          href={resetLink}
                          className="text-xs text-violet-400 hover:text-violet-300 break-all underline"
                        >
                          {resetLink}
                        </a>
                      </AlertDescription>
                    </Alert>
                  )}

                  {/* Return to Login */}
                  <Button
                    asChild
                    variant="outline"
                    className="w-full border-slate-700 bg-slate-800/50 text-slate-300 hover:bg-slate-800 hover:text-white"
                  >
                    <Link to="/login">
                      <ArrowLeft className="h-4 w-4 mr-2" />
                      Back to Login
                    </Link>
                  </Button>
                </div>
              )}
            </CardContent>
            <CardFooter className="flex flex-col space-y-2">
              {!emailSent && (
                <Link
                  to="/login"
                  className="text-center text-sm text-slate-400 hover:text-violet-400 transition-colors flex items-center gap-1 mx-auto"
                >
                  <ArrowLeft className="h-3 w-3" />
                  Back to Login
                </Link>
              )}
              <p className="text-center text-xs text-slate-500 w-full">
                Don't have an account?{' '}
                <Link to="/register" className="text-violet-400 hover:text-violet-300">
                  Create account
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

export default ForgotPassword;
