import React, { useState } from 'react';
import { Search, Clock, TrendingUp, Loader } from 'lucide-react';

interface QueryResult {
  document: {
    id: string;
    filename: string;
    uploadedAt: string;
  };
  score: number;
  relevance: number;
  matchedTerms: string[];
  snippets: string[];
}

interface QueryResponse {
  query: string;
  results: QueryResult[];
  responseTime: number;
  totalDocuments: number;
  error?: string;
}

const QueryStudio: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'search' | 'recent' | 'insights'>('search');
  const [query, setQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<QueryResult[]>([]);
  const [responseTime, setResponseTime] = useState<number | null>(null);
  const [recentQueries, setRecentQueries] = useState<string[]>([
    'What is our Q4 revenue target?',
    'How to onboard new team members?',
    'API integration best practices',
    'Performance review process',
  ]);

  const handleSearch = async (searchQuery: string = query) => {
    if (!searchQuery.trim()) {
      console.log('Empty query, not searching');
      return;
    }

    console.log('Starting search for:', searchQuery);
    setIsSearching(true);
    try {
      console.log('Making API call to:', 'http://localhost:3001/api/query');
      const response = await fetch('http://localhost:3001/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: searchQuery,
          limit: 3
        }),
      });

      console.log('API response status:', response.status);
      const data: QueryResponse = await response.json();
      console.log('API response data:', data);

      if (response.ok) {
        setSearchResults(data.results);
        setResponseTime(data.responseTime);
        
        // Add to recent queries if not already there
        if (!recentQueries.includes(searchQuery)) {
          setRecentQueries(prev => [searchQuery, ...prev.slice(0, 9)]);
        }
        
        console.log('Search completed successfully, found', data.results.length, 'results');
      } else {
        throw new Error(data.error || 'Search failed');
      }
    } catch (error) {
      console.error('Search error:', error);
      alert(`Search failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsSearching(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !isSearching) {
      handleSearch();
    }
  };

  const tabs = [
    { id: 'search', label: 'Search', icon: Search },
    { id: 'recent', label: 'Recent', icon: Clock },
    { id: 'insights', label: 'Insights', icon: TrendingUp },
  ] as const;

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
                onKeyPress={handleKeyPress}
                placeholder="Ask about documents, processes, or knowledge… "
                className="w-full px-6 py-4 bg-white/50 backdrop-blur-sm rounded-2xl border border-black/10 text-lg placeholder-black/40 focus:outline-none focus:ring-2 focus:ring-black/10 focus:border-black/20 transition-all duration-200 shadow-sm hover:shadow-md focus:shadow-md"
                disabled={isSearching}
              />
              <button
                onClick={() => {
                  console.log('Search button clicked!');
                  handleSearch();
                }}
                disabled={isSearching || !query.trim()}
                className="absolute right-5 top-1/2 transform -translate-y-1/2 p-1 rounded-lg hover:bg-black/5 transition-all duration-150 disabled:opacity-50"
              >
                {isSearching ? (
                  <Loader size={20} className="text-black/40 animate-spin" />
                ) : (
                  <Search size={20} strokeWidth={1.5} className="text-black/40" />
                )}
              </button>
            </div>
            
            {/* Search Results */}
            {searchResults.length > 0 && (
              <div className="mt-8 space-y-4">
                {/* Search Header */}
                <div className="flex items-center justify-between">
                  <h3 className="text-xl font-semibold tracking-tight text-black">Search Results</h3>
                  {responseTime && (
                    <span className="text-sm text-gray-400">
                      Found {searchResults.length} result{searchResults.length !== 1 ? 's' : ''} in {responseTime}ms
                    </span>
                  )}
                </div>
                
                {/* Results Cards */}
                <div className="space-y-4">
                  {searchResults.map((result) => (
                    <div
                      key={result.document.id}
                      className="group bg-[#f9f9f9] rounded-2xl p-4 md:p-6 lg:p-8 shadow-md hover:shadow-lg transition-all duration-200 ease-in-out hover:scale-[1.01] cursor-pointer"
                    >
                      {/* File Header */}
                      <div className="flex flex-col md:flex-row md:items-start md:justify-between mb-4 gap-2">
                        <h4 className="text-lg font-semibold tracking-tight text-black">
                          {result.document.filename}
                        </h4>
                        <div className="flex items-center space-x-2 text-sm text-gray-500 md:text-right">
                          <span>Relevance: {Math.round(result.relevance * 100)}%</span>
                          <span className="hidden md:inline">•</span>
                          <span>{new Date(result.document.uploadedAt).toLocaleDateString()}</span>
                        </div>
                      </div>
                      
                      {/* Document Preview Text */}
                      {result.snippets.length > 0 && (
                        <div className="space-y-4 mb-6">
                          {result.snippets.map((snippet, snippetIndex) => (
                            <div key={snippetIndex} className="relative">
                              <p
                                className="text-gray-700 leading-relaxed text-base line-clamp-4"
                                dangerouslySetInnerHTML={{
                                  __html: snippet.replace(/\*\*(.*?)\*\*/g, '<strong class="bg-yellow-100 text-yellow-800 px-1.5 py-0.5 rounded-md font-medium">$1</strong>')
                                }}
                              />
                              {/* Subtle fade for long content */}
                              <div className="absolute bottom-0 left-0 right-0 h-4 bg-gradient-to-t from-[#f9f9f9] to-transparent pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity duration-200"></div>
                            </div>
                          ))}
                        </div>
                      )}
                      
                      {/* Tags */}
                      {result.matchedTerms.length > 0 && (
                        <div className="flex flex-wrap gap-2">
                          {result.matchedTerms.map((term, termIndex) => (
                            <span
                              key={termIndex}
                              className="inline-flex items-center rounded-full bg-gray-100 hover:bg-gray-200 text-gray-600 hover:text-gray-700 text-xs px-3 py-1.5 font-medium hover:shadow-sm hover:scale-[1.02] transition-all duration-150 ease-in-out"
                            >
                              {term}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Tab Content */}
        {activeTab === 'recent' && (
          <div className="bg-white/60 backdrop-blur-sm rounded-2xl border border-black/10 p-10 shadow-sm">
            <h3 className="text-xl font-semibold text-black mb-8 tracking-tight">Recent Queries</h3>
            <div className="space-y-3">
              {recentQueries.map((recentQuery, index) => (
                <button
                  key={index}
                  onClick={() => {
                    setQuery(recentQuery);
                    setActiveTab('search');
                    handleSearch(recentQuery);
                  }}
                  className="w-full text-left p-4 bg-white/80 rounded-xl hover:bg-white hover:shadow-sm transition-all duration-200 border border-black/5 hover:scale-[1.01]"
                >
                  <p className="text-black font-medium">{recentQuery}</p>
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