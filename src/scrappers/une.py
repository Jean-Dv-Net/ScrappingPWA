from typing import Tuple
from bs4 import BeautifulSoup, Tag
from src.scrappers.scrapper import Scrapper
from playwright.async_api import Page

class UNE(Scrapper):
    def __init__(self):
        super().__init__(name="UNE Scrapper")

    async def __open_page(self, url: str) -> bool:
        try:
            await self.page.goto(url, wait_until="domcontentloaded")
            await self.page.locator("input[name='identity']").wait_for(state="visible")
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
            if not (self.hasButtonReturn):
            # Fill identification
                await self.page.fill("input[name='identity']", debtor["username"])
                await self.page.fill("input[name='credential']", debtor["password"])
                await self.page.click("button[name='submit']")
                await self.page.wait_for_load_state(state="domcontentloaded")
                if (await self.page.locator("#content > div > div > div > form > ul > li").is_visible()):
                    self.data[self.i] = {
                        "message": "Credenciales para ingresar invalidas, intente cambiando la configuración de la página...",
                        "status": "fail",
                        "data": []
                    }
                    return False

            await self.page.fill("input[name='cedulanit']", debtor["identification"])
            await self.page.click("#submitbutton")
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
        element = self.page.locator("#resultadobusqueda")
        text = await element.inner_text()
        while "Cargando" in text:
            await self.page.wait_for_timeout(timeout=200)
            text = await element.inner_text()
        if ("No hay guias con este criterio" in text):
            self.data[self.i] = {
                "message": "No data found",
                "status": "novelty",
                "data": []
            }
            return False
        await self.page.locator("#resultadobusqueda table").wait_for(state="visible")
        return True
    
    async def __scrape_detail(self, page: Page) -> Tuple[str, str]:        
        await page.wait_for_load_state(state="domcontentloaded")

        await page.locator("div[id='detalleguia']").wait_for(state="visible")
        table = await page.locator("div[id='detalleguia']").inner_html()

        # Analizar el HTML para obtener los datos de teléfono y dirección del destinatario
        soup = BeautifulSoup(table, "html.parser")
        table_receiver = soup.find('p', string='Destinatario').find_next_sibling('table')
        email = table_receiver.select_one('th:-soup-contains("Direccion") + td table tbody tr td').get_text(strip=True)
        phone = table_receiver.select_one("th:-soup-contains('Telefono') + td table tbody tr td").get_text(strip=True)
        await page.close()
        return email, phone
        
    def __is_valid_data(self, data: str) -> bool:
        return data is not None and data != ""
    
    async def __scrape_data(self, debtor: dict) -> bool:
        try:
            vars = debtor["variables"]
            vars = [vars.strip() for vars in vars.split(',')]

            rows = await self.page.locator("#resultadobusqueda table tbody tr").element_handles()

            data_scraping = []
            cont = 0
            for row_element in rows:
                row = BeautifulSoup(await row_element.inner_html(), "html.parser")
                link = await row_element.query_selector('a')
                if link is not None:
                    async with self.page.expect_popup() as new_page_info:
                        await link.click()
                    newpage = await new_page_info.value
                    email, phone = await self.__scrape_detail(newpage)
                
                direction_data = row.find('td', {'width': '12%'}).get_text(strip=True)
                last_invoice = row.find_all('td')[7].get_text(strip=True)
                source_destination = row.find_all('td')[8].get_text(strip=True)
                self.logger.info({ "rowfind": row.find_all('td')[8], "source_destination": source_destination })

                if self.__is_valid_data(direction_data) and direction_data.find('@') != -1:
                    data_scraping.append({
                        'field': 'email',
                        'field_value': direction_data
                    })
                elif self.__is_valid_data(direction_data):
                    data_scraping.append({
                        'field': 'address',
                        'field_value': direction_data
                    })
                if (self.__is_valid_data(email)) and email.find('@') != -1:
                    data_scraping.append({
                        'field': 'email',
                        'field_value': email
                    })
                if self.__is_valid_data(phone) and len(phone) >= 10 and phone.startswith('3'):
                    data_scraping.append({
                        'field': 'cellphone',
                        'field_value': phone
                    })
                if self.__is_valid_data(phone) and len(phone) <= 10:
                    data_scraping.append({
                        'field': 'phone',
                        'field_value': phone
                    })
                if self.__is_valid_data(last_invoice) and cont == 0:
                    data_scraping.append({
                        'field': 'last_invoice',
                        'field_value': last_invoice
                    })
                if self.__is_valid_data(source_destination):
                    destination = source_destination.split(' / ')[1]
                    data_scraping.append({
                        'field': 'source_destination',
                        'field_value': destination
                    })
                cont = cont + 1
                
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
                self.hasButtonReturn = True
            self.i += 1
        self.logger.info("Scrapper finished")
        self.logger.info(f"Data scraped: {self.data}")
        return self.data