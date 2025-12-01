// app/frontend/src/pages/education/Glossary.jsx
/**
 * Trading Glossary Component
 * Phase 7 Implementation - TradeScanPro
 * TradingView-inspired A-Z directory
 */

import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../../api/client';

const Glossary = () => {
  const { termSlug } = useParams();
  const [terms, setTerms] = useState([]);
  const [filteredTerms, setFilteredTerms] = useState([]);
  const [selectedTerm, setSelectedTerm] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedLetter, setSelectedLetter] = useState('all');

  const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');
  
  const categories = [
    { value: 'all', label: 'All Categories' },
    { value: 'technical', label: 'Technical Analysis' },
    { value: 'fundamental', label: 'Fundamental Analysis' },
    { value: 'order_types', label: 'Order Types' },
    { value: 'market_structure', label: 'Market Structure' },
    { value: 'risk_management', label: 'Risk Management' },
    { value: 'psychology', label: 'Trading Psychology' },
    { value: 'options', label: 'Options & Derivatives' },
    { value: 'general', label: 'General Trading' },
  ];

  useEffect(() => {
    fetchTerms();
  }, []);

  useEffect(() => {
    if (termSlug && terms.length > 0) {
      const term = terms.find(t => t.slug === termSlug);
      if (term) {
        fetchTermDetail(term.slug);
      }
    }
  }, [termSlug, terms]);

  useEffect(() => {
    filterTerms();
  }, [terms, searchQuery, selectedCategory, selectedLetter]);

  const fetchTerms = async () => {
    try {
      const response = await api.get('/api/education/glossary/');
      setTerms(response.data || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching glossary:', error);
      setTerms([]);
      setLoading(false);
    }
  };

  const fetchTermDetail = async (slug) => {
    try {
      const response = await api.get(`/api/education/glossary/${slug}/`);
      setSelectedTerm(response.data);
      
      // Track view
      await api.post(`/api/education/glossary/${slug}/track-view/`);
    } catch (error) {
      console.error('Error fetching term detail:', error);
    }
  };

  const filterTerms = () => {
    let filtered = [...terms];

    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(term =>
        term.term.toLowerCase().includes(searchQuery.toLowerCase()) ||
        term.definition.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Category filter
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(term => term.category === selectedCategory);
    }

    // Letter filter
    if (selectedLetter !== 'all') {
      filtered = filtered.filter(term =>
        term.term.toUpperCase().startsWith(selectedLetter)
      );
    }

    setFilteredTerms(filtered);
  };

  const groupTermsByLetter = () => {
    const grouped = {};
    
    filteredTerms.forEach(term => {
      const firstLetter = term.term[0].toUpperCase();
      if (!grouped[firstLetter]) {
        grouped[firstLetter] = [];
      }
      grouped[firstLetter].push(term);
    });

    return grouped;
  };

  const groupedTerms = groupTermsByLetter();

  if (loading) {
    return (
      <div className="min-h-screen bg-[#131722] flex items-center justify-center">
        <div className="text-[#787B86]">Loading glossary...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#131722]">
      {/* Header */}
      <div className="bg-[#1E222D] border-b border-[#2A2E39] py-8">
        <div className="max-w-7xl mx-auto px-4">
          <h1 className="text-3xl font-bold text-[#D1D4DC] mb-2">Trading Glossary</h1>
          <p className="text-[#787B86]">
            Learn the language of trading with 200+ terms and definitions
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Sidebar - Filters & Term List */}
          <div className="lg:col-span-1">
            <div className="bg-[#1E222D] border border-[#2A2E39] rounded-lg p-4 sticky top-4">
              {/* Search */}
              <div className="mb-4">
                <input
                  type="text"
                  placeholder="Search terms..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full bg-[#131722] border border-[#2A2E39] rounded-lg px-4 py-2
                           text-[#D1D4DC] placeholder-[#545861]
                           focus:outline-none focus:border-[#2962FF]"
                />
              </div>

              {/* Category Filter */}
              <div className="mb-4">
                <label className="block text-sm text-[#787B86] mb-2">Category</label>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="w-full bg-[#131722] border border-[#2A2E39] rounded-lg px-3 py-2
                           text-[#D1D4DC] text-sm focus:outline-none focus:border-[#2962FF]"
                >
                  {categories.map((cat) => (
                    <option key={cat.value} value={cat.value}>
                      {cat.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Alphabet Navigation */}
              <div className="mb-4">
                <label className="block text-sm text-[#787B86] mb-2">Jump to Letter</label>
                <div className="flex flex-wrap gap-1">
                  <button
                    onClick={() => setSelectedLetter('all')}
                    className={`px-2 py-1 rounded text-sm transition-colors ${
                      selectedLetter === 'all'
                        ? 'bg-[#2962FF] text-white'
                        : 'bg-[#2A2E39] text-[#D1D4DC] hover:bg-[#3A3E49]'
                    }`}
                  >
                    All
                  </button>
                  {alphabet.map((letter) => (
                    <button
                      key={letter}
                      onClick={() => setSelectedLetter(letter)}
                      className={`px-2 py-1 rounded text-sm transition-colors ${
                        selectedLetter === letter
                          ? 'bg-[#2962FF] text-white'
                          : 'bg-[#2A2E39] text-[#D1D4DC] hover:bg-[#3A3E49]'
                      }`}
                    >
                      {letter}
                    </button>
                  ))}
                </div>
              </div>

              {/* Term Count */}
              <p className="text-sm text-[#787B86]">
                {filteredTerms.length} term{filteredTerms.length !== 1 ? 's' : ''} found
              </p>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-2">
            {selectedTerm ? (
              /* Term Detail View */
              <div className="bg-[#1E222D] border border-[#2A2E39] rounded-lg p-8">
                <button
                  onClick={() => {
                    setSelectedTerm(null);
                    window.history.pushState({}, '', '/glossary');
                  }}
                  className="text-[#2962FF] hover:underline mb-6 flex items-center gap-2"
                >
                  ← Back to Glossary
                </button>

                <div className="flex items-start justify-between mb-4">
                  <h2 className="text-3xl font-bold text-[#D1D4DC]">
                    {selectedTerm.term}
                  </h2>
                  <span className="px-3 py-1 bg-[#2962FF]/20 text-[#2962FF] text-sm rounded-full">
                    {categories.find(c => c.value === selectedTerm.category)?.label}
                  </span>
                </div>

                <div className="mb-6">
                  <h3 className="text-sm font-semibold text-[#787B86] mb-2 uppercase">
                    Definition
                  </h3>
                  <p className="text-lg text-[#D1D4DC] leading-relaxed">
                    {selectedTerm.definition}
                  </p>
                </div>

                {selectedTerm.example && (
                  <div className="mb-6 p-4 bg-[#131722] rounded-lg border border-[#2A2E39]">
                    <h3 className="text-sm font-semibold text-[#787B86] mb-2 uppercase">
                      Example
                    </h3>
                    <p className="text-[#D1D4DC] italic">
                      {selectedTerm.example}
                    </p>
                  </div>
                )}

                {selectedTerm.related_terms && selectedTerm.related_terms.length > 0 && (
                  <div className="pt-6 border-t border-[#2A2E39]">
                    <h3 className="text-sm font-semibold text-[#787B86] mb-3 uppercase">
                      Related Terms
                    </h3>
                    <div className="grid grid-cols-2 gap-2">
                      {selectedTerm.related_terms.map((relatedTerm) => (
                        <button
                          key={relatedTerm.id}
                          onClick={() => fetchTermDetail(relatedTerm.slug)}
                          className="p-3 bg-[#2A2E39] text-[#D1D4DC] rounded-lg text-left
                                   hover:bg-[#3A3E49] transition-colors"
                        >
                          {relatedTerm.term}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              /* Term List View */
              <div className="space-y-8">
                {Object.keys(groupedTerms).sort().map((letter) => (
                  <div key={letter} id={`letter-${letter}`}>
                    <h2 className="text-2xl font-bold text-[#D1D4DC] mb-4 pb-2
                                 border-b border-[#2A2E39]">
                      {letter}
                    </h2>
                    <div className="grid grid-cols-1 gap-3">
                      {groupedTerms[letter].map((term) => (
                        <button
                          key={term.id}
                          onClick={() => fetchTermDetail(term.slug)}
                          className="bg-[#1E222D] border border-[#2A2E39] rounded-lg p-4
                                   hover:border-[#3A3E49] hover:bg-[#2A2E39]
                                   transition-all text-left group"
                        >
                          <h3 className="text-lg font-semibold text-[#D1D4DC] mb-1
                                       group-hover:text-[#2962FF]">
                            {term.term}
                          </h3>
                          <p className="text-sm text-[#787B86] line-clamp-2">
                            {term.definition}
                          </p>
                          <div className="flex items-center gap-2 mt-2">
                            <span className="text-xs px-2 py-1 bg-[#2A2E39] text-[#787B86] rounded">
                              {categories.find(c => c.value === term.category)?.label}
                            </span>
                            {term.difficulty && (
                              <span className="text-xs px-2 py-1 bg-[#2A2E39] text-[#787B86] rounded">
                                {term.difficulty}
                              </span>
                            )}
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                ))}

                {filteredTerms.length === 0 && (
                  <div className="text-center py-12">
                    <p className="text-[#787B86]">No terms found matching your criteria.</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Glossary;
