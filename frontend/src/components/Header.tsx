import React, { useState } from 'react';
import { User } from 'lucide-react';
import ProfileDropdown from './ProfileDropdown';

interface HeaderProps {
  activeTab: 'workspace' | 'analytics';
  onTabChange: (tab: 'workspace' | 'analytics') => void;
}

const Header: React.FC<HeaderProps> = ({ activeTab, onTabChange }) => {
  const [showProfileDropdown, setShowProfileDropdown] = useState(false);

  const tabs = [
    { id: 'workspace' as const, label: 'Workspace' },
    { id: 'analytics' as const, label: 'Analytics' }
  ];

  return (
    <>
      <header className="sticky top-0 z-50 backdrop-blur-xl bg-white/80 border-b border-zinc-200/20">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <div className="flex-shrink-0">
              <h1 className="text-xl font-semibold text-black tracking-tight">
                QuerySense
              </h1>
            </div>

            {/* Apple-style Segmented Control */}
            <div 
              className="relative flex items-center bg-zinc-100/80 backdrop-blur-sm rounded-full p-1 shadow-sm"
              role="tablist"
              aria-label="Navigation tabs"
            >
              {/* Animated background pill - perfectly centered under each tab */}
              <div 
                className="absolute top-1 bottom-1 bg-white rounded-full transition-all duration-[400ms] ease-[cubic-bezier(0.25,0.46,0.45,0.94)]"
                style={{
                  width: '108px',
                  left: activeTab === 'workspace' ? 'calc(25% - 54px)' : 'calc(75% - 54px)',
                  boxShadow: '0 3px 12px rgba(0, 0, 0, 0.12), 0 1px 4px rgba(0, 0, 0, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.8)',
                  willChange: 'left'
                }}
              />
              
              {/* Tab buttons */}
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => onTabChange(tab.id)}
                  className={`relative z-10 px-6 py-2.5 text-sm rounded-full transition-all duration-[250ms] ease-[cubic-bezier(0.25,0.46,0.45,0.94)] text-center min-w-[108px] ${
                    activeTab === tab.id
                      ? 'text-black font-semibold transform scale-[1.01]'
                      : 'text-zinc-500 hover:text-zinc-700 font-medium hover:scale-[1.005]'
                  }`}
                  role="tab"
                  aria-selected={activeTab === tab.id}
                  aria-controls={`${tab.id}-panel`}
                  tabIndex={activeTab === tab.id ? 0 : -1}
                  onKeyDown={(e) => {
                    if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
                      e.preventDefault();
                      const currentIndex = tabs.findIndex(t => t.id === activeTab);
                      const nextIndex = e.key === 'ArrowRight' 
                        ? (currentIndex + 1) % tabs.length
                        : (currentIndex - 1 + tabs.length) % tabs.length;
                      onTabChange(tabs[nextIndex].id);
                    }
                  }}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Right Section */}
            <div className="flex items-center space-x-3">
              <div className="relative">
                <button
                  onClick={() => setShowProfileDropdown(!showProfileDropdown)}
                  className="w-9 h-9 bg-zinc-100/80 rounded-full flex items-center justify-center text-zinc-600 hover:bg-zinc-200/60 transition-all duration-200 hover:scale-105"
                  aria-label="User profile"
                  aria-expanded={showProfileDropdown}
                  aria-haspopup="true"
                >
                  <User size={16} strokeWidth={1.5} />
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