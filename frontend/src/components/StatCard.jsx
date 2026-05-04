export default function StatCard({ title, value, subtitle, color = "blue" }) {
  const colorClasses = {
    blue: "bg-blue-50 text-blue-700 border-blue-200",
    green: "bg-green-50 text-green-700 border-green-200",
    red: "bg-red-50 text-red-700 border-red-200",
    yellow: "bg-yellow-50 text-yellow-700 border-yellow-200",
    purple: "bg-purple-50 text-purple-700 border-purple-200",
  };

  return (
    <div className={`p-6 rounded-lg border ${colorClasses[color]} shadow-sm`}>
      <div className="text-sm font-medium opacity-75">{title}</div>
      <div className="text-3xl font-bold mt-2">{value}</div>
      {subtitle && <div className="text-xs mt-1 opacity-60">{subtitle}</div>}
    </div>
  );
}