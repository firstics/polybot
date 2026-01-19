# Polymarket Activity Monitor

A Python application that monitors multiple Polymarket wallet addresses for trading activity and sends real-time notifications via Telegram.

## Features

- 🔄 Monitor multiple wallet addresses concurrently
- 📱 Real-time Telegram notifications for new activities
- 🎯 Track trades, market outcomes, sizes, and values
- ⚡ Efficient polling with timestamp-based tracking
- 🐳 Docker support for easy deployment

## Prerequisites

- Docker and Docker Compose (recommended)
- OR Python 3.13+ with pip

## Configuration

Edit the `main.py` file to configure:

1. **Wallet addresses** to monitor (in the `wallets` list)
2. **Telegram bot token** and **chat ID** for notifications
3. **Check interval** (default: 1 second)

```python
wallets = [
    "0x37e4728b3c4607fb2b3b205386bb1d1fb1a8c991",
    "0x006cc834cc092684f1b56626e23bedb3835c16ea",
    # Add more addresses here
]

telegram_bot_token = "YOUR_BOT_TOKEN"
telegram_chat_id = "YOUR_CHAT_ID"
check_interval = 1  # seconds
```

## Running with Docker (Recommended)

### Build and run with Docker Compose:

```bash
# Build and start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

### Or use Docker directly:

```bash
# Build the image
docker build -t polymarket-monitor .

# Run the container
docker run -d --name polymarket-monitor --restart unless-stopped polymarket-monitor

# View logs
docker logs -f polymarket-monitor

# Stop the container
docker stop polymarket-monitor
docker rm polymarket-monitor
```

## Running with Python

### Install dependencies:

```bash
pip install -r requirements.txt
```

### Run the application:

```bash
python main.py
```

## Project Structure

```
polymarket/
├── main.py              # Main application code
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker image definition
├── docker-compose.yml  # Docker Compose configuration
├── .dockerignore       # Files to exclude from Docker build
└── README.md           # This file
```

## Output Examples

### Console Output:
```
🚀 Starting activity monitor for wallet [0x37e4728b]: 0x37e4728b3c4607fb2b3b205386bb1d1fb1a8c991
⏱️  Checking every 1 seconds...
📱 Telegram notifications enabled
────────────────────────────────────────────────────────────────────────────────

⏳ [0x37e4728b] [2026-01-19 12:00:00] Fetching user activity...
🆕 [UserName] Found 1 new activity(s)!

  [UserName] 🆔 Activity ID: abc123
  [UserName] 📊 Market: Will Bitcoin reach $100k in 2026?
  [UserName] 🎯 Outcome: Yes
  [UserName] 💰 Size: 100.0 shares @ $0.65
  [UserName] 📈 Side: BUY
  [UserName] 💸 Value: $65.00
  [UserName] ⏰ Timestamp: 2026-01-19 12:00:00 (1737244800)
  [UserName] 🏷️  Type: TRADE
```

### Telegram Notification:
```
🆕 New Activity Alert!

Wallet: UserName
📊 Market: Will Bitcoin reach $100k in 2026?
🎯 Outcome: Yes
💰 Size: 100.0 shares @ $0.65
📈 Side: BUY
💸 Value: $65.00
⏰ Time: 2026-01-19 12:00:00
```

## Stopping the Application

### Docker Compose:
```bash
docker-compose down
```

### Docker:
```bash
docker stop polymarket-monitor
```

### Python:
Press `Ctrl+C` to stop gracefully.

## Troubleshooting

### Check logs:
```bash
# Docker Compose
docker-compose logs -f

# Docker
docker logs -f polymarket-monitor
```

### Rebuild after code changes:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## License

MIT License
