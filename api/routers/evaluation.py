from fastapi import APIRouter

router = APIRouter(
    prefix="/api/evaluation",
    tags=["Evaluation"]
)

@router.get("/report")
async def get_report():
    return {
        "rsr": 0.78,
        "precision": 0.82,
        "recall": 0.76,
        "time_saved_hours": 1042
    }