from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from jose import jwt
import uvicorn
import os
from dotenv import load_dotenv

from database import get_db, engine
from models import Base, User, CognitiveSession, ConsciousnessMetrics
from schemas import UserCreate, UserResponse, Token, CognitiveData, MetricsData
from auth import authenticate_user, create_access_token, get_current_user, get_password_hash
from cognitive_framework import CognitiveFramework
from websocket_manager import WebSocketManager

load_dotenv()

app = FastAPI(title="Syntelligence OS Cloud Backend", version="12.7.8")

# Create database tables
Base.metadata.create_all(bind=engine)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# WebSocket manager
ws_manager = WebSocketManager()

# Cognitive framework
cognitive_framework = CognitiveFramework()

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)))
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/me/", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.post("/cognitive/process")
async def process_cognitive_data(data: CognitiveData, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    result = await cognitive_framework.process_input({"input_data": data.input_data, "user_id": current_user.id})
    
    # Store session
    session = CognitiveSession(
        user_id=current_user.id,
        input_data=data.input_data,
        output_data=json.dumps(result),
        timestamp=datetime.utcnow()
    )
    db.add(session)
    db.commit()
    
    return result

@app.post("/metrics/update")
async def update_metrics(data: MetricsData, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    metrics = ConsciousnessMetrics(
        user_id=current_user.id,
        phi_value=data.phi_value,
        consciousness_level=data.consciousness_level,
        workspace_capacity=data.workspace_capacity,
        timestamp=datetime.utcnow()
    )
    db.add(metrics)
    db.commit()
    return {"status": "metrics updated"}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await ws_manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Process real-time cognitive data
            result = await cognitive_framework.process_input(json.loads(data))
            await ws_manager.send_personal_message(json.dumps(result), client_id)
@app.get("/system/status")
async def get_system_status(current_user: User = Depends(get_current_user)):
    """Get complete system status including consciousness metrics"""
    return cognitive_framework.get_system_status()

@app.get("/agents/")
async def get_agents(current_user: User = Depends(get_current_user)):
    """Get all cognitive agents status"""
    agents = cognitive_framework.get_system_status()['agents']
    return {"agents": agents}

@app.post("/agents/{agent_name}/activate")
async def activate_agent(agent_name: str, current_user: User = Depends(get_current_user)):
    """Activate a specific cognitive agent"""
    if agent_name in cognitive_framework.agents:
        cognitive_framework.agents[agent_name].active = True
        cognitive_framework.agents[agent_name].activation_level = 1.0
        return {"status": f"Agent {agent_name} activated"}
    return {"error": f"Agent {agent_name} not found"}

@app.get("/consciousness/metrics")
async def get_consciousness_metrics(current_user: User = Depends(get_current_user)):
    """Get current consciousness metrics"""
    return cognitive_framework._get_metrics()

@app.post("/subsystems/{subsystem_name}/stimulate")
async def stimulate_subsystem(subsystem_name: str, intensity: float = 0.5, current_user: User = Depends(get_current_user)):
    """Stimulate a cognitive subsystem"""
    if subsystem_name in cognitive_framework.subsystems:
        cognitive_framework.subsystems[subsystem_name].activation += intensity
        return {"status": f"Subsystem {subsystem_name} stimulated"}
    return {"error": f"Subsystem {subsystem_name} not found"}

@app.get("/workspace/content")
async def get_workspace_content(current_user: User = Depends(get_current_user)):
    """Get current global workspace content"""
    return {"workspace": cognitive_framework.gwt_engine.get_workspace_content()}

@app.post("/feedback/cycle")
async def trigger_feedback_cycle(input_data: Dict, current_user: User = Depends(get_current_user)):
    """Trigger a recursive feedback cycle"""
    result = await cognitive_framework.rfl_engine.process_cycle(
        input_data, cognitive_framework.iit_engine, cognitive_framework.gwt_engine
    )
    return result

@app.get("/sessions/")
async def get_cognitive_sessions(limit: int = 10, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get recent cognitive sessions"""
    sessions = db.query(CognitiveSession).filter(
        CognitiveSession.user_id == current_user.id
    ).order_by(CognitiveSession.timestamp.desc()).limit(limit).all()
    
    return {"sessions": [
        {
            "id": s.id,
            "input_data": s.input_data,
            "output_data": s.output_data,
            "timestamp": s.timestamp
        } for s in sessions
    ]}

async def process_realtime(self, data: str, client_id: str) -> str:
    if self.llm:
        try:
            response = self.llm(data, max_length=50, num_return_sequences=1)[0]['generated_text']
        except:
            response = f"Echo: {data}"
    else:
        response = f"Echo: {data}"
    return response

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)