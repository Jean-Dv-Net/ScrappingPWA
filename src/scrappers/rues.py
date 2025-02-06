import random
from typing import Dict, List
from bs4 import BeautifulSoup
import requests
from src.scrappers.scrapper import Scrapper


class Rues(Scrapper):
    FIELDS_SCRAP_TO_DATABASE = {
        "Numero de Matricula": "registration_number",
        "Último Año Renovado": "last_renewed_year",
        "Fecha de Renovacion": "renovation_date",
        "Fecha de Matricula": "registration_date",
        "Estado de la matricula": "registration_status",
        "Tipo de Sociedad": "society_type",
        "Tipo de Organización": "organization_type",
        "Categoria de la Matricula": "registration_category",
        "Fecha Ultima Actualización": "last_update_date",
        "Activo Corriente": "current_assets",
        "Activo No Corriente": "non_current_assets",
        "Activo Total": "total_assets",
        "Pasivo Corriente": "current_liabilities",
        "Pasivo No Corriente": "non_current_liabilities",
        "Pasivo Total": "total_liabilities",
        "Patrimonio Neto": "net_equity",
        "Pasivo Mas Patrimonio": "liabilities_plus_equity",
        "Balance Social": "social_balance",
        "Ingresos Actividad Ordinaria": "ordinary_activity_income",
        "Otros Ingresos": "other_income",
        "Costo de Ventas": "cost_of_sales",
        "Gastos Operacionales": "operational_expenses",
        "Otros Gastos": "other_expenses",
        "Gastos Impuestos": "tax_expenses",
        "Utilidad/Perdida Operacional": "operational_profit_loss",
        "Resultado del Periodo": "period_result"
    }

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
            await self.page.locator("#txtNIT").clear()
            await self.page.locator("#txtNIT").type(debtor["identification"], delay=random.randint(100, 200))
            await self.page.locator("#btnConsultaNIT").click()
            return True
        except Exception as e:
            self.logger.error(f"Error generating form: {e}")
            self.data[self.i] = {
                "message": f"Error generando el formulario",
                "status": "fail",
                "data": []
            }
            return False

    async def __has_information(self)-> bool:
        while await self.page.locator("#divLoading").first.is_visible():
            await self.page.wait_for_timeout(timeout=200)

        text_info = ""
        # Check if there is information
        if await self.page.locator("#card-info").is_visible():
            text_info = await self.page.locator("#card-info").inner_text()
        
        if "no ha retornado resultados" in text_info:
            
            self.data[self.i] = {
                "message": "No se encontraron datos",
                "status": "success",
                "data": []
            }
            return False
        return True

    async def __has_scraped_data(self, number_registration: str, data_scrapping: List[Dict]) -> bool:
        for item in data_scrapping:
            if item['field'] == 'registration_number' and item['field_value'] == number_registration:
                return True
        return False
    
    async def __parse_table_registration(self, html_content: str) -> List[Dict]:
        soup = BeautifulSoup(html_content, 'html.parser')
        data_scrapping = []

        commercial_municipality = ""
        fiscal_municipality = ""
        is_contact_info = False

        for row in soup.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) == 1 and 'colspan' in cols[0].attrs:
                is_contact_info = True
            if len(cols) == 2 and 'colspan' not in cols[0].attrs and is_contact_info:
                key = cols[0].text.strip()
                value = cols[1].text.strip()
                value = value.replace(' \xa0 ', ' ')
                if (value == ""):
                    continue
                if "Municipio Comercial" in key:
                    commercial_municipality = value
                if "Municipio Fiscal" in key:
                    fiscal_municipality = value
                if "Dirección Comercial" in key:
                    data_scrapping.append({
                        "area": "contact_information",
                        "field": "address",
                        "field_value": value + " || " + commercial_municipality,
                    })
                if "Dirección Fiscal" in key:
                    data_scrapping.append({
                        "area": "contact_information",
                        "field": "address",
                        "field_value": value + " || " + fiscal_municipality,
                    })
                if "Teléfono Comercial" in key or "Teléfono Fiscal" in key:
                    phones: List[str] = value.split(" ")
                    if len(phones) > 1:
                        for phone in phones:
                            if phone.startswith("0"):
                                continue
                            if len(phone) >= 10 and phone.startswith("3"):
                                data_scrapping.append({
                                    "area": "contact_information",
                                    "field": "cellphone",
                                    "field_value": phone,
                                })
                            if len(phone) <= 10:
                                data_scrapping.append({
                                    "area": "contact_information",
                                    "field": "phone",
                                    "field_value": phone,
                                })
                if "Correo Electrónico Comercial" in key or "Correo Electrónico Fiscal" in key:
                    data_scrapping.append({
                        "area": "contact_information",
                        "field": "email",
                        "field_value": value,
                    })
            if len(cols) == 2 and 'colspan' not in cols[0].attrs and not is_contact_info:
                key = cols[0].text.strip()
                value = cols[1].text.strip()
                data_scrapping.append({
                    "area": "comercial_establishment",
                    "field": self.FIELDS_SCRAP_TO_DATABASE.get(key, key),
                    "field_value": value
                })
        return data_scrapping

    async def __parse_table_finantial(self, html_content: str) -> List[Dict]:
        soup = BeautifulSoup(html_content, "html.parser")
        data_scrapping = []
        for row in soup.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) == 2:
                key = cols[0].text.strip()
                value = cols[1].text.strip().replace('$', '').replace(',', '').strip()
                data_scrapping.append({
                    "area": "comercial_establishment",
                    "field": self.FIELDS_SCRAP_TO_DATABASE.get(key, key),
                    "field_value": value
                })
        return data_scrapping


    async def __scrape_data(self, debtor: dict) -> bool:
        try:
            data_scrapping = []
            await self.page.locator("#rmTable2 > tbody > tr.odd > td:nth-child(1)").click()
            await self.page.locator("#rmTable2 > tbody > tr.child > td > ul a").first.click()
            has_more_information = True
            while has_more_information:
                # First table
                data_scrapping.extend(await self.__parse_table_registration(await self.page.locator("body > div:nth-child(3) > main > div > div.container-fluid > div:nth-child(6) > div > div.col-md-8 > div > div.card-block > div > table").inner_html()))
                economic_activity = await self.page.locator("body > div:nth-child(3) > main > div > div.container-fluid > div:nth-child(6) > div > div.col-md-4 > div:nth-child(3) > div.card-body > ul").inner_text()
                data_scrapping.append({
                    "area": "comercial_establishment",
                    "field": "economic_activity",
                    "field_value": economic_activity.strip().replace(' \xa0 ', ' ')
                })

                # Verify if financial information exists
                if (await self.page.locator("#btnConsultarInformacionFinanciera").is_visible()):
                    await self.page.locator("#btnConsultarInformacionFinanciera > span").click()
                    await self.page.locator("#accordionExample").wait_for(state="visible")
                    financial_information_text = await self.page.locator("#accordionExample").inner_text()
                    if "Sin resultados para mostrar" not in financial_information_text.strip():
                        # Scrapping the financial information
                        buttons = self.page.locator("#accordionExample .card-header button")
                        count = await buttons.count()
                        await buttons.nth(count -  1).click()
                        await self.page.wait_for_selector("#accordionExample .show")
                        data_scrapping.extend(
                            await self.__parse_table_finantial(
                                await self.page.locator("#accordionExample .show table").inner_html()
                            )
                        )

                # Click in Information Property, other comercial information
                if not (await self.page.locator("#btnConsultarEstablecimientos").is_visible()):
                    break
                await self.page.locator("#btnConsultarEstablecimientos > span").scroll_into_view_if_needed()
                await self.page.locator("#btnConsultarEstablecimientos > span").click()
                rows_elements = await self.page.locator("#relPropEst > tbody > tr").element_handles()
                for row_element in rows_elements:
                    registration_element = await row_element.query_selector('td:nth-child(3)')
                    registration_number = await registration_element.inner_text()
                    if not registration_number.isdigit():
                        registration_element = await row_element.query_selector('td:nth-child(4)')
                        registration_number = await registration_element.inner_text()
                    self.logger.info({ "registration_number": registration_number })
                    if await self.__has_scraped_data(registration_number, data_scrapping):
                        has_more_information = False
                        continue
                    has_more_information = True
                    element = await row_element.query_selector('td:nth-child(1)')
                    await element.click()
                    await self.page.locator("#relPropEst > tbody > tr.child > td > ul a").click()
                    break
            if len(data_scrapping) > 0:
                self.data[self.i] = {
                    "message": "Se encontro información",
                    "status": "success",
                    "data": data_scrapping
                }
                return True
            self.data[self.i] = {
                "message": "No se encontro información",
                "status": "success",
                "data": data_scrapping
            }
            return False 
        except Exception as e:
            self.logger.error(f"Error scraping data: {e}")
            self.data[self.i] = {
                "message": f"Error obteniendo información",
                "status": "fail",
                "data": []
            }
        return False
    
    async def __return_to_other(self):
        await self.page.locator("body > div:nth-child(3) > main > div > div:nth-child(1) > a").scroll_into_view_if_needed()
        await self.page.locator("body > div:nth-child(3) > main > div > div:nth-child(1) > a").click()


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
                    await self.__return_to_other()
                self.hasButtonReturn = True
            self.i += 1
        self.logger.info("Data scraped successfully")
        return self.data