from fastapi import FastAPI, Query, Path, HTTPException
from typing import Optional
from pydantic import BaseModel
from . import data_scraper  # Importa il tuo modulo di scraping

app = FastAPI(
    title="AutoScout24 Scraper API",
    description="API per estrarre dati da AutoScout24",
    version="1.0.0"
)

params = {
    'cy': 'I',
    'damaged_listing': 'exclude',
    'kmto': '',
    'page': '1',
    'lat': '45.80393',
    'lon': '9.33157',
    'priceto': '',
    'ustate': 'N,U',
    'zip': '23841-annone-di-brianza',
    'zipr': '300'
}

class SearchParams(BaseModel):
    marca: str
    modello: str
    prezzo_max: Optional[int] = None
    km_max: Optional[int] = None
    anno_min: Optional[int] = None
    pagina: Optional[int] = 1

@app.get("/")
def read_root():
    return {"status": "online", "descrizione": "AutoScraper API, utilizza /docs per vedere la documentazione dell'API"}

@app.get("/prices/{marca}/{modello}")
def get_car_prices(
    marca: str = Path(..., description="Marca dell'auto (es. alfa-romeo)"),
    modello: str = Path(..., description="Modello dell'auto (es. giulietta)"),
    priceto: Optional[int] = Query(None, description="Prezzo massimo (es. 10000)"),
    kmto: Optional[int] = Query(None, description="Chilometraggio massimo (es. 100000)"),
    page: int = Query(1, description="Numero pagina dei risultati da cui partire (default: 1)")
):
    try:
        search_params = params.copy()
        search_params['page'] = str(page)
        
        if priceto is not None:
            search_params['priceto'] = str(priceto)
        
        if kmto is not None:
            search_params['kmto'] = str(kmto)
        
        print(f"Parametri di ricerca: {search_params}")
        
        risultati = data_scraper.get_car_prices(f"/{marca}/{modello}", search_params)
        return {
            "parametri": {
                "marca": marca,
                "modello": modello,
                "prezzo_max": priceto,
                "km_max": kmto,
                "pagina_partenza": page
            },
            "numero_risultati": len(risultati),
            "risultati": risultati
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante la ricerca: {str(e)}")
    
@app.get("/average_price/{marca}/{modello}")
def get_average_price(
    marca: str = Path(..., description="Marca dell'auto (es. audi)"),
    modello: str = Path(..., description="Modello dell'auto (es. a1)"),
    priceto: Optional[int] = Query(None, description="Prezzo massimo"),
    kmto: Optional[int] = Query(None, description="Chilometraggio massimo"),
    page: int = Query(1, description="Numero pagina dei risultati da cui partire")
):
    try:
        search_params = params.copy()
        search_params['page'] = str(page)
        
        if priceto is not None:
            search_params['priceto'] = str(priceto)
        
        if kmto is not None:
            search_params['kmto'] = str(kmto)
        
        print(f"Parametri di ricerca: {search_params}")

        risultati = data_scraper.get_car_prices(f"/{marca}/{modello}", search_params)
        if len(risultati) == 0:
            return {"errore": "Nessun risultato trovato"}
        
        somma_prezzi = sum([car['price'] for car in risultati])
        media_prezzi = somma_prezzi / len(risultati)
        return {
            "marca": marca,
            "modello": modello,
            "numero_risultati": len(risultati),
            "prezzo_medio": media_prezzi
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante il calcolo del prezzo medio: {str(e)}")