import requests
from bs4 import BeautifulSoup

# Base parts of the URL
scheme = 'https'
netloc = 'www.autoscout24.it/lst'    
# Dichiara esplicitamente la variabile globale
list_of_cars = []

def _scrape_prices_from_website(path: str, params: dict) -> list[dict]:
    """Funzione che raccoglie i prezzi dalle pagine web"""
    global list_of_cars
    
    current_page = int(params.get('page', 1))
        
    print(f"Requesting page {current_page} with params: {params}")
    
    response = requests.get(f'https://{netloc}{path}', params=params)
    if response.status_code == 200 and response.text != '':
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        price_paragraphs = soup.find_all('p', class_='Price_price__APlgs PriceAndSeals_current_price__ykUpx')
        km_spans = soup.find_all('span', {'aria-label': 'Chilometraggio'})
        
        # Prima creiamo tutte le auto con i prezzi
        cars = []
        if price_paragraphs:
            for p in price_paragraphs:
                price_text = p.text.replace('€', '').replace('.', '').replace(',', '').replace('-', '').strip()
                if price_text:
                    try:
                        price_value = int(price_text)
                        car = {
                            'price': price_value,
                            'km': 0  # Inizializza con 0 invece di stringa vuota
                        }
                        cars.append(car)
                    except ValueError:
                        print(f"Non posso convertire '{price_text}' in int, lo ignoro")
        
        # Poi aggiungiamo i km alle auto create
        if km_spans and cars:
            for i, km in enumerate(km_spans):
                if i < len(cars):  # Assicurati che ci sia un'auto corrispondente
                    km_text = km.text.replace(' km', '').replace('.', '').strip()
                    if km_text:
                        try:
                            km_value = int(km_text)
                            cars[i]['km'] = km_value
                        except ValueError:
                            print(f"Non posso convertire '{km_text}' in int, lo ignoro")
            
            # Aggiungi le auto alla lista globale
            list_of_cars.extend(cars)
            
            # Copia i parametri per evitare di modificare quelli originali
            next_params = params.copy()
            next_params['page'] = str(current_page + 1)
            _scrape_prices_from_website(path, next_params)
    else:
        print(f'Failed to retrieve page. Status code: {response.status_code}')
    
    return list_of_cars

def get_car_prices(path: str, params: dict) -> list[dict]:
    """
    Cerca prezzi auto su AutoScout24 con i parametri specificati
    """
    # Resetta la lista dei prezzi all'inizio di ogni chiamata
    global list_of_cars
    list_of_cars = []

    all_cars = _scrape_prices_from_website(path, params)
    print(f"Total cars collected: {len(all_cars)}")
    
    filtered_cars = all_cars.copy()  # Inizia con tutte le auto
    
    # Filtra per prezzo se specificato
    if params.get('priceto') and str(params.get('priceto')).strip() != '':
        try:
            max_price = int(params.get('priceto'))
            print(f"Filtering by max price: {max_price}")
            filtered_cars = [car for car in filtered_cars if car['price'] <= max_price]
            print(f"Cars after price filter: {len(filtered_cars)}")
        except ValueError:
            print(f"Impossibile convertire priceto '{params.get('priceto')}' in int")

    # Filtra per km se specificato
    if params.get('kmto') and str(params.get('kmto')).strip() != '':
        try:
            max_km = int(params.get('kmto'))
            print(f"Filtering by max km: {max_km}")
            # Filtra solo auto con km <= max_km
            filtered_cars = [car for car in filtered_cars if isinstance(car['km'], int) and car['km'] <= max_km]
            print(f"Cars after km filter: {len(filtered_cars)}")
        except ValueError:
            print(f"Impossibile convertire kmto '{params.get('kmto')}' in int")
            
    return filtered_cars