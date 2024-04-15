import json
import alpaca_trade_api as tradeapi

# Initialize Alpaca API
alpaca = tradeapi.REST(alpaca_api_key, alpaca_secret_key, base_url='https://paper-api.alpaca.markets')

def lambda_handler(event, context):
    # Parse the request data from TradingView
    data = json.loads(event['body'])

    # Implement your trading strategy logic here
    symbol = data['symbol']
    side = data['strategy']['order_action'].lower()
    quantity = data['strategy']['order_size']

    # Execute trade with Alpaca API
    alpaca.submit_order(symbol, quantity, side, 'market', 'day')

    return {
        'statusCode': 200,
        'body': json.dumps('Trade executed successfully')
    }
