// app/frontend/src/pages/education/CourseDetail.jsx
/**
 * Course Detail Component
 * Phase 7 Implementation - TradeScanPro
 * Shows course details with lesson list
 */

import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { api } from '../../api/client';
import logger from '../../lib/logger';

const CourseDetail = () => {
  const { courseSlug } = useParams();
  const navigate = useNavigate();
  const [course, setCourse] = useState(null);
  const [loading, setLoading] = useState(true);
  const [enrolling, setEnrolling] = useState(false);

  useEffect(() => {
    fetchCourse();
  }, [courseSlug]);

  const fetchCourse = async () => {
    try {
      const response = await api.get(`/api/education/courses/${courseSlug}/`);
      setCourse(response.data);
      setLoading(false);
    } catch (error) {
      logger.error('Error fetching course:', error);
      setLoading(false);
    }
  };

  const handleEnroll = async () => {
    setEnrolling(true);
    try {
      const response = await api.post(`/api/education/courses/${courseSlug}/enroll/`);
      if (response.data.first_lesson_slug) {
        navigate(`/learn/lesson/${response.data.first_lesson_slug}`);
      }
    } catch (error) {
      logger.error('Error enrolling:', error);
      if (error.response?.status === 403) {
        alert('Premium subscription required for this course');
      }
    } finally {
      setEnrolling(false);
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

  if (loading) {
    return (
      <div className="min-h-screen bg-[#131722] flex items-center justify-center">
        <div className="text-[#787B86]">Loading course...</div>
      </div>
    );
  }

  if (!course) {
    return (
      <div className="min-h-screen bg-[#131722] flex items-center justify-center">
        <div className="text-center">
          <p className="text-[#787B86] mb-4">Course not found</p>
          <Link
            to="/learn"
            className="text-[#2962FF] hover:underline"
          >
            Back to Courses
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#131722]">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-[#2962FF]/10 to-[#089981]/10 border-b border-[#2A2E39]">
        <div className="max-w-7xl mx-auto px-4 py-12">
          <Link
            to="/learn"
            className="text-[#2962FF] hover:underline mb-4 inline-block"
          >
            ← Back to Courses
          </Link>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left: Course Info */}
            <div className="lg:col-span-2">
              <div className="flex items-center gap-3 mb-4">
                <span className={`px-3 py-1 rounded text-sm border
                                ${getDifficultyBadgeColor(course.difficulty)}`}>
                  {course.difficulty}
                </span>
                {course.is_premium && (
                  <span className="px-3 py-1 rounded text-sm border
                               bg-[#2962FF]/20 text-[#2962FF] border-[#2962FF]/30">
                    Premium
                  </span>
                )}
              </div>

              <h1 className="text-4xl font-bold text-[#D1D4DC] mb-4">
                {course.title}
              </h1>

              <p className="text-lg text-[#D1D4DC] mb-6 leading-relaxed">
                {course.description}
              </p>

              <div className="flex items-center gap-6 text-[#787B86]">
                <div className="flex items-center gap-2">
                  <span>📚</span>
                  <span>{course.total_lessons} lessons</span>
                </div>
                <div className="flex items-center gap-2">
                  <span>⏱️</span>
                  <span>{formatDuration(course.duration_minutes)}</span>
                </div>
                {course.completion_percentage > 0 && (
                  <div className="flex items-center gap-2">
                    <span>✓</span>
                    <span>{course.completion_percentage}% complete</span>
                  </div>
                )}
              </div>
            </div>

            {/* Right: CTA Card */}
            <div className="lg:col-span-1">
              <div className="bg-[#1E222D] border border-[#2A2E39] rounded-lg p-6 sticky top-4">
                {/* Progress */}
                {course.completion_percentage > 0 ? (
                  <>
                    <div className="mb-6">
                      <div className="flex justify-between text-sm text-[#787B86] mb-2">
                        <span>Your Progress</span>
                        <span>{course.completion_percentage}%</span>
                      </div>
                      <div className="w-full bg-[#2A2E39] rounded-full h-3">
                        <div
                          className="bg-[#2962FF] h-3 rounded-full transition-all"
                          style={{ width: `${course.completion_percentage}%` }}
                        ></div>
                      </div>
                      <p className="text-sm text-[#787B86] mt-2">
                        {course.completed_lessons} of {course.total_lessons} lessons completed
                      </p>
                    </div>

                    <button
                      onClick={() => {
                        // Find first incomplete lesson or last lesson
                        const incompleteLessons = course.lessons.filter(l => !l.is_completed);
                        const nextLesson = incompleteLessons[0] || course.lessons[0];
                        navigate(`/learn/lesson/${nextLesson.slug}`);
                      }}
                      className="w-full bg-[#2962FF] text-white py-3 rounded-lg
                               hover:bg-[#1E53E5] transition-colors font-medium mb-3"
                    >
                      Continue Learning
                    </button>

                    {course.has_certificate && (
                      <div className="p-3 bg-[#089981]/20 border border-[#089981]/30 rounded-lg">
                        <p className="text-[#089981] text-sm font-medium text-center">
                          🏆 Certificate Earned!
                        </p>
                      </div>
                    )}
                  </>
                ) : (
                  <>
                    <p className="text-[#D1D4DC] mb-4 text-center">
                      Start your learning journey today
                    </p>
                    <button
                      onClick={handleEnroll}
                      disabled={enrolling}
                      className="w-full bg-[#2962FF] text-white py-3 rounded-lg
                               hover:bg-[#1E53E5] transition-colors font-medium
                               disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {enrolling ? 'Enrolling...' : 'Start Course'}
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Lessons List */}
      <div className="max-w-7xl mx-auto px-4 py-12">
        <h2 className="text-2xl font-bold text-[#D1D4DC] mb-6">Course Content</h2>

        <div className="space-y-3">
          {course.lessons.map((lesson, index) => (
            <div
              key={lesson.id}
              className="bg-[#1E222D] border border-[#2A2E39] rounded-lg
                       hover:border-[#3A3E49] transition-all"
            >
              <Link
                to={`/learn/lesson/${lesson.slug}`}
                className="block p-4"
              >
                <div className="flex items-start gap-4">
                  {/* Lesson Number */}
                  <div className={`flex-shrink-0 w-10 h-10 rounded-full
                                flex items-center justify-center font-bold ${
                    lesson.is_completed
                      ? 'bg-[#089981]/20 text-[#089981]'
                      : 'bg-[#2A2E39] text-[#787B86]'
                  }`}>
                    {lesson.is_completed ? '✓' : index + 1}
                  </div>

                  {/* Lesson Info */}
                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-[#D1D4DC] mb-1">
                          {lesson.title}
                        </h3>
                        <div className="flex items-center gap-3 text-sm text-[#787B86]">
                          <span>{lesson.content_type}</span>
                          <span>•</span>
                          <span>{lesson.duration_minutes} min</span>
                          {lesson.is_premium && (
                            <>
                              <span>•</span>
                              <span className="text-[#2962FF]">Premium</span>
                            </>
                          )}
                        </div>
                      </div>

                      {/* Play Icon */}
                      <div className="text-[#2962FF] text-2xl">
                        ▶
                      </div>
                    </div>

                    {/* User Progress for this lesson */}
                    {lesson.user_progress && (
                      <div className="mt-3 pt-3 border-t border-[#2A2E39]">
                        <div className="flex items-center justify-between text-sm">
                          <div className="flex items-center gap-4">
                            {lesson.user_progress.quiz_score !== null && (
                              <span className={`font-medium ${
                                lesson.user_progress.quiz_score >= 70
                                  ? 'text-[#089981]'
                                  : 'text-[#FF9800]'
                              }`}>
                                Quiz: {lesson.user_progress.quiz_score}%
                              </span>
                            )}
                            <span className="text-[#787B86]">
                              {lesson.user_progress.time_spent_minutes} min spent
                            </span>
                          </div>
                          <div className="text-[#787B86]">
                            {lesson.user_progress.progress_percentage}% complete
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </Link>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default CourseDetail;
