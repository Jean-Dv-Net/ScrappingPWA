import requests
from src.scrappers.scrapper import Scrapper


class Registraduria(Scrapper):
    def __init__(self):
        super().__init__(name="Registraduria Scrapper")

    async def __open_page(self, url: str) -> bool:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                await self.page.goto(url, wait_until="domcontentloaded")
                await self.page.locator("input[name='username']").wait_for(state="visible")
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
        return False

    async def __generate_form(self, debtor: dict) -> bool:
        try:
            if not self.hasButtonReturn:
                # Fill username
                await self.page.fill("input[name='username']", debtor["username"])

                # Fill password
                await self.page.fill("input[name='password']", debtor["password"])

                # Click button to go
                await self.page.click("input[name='login']")

                # Click button basic consult
                await self.page.click("a[href='busqueda.php']")

            # Fill identification
            await self.page.fill("input[id='cc']", debtor["identification"])

            # Search with enter
            await self.page.press("input[id='cc']", key='Enter')
            return True
        except Exception as e:
            self.logger.error(f"Error generating form: {e}")
            self.data[self.i] = {
                "message": f"Error generating form: {e}",
                "status": "fail",
                "data": []
            }
        return False

    async def __has_information(self) -> bool:
        try:
            data = await self.page.locator("div[id='example_info']").inner_html(timeout=7000)
            if (data.find("of 0") == -1):
                return True
            self.data[self.i] = {
                "message": "Information not found",
                "status": "novelty",
                "data": []
            }
            return False
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
            vars = [var.strip() for var in vars.split(',')]

            data_scraping = []

            if "celular" in vars:
                data = await self.page.locator("table#example tbody:nth-of-type(2) tr:nth-child(1) td:nth-child(2)").inner_text()
                if data is not None and data != '':
                    data_scraping.append({
                        'area': 'Datos',
                        'field': 'celular',
                        'field_value': data.strip()
                    })
            
            if "direccion" in vars:
                data = await self.page.locator("table#example tbody:nth-of-type(2) tr:nth-child(1) td:nth-child(1)").inner_text()
                if data is not None and data != '':
                    data_scraping.append({
                        'area': 'Datos',
                        'field': 'direccion',
                        'field_value': data.strip()
                    })

            if "ciudad" in vars:
                data = await self.page.locator("table#example tbody:nth-of-type(2) tr:nth-child(1) td:nth-child(5)").inner_text()
                if data is not None and data != '':
                    data_scraping.append({
                        'area': 'Datos',
                        'field': 'ciudad',
                        'field_value': data.strip()
                    })
            
            if len(data_scraping) > 0:
                self.data[self.i] = {
                    "message": "Data scraped succesfully",
                    "status": "success",
                    "data": data_scraping
                }
                return True
            self.data[self.i] = {
                "message": "No data scrapped found",
                "status": "novelty",
                "data": []
            }
            return False
        except Exception as e:
            self.logger.error(f"Error scraping data: {e}")
            self.data[self.i] = {
                "message": f"Error scraping data: {e}",
                "status": "fail",
                "data": []
            }
            return
        

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
            self.hasButtonReturn = True
            self.i += 1
        self.logger.info("Scraping finished")
        self.logger.info(f"Data recolected: {self.data}")
        return self.data