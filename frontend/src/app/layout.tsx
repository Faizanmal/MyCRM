import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/contexts/AuthContext";
import { ClientLayout } from '@/components/ClientLayout';
import { QueryProvider } from "@/components/QueryProvider";
import { RealtimeProvider } from "@/components/enterprise/RealtimeProvider";
import InstallPrompt from "@/components/InstallPrompt";
import CommandPalette from "@/components/CommandPalette";
import FloatingAIAssistant from "@/components/FloatingAIAssistant";
import { AchievementProvider } from "@/components/AchievementToast";
import KeyboardShortcutsModal from "@/components/KeyboardShortcutsModal";
import ProductTour from "@/components/ProductTour";
import QuickActionsFab from "@/components/QuickActionsFab";
import OnboardingChecklist from "@/components/OnboardingChecklist";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "MyCRM - Customer Relationship Management",
  description: "A fully functional CRM system for managing customer interactions, sales pipelines, and business relationships.",
  manifest: "/manifest.json",
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "MyCRM",
  },
  icons: {
    icon: [
      { url: "/icon-192.svg", sizes: "192x192", type: "image/svg+xml" },
      { url: "/icon-512.svg", sizes: "512x512", type: "image/svg+xml" },
    ],
    apple: [
      { url: "/icon-192.svg", sizes: "192x192", type: "image/svg+xml" },
    ],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <meta name="application-name" content="MyCRM" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta name="apple-mobile-web-app-title" content="MyCRM" />
        <meta name="format-detection" content="telephone=no" />
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="theme-color" content="#2563eb" />
        <script
          dangerouslySetInnerHTML={{
            __html: `!function(){try{var d=document.documentElement.classList;d.remove('light','dark');var e=localStorage.getItem('theme');if('system'===e||(!e&&true)){var m='(prefers-color-scheme: dark)',t=window.matchMedia(m);t.media!==m||t.matches?d.add('dark'):d.add('light')}else if(e) d.add(e)}catch(e){}}()`,
          }}
        />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <ClientLayout>
          <QueryProvider>
            <AuthProvider>
              <AchievementProvider>
                <RealtimeProvider>
                  {children}
                  <CommandPalette />
                  <FloatingAIAssistant />
                  <InstallPrompt />
                  <KeyboardShortcutsModal />
                  <ProductTour />
                  <QuickActionsFab />
                  <OnboardingChecklist />
                </RealtimeProvider>
              </AchievementProvider>
            </AuthProvider>
          </QueryProvider>
        </ClientLayout>
      </body>
    </html>
  );
}
