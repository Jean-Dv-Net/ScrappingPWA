import random
from src.scrappers.scrapper import Scrapper


class Positiva2(Scrapper):
    def __init__(self):
        super().__init__(name="Positiva2 Scrapper")

    async def __open_page(self, url: str) -> bool:
        try:
            await self.page.goto(url, wait_until="domcontentloaded")
            await self.page.locator("input[id='username']").wait_for(state="visible")
            return True
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
                await self.page.type("input[id='username']", debtor["username"], delay=random.randint(100, 200))
                await self.page.type("input[id='password']", debtor["password"], delay=random.randint(100, 200))
                await self.page.click("input[type='submit']")
            await self.page.select_option("select[id='tipoDocumento']", debtor["type_identification"])
            await self.page.fill("input[id='numeroDocumento']", debtor["identification"])
            await self.page.click("button[id='buscar']")
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
            await self.page.locator("form[id='solicitudUrgenciaDto']").wait_for(state="visible", timeout=4000)
            return True
        except TimeoutError as e:
            self.logger.error(f"Error has information: {e}")
            self.data[self.i] = {
                "message": "No se encontrarón registros para el documento ingresado",
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
            vars = [vars.strip() for vars in vars.split(",")]

            data_scrapping = []

            if "direccion" in vars:
                data = await self.page.locator("input[id='datosDelPaciente_direccionResidencia']").get_attribute("value")
                if data != None and data != "":
                    data_scrapping.append({
                        "area": "Datos",
                        "field": "direccion",
                        "field_value": data
                    })
            
            if "departamento" in vars:
                data = await self.page.locator("select[id='datosDelPaciente_departamentoDescripcion']").locator("option[selected]").inner_text()
                if data != None and data != "":
                    data_scrapping.append({
                        "area": "Datos",
                        "field": "departamento",
                        "field_value": data
                    })
            
            if "ciudad" in vars:
                data = await self.page.locator("select[id='datosDelPaciente_municipioDescripcion']").locator("option[selected]").inner_text()
                if data != None and data != "":
                    data_scrapping.append({
                        "area": "Datos",
                        "field": "ciudad",
                        "field_value": data
                    })
            
            if "correo_electronico" in vars:
                data = await self.page.locator("input[id='datosDelPaciente_email']").get_attribute("value")
                if data != None and data != "":
                    data_scrapping.append({
                        "area": "Datos",
                        "field": "correo_electronico",
                        "field_value": data
                    })
            
            if "telefono_fijo" in vars:
                pre = await self.page.locator("input[id='datosDelPaciente_telParticularPre']").get_attribute("value")
                data = await self.page.locator("input[id='datosDelPaciente_telParticular']").get_attribute("value")
                if pre != None and pre != "" and data != None and data != "":
                    data_scrapping.append({
                        "area": "Datos",
                        "field": "telefono_fijo",
                        "field_value": pre + data
                    })
            
            if "celular" in vars:
                pre = await self.page.locator("input[id='datosDelPaciente_celParticularPre']").get_attribute("value")
                data = await self.page.locator("input[id='datosDelPaciente_celParticular']").get_attribute("value")
                if pre != None and pre != "" and data != None and data != "":
                    data_scrapping.append({
                        "area": "Datos",
                        "field": "celular",
                        "field_value": pre + data
                    })

            if len(data_scrapping) > 0:
                self.data[self.i] = {
                    "message": "Data scraped",
                    "status": "success",
                    "data": data_scrapping
                }
                self.logger.info(self.data)
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
    
    async def run(self, url: str, debtors: list):
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
                await self.page.go_back()
            self.hasButtonReturn = True
            self.i += 1
        return self.data