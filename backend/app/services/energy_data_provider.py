from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, List, Optional, Tuple

import httpx

Snapshot = Dict[Tuple[str, str], float]
MeterDelta = Dict[str, Any]


class RealDataUnavailable(Exception):
    """Raised when live energy data cannot be retrieved."""


class RealDataRequestError(RealDataUnavailable):
    """Raised when station data cannot be reached."""


DEFAULT_TIMEOUT = httpx.Timeout(timeout=1.5, connect=0.5, read=1.0)
DEFAULT_WINDOW_PROFILES: List[Tuple[int, int]] = [
    (4, 4),  # ±4 minutes for near-real-time snapshots
    (12, 6),  # widen window if immediate data missing
    (24, 6),  # fallback to a broader historical window
]
LONG_WINDOW_PROFILES: List[Tuple[int, int]] = [
    (30, 15),
    (60, 20),
    (90, 30),
]
DAILY_WINDOW_PROFILES: List[Tuple[int, int]] = [
    (60, 60),  # ±1 hour
    (120, 90),  # ±2 hours
    (240, 120),  # ±4 hours fallback
]
# MAX_CONCURRENT_REQUESTS removed (sequential snapshot loading)
CATEGORY_KEYWORDS: List[Tuple[str, str]] = [
    ("冷机", "冷机系统"),
    ("冷冻水泵", "水泵系统"),
    ("冷却水泵", "水泵系统"),
    ("水泵", "水泵系统"),
    ("冷却塔", "冷却塔"),
    ("照明", "照明系统"),
    ("照", "照明系统"),
    ("风机", "通风系统"),
    ("空调", "空调系统"),
    ("送风", "通风系统"),
    ("排风", "通风系统"),
    ("电扶梯", "电扶梯"),
    ("扶梯", "电扶梯"),
]


def _safe_float(value: Any) -> Optional[float]:
    try:
        if value in (None, "", "null"):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_time(value: Any) -> Optional[datetime]:
    if not value or not isinstance(value, str):
        return None
    candidate = value.replace("T", " ")
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(candidate, fmt)
        except ValueError:
            continue
    return None


def _select_value_near_timestamp(values: Any, timestamp: datetime) -> Optional[float]:
    if not isinstance(values, list) or not values:
        return None

    closest_value: Optional[float] = None
    closest_delta: Optional[float] = None
    for value_entry in values:
        ts = _parse_time(value_entry.get("time"))
        val = _safe_float(value_entry.get("value"))
        if ts is None or val is None:
            continue
        delta = abs((ts - timestamp).total_seconds())
        if closest_delta is None or delta < closest_delta:
            closest_delta = delta
            closest_value = val
    return closest_value


async def _fetch_snapshot_once(
    client: httpx.AsyncClient,
    station_cfg: Dict[str, Any],
    timestamp: datetime,
    before_min: int,
    after_min: int,
) -> Snapshot:
    ip = station_cfg.get("ip") or station_cfg.get("station_ip")
    data_codes = station_cfg.get("data_codes") or []
    object_codes = station_cfg.get("object_codes") or []

    if not ip or not data_codes or not object_codes:
        raise RealDataUnavailable("station configuration missing required fields")

    start_ms = int((timestamp - timedelta(minutes=before_min)).timestamp() * 1000)
    end_ms = int((timestamp + timedelta(minutes=after_min)).timestamp() * 1000)
    if end_ms <= start_ms:
        end_ms = start_ms + 60_000

    payload = {
        "dataCodes": data_codes,
        "objectCodes": object_codes,
        "measurement": "realData",
        "startTime": start_ms,
        "endTime": end_ms,
        "fill": "0",
        "funcName": "",
        "funcTime": "",
    }
    url = f"http://{ip}:9898/data/selectHisData"

    try:
        response = await client.post(url, json=payload)
        response.raise_for_status()
    except httpx.HTTPError as exc:  # pragma: no cover - network failure
        raise RealDataRequestError(f"request failed: {exc}") from exc

    data_block = response.json().get("data")
    if not data_block:
        raise RealDataUnavailable("no data returned from station")

    snapshot: Snapshot = {}
    for entry in data_block:
        tags = entry.get("tags") or {}
        obj_code = tags.get("objectCode")
        data_code = tags.get("dataCode")
        if not obj_code or not data_code:
            continue

        closest_value = _select_value_near_timestamp(entry.get("values"), timestamp)
        if closest_value is not None:
            snapshot[(obj_code, data_code)] = closest_value

    if not snapshot:
        raise RealDataUnavailable("empty snapshot after parsing")

    return snapshot


async def fetch_snapshot(
    client: httpx.AsyncClient,
    station_cfg: Dict[str, Any],
    timestamp: datetime,
    window_profiles: Optional[Iterable[Tuple[int, int]]] = None,
) -> Snapshot:
    profiles = list(window_profiles) if window_profiles else DEFAULT_WINDOW_PROFILES
    last_exc: Optional[Exception] = None
    for before_min, after_min in profiles:
        try:
            return await _fetch_snapshot_once(
                client, station_cfg, timestamp, before_min, after_min
            )
        except RealDataRequestError as exc:
            last_exc = exc
            break
        except RealDataUnavailable as exc:
            last_exc = exc
            continue
    raise RealDataUnavailable(str(last_exc) if last_exc else "snapshot unavailable")


async def fetch_snapshots(
    client: httpx.AsyncClient,
    station_cfg: Dict[str, Any],
    timestamps: List[datetime],
    window_profiles: Optional[Iterable[Tuple[int, int]]] = None,
) -> Dict[datetime, Snapshot]:
    if not timestamps:
        return {}

    snapshots: Dict[datetime, Snapshot] = {}
    for ts in timestamps:
        snapshots[ts] = await fetch_snapshot(client, station_cfg, ts, window_profiles)
    return snapshots


def aggregate_delta(
    station_cfg: Dict[str, Any],
    start_snapshot: Snapshot,
    end_snapshot: Snapshot,
) -> Tuple[float, List[MeterDelta]]:
    data_codes = station_cfg.get("data_codes") or []
    object_codes = station_cfg.get("object_codes") or []
    data_list = station_cfg.get("data_list") or []

    total = 0.0
    per_meter: List[MeterDelta] = []

    for idx, data_code in enumerate(data_codes):
        meter_info = data_list[idx] if idx < len(data_list) else {}
        meter_name = meter_info.get("p3") or meter_info.get("name") or data_code
        record: MeterDelta = {
            "name": meter_name,
            "data_code": data_code,
            "object_code": None,
            "start": None,
            "end": None,
            "delta": None,
        }

        for object_code in object_codes:
            key = (object_code, data_code)
            start_val = start_snapshot.get(key)
            end_val = end_snapshot.get(key)
            if start_val is None or end_val is None:
                continue

            delta = end_val - start_val
            if delta < -1:  # filter out obvious counter resets
                delta = 0.0
            delta = max(delta, 0.0)

            record.update(
                {
                    "object_code": object_code,
                    "start": start_val,
                    "end": end_val,
                    "delta": delta,
                }
            )
            total += delta
            break

        per_meter.append(record)

    return total, per_meter


async def compute_total_consumption(
    client: httpx.AsyncClient,
    station_cfg: Dict[str, Any],
    start_dt: datetime,
    end_dt: datetime,
    window_profiles: Optional[Iterable[Tuple[int, int]]] = None,
) -> Tuple[float, List[MeterDelta]]:
    if end_dt <= start_dt:
        return 0.0, []

    start_snapshot = await fetch_snapshot(
        client, station_cfg, start_dt, window_profiles
    )
    end_snapshot = await fetch_snapshot(client, station_cfg, end_dt, window_profiles)
    return aggregate_delta(station_cfg, start_snapshot, end_snapshot)


def _categorize_meter(name: str) -> str:
    target = (name or "").lower()
    for keyword, category in CATEGORY_KEYWORDS:
        if keyword.lower() in target:
            return category
    return "其他"


async def compute_kpi_for_station(station_cfg: Dict[str, Any]) -> Dict[str, float]:
    now = datetime.now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        start_snapshot = await fetch_snapshot(
            client, station_cfg, start_of_day, LONG_WINDOW_PROFILES
        )
        now_snapshot = await fetch_snapshot(client, station_cfg, now)
        total_kwh, _ = aggregate_delta(station_cfg, start_snapshot, now_snapshot)

        fifteen_minutes_ago = now - timedelta(minutes=15)
        try:
            quarter_snapshot = await fetch_snapshot(
                client, station_cfg, fifteen_minutes_ago
            )
            quarter_delta, _ = aggregate_delta(
                station_cfg, quarter_snapshot, now_snapshot
            )
        except RealDataUnavailable:
            quarter_delta = 0.0

        one_hour_ago = now - timedelta(hours=1)
        try:
            hour_snapshot = await fetch_snapshot(client, station_cfg, one_hour_ago)
            hour_delta, _ = aggregate_delta(station_cfg, hour_snapshot, now_snapshot)
        except RealDataUnavailable:
            hour_delta = 0.0

    current_kw = 0.0
    if quarter_delta > 0:
        current_kw = quarter_delta * (60.0 / 15.0)
    elif hour_delta > 0:
        current_kw = hour_delta

    peak_kw = max(current_kw, hour_delta)

    return {
        "total_kwh_today": round(total_kwh, 2),
        "current_kw": round(current_kw, 2),
        "peak_kw": round(peak_kw, 2),
    }


async def compute_realtime_series_for_station(
    station_cfg: Dict[str, Any],
    *,
    points: int = 12,
    interval_minutes: int = 10,
) -> Dict[str, Any]:
    if points < 1:
        return {"timestamps": [], "powers": []}

    interval = timedelta(minutes=interval_minutes)
    now = datetime.now()
    boundaries = [now - interval * (points - idx) for idx in range(points + 1)]

    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        snapshots = await fetch_snapshots(client, station_cfg, boundaries)

    timestamps: List[str] = []
    powers: List[float] = []

    for idx in range(points):
        start_ts = boundaries[idx]
        end_ts = boundaries[idx + 1]
        start_snapshot = snapshots.get(start_ts)
        end_snapshot = snapshots.get(end_ts)
        if not start_snapshot or not end_snapshot:
            powers.append(0.0)
            timestamps.append(end_ts.strftime("%H:%M"))
            continue
        delta, _ = aggregate_delta(station_cfg, start_snapshot, end_snapshot)
        power = delta * (60.0 / interval_minutes)
        powers.append(round(power, 2))
        timestamps.append(end_ts.strftime("%H:%M"))

    return {
        "timestamps": timestamps,
        "powers": powers,
        "interval_minutes": interval_minutes,
    }


async def compute_trend_for_station(
    station_cfg: Dict[str, Any], period: str
) -> Dict[str, Any]:
    now = datetime.now()

    if period == "24h":
        points = 24
        interval = timedelta(hours=1)
        label_format = "%H:%M"
        profiles = DEFAULT_WINDOW_PROFILES
    elif period == "7d":
        points = 7
        interval = timedelta(days=1)
        label_format = "%m-%d"
        profiles = DAILY_WINDOW_PROFILES
    elif period == "30d":
        points = 30
        interval = timedelta(days=1)
        label_format = "%m-%d"
        profiles = DAILY_WINDOW_PROFILES
    else:
        raise RealDataUnavailable(f"unsupported period: {period}")

    boundaries = [now - interval * (points - idx) for idx in range(points + 1)]

    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        snapshots = await fetch_snapshots(client, station_cfg, boundaries, profiles)

    values: List[float] = []
    timestamps: List[str] = []

    for idx in range(points):
        start_ts = boundaries[idx]
        end_ts = boundaries[idx + 1]
        start_snapshot = snapshots.get(start_ts)
        end_snapshot = snapshots.get(end_ts)
        if not start_snapshot or not end_snapshot:
            values.append(0.0)
        else:
            delta, _ = aggregate_delta(station_cfg, start_snapshot, end_snapshot)
            values.append(round(delta, 2))
        timestamps.append(end_ts.strftime(label_format))

    return {"values": values, "timestamps": timestamps, "period": period}


async def compute_compare_for_station(
    station_cfg: Dict[str, Any], period: str
) -> Dict[str, float]:
    if period == "24h":
        duration = timedelta(hours=24)
    elif period == "7d":
        duration = timedelta(days=7)
    elif period == "30d":
        duration = timedelta(days=30)
    else:
        raise RealDataUnavailable(f"unsupported period: {period}")

    now = datetime.now()
    current_start = now - duration
    previous_start = current_start - duration
    last_year_offset = timedelta(days=365)

    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        current_total, _ = await compute_total_consumption(
            client, station_cfg, current_start, now, DAILY_WINDOW_PROFILES
        )
        previous_total, _ = await compute_total_consumption(
            client, station_cfg, previous_start, current_start, DAILY_WINDOW_PROFILES
        )
        try:
            last_year_total, _ = await compute_total_consumption(
                client,
                station_cfg,
                current_start - last_year_offset,
                now - last_year_offset,
                DAILY_WINDOW_PROFILES,
            )
        except RealDataUnavailable:
            last_year_total = 0.0

    mom_percent = 0.0
    if previous_total > 0:
        mom_percent = (current_total - previous_total) / previous_total * 100.0

    yoy_percent = 0.0
    if last_year_total > 0:
        yoy_percent = (current_total - last_year_total) / last_year_total * 100.0

    return {
        "current_kwh": round(current_total, 2),
        "previous_kwh": round(previous_total, 2),
        "last_year_kwh": round(last_year_total, 2),
        "mom_percent": round(mom_percent, 1),
        "yoy_percent": round(yoy_percent, 1),
        "period": period,
    }


async def compute_classification_for_station(
    station_cfg: Dict[str, Any], period: str
) -> Dict[str, Any]:
    if period == "24h":
        duration = timedelta(hours=24)
        profiles = DAILY_WINDOW_PROFILES
    elif period == "7d":
        duration = timedelta(days=7)
        profiles = DAILY_WINDOW_PROFILES
    elif period == "30d":
        duration = timedelta(days=30)
        profiles = DAILY_WINDOW_PROFILES
    else:
        raise RealDataUnavailable(f"unsupported period: {period}")

    now = datetime.now()
    start = now - duration

    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        total, per_meter = await compute_total_consumption(
            client, station_cfg, start, now, profiles
        )

    category_totals: Dict[str, float] = {}
    for record in per_meter:
        delta = record.get("delta")
        if delta is None or delta <= 0:
            continue
        category = _categorize_meter(record.get("name", ""))
        category_totals[category] = category_totals.get(category, 0.0) + float(delta)

    total_kwh = sum(category_totals.values())
    if total_kwh <= 0:
        return {"items": [], "total_kwh": 0.0}

    items = []
    for category, value in category_totals.items():
        percentage = (value / total_kwh) * 100.0 if total_kwh > 0 else 0.0
        items.append(
            {
                "name": category,
                "kwh": round(value, 2),
                "percentage": round(percentage, 1),
            }
        )

    items.sort(key=lambda item: item["kwh"], reverse=True)
    return {"items": items, "total_kwh": round(total_kwh, 2)}
