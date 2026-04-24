import type { Metadata } from "next";
import { Cairo } from "next/font/google";
import { Toaster } from "@/components/ui/sonner";
import "./globals.css";

const cairo = Cairo({
  variable: "--font-sans",
  subsets: ["arabic", "latin"],
  weight: ["300", "400", "500", "600", "700", "800"],
});

export const metadata: Metadata = {
  title: "سر الجدة - حكمة زمان بصوت دلوقتي",
  description:
    "منصة مصرية لحفظ حكم وأسرار الجدات - وصفات، علاجات شعبية، أمثال، نصائح حياتية، وحكايات من زمان",
  keywords: [
    "حكمة",
    "جدة",
    "مصر",
    "وصفات",
    "أمثال",
    "علاجات شعبية",
    "تراث مصري",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ar" dir="rtl" className={`${cairo.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col font-sans">
        {children}
        <Toaster position="top-center" richColors />
      </body>
    </html>
  );
}
