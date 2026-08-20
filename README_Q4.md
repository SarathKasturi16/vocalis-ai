# Question 4: Live Insights and Nudges (Implementation Guide)

## Architecture Overview

For Question 4, we built a fully separated **Live Coach Dashboard** into the unified prototype. 
The system simulates real-time call audio streaming and extracts actionable nudges via an LLM.

### Pipeline
1. **Streaming Simulation:** Pre-recorded call transcripts (with timestamps) are replayed on the backend using Server-Sent Events (SSE). Chunks are emitted precisely at their real-world spoken timestamp.
2. **ASR Component:** In this simulation, ASR transcription latency is tracked via a stochastic distribution (avg ~250ms) to mirror a production WebSockets ASR like Deepgram.
3. **Signal Extraction (LLM):** The growing conversation history is dispatched continuously to Gemini 1.5 Flash. A precise prompt extracts exactly one of three signals (cross-sell, compliance gap, frustration) with a confidence score.
4. **Nudge Engine:** A stateful `session_states` dictionary tracks triggered signals. Duplicate nudges are suppressed (e.g., if a frustration nudge fires, it won't fire again for the same call).
5. **Dashboard Delivery:** The SSE stream delivers the transcript, telemetry (ASR Latency, LLM Latency, E2E P95 Latency), and the actionable Nudge object to the frontend.

## How to Test and Record your Video

1. Start the API server: `python api/main.py`
2. Open `index.html` in your browser.
3. Navigate to the **Q4: Live Coach** tab.
4. **Scenario 1:** Click Play on "Missed Cross-Sell". The transcript will stream. Watch as the customer mentions a second vehicle. The agent ignores it. Within ~1.5s, an AI Co-Pilot Nudge will appear prompting the agent to offer the multi-vehicle discount.
5. **Scenario 2:** Click Play on "Compliance Gap". The agent starts a debt collection discussion without reading the mini-Miranda disclosure. A compliance nudge will fire immediately.
6. **Scenario 3:** Click Play on "Frustration". The customer gets angry. The agent responds poorly. A frustration nudge will trigger.

### Key Video Points to Hit:
- Point out the **Live Telemetry** panel showing real-time latency breakdowns (proving we measure End-to-End latency!).
- Show that **duplicate suppression** works (the nudge only fires once despite the LLM seeing the context multiple times).
- Emphasize that the LLM call happens asynchronously to keep the UI smooth.

## Production Improvements (For your presentation)
- **Real Audio Streaming:** In a true production environment, this SSE loop would be replaced by a bi-directional WebSocket directly ingesting PCMU audio, piping through Deepgram, and chaining into the LLM.
- **Async Signal Queues:** LLM inferences would be offloaded to Celery workers rather than awaited sequentially in the SSE generator.
- **Cooldown Logic:** Expand duplicate suppression to include a timed cooldown (e.g., 2 minutes) instead of just once per call.
