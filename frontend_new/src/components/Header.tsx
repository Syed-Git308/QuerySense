import React, { useState } from 'react';
import { Settings, User } from 'lucide-react';
import ProfileDropdown from './ProfileDropdown';

interface HeaderProps {
  activeTab: 'workspace' | 'analytics';
  onTabChange: (tab: 'workspace' | 'analytics') => void;
}

const Header: React.FC<HeaderProps> = ({ activeTab, onTabChange }) => {
  const [showProfileDropdown, setShowProfileDropdown] = useState(false);

  return (
    <>
      <header className="sticky top-0 z-50 backdrop-blur-xl bg-white/80 border-b border-black/5">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <div className="flex-shrink-0">
              <h1 className="text-xl font-semibold text-black tracking-tight">
                QuerySense
              </h1>
            </div>

            {/* Apple-style Segmented Control */}
            <div className="relative flex items-center bg-black/5 p-1 rounded-full backdrop-blur-sm">
              {/* Background slider */}
              <div 
                className={`absolute top-1 h-8 bg-white rounded-full shadow-sm transition-all duration-300 ease-out ${
                  activeTab === 'workspace' 
                    ? 'left-1 w-[88px]' 
                    : 'left-[93px] w-[80px]'
                }`}
              />
              
              {/* Buttons */}
              <button
                onClick={() => onTabChange('workspace')}
                className={`relative z-10 px-5 py-2 text-sm font-medium rounded-full transition-all duration-300 ease-out ${
                  activeTab === 'workspace'
                    ? 'text-black'
                    : 'text-black/60 hover:text-black/80'
                }`}
              >
                Workspace
              </button>
              <button
                onClick={() => onTabChange('analytics')}
                className={`relative z-10 px-5 py-2 text-sm font-medium rounded-full transition-all duration-300 ease-out ${
                  activeTab === 'analytics'
                    ? 'text-black'
                    : 'text-black/60 hover:text-black/80'
                }`}
              >
                Analytics
              </button>
            </div>

            {/* Right Section */}
            <div className="flex items-center space-x-3">
              <button className="p-2 text-black/60 hover:text-black hover:bg-black/5 rounded-full transition-all duration-200">
                <Settings size={18} strokeWidth={1.5} />
              </button>
              <div className="relative">
                <button
                  onClick={() => setShowProfileDropdown(!showProfileDropdown)}
                  className="w-8 h-8 bg-black/10 rounded-full flex items-center justify-center text-black/70 hover:bg-black/15 transition-all duration-200"
                >
                  <User size={14} strokeWidth={1.5} />
                </button>
                {showProfileDropdown && (
                  <ProfileDropdown onClose={() => setShowProfileDropdown(false)} />
                )}
              </div>
            </div>
          </div>
        </div>
      </header>
    </>
  );
};

export default Header;