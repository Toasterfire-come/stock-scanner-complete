import React from 'react';
import RealTimeNewsFeed from '../../components/RealTimeNewsFeed';

const NewsFeed = () => {
  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Market News</h1>
          <p className="text-gray-600">Stay updated with the latest market news and analysis</p>
        </div>
        
        <RealTimeNewsFeed 
          maxItems={50}
          showHeader={false}
          autoRefresh={true}
        />
      </div>
    </div>
  );
};

export default NewsFeed;

export default NewsFeed;