from fastapi import FastAPI, HTTPException
from bs4 import BeautifulSoup
import requests

app = FastAPI()


def scrape_website():
    url = 'https://dolar-arg-app.netlify.app'
    page = requests.get(url)

    soup = BeautifulSoup(page.content, "html.parser")
    data_blue_venta = soup.find_all("div", class_="text-right")

    data_blue_compra = soup.find_all("div", class_=lambda value: value == "" or value is None)

    data_blue_venta = data_blue_venta[1].text.strip().replace("Venta", "").replace("$", "").lstrip()
    data_blue_compra = data_blue_compra[2].text.strip().replace("Compra", "").replace("$", "").lstrip()
    promedio = (float(data_blue_compra) + float(data_blue_venta)) / 2

    return {"compra": data_blue_compra,
            "venta": data_blue_venta,
            "promedio": f"{promedio:.0f}"
            }


@app.get("/blue")
async def scrape():
    return scrape_website()
