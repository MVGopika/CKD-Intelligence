"use client";

import { useState, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { getCurrentUser } from "../../services/authService";
import { clearToken } from "../../lib/auth";
import Link from "next/link";
import { toast } from "sonner";

export default function Navbar() {
  const [user, setUser] = useState<any>(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    async function loadUser() {
      try {
        const response = await getCurrentUser();
        setUser(response.data);
      } catch {
        setUser(null);
      }
    }
    loadUser();
  }, []);

  const handleLogout = () => {
    clearToken();
    setUser(null);
    toast.success("Logged out successfully");
    router.push("/");
  };

  const linkClass = (path: string) =>
    `relative transition px-3 py-2 rounded-lg ${
      pathname === path
        ? "text-white bg-white/10"
        : "text-zinc-400 hover:text-white hover:bg-white/5"
    }`;

  return (
    <nav className="sticky top-0 z-50 backdrop-blur-xl bg-black/70 border-b border-white/10 shadow-[0_4px_30px_rgba(0,0,0,0.4)]">
      <div className="mx-auto px-6">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href="/" className="text-2xl font-bold tracking-tight">
            <span className="text-white">CKD</span>{" "}
            <span className="bg-gradient-to-r from-blue-500 to-cyan-400 bg-clip-text text-transparent">
              Intelligence
            </span>
          </Link>

          {/* Desktop Links */}
          {user && (
            <div className="hidden md:flex items-center gap-3 text-sm font-medium">
              <Link
                href={
                  user.role_id === 11 || user.role_id === 1
                    ? "/dashboard/patient"
                    : "/dashboard/doctor"
                }
                className={linkClass(
                  user.role_id === 11 || user.role_id === 1
                    ? "/dashboard/patient"
                    : "/dashboard/doctor",
                )}
              >
                Dashboard
              </Link>

              {user.role_id === 11 || user.role_id === 1 && (
                <>
                  <Link
                    href="/consultation"
                    className={linkClass("/consultation")}
                  >
                    Consultation Prediction
                  </Link>
                  <Link href="/prediction" className={linkClass("/prediction")}>
                    Features Prediction
                  </Link>
                  <a
                    href="http://127.0.0.1:5000/image_based"
                    target="_blank"
                    rel="noopener noreferrer"
                    className={linkClass("/image_based")}
                  >
                    Image Prediction
                  </a>
                  <Link href="/reports" className={linkClass("/reports")}>
                    Reports
                  </Link>
                </>
              )}
            </div>
          )}

          {/* Right Side */}
          <div className="flex items-center gap-4">
            {!user && (
              <div className="hidden md:flex items-center gap-4">
                <Link
                  href="/auth/login"
                  className="text-zinc-400 hover:text-white transition text-sm"
                >
                  Login
                </Link>
                <Link
                  href="/auth/register"
                  className="bg-gradient-to-r from-blue-600 to-cyan-500 hover:opacity-90 text-white px-5 py-2 rounded-xl text-sm font-semibold shadow-lg shadow-blue-500/20 transition"
                >
                  Get Started
                </Link>
              </div>
            )}

            {/* Profile */}
            {user && (
              <div className="relative">
                <button
                  onClick={() => setMenuOpen(!menuOpen)}
                  className="flex items-center gap-2"
                >
                  <div className="h-9 w-9 rounded-full bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center text-white font-semibold shadow-lg">
                    {user.full_name?.charAt(0)}
                  </div>
                  <span className="hidden md:block text-zinc-300 text-sm">
                    {user.full_name}
                  </span>
                </button>

                {menuOpen && (
                  <div className="absolute right-0 mt-3 w-56 bg-black backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl py-2 animate-fadeIn">
                    <div className="px-4 py-2 text-xs text-zinc-500">
                      Signed in as
                      <div className="text-zinc-300 text-sm mt-1">
                        {user.email}
                      </div>
                    </div>
                    <div className="border-t border-white/10 my-2" />
                    <button
                      onClick={handleLogout}
                      className="w-full text-left px-4 py-2 text-sm text-zinc-300 hover:bg-white/5 hover:text-white transition rounded-lg"
                    >
                      Logout
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* Mobile Toggle */}
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="md:hidden text-zinc-300 text-2xl"
            >
              {mobileOpen ? "✕" : "☰"}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        <div
          className={`md:hidden overflow-hidden transition-all duration-300 ${
            mobileOpen ? "max-h-96 opacity-100 py-4" : "max-h-0 opacity-0"
          }`}
        >
          <div className="space-y-3 text-sm font-medium">
            {user ? (
              <>
                <Link
                  href={
                    user.role_id === 11 || user.role_id === 1
                      ? "/dashboard/patient"
                      : "/dashboard/doctor"
                  }
                  className="block text-zinc-400 hover:text-white"
                >
                  Dashboard
                </Link>

                {user.role_id === 11 ||  user.role_id === 1 && (
                  <>
                    <Link
                      href="/consultation"
                      className="block text-zinc-400 hover:text-white"
                    >
                      Consultation
                    </Link>
                    <Link
                      href="/prediction"
                      className="block text-zinc-400 hover:text-white"
                    >
                      Prediction
                    </Link>
                    <Link
                      href="/reports"
                      className="block text-zinc-400 hover:text-white"
                    >
                      Reports
                    </Link>
                  </>
                )}

                <button
                  onClick={handleLogout}
                  className="block text-left text-red-400 hover:text-red-500"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link
                  href="/auth/login"
                  className="block text-zinc-400 hover:text-white"
                >
                  Login
                </Link>
                <Link
                  href="/auth/register"
                  className="block text-zinc-400 hover:text-white"
                >
                  Register
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
