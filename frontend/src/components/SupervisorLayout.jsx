import { Outlet } from "react-router-dom";
import Sidebar from "@/components/Sidebar";

/**
 * Supervisor Layout — sidebar + header + page content
 * Sidebar `useLocation()` ile path'e göre supervisor nav'ını otomatik gösterir.
 */
export default function SupervisorLayout() {
  return (
    <div className="flex min-h-screen bg-gradient-to-br from-slate-100 via-[#edf3f8] to-[#e6eef6] p-3 gap-3">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <main className="flex-1 overflow-x-hidden relative">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
