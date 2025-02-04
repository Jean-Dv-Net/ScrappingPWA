import requests
from src.scrappers.scrapper import Scrapper

class Compensar(Scrapper):
    def __init__(self):
        super().__init__(name="Compensar Scrapper")
    
    async def __open_page(self, url: str) -> bool:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                await self.page.goto(url, wait_until="domcontentloaded")
                await self.page.locator("input[id='ctl00_ajaxPlaceHolder_login_UserName']").wait_for(state="visible")
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
        types_documents = {
            "CC": "4",
            "CE": "5",
            "TI": "3",
            "RC": "2",
            "MS": "1",
            "PA": "6",
            "AS": "7",
            "CN": "8",
            "NIT": "9",
            "NU": "10"
        }
        try:
            # Fill username
            if not (self.hasButtonReturn):
                await self.page.fill("input[id='ctl00_ajaxPlaceHolder_login_UserName']", debtor["username"])
                await self.page.fill("input[id='ctl00_ajaxPlaceHolder_login_Password']", debtor["password"])
                await self.page.click("input[type='submit']")
            await self.page.fill("input[id='ctl00_ajaxPlaceHolder_paciente_txtNumeroDocumento_txt']", debtor["identification"])
            await self.page.select_option("select[id='ctl00_ajaxPlaceHolder_paciente_cboTipoDocumento_cbo']", types_documents[debtor["type_identification"]])
            await self.page.click("input[id='ctl00_ajaxPlaceHolder_paciente_btnBuscarPaciente']")
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
            await self.page.locator("div[id='ctl00_progress_mpeProgress_foregroundElement']").wait_for(state="hidden")
            if (await self.page.locator("div[id='ctl00_box_pan']").is_visible()):
                return False
            return True
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

            data_scrapping = []

            if "direccion" in vars:
                data = await self.page.locator("input[id='ctl00_ajaxPlaceHolder_paciente_txtDireccion_txt']").get_attribute("value")
                if data != None and data != "":
                    data_scrapping.append({
                        "area": "Datos",
                        "field": "direccion",
                        "field_value": data
                    })
            
            if "celular" in vars:
                data = await self.page.locator("input[id='ctl00_ajaxPlaceHolder_paciente_txtCelular_txt']").get_attribute("value")
                if data != None and data != "":
                    data_scrapping.append({
                        "area": "Datos",
                        "field": "celular",
                        "field_value": data
                    })
            
            if "telefono_fijo" in vars:
                data = await self.page.locator("input[id='ctl00_ajaxPlaceHolder_paciente_txtTelefono_txt']").get_attribute("value")
                if data != None and data != "":
                    data_scrapping.append({
                        "area": "Datos",
                        "field": "telefono_fijo",
                        "field_value": data
                    })
            
            if "correo_electronico" in vars:
                data = await self.page.locator("input[id='ctl00_ajaxPlaceHolder_paciente_txtEmail_txt']").get_attribute("value")
                if data != None and data != "":
                    data_scrapping.append({
                        "area": "Datos",
                        "field": "correo_electronico",
                        "field_value": data
                    })
            
            if "ciudad" in vars:
                data = await self.page.locator("select[id='ctl00_ajaxPlaceHolder_paciente_cboMunicipio_cbo']").locator("option[selected]").inner_text()
                if data != "Seleccione...":
                    data_scrapping.append({
                        "area": "Datos",
                        "field": "ciudad",
                        "field_value": data
                    })
            
            if "departamento" in vars:
                data = await self.page.locator("select[id='ctl00_ajaxPlaceHolder_paciente_cboDepartamento_cbo']").locator("option[selected]").inner_text()
                if data != "Seleccione...":
                    data_scrapping.append({
                        "area": "Datos",
                        "field": "departamento",
                        "field_value": data
                    })

            if len(data_scrapping) > 0:
                self.data[self.i] = {
                    "message": "Data scraped",
                    "status": "success",
                    "data": data_scrapping,
                    "debtor": debtor
                }
                return True
            
            self.data[self.i] = {
                "message": "No data scraped",
                "status": "novelty",
                "data": [],
                "debtor": debtor
            }
        except Exception as e:
            self.logger.error(f"Error scraping data: {e}")
            self.data[self.i] = {
                "message": f"Error scraping data: {e}",
                "status": "fail",
                "data": []
            }

    
    async def __return_to_other(self):
        await self.page.click("input[id='ctl00_ajaxPlaceHolder_paciente_limpiarBtn']")
        self.hasButtonReturn = True
        
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
                await self.__return_to_other()
            self.i += 1
        return self.data