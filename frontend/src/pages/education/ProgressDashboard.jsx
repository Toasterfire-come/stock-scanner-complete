// User Progress Dashboard Component - Phase 7
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getApiClient } from '../../api/client';

const ProgressDashboard = () => {
  const [stats, setStats] = useState(null);
  const [recentProgress, setRecentProgress] = useState([]);
  const [certificates, setCertificates] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUserStats();
    fetchRecentProgress();
    fetchCertificates();
  }, []);

  const fetchUserStats = async () => {
    try {
      const api = getApiClient();
      const response = await api.get('/api/education/user-stats/overview/');
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchRecentProgress = async () => {
    try {
      const api = getApiClient();
      const response = await api.get('/api/education/user-stats/progress/');
      setRecentProgress((response.data || []).slice(0, 5));
    } catch (error) {
      console.error('Error fetching progress:', error);
    }
  };

  const fetchCertificates = async () => {
    try {
      const api = getApiClient();
      const response = await api.get('/api/education/user-stats/certificates/');
      setCertificates(response.data || []);
    } catch (error) {
      console.error('Error fetching certificates:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#131722] flex items-center justify-center">
        <div className="text-[#787B86]">Loading progress...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#131722]" data-testid="progress-dashboard">
      {/* Header */}
      <div className="bg-[#1E222D] border-b border-[#2A2E39] py-8">
        <div className="max-w-7xl mx-auto px-4">
          <h1 className="text-3xl font-bold text-[#D1D4DC] mb-2">My Learning Progress</h1>
          <p className="text-[#787B86]">Track your trading education journey</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-[#1E222D] border border-[#2A2E39] rounded-lg p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-2xl">📚</span>
              <span className="text-[#2962FF] text-sm font-medium">Courses</span>
            </div>
            <p className="text-3xl font-bold text-[#D1D4DC] mb-1">
              {stats?.total_courses_completed || 0}
            </p>
            <p className="text-sm text-[#787B86]">
              of {stats?.total_courses_started || 0} started
            </p>
          </div>

          <div className="bg-[#1E222D] border border-[#2A2E39] rounded-lg p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-2xl">✓</span>
              <span className="text-[#089981] text-sm font-medium">Lessons</span>
            </div>
            <p className="text-3xl font-bold text-[#D1D4DC] mb-1">
              {stats?.total_lessons_completed || 0}
            </p>
            <p className="text-sm text-[#787B86]">Lessons completed</p>
          </div>

          <div className="bg-[#1E222D] border border-[#2A2E39] rounded-lg p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-2xl">⏱️</span>
              <span className="text-[#FF9800] text-sm font-medium">Time</span>
            </div>
            <p className="text-3xl font-bold text-[#D1D4DC] mb-1">
              {stats?.total_time_spent_hours || 0}h
            </p>
            <p className="text-sm text-[#787B86]">Learning time</p>
          </div>

          <div className="bg-[#1E222D] border border-[#2A2E39] rounded-lg p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-2xl">🔥</span>
              <span className="text-[#F23645] text-sm font-medium">Streak</span>
            </div>
            <p className="text-3xl font-bold text-[#D1D4DC] mb-1">
              {stats?.current_streak || 0}
            </p>
            <p className="text-sm text-[#787B86]">
              Best: {stats?.longest_streak || 0} days
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Activity */}
          <div className="bg-[#1E222D] border border-[#2A2E39] rounded-lg p-6">
            <h2 className="text-xl font-semibold text-[#D1D4DC] mb-6">
              Recent Activity
            </h2>
            
            {recentProgress.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-[#787B86] mb-4">No recent activity</p>
                <Link
                  to="/learn"
                  className="inline-block bg-[#2962FF] text-white px-6 py-2 rounded-lg
                           hover:bg-[#1E53E5] transition-colors"
                >
                  Start Learning
                </Link>
              </div>
            ) : (
              <div className="space-y-4">
                {recentProgress.map((progress) => (
                  <Link
                    key={progress.id}
                    to={`/learn/lesson/${progress.lesson_slug || progress.lesson}`}
                    className="block"
                  >
                    <div className="p-4 bg-[#131722] rounded-lg border border-[#2A2E39]
                                  hover:border-[#3A3E49] hover:bg-[#1E222D] transition-all">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <h3 className="text-[#D1D4DC] font-medium mb-1">
                            {progress.lesson_title}
                          </h3>
                          <p className="text-sm text-[#787B86]">
                            {progress.course_title}
                          </p>
                        </div>
                        {progress.completed && (
                          <span className="text-[#089981]">✓</span>
                        )}
                      </div>
                      
                      <div className="mt-3">
                        <div className="flex justify-between text-xs text-[#787B86] mb-1">
                          <span>Progress</span>
                          <span>{progress.progress_percentage}%</span>
                        </div>
                        <div className="w-full bg-[#2A2E39] rounded-full h-1.5">
                          <div
                            className="bg-[#2962FF] h-1.5 rounded-full transition-all"
                            style={{ width: `${progress.progress_percentage}%` }}
                          ></div>
                        </div>
                      </div>

                      {progress.quiz_score !== null && (
                        <div className="mt-2 flex items-center gap-2">
                          <span className="text-xs text-[#787B86]">Quiz:</span>
                          <span className={`text-xs font-medium ${
                            progress.quiz_score >= 70 ? 'text-[#089981]' : 'text-[#F23645]'
                          }`}>
                            {progress.quiz_score}%
                          </span>
                        </div>
                      )}
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>

          {/* Certificates */}
          <div className="bg-[#1E222D] border border-[#2A2E39] rounded-lg p-6">
            <h2 className="text-xl font-semibold text-[#D1D4DC] mb-6">
              Certificates Earned
            </h2>

            {certificates.length === 0 ? (
              <div className="text-center py-8">
                <span className="text-6xl mb-4 block">🏆</span>
                <p className="text-[#787B86] mb-4">
                  Complete a course to earn your first certificate
                </p>
                <Link
                  to="/learn"
                  className="inline-block bg-[#2962FF] text-white px-6 py-2 rounded-lg
                           hover:bg-[#1E53E5] transition-colors"
                >
                  View Courses
                </Link>
              </div>
            ) : (
              <div className="space-y-4">
                {certificates.map((cert) => (
                  <div
                    key={cert.id}
                    className="p-4 bg-gradient-to-r from-[#2962FF]/10 to-[#089981]/10
                             border border-[#2962FF]/30 rounded-lg"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <h3 className="text-[#D1D4DC] font-semibold mb-1">
                          {cert.course_title}
                        </h3>
                        <p className="text-sm text-[#787B86]">
                          Completed {new Date(cert.issued_at).toLocaleDateString()}
                        </p>
                      </div>
                      <span className="text-2xl">🏆</span>
                    </div>

                    <div className="flex items-center justify-between text-sm">
                      <div className="flex gap-4">
                        <div>
                          <span className="text-[#787B86]">Time: </span>
                          <span className="text-[#D1D4DC]">
                            {cert.completion_time_hours}h
                          </span>
                        </div>
                        <div>
                          <span className="text-[#787B86]">Score: </span>
                          <span className="text-[#089981] font-medium">
                            {cert.average_quiz_score}%
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="mt-2 pt-2 border-t border-[#2A2E39]">
                      <p className="text-xs text-[#787B86]">
                        Certificate ID: {cert.certificate_id}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Call to Action */}
        <div className="mt-8 text-center">
          <Link
            to="/learn"
            className="inline-block bg-[#2962FF] text-white px-8 py-3 rounded-lg
                     hover:bg-[#1E53E5] transition-colors font-medium text-lg"
          >
            Continue Learning
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ProgressDashboard;
