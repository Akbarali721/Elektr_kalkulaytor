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
            # Standard uylar uchun tarif bosqichlari
            tiers = [
                (200, 600),     # 0–200 kVt·s @600 so‘m
                (800, 1000),    # 201–1000 kVt·s @1000 so‘m
                (4000, 1500),   # 1001–5000 kVt·s @1500 so‘m
                (5000, 1750),   # 5001–10000 kVt·s @1750 so‘m
                (float('inf'), 2000),  # 10001+ kVt·s @2000 so‘m
            ]
        else:
            # Elektr plitali uylar uchun
            tiers = [
                (200, 300),     # 0–200 kVt·s @300 so‘m
                (300, 800),     # 201–500 kVt·s @800 so‘m
                (500, 1000),    # 501–1000 kVt·s @1000 so‘m
                (4000, 1500),   # 1001–5000 kVt·s @1500 so‘m
                (5000, 1750),   # 5001–10000 kVt·s @1750 so‘m
                (float('inf'), 2000),  # 10001+ kVt·s @2000 so‘m
            ]

        remaining = usage
        for limit, rate in tiers:
            if remaining > limit:
                cost = limit * rate
                price += cost
                breakdown.append({"kwh": limit, "rate": rate, "cost": cost})
                remaining -= limit
            else:
                cost = remaining * rate
                price += cost
                breakdown.append({"kwh": remaining, "rate": rate, "cost": cost})
                break

        context.update({
            "usage": usage,
            "price": price,
            "breakdown": breakdown,
        })

    # 2. To‘lov → Sarf (ixtiyoriy, agar kerak bo‘lsa qo‘shing)
    elif payment is not None:
        if house_type == "standard":
            thresholds = [
                (200, 600),
                (800, 1000),
                (4000, 1500),
                (5000, 1750),
                (float('inf'), 2000),
            ]
        else:
            thresholds = [
                (200, 300),
                (300, 800),
                (500, 1000),
                (4000, 1500),
                (5000, 1750),
                (float('inf'), 2000),
            ]

        remaining = payment
        kwh = 0
        for limit, rate in thresholds:
            max_cost = limit * rate
            if remaining >= max_cost:
                kwh += limit
                remaining -= max_cost
            else:
                kwh += remaining // rate
                break

        context.update({
            "payment": payment,
            "kwh": kwh,
        })

    return templates.TemplateResponse("result.html", context)
