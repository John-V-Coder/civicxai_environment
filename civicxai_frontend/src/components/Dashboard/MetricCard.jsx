import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

const MetricCard = ({ title, value, subtitle, change, icon, color = 'blue' }) => {
  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    yellow: 'bg-yellow-500',
    purple: 'bg-purple-500',
    red: 'bg-red-500',
  };

  const bgColorClasses = {
    blue: 'bg-blue-50 dark:bg-blue-900/20',
    green: 'bg-green-50 dark:bg-green-900/20',
    yellow: 'bg-yellow-50 dark:bg-yellow-900/20',
    purple: 'bg-purple-50 dark:bg-purple-900/20',
    red: 'bg-red-50 dark:bg-red-900/20',
  };

  const iconColorClasses = {
    blue: 'text-blue-600 dark:text-blue-400',
    green: 'text-green-600 dark:text-green-400',
    yellow: 'text-yellow-600 dark:text-yellow-400',
    purple: 'text-purple-600 dark:text-purple-400',
    red: 'text-red-600 dark:text-red-400',
  };

  const getTrendIcon = () => {
    if (change?.includes('+') && !change.includes('+0')) {
      return <TrendingUp className="h-4 w-4 text-green-500" />;
    } else if (change?.includes('-') && !change.includes('-0')) {
      return <TrendingDown className="h-4 w-4 text-red-500" />;
    }
    return <Minus className="h-4 w-4 text-gray-400" />;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300 p-6"
    >
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-lg ${bgColorClasses[color]}`}>
          <div className={iconColorClasses[color]}>{icon}</div>
        </div>
        {change && (
          <div className="flex items-center space-x-1">
            {getTrendIcon()}
          </div>
        )}
      </div>
      
      <div>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">{title}</p>
        <p className="text-3xl font-bold text-gray-900 dark:text-white">{value}</p>
        <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">{subtitle}</p>
        {change && (
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 flex items-center">
            <span className="mr-1">↗</span> {change}
          </p>
        )}
      </div>
    </motion.div>
  );
};

export default MetricCard;
