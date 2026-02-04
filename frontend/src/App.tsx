import { useState } from "react";

type RiskResult = {
  risk_score: number;
  risk_level: "LOW" | "MEDIUM" | "HIGH";
  risk_factors: string[];
  context_signals?: string[]; 
  explanation: string;
};

export default function App() {
  const [form, setForm] = useState({
    user_id: 10,
    transaction_type: "payment",
    amount: 1200,
    timestamp: "2024-01-12T12:14:00",
    device_id: "device_10_1",
    location: "UK",
  });

  const [result, setResult] = useState<RiskResult | null>(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const analyze = async () => {
    setLoading(true);
    setResult(null);

    const res = await fetch("http://127.0.0.1:8000/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: Number(form.user_id),
        transaction_type: form.transaction_type,
        amount: Number(form.amount),
        timestamp: form.timestamp,
        device_id: form.device_id,
        location: form.location,
      }),
    });

    const data = await res.json();
    setResult(data);
    setLoading(false);
  };

  const riskColor =
    result?.risk_level === "HIGH"
      ? "#DC2626"
      : result?.risk_level === "MEDIUM"
      ? "#F59E0B"
      : "#16A34A";

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#FCE8E8",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        padding: 32,
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: 960,
          background: "#0F172A",
          padding: "48px",
          borderRadius: 14,
          color: "#E5E7EB",
          fontFamily: "sans-serif",
        }}
      >
        <h1 style={{ textAlign: "center", marginBottom: 32 }}>
          AI Transaction Risk Analyzer
        </h1>

        {/* INPUT FORM */}
        <div style={{ display: "grid", gap: 12 }}>
          <input
            name="user_id"
            placeholder="User ID"
            value={form.user_id}
            onChange={handleChange}
          />

          <select
            name="transaction_type"
            value={form.transaction_type}
            onChange={handleChange}
          >
            <option value="payment">Payment</option>
            <option value="transfer">Transfer</option>
            <option value="cashout">Cash Out</option>
            <option value="deposit">Deposit</option>
          </select>

          <input
            name="amount"
            placeholder="Amount"
            value={form.amount}
            onChange={handleChange}
          />

          <input
            name="timestamp"
            placeholder="Timestamp (ISO)"
            value={form.timestamp}
            onChange={handleChange}
          />

          <input
            name="device_id"
            placeholder="Device ID"
            value={form.device_id}
            onChange={handleChange}
          />

          <select
            name="location"
            value={form.location}
            onChange={handleChange}
          >
            <option value="IN">IN</option>
            <option value="UK">UK</option>
            <option value="US">US</option>
          </select>

          <button
            onClick={analyze}
            disabled={loading}
            style={{
              marginTop: 16,
              backgroundColor: loading ? "#93C5FD" : "#60A5FA",
              color: "#0F172A",
              padding: "14px",
              borderRadius: 10,
              border: "none",
              fontWeight: 600,
              cursor: loading ? "not-allowed" : "pointer",
            }}
          >
            {loading ? "Analyzing..." : "Analyze Transaction"}
          </button>
        </div>

        {/* RESULT */}
        {result && (
          <div
            style={{
              marginTop: 40,
              padding: 24,
              borderRadius: 12,
              background: "#020617",
              border: "1px solid #334155",
            }}
          >
            <h2>Risk Assessment</h2>

            <p>
              <strong>Risk Level:</strong>{" "}
              <span style={{ color: riskColor, fontWeight: "bold" }}>
                {result.risk_level}
              </span>
            </p>

            <p>
              <strong>Risk Score:</strong> {result.risk_score}
            </p>

            {result.risk_factors.length > 0 && (
              <div style={{ marginTop: 12 }}>
                <strong>Risk Factors:</strong>
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                  {result.risk_factors.map((f, i) => (
                    <span
                      key={i}
                      style={{
                        background: "#1E293B",
                        border: "1px solid #334155",
                        padding: "6px 10px",
                        borderRadius: 999,
                        fontSize: 12,
                      }}
                    >
                      {f}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {result.context_signals && result.context_signals.length > 0 && (
              <>
                <p><b>Context:</b></p>
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                  {result.context_signals.map((c, i) => (
                    <span
                      key={i}
                      style={{
                        padding: "4px 8px",
                        borderRadius: 12,
                        background: "#1f2937",
                        border: "1px solid #374151",
                        fontSize: 12,
                        color: "#cbd5e1"
                      }}
                    >
                      {c}
                    </span>
                  ))}
                </div>
              </>
            )}

            <div style={{ marginTop: 16 }}>
              <strong>Explanation:</strong>
              <p style={{ marginTop: 6, lineHeight: 1.5 }}>
                {result.explanation}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}