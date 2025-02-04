import random
from bs4 import BeautifulSoup
from src.scrappers.scrapper import Scrapper

class Positiva1(Scrapper):
    def __init__(self):
        super().__init__('Positiva1')

    async def __open_page(self, url: str) -> bool:
        try:
            await self.page.goto(url, wait_until='domcontentloaded')
            await self.page.locator("input[name='username']").wait_for(state='visible')
            return True
        except Exception as e:
            self.logger.error(f'Error opening page: {e}')
            self.data[self.i] = {
                'message': f'Error opening page: {e}',
                'status': 'fail',
                'data': []
            }
            return False
        
    async def __generate_form(self, debtor: dict) -> bool:
        types_document = {
            "CC": "formDataConsultaCaso:tipoDocumentoAsegurado_0",
            "CE": "formDataConsultaCaso:tipoDocumentoAsegurado_1",
            "PA": "formDataConsultaCaso:tipoDocumentoAsegurado_2",
            "RC": "formDataConsultaCaso:tipoDocumentoAsegurado_3",
            "TI": "formDataConsultaCaso:tipoDocumentoAsegurado_4",
            "PE": "formDataConsultaCaso:tipoDocumentoAsegurado_6",
            "PT": "formDataConsultaCaso:tipoDocumentoAsegurado_7",
            "CD": "formDataConsultaCaso:tipoDocumentoAsegurado_8",
            "SC": "formDataConsultaCaso:tipoDocumentoAsegurado_9",
            "NUIP": "formDataConsultaCaso:tipoDocumentoAsegurado_10",
        }
        try:
            if not (self.hasButtonReturn):
                await self.page.type("input[name='username']", debtor['username'], delay=random.randint(100, 200))
                await self.page.type("input[name='password']", debtor['password'], delay=random.randint(100, 200))
                await self.page.click("input[type='submit']")
            await self.page.locator("div.ui-selectonemenu-trigger").first.click()
            await self.page.locator(f"li[id='{types_document[debtor['type_identification']]}']").click()
            await self.page.fill("input[id='formDataConsultaCaso:numeroIdentificacionAsegurado']", debtor["identification"])
            await self.page.click("button[id='formDataConsultaCaso:buscar']")
            return True
        except Exception as e:
            self.logger.error(f'Error generating form: {e}')
            self.data[self.i] = {
                'message': f'Error generating form: {e}',
                'status': 'fail',
                'data': []
            }
            return False
    
    async def __has_information(self) -> bool:
        try:
            if (await self.page.locator("div[id='j_idt23']").is_visible()):
                await self.page.locator("div[id='j_idt23']").wait_for(state='hidden')
            
            if (await self.page.locator("div[id='formDataConsultaCaso:messages'] div.ui-messages-info").is_visible()):
                self.data[self.i] = {
                    'message': 'No se encontraron registros para el documento ingresado',
                    'status': 'novelty',
                    'data': []
                }
                return False
            
            await self.page.locator("div[id='formDataConsultaCaso:tabViewConsultaIntegral:j_idt141']").wait_for(state='visible', timeout=7000)
            return True
        except Exception as e:
            self.logger.error(f'Error has information: {e}')
            self.data[self.i] = {
                'message': f'No se encontro información para el documento ingreasado',
                'status': 'novelty',
                'data': []
            }
            return False
        
    async def __scrape_data(self, debtor: dict) -> bool:
        try:
            vars = debtor['variables']
            vars = [var.strip() for var in vars.split(',')]

            rows = await self.page.locator("div[id='formDataConsultaCaso:tabViewConsultaIntegral:j_idt142:j_idt143_content'] div.col-md-3").element_handles()

            data_scraping = []
            for row_element in rows:
                row = BeautifulSoup(await row_element.inner_html(), 'html.parser')
                label = row.find('label').get_text(strip=True)
                value = row.text.replace(label, '').strip()

                if label == "Correo Electronico" and "correo_electronico" in vars:
                    data_scraping.append({
                        'area': 'Datos',
                        'field': 'correo_electronico',
                        'field_value': value
                    })

                if label == "Departamento" and "departamento" in vars:
                    data_scraping.append({
                        'area': 'Datos',
                        'field': 'departamento',
                        'field_value': value
                    })
                
                if label == "Ciudad/ Municipio" and "ciudad" in vars:
                    data_scraping.append({
                        'area': 'Datos',
                        'field': 'ciudad',
                        'field_value': value
                    })

                if label == "Dirección de Residencia" and "direccion" in vars:
                    data_scraping.append({
                        'area': 'Datos',
                        'field': 'direccion',
                        'field_value': value
                    })
                
                if label == "Telefóno Fijo Particular" and "telefono_fijo" in vars:
                    data_scraping.append({
                        'area': 'Datos',
                        'field': 'telefono',
                        'field_value': value
                    })
                
                if label == "Celular Particular" and "celular" in vars:
                    data_scraping.append({
                        'area': 'Datos',
                        'field': 'celular',
                        'field_value': value
                    })
            self.logger.info(f'Data scraped: {data_scraping}')
            if len(data_scraping) > 0:
                self.data[self.i] = {
                    'message': 'Data scraped',
                    'status': 'success',
                    'data': data_scraping
                }
                return True
            self.data[self.i] = {
                'message': 'No data scraped',
                'status': 'novelty',
                'data': []
            }
            return False
        except Exception as e:
            self.logger.error(f'Error scraping data: {e}')
            self.data[self.i] = {
                'message': f'Error scraping data: {e}',
                'status': 'fail',
                'data': []
            }
            return False

    async def __return_to_other(self) -> bool:
        try:
            await self.page.click("button[id='formDataConsultaCaso:limpairaSencillo1']")
            self.hasButtonReturn = True
            return True
        except Exception as e:
            self.logger.error(f'Error returning to other: {e}')
            self.data[self.i] = {
                'message': f'Error returning to other: {e}',
                'status': 'fail',
                'data': []
            }
            return False

    async def run(self, url: str, debtors: list) -> list:
        self.data = [None] * len(debtors)
        self.i = 0
        if not (await self._initialize_browser()):
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
        return self.data