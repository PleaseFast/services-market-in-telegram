import i18n from "i18next";
import { initReactI18next } from "react-i18next";

import en from "./locales/en.json";
import ru from "./locales/ru.json";

export const SUPPORTED_LANGUAGES = ["ru", "en"] as const;
export type Language = (typeof SUPPORTED_LANGUAGES)[number];
export const DEFAULT_LANGUAGE: Language = "ru";

const STORAGE_KEY = "doings-lang";

export function normalizeLanguage(raw: string | null | undefined): Language {
  if (!raw) return DEFAULT_LANGUAGE;
  const primary = raw.toLowerCase().replace(/_/g, "-").split("-")[0];
  return (SUPPORTED_LANGUAGES as readonly string[]).includes(primary)
    ? (primary as Language)
    : DEFAULT_LANGUAGE;
}

function detectInitialLanguage(): Language {
  // 1) Telegram Mini App user language wins when available — the user
  //    chose it in their Telegram client.
  const tgLang = window.Telegram?.WebApp?.initDataUnsafe?.user?.language_code;
  if (tgLang) return normalizeLanguage(tgLang);

  // 2) Persisted user choice from a previous session.
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) return normalizeLanguage(stored);
  } catch {
    /* private mode / SSR — ignore */
  }

  // 3) Browser preference.
  if (typeof navigator !== "undefined" && navigator.language) {
    return normalizeLanguage(navigator.language);
  }

  return DEFAULT_LANGUAGE;
}

const initialLanguage = detectInitialLanguage();

void i18n.use(initReactI18next).init({
  resources: {
    en: { translation: en },
    ru: { translation: ru },
  },
  lng: initialLanguage,
  fallbackLng: DEFAULT_LANGUAGE,
  supportedLngs: [...SUPPORTED_LANGUAGES],
  interpolation: { escapeValue: false },
  returnNull: false,
});

function syncDocument(lang: Language) {
  if (typeof document !== "undefined") {
    document.documentElement.setAttribute("lang", lang);
    const title = i18n.t("common.appTitle");
    if (typeof title === "string") {
      document.title = title;
    }
  }
}

syncDocument(initialLanguage);

i18n.on("languageChanged", (lang) => {
  const normalized = normalizeLanguage(lang);
  try {
    localStorage.setItem(STORAGE_KEY, normalized);
  } catch {
    /* ignore */
  }
  syncDocument(normalized);
});

export function changeLanguage(lang: Language): Promise<unknown> {
  return i18n.changeLanguage(lang);
}

export function getCurrentLanguage(): Language {
  return normalizeLanguage(i18n.language);
}

export default i18n;
