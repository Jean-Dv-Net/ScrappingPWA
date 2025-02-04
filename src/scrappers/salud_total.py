import re
import requests
from src.scrappers.scrapper import Scrapper


class SaludTotal(Scrapper):
    def __init__(self):
        super().__init__(name="Salud Total Scrapper")
    
    async def __open_page(self, url: str) -> bool:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                await self.page.goto(url, wait_until="domcontentloaded")
                await self.page.locator("li[id='k-tabstrip-tab-0']").wait_for(state="visible")
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
        debtors_types = {
            "CC": "Cedula de Ciudadania",
            "CE": "Cedula de Extranjeria",
            "TI": "Tarjeta de Identidad",
            "RC": "Registro Civil",
            "MS": "Menor sin Identificacion",
            "PA": "Pasaporte",
            "AS": "Adulto sin Identificacion",
            "CN": "Certificado de Nacido Vivo",
            "NIT": "NIT",
        }
        try:
            if not self.hasButtonReturn:
                # Click in the tab four
                await self.page.click("li[id='k-tabstrip-tab-3']")
                await self.page.locator("kendo-combobox[formcontrolname='ddlTipoDocumentoIPS'] input").type("NIT")
                await self.page.press("kendo-combobox[formcontrolname='ddlTipoDocumentoIPS'] input", "Enter")
                await self.page.fill("input[formcontrolname='txtNumeroDocumentoIPS']", "816001182")
                await self.page.locator("kendo-combobox[formcontrolname='ddlTipoDocumento'] input").type("NIT")
                await self.page.press("kendo-combobox[formcontrolname='ddlTipoDocumento'] input", "Enter")
                await self.page.fill("input[formcontrolname='txtNumeroDocumento']", debtor["username"])
                await self.page.fill("input[formcontrolname='txtContrasena']", debtor["password"])
                await self.page.click("button[type='button']")

                # Click in consultas
                await self.page.get_by_text("CONSULTAS").click(timeout=60000)
                # Click in estado afiliacion grupo familiar
                await self.page.locator("button").get_by_text("ESTADO AFILIACIÓN GRUPO FAMILIAR").click()
            # Fill the form
            await self.page.fill("kendo-combobox[formcontrolname='ddlTipoDoc'] input", "")
            await self.page.type("kendo-combobox[formcontrolname='ddlTipoDoc'] input", debtors_types[debtor["type_identification"]])
            await self.page.press("kendo-combobox[formcontrolname='ddlTipoDoc'] input", "Enter")
            await self.page.fill("input[formcontrolname='txtNumeroIdentificacion']", debtor["identification"])
            await self.page.click("button[type='button']")
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
            await self.page.locator("ngx-spinner[type='ball-spin-clockwise']").wait_for(state="hidden", timeout=5000)
            await self.page.locator("kendo-dialog").wait_for(state="visible", timeout=5000)
            if (await self.page.locator("kendo-dialog").is_visible()):
                await self.page.click("button[role='button']")
                self.data[self.i] = {
                    "message": "No se encontrarón registros para el documento ingresado",
                    "status": "novelty",
                    "data": []
                }
                return False
            return True
        except TimeoutError:
            return True
        except Exception as e:
            self.logger.error(f"Error has information: {e}")
            self.data[self.i] = {
                "message": "No se encontrarón registros para el documento ingresado",
                "status": "novelty",
                "data": []
            }
            return False

    async def __scrape_data(self, debtor: dict) -> bool:
        try:
            vars = debtor["variables"]
            vars = [vars.strip() for vars in vars.split(",")]

            data_scraping = []
            data = await self.page.locator("p.info").first.inner_text()

            if data == None or data == "":
                self.data[self.i] = {
                    "message": "No se encontrarón registros para el documento ingresado",
                    "status": "novelty",
                    "data": []
                }
                return False
            
            if "celular" in vars:
                phone = re.search(r'Celular:\s*(\d+)', data).group(1)
                if phone != None and phone != "":
                    data_scraping.append({
                        "area": "Datos",
                        "field": "celular",
                        "field_value": phone
                    })
                
            if "telefono_fijo" in vars:
                phone = re.search(r'Teléfono:\s*(\d+)', data).group(1)
                if phone != None and phone != "":
                    data_scraping.append({
                        "area": "Datos",
                        "field": "telefono_fijo",
                        "field_value": phone
                    })
            
            if "correo_electronico" in vars:
                email = re.search(r'Correo Electrónico:\s*([^\s]+)', data).group(1)
                if email != None and email != "":
                    data_scraping.append({
                        "area": "Datos",
                        "field": "correo_electronico",
                        "field_value": email
                    })
                
            if len(data_scraping) > 0:
                self.data[self.i] = {
                    "message": "Data scraped",
                    "status": "success",
                    "data": data_scraping
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
        self.logger.info("Data scraped successfully")
        return self.data