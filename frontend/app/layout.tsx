import "./globals.css";
import Navbar from "../components/layout/Navbar";
import { Toaster } from "../components/ui/sonner";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-black">
        <Navbar />
        <main className="container mx-auto bg-black">{children}</main>
        <Toaster />
      </body>
    </html>
  );
}
