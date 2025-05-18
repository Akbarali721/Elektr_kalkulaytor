from typing import Optional
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/calculator", response_class=HTMLResponse)
async def calculator(request: Request):
    return templates.TemplateResponse("calculator.html", {"request": request})

@app.post("/result", response_class=HTMLResponse)
async def result(
    request: Request,
    usage: Optional[int] = Form(None),
    payment: Optional[int] = Form(None),
    house_type: str = Form(...)
):
    context = {"request": request}

    # 1. Sarf → To‘lov
    if usage is not None:
        price = 0
        breakdown = []

        if house_type == "standard":
            tiers = [
                (200, 600),
                (300, 800),
                (500, 1000),
                (4000, 1500),
                (5000, 1750),
                (float('inf'), 2000),
            ]
        else:
            tiers = [
                (200, 300),
                (300, 400),
                (500, 500),
                (4000, 750),
                (5000, 875),
                (float('inf'), 1000),
            ]

        remaining = usage
        for limit, rate in tiers:
            used = min(remaining, limit)
            cost = used * rate
            price += cost
            breakdown.append({"kwh": used, "rate": rate, "cost": cost})
            remaining -= used
            if remaining <= 0:
                break

        context.update({
            "usage": usage,
            "price": price,
            "breakdown": breakdown,
        })

    # 2. To‘lov → Sarf
    elif payment is not None:
        remaining_money = payment
        breakdown = []
        total_kwh = 0.0

        if house_type == "standard":
            thresholds = [
                (200, 600),
                (300, 800),
                (500, 1000),
                (4000, 1500),
                (5000, 1750),
                (float('inf'), 2000),
            ]
        else:
            thresholds = [
                (200, 300),
                (300, 400),
                (500, 500),
                (4000, 750),
                (5000, 875),
                (float('inf'), 1000),
            ]

        for limit, rate in thresholds:
            max_cost = limit * rate
            if remaining_money >= max_cost:
                # Full tier
                breakdown.append({"kwh": limit, "rate": rate, "cost": max_cost})
                total_kwh += limit
                remaining_money -= max_cost
            else:
                # Partial tier
                partial_kwh = round(remaining_money / rate, 2)
                cost = partial_kwh * rate
                breakdown.append({"kwh": partial_kwh, "rate": rate, "cost": cost})
                total_kwh += partial_kwh
                remaining_money -= cost
                break

        context.update({
            "payment": payment,
            "total_kwh": total_kwh,
            "breakdown": breakdown,
            "remaining_money": remaining_money,
        })

    return templates.TemplateResponse("result.html", context)

# Note: 'standard' — oddiy uy, boshqasi — elektr plitali uy uchun
