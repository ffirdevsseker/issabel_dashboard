const dispositionBadge = (disposition) => {
  const styles = {
    ANSWERED: "bg-green-100 text-green-800",
    "NO ANSWER": "bg-yellow-100 text-yellow-800",
    BUSY: "bg-orange-100 text-orange-800",
    FAILED: "bg-red-100 text-red-800",
  };
  const cls = styles[disposition] || "bg-gray-100 text-gray-800";
  return (
    <span className={`px-2 py-1 rounded text-xs font-semibold ${cls}`}>
      {disposition}
    </span>
  );
};

const formatDuration = (seconds) => {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
};

const formatDate = (iso) => {
  const d = new Date(iso);
  return d.toLocaleString("tr-TR");
};

export default function CallsTable({ calls }) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-800">Son Çağrılar</h2>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 text-xs uppercase text-gray-600">
            <tr>
              <th className="px-6 py-3 text-left">Tarih</th>
              <th className="px-6 py-3 text-left">Arayan</th>
              <th className="px-6 py-3 text-left">Aranan</th>
              <th className="px-6 py-3 text-left">Süre</th>
              <th className="px-6 py-3 text-left">Durum</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 text-sm">
            {calls.map((call) => (
              <tr key={call.uniqueid} className="hover:bg-gray-50">
                <td className="px-6 py-3 text-gray-600">{formatDate(call.calldate)}</td>
                <td className="px-6 py-3 font-medium text-gray-800">{call.src}</td>
                <td className="px-6 py-3 text-gray-700">{call.dst}</td>
                <td className="px-6 py-3 text-gray-600">{formatDuration(call.billsec)}</td>
                <td className="px-6 py-3">{dispositionBadge(call.disposition)}</td>
              </tr>
            ))}
            {calls.length === 0 && (
              <tr>
                <td colSpan={5} className="px-6 py-8 text-center text-gray-500">
                  Henüz çağrı yok
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}