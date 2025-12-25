// app/frontend/src/pages/education/CourseCatalog.jsx
/**
 * Course Catalog Component
 * Phase 7 Implementation - TradeScanPro
 * TradingView-inspired design
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../../api/client';
import logger from '../../lib/logger';

const CourseCatalog = () => {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedDifficulty, setSelectedDifficulty] = useState('all');

  const categories = [
    { value: 'all', label: 'All Courses' },
    { value: 'fundamentals', label: 'Trading Fundamentals' },
    { value: 'technical', label: 'Technical Analysis' },
    { value: 'fundamental', label: 'Fundamental Analysis' },
    { value: 'strategy', label: 'Strategy Development' },
    { value: 'psychology', label: 'Psychology & Risk' },
  ];

  const difficulties = [
    { value: 'all', label: 'All Levels' },
    { value: 'beginner', label: 'Beginner' },
    { value: 'intermediate', label: 'Intermediate' },
    { value: 'advanced', label: 'Advanced' },
  ];

  useEffect(() => {
    fetchCourses();
  }, [selectedCategory, selectedDifficulty]);

  const fetchCourses = async () => {
    setLoading(true);
    try {
      let url = '/api/education/courses/';
      const params = [];
      
      if (selectedCategory !== 'all') {
        params.push(`category=${selectedCategory}`);
      }
      if (selectedDifficulty !== 'all') {
        params.push(`difficulty=${selectedDifficulty}`);
      }
      
      if (params.length > 0) {
        url += '?' + params.join('&');
      }

      const response = await api.get(url);
      setCourses(response.data || []);
    } catch (error) {
      logger.error('Error fetching courses:', error);
      setCourses([]);
    } finally {
      setLoading(false);
    }
  };

  const getDifficultyBadgeColor = (difficulty) => {
    switch (difficulty) {
      case 'beginner':
        return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'intermediate':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'advanced':
        return 'bg-red-500/20 text-red-400 border-red-500/30';
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const formatDuration = (minutes) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) {
      return `${hours}h ${mins}m`;
    }
    return `${mins}m`;
  };

  return (
    <div className="min-h-screen bg-[#131722] text-[#D1D4DC]">
      {/* Header */}
      <div className="bg-[#1E222D] border-b border-[#2A2E39] py-8">
        <div className="max-w-7xl mx-auto px-4">
          <h1 className="text-3xl font-bold mb-2">Trading Education</h1>
          <p className="text-[#787B86]">
            Master the markets with our comprehensive trading courses
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex flex-wrap gap-4 mb-8">
          {/* Category Filter */}
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm text-[#787B86] mb-2">Category</label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full bg-[#1E222D] border border-[#2A2E39] rounded-lg px-4 py-2
                       text-[#D1D4DC] focus:outline-none focus:border-[#2962FF]
                       hover:border-[#3A3E49] transition-colors"
            >
              {categories.map((cat) => (
                <option key={cat.value} value={cat.value}>
                  {cat.label}
                </option>
              ))}
            </select>
          </div>

          {/* Difficulty Filter */}
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm text-[#787B86] mb-2">Difficulty</label>
            <select
              value={selectedDifficulty}
              onChange={(e) => setSelectedDifficulty(e.target.value)}
              className="w-full bg-[#1E222D] border border-[#2A2E39] rounded-lg px-4 py-2
                       text-[#D1D4DC] focus:outline-none focus:border-[#2962FF]
                       hover:border-[#3A3E49] transition-colors"
            >
              {difficulties.map((diff) => (
                <option key={diff.value} value={diff.value}>
                  {diff.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Course Grid */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="bg-[#1E222D] rounded-lg p-6 animate-pulse">
                <div className="h-4 bg-[#2A2E39] rounded w-3/4 mb-4"></div>
                <div className="h-3 bg-[#2A2E39] rounded w-full mb-2"></div>
                <div className="h-3 bg-[#2A2E39] rounded w-5/6"></div>
              </div>
            ))}
          </div>
        ) : courses.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-[#787B86]">No courses found matching your filters.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {courses.map((course) => (
              <Link
                key={course.id}
                to={`/learn/${course.slug}`}
                className="block"
              >
                <div className="bg-[#1E222D] border border-[#2A2E39] rounded-lg p-6
                              hover:border-[#3A3E49] hover:shadow-lg
                              transition-all duration-200 cursor-pointer
                              hover:-translate-y-1">
                  {/* Header */}
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-[#D1D4DC] mb-1">
                        {course.title}
                      </h3>
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-1 rounded text-xs border
                                      ${getDifficultyBadgeColor(course.difficulty)}`}>
                          {course.difficulty}
                        </span>
                        {course.is_premium && (
                          <span className="px-2 py-1 rounded text-xs border
                                       bg-[#2962FF]/20 text-[#2962FF] border-[#2962FF]/30">
                            Premium
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Description */}
                  <p className="text-sm text-[#787B86] mb-4 line-clamp-2">
                    {course.description}
                  </p>

                  {/* Stats */}
                  <div className="flex items-center justify-between text-sm text-[#787B86] mb-4">
                    <span>📚 {course.lesson_count} lessons</span>
                    <span>⏱️ {formatDuration(course.duration_minutes)}</span>
                  </div>

                  {/* Progress Bar */}
                  {course.completion_percentage > 0 && (
                    <div className="mb-2">
                      <div className="flex justify-between text-xs text-[#787B86] mb-1">
                        <span>Progress</span>
                        <span>{course.completion_percentage}%</span>
                      </div>
                      <div className="w-full bg-[#2A2E39] rounded-full h-2">
                        <div
                          className="bg-[#2962FF] h-2 rounded-full transition-all duration-300"
                          style={{ width: `${course.completion_percentage}%` }}
                        ></div>
                      </div>
                    </div>
                  )}

                  {/* CTA */}
                  <button className="w-full mt-4 bg-[#2962FF] text-white py-2 rounded-lg
                                   hover:bg-[#1E53E5] transition-colors duration-150
                                   font-medium">
                    {course.completion_percentage > 0 ? 'Continue Learning' : 'Start Course'}
                  </button>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default CourseCatalog;
