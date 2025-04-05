@mcp.tool()
async def get_portfolio_summary() -> str:
    """
    Get a comprehensive summary of the portfolio including performance metrics and allocation.
    """
    try:
        # Get account and positions information
        account = trading_client.get_account()
        positions = trading_client.get_all_positions()
        
        if not positions:
            return "No open positions found. Portfolio is entirely in cash."
        
        # Calculate portfolio statistics
        portfolio_value = float(account.portfolio_value)
        cash = float(account.cash)
        equity_value = float(account.equity)
        
        # Calculate sector/stock allocation
        allocation = []
        total_investment = sum(float(position.market_value) for position in positions)
        
        for position in positions:
            symbol = position.symbol
            market_value = float(position.market_value)
            percentage = (market_value / portfolio_value) * 100
            allocation.append((symbol, market_value, percentage))
        
        # Sort allocation by percentage (descending)
        allocation.sort(key=lambda x: x[2], reverse=True)
        
        # Format the portfolio summary
        summary = f"""
Portfolio Summary
----------------
Total Portfolio Value: ${portfolio_value:.2f}
Cash: ${cash:.2f} ({(cash/portfolio_value)*100:.2f}% of portfolio)
Equity: ${equity_value:.2f}

Portfolio Allocation:
| Symbol | Value | % of Portfolio |
|--------|-------|----------------|
"""
        for symbol, value, percentage in allocation:
            summary += f"| {symbol} | ${value:.2f} | {percentage:.2f}% |\n"
        
        # Calculate diversification metrics
        num_positions = len(positions)
        top_holding_pct = allocation[0][2] if allocation else 0
        
        summary += f"""
Diversification Metrics:
- Number of Positions: {num_positions}
- Top Holding: {allocation[0][0] if allocation else "None"} ({top_holding_pct:.2f}%)
- Cash Position: {(cash/portfolio_value)*100:.2f}%
"""
        
        return summary
        
    except Exception as e:
        return f"Error generating portfolio summary: {str(e)}"

@mcp.tool()
async def analyze_risk() -> str:
    """
    Perform a basic risk analysis of the current portfolio.
    """
    try:
        positions = trading_client.get_all_positions()
        
        if not positions:
            return "No open positions found. No risk analysis available."
        
        # Get historical data for risk calculations
        symbols = [position.symbol for position in positions]
        
        start_time = datetime.now() - timedelta(days=30)  # Use 30 days for volatility
        
        request_params = StockBarsRequest(
            symbol_or_symbols=symbols,
            timeframe=TimeFrame.Day,
            start=start_time
        )
        
        all_bars = stock_client.get_stock_bars(request_params)
        
        # Calculate volatility and risk metrics for each position
        risk_analysis = "Portfolio Risk Analysis\n"
        risk_analysis += "----------------------\n"
        risk_analysis += "| Symbol | Volatility (30-day) | Position Value | % of Portfolio |\n"
        risk_analysis += "|--------|---------------------|----------------|----------------|\n"
        
        account = trading_client.get_account()
        portfolio_value = float(account.portfolio_value)
        
        high_risk_positions = []
        
        for position in positions:
            symbol = position.symbol
            market_value = float(position.market_value)
            portfolio_pct = (market_value / portfolio_value) * 100
            
            # Calculate volatility
            if symbol in all_bars and len(all_bars[symbol]) > 5:
                prices = [bar.close for bar in all_bars[symbol]]
                daily_returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
                volatility = (sum((r - sum(daily_returns) / len(daily_returns)) ** 2 for r in daily_returns) / len(daily_returns)) ** 0.5 * 100
                
                # Flag high-risk positions (high volatility and significant position)
                if volatility > 3 and portfolio_pct > 10:
                    high_risk_positions.append((symbol, volatility, portfolio_pct))
            else:
                volatility = "Insufficient data"
            
            risk_analysis += f"| {symbol} | {volatility if isinstance(volatility, str) else f'{volatility:.2f}%'} | ${market_value:.2f} | {portfolio_pct:.2f}% |\n"
        
        # Add risk summary
        risk_analysis += "\nRisk Summary:\n"
        
        if high_risk_positions:
            risk_analysis += "High-Risk Positions (High volatility + Large allocation):\n"
            for symbol, vol, pct in high_risk_positions:
                risk_analysis += f"- {symbol}: {vol:.2f}% volatility, {pct:.2f}% of portfolio\n"
        else:
            risk_analysis += "No high-risk positions identified based on volatility and allocation.\n"
        
        # Portfolio concentration risk
        top_positions = sorted([(position.symbol, float(position.market_value) / portfolio_value * 100) 
                               for position in positions], key=lambda x: x[1], reverse=True)
        
        top_3_concentration = sum(pct for _, pct in top_positions[:3])
        
        if top_3_concentration > 50:
            risk_analysis += f"\nConcentration Risk: High - Top 3 positions represent {top_3_concentration:.2f}% of portfolio\n"
        else:
            risk_analysis += f"\nConcentration Risk: Moderate/Low - Top 3 positions represent {top_3_concentration:.2f}% of portfolio\n"
        
        return risk_analysis
        
    except Exception as e:
        return f"Error performing risk analysis: {str(e)}"