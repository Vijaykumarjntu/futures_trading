import argparse
import logging
import sys
from typing import Dict, Any
from decimal import Decimal, InvalidOperation
from binance_client import BinanceFuturesClient
from config import Config
from datetime import datetime

logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG for more details
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'binance_debug_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OrderCLI:
    """Command Line Interface for placing orders"""
    
    def __init__(self):
        try:
            Config.validate_config()
            self.client = BinanceFuturesClient(Config.API_KEY, Config.SECRET_KEY)
        except Exception as e:
            logger.error(f"Failed to initialize client: {e}")
            print(f"❌ Initialization error: {e}")
            print("Please check your API credentials in .env file")
            sys.exit(1)
    
    def validate_inputs(self, symbol: str, side: str, order_type: str, 
                       quantity: str, price: str = None) -> tuple:
        """Validate and parse all input parameters"""
        errors = []
        
        # Validate symbol
        if not symbol or len(symbol) < 6:
            errors.append("Symbol must be at least 6 characters (e.g., BTCUSDT)")
        
        # Validate side
        if side.upper() not in ['BUY', 'SELL']:
            errors.append("Side must be either 'BUY' or 'SELL'")
        
        # Validate order type
        if order_type.upper() not in ['MARKET', 'LIMIT']:
            errors.append("Order type must be either 'MARKET' or 'LIMIT'")
        
        # Validate quantity
        try:
            qty = Decimal(quantity)
            if qty <= 0:
                errors.append("Quantity must be greater than 0")
        except (InvalidOperation, ValueError):
            errors.append("Quantity must be a valid number")
        
        # Validate price for LIMIT orders
        price_val = None
        if order_type.upper() == 'LIMIT':
            if not price:
                errors.append("Price is required for LIMIT orders")
            else:
                try:
                    price_val = Decimal(price)
                    if price_val <= 0:
                        errors.append("Price must be greater than 0")
                except (InvalidOperation, ValueError):
                    errors.append("Price must be a valid number")
        
        if errors:
            raise ValueError("\n".join(errors))
        
        return (
            symbol.upper(),
            side.upper(),
            order_type.upper(),
            float(qty),
            float(price_val) if price_val else None
        )
    
    def format_order_response(self, response: Dict[str, Any]) -> str:
        """Format order response for display"""
        if 'code' in response and response['code'] != 200:
            return f"❌ Error: {response.get('msg', 'Unknown error')}"
        
        output_lines = [
            "=" * 50,
            "✅ ORDER PLACED SUCCESSFULLY",
            "=" * 50,
            f"Order ID: {response.get('orderId', 'N/A')}",
            f"Symbol: {response.get('symbol', 'N/A')}",
            f"Side: {response.get('side', 'N/A')}",
            f"Type: {response.get('type', 'N/A')}",
            f"Status: {response.get('status', 'N/A')}",
            f"Quantity: {response.get('origQty', 'N/A')}",
            f"Executed Quantity: {response.get('executedQty', '0')}",
            f"Price: {response.get('price', 'N/A')}",
        ]
        
        if 'avgPrice' in response and float(response['avgPrice']) > 0:
            output_lines.append(f"Average Price: {response['avgPrice']}")
        
        output_lines.append(f"Time: {response.get('updateTime', 'N/A')}")
        output_lines.append("=" * 50)
        
        return "\n".join(output_lines)
    
    def place_order_interactive(self):
        """Interactive order placement"""
        print("\n" + "="*50)
        print("BINANCE FUTURES TESTNET ORDER PLACER")
        print("="*50)
        
        try:
            # Test connection first
            print("🔍 Testing API connection...")
            if not self.client.test_connection():
                print("❌ Cannot connect to Binance API. Check credentials and network.")
                return
            
            print("✅ Connected to Binance Futures Testnet")
            
            # Get user inputs
            symbol = input("\nEnter trading pair (e.g., BTCUSDT): ").strip()
            side = input("Enter side (BUY/SELL): ").strip()
            order_type = input("Enter order type (MARKET/LIMIT): ").strip()
            quantity = input("Enter quantity: ").strip()
            
            price = None
            if order_type.upper() == 'LIMIT':
                price = input("Enter price: ").strip()
            
            # Validate and place order
            symbol, side, order_type, qty, price_val = self.validate_inputs(
                symbol, side, order_type, quantity, price
            )
            
            print("\n" + "="*50)
            print("📋 ORDER SUMMARY")
            print("="*50)
            print(f"Symbol: {symbol}")
            print(f"Side: {side}")
            print(f"Type: {order_type}")
            print(f"Quantity: {qty}")
            if price_val:
                print(f"Price: {price_val}")
            print("="*50)
            
            confirm = input("\nConfirm order? (yes/no): ").strip().lower()
            if confirm != 'yes':
                print("Order cancelled.")
                return
            
            # Place the order
            print("\n🚀 Placing order...")
            response = self.client.place_order(
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=qty,
                price=price_val
            )
            
            # Display results
            print("\n" + self.format_order_response(response))
            
        except ValueError as e:
            print(f"\n❌ Validation Error: {e}")
        except KeyboardInterrupt:
            print("\n\nOrder cancelled by user.")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            logger.error(f"Order placement failed: {e}")
    
    def run_from_args(self, args):
        """Run from command line arguments"""
        try:
            # Test connection
            if not self.client.test_connection():
                print("❌ Cannot connect to Binance API")
                sys.exit(1)
            
            # Validate inputs
            symbol, side, order_type, qty, price_val = self.validate_inputs(
                args.symbol, args.side, args.order_type, args.quantity, args.price
            )
            
            # Display order summary
            print("\n" + "="*50)
            print("📋 ORDER REQUEST SUMMARY")
            print("="*50)
            print(f"Symbol: {symbol}")
            print(f"Side: {side}")
            print(f"Type: {order_type}")
            print(f"Quantity: {qty}")
            if price_val:
                print(f"Price: {price_val}")
            print("="*50)
            
            # Place the order
            print("\n🚀 Placing order...")
            response = self.client.place_order(
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=qty,
                price=price_val
            )
            
            # Display results
            print("\n" + self.format_order_response(response))
            
        except Exception as e:
            print(f"❌ Error: {e}")
            logger.error(f"Order placement failed: {e}")
            sys.exit(1)

def main():
    """Main entry point"""
    # Setup argument parser
    parser = argparse.ArgumentParser(description='Binance Futures Testnet Order Placer')
    
    # Create subparsers for different modes
    subparsers = parser.add_subparsers(dest='mode', help='Run mode')
    
    # Interactive mode
    subparsers.add_parser('interactive', help='Run in interactive mode')
    
    # CLI mode
    cli_parser = subparsers.add_parser('place', help='Place an order directly')
    cli_parser.add_argument('symbol', help='Trading pair (e.g., BTCUSDT)')
    cli_parser.add_argument('side', choices=['BUY', 'SELL'], help='Order side')
    cli_parser.add_argument('order_type', choices=['MARKET', 'LIMIT'], help='Order type')
    cli_parser.add_argument('quantity', type=float, help='Order quantity')
    cli_parser.add_argument('--price', type=float, help='Price (required for LIMIT orders)')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('binance_orders.log'),
            logging.StreamHandler()
        ]
    )
    
    # Run the CLI
    cli = OrderCLI()
    
    if args.mode == 'interactive' or not args.mode:
        cli.place_order_interactive()
    elif args.mode == 'place':
        cli.run_from_args(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()