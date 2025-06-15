import React, { useState } from 'react';
import { ArrowRight, Play, Zap, Target, Users, X } from 'lucide-react';

const Hero: React.FC = () => {
  const [showVideoModal, setShowVideoModal] = useState(false);
  const valueCards = [
    { icon: Zap, title: '10x Faster', description: 'Instant knowledge retrieval' },
    { icon: Target, title: '99.8% Accuracy', description: 'Precision-tuned responses' },
    { icon: Users, title: '500+ Organizations', description: 'Trusted by enterprises' },
  ];

  const scrollToQueryStudio = () => {
    const queryStudio = document.getElementById('query-studio');
    if (queryStudio) {
      const headerHeight = 80; // Approximate header height
      const yOffset = -headerHeight - 20; // Extra space to show tabs clearly
      const yPosition = queryStudio.getBoundingClientRect().top + window.pageYOffset + yOffset;
      
      window.scrollTo({
        top: yPosition,
        behavior: 'smooth'
      });
    }
  };

  return (
    <section className="relative py-24 px-6 overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0 bg-gradient-to-br from-black/[0.02] via-white to-black/[0.01] pointer-events-none" />
      
      <div className="relative max-w-4xl mx-auto text-center">
        {/* Main Headline */}
        <h1 className="text-6xl md:text-7xl font-semibold text-black mb-6 tracking-tight leading-none">
          Think Beyond
          <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            {' '}Search
          </span>
        </h1>
        
        {/* Subheadline */}
        <p className="text-xl text-black/70 mb-16 max-w-2xl mx-auto leading-relaxed font-medium">
          Your knowledge, instantly accessible. Questions answered with intelligence.
        </p>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-24">
          <button 
            onClick={scrollToQueryStudio}
            className="inline-flex items-center px-8 py-3 bg-black text-white rounded-full font-medium hover:bg-black/90 transition-all duration-200 hover:shadow-lg hover:scale-[1.02] active:scale-[0.98] group"
          >
            Start Creating
            <ArrowRight size={18} strokeWidth={1.5} className="ml-2 group-hover:translate-x-0.5 transition-transform duration-200" />
          </button>
          <button 
            onClick={() => setShowVideoModal(true)}
            className="inline-flex items-center px-8 py-3 bg-white/80 backdrop-blur-sm text-black rounded-full font-medium border border-black/10 hover:bg-white hover:shadow-lg transition-all duration-200 hover:scale-[1.02] active:scale-[0.98] group"
          >
            <Play size={18} strokeWidth={1.5} className="mr-2 group-hover:scale-110 transition-transform duration-200" />
            Watch Demo
          </button>
        </div>

        {/* Value Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
          {valueCards.map((card, index) => (
            <div
              key={index}
              className="bg-white/60 backdrop-blur-sm rounded-2xl p-8 border border-black/10 hover:bg-white/80 hover:shadow-lg transition-all duration-300 group hover:scale-[1.02]"
            >
              <div className="w-12 h-12 bg-black/5 rounded-xl flex items-center justify-center mb-6 group-hover:bg-black/10 transition-colors duration-200">
                <card.icon size={24} strokeWidth={1.5} className="text-black/70" />
              </div>
              <h3 className="text-2xl font-semibold text-black mb-3 tracking-tight">{card.title}</h3>
              <p className="text-black/70 font-medium">{card.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Video Modal */}
      {showVideoModal && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
          onClick={() => setShowVideoModal(false)}
        >
          <div 
            className="relative bg-white/95 backdrop-blur-md rounded-3xl shadow-2xl max-w-4xl w-full max-h-[80vh] overflow-hidden"
            onClick={(e) => e.stopPropagation()}
            style={{
              boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(255, 255, 255, 0.1)'
            }}
          >
            {/* Close button */}
            <button
              onClick={() => setShowVideoModal(false)}
              className="absolute top-4 right-4 z-10 w-10 h-10 bg-black/10 hover:bg-black/20 rounded-full flex items-center justify-center transition-all duration-200 hover:scale-110"
            >
              <X size={20} className="text-black/70" />
            </button>
            
            {/* Video container */}
            <div className="aspect-video w-full">
              <iframe
                src="https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=1&mute=1&rel=0&modestbranding=1"
                title="QuerySense Demo"
                className="w-full h-full rounded-3xl"
                frameBorder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
            </div>
          </div>
        </div>
      )}
    </section>
  );
};

export default Hero;