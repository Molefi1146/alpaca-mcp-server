@mcp.tool()
async def get_simple_analysis(symbol: str, days: int = 30) -> str:
    """
    Get a simple market analysis for a stock including moving averages and basic indicators.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT)
        days: Number of trading days to analyze (default: 30)
    """
    try:
        # Get historical data
        start_time = datetime.now() - timedelta(days=days)
        
        request_params = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame.Day,
            start=start_time
        )
        
        bars = stock_client.get_stock_bars(request_params)
        
        if symbol not in bars or not bars[symbol]:
            return f"No historical data found for {symbol} in the last {days} days."
        
        # Extract closing prices
        prices = [bar.close for bar in bars[symbol]]
        dates = [bar.timestamp.date() for bar in bars[symbol]]
        
        if len(prices) < 10:
            return f"Insufficient data for {symbol}. Need at least 10 days of data for analysis."
        
        # Calculate simple moving averages
        sma5 = sum(prices[-5:]) / 5 if len(prices) >= 5 else None
        sma20 = sum(prices[-20:]) / 20 if len(prices) >= 20 else None
        
        # Calculate price change
        price_change = prices[-1] - prices[0]
        percent_change = (price_change / prices[0]) * 100
        
        # Calculate volatility (standard deviation)
        volatility = (sum((price - sum(prices) / len(prices)) ** 2 for price in prices) / len(prices)) ** 0.5
        
        # Current price
        current_price = prices[-1]
        
        # Simple trend detection
        trend = "Uptrend" if prices[-1] > sma20 and sma5 > sma20 and len(prices) >= 20 else \
                "Downtrend" if prices[-1] < sma20 and sma5 < sma20 and len(prices) >= 20 else \
                "Neutral/Consolidating"
        
        # Generate the analysis report
        analysis = f"""
Market Analysis for {symbol} (Past {days} Trading Days)
------------------------------------------------------
Current Price: ${current_price:.2f}
Price Change: ${price_change:.2f} ({percent_change:.2f}%)
Volatility: ${volatility:.2f}

Moving Averages:
- 5-Day SMA: ${sma5:.2f} if sma5 else "Insufficient data"
- 20-Day SMA: ${sma20:.2f} if sma20 else "Insufficient data"

Simple Trend Analysis: {trend}

Market Conditions: {
    "Potentially Overbought" if percent_change > 10 else
    "Potentially Oversold" if percent_change < -10 else
    "Within normal range"
}

Note: This is a simplified analysis and should not be used as the sole basis for investment decisions.
"""
        return analysis
        
    except Exception as e:
        return f"Error performing analysis for {symbol}: {str(e)}"

@mcp.tool()
async def compare_stocks(symbols: str, days: int = 30) -> str:
    """
    Compare multiple stocks over a period.
    
    Args:
        symbols: Comma-separated list of stock ticker symbols (e.g., "AAPL,MSFT,GOOGL")
        days: Number of trading days to compare (default: 30)
    """
    try:
        symbol_list = [s.strip() for s in symbols.split(',')]
        if len(symbol_list) < 2 or len(symbol_list) > 5:
            return "Please provide between 2 and 5 stock symbols to compare."
        
        # Get historical data for each symbol
        start_time = datetime.now() - timedelta(days=days)
        
        request_params = StockBarsRequest(
            symbol_or_symbols=symbol_list,
            timeframe=TimeFrame.Day,
            start=start_time
        )
        
        all_bars = stock_client.get_stock_bars(request_params)
        
        # Prepare comparison results
        comparison = f"Stock Comparison (Last {days} Trading Days)\n"
        comparison += "--------------------------------------\n"
        comparison += "| Symbol | Start Price | Current Price | % Change | Volume (Avg) |\n"
        comparison += "|--------|-------------|---------------|----------|-------------|\n"
        
        for symbol in symbol_list:
            if symbol not in all_bars or not all_bars[symbol]:
                comparison += f"| {symbol} | No data available | - | - | - |\n"
                continue
                
            bars = all_bars[symbol]
            start_price = bars[0].close
            end_price = bars[-1].close
            percent_change = ((end_price - start_price) / start_price) * 100
            avg_volume = sum(bar.volume for bar in bars) / len(bars)
            
            comparison += f"| {symbol} | ${start_price:.2f} | ${end_price:.2f} | {percent_change:.2f}% | {int(avg_volume):,} |\n"
        
        # Determine best and worst performers
        performance = []
        for symbol in symbol_list:
            if symbol in all_bars and all_bars[symbol]:
                bars = all_bars[symbol]
                start_price = bars[0].close
                end_price = bars[-1].close
                percent_change = ((end_price - start_price) / start_price) * 100
                performance.append((symbol, percent_change))
        
        if performance:
            performance.sort(key=lambda x: x[1], reverse=True)
            best = performance[0]
            worst = performance[-1]
            
            comparison += f"\nBest Performer: {best[0]} ({best[1]:.2f}%)\n"
            comparison += f"Worst Performer: {worst[0]} ({worst[1]:.2f}%)\n"
        
        return comparison
        
    except Exception as e:
        return f"Error comparing stocks: {str(e)}"