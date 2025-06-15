import Navigation from '@/components/Navigation';
import HeroSection from '@/components/HeroSection';
import DocumentWorkspace from '@/components/DocumentWorkspace';
import QueryStudio from '@/components/QueryStudio';
import InsightsPanel from '@/components/InsightsPanel';
import FloatingAI from '@/components/FloatingAI';

export default function Home() {
  return (
    <main 
      className="min-h-screen relative overflow-hidden"
      style={{ background: 'var(--background-primary)' }}
    >
      {/* Vision Pro Ambient Lighting - Softer & More Refined */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {/* Primary ambient light - softer blend */}
        <div 
          className="absolute -top-32 right-1/3 w-[800px] h-[800px] rounded-full opacity-12 blur-3xl"
          style={{
            background: 'radial-gradient(circle, var(--accent-blue) 0%, var(--accent-blue-subtle) 40%, transparent 70%)',
            animation: 'float 25s ease-in-out infinite'
          }}
        />
        
        {/* Secondary ambient - ultra subtle */}
        <div 
          className="absolute bottom-0 left-1/4 w-[600px] h-[600px] rounded-full opacity-8 blur-3xl"
          style={{
            background: 'radial-gradient(circle, var(--accent-indigo) 0%, transparent 60%)',
            animation: 'float 30s ease-in-out infinite reverse',
            animationDelay: '12s'
          }}
        />
      </div>

      <div className="relative z-10 animate-in">
        <Navigation />
        
        {/* Vision Pro Content Container with Refined Grid */}
        <div className="max-w-screen-2xl mx-auto px-8 lg:px-12">
          <HeroSection />
          
          {/* Main workspace with Vision Pro spacing */}
          <section style={{ paddingTop: 'var(--space-32)', paddingBottom: 'var(--space-24)' }}>
            <div className="grid grid-cols-1 xl:grid-cols-12 gap-10">
              {/* Document workspace - Perfect grid alignment */}
              <div className="xl:col-span-4">
                <DocumentWorkspace />
              </div>
              
              {/* Query studio - Primary content area */}
              <div className="xl:col-span-8">
                <QueryStudio />
              </div>
            </div>
          </section>
          
          {/* Insights section with gradient divider */}
          <section 
            className="relative"
            style={{ paddingTop: 'var(--space-32)', paddingBottom: 'var(--space-32)' }}
          >
            {/* Subtle gradient divider */}
            <div 
              className="absolute top-0 left-0 right-0 h-px"
              style={{
                background: 'linear-gradient(90deg, transparent 0%, var(--border-thin) 20%, var(--border-regular) 50%, var(--border-thin) 80%, transparent 100%)',
                filter: 'blur(0.5px)'
              }}
            />
            
            <div className="text-center" style={{ marginBottom: 'var(--space-20)' }}>
              <h2 
                className="text-title-1"
                style={{ 
                  color: 'var(--text-primary)',
                  marginBottom: 'var(--space-6)'
                }}
              >
                Analytics Overview
              </h2>
              <p 
                className="text-body max-w-2xl mx-auto"
                style={{ color: 'var(--text-secondary)' }}
              >
                Real-time insights into your knowledge ecosystem with intelligent metrics 
                and predictive analytics powered by machine learning.
              </p>
            </div>
            <InsightsPanel />
          </section>
        </div>
      </div>

      {/* Floating AI Assistant */}
      <FloatingAI />
    </main>
  );
}
