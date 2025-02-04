import requests
from src.scrappers.scrapper import Scrapper

class NEPS(Scrapper):
    def __init__(self):
        super().__init__(name="Nueva EPS Scrapper")
    
    async def __open_page(self, url: str) -> bool:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                await self.page.goto(url, wait_until="domcontentloaded")
                await self.page.wait_for_selector("app-login")
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
            if not self.hasButtonReturn:
                # Fill username
                await self.page.fill("input[type='text']", debtor["username"])

                # Click button to go
                await self.page.click("button[type='submit']")

                # Fill password
                await self.page.fill("input[type='password']", debtor["password"])

                # Select sede button
                await self.page.locator('ion-item ionic-selectable button').click()
                await self.page.locator("ion-item ion-label:text-is('E.S.E. HOSPITAL SAN VICENTE DE PAUL DE CALDAS ANTIOQUIA')").click()
                await self.page.click("button[type='submit']")
        
            # Fill identification
            await self.page.fill("input[name='numero_documento']", debtor["identification"])

            # Fill type identification
            await self.page.locator("ion-select[name='tipo_documento']").click()
            await self.page.locator(f"button:has-text('{debtor['type_identification']}')").click()
            await self.page.locator("button:has-text('OK')").click()
            await self.page.locator("ion-button:has-text('Verificar Derechos')").click()
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
            await self.page.locator("ion-item-divider:has-text('Datos básicos paciente')").wait_for(state="visible", timeout=20000)
            return True
        except Exception as e:
            self.logger.error(f"Error getting information: {e}")
            self.data[self.i] = {
                "message": f"Error getting information: {e}",
                "status": "fail",
                "data": []
            }
            return False

    async def __scrape_data(self, debtor):
        try:
            vars = debtor["variables"]
            vars = [var.strip() for var in vars.split(',')]
            data_scraping = []

            if "celular" in vars:
                data = await self.page.locator("ion-input[name='celular']").get_attribute("ng-reflect-model")
                if data != '':
                    self.logger.info(f"Data scraped: {data}")
                    data_scraping.append({
                        'area': 'Datos',
                        'field': 'celular',
                        'field_value': data
                    })
            
            if "telefono_fijo" in vars:
                data = await self.page.locator("ion-input[name='telefono1']").get_attribute("ng-reflect-model")
                if data == None or data == "":
                    data = await self.page.locator("ion-input[name='telefono2']").get_attribute("ng-reflect-model")

                if data != '':
                    data_scraping.append({
                        'area': 'Datos',
                        'field': 'telefono_fijo',
                        'field_value': data
                    })
            
            if "correo_electronico" in vars:
                data = await self.page.locator("ion-input[name='email']").get_attribute("ng-reflect-model")

                if data != '' and data.find('@') != -1:
                    data_scraping.append({
                        'area': 'Datos',
                        'field': 'correo_electronico',
                        'field_value': data
                    })
            
            if "ciudad" in vars:
                data = await self.page.locator("ion-input[name='municipio_residencia']").get_attribute("ng-reflect-model")
                self.logger.info(f"Data scraped: {data}")
                if data != '':
                    data_scraping.append({
                        'area': 'Datos',
                        'field': 'ciudad',
                        'field_value': data
                    })

            if "departamento" in vars:
                data = await self.page.locator("ion-input[name='depto_residencia']").get_attribute("ng-reflect-model")
                self.logger.info(f"Data scraped: {data}")
                if data != '':
                    data_scraping.append({
                        'area': 'Datos',
                        'field': 'departamento',
                        'field_value': data
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
                "data": []
            }
            
        except Exception as e:
            self.logger.error(f"Error scraping data: {e}")
            self.data[self.i] = {
                "message": f"Error scraping data: {e}",
                "status": "fail",
                "data": []
            }
            return
    
    async def __return_to_other(self):
        await self.page.locator("ion-button:has-text('Regresar')").scroll_into_view_if_needed()
        await self.page.locator("ion-button:has-text('Regresar')").click()
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
        return self.data