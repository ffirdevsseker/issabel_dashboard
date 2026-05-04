import { Navigate } from "react-router-dom";
import { Loader2 } from "lucide-react";
import { useAuth } from "@/context/AuthContext";

export default function ProtectedRoute({
  children,
  requireAdmin = false,
  requireSupervisor = false,
}) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <Loader2 className="h-8 w-8 animate-spin text-slate-400" />
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (requireAdmin && user.role !== "admin") {
    // Yetkisiz kullanıcı ana dashboard'a geri gitsin
    return <Navigate to="/" replace />;
  }

  if (requireSupervisor && !["admin", "supervizor"].includes(user.role)) {
    // Yetkisiz personel ana dashboard'a geri gitsin
    return <Navigate to="/" replace />;
  }

  return children;
}