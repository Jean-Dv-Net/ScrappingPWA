import asyncio
from src.scrappers.registraduria import Registraduria
from src.scrappers.neps import NEPS
from src.scrappers.simit import Simit
from src.scrappers.une import UNE
from src.scrappers.positiva_1 import Positiva1
from src.scrappers.ruaf import Ruaf
from src.scrappers.compensar import Compensar
from src.scrappers.rues import Rues
from src.scrappers.positiva_2 import Positiva2
from src.scrappers.salud_total import SaludTotal
if __name__ == "__main__":
    scraper = UNE()
    debtors = [
        {
            "id": 391,
            "rpa_batch_scraping_id": 49,
            "identification": "80028030",
            "date_expedition": "08/02/2023",
            "type_identification": "CC",
            "rpa_batch_detail_scraping_id": 391,
            "url": "https://pwa.referencias.nuevaeps.com.co",
            "name": "NUEVA EPS",
            "username": "pymes3",
            "password": "Pymes1829",
            "variables": "celular, ciudad"
        },
        {
            "id": 402,
            "rpa_batch_scraping_id": 49,
            "identification": "1027281247",
            "date_expedition": "03/12/1999",
            "type_identification": "CC",
            "rpa_batch_detail_scraping_id": 402,
            "url": "https://pwa.referencias.nuevaeps.com.co",
            "name": "NUEVA EPS",
            "username": "1018439363",
            "password": "Pandora2024**",
            "variables": "correo_electronico"
        },
        {
            "id": 402,
            "rpa_batch_scraping_id": 49,
            "identification": "71450598",
            "date_expedition": "03/12/1999",
            "type_identification": "CC",
            "rpa_batch_detail_scraping_id": 402,
            "url": "https://pwa.referencias.nuevaeps.com.co",
            "name": "NUEVA EPS",
            "username": "pymes3",
            "password": "Pymes1829",
            "variables": "correo_electronico"
        },
        {
            "id": 402,
            "rpa_batch_scraping_id": 49,
            "identification": "94324331",
            "date_expedition": "03/12/1999",
            "type_identification": "CC",
            "rpa_batch_detail_scraping_id": 402,
            "url": "https://pwa.referencias.nuevaeps.com.co",
            "name": "NUEVA EPS",
            "username": "pymes3",
            "password": "Pymes1829",
            "variables": "correo_electronico"
        },
        {
            "id": 402,
            "rpa_batch_scraping_id": 49,
            "identification": "87941635",
            "date_expedition": "03/12/1999",
            "type_identification": "CC",
            "rpa_batch_detail_scraping_id": 402,
            "url": "https://pwa.referencias.nuevaeps.com.co",
            "name": "NUEVA EPS",
            "username": "pymes3",
            "password": "Pymes1829",
            "variables": "correo_electronico"
        },
        {
            "id": 402,
            "rpa_batch_scraping_id": 49,
            "identification": "79710928",
            "date_expedition": "03/12/1999",
            "type_identification": "CC",
            "rpa_batch_detail_scraping_id": 402,
            "url": "https://pwa.referencias.nuevaeps.com.co",
            "name": "NUEVA EPS",
            "username": "pymes3",
            "password": "Pymes1829",
            "variables": "correo_electronico"
        },
        {
            "id": 402,
            "rpa_batch_scraping_id": 49,
            "identification": "41663997",
            "date_expedition": "03/12/1999",
            "type_identification": "CC",
            "rpa_batch_detail_scraping_id": 402,
            "url": "https://pwa.referencias.nuevaeps.com.co",
            "name": "NUEVA EPS",
            "username": "pymes3",
            "password": "Pymes1829",
            "variables": "correo_electronico"
        }
    ]
    asyncio.run(scraper.run("https://une.infokairos.com.co/user/login", debtors=debtors))