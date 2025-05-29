# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import asyncio
import os
import tempfile
import signal
import sys
import time
from pyrogram import Client
from pyrogram.errors import FloodWait, AuthKeyUnregistered, SessionRevoked
from config import API_ID, API_HASH, BOT_TOKEN

class Bot(Client):

    def __init__(self):
        # Create unique session name with timestamp to avoid conflicts
        session_name = f"techvj_bot_{os.getpid()}_{int(time.time())}"
        session_path = os.path.join(tempfile.gettempdir(), session_name)
        
        super().__init__(
            session_path,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="TechVJ"),
            workers=20,  # Reduced workers to avoid rate limits
            sleep_threshold=30,  # Increased sleep threshold
            max_concurrent_transmissions=5  # Limit concurrent operations
        )
        
        # Track shutdown state
        self.shutdown_requested = False
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print(f"Received signal {signum}. Initiating graceful shutdown...")
        self.shutdown_requested = True
        
        # Create a task to stop the bot if we're in an event loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.graceful_shutdown())
        except:
            pass

    async def graceful_shutdown(self):
        """Perform graceful shutdown"""
        try:
            print("Performing graceful shutdown...")
            await asyncio.sleep(2)  # Give time for current operations to complete
            await self.stop()
            sys.exit(0)
        except Exception as e:
            print(f"Error during graceful shutdown: {e}")
            sys.exit(1)

    async def start(self):
        max_retries = 10
        base_delay = 5
        
        for attempt in range(max_retries):
            if self.shutdown_requested:
                return
                
            try:
                # Clean up any existing session files first
                await self.cleanup_session_files()
                
                print(f"Starting bot (attempt {attempt + 1}/{max_retries})...")
                await super().start()
                print('✅ Bot Started Successfully! Powered By @VJ_Botz')
                
                # Verify bot is working by getting bot info
                me = await self.get_me()
                print(f"✅ Bot authenticated as: @{me.username}")
                
                return
                
            except FloodWait as e:
                wait_time = min(e.value, 300)  # Cap at 5 minutes
                print(f"⚠️ FloodWait: Sleeping for {wait_time} seconds")
                await asyncio.sleep(wait_time)
                
            except (AuthKeyUnregistered, SessionRevoked) as e:
                print(f"❌ Authentication error: {e}")
                print("Bot token may be invalid. Please check BOT_TOKEN.")
                await self.cleanup_session_files()
                raise
                
            except Exception as e:
                print(f"❌ Error starting bot (attempt {attempt + 1}/{max_retries}): {e}")
                
                # Clean up potential lock files
                await self.cleanup_session_files()
                
                if attempt < max_retries - 1:
                    # Exponential backoff with jitter
                    delay = base_delay * (2 ** attempt) + (attempt * 2)
                    delay = min(delay, 300)  # Cap at 5 minutes
                    print(f"⏳ Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    print("❌ Max retries reached. Bot startup failed.")
                    await self.cleanup_session_files()
                    raise

    async def cleanup_session_files(self):
        """Clean up session files that might be causing locks"""
        try:
            # Get all potential session file patterns
            session_patterns = [
                f"{self.name}*",
                "techvj_bot_*",
                "techvj_login_*"
            ]
            
            temp_dir = tempfile.gettempdir()
            
            for pattern in session_patterns:
                # Find files matching pattern
                import glob
                for file_path in glob.glob(os.path.join(temp_dir, pattern)):
                    if any(file_path.endswith(ext) for ext in ['.session', '.session-journal', '.session-wal', '.session-shm']):
                        try:
                            os.remove(file_path)
                            print(f"🧹 Cleaned up: {os.path.basename(file_path)}")
                        except Exception as e:
                            print(f"⚠️ Could not remove {file_path}: {e}")
                            
        except Exception as e:
            print(f"⚠️ Error during session cleanup: {e}")

    async def stop(self, *args):
        """Stop the bot gracefully"""
        try:
            print("🛑 Stopping bot...")
            await super().stop()
            print('👋 Bot Stopped Successfully!')
        except Exception as e:
            print(f"⚠️ Error stopping bot: {e}")
        finally:
            # Clean up session files on stop
            await self.cleanup_session_files()

    async def restart(self):
        """Restart the bot"""
        print("🔄 Restarting bot...")
        await self.stop()
        await asyncio.sleep(5)
        await self.start()

# Health check and monitoring
class BotMonitor:
    def __init__(self, bot):
        self.bot = bot
        self.last_health_check = time.time()
        
    async def health_check(self):
        """Perform periodic health checks"""
        while not self.bot.shutdown_requested:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                if self.bot.is_connected:
                    # Try to get bot info to verify connection
                    await self.bot.get_me()
                    self.last_health_check = time.time()
                    print("💚 Health check: Bot is running normally")
                else:
                    print("💔 Health check: Bot is disconnected")
                    
            except Exception as e:
                print(f"⚠️ Health check failed: {e}")
                
                # If bot has been unhealthy for too long, try to restart
                if time.time() - self.last_health_check > 1800:  # 30 minutes
                    print("🚨 Bot unhealthy for too long, attempting restart...")
                    try:
                        await self.bot.restart()
                        self.last_health_check = time.time()
                    except Exception as restart_error:
                        print(f"❌ Restart failed: {restart_error}")

async def main():
    """Main function with proper error handling"""
    bot = None
    monitor = None
    
    try:
        bot = Bot()
        await bot.start()
        
        # Start health monitoring
        monitor = BotMonitor(bot)
        monitor_task = asyncio.create_task(monitor.health_check())
        
        # Keep the bot running
        print("🤖 Bot is now running. Press Ctrl+C to stop.")
        await asyncio.Event().wait()  # Run forever until interrupted
        
    except KeyboardInterrupt:
        print("\n👋 Keyboard interrupt received. Shutting down...")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if bot:
            await bot.stop()

if __name__ == "__main__":
    # Check required environment variables
    required_vars = ['BOT_TOKEN', 'API_ID', 'API_HASH', 'DB_URI']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    # Set up proper event loop policy for better stability
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Application error: {e}")
        sys.exit(1)

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
