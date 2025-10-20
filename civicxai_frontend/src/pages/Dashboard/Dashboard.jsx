import React, { useState, useEffect } from 'react';
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
  Activity
} from 'lucide-react';
import { motion } from 'framer-motion';
import { dashboardAPI } from '../../services/api';
import useAuthStore from '../../store/authStore';
import MetricCard from '../../components/Dashboard/MetricCard';
import ProposalCard from '../../components/Dashboard/ProposalCard';
import EventItem from '../../components/Dashboard/EventItem';
import ContributorCard from '../../components/Dashboard/ContributorCard';
import toast from 'react-hot-toast';

const Dashboard = () => {
  const { user } = useAuthStore();
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const response = await dashboardAPI.getOverview();
      setMetrics(response.data);
    } catch (error) {
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Welcome Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Welcome back, {user?.username || 'User'}!
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Ready to participate in governance decisions
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">
            Core Contributor
          </span>
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
            Available
          </span>
        </div>
      </div>

      {/* Dashboard Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Workgroups"
          value={metrics?.metrics?.total_workgroups || 21}
          subtitle="All workgroups and guilds"
          change="+0 from last month"
          icon={<Briefcase className="h-6 w-6" />}
          color="blue"
        />
        
        <MetricCard
          title="Active Workgroups"
          value={metrics?.metrics?.active_workgroups || 21}
          subtitle="Currently active workgroups"
          change="+0 from last month"
          icon={<Activity className="h-6 w-6" />}
          color="green"
        />
        
        <MetricCard
          title="Inactive Workgroups"
          value={metrics?.metrics?.inactive_workgroups || 0}
          subtitle="Currently inactive workgroups"
          change="+0 from last month"
          icon={<AlertCircle className="h-6 w-6" />}
          color="yellow"
        />
        
        <MetricCard
          title="Total Members"
          value={metrics?.metrics?.total_members || 4}
          subtitle="Community members across all groups"
          change="+0 from last month"
          icon={<Users className="h-6 w-6" />}
          color="purple"
        />
      </div>

      {/* Quick Actions & Ambassador Links */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Quick Actions */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Quick Actions
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            Quick access to frequently used tasks
          </p>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer transition-colors">
              <div className="flex items-center">
                <FileText className="h-5 w-5 text-gray-600 dark:text-gray-400 mr-3" />
                <div>
                  <h3 className="font-medium text-gray-900 dark:text-white">Current Proposals</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Browse ongoing proposals</p>
                </div>
              </div>
              <button className="text-purple-600 dark:text-purple-400 hover:text-purple-700">
                Go to →
              </button>
            </div>
            
            <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer transition-colors">
              <div className="flex items-center">
                <FileText className="h-5 w-5 text-gray-600 dark:text-gray-400 mr-3" />
                <div>
                  <h3 className="font-medium text-gray-900 dark:text-white">Quarterly Reports</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Review quarterly report proposals</p>
                </div>
              </div>
              <button className="text-purple-600 dark:text-purple-400 hover:text-purple-700">
                Go to →
              </button>
            </div>
            
            <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer transition-colors">
              <div className="flex items-center">
                <Users className="h-5 w-5 text-gray-600 dark:text-gray-400 mr-3" />
                <div>
                  <h3 className="font-medium text-gray-900 dark:text-white">Update your profile</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Edit your profile information</p>
                </div>
              </div>
              <button className="text-purple-600 dark:text-purple-400 hover:text-purple-700">
                Go to →
              </button>
            </div>
            
            <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer transition-colors">
              <div className="flex items-center">
                <Activity className="h-5 w-5 text-gray-600 dark:text-gray-400 mr-3" />
                <div>
                  <h3 className="font-medium text-gray-900 dark:text-white">Analytics</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Governance analytics dashboard</p>
                </div>
              </div>
              <button className="text-purple-600 dark:text-purple-400 hover:text-purple-700">
                Go to →
              </button>
            </div>
          </div>
        </div>

        {/* Ambassador Program Links */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Ambassador Program Links
          </h2>
          
          <div className="space-y-3">
            <a href="#" className="block p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg hover:bg-purple-100 dark:hover:bg-purple-900/30 transition-colors">
              <h3 className="font-medium text-purple-900 dark:text-purple-200">Knowledge Base</h3>
            </a>
            
            <a href="#" className="block p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg hover:bg-purple-100 dark:hover:bg-purple-900/30 transition-colors">
              <h3 className="font-medium text-purple-900 dark:text-purple-200">Summary Tool</h3>
            </a>
          </div>
        </div>
      </div>

      {/* Calendar */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          📅 Calendar
        </h2>
        
        <div className="space-y-4">
          <h3 className="font-medium text-gray-900 dark:text-white">Upcoming Events</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">Important dates and deadlines</p>
          
          <div className="space-y-3">
            {metrics?.recent_events?.map((event, idx) => (
              <EventItem
                key={idx}
                title={event.title}
                date={event.date}
                priority={event.high_priority ? 'high' : 'normal'}
                type={event.type}
              />
            )) || (
              <>
                <EventItem
                  title="Q3 Reports & Q4 Budgets Deadline"
                  date="Sep 17"
                  priority="high"
                  description="Deadline for WGs to submit Q3 quarterly reports and Q4 budgets."
                  daysAgo="30 days ago"
                />
                <EventItem
                  title="Review & Comment Window Closes"
                  date="Sep 22"
                  priority="high"
                  description="Until this time, Core Contributors can read/comment in the Gov Dashboard. WGs may update budgets in response to comments."
                  daysAgo="25 days ago"
                />
                <EventItem
                  title="Editing Locked: Consent Opens"
                  date="Sep 22"
                  priority="high"
                  description="Editing of budgets and reports is locked at 23:59 UTC; consent process opens immediately after."
                  daysAgo="25 days ago"
                />
                <EventItem
                  title="Consent Deadline"
                  date="Sep 24"
                  priority="high"
                  description="Deadline for Core Contributors to consent, object, or abstain to the versions in the Dashboard."
                  daysAgo="23 days ago"
                />
              </>
            )}
          </div>
        </div>
      </div>

      {/* Proposals Section */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Proposals
          </h2>
          <div className="flex items-center space-x-4 text-sm">
            <span className="text-gray-600 dark:text-gray-400">Total 21</span>
            <span className="text-gray-600 dark:text-gray-400">In Review 21</span>
            <span className="text-gray-600 dark:text-gray-400">Approved 0</span>
            <span className="text-gray-600 dark:text-gray-400">Rejected 0</span>
          </div>
        </div>
        
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
          Manage and track community proposals
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {metrics?.recent_proposals?.map((proposal, idx) => (
            <ProposalCard
              key={idx}
              title={proposal.title}
              status={proposal.status}
              type={proposal.type}
              date={proposal.date}
            />
          )) || (
            <>
              <ProposalCard
                title="Quarterly Report"
                status="In Review"
                type="Q3 2025"
                date="Q3 2025"
              />
              <ProposalCard
                title="Quarterly Report"
                status="In Review"
                type="Q4 2025"
                date="Q4 2025"
              />
              <ProposalCard
                title="Quarterly Report"
                status="In Review"
                type="Q3 2025"
                date="Q3 2025"
              />
              <ProposalCard
                title="Quarterly Report"
                status="In Review"
                type="Q3 2025"
                date="Q3 2025"
              />
            </>
          )}
        </div>
      </div>

      {/* Contributors */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            👥 Contributors
          </h2>
          <span className="text-sm text-gray-600 dark:text-gray-400">
            20 online • 61 total
          </span>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {metrics?.active_contributors?.map((contributor, idx) => (
            <ContributorCard
              key={idx}
              name={contributor.username}
              avatar={contributor.profile_image}
              role={contributor.role}
              online={contributor.online}
            />
          )) || (
            <>
              <ContributorCard
                name="0xkenichi"
                role="Online"
                online={true}
                workgroups={["Marketing Guild", "R&D Guild", "Writers WG"]}
              />
              <ContributorCard
                name="ayomishu..."
                role="Online"
                online={true}
                workgroups={[]}
              />
              <ContributorCard
                name="cardano_..."
                role="Online"
                online={true}
                workgroups={["R&D Guild"]}
              />
              <ContributorCard
                name="dukepeter_"
                role="Online"
                online={true}
                workgroups={["Translators WG", "Video WG"]}
              />
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
