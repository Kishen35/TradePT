// AI Integration Module for TradePT Extension
// Connects extension data collection with backend AI endpoints

class AIIntegration {
    constructor() {
        this.backendUrl = 'http://localhost:8000'; // Update for production
        this.userId = 1; // Default user ID for now
        this.sessionId = null;
    }

    // Prepare comprehensive context from extension data + Deriv API
    async prepareAIContext() {
        const context = {
            // Extension scraped data
            current_balance: state.balance,
            current_symbol: state.currentSymbol,
            win_rate: state.winRate,
            live_positions: state.positions,
            recent_trades: state.recentTrades,

            // Page context
            current_page: this.getCurrentPageType(),
            timestamp: new Date().toISOString(),

            // Additional Deriv API data (if needed)
            deriv_data: await this.fetchDerivData()
        };

        return context;
    }

    // Determine what page user is on for context
    getCurrentPageType() {
        const url = window.location.href;
        if (url.includes('/dtrader')) return 'trading';
        if (url.includes('/reports/profit')) return 'profit_analysis';
        if (url.includes('/reports/statement')) return 'transaction_history';
        if (url.includes('/cashier')) return 'cashier';
        return 'general';
    }

    // Fetch additional data from backend Deriv endpoints if needed
    async fetchDerivData() {
        try {
            const [balance, portfolio] = await Promise.all([
                fetch(`${this.backendUrl}/deriv/balance`).then(r => r.json()),
                fetch(`${this.backendUrl}/deriv/portfolio`).then(r => r.json())
            ]);

            return { balance, portfolio };
        } catch (error) {
            console.log('Could not fetch additional Deriv data:', error);
            return null;
        }
    }

    // Send message to AI with full context
    async sendMessageToAI(userMessage, messageType = 'general') {
        try {
            const context = await this.prepareAIContext();

            const payload = {
                user_id: this.userId,
                message: userMessage,
                session_id: this.sessionId,
                user_context: {
                    ...context,
                    message_type: messageType,
                    // User profile data (from questionnaire)
                    experience_level: this.getUserProfile()?.experience_level || 'beginner'
                }
            };

            // Debug: Log the context being sent
            console.log('🔍 AI Request Context:', {
                message: userMessage,
                context: context,
                payload: payload
            });

            // Try direct fetch first, fallback to background script if CORS fails
            let response;
            try {
                response = await fetch(`${this.backendUrl}/ai/chat`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload)
                });
            } catch (corsError) {
                console.log('Direct fetch failed, trying background script:', corsError);
                response = await this.makeBackgroundRequest(`${this.backendUrl}/ai/chat`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: payload
                });
            }

            if (!response.ok) {
                throw new Error(`AI request failed: ${response.status}`);
            }

            const result = await response.json();
            console.log('🤖 AI Response:', result);
            
            this.sessionId = result.session_id; // Maintain session

            return result.response;
        } catch (error) {
            console.error('AI request failed:', error);
            return "I'm having trouble connecting to the AI service. Please try again.";
        }
    }

    // Get trading insights based on current data
    async getTradingInsights() {
        try {
            const userLevel = this.getUserProfile()?.experience_level || 'beginner';

            let response;
            try {
                response = await fetch(
                    `${this.backendUrl}/ai/insights/${this.userId}?days=7&user_level=${userLevel}`,
                    {
                        method: 'GET',
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    }
                );
            } catch (corsError) {
                console.log('Direct fetch failed, trying background script:', corsError);
                response = await this.makeBackgroundRequest(
                    `${this.backendUrl}/ai/insights/${this.userId}?days=7&user_level=${userLevel}`,
                    {
                        method: 'GET',
                        headers: { 'Content-Type': 'application/json' }
                    }
                );
            }

            if (!response.ok) {
                throw new Error(`Insights request failed: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Insights request failed:', error);
            return null;
        }
    }

    // Make request via background script (CORS bypass)
    async makeBackgroundRequest(url, options) {
        return new Promise((resolve, reject) => {
            chrome.runtime.sendMessage({
                action: 'apiRequest',
                url: url,
                method: options.method,
                headers: options.headers,
                body: options.body
            }, (response) => {
                if (chrome.runtime.lastError) {
                    reject(new Error(chrome.runtime.lastError.message));
                    return;
                }

                if (response.success) {
                    // Create a Response-like object
                    resolve({
                        ok: true,
                        status: 200,
                        json: async () => response.data
                    });
                } else {
                    reject(new Error(response.error));
                }
            });
        });
    }

    // Generate contextual lesson suggestions
    async suggestLessons() {
        try {
            const userLevel = this.getUserProfile()?.experience_level || 'beginner';

            const response = await fetch(
                `${this.backendUrl}/ai/suggest-topic/${this.userId}?skill_level=${userLevel}`,
                {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                }
            );

            if (!response.ok) {
                throw new Error(`Topic suggestion failed: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Topic suggestion failed:', error);
            return null;
        }
    }

    // Get user profile from storage
    getUserProfile() {
        try {
            return JSON.parse(localStorage.getItem('tradept_user_profile'));
        } catch {
            return null;
        }
    }

    // Smart message categorization for better AI responses
    categorizeMessage(message) {
        const msg = message.toLowerCase();

        if (msg.includes('position') || msg.includes('trade') || msg.includes('buy') || msg.includes('sell')) {
            return 'trading_action';
        }
        if (msg.includes('risk') || msg.includes('loss') || msg.includes('profit')) {
            return 'risk_management';
        }
        if (msg.includes('learn') || msg.includes('explain') || msg.includes('how')) {
            return 'education';
        }
        if (msg.includes('analysis') || msg.includes('insight') || msg.includes('performance')) {
            return 'analysis';
        }

        return 'general';
    }
}

// Export for use in content.js
window.AIIntegration = AIIntegration;