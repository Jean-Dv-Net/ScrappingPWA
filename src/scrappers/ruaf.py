import requests
from src.scrappers.scrapper import Scrapper

class Ruaf(Scrapper):
    def __init__(self):
        super().__init__(name = "RUAF Scrapper")
    
    async def __open_page(self, url: str) -> bool:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                await self.page.goto(url, wait_until="domcontentloaded")
                await self.page.locator("div[id='TerminosyCond']").wait_for(state="visible")
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
            types_documents_value = {
                "CC": "5|CC",
                "PA": "6|PA",
                "AS": "7|AS",
                "CD": "10|CD",
                "CN": "12|CN",
                "SC": "13|SC",
                "PE": "14|PE",
                "PT": "15|PT",
                "MS": "1|MS",
                "RC": "2|RC",
                "TI": "3|TI",
                "CE": "4|CE"
            }
            if not self.hasButtonReturn:
                await self.page.click("input[id='MainContent_RadioButtonList1_0']")
                await self.page.click("input[id='MainContent_btnEnviar']")
            await self.page.locator("select[id='ddlTiposDocumentos']").select_option(types_documents_value[debtor["type_identification"]])
            await self.page.fill("input[id='MainContent_txbNumeroIdentificacion']", debtor["identification"])
            await self.page.fill("input[id='MainContent_datepicker']", debtor["date_expedition"])
            await self.page.locator("body").click(position={"x": 0, "y": 0})
            await self.page.click("input[id='MainContent_btnConsultar']")
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
            await self.page.locator("table[id='ctl00_MainContent_rvConsulta_fixedTable']").wait_for(state="visible", timeout=5000)
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

    async def __scrape_data(self, debtor: dict) -> bool:
        try:
            vars = debtor["variables"]
            vars = [vars.strip() for vars in vars.split(",")]
            data_scraping = []
            if "afiliacion" in vars:
                data_scraping.append({
                    "area": "Datos",
                    "field": "afiliacion",
                    "field_value": "Si"
                })
        
            if len(data_scraping) > 0:
                self.data[self.i] = {
                    "message": "Data scraped",
                    "status": "success",
                    "data": data_scraping
                }
                return True
            self.data[self.i] = {
                "message": "No data scraped",
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
                await self.page.evaluate("window.history.go(-2)")
                self.hasButtonReturn = True
            self.i += 1
        return self.data
