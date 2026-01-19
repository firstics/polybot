# Your first line of Python code
import os
import asyncio
import json
import time
from datetime import datetime
import requests

host = "https://clob.polymarket.com"
chain_id = 137 # Polygon mainnet

def get_markets_by_condition_id(condition_id: str) -> dict:
    """
    Get market by condition ID.
    
    Args:
        condition_id: Condition ID to query
    
    Returns:
        Dictionary with market information or None if not found
    """
    print(f"Fetching market for condition_id: {condition_id}")
    
    try:
        base_url = "https://gamma-api.polymarket.com/markets"
        full_url = f"{base_url}?condition_ids={condition_id}"
        
        response = requests.get(full_url)
        response.raise_for_status()
        markets = response.json()
        
        # Extract market information
        if isinstance(markets, list) and len(markets) > 0:
            market = markets[0]
            market_info = {
                "question": market.get("question"),
                "condition_id": market.get("conditionId"),
                "market_slug": market.get("marketSlug"),
                "title": market.get("title")
            }
            print(f"Found market: {market_info.get('title')}")
            return market_info
        elif isinstance(markets, dict):
            market_info = {
                "question": markets.get("question"),
                "condition_id": markets.get("conditionId"),
                "market_slug": markets.get("marketSlug"),
                "title": markets.get("title")
            }
            print(f"Found market: {market_info.get('title')}")
            return market_info
        else:
            print(f"No market found for condition_id: {condition_id}")
            return None
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching market: {e}")
        return None

def get_markets_by_tags(tag_ids: list, limit: int = 50) -> list:
    """
    Get markets for each tag ID individually and return a combined list.
    
    Args:
        tag_ids: List of tag IDs to query
        limit: Maximum number of markets per tag (default: 50)
    
    Returns:
        List of dictionaries with market question and condition ID
    """
    all_markets = []
    
    for tag_id in tag_ids:
        print(f"Fetching markets for tag_id: {tag_id}")
        
        try:
            response = requests.get(
                "https://gamma-api.polymarket.com/markets",
                params={
                    "tag_id": tag_id,
                    "closed": "false",
                    "limit": limit
                }
            )
            response.raise_for_status()
            markets = response.json()
            
            # Extract question and condition ID for each market
            for market in markets:
                all_markets.append({
                    "question": market.get("question"),
                    "condition_id": market.get("conditionId"),
                    "tag_id": tag_id
                })
            
            print(f"Found {len(markets)} markets for tag_id: {tag_id}")
            
            # Optional: Add a small delay to avoid rate limiting
            time.sleep(0.1)
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching markets for tag_id {tag_id}: {e}")
            continue
    
    return all_markets


def get_user_activity(wallet_address: str) -> list:
    """
    Get all activity for a specific user.
    
    Args:
        wallet_address: The user's wallet address
    
    Returns:
        List of user activities
    """
    base_url = "https://data-api.polymarket.com/activity"
    
    params = {
        "user": wallet_address,
        "limit": 1,
        "sortBy": "TIMESTAMP",
        "sortDirection": "DESC"
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        activities = response.json()
        
        return activities
    except requests.exceptions.RequestException as e:
        print(f"Error fetching user activity: {e}")
        return []


def send_telegram_message(bot_token: str, chat_id: str, message: str) -> bool:
    """
    Send a message via Telegram Bot API.
    
    Args:
        bot_token: Telegram bot token
        chat_id: Chat ID to send message to
        message: Message text to send
    
    Returns:
        True if message sent successfully, False otherwise
    """
    base_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(
            base_url,
            headers={"Content-Type": "application/json"},
            json=payload
        )
        response.raise_for_status()
        print(f"📤 Telegram message sent successfully")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending Telegram message: {e}")
        return False


async def monitor_user_trades(wallet_address: str, interval: int = 10, 
                             telegram_bot_token: str = None, telegram_chat_id: str = None,
                             wallet_name: str = None):
    """
    Continuously monitor user activity for a single wallet.
    
    Args:
        wallet_address: The user's wallet address
        interval: Time in seconds between checks (default: 10)
        telegram_bot_token: Optional Telegram bot token for notifications
        telegram_chat_id: Optional Telegram chat ID for notifications
        wallet_name: Optional name/label for the wallet (for easier identification)
    """
    wallet_label = wallet_name if wallet_name else wallet_address[:10]
    print(f"🚀 Starting activity monitor for wallet [{wallet_label}]: {wallet_address}")
    print(f"⏱️  Checking every {interval} seconds...")
    if telegram_bot_token and telegram_chat_id:
        print(f"📱 Telegram notifications enabled")
    print("-" * 80)
    
    # Track the last check time as Unix timestamp
    # Initialize to 0 to get all activities on first run
    last_check_timestamp = 0
    
    while True:
        current_timestamp = int(time.time())
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n⏳ [{wallet_label}] [{timestamp_str}] Fetching user activity...")
        
        # Get all user activities
        activities = get_user_activity(wallet_address)
        
        if activities:
            
            # Filter for new activities based on Unix timestamp
            new_activities = []
            for activity in activities:
                activity_timestamp = activity.get('timestamp')
                if activity_timestamp:
                    try:
                        # Convert to int if it's a string
                        if isinstance(activity_timestamp, str):
                            activity_timestamp = int(activity_timestamp)
                        
                        # Only include activities newer than our last check
                        if activity_timestamp != last_check_timestamp:
                            activity_timestamp = last_check_timestamp
                            new_activities.append(activity)
                    except (ValueError, TypeError) as e:
                        print(f"⚠️  Warning: Could not parse timestamp: {activity_timestamp}")
                        continue
            
            if new_activities:
                print(f"🆕 [{activity.get('name', 'N/A')}] Found {len(new_activities)} new activity(s)!")
                
                # Track the latest timestamp from new activities
                latest_activity_timestamp = last_check_timestamp

                for activity in new_activities:
                    activity_id = activity.get('id')
                    activity_name = activity.get('name', 'N/A')
                    print(f"\n  [{activity_name}] 🆔 Activity ID: {activity_id}")
                    print(f"  [{activity_name}] 📊 Market: {activity.get('title')}")
                    print(f"  [{activity_name}] 🎯 Outcome: {activity.get('outcome')}")

                    size = float(activity.get('size', 0))
                    price = float(activity.get('price', 0))
                    value = size * price

                    print(f"  [{activity_name}] 💰 Size: {size} shares @ ${price}")
                    print(f"  [{activity_name}] 📈 Side: {activity.get('side')}")
                    print(f"  [{activity_name}] 💸 Value: ${value:.2f}")
                    if 'timestamp' in activity:
                        # Convert Unix timestamp to readable format
                        activity_timestamp_int = int(activity.get('timestamp'))
                        readable_time = datetime.fromtimestamp(activity_timestamp_int).strftime("%Y-%m-%d %H:%M:%S")
                        print(f"  [{activity_name}] ⏰ Timestamp: {readable_time} ({activity.get('timestamp')})")

                        # Track the latest timestamp
                        if activity_timestamp_int > latest_activity_timestamp:
                            latest_activity_timestamp = activity_timestamp_int
                    
                    if 'type' in activity:
                        print(f"  [{activity_name}] 🏷️  Type: {activity.get('type')}")
                    print("-" * 40)
                    
                    # Send individual Telegram message for each activity
                    if telegram_bot_token and telegram_chat_id:
                        telegram_message = f"🆕 <b>New Activity Alert!</b>\n\n"
                        telegram_message += f"<b>Wallet:</b> {activity.get('name', 'N/A')}\n"
                        telegram_message += f"📊 <b>Market:</b> {activity.get('title', 'N/A')}\n"
                        telegram_message += f"👀 <b>Type:</b> {activity.get('type', 'N/A')}\n"
			            telegram_message += f"🎯 <b>Outcome:</b> {activity.get('outcome', 'N/A')}\n"
                        telegram_message += f"💰 <b>Size:</b> {size} shares @ ${price}\n"
                        telegram_message += f"📈 <b>Side:</b> {activity.get('side', 'N/A')}\n"
                        telegram_message += f"💸 <b>Value:</b> ${value:.2f}\n"
                        if 'timestamp' in activity:
                            telegram_message += f"⏰ <b>Time:</b> {readable_time}\n"
                        send_telegram_message(telegram_bot_token, telegram_chat_id, telegram_message)
                
                # Update last_check_timestamp to the latest activity timestamp
                print(f"🔄 [{activity_name}] Updating last_check_timestamp from {last_check_timestamp} to {latest_activity_timestamp}")
                last_check_timestamp = latest_activity_timestamp
                
            else:
                print(f"✅ [{activity_name}] No new activities (total: {len(activities)} activities tracked)")
        else:
            print(f"❌ [{activity_name}] No activities found")

        # Wait before next check
        await asyncio.sleep(interval)


async def main():
    """Main entry point - monitor multiple user wallets concurrently"""
    
    # Configuration - List of wallet addresses to monitor
    wallets = [
        "0x37e4728b3c4607fb2b3b205386bb1d1fb1a8c991",
        "0x006cc834cc092684f1b56626e23bedb3835c16ea"
        # Add more wallet addresses here as needed:
        # "0x1234567890abcdef1234567890abcdef12345678",
        # "0xabcdef1234567890abcdef1234567890abcdef12",
    ]
    
    # Telegram configuration (optional) - shared across all wallets
    telegram_bot_token = "8479150225:AAFp17cedT3sL8EO-5Ns8y2WyO4pU9XlHJE"
    telegram_chat_id = "-5280096124"
    
    check_interval = 1  # seconds
    
    print("=" * 80)
    print(f"🌟 Starting Multi-Wallet Monitor")
    print(f"📊 Monitoring {len(wallets)} wallet(s)")
    print("=" * 80)
    
    # Create monitoring tasks for each wallet
    tasks = []
    for wallet_address in wallets:
        task = asyncio.create_task(
            monitor_user_trades(
                wallet_address=wallet_address,
                interval=check_interval,
                telegram_bot_token=telegram_bot_token,
                telegram_chat_id=telegram_chat_id,
                wallet_name=None
            )
        )
        tasks.append(task)
    
    # Run all monitoring tasks concurrently
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nShutting down trade monitor gracefully...")
    except Exception as e:
        print(f"Fatal error: {e}")
        raise