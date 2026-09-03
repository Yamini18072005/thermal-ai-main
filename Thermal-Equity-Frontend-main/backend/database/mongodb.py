from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Ensure paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = Path(__file__).resolve().parent.parent

for p in [BACKEND_DIR, PROJECT_ROOT]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

# Load environment variables
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")
load_dotenv(dotenv_path=BACKEND_DIR / ".env")
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "").strip()
DATABASE_NAME = os.getenv("DATABASE_NAME", "thermal_equity")
REQUIRE_MONGODB = os.getenv("REQUIRE_MONGODB", "true").strip().lower() == "true" or bool(os.getenv("PORT"))

# Resilient in-memory database store for continuous operation
_in_memory_db: dict[str, list[dict[str, Any]]] = {
    "users": [],
    "locations": [],
    "telemetry": [],
    "alerts": [],
    "insights": [],
    "recommendations": [],
}

# 8 Monitored GCC Chennai Wards Initial Seed Data
CHENNAI_LOCATIONS_SEED = [
    {
        "id": "perambur",
        "name": "Perambur",
        "zone": "Zone 4 (North Chennai)",
        "area": "North Chennai",
        "latitude": 13.1143,
        "longitude": 80.2333,
        "population_density": "24,500 / km²",
        "green_canopy_pct": "4.2%",
        "built_up_ratio": "88%",
        "pm25": "20.8 µg/m³",
        "aqi": "87 (Moderate)",
        "env_ph": "7.3",
        "priority_action": "Immediate Cooling Intervention",
        "lst_offset": 2.8,
        "base_temp": 31.0,
        "base_humidity": 67.0,
        "base_heat_index": 35.1,
        "base_vulnerability": 91,
        "base_risk": "Critical",
    },
    {
        "id": "royapuram",
        "name": "Royapuram",
        "zone": "Zone 5 (North Coastal)",
        "area": "North Coastal",
        "latitude": 13.1118,
        "longitude": 80.2941,
        "population_density": "21,200 / km²",
        "green_canopy_pct": "3.8%",
        "built_up_ratio": "84%",
        "pm25": "20.8 µg/m³",
        "aqi": "87 (Moderate)",
        "env_ph": "7.4",
        "priority_action": "Emergency Hydration Units",
        "lst_offset": 2.8,
        "base_temp": 31.0,
        "base_humidity": 67.0,
        "base_heat_index": 35.2,
        "base_vulnerability": 89,
        "base_risk": "Critical",
    },
    {
        "id": "tnagar",
        "name": "T. Nagar",
        "zone": "Zone 10 (Central Chennai)",
        "area": "Central Commercial",
        "latitude": 13.0418,
        "longitude": 80.2341,
        "population_density": "26,000 / km²",
        "green_canopy_pct": "4.6%",
        "built_up_ratio": "86%",
        "pm25": "20.8 µg/m³",
        "aqi": "87 (Moderate)",
        "env_ph": "7.2",
        "priority_action": "Pedestrian Misting Corridors",
        "lst_offset": 2.6,
        "base_temp": 31.0,
        "base_humidity": 70.0,
        "base_heat_index": 35.3,
        "base_vulnerability": 84,
        "base_risk": "High",
    },
    {
        "id": "ambattur",
        "name": "Ambattur",
        "zone": "Zone 7 (West Industrial)",
        "area": "West Industrial",
        "latitude": 13.1143,
        "longitude": 80.1548,
        "population_density": "16,800 / km²",
        "green_canopy_pct": "8.5%",
        "built_up_ratio": "78%",
        "pm25": "24.0 µg/m³",
        "aqi": "68 (Satisfactory)",
        "env_ph": "7.1",
        "priority_action": "Protect Outdoor Workers",
        "lst_offset": 2.8,
        "base_temp": 30.2,
        "base_humidity": 70.0,
        "base_heat_index": 34.6,
        "base_vulnerability": 82,
        "base_risk": "High",
    },
    {
        "id": "guindy",
        "name": "Guindy",
        "zone": "Zone 9 (South Industrial)",
        "area": "South Industrial",
        "latitude": 13.0067,
        "longitude": 80.2026,
        "population_density": "15,100 / km²",
        "green_canopy_pct": "11.8%",
        "built_up_ratio": "72%",
        "pm25": "20.8 µg/m³",
        "aqi": "87 (Moderate)",
        "env_ph": "7.4",
        "priority_action": "Transit Corridor Cooling",
        "lst_offset": 2.5,
        "base_temp": 30.3,
        "base_humidity": 74.0,
        "base_heat_index": 35.4,
        "base_vulnerability": 76,
        "base_risk": "High",
    },
    {
        "id": "velachery",
        "name": "Velachery",
        "zone": "Zone 13 (South Residential)",
        "area": "South Residential",
        "latitude": 12.9815,
        "longitude": 80.2180,
        "population_density": "18,400 / km²",
        "green_canopy_pct": "6.2%",
        "built_up_ratio": "81%",
        "pm25": "22.5 µg/m³",
        "aqi": "74 (Satisfactory)",
        "env_ph": "7.3",
        "priority_action": "Cool Roof Retrofits",
        "lst_offset": 2.4,
        "base_temp": 30.5,
        "base_humidity": 72.0,
        "base_heat_index": 35.1,
        "base_vulnerability": 78,
        "base_risk": "High",
    },
    {
        "id": "annanagar",
        "name": "Anna Nagar",
        "zone": "Zone 8 (Central Residential)",
        "area": "Central Residential",
        "latitude": 13.0850,
        "longitude": 80.2101,
        "population_density": "19,200 / km²",
        "green_canopy_pct": "14.5%",
        "built_up_ratio": "68%",
        "pm25": "18.2 µg/m³",
        "aqi": "62 (Satisfactory)",
        "env_ph": "7.2",
        "priority_action": "Urban Forest Preservation",
        "lst_offset": 1.9,
        "base_temp": 29.8,
        "base_humidity": 68.0,
        "base_heat_index": 33.4,
        "base_vulnerability": 48,
        "base_risk": "Moderate",
    },
    {
        "id": "adyar",
        "name": "Adyar",
        "zone": "Zone 13 (Coastal South)",
        "area": "Coastal South",
        "latitude": 13.0012,
        "longitude": 80.2565,
        "population_density": "12,300 / km²",
        "green_canopy_pct": "22.4%",
        "built_up_ratio": "54%",
        "pm25": "15.4 µg/m³",
        "aqi": "55 (Satisfactory)",
        "env_ph": "7.5",
        "priority_action": "Eco-Canopy Maintenance",
        "lst_offset": 1.2,
        "base_temp": 29.2,
        "base_humidity": 76.0,
        "base_heat_index": 33.2,
        "base_vulnerability": 28,
        "base_risk": "Low",
    },
]

# Client variables
_client = None
_db = None
_is_connected = False


class MongoDBManager:
    """Manages the MongoDB connection and dashboard collections."""

    @classmethod
    async def connect_to_database(cls):
        global _client, _db, _is_connected
        
        if not MONGODB_URI or "<db_username>" in MONGODB_URI or "<username>" in MONGODB_URI:
            _is_connected = False
            raise RuntimeError("MONGODB_URI is required")

        try:
            from motor.motor_asyncio import AsyncIOMotorClient

            print("[MongoDB] MONGODB_URI found in environment (secret hidden)")
            _client = AsyncIOMotorClient(
                MONGODB_URI,
                serverSelectionTimeoutMS=4000,
            )
            _db = _client[DATABASE_NAME]
            print(f"[MongoDB] Client created for database: {DATABASE_NAME}")

            # Ping database to verify connection
            await _client.admin.command("ping")
            print("[MongoDB] Ping succeeded")
            _is_connected = True
            print(f"[MongoDB] Database connection successful: {DATABASE_NAME}")

            # Ensure unique index on email
            await _db.users.create_index("email", unique=True)
            await _db.telemetry.create_index([("location_id", 1), ("timestamp", -1)])
            await _db.alerts.create_index([("status", 1), ("timestamp", -1)])

            # Auto-seed initial data
            await cls.seed_initial_data()

        except Exception as exc:
            _is_connected = False
            if _client:
                _client.close()
            _client = None
            _db = None
            raise RuntimeError(f"MongoDB connection failed: {type(exc).__name__}") from exc

    @classmethod
    async def close_database_connection(cls):
        global _client
        if _client:
            _client.close()
            print("MongoDB Atlas connection closed.")

    @classmethod
    def get_database(cls):
        global _db
        return _db

    @classmethod
    def is_connected(cls) -> bool:
        global _is_connected
        return _is_connected

    @classmethod
    async def seed_initial_data(cls):
        """Seeds MongoDB collections if empty."""
        from backend.services.auth import get_password_hash

        if _db is None:
            return

        try:
            # 1. Seed Locations
            loc_count = await _db.locations.count_documents({})
            if loc_count == 0:
                await _db.locations.insert_many(CHENNAI_LOCATIONS_SEED)
                print(f"✓ Seeded {len(CHENNAI_LOCATIONS_SEED)} Chennai ward stations in MongoDB.")

            # Seed telemetry without creating authentication users.
            tel_count = await _db.telemetry.count_documents({})
            if tel_count == 0:
                now_iso = datetime.now(timezone.utc).isoformat()
                records = []
                for s in CHENNAI_LOCATIONS_SEED:
                    records.append({
                        "location_id": s["id"],
                        "location_name": s["name"],
                        "area": s["area"],
                        "latitude": s["latitude"],
                        "longitude": s["longitude"],
                        "temperature": s["base_temp"],
                        "humidity": s["base_humidity"],
                        "heat_index": s["base_heat_index"],
                        "lst_temp": +(s["base_temp"] + s["lst_offset"]),
                        "air_quality": {"pm25": s["pm25"], "aqi": s["aqi"]},
                        "source": "Open-Meteo Synoptic + Landsat-8",
                        "timestamp": now_iso,
                    })
                await _db.telemetry.insert_many(records)
                print(f"✓ Seeded {len(records)} baseline telemetry records in MongoDB.")
        except Exception as err:
            print(f"Warning during MongoDB seeding: {err}")

    @classmethod
    def seed_in_memory_data(cls):
        """Populates non-authentication data for compatibility with local callers."""

        if not _in_memory_db["locations"]:
            _in_memory_db["locations"] = [dict(item) for item in CHENNAI_LOCATIONS_SEED]

        now_iso = datetime.now(timezone.utc).isoformat()
        if not _in_memory_db["telemetry"]:
            _in_memory_db["telemetry"] = [
                {
                    "location_id": s["id"],
                    "location_name": s["name"],
                    "area": s["area"],
                    "latitude": s["latitude"],
                    "longitude": s["longitude"],
                    "temperature": s["base_temp"],
                    "humidity": s["base_humidity"],
                    "heat_index": s["base_heat_index"],
                    "lst_temp": +(s["base_temp"] + s["lst_offset"]),
                    "air_quality": {"pm25": s["pm25"], "aqi": s["aqi"]},
                    "source": "Open-Meteo Synoptic + Landsat-8",
                    "timestamp": now_iso,
                }
                for s in CHENNAI_LOCATIONS_SEED
            ]

        if not _in_memory_db["alerts"]:
            _in_memory_db["alerts"] = [
                {
                    "id": "alt-1",
                    "location_name": "Perambur",
                    "risk_level": "Critical",
                    "alert_type": "Thermal Exposure Advisory",
                    "message": "Critical thermal advisory active for Perambur corridor. High surface heat storage.",
                    "severity": "critical",
                    "status": "active",
                    "timestamp": now_iso,
                },
                {
                    "id": "alt-2",
                    "location_name": "Royapuram",
                    "risk_level": "Critical",
                    "alert_type": "Heat Wave Warning",
                    "message": "Elevated apparent heat index in Royapuram coastal residential belt.",
                    "severity": "critical",
                    "status": "active",
                    "timestamp": now_iso,
                },
            ]


# Helper CRUD functions
async def get_all_locations() -> list[dict[str, Any]]:
    if _is_connected and _db is not None:
        try:
            cursor = _db.locations.find({}, {"_id": 0})
            locs = await cursor.to_list(length=100)
            if locs:
                return locs
        except Exception as exc:
            if REQUIRE_MONGODB:
                raise RuntimeError("MongoDB Atlas query failed") from exc
    return _in_memory_db["locations"]


async def get_latest_telemetry() -> list[dict[str, Any]]:
    if _is_connected and _db is not None:
        try:
            cursor = _db.telemetry.find({}, {"_id": 0}).sort("timestamp", -1).limit(20)
            tels = await cursor.to_list(length=20)
            if tels:
                return tels
        except Exception as exc:
            if REQUIRE_MONGODB:
                raise RuntimeError("MongoDB Atlas query failed") from exc
    return _in_memory_db["telemetry"]


async def get_active_alerts() -> list[dict[str, Any]]:
    if _is_connected and _db is not None:
        try:
            cursor = _db.alerts.find({"status": "active"}, {"_id": 0}).sort("timestamp", -1)
            alts = await cursor.to_list(length=50)
            if alts:
                return alts
        except Exception as exc:
            if REQUIRE_MONGODB:
                raise RuntimeError("MongoDB Atlas query failed") from exc
    return [a for a in _in_memory_db["alerts"] if a.get("status") == "active"]


async def save_telemetry_batch(telemetry_list: list[dict[str, Any]]) -> int:
    if not telemetry_list:
        return 0
    if _is_connected and _db is not None:
        try:
            result = await _db.telemetry.insert_many(telemetry_list)
            return len(result.inserted_ids)
        except Exception as exc:
            if REQUIRE_MONGODB:
                raise RuntimeError("MongoDB Atlas write failed") from exc
    _in_memory_db["telemetry"].extend(telemetry_list)
    return len(telemetry_list)


async def find_user_by_email(email: str) -> dict[str, Any] | None:
    clean_email = email.strip().lower()
    if not _is_connected or _db is None:
        raise RuntimeError("MongoDB is not connected")
    try:
        return await _db.users.find_one({"email": clean_email})
    except Exception as exc:
        raise RuntimeError("MongoDB user lookup failed") from exc


async def create_user(user_doc: dict[str, Any]) -> dict[str, Any]:
    if not _is_connected or _db is None:
        raise RuntimeError("MongoDB is not connected")
    user_doc["email"] = user_doc["email"].strip().lower()
    if "created_at" not in user_doc:
        user_doc["created_at"] = datetime.now(timezone.utc).isoformat()
    try:
        result = await _db.users.insert_one(user_doc)
        user_doc["_id"] = str(result.inserted_id)
        return user_doc
    except Exception as exc:
        raise RuntimeError("MongoDB user creation failed") from exc
