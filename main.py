import httpx
from bs4 import BeautifulSoup
import requests
from fastapi import FastAPI, HTTPException

app = FastAPI()


def extract_value(element, type_value):
    try:
        value_text = element.text.replace(',', '.').replace('$', '').strip()
        value_text = ''.join(filter(lambda x: x.isdigit() or x == '.', value_text))
        return float(value_text)
    except ValueError as e:
        raise ValueError(f"Failed to convert {type_value} value to float: {e}")


def scrape_currency_website(currency_type, venta_index, compra_index):
    main_url = 'https://dolar-arg-app.netlify.app'
    try:
        response = requests.get(main_url)

        if response.status_code != 200:
            raise HTTPException(status_code=404,
                                detail=f"Failed to fetch the webpage: Status code {response.status_code}")

        soup = BeautifulSoup(response.content, "html.parser")

        venta_elements = soup.find_all("div", class_="text-right")
        compra_elements = soup.find_all("div", class_=lambda value: value == "" or value is None)

        if len(venta_elements) <= venta_index or len(compra_elements) <= compra_index:
            raise HTTPException(status_code=404, detail="Required elements not found or index out of range")

        venta_value = extract_value(venta_elements[venta_index], "Venta")
        compra_value = extract_value(compra_elements[compra_index], "Compra")

        promedio = (compra_value + venta_value) / 2

        return {
            "currency": currency_type,
            "compra": f"{compra_value:.2f}",
            "venta": f"{venta_value:.2f}",
            "promedio": f"{promedio:.2f}"
        }
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
async def scrape_usd():
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
async def scrape_chilenos():
    url = 'https://dolarhoy.com/cotizacion-peso-chileno'
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)

            if response.status_code != 200:
                raise HTTPException(status_code=404, detail="Failed to fetch the webpage")

            soup = BeautifulSoup(response.content, "html.parser")
            values = soup.find_all("div", class_="value")

            if len(values) < 2:
                raise HTTPException(status_code=404, detail="Required elements not found")

            # Extract the values and clean them
            compra_text = values[0].text.replace(',', '.').replace('$', '').strip()
            venta_text = values[1].text.replace(',', '.').replace('$', '').strip()

            compra = float(compra_text)
            venta = float(venta_text)
            promedio = (compra + venta) / 2

            return {
                "currency": "Chilenos",
                "compra": f"{compra:.2f}",
                "venta": f"{venta:.2f}",
                "promedio": f"{promedio:.2f}"
            }

    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request error: {e}")
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Value error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")