import { AlertOctagon, Rocket, ShieldAlert, Sparkles } from "lucide-react";

const buttonBase = {
  borderRadius: 10,
  border: "1px solid transparent",
  padding: "9px 12px",
  fontSize: 12,
  fontWeight: 800,
  cursor: "pointer",
  display: "inline-flex",
  alignItems: "center",
  gap: 6,
  transition: "all 0.2s",
  whiteSpace: "nowrap",
};

export default function AdminActionBar({
  primaryLabel = "Talimat Ver",
  directApplyLabel = "Doğrudan Uygula",
  overrideLabel = "Override",
  emergencyLabel = "Acil Müdahale",
}) {
  return (
    <div
      style={{
        display: "flex",
        flexWrap: "wrap",
        gap: 8,
        alignItems: "center",
      }}
    >
      <button
        style={{
          ...buttonBase,
          background: "linear-gradient(135deg,#2563eb,#1d4ed8)",
          color: "#fff",
          boxShadow: "0 2px 8px rgba(37,99,235,0.25)",
        }}
      >
        <Sparkles style={{ width: 14, height: 14 }} />
        {primaryLabel}
      </button>

      <button
        style={{
          ...buttonBase,
          background: "rgba(16,185,129,0.1)",
          border: "1px solid rgba(16,185,129,0.3)",
          color: "#059669",
        }}
      >
        <Rocket style={{ width: 14, height: 14 }} />
        {directApplyLabel}
      </button>

      <button
        style={{
          ...buttonBase,
          background: "rgba(249,115,22,0.1)",
          border: "1px solid rgba(249,115,22,0.28)",
          color: "#c2410c",
        }}
      >
        <ShieldAlert style={{ width: 14, height: 14 }} />
        {overrideLabel}
      </button>

      <button
        style={{
          ...buttonBase,
          background: "rgba(239,68,68,0.1)",
          border: "1px solid rgba(239,68,68,0.3)",
          color: "#b91c1c",
        }}
      >
        <AlertOctagon style={{ width: 14, height: 14 }} />
        {emergencyLabel}
      </button>
    </div>
  );
}
