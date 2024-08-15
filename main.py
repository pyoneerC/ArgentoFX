import json
from functools import lru_cache

import httpx
from bs4 import BeautifulSoup
import requests
from fastapi import FastAPI, HTTPException, Depends
import redis
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(
    title="ArgentoFX",
    description="API RESTful para obtener cotizaciones de divisas extranjeras en vivo, en Argentina.",
    version="4.0.0",
    openapi_tags=[
        {"name": "usd", "description": "Cotizaciones del dólar"},
        {"name": "otros", "description": "Cotizaciones de otras divisas"},
        {"name": "status", "description": "Estado del servidor"},
    ],
    contact={
        "name": "Max Comperatore",
        "url": "https://maxcomperatore.com",
        "email": "maxcomperatore@gmail.com"
    },
    license_info={
        "name": "Unlicense",
        "url": "https://unlicense.org"
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

r = redis.Redis(
    host='assured-shrew-49745.upstash.io',
    port=6379,
    password='AcJRAAIjcDFkZmQ4MzA5NGM2MjU0NTNlOWI4OTVjYzNiODAwZjY5MnAxMA',
    ssl=True
)

def extract_value(element, type_value):
    try:
        value_text = element.text.replace(",", ".").replace("$", "").strip()
        value_text = "".join(filter(lambda x: x.isdigit() or x == ".", value_text))
        return float(value_text)
    except ValueError as e:
        raise ValueError(f"Failed to convert {type_value} value to float: {e}")


@lru_cache(maxsize=7)
def scrape_currency_website(currency_type, venta_index, compra_index):
    main_url = "https://dolar-arg-app.netlify.app"
    cache_value = r.get(currency_type.lower())
    if cache_value:
        return json.loads(cache_value)

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

        r.setex(currency_type.lower(), 6000, json.dumps(result))

        return result

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Request error: {e}")
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Value error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")


@lru_cache(maxsize=4)
def scrape_dolar_hoy(category):
    url = f"https://dolarhoy.com/cotizacion-{category}"
    cache_value = r.get(category)
    if cache_value:
        return eval(cache_value)

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

        r.setex(category, 6000, str(result))

        return result

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Request error: {e}")
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Value error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")


@app.get("/blue", tags=["usd"], summary="Cotización del dólar blue")
async def scrape_blue():
    return scrape_currency_website("blue", 1, 2)


@app.get("/oficial", tags=["usd"], summary="Cotización del dólar oficial")
async def scrape_oficial():
    return scrape_currency_website("oficial", 0, 1)


@app.get("/mep", tags=["usd"], summary="Cotización del dólar MEP")
async def scrape_mep():
    return scrape_currency_website("MEP", 2, 3)


@app.get("/ccl", tags=["usd"], summary="Cotización del dólar CCL")
async def scrape_ccl():
    return scrape_currency_website("CCL", 3, 4)


@app.get("/mayorista", tags=["usd"], summary="Cotización del dólar mayorista")
async def scrape_mayorista():
    return scrape_currency_website("Mayorista", 4, 5)


@app.get("/cripto", tags=["usd"], summary="Cotización del dólar cripto")
async def scrape_cripto():
    return scrape_currency_website("Cripto", 5, 6)


@app.get("/tarjeta", tags=["usd"], summary="Cotización del dólar tarjeta")
async def scrape_tarjeta():
    return scrape_currency_website("Tarjeta", 6, 7)


@app.get("/usd", tags=["usd"], summary="Cotizaciones del dólar")
async def scrape_usd():
    cache_value = r.get("usd")
    if cache_value:
        return eval(cache_value)

    result = {
        "blue": await scrape_blue(),
        "oficial": await scrape_oficial(),
        "MEP": await scrape_mep(),
        "CCL": await scrape_ccl(),
        "Mayorista": await scrape_mayorista(),
        "Cripto": await scrape_cripto(),
        "Tarjeta": await scrape_tarjeta(),
    }

    r.setex("usd", 6000, str(result))
    return result


@app.get("/euro", tags=["otros"], summary="Cotización del euro")
async def scrape_euro():
    return scrape_dolar_hoy("euro")


@app.get("/real", tags=["otros"], summary="Cotización del real")
async def scrape_real():
    return scrape_dolar_hoy("real-brasileno")


@app.get("/clp", tags=["otros"], summary="Cotización del peso chileno")
async def scrape_chilenos():
    return scrape_dolar_hoy("peso-chileno")


@app.get("/uru", tags=["otros"], summary="Cotización del peso uruguayo")
async def scrape_uruguayos():
    return scrape_dolar_hoy("peso-uruguayo")


@app.get("/cotizaciones", tags=["otros"], summary="Cotizaciones de otras divisas")
async def scrape_all():
    cache_value = r.get("cotizaciones")
    if cache_value:
        return eval(cache_value)

    result = {
        "usd": await scrape_usd(),
        "euro": await scrape_euro(),
        "real": await scrape_real(),
        "clp": await scrape_chilenos(),
        "uru": await scrape_uruguayos(),
    }

    r.setex("cotizaciones", 6000, str(result))
    return result


@app.get("/", tags=["status"], summary="Estado del servidor")
async def status():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://example.com")
            if response.status_code == 200:
                return {"status": "OK"}
            else:
                return {"status": "DOWN"}

    except Exception as e:
        return {"status": "DOWN ", "error": str(e)}
