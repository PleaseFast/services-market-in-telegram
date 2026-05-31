declare global {
  interface Window {
    Telegram?: {
      WebApp?: {
        initData: string;
        ready: () => void;
        expand: () => void;
        themeParams?: { bg_color?: string };
        colorScheme?: "light" | "dark";
        initDataUnsafe?: {
          user?: { language_code?: string };
        };
      };
    };
  }
}

export function getInitData(): string | null {
  const wa = window.Telegram?.WebApp;
  if (wa && wa.initData) return wa.initData;
  return null;
}

export function isMiniApp(): boolean {
  return !!getInitData();
}

export function applyTelegramTheme(): void {
  const wa = window.Telegram?.WebApp;
  if (!wa) return;
  wa.ready();
  wa.expand();
  if (wa.colorScheme === "dark") document.documentElement.classList.add("dark");
}
