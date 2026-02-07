# Deriv AI Trading Tutor - In-Line Coaching POC

This version introduces **In-Line Decision Support**, placing AI advice exactly where you make your trades.

## New Features
- **In-Line Advice Buttons**: 
    - **Buy Advice**: A new "AI Analysis" button appears right below the 'Buy' button in DTrader. It checks your balance vs. the stake to suggest if it's a safe trade.
    - **Close Advice**: A "Should I close?" button appears below every open position. It analyzes current profit vs. market trends to suggest whether to hold or sell.
- **Decision Support Overlay**: Clicking these buttons opens a focused analysis window with a "Risk Rating" and personalized reasoning.
- **Live Balance Tracking**: The AI reads your account balance in real-time to adjust its risk management advice.

## How it Works
The extension uses a dynamic injection engine that monitors the Deriv DOM. When it finds purchase or close buttons, it attaches the AI advice buttons without breaking the original platform's functionality.

## Future Backend Integration
- **Market Sentiment API**: The "AI Analysis" should fetch real-time RSI, Moving Averages, or News Sentiment to provide accurate "Buy/Hold" ratings.
- **Risk Profile**: Integrate with a user database to understand if the trader is "Conservative" or "Aggressive" to tailor the advice.

## Installation
1. Load the unpacked folder in `chrome://extensions/`.
2. Open `https://app.deriv.com/dtrader`.
3. Look for the dashed red buttons below the 'Buy' and 'Close' actions.
