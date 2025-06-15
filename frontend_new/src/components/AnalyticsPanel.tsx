import React from 'react';
import { MessageSquare, Users, Clock, FileText, ArrowUp, ArrowDown } from 'lucide-react';

const AnalyticsPanel: React.FC = () => {
  const metrics = [
    {
      title: 'Total Queries',
      value: '12,847',
      change: '12.5%',
      trend: 'up',
      icon: MessageSquare,
    },
    {
      title: 'Active Users',
      value: '1,249',
      change: '8.2%',
      trend: 'up',
      icon: Users,
    },
    {
      title: 'Avg Response Time',
      value: '1.2s',
      change: '15.3%',
      trend: 'down',
      icon: Clock,
    },
    {
      title: 'Total Documents',
      value: '3,456',
      change: '23.1%',
      trend: 'up',
      icon: FileText,
    },
  ];

  const recentActivity = [
    {
      user: 'Sarah Chen',
      action: 'uploaded new document',
      file: 'Q4-Marketing-Strategy.pdf',
      time: '2 minutes ago',
      avatar: 'SC',
    },
    {
      user: 'Mike Johnson',
      action: 'searched for',
      file: 'API documentation best practices',
      time: '5 minutes ago',
      avatar: 'MJ',
    },
    {
      user: 'Lisa Wang',
      action: 'queried about',
      file: 'employee onboarding process',
      time: '12 minutes ago',
      avatar: 'LW',
    },
    {
      user: 'David Park',
      action: 'uploaded new document',
      file: 'Tech-Specs-v2.1.md',
      time: '18 minutes ago',
      avatar: 'DP',
    },
    {
      user: 'Emma Rodriguez',
      action: 'searched for',
      file: 'quarterly budget allocation',
      time: '25 minutes ago',
      avatar: 'ER',
    },
  ];

  return (
    <section className="py-20 px-6">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-semibold text-black mb-4 tracking-tight">Analytics Dashboard</h2>
          <p className="text-xl text-black/70 font-medium">Track usage, performance, and insights across your organization</p>
        </div>

        {/* Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          {metrics.map((metric, index) => (
            <div
              key={index}
              className="bg-white/60 backdrop-blur-sm rounded-2xl p-6 border border-black/10 hover:bg-white/80 hover:shadow-lg transition-all duration-300 hover:scale-[1.02]"
            >
              <div className="flex items-center justify-between mb-6">
                <div className="w-12 h-12 bg-black/5 rounded-xl flex items-center justify-center">
                  <metric.icon size={24} strokeWidth={1.5} className="text-black/70" />
                </div>
                <div className="flex items-center space-x-1 text-sm text-black/50">
                  {metric.trend === 'up' ? (
                    <ArrowUp size={12} strokeWidth={2} />
                  ) : (
                    <ArrowDown size={12} strokeWidth={2} />
                  )}
                  <span>{metric.change}</span>
                </div>
              </div>
              <h3 className="text-3xl font-semibold text-black mb-2 tracking-tight">{metric.value}</h3>
              <p className="text-black/60 font-medium">{metric.title}</p>
            </div>
          ))}
        </div>

        {/* Recent Activity */}
        <div className="bg-white/60 backdrop-blur-sm rounded-2xl border border-black/10 p-8 shadow-sm">
          <h3 className="text-2xl font-semibold text-black mb-8 tracking-tight">Recent Activity</h3>
          <div className="space-y-3">
            {recentActivity.map((activity, index) => (
              <div
                key={index}
                className="flex items-center space-x-4 p-4 bg-white/80 rounded-xl hover:bg-white hover:shadow-sm transition-all duration-200 border border-black/5 hover:scale-[1.01]"
              >
                <div className="w-10 h-10 bg-black/10 rounded-full flex items-center justify-center text-black/70 text-sm font-medium">
                  {activity.avatar}
                </div>
                <div className="flex-1">
                  <p className="text-black font-medium">
                    <span className="font-semibold">{activity.user}</span>
                    <span className="text-black/60"> {activity.action} </span>
                    <span className="font-semibold text-black">{activity.file}</span>
                  </p>
                  <p className="text-sm text-black/50 mt-1">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default AnalyticsPanel;