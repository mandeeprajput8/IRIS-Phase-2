from fastapi import APIRouter

from schemas.command import CommandRequest, CommandResponse
from app_services.iris_service import iris_service


router = APIRouter(
    prefix="/api",
    tags=["Commands"]
)



@router.post("/command", response_model= CommandResponse)
def execute_command(request: CommandRequest):
    result = iris_service.process_command(request.command)

    return {
        "response": result
    }