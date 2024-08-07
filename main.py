import httpx
from bs4 import BeautifulSoup
import requests
from fastapi import FastAPI, HTTPException
import redis
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

r = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=6379,
    password=os.getenv("REDIS_PASSWORD"),
    ssl=True
)


def extract_value(element, type_value):
    try:
        value_text = element.text.replace(",", ".").replace("$", "").strip()
        value_text = "".join(filter(lambda x: x.isdigit() or x == ".", value_text))
        return float(value_text)
    except ValueError as e:
        raise ValueError(f"Failed to convert {type_value} value to float: {e}")


def scrape_currency_website(currency_type, venta_index, compra_index):
    main_url = "https://dolar-arg-app.netlify.app"
    cache_key = currency_type
    cached_value = r.get(cache_key)
    if cached_value:
        return eval(cached_value)

    try:
        response = requests.get(main_url)

        if response.status_code != 200:
            raise HTTPException(
                status_code=404,
                detail=f"Failed to fetch the webpage: Status code {response.status_code}",
            )

        soup = BeautifulSoup(response.content, "html.parser")

        venta_elements = soup.find_all("div", class_="text-right")
        compra_elements = soup.find_all(
            "div", class_=lambda value: value == "" or value is None
        )

        if len(venta_elements) <= venta_index or len(compra_elements) <= compra_index:
            raise HTTPException(
                status_code=404,
                detail="Required elements not found or index out of range",
            )

        venta_value = extract_value(venta_elements[venta_index], "Venta")
        compra_value = extract_value(compra_elements[compra_index], "Compra")

        promedio = (compra_value + venta_value) / 2

        result = {
            "currency": currency_type,
            "compra": f"{compra_value:.2f} ARS",
            "venta": f"{venta_value:.2f} ARS",
            "promedio": f"{promedio:.2f} ARS",
            "spread": f"{venta_value - compra_value:.2f} ARS",
        }

        r.setex(currency_type, 1200, str(result))

        return result

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Request error: {e}")
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Value error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")


def scrape_dolar_hoy(category):
    url = f"https://dolarhoy.com/cotizacion-{category}"
    cache_key = f"{category}_value"
    cached_value = r.get(cache_key)
    if cached_value:
        return eval(cached_value)

    try:
        response = requests.get(url)

        if response.status_code != 200:
            raise HTTPException(
                status_code=404, detail="Failed to fetch the webpage"
            )

        soup = BeautifulSoup(response.content, "html.parser")
        values = soup.find_all("div", class_="value")

        if len(values) < 2:
            raise HTTPException(
                status_code=404, detail="Required elements not found"
            )

        compra_text = values[0].text.replace(",", ".").replace("$", "").strip()
        venta_text = values[1].text.replace(",", ".").replace("$", "").strip()

        compra = float(compra_text)
        venta = float(venta_text)
        promedio = (compra + venta) / 2

        result = {
            "currency": category.capitalize(),
            "compra": f"{compra:.2f} ARS",
            "venta": f"{venta:.2f} ARS",
            "promedio": f"{promedio:.2f} ARS",
            "spread": f"{venta - compra:.2f} ARS",
        }

        r.setex(cache_key, 1200, str(result))

        return result

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Request error: {e}")
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Value error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")


@app.get("/blue")
async def scrape_blue():
    return scrape_currency_website("blue", 1, 2)


@app.get("/oficial")
async def scrape_oficial():
    return scrape_currency_website("oficial", 0, 1)


@app.get("/mep")
async def scrape_mep():
    return scrape_currency_website("MEP", 2, 3)


@app.get("/ccl")
async def scrape_ccl():
    return scrape_currency_website("CCL", 3, 4)


@app.get("/mayorista")
async def scrape_mayorista():
    return scrape_currency_website("Mayorista", 4, 5)


@app.get("/cripto")
async def scrape_cripto():
    return scrape_currency_website("Cripto", 5, 6)


@app.get("/tarjeta")
async def scrape_tarjeta():
    return scrape_currency_website("Tarjeta", 6, 7)


@app.get("/usd")
async def scrape_usd():
    return {
        "blue": await scrape_blue(),
        "oficial": await scrape_oficial(),
        "MEP": await scrape_mep(),
        "CCL": await scrape_ccl(),
        "Mayorista": await scrape_mayorista(),
        "Cripto": await scrape_cripto(),
        "Tarjeta": await scrape_tarjeta(),
    }


@app.get("/euro")
async def scrape_euro():
    return scrape_dolar_hoy("euro")


@app.get("/real")
async def scrape_real():
    return scrape_dolar_hoy("real-brasileno")


@app.get("/clp")
async def scrape_chilenos():
    return scrape_dolar_hoy("peso-chileno")


@app.get("/uru")
async def scrape_uruguayos():
    return scrape_dolar_hoy("peso-uruguayo")


@app.get("/cotizaciones")
async def scrape_all():
    return {
        "usd": await scrape_usd(),
        "euro": await scrape_euro(),
        "real": await scrape_real(),
        "clp": await scrape_chilenos(),
        "uru": await scrape_uruguayos(),
    }


@app.get("/")
async def status():
    cache_key = "status"
    cache_value = r.get(cache_key)
    if cache_value:
        return eval(cache_value)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://example.com")
            if response.status_code == 200:
                r.setex(cache_key, 600, '{"status": "UP"}')
                return {"status": "OK"}
            else:
                r.setex(cache_key, 600, '{"status": "DOWN"}')
                return {"status": "DOWN"}


    except Exception as e:
        return {"status": "DOWN ", "error": str(e)}
