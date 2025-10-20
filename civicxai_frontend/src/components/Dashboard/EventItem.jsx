import React from 'react';
import { Clock, AlertCircle, Calendar } from 'lucide-react';

const EventItem = ({ title, date, priority, description, daysAgo, type }) => {
  const priorityStyles = {
    high: 'border-red-500 bg-red-50 dark:bg-red-900/20',
    normal: 'border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800',
    low: 'border-blue-300 bg-blue-50 dark:bg-blue-900/20',
  };

  const iconMap = {
    deadline: <AlertCircle className="h-5 w-5 text-red-500" />,
    meeting: <Calendar className="h-5 w-5 text-blue-500" />,
    report: <Clock className="h-5 w-5 text-yellow-500" />,
  };

  return (
    <div className={`border-l-4 p-4 rounded-r-lg ${priorityStyles[priority || 'normal']}`}>
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0 mt-0.5">
            {iconMap[type] || <Clock className="h-5 w-5 text-gray-400" />}
          </div>
          <div className="flex-1">
            <h4 className="font-medium text-gray-900 dark:text-white">{title}</h4>
            {description && (
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{description}</p>
            )}
            {daysAgo && (
              <p className="text-xs text-gray-500 dark:text-gray-500 mt-2">{daysAgo}</p>
            )}
          </div>
        </div>
        <div className="flex-shrink-0">
          <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${
            priority === 'high' 
              ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' 
              : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
          }`}>
            {priority === 'high' ? 'high' : date}
          </span>
        </div>
      </div>
    </div>
  );
};

export default EventItem;
