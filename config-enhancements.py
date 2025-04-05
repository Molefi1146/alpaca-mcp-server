# At the beginning of the file, add these imports
import os
import sys
import json
import logging
from dotenv import load_dotenv
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("alpaca-mcp")

# Load environment variables
load_dotenv()

# Configuration handling
def load_config() -> Dict[str, Any]:
    """Load configuration from environment variables with fallbacks"""
    config = {
        "api_key": os.getenv("API_KEY_ID"),
        "api_secret": os.getenv("API_SECRET_KEY"),
        "paper_trading": os.getenv("PAPER_TRADING", "true").lower() == "true",
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
        "max_days_history": int(os.getenv("MAX_DAYS_HISTORY", "30")),
        "default_order_limit": int(os.getenv("DEFAULT_ORDER_LIMIT", "10")),
    }
    
    # Validate required config
    if not config["api_key"] or not config["api_secret"]:
        logger.error("Alpaca API credentials not found in environment variables")
        raise ValueError("Alpaca API credentials not found in environment variables.")
    
    return config

# Replace the early part of your script with this
# Initialize FastMCP server with metadata for Claude
mcp = FastMCP(
    name="alpaca-trading",
    display_name="Alpaca Trading",
    description="A trading assistant that allows Claude to manage your Alpaca brokerage account, get market data, and place trades."
)

# Load configuration
try:
    config = load_config()
    logger.setLevel(getattr(logging, config["log_level"]))
    logger.info(f"Starting Alpaca MCP server (Paper Trading: {config['paper_trading']})")
except Exception as e:
    logger.error(f"Failed to load configuration: {e}")
    sys.exit(1)

# Initialize trading and data clients
try:
    trading_client = TradingClient(config["api_key"], config["api_secret"], paper=config["paper_trading"])
    stock_client = StockHistoricalDataClient(config["api_key"], config["api_secret"])
    logger.info("Successfully connected to Alpaca API")
except Exception as e:
    logger.error(f"Failed to initialize Alpaca clients: {e}")
    sys.exit(1)