from fastapi import FastAPI
from bs4 import BeautifulSoup
import requests
import time

app = FastAPI()

cache = {"data": None, "timestamp": 0}
cache_duration = 60 * 30  # 30 minutes


def scrape_website(idx: int):
    global cache
    current_time = time.time()

    if cache["data"] and (current_time - cache["timestamp"] < cache_duration):
        return cache["data"]

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

    # Update cache with new data
    scraped_data = {
        "compra": "example_compra",  # Replace with actual data
        "venta": "example_venta",  # Replace with actual data
        "promedio": "example_promedio"  # Replace with actual data
    }
    cache = {"data": scraped_data, "timestamp": current_time}

    return scraped_data


def scrape_extra(idx: int):
    return


@app.get("/oficial")
async def scrape():
    return scrape_website(0)


@app.get("/blue")
async def scrape():
    return scrape_website(1)


@app.get("/MEP")
async def scrape():
    return scrape_website(2)


@app.get("/CCL")
async def scrape():
    return scrape_website(3)


@app.get("/Mayorista")
async def scrape():
    return scrape_website(4)


@app.get("/Cripto")
async def scrape():
    return scrape_website(5)


@app.get("/Tarjeta")
async def scrape():
    return scrape_website(6)


@app.get("/USD")
async def scrape():
    return scrape_website(7)


@app.get("/Euro")
async def scrape():
    return scrape_extra(0)


@app.get("/Real")
async def scrape():
    return scrape_extra(1)


@app.get("/Chilenos")
async def scrape():
    return scrape_extra(2)
