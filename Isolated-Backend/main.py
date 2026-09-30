import asyncio
import json
import os
import sys
import pandas as pd
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Add the parent directory to sys.path so we can import from load-adaptive-iir.src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'load-adaptive-iir')))

from src.filters import fixed_ema, load_adaptive_ema
from src.queue_simulator import simulate_backpressure
from src.anomaly_injection import inject_anomalies

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    print("Client connected to stream.")
    
    # Shared state between tasks
    state = {"is_paused": False}
    
    async def receiver():
        try:
            while True:
                text = await websocket.receive_text()
                try:
                    data = json.loads(text)
                    if data.get("command") == "pause":
                        state["is_paused"] = True
                    elif data.get("command") == "resume":
                        state["is_paused"] = False
                except Exception:
                    pass
        except WebSocketDisconnect:
            pass

    async def sender():
        try:
            # Load sample data (we'll use a preprocessed binance file)
            data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'load-adaptive-iir', 'data', 'processed', 'binance_BTCUSDT_20240102_20240102.parquet'))
            if not os.path.exists(data_path):
                await websocket.send_json({"error": f"Data file not found at {data_path}"})
                return
                
            df = pd.read_parquet(data_path)
            # Take a slice of 2000 points to stream
            df = df.iloc[5000:7000].copy().reset_index(drop=True)
            
            # Inject anomalies on the fly for demonstration
            x_injected, mask, anomaly_info = inject_anomalies(df['price'], n_each=2, window_std=50)
            df['price_injected'] = x_injected
            df['is_anomaly'] = mask
            
            # Simulate backpressure based on original timestamps, but adding a synthetic burst
            L_full = simulate_backpressure(
                df['timestamp'],
                target_rho=0.75, 
                burst_multiplier=5.0, 
                burst_intervals=[(300, 500), (1200, 1400)] # Synthetic load spikes
            ).values
            
            # Pre-compute filter outputs so we don't have to manage state tick-by-tick (since our DSP code is vectorized)
            y_fixed, _ = fixed_ema(x_injected, alpha=0.30)
            y_adaptive, pole_adaptive = load_adaptive_ema(x_injected, L_full, alpha_min=0.02, alpha_max=0.30)
            
            # Stream points infinitely for the presentation
            loop_count = 0
            time_delta = df['timestamp'].iloc[-1] - df['timestamp'].iloc[0] + 1.0 # Offset for next loop

            while True:
                for i in range(len(df)):
                    # Wait if paused
                    while state["is_paused"]:
                        await asyncio.sleep(0.1)
                        
                    current_timestamp = df['timestamp'].iloc[i] + (loop_count * time_delta)
                    
                    payload = {
                        "timestamp": current_timestamp,
                        "price": float(x_injected[i]),
                        "raw_price": float(df['price'].iloc[i]),
                        "is_anomaly": bool(mask[i]),
                        "load": float(L_full[i]),
                        "fixed_ema": float(y_fixed[i]),
                        "adaptive_ema": float(y_adaptive[i]),
                        "alpha": float(1.0 - pole_adaptive[i]) # Since pole = 1 - alpha
                    }
                    
                    await websocket.send_json(payload)
                    await asyncio.sleep(0.05) # Stream 20 ticks per second
                
                loop_count += 1
                
        except WebSocketDisconnect:
            pass
        except Exception as e:
            print(f"Sender Error: {e}")
            try:
                await websocket.close()
            except:
                pass

    # Run both the receiver and sender concurrently
    recv_task = asyncio.create_task(receiver())
    send_task = asyncio.create_task(sender())
    
    # Wait for whichever task finishes or errors out first (usually WebSocketDisconnect)
    done, pending = await asyncio.wait(
        [recv_task, send_task],
        return_when=asyncio.FIRST_COMPLETED
    )
    
    # Cancel remaining task
    for task in pending:
        task.cancel()
        
    print("Client disconnected.")
