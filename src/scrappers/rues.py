import random
import requests
from src.scrappers.scrapper import Scrapper


class Rues(Scrapper):
    def __init__(self):
        super().__init__(name="RUES Scrapper")
    
    async def __open_page(self, url: str) -> bool:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                await self.page.goto(url, wait_until="domcontentloaded")
                await self.page.locator("#st-header > div.mn-navigation > button").wait_for(state="visible")
                await self.page.locator("#modalInformativo > div > div > div.modal-footer > button").click()
                return True
            self.data[self.i] = {
                "message": f"Error opening page: {response.status_code}",
                "status": "fail",
                "data": []
            }
            return False
        except Exception as e:
            self.logger.error(f"Error opening page: {e}")
            self.data[self.i] = {
                "message": f"Error opening page: {e}",
                "status": "fail",
                "data": []
            }
        
    async def __generate_form(self, debtor: dict) -> bool:
        try:
            if not self.hasButtonReturn:
                await self.page.click("#st-header > div.mn-navigation > button")
                await self.page.locator("input[id='Email']").type(debtor['username'], delay=random.randint(100, 200))
                await self.page.locator("input[id='Password']").type(debtor['password'], delay=random.randint(100, 200))
                await self.page.locator("#frmLogin > div.main-login-form > div > div.form-group > button").click()
            
            # Fill identification and click button
            await self.page.locator("#txtNIT").type(debtor["identification"], delay=random.randint(100, 200))
            await self.page.locator("#btnConsultaNIT").click()
        except Exception as e:
            self.logger.error(f"Error generating form: {e}")
            self.data[self.i] = {
                "message": f"Error generando el formulario",
                "status": "fail",
                "data": []
            }
            return False

    async def __has_information(self)-> bool:
        # Wait for loading
        await self.page.locator("#divLoading").wait_for(state="visible", timeout=3000)
        while await self.page.locator("#divLoading").is_visible():
            await self.page.wait_for_timeout(timeout=200)

        # Check if there is information
        text_info = await self.page.locator("#card-info").inner_text()
        
        if "no ha retornado resultados" in text_info:
            self.data[self.i] = {
                "message": "No se encontraron datos",
                "status": "success",
                "data": []
            }
            return False
        
        await self.page.locator("#rmTable2").wait_for(state="visible")
        return True

    async def __scrape_data(self, debtor: dict) -> bool:
        try:
            pass
        except Exception as e:
            self.logger.error(f"Error scraping data: {e}")
            self.data[self.i] = {
                "message": f"Error scraping data: {e}",
                "status": "fail",
                "data": []
            }
        return False

    async def run(self, url: str, debtors: list) -> dict:
        self.data = [None] * len(debtors)
        self.i = 0
        if not (await super()._initialize_browser()):
            return self.data
        
        if not (await self.__open_page(url)):
            return self.data
        
        for debtor in debtors:
            if (await self.__generate_form(debtor)):
                if (await self.__has_information()):
                    await self.__scrape_data(debtor)
                self.hasButtonReturn = True
            self.i += 1
        self.logger.info("Data scraped successfully")
        self.logger.info(self.data)
        return self.data