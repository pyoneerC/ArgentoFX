# Monedas API

## Overview
This project is a FastAPI application that provides real-time currency exchange rates by scraping various financial websites. It supports multiple currencies, including USD, Euro, Brazilian Real, Chilean Peso, Uruguayan Peso, and more. The API also offers a conversion feature that allows users to convert amounts between supported currencies.

## Features
- **Real-time Currency Rates**: Fetches the latest exchange rates for various currencies.
- **Currency Conversion**: Converts an amount from one currency to another using the latest exchange rates.
- **Comprehensive Currency Support**: Includes support for multiple currencies such as USD, Euro, ARS, BRL, CLP, UYU, and more.
- **Error Handling**: Implements robust error handling to manage and respond to potential issues during data fetching and processing.

## Endpoints

### Get Exchange Rates
- `/blue`
- `/oficial`
- `/mep`
- `/ccl`
- `/mayorista`
- `/cripto`
- `/tarjeta`
- `/usd`
- `/euro`
- `/real`
- `/clp`
- `/uru`
- `/oro`

Each endpoint returns the current exchange rate for the specified currency, including buy and sell prices, average rate, and spread.

- https://fastapiproject-1-eziw.onrender.com/docs

Returns the current status of the API, indicating whether it is "up" or "down".

## Setup and Installation

1. **Clone the Repository**
    
    ```bash
    git clone https://github.com/pyoneerC/monedas-api
    ```
   
2. **Install the Dependencies**

    ```bash
    cd monedas-api
    pip install -r requirements.txt
    ```
   
3. **Run the Application**

    ```bash
    uvicorn main:app --reload
    ```
   
4. **Access the API!**