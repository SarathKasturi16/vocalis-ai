from dotenv import load_dotenv
load_dotenv()
import json
import time
import asyncio
import os
import random
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from google import genai
from google.genai import types

router = APIRouter()

# In-memory store for session states (cooldowns, suppressed nudges)
session_states = {}

class Q4StreamRequest(BaseModel):
    scenario_id: str

PROMPT_TEMPLATE = """
You are a real-time Live Coach AI monitoring an active customer service call.
Analyze the conversation history up to the latest utterance. 
Look for exactly ONE of these specific actionable signals that require an immediate Nudge to the Agent:
1. 'missed_cross_sell': The customer mentions an explicit need (e.g., buying a second vehicle, getting a new home), but the agent HAS NOT offered a relevant product yet.
2. 'compliance_gap': The agent is collecting debt or discussing account arrears but HAS NOT provided the mandatory compliance disclosure (e.g., "This is an attempt to collect a debt").
3. 'frustration': The customer expresses clear and rising anger or frustration, and the agent has NOT actively de-escalated or empathized.

If a signal is detected and actionable, return a JSON object with:
{
  "detected": true,
  "nudge_text": "Short actionable recommendation for the agent (max 10 words)",
  "type": "missed_cross_sell" | "compliance_gap" | "frustration",
  "confidence": 0.0 to 1.0
}

If no signal is detected, or the agent has already handled it properly, return:
{
  "detected": false
}

Output ONLY valid JSON.
"""

client = genai.Client()

async def analyze_chunk_llm(history_text: str):
    try:
        start_time = time.time()
        
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=f"{PROMPT_TEMPLATE}\n\nCall History:\n{history_text}",
            config=types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json"
            )
        )
        
        latency = int((time.time() - start_time) * 1000)
        result = json.loads(response.text)
        return result, latency
    except Exception as e:
        print(f"LLM Error: {e}")
        return {"detected": False}, 0

async def sse_generator(scenario_id: str, session_id: str):
    file_path = f"data/q4_scenarios/scenario_{scenario_id}.json"
    if not os.path.exists(file_path):
        yield f"data: {json.dumps({'error': 'Scenario not found'})}\n\n"
        return
        
    with open(file_path, 'r', encoding='utf-8') as f:
        scenario = json.load(f)
        
    session_states[session_id] = {
        "history": [],
        "triggered_types": set()
    }
    
    start_sim_time = time.time()
    
    for utterance in scenario:
        # Wait until the utterance start time to simulate real-time playback
        target_time = start_sim_time + utterance["start"]
        now = time.time()
        if target_time > now:
            await asyncio.sleep(target_time - now)
            
        # 1. Simulate ASR transcription latency (Audio -> Text)
        asr_latency = random.randint(150, 350)
        
        state = session_states[session_id]
        line = f"[{utterance['speaker']}] {utterance['text']}"
        state['history'].append(line)
        history_text = "\n".join(state['history'])
        
        # 2. Call LLM for Signal Extraction & Nudge Generation
        nudge_result, llm_latency = await analyze_chunk_llm(history_text)
        
        nudge_payload = None
        # 3. Nudge Control Logic (False positive & Duplicate suppression)
        if nudge_result.get("detected") and nudge_result.get("confidence", 0) > 0.7:
            nudge_type = nudge_result.get("type")
            # Duplicate suppression: only trigger once per type per session
            if nudge_type not in state['triggered_types']:
                state['triggered_types'].add(nudge_type)
                nudge_payload = {
                    "text": nudge_result.get("nudge_text"),
                    "type": nudge_type,
                    "confidence": nudge_result.get("confidence")
                }
        
        e2e_latency = asr_latency + llm_latency
        
        # Construct event payload
        event_data = {
            "speaker": utterance["speaker"],
            "transcript": utterance["text"],
            "asr_latency_ms": asr_latency,
            "llm_latency_ms": llm_latency,
            "e2e_latency_ms": e2e_latency,
            "nudge": nudge_payload
        }
        
        yield f"data: {json.dumps(event_data)}\n\n"
        
    yield "data: [DONE]\n\n"

@router.get("/stream")
async def stream_call(scenario: str, session: str):
    return StreamingResponse(sse_generator(scenario, session), media_type="text/event-stream")

@router.get("/scenarios")
async def get_scenarios():
    return [
        {"id": "1", "name": "Missed Cross-Sell"},
        {"id": "2", "name": "Compliance Gap"},
        {"id": "3", "name": "Rising Frustration"}
    ]
