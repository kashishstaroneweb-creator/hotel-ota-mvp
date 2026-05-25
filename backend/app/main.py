from datetime import date
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing_extensions import Literal


app = FastAPI(title="OTA Revenue Management MVP", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


Channel = Literal["Booking.com", "Agoda", "MakeMyTrip", "Direct"]
SignalType = Literal["local_event", "search_demand", "competitor_rate", "pickup", "seasonality"]


class OtaListing(BaseModel):
    channel: Channel
    status: Literal["healthy", "needs_attention", "offline"]
    current_rate: int
    available_rooms: int
    parity_gap: int = Field(description="Difference versus the hotel's direct rate")
    last_synced: str


class RoomType(BaseModel):
    id: str
    name: str
    base_rate: int
    min_rate: int
    max_rate: int
    total_rooms: int
    sold_rooms: int


class DemandSignal(BaseModel):
    id: int
    signal_type: SignalType
    label: str
    strength: int = Field(ge=1, le=100)
    impact: Literal["up", "down", "neutral"]
    note: Optional[str] = None


class DemandSignalCreate(BaseModel):
    signal_type: SignalType
    label: str
    strength: int = Field(ge=1, le=100)
    impact: Literal["up", "down", "neutral"] = "up"
    note: Optional[str] = None


class Hotel(BaseModel):
    id: int
    name: str
    location: str
    total_rooms: int
    direct_rate: int
    room_types: List[RoomType]
    ota_listings: List[OtaListing]
    demand_signals: List[DemandSignal]


class RateRecommendation(BaseModel):
    room_type_id: str
    room_type: str
    channel: Channel
    current_rate: int
    recommended_rate: int
    change_percent: float
    reason: str


class RevenueReport(BaseModel):
    month: str
    baseline_revenue: int
    optimized_revenue: int
    revenue_uplift: int
    uplift_percent: float
    baseline_adr: int
    optimized_adr: int
    occupancy_percent: float
    commission_model_estimate: int


class Dashboard(BaseModel):
    hotel: Hotel
    kpis: Dict[str, float]
    recommendations: List[RateRecommendation]
    report: RevenueReport


HOTELS: Dict[int, Hotel] = {
    1: Hotel(
        id=1,
        name="Lakeview Residency",
        location="Udaipur, Rajasthan",
        total_rooms=42,
        direct_rate=4200,
        room_types=[
            RoomType(
                id="deluxe",
                name="Deluxe Room",
                base_rate=3800,
                min_rate=2600,
                max_rate=7200,
                total_rooms=24,
                sold_rooms=18,
            ),
            RoomType(
                id="premium",
                name="Premium Lake View",
                base_rate=5200,
                min_rate=3800,
                max_rate=9800,
                total_rooms=12,
                sold_rooms=10,
            ),
            RoomType(
                id="suite",
                name="Family Suite",
                base_rate=7600,
                min_rate=5600,
                max_rate=14000,
                total_rooms=6,
                sold_rooms=3,
            ),
        ],
        ota_listings=[
            OtaListing(
                channel="Booking.com",
                status="healthy",
                current_rate=4350,
                available_rooms=11,
                parity_gap=150,
                last_synced="2026-05-25 09:30",
            ),
            OtaListing(
                channel="Agoda",
                status="needs_attention",
                current_rate=3999,
                available_rooms=9,
                parity_gap=-201,
                last_synced="2026-05-24 18:10",
            ),
            OtaListing(
                channel="MakeMyTrip",
                status="healthy",
                current_rate=4499,
                available_rooms=12,
                parity_gap=299,
                last_synced="2026-05-25 08:45",
            ),
            OtaListing(
                channel="Direct",
                status="healthy",
                current_rate=4200,
                available_rooms=13,
                parity_gap=0,
                last_synced="2026-05-25 09:40",
            ),
        ],
        demand_signals=[
            DemandSignal(
                id=1,
                signal_type="local_event",
                label="Weekend wedding demand",
                strength=82,
                impact="up",
                note="Multiple group inquiries in the city for the next weekend.",
            ),
            DemandSignal(
                id=2,
                signal_type="pickup",
                label="Fast 7-day pickup",
                strength=74,
                impact="up",
                note="18 rooms sold in the last 7 days.",
            ),
            DemandSignal(
                id=3,
                signal_type="competitor_rate",
                label="Competitors priced higher",
                strength=64,
                impact="up",
                note="Nearby comparable hotels are averaging Rs 4,900.",
            ),
        ],
    )
}


def clamp(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(value, maximum))


def demand_multiplier(hotel: Hotel, room: RoomType) -> float:
    occupancy = room.sold_rooms / room.total_rooms
    multiplier = 1.0

    if occupancy >= 0.8:
        multiplier += 0.18
    elif occupancy >= 0.6:
        multiplier += 0.10
    elif occupancy <= 0.35:
        multiplier -= 0.08

    for signal in hotel.demand_signals:
        weighted_strength = signal.strength / 100
        if signal.impact == "up":
            multiplier += weighted_strength * 0.08
        elif signal.impact == "down":
            multiplier -= weighted_strength * 0.07

    return max(0.75, min(multiplier, 1.55))


def channel_adjustment(channel: Channel) -> float:
    adjustments = {
        "Booking.com": 1.03,
        "Agoda": 0.99,
        "MakeMyTrip": 1.04,
        "Direct": 1.0,
    }
    return adjustments[channel]


def build_recommendations(hotel: Hotel) -> List[RateRecommendation]:
    recommendations: List[RateRecommendation] = []

    for room in hotel.room_types:
        multiplier = demand_multiplier(hotel, room)
        for listing in hotel.ota_listings:
            raw_rate = int(room.base_rate * multiplier * channel_adjustment(listing.channel))
            recommended_rate = clamp(raw_rate, room.min_rate, room.max_rate)
            current_rate = listing.current_rate if room.id == "deluxe" else int(room.base_rate * channel_adjustment(listing.channel))
            change_percent = round(((recommended_rate - current_rate) / current_rate) * 100, 1)

            if change_percent > 8:
                reason = "Raise rate: strong demand and limited remaining inventory."
            elif change_percent < -5:
                reason = "Reduce rate: softer demand for this room type."
            else:
                reason = "Hold close to current rate: demand and inventory are balanced."

            recommendations.append(
                RateRecommendation(
                    room_type_id=room.id,
                    room_type=room.name,
                    channel=listing.channel,
                    current_rate=current_rate,
                    recommended_rate=recommended_rate,
                    change_percent=change_percent,
                    reason=reason,
                )
            )

    return recommendations


def build_report(hotel: Hotel) -> RevenueReport:
    sold_rooms = sum(room.sold_rooms for room in hotel.room_types)
    room_nights = sold_rooms * 30
    baseline_adr = int(sum(room.base_rate * room.sold_rooms for room in hotel.room_types) / sold_rooms)
    optimized_rates = {
        recommendation.room_type_id: recommendation.recommended_rate
        for recommendation in build_recommendations(hotel)
        if recommendation.channel == "Direct"
    }
    optimized_adr = int(
        sum(optimized_rates[room.id] * room.sold_rooms for room in hotel.room_types) / sold_rooms
    )
    baseline_revenue = baseline_adr * room_nights
    optimized_revenue = optimized_adr * room_nights
    revenue_uplift = optimized_revenue - baseline_revenue

    return RevenueReport(
        month=date.today().strftime("%B %Y"),
        baseline_revenue=baseline_revenue,
        optimized_revenue=optimized_revenue,
        revenue_uplift=revenue_uplift,
        uplift_percent=round((revenue_uplift / baseline_revenue) * 100, 1),
        baseline_adr=baseline_adr,
        optimized_adr=optimized_adr,
        occupancy_percent=round((sold_rooms / hotel.total_rooms) * 100, 1),
        commission_model_estimate=int(revenue_uplift * 0.15),
    )


def build_kpis(hotel: Hotel) -> Dict[str, float]:
    report = build_report(hotel)
    rooms_sold = sum(room.sold_rooms for room in hotel.room_types)
    available_inventory = sum(room.total_rooms - room.sold_rooms for room in hotel.room_types)
    healthy_channels = len([listing for listing in hotel.ota_listings if listing.status == "healthy"])

    return {
        "adr": report.optimized_adr,
        "occupancy": report.occupancy_percent,
        "revenue_uplift": report.revenue_uplift,
        "rooms_sold": rooms_sold,
        "available_inventory": available_inventory,
        "healthy_channels": healthy_channels,
    }


def get_hotel_or_404(hotel_id: int) -> Hotel:
    hotel = HOTELS.get(hotel_id)
    if hotel is None:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return hotel


@app.get("/api/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/api/hotels", response_model=List[Hotel])
def list_hotels() -> List[Hotel]:
    return list(HOTELS.values())


@app.get("/api/hotels/{hotel_id}", response_model=Hotel)
def get_hotel(hotel_id: int) -> Hotel:
    return get_hotel_or_404(hotel_id)


@app.get("/api/hotels/{hotel_id}/recommendations", response_model=List[RateRecommendation])
def get_recommendations(hotel_id: int) -> List[RateRecommendation]:
    return build_recommendations(get_hotel_or_404(hotel_id))


@app.get("/api/hotels/{hotel_id}/report", response_model=RevenueReport)
def get_report(hotel_id: int) -> RevenueReport:
    return build_report(get_hotel_or_404(hotel_id))


@app.get("/api/hotels/{hotel_id}/dashboard", response_model=Dashboard)
def get_dashboard(hotel_id: int) -> Dashboard:
    hotel = get_hotel_or_404(hotel_id)
    return Dashboard(
        hotel=hotel,
        kpis=build_kpis(hotel),
        recommendations=build_recommendations(hotel),
        report=build_report(hotel),
    )


@app.post("/api/hotels/{hotel_id}/demand-signals", response_model=Dashboard, status_code=201)
def add_demand_signal(hotel_id: int, payload: DemandSignalCreate) -> Dashboard:
    hotel = get_hotel_or_404(hotel_id)
    next_id = max([signal.id for signal in hotel.demand_signals], default=0) + 1
    hotel.demand_signals.append(DemandSignal(id=next_id, **payload.dict()))
    return get_dashboard(hotel_id)
