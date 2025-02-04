import requests
from src.scrappers.scrapper import Scrapper


class SOS(Scrapper):
    def __init__(self):
        super().__init__(name="SOS Scrapper")

    async def __open_page(self, url: str) -> bool:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                await self.page.goto(url, wait_until="domcontentloaded")
                await self.page.locator("input[id='j_username']").wait_for(state="visible")
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
                await self.page.fill("input[id='j_username']", debtor["username"])
                await self.page.fill("input[id='j_password']", debtor["password"])
                await self.page.locator("input[type='submit']").click()
                await self.page.locator("a[id='j_id10:j_id13:0:j_id15']").click()
            
            await self.page.select_option("select[id='afiliadoForm:tipoId']", debtor["type_identification"])
            await self.page.fill("input[id='afiliadoForm:numeroId']", debtor["identification"])
            await self.page.click("input[id='afiliadoForm:consultarAfiliado']")
            await self.page.locator("div[id='formPopupMessages:modalPnlPopCDiv']").wait_for(state="visible", timeout=5000)
            if (await self.page.locator("div[id='formPopupMessages:modalPnlPopCDiv']").is_visible()):
                message_modal = await self.page.locator("div[id='formPopupMessages:modalPnlPopCDiv']").inner_text()
                if message_modal.rfind("EPS") != -1:
                    await self.page.click("input[id='formPopupMessages:j_id350:0:modalPnlCloseButton1']")
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
            if (await self.page.locator("input[id='formPopupMessages:j_id350:0:modalPnlCloseButton1']").is_visible()):
                await self.page.locator("input[id='formPopupMessages:j_id350:0:modalPnlCloseButton1']").click()
                await self.page.locator("div[id='waitPanel']").wait_for(state="hidden")
                self.data[self.i] = {
                    "message": "No se encontrarón registros para el documento ingresado",
                    "status": "novelty",
                    "data": []
                }
                return False
            return True
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
            await self.page.click("input[id='afiliadoForm:j_id163']")
            panel_selector = "#informacionAdicionalPopupMessages\\:j_id304_body tr"
            rows = await self.page.locator(panel_selector).all()

            vars = debtor["variables"]
            vars = [vars.strip() for vars in vars.split(",")]
            data_scrapping = []

            for row in rows:
                label = await row.locator("label").inner_text()
                data = await row.locator("td:nth-child(2)").inner_text()

                if "celular" in vars and label.find("Teléfono") != -1:
                    data_scrapping.append({
                        "area": "Datos",
                        "field": "celular",
                        "field_value": data.strip()
                    })
                
                if "ciudad" in vars and label.find("Ciudad") != -1:
                    data_scrapping.append({
                        "area": "Datos",
                        "field": "ciudad",
                        "field_value": data.strip()
                    })

                if "departamento" in vars and label.find("Departamento") != -1:
                    data_scrapping.append({
                        "area": "Datos",
                        "field": "departamento",
                        "field_value": data.strip()
                    })
                
                if "direccion" in vars and label.find("Dirección") != -1:
                    data_scrapping.append({
                        "area": "Datos",
                        "field": "direccion",
                        "field_value": data.strip()
                    })
            if len(data_scrapping) > 0:
                self.data[self.i] = {
                    "message": "Data scraped",
                    "status": "success",
                    "data": data_scrapping
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

    async def __return_to_other(self):
        await self.page.click("a[id='informacionAdicionalPopupMessages:j_id302']")
        await self.page.locator("div[id='waitPanel']").wait_for(state="hidden")
        await self.page.click("input[name='afiliadoForm:j_id165']")
        self.hasButtonReturn = True
    
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
                    await self.__return_to_other()
                self.hasButtonReturn = True
                self.i += 1
        self.logger.info("Scraping finished")
        self.logger.info("Data recolected: ", self.data)