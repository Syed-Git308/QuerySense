import React, { useState } from 'react';
import { Search, Clock, TrendingUp } from 'lucide-react';

const QueryStudio: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'search' | 'recent' | 'insights'>('search');
  const [query, setQuery] = useState('');

  const tabs = [
    { id: 'search', label: 'Search', icon: Search },
    { id: 'recent', label: 'Recent', icon: Clock },
    { id: 'insights', label: 'Insights', icon: TrendingUp },
  ] as const;

  const recentQueries = [
    'What is our Q4 revenue target?',
    'How to onboard new team members?',
    'API integration best practices',
    'Performance review process',
  ];

  const insights = [
    { title: 'Most searched topic', value: 'API Documentation', trend: '+23%' },
    { title: 'Peak usage time', value: '2-4 PM EST', trend: 'Daily' },
    { title: 'Popular department', value: 'Engineering', trend: '45% of queries' },
  ];

  return (
    <section id="query-studio" className="py-12 px-6">
      <div className="max-w-4xl mx-auto">
        {/* Tab Navigation - Apple Style */}
        <div className="flex justify-center mb-12">
          <div 
            className="relative flex items-center bg-zinc-100/80 backdrop-blur-sm rounded-full p-1 shadow-sm"
            role="tablist"
            aria-label="Query Studio tabs"
          >
            {/* Animated background pill - perfectly centered under each tab */}
            <div 
              className={`absolute top-1 bottom-1 bg-white rounded-full transition-all duration-[400ms] ease-[cubic-bezier(0.25,0.46,0.45,0.94)]`}
              style={{
                width: '90px',
                left: activeTab === 'search' ? 'calc(16.67% - 45px)' :
                      activeTab === 'recent' ? 'calc(50% - 45px)' :
                      'calc(83.33% - 45px)',
                boxShadow: '0 3px 12px rgba(0, 0, 0, 0.12), 0 1px 4px rgba(0, 0, 0, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.8)',
                willChange: 'left'
              }}
            />
            
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`relative z-10 flex items-center px-5 py-2.5 text-sm rounded-full transition-all duration-[250ms] ease-[cubic-bezier(0.25,0.46,0.45,0.94)] text-center min-w-[90px] ${
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
                    setActiveTab(tabs[nextIndex].id);
                  }
                }}
              >
                <tab.icon size={14} strokeWidth={1.5} className="mr-2" />
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Search Input - Only show when on search tab */}
        {activeTab === 'search' && (
          <div className="relative mb-12">
            <div className="relative">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask about documents, processes, or knowledge… "
                className="w-full px-6 py-4 bg-white/50 backdrop-blur-sm rounded-2xl border border-black/10 text-lg placeholder-black/40 focus:outline-none focus:ring-2 focus:ring-black/10 focus:border-black/20 transition-all duration-200 shadow-sm hover:shadow-md focus:shadow-md"
              />
              <div className="absolute right-5 top-1/2 transform -translate-y-1/2">
                <Search size={20} strokeWidth={1.5} className="text-black/40" />
              </div>
            </div>
          </div>
        )}

        {/* Tab Content */}
        {activeTab === 'recent' && (
          <div className="bg-white/60 backdrop-blur-sm rounded-2xl border border-black/10 p-10 shadow-sm">
            <h3 className="text-xl font-semibold text-black mb-8 tracking-tight">Recent Queries</h3>
            <div className="space-y-3">
              {recentQueries.map((query, index) => (
                <button
                  key={index}
                  className="w-full text-left p-4 bg-white/80 rounded-xl hover:bg-white hover:shadow-sm transition-all duration-200 border border-black/5 hover:scale-[1.01]"
                >
                  <p className="text-black font-medium">{query}</p>
                  <p className="text-sm text-black/50 mt-1">{Math.floor(Math.random() * 24)} hours ago</p>
                </button>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'insights' && (
          <div className="bg-white/60 backdrop-blur-sm rounded-2xl border border-black/10 p-10 shadow-sm">
            <h3 className="text-xl font-semibold text-black mb-8 tracking-tight">Usage Insights</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {insights.map((insight, index) => (
                <div key={index} className="bg-white/80 rounded-xl p-6 border border-black/5 hover:shadow-sm transition-all duration-200">
                  <p className="text-sm text-black/60 mb-3 font-medium">{insight.title}</p>
                  <p className="text-2xl font-semibold text-black mb-2 tracking-tight">{insight.value}</p>
                  <p className="text-sm text-black/50 font-medium">{insight.trend}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </section>
  );
};

export default QueryStudio;