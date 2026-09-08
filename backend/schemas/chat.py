from pydantic import BaseModel
# pydantic comes in action when the Client wants to SEND data. (POST)
# this part is basically for the client(us) where we are posting the message or what we want to ask to iris

class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str