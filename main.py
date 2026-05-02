import os, sys
from dotenv import load_dotenv
load_dotenv()
from bot.main import main
import asyncio
asyncio.run(main())
