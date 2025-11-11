
import type { Metadata } from "next";
// import { Inter } from "next/font/google";
import "./globals.css";
import { Toaster } from "sonner";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import Providers from "@/components/providers";

// const inter = Inter({ subsets: ["latin"] });
// Using system fonts instead of Google Fonts due to network restrictions
const inter = { className: "font-sans" };

export const metadata: Metadata = {
  title: "Sovereign Legacy Loop - Crypto Wealth Management",
  description: "Professional crypto wealth management platform with dual-tier trading and cold vault storage",
};

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await getServerSession(authOptions);

  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers session={session}>
          {children}
          <Toaster richColors position="top-right" />
        </Providers>
      </body>
    </html>
  );
}
