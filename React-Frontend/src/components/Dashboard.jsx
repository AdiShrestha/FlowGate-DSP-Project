import React, { useState, useEffect, useRef } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceDot } from 'recharts';
import { Activity, Zap, ShieldAlert, Cpu, Pause, Play } from 'lucide-react';

export default function Dashboard() {
  const [data, setData] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [latestData, setLatestData] = useState(null);
  const [anomalies, setAnomalies] = useState([]);
  const [isPaused, setIsPaused] = useState(false);
  const isPausedRef = useRef(false);
  const ws = useRef(null);

  const togglePause = () => {
    const newPausedState = !isPaused;
    setIsPaused(newPausedState);
    isPausedRef.current = newPausedState;
    
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ command: newPausedState ? 'pause' : 'resume' }));
    }
  };

  useEffect(() => {
    // Connect to WebSocket
    ws.current = new WebSocket('ws://localhost:8000/ws/stream');

    ws.current.onopen = () => {
      setIsConnected(true);
    };

    ws.current.onmessage = (event) => {
      // We no longer ignore messages on the frontend. We just let the backend control the flow.
      const parsedData = JSON.parse(event.data);
      
      if (parsedData.error) {
        console.error("Backend Error:", parsedData.error);
        return;
      }

      setLatestData(parsedData);
      
      setData((prevData) => {
        const newData = [...prevData, parsedData];
        // Keep only the last 150 points for smooth scrolling
        if (newData.length > 150) {
          return newData.slice(newData.length - 150);
        }
        return newData;
      });

      if (parsedData.is_anomaly) {
        setAnomalies(prev => [{
          time: new Date(parsedData.timestamp * 1000).toLocaleTimeString(),
          price: parsedData.price.toFixed(2),
          load: parsedData.load.toFixed(2)
        }, ...prev].slice(0, 10)); // Keep last 10 anomalies
      }
    };

    ws.current.onclose = () => {
      setIsConnected(false);
    };

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, []);

  return (
    <div className="min-h-screen p-8">
      <header className="mb-8 flex justify-between items-center bg-slate-800 p-6 rounded-2xl shadow-lg border border-slate-700">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">
            Load-Adaptive IIR Filter
          </h1>
          <p className="text-slate-400 mt-2">Real-Time DSP Presentation Dashboard</p>
        </div>
        <div className="flex items-center gap-3 bg-slate-900 px-4 py-2 rounded-full border border-slate-700">
          <button 
            onClick={togglePause}
            disabled={!isConnected}
            className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm font-bold transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed ${
              isPaused ? 'bg-amber-500/20 text-amber-400 hover:bg-amber-500/30' : 'bg-blue-500/20 text-blue-400 hover:bg-blue-500/30'
            }`}
          >
            {isPaused ? <Play size={16} /> : <Pause size={16} />}
            {isPaused ? 'RESUME' : 'PAUSE'}
          </button>
          
          <div className="w-px h-6 bg-slate-700 mx-1"></div>
          
          <div className={`w-3 h-3 rounded-full ${isConnected ? (isPaused ? 'bg-amber-500 shadow-[0_0_10px_#f59e0b]' : 'bg-emerald-500 shadow-[0_0_10px_#10b981] animate-pulse') : 'bg-rose-500'}`} />
          <span className="font-mono text-sm text-slate-300">
            {isConnected ? (isPaused ? 'PAUSED' : 'LIVE STREAM') : 'DISCONNECTED'}
          </span>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        
        {/* Main Chart Area */}
        <div className="lg:col-span-3 bg-slate-800 rounded-2xl shadow-lg border border-slate-700 p-6">
          <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
            <Activity className="text-blue-400" /> Signal Tracking & Detection
          </h2>
          <div className="h-[500px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data} margin={{ top: 10, right: 30, left: 20, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis 
                  dataKey="timestamp" 
                  type="number"
                  domain={['dataMin', 'dataMax']}
                  tickFormatter={(unixTime) => new Date(unixTime * 1000).toLocaleTimeString([], {hour12:false})}
                  stroke="#94a3b8" 
                  minTickGap={50}
                />
                <YAxis domain={['dataMin - 10', 'dataMax + 10']} stroke="#94a3b8" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                  labelFormatter={(unixTime) => new Date(unixTime * 1000).toLocaleTimeString()}
                />
                <Legend wrapperStyle={{ paddingTop: '20px' }}/>
                
                <Line 
                  type="monotone" 
                  dataKey="price" 
                  name="Raw Signal (Price)"
                  stroke="#94a3b8" 
                  strokeWidth={1.5}
                  dot={false}
                  opacity={0.5}
                  isAnimationActive={false}
                />
                <Line 
                  type="monotone" 
                  dataKey="fixed_ema" 
                  name="Fixed EMA"
                  stroke="#f43f5e" 
                  strokeWidth={2}
                  dot={false}
                  isAnimationActive={false}
                />
                <Line 
                  type="monotone" 
                  dataKey="adaptive_ema" 
                  name="Load-Adaptive EMA"
                  stroke="#3b82f6" 
                  strokeWidth={3}
                  dot={false}
                  isAnimationActive={false}
                />
                
                {/* Render red dots for anomalies on the adaptive line */}
                {data.map((entry, index) => {
                  if (entry.is_anomaly) {
                    return <ReferenceDot key={index} x={entry.timestamp} y={entry.price} r={6} fill="#ef4444" stroke="#7f1d1d" strokeWidth={2} />
                  }
                  return null;
                })}
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Real-time Metrics Side Panel */}
        <div className="space-y-8">
          
          {/* Backpressure Gauge */}
          <div className="bg-slate-800 rounded-2xl shadow-lg border border-slate-700 p-6 transition-all duration-300">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Cpu className="text-rose-400" /> System Load (L)
            </h2>
            <div className="relative pt-1">
              <div className="flex mb-2 items-center justify-between">
                <div>
                  <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full bg-slate-700">
                    Queue Utilization
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-xl font-bold font-mono">
                    {latestData ? (latestData.load * 100).toFixed(1) : 0}%
                  </span>
                </div>
              </div>
              <div className="overflow-hidden h-4 mb-4 text-xs flex rounded-full bg-slate-900 border border-slate-700">
                <div 
                  style={{ width: `${latestData ? latestData.load * 100 : 0}%` }} 
                  className={`shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center transition-all duration-300 ${
                    latestData && latestData.load > 0.8 ? 'bg-rose-500' : 'bg-blue-500'
                  }`}
                ></div>
              </div>
            </div>
          </div>

          {/* Pole Alpha Visualizer */}
          <div className="bg-slate-800 rounded-2xl shadow-lg border border-slate-700 p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Zap className="text-amber-400" /> Adaptive Pole (α)
            </h2>
            <div className="flex items-center justify-center p-4 bg-slate-900 rounded-xl border border-slate-700">
              <span className="text-4xl font-mono font-bold text-amber-400 shadow-amber-500/20 drop-shadow-md transition-all duration-300">
                {latestData ? latestData.alpha.toFixed(4) : "0.0000"}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-4 text-center">
              Pole shifts toward DC (lower α) under high load to aggressively smooth noise and shed compute.
            </p>
          </div>

          {/* Anomaly Feed */}
          <div className="bg-slate-800 rounded-2xl shadow-lg border border-slate-700 p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <ShieldAlert className="text-emerald-400" /> Anomaly Feed
            </h2>
            <div className="space-y-3 h-[200px] overflow-y-auto pr-2 custom-scrollbar">
              {anomalies.length === 0 ? (
                <div className="text-slate-500 text-sm italic text-center mt-10">Waiting for anomalies...</div>
              ) : (
                anomalies.map((a, idx) => (
                  <div key={idx} className="flex justify-between items-center bg-slate-900 p-3 rounded-lg border border-slate-700 animate-in slide-in-from-right-4 duration-300">
                    <div>
                      <div className="text-sm font-semibold text-rose-400">Spike Detected</div>
                      <div className="text-xs font-mono text-slate-400">{a.time}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-mono text-slate-200">${a.price}</div>
                      <div className="text-xs text-slate-500">Load: {(a.load*100).toFixed(0)}%</div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
