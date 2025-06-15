import React, { useState } from 'react';
import Header from './components/Header';
import Hero from './components/Hero';
import QueryStudio from './components/QueryStudio';
import UploadPanel from './components/UploadPanel';
import AnalyticsPanel from './components/AnalyticsPanel';

function App() {
  const [activeTab, setActiveTab] = useState<'workspace' | 'analytics'>('workspace');

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-white">
      <Header activeTab={activeTab} onTabChange={setActiveTab} />
      
      {activeTab === 'workspace' ? (
        <>
          <Hero />
          <QueryStudio />
          <UploadPanel />
        </>
      ) : (
        <AnalyticsPanel />
      )}
    </div>
  );
}

export default App;