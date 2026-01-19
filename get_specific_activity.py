import os
import asyncio
import json
import time
from datetime import datetime
import requests

host = "https://clob.polymarket.com"
chain_id = 137 # Polygon mainnet


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


def get_user_activity(wallet_address: str, market_condition_ids: list = None) -> list:
    """
    Get activity for a specific user, optionally filtered by market condition IDs.
    
    Args:
        wallet_address: The user's wallet address
        market_condition_ids: Optional list of condition IDs to filter by
    
    Returns:
        List of user activities filtered by markets
    """
    base_url = "https://data-api.polymarket.com/activity"
    
    params = {
        "user": wallet_address
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        activities = response.json()
        
        # Filter by market condition IDs if provided
        if market_condition_ids:
            activities = [
                activity for activity in activities 
                if activity.get('conditionId') in market_condition_ids
            ]
        
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


async def monitor_user_trades(wallet_address: str, market_condition_ids: list, interval: int = 10, 
                             telegram_bot_token: str = None, telegram_chat_id: str = None):
    """
    Continuously monitor user activity.
    
    Args:
        wallet_address: The user's wallet address
        market_condition_ids: List of condition IDs of the markets to monitor (for filtering)
        interval: Time in seconds between checks (default: 10)
        telegram_bot_token: Optional Telegram bot token for notifications
        telegram_chat_id: Optional Telegram chat ID for notifications
    """
    print(f"🚀 Starting activity monitor for wallet: {wallet_address}")
    print(f"📡 Monitoring {len(market_condition_ids)} market(s)")
    print(f"⏱️  Checking every {interval} seconds...")
    if telegram_bot_token and telegram_chat_id:
        print(f"📱 Telegram notifications enabled")
    print("-" * 80)
    
    # Track the last check time as Unix timestamp
    last_check_timestamp = int(time.time())
    
    while True:
        current_timestamp = int(time.time())
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n⏳ [{timestamp_str}] Fetching user activity...")
        
        # Get activities already filtered by market condition IDs
        activities = get_user_activity(wallet_address, market_condition_ids)
        
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
                        if activity_timestamp > last_check_timestamp:
                            new_activities.append(activity)
                    except (ValueError, TypeError) as e:
                        print(f"⚠️  Warning: Could not parse timestamp: {activity_timestamp}")
                        continue
            
            if new_activities:
                print(f"🆕 Found {len(new_activities)} new activity(s)!")
                
                # Send Telegram notification if configured
                if telegram_bot_token and telegram_chat_id:
                    telegram_message = f"🆕 <b>New Activity Alert!</b>\n\n"
                    telegram_message += f"Wallet: <code>{wallet_address}</code>\n"
                    telegram_message += f"Found {len(new_activities)} new activity(s)\n\n"
                
                for activity in new_activities:
                    activity_id = activity.get('id')
                    
                    print(f"\n  🆔 Activity ID: {activity_id}")
                    print(f"  📊 Market: {activity.get('title')}")
                    print(f"  🎯 Outcome: {activity.get('outcome')}")
                    
                    size = float(activity.get('size', 0))
                    price = float(activity.get('price', 0))
                    value = size * price
                    
                    print(f"  💰 Size: {size} shares @ ${price}")
                    print(f"  📈 Side: {activity.get('side')}")
                    print(f"  💸 Value: ${value:.2f}")
                    
                    if 'timestamp' in activity:
                        # Convert Unix timestamp to readable format
                        readable_time = datetime.fromtimestamp(int(activity.get('timestamp'))).strftime("%Y-%m-%d %H:%M:%S")
                        print(f"  ⏰ Timestamp: {readable_time} ({activity.get('timestamp')})")
                    if 'type' in activity:
                        print(f"  🏷️  Type: {activity.get('type')}")
                    print("-" * 40)
                    
                    # Add to Telegram message
                    if telegram_bot_token and telegram_chat_id:
                        telegram_message += f"━━━━━━━━━━━━━━━━━━\n"
                        telegram_message += f"📊 <b>Market:</b> {activity.get('title', 'N/A')}\n"
                        telegram_message += f"🎯 <b>Outcome:</b> {activity.get('outcome', 'N/A')}\n"
                        telegram_message += f"💰 <b>Size:</b> {size} shares @ ${price}\n"
                        telegram_message += f"📈 <b>Side:</b> {activity.get('side', 'N/A')}\n"
                        telegram_message += f"💸 <b>Value:</b> ${value:.2f}\n"
                        if 'timestamp' in activity:
                            telegram_message += f"⏰ <b>Time:</b> {readable_time}\n"
                
                # Send the Telegram notification
                if telegram_bot_token and telegram_chat_id:
                    send_telegram_message(telegram_bot_token, telegram_chat_id, telegram_message)
            else:
                print(f"✅ No new activities (total: {len(activities)} activities tracked)")
        else:
            print("❌ No activities found")
        
        # Update last check timestamp to current time
        last_check_timestamp = current_timestamp
        
        # Wait before next check
        await asyncio.sleep(interval)


async def main():
    """Main entry point - monitor user trades continuously"""
    
    # Configuration
    wallet = "0x37e4728b3c4607fb2b3b205386bb1d1fb1a8c991"  # Target user's wallet
    
    # Telegram configuration (optional)
    telegram_bot_token = "8479150225:AAFp17cedT3sL8EO-5Ns8y2WyO4pU9XlHJE"
    telegram_chat_id = "-5280096124"
    
    # Get markets from tags
    tag_ids = ["82", "306"]  # Tag IDs to monitor
    print("🔍 Fetching markets from tags...")
    markets = get_markets_by_tags(tag_ids, limit=1000)
    
    # Extract condition IDs from markets
    market_condition_ids = [market['condition_id'] for market in markets if market['condition_id']]
    
    print(f"\n{'='*80}")
    print(f"✅ Found {len(markets)} total markets")
    print(f"🎯 Monitoring {len(market_condition_ids)} markets with condition IDs")
    print(f"{'='*80}\n")
    
    # Display all markets being monitored
    for i, market in enumerate(markets, 1):
        print(f"{i}. {market['question']}")
    print()
    
    check_interval = 10  # seconds
    
    # Start monitoring with Telegram notifications
    await monitor_user_trades(
        wallet, 
        market_condition_ids, 
        check_interval,
        telegram_bot_token=telegram_bot_token,
        telegram_chat_id=telegram_chat_id
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nShutting down trade monitor gracefully...")
    except Exception as e:
        print(f"Fatal error: {e}")
        raise