from bs4 import BeautifulSoup
import requests
from src.scrappers.scrapper import Scrapper
from src.utils.logging import setup_logger

class Simit(Scrapper):
    def __init__(self):
        super().__init__(name="Simit Scrapper")

    async def __open_page(self, url: str) -> bool:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                await self.page.goto(url, wait_until="domcontentloaded")
                await self.page.locator("input[name='txtBusqueda']").wait_for(state="visible")
                return True
            else:
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
        return False
    
    async def __generate_form(self, debtor: dict) -> bool:
        try:
            # Fill username
            await self.page.fill("input[name='txtBusqueda']", debtor["identification"])
            await self.page.click("button[type='submit']")
            return True
        except Exception as e:
            self.logger.error(f"Error generating form: {e}")
            self.data[self.i] = {
                "message": f"Error generating form: {e}",
                "status": "fail",
                "data": []
            }
        return False
    
    async def __has_information(self)-> bool:
        try:
            if (await self.page.locator("#whcModal").is_hidden()):
                await self.page.locator("#whcModal").wait_for(state="visible", timeout=2000)
                await self.page.locator("#whcModal").wait_for(state="hidden")
            await self.page.locator("#multaTable").wait_for(state="visible", timeout=7000)
            return True
        except TimeoutError as e:
            self.logger.error(f"TimeoutError: {e}")
            self.data[self.i] = {
                "message": f"No se encontrarón registros para el documento ingresado: {e}",
                "status": "novelty",
                "data": []
            }
        except Exception as e:
            self.logger.error(f"Error has information: {e}")
            self.data[self.i] = {
                "message": f"Error has information: {e}",
                "status": "fail",
                "data": []
            }
        return False

    async def __scrape_data(self, debtor: dict) -> bool:
        try:
            vars = debtor["variables"]
            vars = [vars.strip() for vars in vars.split(",")]

            rows = await self.page.locator("#multaTable tbody tr").element_handles()

            data_scraping = []

            for row_element in rows:
                row = BeautifulSoup(await row_element.inner_html(), "html.parser")
                
                plate = row.find('td', {'data-label': 'Placa'}).get_text(strip=True)
                if "placa" in vars and plate != None and plate != "":
                    data_scraping.append({
                        "area": "Datos",
                        "field": "placa",
                        "field_value": plate
                    })

                city = row.find('td', {'data-label': 'Secretaría'}).get_text(strip=True)
                if "city" in vars and city != None and city != "":
                    data_scraping.append({
                        "area": "Datos",
                        "field": "ciudad",
                        "field_value": city
                    })
            if len(data_scraping) > 0:
                self.data[self.i] = {
                    "message": "Data scraped successfully",
                    "status": "success",
                    "data": data_scraping,
                    "debtor": debtor
                }
                return True
            self.data[self.i] = {
                "message": "No data scraped",
                "status": "novelty",
                "data": [],
                "debtor": debtor
            }
            return False
        except Exception as e:
            self.logger.error(f"Error scraping data: {e}")
            self.data[self.i] = {
                "message": f"Error scraping data: {e}",
                "status": "fail",
                "data": []
            }
        return False

    async def run(self, url: str, debtors: list) -> list:
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
            self.i += 1
        return self.data