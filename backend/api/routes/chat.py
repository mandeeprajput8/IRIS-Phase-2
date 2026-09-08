from fastapi import APIRouter

from schemas.chat import ChatRequest, ChatResponse
from app_services.iris_service import iris_service


router = APIRouter(
    prefix="/api",
    tags=["Chat"]
)


# connecting/routing the API with IRIS
# the response model tell that the output of this endpoint should follow the ChatResponse structure
@router.post("/chat", response_model= ChatResponse)
def chat(request: ChatRequest):
    # someones posts to /chat, take the message and send to iris and store the response from the OPENAI into response
    response = iris_service.process_chat(request.message)

    return {
        "response": response
    }
