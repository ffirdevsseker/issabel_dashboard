import AdminActionBar from "@/pages/admin/components/AdminActionBar";

export default function AdminPageHeader({
  title,
  description,
  primaryLabel,
  directApplyLabel,
  overrideLabel,
  emergencyLabel,
}) {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "flex-start",
        justifyContent: "space-between",
        gap: 16,
        flexWrap: "wrap",
      }}
    >
      <div>
        <h2 style={{ color: "#1e293b", fontSize: 22, fontWeight: 800, margin: 0 }}>{title}</h2>
        <p style={{ color: "#64748b", fontSize: 13, margin: "5px 0 0", maxWidth: 760 }}>
          {description}
        </p>
      </div>

      <AdminActionBar
        primaryLabel={primaryLabel}
        directApplyLabel={directApplyLabel}
        overrideLabel={overrideLabel}
        emergencyLabel={emergencyLabel}
      />
    </div>
  );
}
