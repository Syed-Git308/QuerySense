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
    <section className="py-20 px-6">
      <div className="max-w-4xl mx-auto">
        {/* Search Input */}
        <div className="relative mb-12">
          <div className="relative">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask about documents, processes, or knowledge…  ⌘K"
              className="w-full px-6 py-4 bg-white/50 backdrop-blur-sm rounded-2xl border border-black/10 text-lg placeholder-black/40 focus:outline-none focus:ring-2 focus:ring-black/10 focus:border-black/20 transition-all duration-200 shadow-sm hover:shadow-md focus:shadow-md"
            />
            <div className="absolute right-5 top-1/2 transform -translate-y-1/2">
              <Search size={20} strokeWidth={1.5} className="text-black/40" />
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex justify-center mb-12">
          <div className="relative flex bg-black/5 p-1 rounded-full backdrop-blur-sm">
            {/* Background slider */}
            <div 
              className={`absolute top-1 h-9 bg-white rounded-full shadow-sm transition-all duration-300 ease-out ${
                activeTab === 'search' ? 'left-1 w-[90px]' :
                activeTab === 'recent' ? 'left-[95px] w-[82px]' :
                'left-[181px] w-[88px]'
              }`}
            />
            
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`relative z-10 flex items-center px-5 py-2 text-sm font-medium rounded-full transition-all duration-200 ${
                  activeTab === tab.id
                    ? 'text-black'
                    : 'text-black/60 hover:text-black/80'
                }`}
              >
                <tab.icon size={14} strokeWidth={1.5} className="mr-2" />
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <div className="bg-white/60 backdrop-blur-sm rounded-2xl border border-black/10 p-10 shadow-sm">
          {activeTab === 'search' && (
            <div className="text-center text-black/50">
              <Search size={48} strokeWidth={1} className="mx-auto mb-6 text-black/20" />
              <p className="text-xl font-medium mb-2 text-black/70">Enter your query above to get started</p>
              <p className="text-black/50">Ask about documents, processes, or any knowledge in your workspace</p>
            </div>
          )}

          {activeTab === 'recent' && (
            <div>
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
            <div>
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
      </div>
    </section>
  );
};

export default QueryStudio;