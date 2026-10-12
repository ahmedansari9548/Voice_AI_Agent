from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.integrations.vapi import process_tool_call

router = APIRouter()


@router.post("/vapi/tools")
async def vapi_tools(
    request: Request,
    db: Session = Depends(get_db),
):
    body = await request.json()
    message = body.get("message", {})
    tool_calls = message.get("toolCallList", [])

    if not isinstance(tool_calls, list):
        return {"results": []}

    results = [
        process_tool_call(db, tool_call)
        for tool_call in tool_calls
    ]

    return {"results": results}
