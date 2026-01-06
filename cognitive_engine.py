import asyncio
import torch
import numpy as np
from typing import Dict, Any
from transformers import pipeline

class CognitiveEngine:
    def __init__(self):
        # Initialize language model (using a smaller model for testing)
        try:
            self.llm = pipeline("text-generation", model="distilgpt2", device=0 if torch.cuda.is_available() else -1)
        except:
            # Fallback to simple text processing if model fails to load
            self.llm = None
        
        # Simple in-memory storage instead of ChromaDB for now
        self.memory = []
        
        # Consciousness metrics
        self.phi_value = 0.0
        self.consciousness_level = 0.0
        
    async def process(self, input_data: str, user_id: int) -> str:
        # Store input in memory
        self.memory.append({
            "input": input_data,
            "user_id": user_id,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        # Generate response using LLM or fallback
        if self.llm:
            try:
                response = self.llm(input_data, max_length=50, num_return_sequences=1)[0]['generated_text']
            except:
                response = f"Echo: {input_data}"
        else:
            response = f"Echo: {input_data}"
        
        # Update consciousness metrics
        self.update_consciousness_metrics(input_data, response)
        
        return response
    
    async def process_realtime(self, data: str, client_id: str) -> str:
        # Real-time processing for WebSocket
        if self.llm:
            try:
                response = self.llm(data, max_length=50, num_return_sequences=1)[0]['generated_text']
            except:
                response = f"Echo: {data}"
        else:
            response = f"Echo: {data}"
        return response
    
    def update_consciousness_metrics(self, input: str, output: str):
        # Simple Phi calculation (Integrated Information Theory approximation)
        input_complexity = len(set(input.split())) / len(input.split()) if input.split() else 0
        output_complexity = len(set(output.split())) / len(output.split()) if output.split() else 0
        self.phi_value = (input_complexity + output_complexity) / 2
        
        # Consciousness level based on interaction depth
        self.consciousness_level = min(1.0, self.consciousness_level + 0.01)
    
    def get_metrics(self) -> Dict[str, float]:
        return {
            "phi_value": self.phi_value,
            "consciousness_level": self.consciousness_level,
            "workspace_capacity": 0.8  # Placeholder
        }