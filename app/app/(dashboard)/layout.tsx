
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { redirect } from "next/navigation";
import Sidebar from "@/components/sidebar";
import DynamicFloatingCoins from "@/components/dynamic-floating-coins";

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await getServerSession(authOptions);

  if (!session) {
    redirect("/");
  }

  return (
    <div className="flex h-screen overflow-hidden relative bg-black text-white">
      {/* Custom Nebula Background - Same as welcome page */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,#1a1a1a,#000)]" />
      <div
        className="absolute inset-0"
        style={{
          backgroundImage: `
            radial-gradient(circle at 50% 20%, rgba(255,140,66,0.25), transparent 55%),
            radial-gradient(circle at 20% 80%, rgba(76,145,255,0.18), transparent 55%),
            radial-gradient(circle at 80% 20%, rgba(139,69,199,0.15), transparent 55%)
          `,
          backgroundSize: "cover, cover, cover",
          backgroundPosition: "center, center, center",
          opacity: 0.9,
        }}
      />
      
      {/* Dynamic Floating Coins System */}
      <DynamicFloatingCoins />
      
      {/* Content */}
      <div className="relative z-10 flex h-full w-full">
        <Sidebar />
        <main className="flex-1 ml-64 overflow-y-auto">
          <div className="container mx-auto px-6 py-6 max-w-7xl">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
