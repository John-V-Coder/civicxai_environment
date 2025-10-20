import React from 'react';
import { motion } from 'framer-motion';

const ProposalCard = ({ title, status, type, date }) => {
  const statusColors = {
    'In Review': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
    'Approved': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
    'Rejected': 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
    'Expired': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.02 }}
      className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors cursor-pointer"
    >
      <div className="flex items-start justify-between mb-2">
        <span className={`inline-flex items-center px-2 py-1 rounded-md text-xs font-medium ${statusColors[status] || statusColors['In Review']}`}>
          {status}
        </span>
        <span className={`inline-flex items-center px-2 py-1 rounded-md text-xs font-medium ${statusColors[status] || statusColors['In Review']}`}>
          {status}
        </span>
      </div>
      <h3 className="font-medium text-gray-900 dark:text-white mb-1">{title}</h3>
      <p className="text-sm text-gray-600 dark:text-gray-400">{type}</p>
      <p className="text-xs text-gray-500 dark:text-gray-500 mt-2">{date}</p>
    </motion.div>
  );
};

export default ProposalCard;
