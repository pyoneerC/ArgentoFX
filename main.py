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


def scrape_blue_website():
    main_url = 'https://dolar-arg-app.netlify.app'
    page = requests.get(main_url)
    soup = BeautifulSoup(page.content, "html.parser")

    venta_elements = soup.find_all("div", class_="text-right")
    compra_elements = soup.find_all("div", class_=lambda value: value == "" or value is None)

    venta_value = extract_value(venta_elements[1], "Venta")
    compra_value = extract_value(compra_elements[2], "Compra")

    if venta_value and compra_value:
        promedio = (compra_value + venta_value) / 2
        return {
            "compra": f"{compra_value:.2f}",
            "venta": f"{venta_value:.2f}",
            "promedio": f"{promedio:.0f}"
        }
    return {"error": "Unable to extract data"}

def scrape_oficial_website():
    main_url = 'https://dolar-arg-app.netlify.app'
    page = requests.get(main_url)
    soup = BeautifulSoup(page.content, "html.parser")

    venta_elements = soup.find_all("div", class_="text-right")
    compra_elements = soup.find_all("div", class_=lambda value: value == "" or value is None)

    venta_value = extract_value(venta_elements[0], "Venta")
    compra_value = extract_value(compra_elements[0], "Compra")

    if venta_value and compra_value:
        promedio = (compra_value + venta_value) / 2
        return {
            "compra": f"{compra_value:.2f}",
            "venta": f"{venta_value:.2f}",
            "promedio": f"{promedio:.0f}"
        }
    return {"error": "Unable to extract data"}

@app.get("/blue")
async def scrape():
    return scrape_blue_website()


@app.get("/oficial")
async def scrape():
    return scrape_oficial_website()


@app.get("/MEP")
async def scrape():
    return


@app.get("/CCL")
async def scrape():
    return


@app.get("/Mayorista")
async def scrape():
    return


@app.get("/Cripto")
async def scrape():
    return


@app.get("/Tarjeta")
async def scrape():
    return


@app.get("/USD")
async def scrape():
    return


@app.get("/Euro")
async def scrape():
    return


@app.get("/Real")
async def scrape():
    return


@app.get("/Chilenos")
async def scrape():
    return
