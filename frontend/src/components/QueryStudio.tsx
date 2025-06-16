import React, { useState } from 'react';
import { Search, Clock, TrendingUp, Loader } from 'lucide-react';

interface QueryResult {
  id: string;
  filename: string;
  content: string;
  similarity: number;
  file_type: string;
  upload_timestamp: string;
}

interface QueryResponse {
  query: string;
  answer?: string;  // Generated answer
  answer_source?: string;  // Source filename for the answer
  results: QueryResult[];
  total_results: number;
  response_time_ms: number;
  error?: string;
}

const QueryStudio: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'search' | 'recent' | 'insights'>('search');
  const [query, setQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<QueryResult[]>([]);
  const [responseTime, setResponseTime] = useState<number | null>(null);
  const [generatedAnswer, setGeneratedAnswer] = useState<string | null>(null);
  const [answerSource, setAnswerSource] = useState<string | null>(null);
  const [showSourceModal, setShowSourceModal] = useState(false);
  const [sourceContent, setSourceContent] = useState<string | null>(null);
  const [recentQueries, setRecentQueries] = useState<string[]>([
    'What is our Q4 revenue target?',
    'How to onboard new team members?',
    'API integration best practices',
    'Performance review process',
  ]);

  const handleViewSource = async (filename: string) => {
    try {
      console.log('Fetching source document:', filename);
      // Fetch the document content from the backend
      const response = await fetch(`http://localhost:8001/documents/${encodeURIComponent(filename)}/content`);
      
      if (response.ok) {
        const document = await response.json();
        setSourceContent(document.content || 'Document content not available');
        setShowSourceModal(true);
      } else {
        console.error('Document not found:', filename);
        alert('Document not found');
      }
    } catch (error) {
      console.error('Error fetching document:', error);
      alert('Error fetching document');
    }
  };

  const handleSearch = async (searchQuery: string = query) => {
    if (!searchQuery.trim()) {
      console.log('Empty query, not searching');
      return;
    }

    console.log('Starting search for:', searchQuery);
    setIsSearching(true);
    try {
      console.log('Making API call to:', 'http://localhost:8001/query');
      const response = await fetch('http://localhost:8001/query', {
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
        setResponseTime(data.response_time_ms);
        setGeneratedAnswer(data.answer || null);
        setAnswerSource(data.answer_source || null);
        
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
            
            {/* AI Answer Display */}
            {generatedAnswer && (
              <div className="mt-8">
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-2xl p-6 shadow-sm">
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
                      <span className="text-white text-sm font-semibold">AI</span>
                    </div>
                    <div className="flex-1">
                      <h4 className="text-lg font-semibold text-blue-900 mb-2">Answer</h4>
                      <p className="text-blue-800 leading-relaxed">{generatedAnswer}</p>
                      <div className="flex items-center justify-between mt-3">
                        {answerSource && (
                          <button
                            onClick={() => handleViewSource(answerSource)}
                            className="text-sm text-blue-600 hover:text-blue-800 underline cursor-pointer font-medium transition-colors"
                          >
                            📄 Source: {answerSource}
                          </button>
                        )}
                        {responseTime && (
                          <p className="text-sm text-blue-600">
                            Answered in {responseTime}ms
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* No Results Message */}
            {!generatedAnswer && searchResults.length === 0 && (
              <div className="mt-8 text-center py-12">
                <div className="text-gray-400 mb-4">
                  <Search className="w-16 h-16 mx-auto" />
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No results found</h3>
                <p className="text-gray-500">Try rephrasing your question or using different keywords.</p>
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

      {/* Source Document Modal */}
      {showSourceModal && sourceContent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-6 max-w-4xl max-h-[80vh] overflow-hidden shadow-2xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-gray-900">Source Document: {answerSource}</h3>
              <button
                onClick={() => setShowSourceModal(false)}
                className="text-gray-500 hover:text-gray-700 text-2xl font-semibold"
              >
                ×
              </button>
            </div>
            <div className="overflow-y-auto max-h-[60vh] bg-gray-50 rounded-lg p-4">
              <pre className="whitespace-pre-wrap text-sm text-gray-700 font-mono">
                {sourceContent}
              </pre>
            </div>
            <div className="mt-4 flex justify-end">
              <button
                onClick={() => setShowSourceModal(false)}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
};

export default QueryStudio;