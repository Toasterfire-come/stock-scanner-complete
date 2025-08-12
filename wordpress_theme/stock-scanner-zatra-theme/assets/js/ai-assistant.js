/**
 * AI-Powered Trading Assistant
 * Provides intelligent help and guidance without backend modifications
 */

class TradingAssistant {
    constructor() {
        this.isOpen = false;
        this.conversationHistory = [];
        this.knowledgeBase = this.initializeKnowledgeBase();
        this.init();
    }

    init() {
        this.createAssistantUI();
        this.bindEvents();
        this.loadPersonalizedGreeting();
    }

    createAssistantUI() {
        const assistantHTML = `
            <div id="trading-assistant" class="trading-assistant">
                <div class="assistant-toggle" id="assistantToggle">
                    <div class="assistant-avatar">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="assistant-pulse"></div>
                </div>
                
                <div class="assistant-chat" id="assistantChat">
                    <div class="chat-header">
                        <div class="assistant-info">
                            <div class="assistant-avatar-small">
                                <i class="fas fa-robot"></i>
                            </div>
                            <div class="assistant-details">
                                <h4>Trading Assistant</h4>
                                <span class="status">Online • Ready to help</span>
                            </div>
                        </div>
                        <button class="close-chat" id="closeChat">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    
                    <div class="chat-messages" id="chatMessages">
                        <div class="welcome-message">
                            <div class="message assistant-message">
                                <div class="message-content">
                                    <p>👋 Hi! I'm your AI Trading Assistant. I can help you with:</p>
                                    <ul>
                                        <li>📊 Understanding stock metrics</li>
                                        <li>🔍 Navigating the platform</li>
                                        <li>📈 Market analysis basics</li>
                                        <li>💡 Trading strategies</li>
                                    </ul>
                                    <p>What would you like to know?</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="quick-actions">
                        <button class="quick-action" data-action="explain-pe">What's P/E ratio?</button>
                        <button class="quick-action" data-action="how-screener">How to use screener?</button>
                        <button class="quick-action" data-action="market-hours">Market hours?</button>
                    </div>
                    
                    <div class="chat-input">
                        <input type="text" id="chatInput" placeholder="Ask me anything about trading..." maxlength="500">
                        <button id="sendMessage" disabled>
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', assistantHTML);
    }

    bindEvents() {
        const toggle = document.getElementById('assistantToggle');
        const closeBtn = document.getElementById('closeChat');
        const chatInput = document.getElementById('chatInput');
        const sendBtn = document.getElementById('sendMessage');
        const quickActions = document.querySelectorAll('.quick-action');

        toggle.addEventListener('click', () => this.toggleChat());
        closeBtn.addEventListener('click', () => this.closeChat());
        
        chatInput.addEventListener('input', (e) => {
            sendBtn.disabled = e.target.value.trim().length === 0;
        });
        
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !sendBtn.disabled) {
                this.sendMessage();
            }
        });
        
        sendBtn.addEventListener('click', () => this.sendMessage());
        
        quickActions.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.target.dataset.action;
                this.handleQuickAction(action);
            });
        });
    }

    toggleChat() {
        const chat = document.getElementById('assistantChat');
        this.isOpen = !this.isOpen;
        
        if (this.isOpen) {
            chat.classList.add('open');
            document.getElementById('chatInput').focus();
        } else {
            chat.classList.remove('open');
        }
    }

    closeChat() {
        this.isOpen = false;
        document.getElementById('assistantChat').classList.remove('open');
    }

    sendMessage() {
        const input = document.getElementById('chatInput');
        const message = input.value.trim();
        
        if (!message) return;
        
        this.addMessage(message, 'user');
        input.value = '';
        document.getElementById('sendMessage').disabled = true;
        
        // Show typing indicator
        this.showTyping();
        
        // Process message and respond
        setTimeout(() => {
            this.hideTyping();
            const response = this.generateResponse(message);
            this.addMessage(response, 'assistant');
        }, 1000 + Math.random() * 2000);
    }

    addMessage(content, type) {
        const messagesContainer = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        if (type === 'assistant') {
            messageDiv.innerHTML = `
                <div class="message-avatar">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="message-content">${content}</div>
            `;
        } else {
            messageDiv.innerHTML = `
                <div class="message-content">${content}</div>
            `;
        }
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        // Store in conversation history
        this.conversationHistory.push({ type, content, timestamp: Date.now() });
    }

    showTyping() {
        const messagesContainer = document.getElementById('chatMessages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message assistant-message typing-indicator';
        typingDiv.id = 'typingIndicator';
        typingDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        
        messagesContainer.appendChild(typingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    hideTyping() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    handleQuickAction(action) {
        const responses = {
            'explain-pe': "The P/E (Price-to-Earnings) ratio compares a company's stock price to its earnings per share. A lower P/E might indicate an undervalued stock, while a higher P/E could suggest growth expectations. Generally, P/E ratios between 15-25 are considered reasonable for most stocks.",
            'how-screener': "The Stock Screener lets you filter stocks by various criteria like market cap, P/E ratio, volume, and sector. Start by setting your preferred ranges, then click 'Apply Filters' to see matching stocks. You can save your favorite screening criteria for future use!",
            'market-hours': "US stock markets are open Monday-Friday, 9:30 AM to 4:00 PM ET. Pre-market trading runs 4:00-9:30 AM, and after-hours trading continues until 8:00 PM. Remember that liquidity is typically lower outside regular hours."
        };
        
        this.addMessage(responses[action], 'assistant');
    }

    generateResponse(message) {
        const lowerMessage = message.toLowerCase();
        
        // Financial terms explanations
        if (lowerMessage.includes('p/e') || lowerMessage.includes('price to earnings')) {
            return "The P/E ratio is calculated by dividing the stock price by earnings per share (EPS). It helps you understand how much investors are willing to pay for each dollar of earnings. A P/E of 20 means investors pay $20 for every $1 of annual earnings.";
        }
        
        if (lowerMessage.includes('market cap')) {
            return "Market capitalization is the total value of a company's shares. It's calculated by multiplying the stock price by the number of outstanding shares. Companies are typically categorized as: Small-cap (under $2B), Mid-cap ($2B-$10B), Large-cap ($10B-$200B), and Mega-cap (over $200B).";
        }
        
        if (lowerMessage.includes('volume')) {
            return "Volume represents the number of shares traded during a specific period. High volume often indicates strong investor interest and can signal potential price movements. Low volume might suggest less interest or uncertainty about the stock.";
        }
        
        if (lowerMessage.includes('dividend')) {
            return "Dividends are payments companies make to shareholders from their profits. The dividend yield shows the annual dividend as a percentage of the stock price. Dividend-paying stocks can provide regular income, but companies can cut or eliminate dividends during tough times.";
        }
        
        // Platform navigation
        if (lowerMessage.includes('watchlist')) {
            return "Your watchlist helps you track stocks you're interested in. Click the star icon next to any stock to add it. You can organize multiple watchlists, set price alerts, and quickly access detailed information about your tracked stocks.";
        }
        
        if (lowerMessage.includes('portfolio')) {
            return "The Portfolio section tracks your actual investments. You can add holdings manually, view performance charts, analyze asset allocation, and monitor your overall investment returns. It's your central hub for investment tracking.";
        }
        
        if (lowerMessage.includes('screener') || lowerMessage.includes('filter')) {
            return "The Stock Screener is powerful! Set criteria like market cap, P/E ratio, price range, and sector to find stocks matching your investment strategy. Try starting with broad criteria, then narrow down based on your specific needs.";
        }
        
        // Trading strategies
        if (lowerMessage.includes('strategy') || lowerMessage.includes('invest')) {
            return "Popular investment strategies include: 1) Value investing (buying undervalued stocks), 2) Growth investing (focusing on companies with high growth potential), 3) Dividend investing (income-focused), and 4) Index investing (broad market exposure). Consider your risk tolerance and time horizon.";
        }
        
        if (lowerMessage.includes('risk')) {
            return "Investment risk varies by asset type and strategy. Diversification across sectors and asset classes can help reduce risk. Consider your age, financial goals, and comfort level with volatility. Generally, younger investors can take more risk for potentially higher long-term returns.";
        }
        
        // Market analysis
        if (lowerMessage.includes('bull') || lowerMessage.includes('bear')) {
            return "A bull market is characterized by rising prices and investor optimism, typically with 20%+ gains from recent lows. A bear market involves declining prices and pessimism, usually with 20%+ drops from recent highs. These cycles are normal parts of market behavior.";
        }
        
        if (lowerMessage.includes('sector')) {
            return "Market sectors group similar companies together: Technology, Healthcare, Financial Services, Consumer Goods, Energy, etc. Sector rotation occurs when investors move money between sectors based on economic cycles and growth expectations.";
        }
        
        // Default responses for unmatched queries
        const defaultResponses = [
            "That's an interesting question! While I can help with basic trading concepts and platform navigation, for specific investment advice, consider consulting with a financial advisor. Is there a particular aspect of trading or our platform you'd like to explore?",
            "I'd be happy to help you understand that better! Could you be more specific about what aspect you're curious about? I can explain financial terms, help you navigate our tools, or discuss general market concepts.",
            "Great question! I specialize in helping users understand our platform and basic financial concepts. What specific area would you like me to focus on - stock analysis, platform features, or market fundamentals?",
            "I'm here to help you make the most of Stock Scanner Pro! While I can't provide personalized investment advice, I can explain how our tools work and help you understand key financial concepts. What would be most helpful?"
        ];
        
        return defaultResponses[Math.floor(Math.random() * defaultResponses.length)];
    }

    initializeKnowledgeBase() {
        return {
            financialTerms: {
                'pe_ratio': 'Price-to-Earnings ratio measures valuation',
                'market_cap': 'Total value of company shares',
                'volume': 'Number of shares traded',
                'dividend_yield': 'Annual dividend as percentage of price',
                'beta': 'Measure of stock volatility vs market',
                'rsi': 'Relative Strength Index - momentum indicator',
                'moving_average': 'Average price over specific time period'
            },
            platformFeatures: {
                'dashboard': 'Central hub for market overview',
                'screener': 'Filter stocks by criteria',
                'watchlist': 'Track favorite stocks',
                'portfolio': 'Monitor your investments',
                'news': 'Latest market updates'
            }
        };
    }

    loadPersonalizedGreeting() {
        const hour = new Date().getHours();
        let greeting = "Hello";
        
        if (hour < 12) greeting = "Good morning";
        else if (hour < 17) greeting = "Good afternoon";
        else greeting = "Good evening";
        
        // Check if user is logged in (from WordPress)
        const isLoggedIn = document.body.classList.contains('logged-in');
        if (isLoggedIn) {
            greeting += "! Ready to explore the markets today?";
        } else {
            greeting += "! I can help you learn about our platform and trading basics.";
        }
        
        // Update welcome message if needed
        setTimeout(() => {
            const welcomeMsg = document.querySelector('.welcome-message .message-content p');
            if (welcomeMsg) {
                welcomeMsg.textContent = `👋 ${greeting}`;
            }
        }, 100);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    new TradingAssistant();
});

// CSS Styles for the AI Assistant
const assistantStyles = `
<style>
.trading-assistant {
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 1000;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.assistant-toggle {
    width: 60px;
    height: 60px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
    transition: all 0.3s ease;
    position: relative;
}

.assistant-toggle:hover {
    transform: scale(1.1);
    box-shadow: 0 6px 25px rgba(102, 126, 234, 0.6);
}

.assistant-avatar {
    color: white;
    font-size: 24px;
}

.assistant-pulse {
    position: absolute;
    top: -2px;
    left: -2px;
    right: -2px;
    bottom: -2px;
    border-radius: 50%;
    border: 2px solid rgba(102, 126, 234, 0.6);
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { transform: scale(1); opacity: 1; }
    100% { transform: scale(1.2); opacity: 0; }
}

.assistant-chat {
    position: absolute;
    bottom: 80px;
    right: 0;
    width: 380px;
    height: 500px;
    background: white;
    border-radius: 16px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
    transform: translateY(20px) scale(0.95);
    opacity: 0;
    visibility: hidden;
    transition: all 0.3s ease;
    display: flex;
    flex-direction: column;
}

.assistant-chat.open {
    transform: translateY(0) scale(1);
    opacity: 1;
    visibility: visible;
}

.chat-header {
    padding: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 16px 16px 0 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.assistant-info {
    display: flex;
    align-items: center;
    gap: 12px;
}

.assistant-avatar-small {
    width: 40px;
    height: 40px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
}

.assistant-details h4 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
}

.assistant-details .status {
    font-size: 12px;
    opacity: 0.9;
}

.close-chat {
    background: none;
    border: none;
    color: white;
    font-size: 18px;
    cursor: pointer;
    padding: 5px;
    border-radius: 4px;
    transition: background 0.2s;
}

.close-chat:hover {
    background: rgba(255, 255, 255, 0.2);
}

.chat-messages {
    flex: 1;
    padding: 20px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.message {
    display: flex;
    gap: 12px;
    max-width: 85%;
}

.user-message {
    align-self: flex-end;
    flex-direction: row-reverse;
}

.user-message .message-content {
    background: #667eea;
    color: white;
    border-radius: 18px 18px 4px 18px;
}

.assistant-message .message-content {
    background: #f1f3f5;
    color: #333;
    border-radius: 18px 18px 18px 4px;
}

.message-content {
    padding: 12px 16px;
    font-size: 14px;
    line-height: 1.4;
}

.message-content ul {
    margin: 8px 0;
    padding-left: 20px;
}

.message-content li {
    margin: 4px 0;
}

.message-avatar {
    width: 32px;
    height: 32px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 14px;
    flex-shrink: 0;
}

.typing-indicator .message-content {
    padding: 16px;
}

.typing-dots {
    display: flex;
    gap: 4px;
}

.typing-dots span {
    width: 8px;
    height: 8px;
    background: #999;
    border-radius: 50%;
    animation: typing 1.4s infinite ease-in-out;
}

.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
    0%, 60%, 100% { transform: translateY(0); }
    30% { transform: translateY(-10px); }
}

.quick-actions {
    padding: 0 20px 10px;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.quick-action {
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 20px;
    padding: 8px 12px;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.2s;
    color: #666;
}

.quick-action:hover {
    background: #667eea;
    color: white;
    border-color: #667eea;
}

.chat-input {
    padding: 20px;
    border-top: 1px solid #e9ecef;
    display: flex;
    gap: 12px;
    align-items: center;
}

.chat-input input {
    flex: 1;
    padding: 12px 16px;
    border: 1px solid #e9ecef;
    border-radius: 24px;
    outline: none;
    font-size: 14px;
    transition: border-color 0.2s;
}

.chat-input input:focus {
    border-color: #667eea;
}

.chat-input button {
    width: 40px;
    height: 40px;
    background: #667eea;
    border: none;
    border-radius: 50%;
    color: white;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
}

.chat-input button:disabled {
    background: #ccc;
    cursor: not-allowed;
}

.chat-input button:not(:disabled):hover {
    background: #5a67d8;
    transform: scale(1.05);
}

@media (max-width: 480px) {
    .assistant-chat {
        width: calc(100vw - 40px);
        height: 400px;
        right: 20px;
    }
    
    .trading-assistant {
        right: 20px;
    }
}
</style>
`;

// Inject styles
document.head.insertAdjacentHTML('beforeend', assistantStyles);