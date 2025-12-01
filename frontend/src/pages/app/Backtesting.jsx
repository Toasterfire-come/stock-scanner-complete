import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  Play, 
  Bot, 
  User, 
  TrendingUp, 
  TrendingDown, 
  BarChart2, 
  Target,
  Clock,
  DollarSign,
  AlertCircle,
  CheckCircle,
  Loader2,
  ChevronDown,
  Calendar,
  Code,
  Sparkles,
  RefreshCw
} from 'lucide-react';
import { toast } from 'sonner';
import { 
  chatRefineStrategy, 
  createBacktest, 
  runBacktest,
  summarizeStrategy,
  generateStrategyCode 
} from '../../api/backtestingApi';
import SEO from '../../components/SEO';

const CATEGORIES = [
  { value: 'day_trading', label: 'Day Trading', description: 'Intraday strategies, quick entries/exits' },
  { value: 'swing_trading', label: 'Swing Trading', description: 'Hold for days to weeks' },
  { value: 'long_term', label: 'Long Term', description: 'Hold for months to years' }
];

const EXAMPLE_PROMPTS = [
  "Buy when the 20-day SMA crosses above the 50-day SMA, sell when it crosses below",
  "Enter when RSI drops below 30 and exit when it rises above 70",
  "Buy on a breakout above the 52-week high with 2% stop loss",
  "Enter when price is 10% below the 200-day moving average, exit at 5% profit"
];

export default function Backtesting() {
  // Chat State
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Hi! I'm your AI trading strategy assistant. Describe your trading strategy idea and I'll help you refine it. When you're ready, we can test it against historical data.\n\nFor example, you could say:\n- \"Buy when RSI is oversold and price is above the 200-day moving average\"\n- \"Enter on a golden cross (50 SMA crossing above 200 SMA)\"\n\nWhat strategy would you like to develop?"
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Backtest Configuration
  const [category, setCategory] = useState('swing_trading');
  const [symbol, setSymbol] = useState('AAPL');
  const [startDate, setStartDate] = useState(() => {
    const d = new Date();
    d.setFullYear(d.getFullYear() - 1);
    return d.toISOString().split('T')[0];
  });
  const [endDate, setEndDate] = useState(() => new Date().toISOString().split('T')[0]);
  const [initialCapital, setInitialCapital] = useState(10000);

  // Backtest Results
  const [backtestResults, setBacktestResults] = useState(null);
  const [isRunningBacktest, setIsRunningBacktest] = useState(false);
  const [strategyReady, setStrategyReady] = useState(false);
  const [generatedCode, setGeneratedCode] = useState('');
  const [showCode, setShowCode] = useState(false);

  // Auto-scroll to bottom of chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setIsLoading(true);

    // Add user message to chat
    const newMessages = [...messages, { role: 'user', content: userMessage }];
    setMessages(newMessages);

    try {
      const conversationHistory = newMessages.map(m => ({
        role: m.role,
        content: m.content
      }));

      const result = await chatRefineStrategy(userMessage, conversationHistory, category);

      if (result.success) {
        setMessages([...newMessages, { role: 'assistant', content: result.response }]);
        
        // Check if strategy seems ready (user indicates they're done or AI suggests testing)
        const lowerResponse = result.response.toLowerCase();
        const lowerMessage = userMessage.toLowerCase();
        if (
          lowerMessage.includes('ready') || 
          lowerMessage.includes('test it') ||
          lowerMessage.includes('run backtest') ||
          lowerResponse.includes('ready to test') ||
          lowerResponse.includes('run the backtest')
        ) {
          setStrategyReady(true);
        }
      } else {
        setMessages([...newMessages, { 
          role: 'assistant', 
          content: `I apologize, but I encountered an error: ${result.error}. Please try again.`
        }]);
        toast.error('Chat error: ' + result.error);
      }
    } catch (error) {
      toast.error('Failed to send message');
      setMessages([...newMessages, { 
        role: 'assistant', 
        content: 'Sorry, I encountered an error. Please try again.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRunBacktest = async () => {
    if (messages.length < 2) {
      toast.error('Please describe your strategy first');
      return;
    }

    setIsRunningBacktest(true);
    setBacktestResults(null);

    try {
      // First, summarize the strategy
      const conversationHistory = messages.map(m => ({
        role: m.role,
        content: m.content
      }));

      toast.info('Summarizing your strategy...');
      const summaryResult = await summarizeStrategy(conversationHistory);
      
      if (!summaryResult.success) {
        throw new Error(summaryResult.error || 'Failed to summarize strategy');
      }

      const strategySummary = summaryResult.summary;
      
      // Add summary to chat
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `📋 **Strategy Summary:**\n\n${strategySummary}\n\n🔄 Generating trading code and running backtest...`
      }]);

      // Generate code
      toast.info('Generating trading code...');
      const codeResult = await generateStrategyCode(strategySummary, category);
      
      if (!codeResult.success) {
        throw new Error(codeResult.error || 'Failed to generate code');
      }

      setGeneratedCode(codeResult.generated_code);

      // Create and run backtest
      toast.info('Running backtest...');
      const createResult = await createBacktest({
        name: `Strategy - ${new Date().toLocaleDateString()}`,
        strategyText: strategySummary,
        category,
        symbols: [symbol],
        startDate,
        endDate,
        initialCapital
      });

      if (!createResult.success) {
        throw new Error(createResult.error || 'Failed to create backtest');
      }

      // Run the backtest
      const runResult = await runBacktest(createResult.backtest_id);

      if (!runResult.success) {
        throw new Error(runResult.error || 'Backtest execution failed');
      }

      setBacktestResults(runResult.results);
      toast.success('Backtest completed!');

      // Add results message to chat
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `✅ **Backtest Complete!**\n\nTotal Return: ${runResult.results.total_return?.toFixed(2)}%\nWin Rate: ${runResult.results.win_rate?.toFixed(1)}%\nTotal Trades: ${runResult.results.total_trades}\nSharpe Ratio: ${runResult.results.sharpe_ratio?.toFixed(2)}\n\nCheck the results panel for detailed metrics.`
      }]);

    } catch (error) {
      toast.error(error.message);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `❌ **Backtest Failed**\n\n${error.message}\n\nPlease refine your strategy and try again.`
      }]);
    } finally {
      setIsRunningBacktest(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const insertExamplePrompt = (prompt) => {
    setInputMessage(prompt);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <SEO 
        title="AI Backtesting | Trade Scan Pro" 
        description="Test your trading strategies with AI-powered backtesting"
      />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Sparkles className="h-6 w-6 text-purple-600" />
            AI Strategy Backtester
          </h1>
          <p className="text-gray-600 mt-1">
            Describe your trading strategy in plain English. I'll help you refine it and test it against historical data.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Chat Panel */}
          <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-200 flex flex-col" style={{ height: '70vh' }}>
            {/* Chat Header */}
            <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Bot className="h-5 w-5 text-purple-600" />
                <span className="font-medium text-gray-900">Strategy Assistant</span>
              </div>
              <div className="flex items-center gap-2">
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="text-sm border border-gray-200 rounded-lg px-3 py-1.5 bg-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                  data-testid="category-select"
                >
                  {CATEGORIES.map(cat => (
                    <option key={cat.value} value={cat.value}>{cat.label}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4" data-testid="chat-messages">
              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
                >
                  <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                    msg.role === 'user' ? 'bg-blue-100' : 'bg-purple-100'
                  }`}>
                    {msg.role === 'user' ? (
                      <User className="h-4 w-4 text-blue-600" />
                    ) : (
                      <Bot className="h-4 w-4 text-purple-600" />
                    )}
                  </div>
                  <div className={`flex-1 max-w-[80%] ${msg.role === 'user' ? 'text-right' : ''}`}>
                    <div className={`inline-block px-4 py-2 rounded-2xl ${
                      msg.role === 'user' 
                        ? 'bg-blue-600 text-white rounded-br-md' 
                        : 'bg-gray-100 text-gray-800 rounded-bl-md'
                    }`}>
                      <p className="whitespace-pre-wrap text-sm">{msg.content}</p>
                    </div>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex gap-3">
                  <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center">
                    <Bot className="h-4 w-4 text-purple-600" />
                  </div>
                  <div className="bg-gray-100 rounded-2xl rounded-bl-md px-4 py-2">
                    <Loader2 className="h-4 w-4 animate-spin text-gray-500" />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Example Prompts */}
            {messages.length <= 2 && (
              <div className="px-4 pb-2">
                <p className="text-xs text-gray-500 mb-2">Try an example:</p>
                <div className="flex flex-wrap gap-2">
                  {EXAMPLE_PROMPTS.slice(0, 2).map((prompt, idx) => (
                    <button
                      key={idx}
                      onClick={() => insertExamplePrompt(prompt)}
                      className="text-xs px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-700 transition-colors"
                    >
                      {prompt.substring(0, 40)}...
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Input Area */}
            <div className="p-4 border-t border-gray-200">
              <div className="flex gap-2">
                <textarea
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Describe your trading strategy..."
                  className="flex-1 resize-none border border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  rows={2}
                  disabled={isLoading}
                  data-testid="chat-input"
                />
                <div className="flex flex-col gap-2">
                  <button
                    onClick={handleSendMessage}
                    disabled={!inputMessage.trim() || isLoading}
                    className="px-4 py-2 bg-purple-600 text-white rounded-xl hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                    data-testid="send-button"
                  >
                    <Send className="h-4 w-4" />
                  </button>
                  <button
                    onClick={handleRunBacktest}
                    disabled={messages.length < 2 || isRunningBacktest}
                    className="px-4 py-2 bg-green-600 text-white rounded-xl hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                    data-testid="run-backtest-button"
                  >
                    {isRunningBacktest ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Play className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Configuration & Results Panel */}
          <div className="space-y-4">
            {/* Backtest Configuration */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
              <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Target className="h-4 w-4 text-gray-600" />
                Backtest Settings
              </h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Symbol</label>
                  <input
                    type="text"
                    value={symbol}
                    onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="AAPL"
                    data-testid="symbol-input"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
                    <input
                      type="date"
                      value={startDate}
                      onChange={(e) => setStartDate(e.target.value)}
                      className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
                      data-testid="start-date-input"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                    <input
                      type="date"
                      value={endDate}
                      onChange={(e) => setEndDate(e.target.value)}
                      className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
                      data-testid="end-date-input"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Initial Capital</label>
                  <div className="relative">
                    <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <input
                      type="number"
                      value={initialCapital}
                      onChange={(e) => setInitialCapital(Number(e.target.value))}
                      className="w-full border border-gray-200 rounded-lg pl-9 pr-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
                      data-testid="capital-input"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Results */}
            {backtestResults && (
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4" data-testid="backtest-results">
                <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <BarChart2 className="h-4 w-4 text-gray-600" />
                  Backtest Results
                </h3>
                
                <div className="space-y-3">
                  {/* Total Return */}
                  <div className="flex justify-between items-center py-2 border-b border-gray-100">
                    <span className="text-sm text-gray-600">Total Return</span>
                    <span className={`font-semibold ${backtestResults.total_return >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {backtestResults.total_return >= 0 ? '+' : ''}{backtestResults.total_return?.toFixed(2)}%
                    </span>
                  </div>

                  {/* Win Rate */}
                  <div className="flex justify-between items-center py-2 border-b border-gray-100">
                    <span className="text-sm text-gray-600">Win Rate</span>
                    <span className={`font-semibold ${backtestResults.win_rate >= 50 ? 'text-green-600' : 'text-amber-600'}`}>
                      {backtestResults.win_rate?.toFixed(1)}%
                    </span>
                  </div>

                  {/* Total Trades */}
                  <div className="flex justify-between items-center py-2 border-b border-gray-100">
                    <span className="text-sm text-gray-600">Total Trades</span>
                    <span className="font-semibold text-gray-900">{backtestResults.total_trades}</span>
                  </div>

                  {/* Winning/Losing Trades */}
                  <div className="flex justify-between items-center py-2 border-b border-gray-100">
                    <span className="text-sm text-gray-600">Win/Loss</span>
                    <span className="font-semibold">
                      <span className="text-green-600">{backtestResults.winning_trades}</span>
                      <span className="text-gray-400">/</span>
                      <span className="text-red-600">{backtestResults.losing_trades}</span>
                    </span>
                  </div>

                  {/* Sharpe Ratio */}
                  <div className="flex justify-between items-center py-2 border-b border-gray-100">
                    <span className="text-sm text-gray-600">Sharpe Ratio</span>
                    <span className={`font-semibold ${backtestResults.sharpe_ratio >= 1 ? 'text-green-600' : 'text-amber-600'}`}>
                      {backtestResults.sharpe_ratio?.toFixed(2)}
                    </span>
                  </div>

                  {/* Max Drawdown */}
                  <div className="flex justify-between items-center py-2 border-b border-gray-100">
                    <span className="text-sm text-gray-600">Max Drawdown</span>
                    <span className="font-semibold text-red-600">
                      {backtestResults.max_drawdown?.toFixed(2)}%
                    </span>
                  </div>

                  {/* Profit Factor */}
                  <div className="flex justify-between items-center py-2 border-b border-gray-100">
                    <span className="text-sm text-gray-600">Profit Factor</span>
                    <span className={`font-semibold ${backtestResults.profit_factor >= 1.5 ? 'text-green-600' : 'text-amber-600'}`}>
                      {backtestResults.profit_factor?.toFixed(2)}
                    </span>
                  </div>

                  {/* Composite Score */}
                  <div className="flex justify-between items-center py-2 bg-gray-50 rounded-lg px-3 mt-2">
                    <span className="text-sm font-medium text-gray-700">Strategy Score</span>
                    <span className={`text-lg font-bold ${
                      backtestResults.composite_score >= 60 ? 'text-green-600' : 
                      backtestResults.composite_score >= 40 ? 'text-amber-600' : 'text-red-600'
                    }`}>
                      {backtestResults.composite_score?.toFixed(0)}/100
                    </span>
                  </div>
                </div>

                {/* View Code Button */}
                {generatedCode && (
                  <button
                    onClick={() => setShowCode(!showCode)}
                    className="mt-4 w-full flex items-center justify-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm text-gray-700 transition-colors"
                  >
                    <Code className="h-4 w-4" />
                    {showCode ? 'Hide Code' : 'View Generated Code'}
                    <ChevronDown className={`h-4 w-4 transition-transform ${showCode ? 'rotate-180' : ''}`} />
                  </button>
                )}
              </div>
            )}

            {/* Generated Code */}
            {showCode && generatedCode && (
              <div className="bg-gray-900 rounded-xl shadow-sm border border-gray-700 p-4">
                <h3 className="font-semibold text-white mb-3 flex items-center gap-2">
                  <Code className="h-4 w-4" />
                  Generated Strategy Code
                </h3>
                <pre className="text-xs text-gray-300 overflow-x-auto whitespace-pre-wrap font-mono">
                  {generatedCode}
                </pre>
              </div>
            )}

            {/* Tips */}
            {!backtestResults && (
              <div className="bg-purple-50 rounded-xl p-4">
                <h3 className="font-medium text-purple-900 mb-2 flex items-center gap-2">
                  <Sparkles className="h-4 w-4" />
                  Tips
                </h3>
                <ul className="text-sm text-purple-800 space-y-2">
                  <li>• Be specific about entry and exit conditions</li>
                  <li>• Mention stop-loss or take-profit levels</li>
                  <li>• Describe which indicators to use</li>
                  <li>• Click Run Backtest when ready to test</li>
                </ul>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
