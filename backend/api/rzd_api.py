"""
NonOfficial RZD Api by @snowlover4ever ❤️

GET /stations?part={name}
-------------------------
    Поиск кодов станций.
    Пример: /stations?part=Москва
    Response:
    {
        "stations": [
            {"station": "МОСКВА ОКТ", "code": 2006004},
            {"station": "МОСКВА КАЗ", "code": 2000003}
        ]
    }

GET /routes?code_from={c1}&code_to={c2}
---------------------------------------
    Список рейсов на сегодня.
    Статусы: SCH (план), APR (прибывает), ARR (посадка), ENR (в пути), DEP (ушел).
    Пример: /routes?code_from=2006004&code_to=2004001
    Response:
    {
    "info": {"origin": "МОСКВА", "destination": "СПБ"},
    "trains": [
        {
        "number": "054Ч",
        "route": "МОСКВА - СПБ",
        "ts_dep": "2023-10-27T23:30:00",
        "ts_arr": "2023-10-28T08:15:00",
        "is_express": false
        }
    ]
    }

GET /station_list?train_num={n}&code_from={c1}&code_to={c2}
-----------------------------------------------------------
    Маршрут поезда с остановками.
    Пример: /station_list?train_num=054Ч&code_from=2006004&code_to=2004001
    Response:
    {
    "train": "054Ч",
    "stops": [
        {
        "name": "ТВЕРЬ", 
        "code": "200092",
        "ts_arr": "2023-10-28T01:15:00",
        "ts_dep": "2025-11-28T04:09:30",
        "stop_min": 1,
        "is_target": false
        }
    ]
    }
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import httpx
from fastapi import APIRouter
from aiocache import cached, Cache

rzd_api = APIRouter()

# Настройки
TIMEOUT = 30
CACHE_TTL = 72000
URLS = {
    "SUGGEST": "https://ticket.rzd.ru/api/v1/suggests",
    "ROUTE": "https://ticket.rzd.ru/apib2b/p/Railway/V1/Search/TrainRoute",
    "PRICES": "https://ticket.rzd.ru/api/v1/railway-service/prices/train-pricing",
    "DEPARTED": "https://ticket.rzd.ru/api/v1/railway/departed",
}

client = httpx.AsyncClient(timeout=TIMEOUT)


@cached(ttl=CACHE_TTL, cache=Cache.MEMORY)
async def _fetch_stations_data(query: str) -> List[Dict]:
    """Ищем станции по названию."""
    params = {'Query': query, 'TransportType': 'rail', 'GroupResults': 'true'}
    try:
        resp = await client.get(URLS["SUGGEST"], params=params)
        resp.raise_for_status()
        q_upper = query.upper()
        return [
            {"station": s["name"].upper(), "code": int(s["expressCode"])}
            for s in resp.json().get("train", [])
            if s.get("expressCode") and q_upper in s.get("name", "").upper()
        ]
    except (httpx.HTTPError, KeyError, IndexError):
        return []
    

def normalize_time(time_str: str) -> str:
    """Нормализует время к формату HH:MM:SS."""
    parts = time_str.split(':')
    if len(parts) == 2:
        return f"{time_str}:00"
    return time_str


@cached(ttl=CACHE_TTL, cache=Cache.MEMORY)
async def _fetch_stops_data(number: str, c0: str, c1: str, p: str, s: str) -> Dict:
    """Получаем остановки для конкретного поезда."""
    params = {
        "TrainNumber": number, "Origin": c0, "Destination": c1,
        "DepartureDate": datetime.now().isoformat(),
        "Provider": p, "serviceProvider": s
    }
    try:
        resp = await client.get(URLS["ROUTE"], params=params)
        resp.raise_for_status()
        data = resp.json()
        stops_data = data.get("Routes", [{}])[0].get("RouteStops", [])
    except (httpx.HTTPError, KeyError, IndexError, ValueError):
        return {"train": number, "stops": []}

    stops, current_date, prev_time = [], datetime.today().date(), None
    target_codes = {int(c) for c in (c0, c1) if str(c).isdigit()}

    for stop in stops_data:
        t_arr_str, t_dep_str = stop.get("ArrivalTime"), stop.get("DepartureTime")
        
        # Обработка отсутствующих или пустых времен
        if not t_arr_str or t_arr_str == '':
            ts_arr = "Н/Д"
            full_arr = None
        else:
            dt_arr_time = datetime.strptime(normalize_time(t_arr_str), "%H:%M:%S").time()
            if prev_time and dt_arr_time < prev_time:
                current_date += timedelta(days=1)
            prev_time = dt_arr_time
            full_arr = datetime.combine(current_date, dt_arr_time)
            ts_arr = full_arr.isoformat()
        
        if not t_dep_str or t_dep_str == '':
            ts_dep = "Н/Д"
            full_dep = None
            status = "Н/Д"
        else:
            dt_dep_time = datetime.strptime(normalize_time(t_dep_str), "%H:%M:%S").time()
            full_dep = datetime.combine(current_date, dt_dep_time)
            if full_arr and full_dep < full_arr:
                full_dep += timedelta(days=1)
            ts_dep = full_dep.isoformat()
            
            # Вычисляем статус только если есть время отправления
            rem_min = int((full_dep - datetime.now()).total_seconds() / 60)
            status = "DEP" if datetime.now() > full_dep else ("ARR/APR" if 0 <= rem_min <= 20 else "SCH")

        stops.append({
            "name": stop.get("StationName", "Н/Д"),
            "code": stop.get("StationCode", "Н/Д"),
            "ts_arr": ts_arr,
            "ts_dep": ts_dep,
            "stop_min": stop.get("StopDuration", "Н/Д"),
            "is_target": stop.get("StationCode") in target_codes,
            "status": status if 'status' in locals() else "Н/Д"
        })

    return {"train": number, "stops": stops}


async def _get_real_route(train_num: str, c0: str, c1: str, fallback: str, provider: str, service: str) -> str:
    """Получает реальный маршрут поезда (первая → последняя станция)."""
    try:
        stops_data = await _fetch_stops_data(train_num, c0, c1, provider, service)
        stops = stops_data.get("stops", [])
        if stops and len(stops) >= 2:
            return f"{stops[0]['name']} - {stops[-1]['name']}"
        elif stops:
            return stops[0]['name']
    except Exception as e:
        print(e)
        pass
    print(f"n: {train_num} > {fallback}")
    return fallback


@cached(ttl=300, cache=Cache.MEMORY)
async def _fetch_routes_data(c0: str, c1: str) -> Dict:
    """Получаем поезда между двумя станциями."""
    today = datetime.now().strftime("%d.%m.%Y")
    tasks = [
        client.get(URLS["PRICES"], params={
            "service_provider": "B2B_RZD", 
            "origin": c0, 
            "destination": c1, 
            "departureDate": today
        }),
        client.post(URLS["DEPARTED"], json={
            "departureExpressCode": c0, 
            "arrivalExpressCode": c1
        })
    ]
    responses = await asyncio.gather(*tasks, return_exceptions=True)

    actual_data = responses[0].json() if isinstance(responses[0], httpx.Response) and responses[0].status_code == 200 else {}
    departed_data = responses[1].json() if isinstance(responses[1], httpx.Response) and responses[1].status_code == 200 else []

    # Собираем базовую информацию о поездах
    trains_base = []
    t: dict[str, any]
    for t in departed_data + actual_data.get("Trains", []):
        try:
            dep = datetime.fromisoformat(t.get("DepartureDateTime") or t.get("DepartureTime"))
            arr = datetime.fromisoformat(t.get("ArrivalDateTime") or t.get("ArrivalTime"))
            if (origin := t.get('OriginName', 'Н/Д')) is None: origin = t.get("TrainName", "Н/Д")
            if (dest := t.get('DestinationName', 'Н/Д')) is None: dest = t.get("TrainName", "Н/Д")
            if (description := t.get("TrainDescription")) == '' or description is None: 
                if t.get("Provider", "P1") == "P1":
                    description = "СК"
                else:
                    description = "пригородный"
            trains_base.append({
                "name": t.get("TrainName") or '',
                "type": description,
                "number": t.get("TrainNumber"),
                "ts_dep": dep,
                "ts_arr": arr,
                "is_express": t.get("CategoryId") == 2,
                "class": t.get("TrainClassNames"),
                "fallback_route": f"{origin} - {dest}",
                "provider": t.get("Provider") or "P1",
                "service": t.get("ServiceProvider") or "B2B_RZD"
            })
        except (ValueError, TypeError):
            continue
    
    # Параллельно получаем реальные маршруты для всех поездов
    route_tasks = [
        _get_real_route(t["number"], c0, c1, t["fallback_route"], t["provider"], t["service"]) 
        for t in trains_base
    ]
    real_routes = await asyncio.gather(*route_tasks)

    # Формируем финальный список (ВКЛЮЧАЕМ provider и service!)
    processed_trains = [
        {
            "name": train["name"],
            "type": train["type"],
            "number": train["number"],
            "route": route,
            "ts_dep": train["ts_dep"].isoformat(),
            "ts_arr": train["ts_arr"].isoformat(),
            "is_express": train["is_express"],
            "class": train["class"],
            "provider": train["provider"],      # ← Добавлено
            "service": train["service"]         # ← Добавлено
        }
        for train, route in zip(trains_base, real_routes)
    ]

    return {
        "info": {
            "origin": actual_data.get("OriginStationName", "Н/Д"),
            "destination": actual_data.get("DestinationStationName", "Н/Д")
        },
        "trains": sorted(processed_trains, key=lambda x: x["ts_dep"])
    }


async def _find_train_provider_service(
    train_num: str, 
    code_from: str, 
    code_to: str
) -> Tuple[Optional[str], Optional[str]]:
    """Находит provider и service для указанного поезда."""
    routes_data = await _fetch_routes_data(code_from, code_to)
    
    for train in routes_data.get("trains", []):
        if train.get("number") == train_num:
            return train.get("provider"), train.get("service")
    
    # Поезд не найден - возвращаем дефолтные значения
    return None, None


@rzd_api.get("/stations")
async def get_stations(part: str):
    """Поиск станции по названию"""
    return {"stations": await _fetch_stations_data(part)}


@rzd_api.get("/routes")
async def get_routes(code_from: str, code_to: str):
    """Получение списка рейсов между станциями"""
    data = await _fetch_routes_data(code_from, code_to)
    return data if data.get("trains") else {"status": "Not Found", "trains": []}


@rzd_api.get("/station_list")
async def get_station_list(train_num: str, str_from: str, str_to: str):
    """Маршрут конкретного поезда"""
    stations_from = await _fetch_stations_data(str_from)
    stations_to = await _fetch_stations_data(str_to)
    code_from = stations_from[0].get("code")
    code_to = stations_to[0].get("code")
    provider, service = await _find_train_provider_service(
        train_num, code_from, code_to
    )

    print(provider, service)
    # Если поезд не найден в маршрутах - используем дефолтные значения
    if provider is None:
        provider = "P1"
    if service is None:
        service = "B2B_RZD"
    
    return await _fetch_stops_data(train_num, code_from, code_to, provider, service)


@rzd_api.on_event("shutdown")
async def shutdown_event():
    await client.aclose()