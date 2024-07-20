from fastapi import FastAPI
from bs4 import BeautifulSoup
import requests
import time

app = FastAPI()


def extract_value(element, keyword):
    """Extract and clean the numeric value from the element."""
    if element:
        text = element.text.strip().replace(keyword, "").replace("$", "").strip()
        return float(text)
    return None


def scrape_currency_website(currency_type, venta_index, compra_index):
    main_url = 'https://dolar-arg-app.netlify.app'
    page = requests.get(main_url)
    soup = BeautifulSoup(page.content, "html.parser")

    venta_elements = soup.find_all("div", class_="text-right")
    compra_elements = soup.find_all("div", class_=lambda value: value == "" or value is None)

    venta_value = extract_value(venta_elements[venta_index], "Venta")
    compra_value = extract_value(compra_elements[compra_index], "Compra")

    if venta_value and compra_value:
        promedio = (compra_value + venta_value) / 2
        return {
            "currency": currency_type,
            "compra": f"{compra_value:.2f}",
            "venta": f"{venta_value:.2f}",
            "promedio": f"{promedio:.2f}"
        }
    return {"error": f"Unable to extract data for {currency_type}"}


@app.get("/blue")
async def scrape_blue():
    return scrape_currency_website("blue", 1, 2)


@app.get("/oficial")
async def scrape_oficial():
    return scrape_currency_website("oficial", 0, 1)


@app.get("/MEP")
async def scrape_mep():
    return scrape_currency_website("MEP", 2, 3)


@app.get("/CCL")
async def scrape_ccl():
    return scrape_currency_website("CCL", 3, 4)


@app.get("/Mayorista")
async def scrape_mayorista():
    return scrape_currency_website("Mayorista", 4, 5)


@app.get("/Cripto")
async def scrape_cripto():
    return scrape_currency_website("Cripto", 5, 6)


@app.get("/Tarjeta")
async def scrape_tarjeta():
    return scrape_currency_website("Tarjeta", 6, 7)

@app.get("/USD")
async def scrape():
    return {
        "blue": await scrape_blue(),
        "oficial": await scrape_oficial(),
        "MEP": await scrape_mep(),
        "CCL": await scrape_ccl(),
        "Mayorista": await scrape_mayorista(),
        "Cripto": await scrape_cripto(),
        "Tarjeta": await scrape_tarjeta()
    }


@app.get("/Euro")
async def scrape():
    return


@app.get("/Real")
async def scrape():
    return


@app.get("/Chilenos")
async def scrape():
    return
