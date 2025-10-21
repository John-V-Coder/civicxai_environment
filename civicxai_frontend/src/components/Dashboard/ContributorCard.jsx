import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, Circle, UserCircle } from 'lucide-react';

/**
 * ContributorCard Component
 * Displays contributor information including authenticated and guest/unauthenticated users
 * 
 * @param {string} name - Contributor name (defaults to 'Anonymous' for guests)
 * @param {string} avatar - Avatar URL (optional)
 * @param {string} role - User role (citizen, contributor, admin, analyst, guest)
 * @param {boolean} online - Online status
 * @param {boolean} isAuthenticated - Whether user is authenticated (defaults to true if role provided)
 * @param {array} workgroups - List of workgroups the contributor belongs to
 */
const ContributorCard = ({ 
  name = 'Anonymous', 
  avatar, 
  role = 'guest', 
  online = false, 
  isAuthenticated = true,
  workgroups = [] 
}) => {
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
            <div className={`h-16 w-16 rounded-full flex items-center justify-center text-white font-bold text-xl ${
              isAuthenticated 
                ? 'bg-gradient-to-br from-purple-400 to-pink-600' 
                : 'bg-gradient-to-br from-gray-400 to-gray-600'
            }`}>
              {name?.[0]?.toUpperCase() || (isAuthenticated ? 'U' : 'G')}
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
        <h3 className="font-medium text-gray-900 dark:text-white text-sm mb-1 flex items-center gap-1">
          {name}
          {!isAuthenticated && (
            <span className="text-xs text-gray-400" title="Guest/Unauthenticated">
              <UserCircle className="h-3 w-3 inline" />
            </span>
          )}
        </h3>
        
        {/* Role Display */}
        {role && role !== 'guest' && (
          <p className="text-xs text-gray-500 dark:text-gray-400 capitalize mb-1">
            {role.replace('_', ' ')}
          </p>
        )}
        
        {/* Status */}
        <div className="flex flex-col items-center gap-1">
          <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
            online 
              ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' 
              : 'bg-gray-100 text-gray-600 dark:bg-gray-600 dark:text-gray-300'
          }`}>
            {online ? 'Online' : 'Offline'}
          </span>
          
          {/* Guest/Unauthenticated Badge */}
          {!isAuthenticated && (
            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-200 text-slate-600 dark:bg-slate-700 dark:text-slate-400">
              Guest
            </span>
          )}
        </div>
        
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
