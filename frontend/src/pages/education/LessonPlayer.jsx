// app/frontend/src/pages/education/LessonPlayer.jsx
/**
 * Lesson Player Component
 * Phase 7 Implementation - TradeScanPro
 * TradingView-inspired design
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../../api/client';
import ReactMarkdown from 'react-markdown';
import InfoTooltip from './InfoTooltip';

const LessonPlayer = () => {
  const { lessonSlug } = useParams();
  const navigate = useNavigate();
  
  const [lesson, setLesson] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showQuiz, setShowQuiz] = useState(false);
  const [quizAnswers, setQuizAnswers] = useState([]);
  const [quizResult, setQuizResult] = useState(null);
  const [timeSpent, setTimeSpent] = useState(0);

  useEffect(() => {
    fetchLesson();
    startLesson();
    
    // Track time spent
    const interval = setInterval(() => {
      setTimeSpent(prev => prev + 1);
    }, 1000);
    
    return () => {
      clearInterval(interval);
      updateProgress();
    };
  }, [lessonSlug]);

  const fetchLesson = async () => {
    try {
      const response = await api.get(`/api/education/lessons/${lessonSlug}/`);
      setLesson(response.data);
      
      // Initialize quiz answers
      if (response.data.quiz_questions) {
        setQuizAnswers(new Array(response.data.quiz_questions.length).fill(null));
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching lesson:', error);
      setLoading(false);
    }
  };

  const startLesson = async () => {
    try {
      await axios.post(`/api/education/lessons/${lessonSlug}/start/`);
    } catch (error) {
      console.error('Error starting lesson:', error);
    }
  };

  const updateProgress = async () => {
    if (timeSpent === 0) return;
    
    try {
      await axios.patch(`/api/education/lessons/${lessonSlug}/update-progress/`, {
        time_spent_seconds: timeSpent
      });
    } catch (error) {
      console.error('Error updating progress:', error);
    }
  };

  const handleCompleteLesson = async () => {
    try {
      await axios.post(`/api/education/lessons/${lessonSlug}/complete/`);
      
      // Navigate to next lesson if available
      if (lesson.next_lesson) {
        navigate(`/learn/lesson/${lesson.next_lesson.slug}`);
      } else {
        navigate(`/learn/${lesson.course}`);
      }
    } catch (error) {
      console.error('Error completing lesson:', error);
    }
  };

  const handleQuizSubmit = async () => {
    try {
      const response = await axios.post(
        `/api/education/lessons/${lessonSlug}/submit-quiz/`,
        { answers: quizAnswers }
      );
      
      setQuizResult(response.data);
    } catch (error) {
      console.error('Error submitting quiz:', error);
    }
  };

  const handleQuizAnswer = (questionIndex, answerIndex) => {
    const newAnswers = [...quizAnswers];
    newAnswers[questionIndex] = answerIndex;
    setQuizAnswers(newAnswers);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#131722] flex items-center justify-center">
        <div className="text-[#787B86]">Loading lesson...</div>
      </div>
    );
  }

  if (!lesson) {
    return (
      <div className="min-h-screen bg-[#131722] flex items-center justify-center">
        <div className="text-[#787B86]">Lesson not found</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#131722]">
      {/* Lesson Header */}
      <div className="bg-[#1E222D] border-b border-[#2A2E39] py-4 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <p className="text-sm text-[#787B86] mb-1">{lesson.course_title}</p>
              <h1 className="text-xl font-semibold text-[#D1D4DC]">{lesson.title}</h1>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-[#787B86]">
                ⏱️ {Math.floor(timeSpent / 60)}:{(timeSpent % 60).toString().padStart(2, '0')}
              </span>
              {lesson.user_progress?.completed && (
                <span className="px-3 py-1 bg-[#089981]/20 text-[#089981] rounded-full text-sm">
                  ✓ Completed
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Video Player */}
        {lesson.video_url && (
          <div className="mb-8 bg-[#1E222D] rounded-lg overflow-hidden">
            <div className="aspect-video">
              <iframe
                src={lesson.video_url}
                className="w-full h-full"
                allowFullScreen
              ></iframe>
            </div>
          </div>
        )}

        {/* Lesson Content */}
        <div className="bg-[#1E222D] border border-[#2A2E39] rounded-lg p-8 mb-8">
          <div className="prose prose-invert max-w-none">
            <ReactMarkdown>{lesson.content}</ReactMarkdown>
          </div>

          {/* Key Takeaways */}
          {lesson.key_takeaways && lesson.key_takeaways.length > 0 && (
            <div className="mt-8 pt-8 border-t border-[#2A2E39]">
              <h3 className="text-lg font-semibold text-[#D1D4DC] mb-4">
                🎯 Key Takeaways
              </h3>
              <ul className="space-y-2">
                {lesson.key_takeaways.map((takeaway, index) => (
                  <li key={index} className="text-[#D1D4DC] flex items-start">
                    <span className="text-[#2962FF] mr-2">•</span>
                    {takeaway}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Related Terms */}
          {lesson.related_terms && lesson.related_terms.length > 0 && (
            <div className="mt-8 pt-8 border-t border-[#2A2E39]">
              <h3 className="text-lg font-semibold text-[#D1D4DC] mb-4">
                📚 Related Terms
              </h3>
              <div className="flex flex-wrap gap-2">
                {lesson.related_terms.map((term) => (
                  <InfoTooltip key={term.id} term={term}>
                    <span className="px-3 py-1 bg-[#2A2E39] text-[#D1D4DC] rounded-full text-sm
                                   hover:bg-[#3A3E49] cursor-help border-b border-dotted
                                   border-[#787B86]">
                      {term.term}
                    </span>
                  </InfoTooltip>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Quiz Section */}
        {lesson.quiz_questions && lesson.quiz_questions.length > 0 && (
          <div className="bg-[#1E222D] border border-[#2A2E39] rounded-lg p-8 mb-8">
            <h2 className="text-xl font-semibold text-[#D1D4DC] mb-6">
              📝 Test Your Knowledge
            </h2>

            {!showQuiz && !quizResult ? (
              <button
                onClick={() => setShowQuiz(true)}
                className="bg-[#2962FF] text-white px-6 py-3 rounded-lg
                         hover:bg-[#1E53E5] transition-colors font-medium"
              >
                Start Quiz
              </button>
            ) : quizResult ? (
              <div>
                <div className={`p-4 rounded-lg mb-6 ${
                  quizResult.passed
                    ? 'bg-[#089981]/20 border border-[#089981]/30'
                    : 'bg-[#F23645]/20 border border-[#F23645]/30'
                }`}>
                  <h3 className={`text-lg font-semibold mb-2 ${
                    quizResult.passed ? 'text-[#089981]' : 'text-[#F23645]'
                  }`}>
                    {quizResult.passed ? '✓ Passed!' : '✗ Keep Practicing'}
                  </h3>
                  <p className="text-[#D1D4DC]">
                    Score: {quizResult.score}% ({quizResult.correct}/{quizResult.total} correct)
                  </p>
                </div>
                <button
                  onClick={() => {
                    setQuizResult(null);
                    setShowQuiz(true);
                    setQuizAnswers(new Array(lesson.quiz_questions.length).fill(null));
                  }}
                  className="bg-[#2A2E39] text-[#D1D4DC] px-6 py-2 rounded-lg
                           hover:bg-[#3A3E49] transition-colors"
                >
                  Retry Quiz
                </button>
              </div>
            ) : (
              <div className="space-y-6">
                {lesson.quiz_questions.map((question, qIndex) => (
                  <div key={qIndex} className="border-b border-[#2A2E39] pb-6 last:border-0">
                    <p className="text-[#D1D4DC] font-medium mb-4">
                      {qIndex + 1}. {question.question}
                    </p>
                    <div className="space-y-2">
                      {question.options.map((option, oIndex) => (
                        <label
                          key={oIndex}
                          className={`flex items-center p-3 rounded-lg cursor-pointer
                                   transition-colors ${
                            quizAnswers[qIndex] === oIndex
                              ? 'bg-[#2962FF]/20 border border-[#2962FF]/30'
                              : 'bg-[#2A2E39] hover:bg-[#3A3E49]'
                          }`}
                        >
                          <input
                            type="radio"
                            name={`question-${qIndex}`}
                            checked={quizAnswers[qIndex] === oIndex}
                            onChange={() => handleQuizAnswer(qIndex, oIndex)}
                            className="mr-3"
                          />
                          <span className="text-[#D1D4DC]">{option}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                ))}

                <button
                  onClick={handleQuizSubmit}
                  disabled={quizAnswers.includes(null)}
                  className="bg-[#2962FF] text-white px-6 py-3 rounded-lg
                           hover:bg-[#1E53E5] transition-colors font-medium
                           disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Submit Quiz
                </button>
              </div>
            )}
          </div>
        )}

        {/* Navigation */}
        <div className="flex justify-between items-center">
          <button
            onClick={() => lesson.previous_lesson 
              ? navigate(`/learn/lesson/${lesson.previous_lesson.slug}`)
              : navigate(`/learn/${lesson.course}`)}
            className="px-6 py-2 bg-[#2A2E39] text-[#D1D4DC] rounded-lg
                     hover:bg-[#3A3E49] transition-colors"
          >
            ← {lesson.previous_lesson ? 'Previous Lesson' : 'Back to Course'}
          </button>

          {!lesson.user_progress?.completed && (
            <button
              onClick={handleCompleteLesson}
              className="px-6 py-3 bg-[#089981] text-white rounded-lg
                       hover:bg-[#067662] transition-colors font-medium"
            >
              Mark as Complete
            </button>
          )}

          {lesson.next_lesson && (
            <button
              onClick={() => navigate(`/learn/lesson/${lesson.next_lesson.slug}`)}
              className="px-6 py-2 bg-[#2962FF] text-white rounded-lg
                       hover:bg-[#1E53E5] transition-colors"
            >
              Next Lesson →
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default LessonPlayer;
