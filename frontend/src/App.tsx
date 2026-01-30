import { useState } from "react";

type Result = {
  risk_score: number;
  risk_level: string;
  risk_factors: string[];
  explanation: string;
};

export default function App() {
  const [form, setForm] = useState({
    user_id: 10,
    amount: 1200,
    timestamp: "2024-01-12T03:14:00",
    device_id: 99,
    location: 20,
  });
  
  
  const [result, setResult] = useState<Result | null>(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<any[]>([]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const analyze = async () => {
    setLoading(true);
    setResult(null);

    const res = await fetch("http://127.0.0.1:8000/analyze", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_id: Number(form.user_id),
        amount: Number(form.amount),
        timestamp: form.timestamp,
        device_id: Number(form.device_id),
        location: Number(form.location),
      }),
    });

    const data = await res.json();
    setResult(data);
    setHistory(prev => [data, ...prev].slice(0, 5));
    setLoading(false);
  };
  
  const signals = result?.risk_factors ?? [];

  const riskColor =
  result?.risk_level === "HIGH"
    ? "red"
    : result?.risk_level === "MEDIUM"
    ? "orange"
    : "green";


  return (
    <div style={{ fontFamily: "sans-serif", padding: 30, maxWidth: 600 }}>
      <h1>AI Transaction Risk Analyzer</h1>

      <button onClick={() => setForm({
        user_id: 10,
        amount: 20000,
        timestamp: "2024-01-12T03:14:00",
        device_id: 99,
        location: 20
      })}>
        Load High-Risk Example
      </button>

      <button onClick={() => setForm({
        user_id: 10,
        amount: 200,
        timestamp: "2024-01-12T14:30:00",
        device_id: 5,
        location: 3
      })}>
        Load Normal Example
      </button>

      <div style={{ display: "grid", gap: 10 }}>
        <input name="user_id" placeholder="User ID" value={form.user_id} onChange={handleChange} />
        <input name="amount" placeholder="Amount" value={form.amount} onChange={handleChange} />
        <input name="timestamp" placeholder="Timestamp (ISO)" value={form.timestamp} onChange={handleChange} />
        <input name="device_id" placeholder="Device ID" value={form.device_id} onChange={handleChange} />
        <input name="location" placeholder="Location" value={form.location} onChange={handleChange} />

        <button onClick={analyze} disabled={loading}>
          {loading ? "Analyzing transaction..." : "Analyze Transaction"}
        </button>
      </div>
      {loading && <p>Contacting risk engine…</p>}

      {result && (
        <div
          style={{
            marginTop: 20,
            padding: 20,
            borderRadius: 8,
            background:
              result.risk_level === "HIGH"
                ? "#3b0d0d"
                : result.risk_level === "MEDIUM"
                ? "#3b2d0d"
                : "#0d3b1b",
            border: "1px solid #444"
          }}
        >
          <h2>Result</h2>

          <p>
            <b>Risk Score:</b> {result.risk_score}
          </p>

          <p>
            <b>Risk Level:</b>{" "}
            <span style={{ color: riskColor, fontWeight: "bold" }}>
              {result.risk_level}
            </span>
          </p>
          <div style={{ marginTop: 8, display: "flex", gap: 8, flexWrap: "wrap" }}>
            {signals.map((s, i) => (
              <span
                key={i}
                style={{
                  padding: "4px 8px",
                  borderRadius: 12,
                  background: "#222",
                  border: "1px solid #444",
                  fontSize: 12
                }}
              >
                {s}
              </span>
            ))}
          </div>

          <p>
            <b>Explanation:</b> {result.explanation}
          </p>

          {/* progress bar */}
          <div
            style={{
              height: 10,
              background: "#eee",
              borderRadius: 5,
              overflow: "hidden",
              marginTop: 10
            }}
          >
            <div
              style={{
                width: `${result.risk_score * 100}%`,
                background: riskColor,
                height: "100%"
              }}
            />
          </div>
        </div>
      )}
      {history.length > 0 && (
        <div style={{ marginTop: 30 }}>
          <h3>Recent Analyses</h3>
          {history.map((h, i) => (
            <div
              key={i}
              style={{
                border: "1px solid #333",
                borderRadius: 8,
                padding: 10,
                marginTop: 10,
                background: "#111"
              }}
            >
              <div>Score: {h.risk_score}</div>
              <div>
                Level:{" "}
                <span
                  style={{
                    color:
                      h.risk_level === "HIGH"
                        ? "red"
                        : h.risk_level === "MEDIUM"
                        ? "orange"
                        : "green",
                    fontWeight: "bold"
                  }}
                >
                  {h.risk_level}
                </span>
              </div>
              <div style={{ fontSize: 12, opacity: 0.8 }}>
                {h.explanation}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}