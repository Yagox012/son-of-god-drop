import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SON OF GOD — Drop 01",
  description: "Acceso anticipado para el primer drop de SON OF GOD.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="es-MX"><body>{children}</body></html>;
}
