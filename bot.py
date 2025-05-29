# Don't Remove Credit Tg - @mr_readers
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @mr_readers

import asyncio
import os
import tempfile
from pyrogram import Client
from pyrogram.errors import FloodWait
from config import API_ID, API_HASH, BOT_TOKEN

class Bot(Client):

    def __init__(self):
        # Use a unique session name with temp directory to avoid conflicts
        session_name = f"amk_login_{os.getpid()}"
        session_path = os.path.join(tempfile.gettempdir(), session_name)
        
        super().__init__(
            session_path,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="AMK"),
            workers=50,
            sleep_threshold=10
        )

    async def start(self):
        max_retries = 5
        retry_delay = 10
        
        for attempt in range(max_retries):
            try:
                await super().start()
                print('Bot Started Powered By @mr_readers')
                return
            except FloodWait as e:
                print(f"FloodWait error: Sleeping for {e.value} seconds")
                await asyncio.sleep(e.value)
            except Exception as e:
                print(f"Error starting bot (attempt {attempt + 1}/{max_retries}): {e}")
                
                # Clean up potential lock files
                await self.cleanup_session_files()
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (attempt + 1))
                else:
                    print("Max retries reached. Bot startup failed.")
                    raise

    async def cleanup_session_files(self):
        """Clean up session files that might be causing locks"""
        try:
            session_files = [
                f"{self.name}.session",
                f"{self.name}.session-journal",
                f"{self.name}.session-wal",
                f"{self.name}.session-shm"
            ]
            
            for file_path in session_files:
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        print(f"Cleaned up session file: {file_path}")
                    except Exception as e:
                        print(f"Could not remove {file_path}: {e}")
        except Exception as e:
            print(f"Error during session cleanup: {e}")

    async def stop(self, *args):
        try:
            await super().stop()
            print('Bot Stopped Bye')
        except Exception as e:
            print(f"Error stopping bot: {e}")
        finally:
            # Clean up session files on stop
            await self.cleanup_session_files()

if __name__ == "__main__":
    Bot().run()

# Don't Remove Credit Tg - @mr_readers
# Ask Doubt on telegram @mr_readers
