import { useTranslation } from "react-i18next";

import { Button } from "@/components/ui/button";
import i18n, { type Language, SUPPORTED_LANGUAGES } from "@/i18n";
import { http } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";

const FLAGS: Record<Language, string> = {
  ru: "🇷🇺",
  en: "🇬🇧",
};

export function LanguageSwitcher() {
  const { t } = useTranslation();
  const language = useAuthStore((s) => s.language);
  const accessToken = useAuthStore((s) => s.accessToken);
  const setLanguage = useAuthStore((s) => s.setLanguage);

  // Two-way toggle between the two supported languages. With only RU and EN
  // it's faster than a dropdown for the typical use case.
  const other: Language = language === "ru" ? "en" : "ru";

  const onToggle = async () => {
    setLanguage(other);
    await i18n.changeLanguage(other);
    if (accessToken) {
      try {
        await http.patch("/users/me/language", { language: other });
      } catch {
        /* non-fatal; client-side preference stays */
      }
    }
  };

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => void onToggle()}
      aria-label={t("common.language.toggle")}
      title={`${FLAGS[language]} → ${FLAGS[other]}`}
    >
      <span aria-hidden className="text-base">
        {FLAGS[other]}
      </span>
    </Button>
  );
}

export { SUPPORTED_LANGUAGES };
