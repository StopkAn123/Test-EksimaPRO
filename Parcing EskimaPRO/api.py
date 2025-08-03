from fastapi import FastAPI, Query
from typing import List
from main import fetch_all_tenders

app = FastAPI(title="B2B Tender Parser API")

@app.get("/tenders")
def get_tenders(max: int = Query(10, ge=1, le=100)):
    """
    Получить список тендеров с сайта b2b-center.ru
    """
    tenders = fetch_all_tenders(max)
    return [
        {
            "Номер": t[0],
            "Название": t[1],
            "Стоимость": t[2],
            "Дедлайн": t[3],
            "Организатор": t[4],
            "Заказчики": t[5],
            "Оплата": t[6]
        }
        for t in tenders
    ]
