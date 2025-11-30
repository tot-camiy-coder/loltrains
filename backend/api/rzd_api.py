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
from typing import Dict, List

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


#! ПЕРЕНЕСТИ НА FRONTEND!
def get_train_status(dep: datetime, arr: datetime) -> str:
    """Определяет статус поезда по времени."""
    n = datetime.now()
    if dep < n < arr: return "ENR"  # В пути
    if n > arr: return "DEP"  # Прибыл/ушел (упрощено)
    if n >= dep - timedelta(minutes=5): return "ARR"  # Посадка
    if n >= dep - timedelta(minutes=25): return "APR"  # Прибывает
    return "SCH"  # По расписанию


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


@cached(ttl=CACHE_TTL, cache=Cache.MEMORY)
async def _fetch_stops_data(number: str, c0: str, c1: str) -> Dict:
    """Получаем остановки для конкретного поезда."""
    params = {
        "TrainNumber": number, "Origin": c0, "Destination": c1,
        "DepartureDate": datetime.now().strftime("%Y-%m-%dT00:00:00"),
        "Provider": "P13", "serviceProvider": "B2B_RZD"
    }
    try:
        resp = await client.get(URLS["ROUTE"], params=params)
        resp.raise_for_status()
        data = resp.json()
        stops_data = data.get("Routes", [{}])[0].get("RouteStops", [])
    except (httpx.HTTPError, KeyError, IndexError, ValueError):
        return {"train": number, "stops": []}

    stops, current_date, prev_time = [], datetime.today().date(), None
    target_codes = {int(c) for c in (c0, c1) if c.isdigit()}

    for stop in stops_data:
        t_arr_str, t_dep_str = stop.get("ArrivalTime"), stop.get("DepartureTime")
        if not t_arr_str or not t_dep_str: continue

        # Логика для определения даты остановки (с учетом пересечения полуночи)
        dt_arr_time = datetime.strptime(t_arr_str, "%H:%M:%S").time()
        if prev_time and dt_arr_time < prev_time:
            current_date += timedelta(days=1)
        prev_time = dt_arr_time

        full_arr = datetime.combine(current_date, dt_arr_time)
        full_dep = datetime.combine(current_date, datetime.strptime(t_dep_str, "%H:%M:%S").time())
        if full_dep < full_arr: full_dep += timedelta(days=1)

        rem_min = int((full_dep - datetime.now()).total_seconds() / 60)
        status = "DEP" if datetime.now() > full_dep else ("ARR/APR" if 0 <= rem_min <= 20 else "SCH")

        stops.append({
            "name": stop.get("StationName"), "code": stop.get("StationCode"),
            "ts_arr": full_arr.isoformat(), "ts_dep": full_dep.isoformat(),
            "stop_min": stop.get("StopDuration", 0),
            "is_target": stop.get("StationCode") in target_codes
        })

    return {"train": number, "stops": stops}


async def _get_real_route(train_num: str, c0: str, c1: str, fallback: str) -> str:
    """Получает реальный маршрут поезда (первая → последняя станция)."""
    try:
        stops_data = await _fetch_stops_data(train_num, c0, c1)
        stops = stops_data.get("stops", [])
        if stops and len(stops) >= 2:
            return f"{stops[0]['name']} - {stops[-1]['name']}"
        elif stops:
            return stops[0]['name']
    except Exception:
        pass
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
    for t in departed_data + actual_data.get("Trains", []):
        try:
            dep = datetime.fromisoformat(t.get("DepartureDateTime") or t.get("DepartureTime"))
            arr = datetime.fromisoformat(t.get("ArrivalDateTime") or t.get("ArrivalTime"))
            trains_base.append({
                "number": t.get("TrainNumber"),
                "ts_dep": dep,
                "ts_arr": arr,
                "is_express": t.get("CategoryId") == 2,
                # Fallback на случай если не получим остановки
                "fallback_route": f"{t.get('OriginName', 'Н/Д')} - {t.get('DestinationName', 'Н/Д')}"
            })
        except (ValueError, TypeError):
            continue

    # Параллельно получаем реальные маршруты для всех поездов
    route_tasks = [
        _get_real_route(t["number"], c0, c1, t["fallback_route"]) 
        for t in trains_base
    ]
    real_routes = await asyncio.gather(*route_tasks)

    # Формируем финальный список
    processed_trains = [
        {
            "number": train["number"],
            "route": route,  # ← Теперь тут реальный маршрут!
            "ts_dep": train["ts_dep"].isoformat(),
            "ts_arr": train["ts_arr"].isoformat(),
            "is_express": train["is_express"]
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
async def get_station_list(train_num: str, code_from: str, code_to: str):
    """Маршрут конкретного поезда"""
    return await _fetch_stops_data(train_num, code_from, code_to)


@rzd_api.on_event("shutdown")
async def shutdown_event():
    await client.aclose()