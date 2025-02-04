from abc import ABC, abstractmethod
from playwright.async_api import async_playwright
from src.utils.logging import setup_logger

class Scrapper(ABC):
    def __init__(self, name: str):
        self.logger = setup_logger(name=name)
        self.hasButtonReturn = False
        self.browser = None
        self.page = None
        self.data = []
        self.i = 0

    async def _initialize_browser(self) -> bool:
        try:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(
                headless=False
            )
            context = await self.browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
            self.page = await context.new_page()
            return True
        except Exception as e:
            self.logger.error(f"Error initializing browser: {e}")
            self.data[self.i] = {
                "message": f"Error initializing browser: {e}",
                "status": "fail",
                "data": []
            }

    @abstractmethod
    def run(self, url: str, debtors: list) -> list:
        pass