import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Users,
  Briefcase,
  TrendingUp,
  Calendar,
  ArrowRight,
  CheckCircle,
  Clock,
  AlertCircle,
  FileText,
  Activity,
  DollarSign,
  Target,
  Zap,
  Globe,
  BarChart,
  PieChart,
  ArrowUpRight,
  ArrowDownRight,
  MoreHorizontal
} from 'lucide-react';
import { dashboardAPI } from '@/services/api';
import useAuthStore from '@/store/authStore';

const DashboardNew = () => {
  const { user, isAuthenticated } = useAuthStore();
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Only load data if authenticated
    if (isAuthenticated) {
      loadDashboardData();
    }
  }, [isAuthenticated]);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const response = await dashboardAPI.getOverview();
      setMetrics(response.data);
    } catch (error) {
      console.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const fadeIn = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  const stagger = {
    visible: {
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  return (
    <div className="p-6 lg:p-8">
      {/* Welcome Section */}
      <motion.div
        initial="hidden"
        animate="visible"
        variants={fadeIn}
        className="mb-8"
      >
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">
              {user ? `Welcome back, ${user.username}!` : 'Welcome to CivicXAI'}
            </h1>
            <p className="text-slate-400">
              {user 
                ? "Here's what's happening in your governance platform today"
                : "Explore the governance platform and see what's happening"}
            </p>
          </div>
          
          <div className="flex items-center gap-3 mt-4 lg:mt-0">
            {user ? (
              <>
                <Badge className="bg-violet-600/20 text-violet-400 border-violet-600/30 px-3 py-1">
                  Core Contributor
                </Badge>
                <Badge className="bg-green-600/20 text-green-400 border-green-600/30 px-3 py-1">
                  <span className="mr-1.5 h-2 w-2 rounded-full bg-green-400 inline-block animate-pulse" />
                  Available
                </Badge>
              </>
            ) : (
              <>
                <Badge className="bg-slate-600/20 text-slate-400 border-slate-600/30 px-3 py-1">
                  Guest Mode
                </Badge>
                <Link to="/login">
                  <Button 
                    size="sm"
                    className="bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700 text-white"
                  >
                    Sign In to Contribute
                  </Button>
                </Link>
              </>
            )}
          </div>
        </div>
      </motion.div>

      {/* Key Metrics */}
      <motion.div
        initial="hidden"
        animate="visible"
        variants={stagger}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
      >
        <motion.div variants={fadeIn}>
          <Card className="border-slate-800 bg-gradient-to-br from-violet-950/50 to-slate-900 hover:shadow-violet-900/20 hover:shadow-xl transition-all duration-300">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-slate-400">
                Total Workgroups
              </CardTitle>
              <Briefcase className="h-5 w-5 text-violet-400" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-white">21</div>
              <p className="text-xs text-slate-400 mt-2 flex items-center">
                <TrendingUp className="h-3 w-3 mr-1 text-green-400" />
                <span className="text-green-400">+2.5%</span>
                <span className="ml-1">from last month</span>
              </p>
              <Progress value={75} className="mt-3 h-1.5 bg-slate-800" />
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={fadeIn}>
          <Card className="border-slate-800 bg-gradient-to-br from-indigo-950/50 to-slate-900 hover:shadow-indigo-900/20 hover:shadow-xl transition-all duration-300">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-slate-400">
                Active Members
              </CardTitle>
              <Users className="h-5 w-5 text-indigo-400" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-white">61</div>
              <p className="text-xs text-slate-400 mt-2 flex items-center">
                <TrendingUp className="h-3 w-3 mr-1 text-green-400" />
                <span className="text-green-400">+12%</span>
                <span className="ml-1">from last month</span>
              </p>
              <Progress value={61} className="mt-3 h-1.5 bg-slate-800" />
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={fadeIn}>
          <Card className="border-slate-800 bg-gradient-to-br from-emerald-950/50 to-slate-900 hover:shadow-emerald-900/20 hover:shadow-xl transition-all duration-300">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-slate-400">
                Total Proposals
              </CardTitle>
              <FileText className="h-5 w-5 text-emerald-400" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-white">45</div>
              <p className="text-xs text-slate-400 mt-2 flex items-center">
                <TrendingUp className="h-3 w-3 mr-1 text-green-400" />
                <span className="text-green-400">+8.2%</span>
                <span className="ml-1">from last month</span>
              </p>
              <Progress value={45} className="mt-3 h-1.5 bg-slate-800" />
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={fadeIn}>
          <Card className="border-slate-800 bg-gradient-to-br from-amber-950/50 to-slate-900 hover:shadow-amber-900/20 hover:shadow-xl transition-all duration-300">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-slate-400">
                Total Budget
              </CardTitle>
              <DollarSign className="h-5 w-5 text-amber-400" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-white">$2.4M</div>
              <p className="text-xs text-slate-400 mt-2 flex items-center">
                <ArrowDownRight className="h-3 w-3 mr-1 text-red-400" />
                <span className="text-red-400">-5.1%</span>
                <span className="ml-1">from last month</span>
              </p>
              <Progress value={85} className="mt-3 h-1.5 bg-slate-800" />
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - 2 cols */}
        <div className="lg:col-span-2 space-y-6">
          {/* Proposals Overview */}
          <Card className="border-slate-800 bg-slate-900/50">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-white">Proposals Overview</CardTitle>
                  <CardDescription className="text-slate-400">
                    Track and manage governance proposals
                  </CardDescription>
                </div>
                <Button variant="outline" size="sm" className="border-slate-700 text-slate-300 hover:bg-slate-800">
                  View All <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="active" className="w-full">
                <TabsList className="bg-slate-800 border-slate-700">
                  <TabsTrigger value="active" className="data-[state=active]:bg-violet-600">Active</TabsTrigger>
                  <TabsTrigger value="pending" className="data-[state=active]:bg-violet-600">Pending</TabsTrigger>
                  <TabsTrigger value="completed" className="data-[state=active]:bg-violet-600">Completed</TabsTrigger>
                </TabsList>
                
                <TabsContent value="active" className="mt-4 space-y-4">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="flex items-center justify-between p-4 rounded-lg bg-slate-800/50 hover:bg-slate-800 transition-colors">
                      <div className="flex items-start gap-4">
                        <div className="h-10 w-10 rounded-lg bg-violet-600/20 flex items-center justify-center">
                          <FileText className="h-5 w-5 text-violet-400" />
                        </div>
                        <div>
                          <h4 className="font-semibold text-white">Q3 2025 Budget Allocation</h4>
                          <p className="text-sm text-slate-400 mt-1">Infrastructure Development</p>
                          <div className="flex items-center gap-3 mt-2">
                            <Badge variant="outline" className="border-yellow-600/30 bg-yellow-600/10 text-yellow-400">
                              In Review
                            </Badge>
                            <span className="text-xs text-slate-500">Created 2 days ago</span>
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm text-slate-400 mb-1">Approval Rate</div>
                        <div className="text-2xl font-bold text-green-400">72%</div>
                        <Progress value={72} className="mt-2 h-1.5 w-20 bg-slate-700" />
                      </div>
                    </div>
                  ))}
                </TabsContent>
                
                <TabsContent value="pending" className="mt-4">
                  <div className="text-center py-8 text-slate-400">
                    No pending proposals at this time
                  </div>
                </TabsContent>
                
                <TabsContent value="completed" className="mt-4">
                  <div className="text-center py-8 text-slate-400">
                    View completed proposals
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>

          {/* Activity Timeline */}
          <Card className="border-slate-800 bg-slate-900/50">
            <CardHeader>
              <CardTitle className="text-white">Recent Activity</CardTitle>
              <CardDescription className="text-slate-400">
                Latest updates from your workgroups
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[300px] pr-4">
                <div className="space-y-4">
                  {[1, 2, 3, 4, 5].map((i) => (
                    <div key={i} className="flex gap-4">
                      <div className="relative">
                        <div className="h-10 w-10 rounded-full bg-violet-600/20 flex items-center justify-center">
                          {i % 2 === 0 ? (
                            <CheckCircle className="h-5 w-5 text-green-400" />
                          ) : (
                            <Clock className="h-5 w-5 text-yellow-400" />
                          )}
                        </div>
                        {i < 5 && (
                          <div className="absolute top-10 left-5 w-0.5 h-16 bg-slate-800" />
                        )}
                      </div>
                      <div className="flex-1 pt-1">
                        <p className="text-sm text-white font-medium">
                          {i % 2 === 0 ? 'Proposal approved' : 'New vote submitted'}
                        </p>
                        <p className="text-xs text-slate-400 mt-1">
                          {i % 2 === 0 
                            ? 'Infrastructure budget for Q3 has been approved'
                            : 'John Doe voted on Environmental Protection proposal'}
                        </p>
                        <p className="text-xs text-slate-500 mt-2">{i} hours ago</p>
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </div>

        {/* Right Column - 1 col */}
        <div className="space-y-6">
          {/* Calendar Events */}
          <Card className="border-slate-800 bg-slate-900/50">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-white">Upcoming Events</CardTitle>
                <Calendar className="h-5 w-5 text-slate-400" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="p-3 rounded-lg border border-red-500/30 bg-red-500/10">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm font-medium text-white">Q3 Reports Deadline</p>
                      <p className="text-xs text-slate-400 mt-1">Submit all quarterly reports</p>
                    </div>
                    <Badge variant="destructive" className="text-xs">High</Badge>
                  </div>
                  <div className="flex items-center gap-2 mt-2">
                    <Clock className="h-3 w-3 text-slate-400" />
                    <span className="text-xs text-slate-400">Sep 17, 2025</span>
                  </div>
                </div>

                <div className="p-3 rounded-lg border border-yellow-500/30 bg-yellow-500/10">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm font-medium text-white">Review Window Closes</p>
                      <p className="text-xs text-slate-400 mt-1">Final comments period</p>
                    </div>
                    <Badge className="bg-yellow-600/20 text-yellow-400 border-yellow-600/30 text-xs">Medium</Badge>
                  </div>
                  <div className="flex items-center gap-2 mt-2">
                    <Clock className="h-3 w-3 text-slate-400" />
                    <span className="text-xs text-slate-400">Sep 22, 2025</span>
                  </div>
                </div>

                <div className="p-3 rounded-lg border border-blue-500/30 bg-blue-500/10">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm font-medium text-white">Monthly Meeting</p>
                      <p className="text-xs text-slate-400 mt-1">All hands governance call</p>
                    </div>
                    <Badge className="bg-blue-600/20 text-blue-400 border-blue-600/30 text-xs">Low</Badge>
                  </div>
                  <div className="flex items-center gap-2 mt-2">
                    <Clock className="h-3 w-3 text-slate-400" />
                    <span className="text-xs text-slate-400">Sep 30, 2025</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Active Contributors */}
          <Card className="border-slate-800 bg-slate-900/50">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-white">Active Contributors</CardTitle>
                <Badge variant="outline" className="border-green-600/30 bg-green-600/10 text-green-400">
                  20 Online
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {['0xkenichi', 'ayomishu', 'cardano_wolf', 'dukepeter'].map((name, i) => (
                  <div key={name} className="flex items-center justify-between p-2 rounded-lg hover:bg-slate-800/50 transition-colors">
                    <div className="flex items-center gap-3">
                      <div className="relative">
                        <Avatar className="h-9 w-9 border border-slate-700">
                          <AvatarFallback className="bg-gradient-to-br from-violet-600 to-indigo-600 text-white text-xs">
                            {name[0].toUpperCase()}
                          </AvatarFallback>
                        </Avatar>
                        <div className="absolute -bottom-0.5 -right-0.5 h-3 w-3 rounded-full bg-green-500 border-2 border-slate-900" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-white">{name}</p>
                        <p className="text-xs text-slate-400">Level {10 - i}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="border-violet-600/30 bg-violet-600/10 text-violet-400 text-xs">
                        {i === 0 ? 'Lead' : 'Member'}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
              <Button variant="outline" className="w-full mt-4 border-slate-700 text-slate-300 hover:bg-slate-800">
                View All Members
              </Button>
            </CardContent>
          </Card>

          {/* Quick Stats / Sign In Prompt */}
          <Card className="border-slate-800 bg-gradient-to-br from-violet-950/30 to-slate-900">
            <CardHeader>
              <CardTitle className="text-white">
                {user ? 'Your Impact' : 'Join CivicXAI'}
              </CardTitle>
              <CardDescription className="text-slate-400">
                {user ? 'Personal contribution metrics' : 'Sign in to track your contributions'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {user ? (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-slate-400">Proposals Created</span>
                    <span className="text-lg font-bold text-white">12</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-slate-400">Votes Cast</span>
                    <span className="text-lg font-bold text-white">45</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-slate-400">Contribution Score</span>
                    <span className="text-lg font-bold text-violet-400">892</span>
                  </div>
                  <div className="pt-2 border-t border-slate-800">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs text-slate-400">Level Progress</span>
                      <span className="text-xs text-violet-400">Level 8</span>
                    </div>
                    <Progress value={65} className="h-2 bg-slate-800" />
                    <p className="text-xs text-slate-500 mt-2">350 points to Level 9</p>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <p className="text-sm text-slate-300">
                    Create an account to:
                  </p>
                  <ul className="space-y-2 text-sm text-slate-400">
                    <li className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-400" />
                      Create and vote on proposals
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-400" />
                      Join workgroups
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-400" />
                      Track your contributions
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-400" />
                      Earn reputation points
                    </li>
                  </ul>
                  <Link to="/register" className="block">
                    <Button className="w-full bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700 text-white">
                      Create Account
                    </Button>
                  </Link>
                  <Link to="/login" className="block">
                    <Button variant="outline" className="w-full border-slate-700 text-slate-300 hover:bg-slate-800">
                      Sign In
                    </Button>
                  </Link>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default DashboardNew;
