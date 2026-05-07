import uuid, json, logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from config import settings
from database import engine, Base, get_db, ChatSession, Message, Project
from handlers.chat import analyze_project_plan, generate_file_code, extract_code_from_response
from handlers.github import push_to_github

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(title="AI Code Manager", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/sessions")
async def list_sessions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ChatSession).order_by(ChatSession.created_at.desc()))
    sessions = result.scalars().all()
    return [{"id": s.id, "name": s.name, "status": s.status, "created_at": s.created_at.isoformat()} for s in sessions]

@app.post("/api/analyze")
async def analyze(message: str = Form(...), db: AsyncSession = Depends(get_db)):
    plan = await analyze_project_plan(message)
    session = ChatSession(name=message[:50], status="planning")
    db.add(session)
    db.add(Message(session_id=session.id, role="user", content=message))
    db.add(Message(session_id=session.id, role="assistant", content=json.dumps(plan), files_plan=plan))
    await db.commit()
    return {"session_id": session.id, "plan": plan}

@app.post("/api/generate-code")
async def generate_code(session_id: str = Form(...), db: AsyncSession = Depends(get_db)):
    plan_msg = (await db.execute(
        select(Message).where(Message.session_id == session_id, Message.files_plan != None)
    )).scalar_one_or_none()
    if not plan_msg:
        raise HTTPException(404, "Plan not found")

    plan = plan_msg.files_plan
    files = plan.get("files", [])
    session = (await db.execute(select(ChatSession).where(ChatSession.id == session_id))).scalar_one_or_none()
    if session:
        session.status = "generating"
        await db.commit()

    async def event_generator():
        generated = {}
        for i, f in enumerate(files):
            name = f["name"]
            pct = int((i / len(files)) * 100)
            yield f"data: {json.dumps({'type':'progress','filename':name,'percentage':pct,'current':i+1,'total':len(files)})}\n\n"
            try:
                code = await generate_file_code(name, f.get("description",""), plan.get("description",""))
                clean = extract_code_from_response(code)
                generated[name] = clean
                yield f"data: {json.dumps({'type':'file_complete','filename':name,'percentage':int(((i+1)/len(files))*100)})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'type':'error','filename':name,'error':str(e)})}\n\n"

        # Save
        all_code = "\n\n".join([f"# {n}\n{c}" for n,c in generated.items()])
        db.add(Message(session_id=session_id, role="assistant", content="Code generated", code=all_code))
        db.add(Project(session_id=session_id, name=session.name if session else "Project", files=generated))
        if session:
            session.status = "completed"
        await db.commit()
        yield f"data: {json.dumps({'type':'complete','files':list(generated.keys())})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/api/push-to-github")
async def push(session_id: str = Form(...), repo_name: str = Form(...), db: AsyncSession = Depends(get_db)):
    if not settings.GITHUB_TOKEN or "your_token" in settings.GITHUB_TOKEN:
        raise HTTPException(400, "GitHub token not configured")
    project = (await db.execute(select(Project).where(Project.session_id == session_id))).scalar_one_or_none()
    if not project or not project.files:
        raise HTTPException(400, "No generated files found")
    repo_url = await push_to_github(repo_name, project.files, settings.GITHUB_TOKEN)
    project.name = repo_name
    project.repo_url = repo_url
    project.pushed = "yes"
    session = (await db.execute(select(ChatSession).where(ChatSession.id == session_id))).scalar_one_or_none()
    if session:
        session.status = "pushed"
    await db.commit()
    return {"success": True, "repo_url": repo_url}

@app.get("/api/session/{session_id}")
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    session = (await db.execute(select(ChatSession).where(ChatSession.id == session_id))).scalar_one_or_none()
    if not session:
        raise HTTPException(404, "Session not found")
    project = (await db.execute(select(Project).where(Project.session_id == session_id))).scalar_one_or_none()
    msgs = (await db.execute(select(Message).where(Message.session_id == session_id))).scalars().all()
    return {
        "id": session.id,
        "name": session.name,
        "status": session.status,
        "created_at": session.created_at.isoformat(),
        "plan": next((m.files_plan for m in msgs if m.files_plan), None),
        "project": {"id": project.id, "name": project.name, "files": list(project.files.keys()), "repo_url": project.repo_url, "pushed": project.pushed} if project else None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)