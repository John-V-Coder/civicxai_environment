import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, Circle } from 'lucide-react';

const ContributorCard = ({ name, avatar, role, online, workgroups = [] }) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.05 }}
      className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 hover:bg-gray-100 dark:hover:bg-gray-600 transition-all cursor-pointer"
    >
      <div className="flex flex-col items-center text-center">
        {/* Avatar */}
        <div className="relative mb-3">
          {avatar ? (
            <img
              src={avatar}
              alt={name}
              className="h-16 w-16 rounded-full object-cover"
            />
          ) : (
            <div className="h-16 w-16 rounded-full bg-gradient-to-br from-purple-400 to-pink-600 flex items-center justify-center text-white font-bold text-xl">
              {name?.[0]?.toUpperCase() || 'U'}
            </div>
          )}
          {/* Online indicator */}
          <div className="absolute bottom-0 right-0">
            {online ? (
              <CheckCircle className="h-5 w-5 text-green-500 bg-white dark:bg-gray-800 rounded-full" />
            ) : (
              <Circle className="h-5 w-5 text-gray-400 bg-white dark:bg-gray-800 rounded-full" />
            )}
          </div>
        </div>

        {/* Name */}
        <h3 className="font-medium text-gray-900 dark:text-white text-sm mb-1">{name}</h3>
        
        {/* Status */}
        <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium mb-2 ${
          online 
            ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' 
            : 'bg-gray-100 text-gray-600 dark:bg-gray-600 dark:text-gray-300'
        }`}>
          {online ? 'Online' : 'Offline'}
        </span>
        
        {/* Available status */}
        {online && (
          <span className="text-xs text-gray-500 dark:text-gray-400 flex items-center">
            <CheckCircle className="h-3 w-3 mr-1" />
            Available
          </span>
        )}

        {/* Workgroups */}
        {workgroups.length > 0 && (
          <div className="mt-2 space-y-1">
            <p className="text-xs text-gray-600 dark:text-gray-400">Workgroups:</p>
            <div className="flex flex-wrap gap-1 justify-center">
              {workgroups.map((wg, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300"
                >
                  {wg}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default ContributorCard;
