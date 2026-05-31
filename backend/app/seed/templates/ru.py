"""Russian translations of the curated project templates.

Order and category strings must match ``en.py`` row-for-row — the seed loader
pairs them by index so the canonical English row gets an ``ru`` translation
written into ``project_template_translations`` for the same template_id.
"""

PROJECT_TEMPLATES_RU: list[dict[str, str]] = [
    # ---------------- Frontend ----------------
    {
        "title": "Лендинг для SaaS-продукта",
        "category": "Frontend",
        "description_template": (
            "Сверстать адаптивный маркетинговый лендинг. Секции: герой, фичи, "
            "тарифы, FAQ, футер. Стек на выбор (предпочтительно Next.js). "
            "Результат: задеплоенный превью, Lighthouse ≥ 90, блоки контента, "
            "дружелюбные к CMS."
        ),
    },
    {
        "title": "Перенос маркетингового сайта на Next.js",
        "category": "Frontend",
        "description_template": (
            "Переписать 6–8 страниц маркетингового сайта на Next.js (App Router). "
            "Перенести контент и ассеты с текущего WordPress, подключить "
            "headless CMS (Sanity или Contentful), сохранить SEO-парность с "
            "существующими URL и метатегами."
        ),
    },
    {
        "title": "Админ-панель с CRUD-таблицами",
        "category": "Frontend",
        "description_template": (
            "Внутренняя админ-панель поверх существующего REST API. ~6 сущностей, "
            "у каждой список / детальный экран / создание / редактирование / "
            "удаление, серверная пагинация, фильтры, разграничение прав. "
            "React + shadcn/ui или Refine."
        ),
    },
    {
        "title": "Дашборд аналитики по дизайну Figma",
        "category": "Frontend",
        "description_template": (
            "Реализовать многотабовый дашборд аналитики по готовым макетам "
            "в Figma. Графики через Recharts или Tremor, фильтр по датам, "
            "экспорт CSV. Данные из задокументированного JSON API. "
            "Пиксельная точность на десктопе, адаптив на планшете."
        ),
    },
    {
        "title": "Оптимизация производительности и SSR",
        "category": "Frontend",
        "description_template": (
            "Наше Next.js-приложение даёт 40–55 в Lighthouse на мобильных. "
            "Провести аудит и починить: применить SSR/ISR где уместно, "
            "устранить блокирующий JS, оптимизировать изображения и шрифты, "
            "исправить CLS. Цель — 85+ на 5 самых посещаемых страницах."
        ),
    },
    {
        "title": "Анимации и микровзаимодействия на Framer Motion",
        "category": "Frontend",
        "description_template": (
            "Добавить выверенные анимации на 8–10 поверхностях (навигация, "
            "модалки, перестановка списков, переходы между страницами, "
            "появление героя). Использовать Framer Motion. Уважать "
            "prefers-reduced-motion. На выходе — небольшая переиспользуемая "
            "библиотека вариантов."
        ),
    },
    {
        "title": "Рефакторинг библиотеки компонентов дизайн-системы",
        "category": "Frontend",
        "description_template": (
            "Свести разрозненные компоненты в единую библиотеку (Button, Input, "
            "Select, Modal, Toast, Table и т. д.) с документацией Storybook, "
            "типами на TypeScript, доступными примитивами (Radix или Headless "
            "UI) и тёмной темой."
        ),
    },
    {
        "title": "Встраиваемый виджет для сторонних сайтов",
        "category": "Frontend",
        "description_template": (
            "Сделать JS-виджет, который партнёры встраивают одним тегом "
            "<script>. Изолированные стили (Shadow DOM), настройка через "
            "data-атрибуты, асинхронная загрузка, < 30 КБ в gzip. "
            "Демо-страница и документация по интеграции."
        ),
    },
    {
        "title": "Аудит и исправления по WCAG-доступности",
        "category": "Frontend",
        "description_template": (
            "Аудит приложения по WCAG 2.1 AA. На выходе приоритизированный "
            "список проблем (axe + ручная проверка скринридером) и внедрённые "
            "правки: навигация с клавиатуры, управление фокусом, ARIA, "
            "контраст, разметка форм."
        ),
    },
    {
        "title": "Инструментовка для A/B-тестов",
        "category": "Frontend",
        "description_template": (
            "Подключить GrowthBook (или LaunchDarkly / PostHog experiments) "
            "в воронке оплаты и онбординга. Добавить 3 стартовых эксперимента, "
            "задокументировать паттерн вариантов и связать с аналитикой "
            "событий."
        ),
    },
    {
        "title": "MVP-расширение для Chrome",
        "category": "Frontend",
        "description_template": (
            "Расширение для Chrome на Manifest v3, которое {делает X} на "
            "выбранных страницах. Popup-UI + content-script + background "
            "service worker. Авторизация по нашему API, сохранение настроек, "
            "загрузка в Chrome Web Store."
        ),
    },
    # ---------------- Backend ----------------
    {
        "title": "REST API для мобильного приложения",
        "category": "Backend",
        "description_template": (
            "Спроектировать и реализовать REST API: авторизация, пользователи, "
            "основные сущности, OpenAPI-документация. Postgres + удобный для "
            "вас фреймворк. Включить пагинацию, контракт ошибок, валидацию "
            "запросов и коллекцию Postman."
        ),
    },
    {
        "title": "GraphQL-шлюз поверх существующих сервисов",
        "category": "Backend",
        "description_template": (
            "Поднять GraphQL-шлюз перед 3 существующими REST-сервисами. "
            "Schema-first (Apollo или Yoga), DataLoader против N+1, "
            "persisted queries, JWT-авторизация, интеграционные тесты с "
            "моками даунстримов."
        ),
    },
    {
        "title": "Интеграция Stripe Billing и вебхуков",
        "category": "Backend",
        "description_template": (
            "Подключить Stripe Checkout + Billing для подписок (3 тарифа, "
            "trial, пропорциональный пересчёт). Обрабатывать вебхуки "
            "(invoice.paid, обновление/отмена подписки) с идемпотентностью, "
            "ретраями и ссылкой на портал биллинга. Проверить через CLI."
        ),
    },
    {
        "title": "Multi-tenant авторизация и RBAC",
        "category": "Backend",
        "description_template": (
            "Добавить multi-tenant авторизацию: организации, инвайты, роли "
            "(owner/admin/member), скоп по строкам в Postgres. Готовность "
            "к SSO (OIDC). Декоратор/мидлвэр прав и полное тестовое покрытие."
        ),
    },
    {
        "title": "Полнотекстовый поиск на Postgres / Meilisearch",
        "category": "Backend",
        "description_template": (
            "Добавить быстрый поиск с устойчивостью к опечаткам по ~500 тыс. "
            "записей. Сравнить Postgres FTS и Meilisearch / Typesense, "
            "реализовать выбранный вариант, поднять эндпоинт с фильтрами/"
            "фасетами и забэкфилить индекс."
        ),
    },
    {
        "title": "Система фоновых задач",
        "category": "Backend",
        "description_template": (
            "Внедрить систему фоновых задач (Celery / RQ / Sidekiq / BullMQ) "
            "с ретраями, dead-letter, расписаниями и дашбордом. Перенести "
            "3 текущие синхронные задачи (письма, экспорты, вебхуки)."
        ),
    },
    {
        "title": "Загрузка файлов и пайплайн S3",
        "category": "Backend",
        "description_template": (
            "Прямой аплоад в S3 через presigned URL, антивирусная проверка "
            "(ClamAV или Lambda-хук), миниатюры через libvips/Sharp, таблица "
            "attachments с владельцем, размером, mime и политикой жизненного "
            "цикла."
        ),
    },
    {
        "title": "Слой websocket-обновлений",
        "category": "Backend",
        "description_template": (
            "Добавить websocket-слой для живых обновлений (уведомления, "
            "presence, чат). Стек на выбор (Socket.IO / ws / Phoenix "
            "Channels). Авторизация по JWT, fan-out через Redis pub/sub, "
            "переподключение и heartbeat реализованы."
        ),
    },
    {
        "title": "Выделение из легаси-монолита",
        "category": "Backend",
        "description_template": (
            "Выделить bounded context (например, биллинг или уведомления) "
            "из нашего монолита в отдельный сервис. Согласовать контракт API, "
            "dual-write на момент перехода, бэкфилл, затем переключение "
            "чтения. Без даунтайма."
        ),
    },
    {
        "title": "Rate-limit и наблюдаемость API",
        "category": "Backend",
        "description_template": (
            "Per-tenant и per-IP rate-limit (token bucket в Redis), "
            "структурное логирование, request-id, OpenTelemetry-трейсы в "
            "Tempo/Honeycomb и базовый SLO-дашборд по топ-10 эндпоинтам."
        ),
    },
    {
        "title": "Публичный API v1 со SDK",
        "category": "Backend",
        "description_template": (
            "Спроектировать и выпустить публичный API: политика версионирования, "
            "авторизация (API-ключи + OAuth), rate-limits, спецификация "
            "OpenAPI 3, авто-генерация TypeScript- и Python-SDK и "
            "developer-документация (Mintlify / Redoc)."
        ),
    },
    # ---------------- Bots ----------------
    {
        "title": "MVP Telegram-бота",
        "category": "Bots",
        "description_template": (
            "Сделать Telegram-бота, который {делает X}. Включить /start, "
            "меню и 1–2 ключевых сценария. Хранение в Postgres. Деплой с "
            "перезапуском и базовыми админ-командами."
        ),
    },
    {
        "title": "Telegram Mini App (Web App)",
        "category": "Bots",
        "description_template": (
            "Сделать Telegram Mini App для {use case}: React + Telegram "
            "WebApp SDK, HMAC-валидация initData на бэке, тематический UI, "
            "проводка MainButton + BackButton, deep link из бота."
        ),
    },
    {
        "title": "Telegram-бот клиентской поддержки",
        "category": "Bots",
        "description_template": (
            "Бот принимает вопросы пользователей, классифицирует их, "
            "роутит в группу операторов с действиями claim/resolve и "
            "сохраняет переписки. SLA-таймеры, заготовки ответов, сбор "
            "CSAT в конце."
        ),
    },
    {
        "title": "Discord-бот для модерации и комьюнити",
        "category": "Bots",
        "description_template": (
            "Discord.js-бот: slash-команды, каналы под ролями, automod-правила, "
            "уровни / XP, плановые анонсы, тикет-система. Postgres для "
            "хранилища, Docker-деплой, базовая веб-админка."
        ),
    },
    {
        "title": "Интеграция WhatsApp Business API",
        "category": "Bots",
        "description_template": (
            "Подключить WhatsApp Cloud API (Meta) для общения с клиентами: "
            "opt-in, шаблонные сообщения, входящий вебхук, привязка диалогов "
            "к нашей CRM, поддержка медиа и quick-reply кнопок."
        ),
    },
    {
        "title": "Slack-приложение с workflow и slash-командами",
        "category": "Bots",
        "description_template": (
            "Slack-приложение со slash-командами, интерактивными модалями и "
            "подписками на события. Кейсы: согласование деплоев, обмен "
            "сменами on-call, сборщик еженедельных standup-ов. OAuth-установка "
            "и настройки per-workspace."
        ),
    },
    {
        "title": "Бот для сбора лидов с синком в CRM",
        "category": "Bots",
        "description_template": (
            "Telegram- или WhatsApp-бот квалифицирует лиды короткой анкетой "
            "и пушит их в HubSpot / Pipedrive / Notion. Тег по источнику, "
            "ретраи при сбоях API, еженедельный отчёт продажникам."
        ),
    },
    {
        "title": "Бот напоминаний и привычек",
        "category": "Bots",
        "description_template": (
            "Бот позволяет настраивать регулярные напоминания (ежедневный "
            "standup, вода, лекарства и т. п.), учитывает таймзоны, "
            "поддерживает действия snooze/complete, выдаёт недельную "
            "статистику. Хранилище + cron-шедулер."
        ),
    },
    {
        "title": "Бот статусов заказов для e-commerce",
        "category": "Bots",
        "description_template": (
            "Бот позволяет покупателям проверить статус заказа, получить "
            "обновления доставки и открыть возврат. Берёт данные из Shopify "
            "/ WooCommerce API, шлёт проактивный пуш по событиям "
            "shipped/delivered."
        ),
    },
    {
        "title": "FAQ-бот по базе знаний",
        "category": "Bots",
        "description_template": (
            "Бот отвечает на FAQ из подобранной базы знаний. Админка для "
            "правки Q&A, фолбэк на оператора, еженедельный отчёт о "
            "неотвеченных вопросах для улучшения базы."
        ),
    },
    {
        "title": "Платежи внутри бота (Telegram Payments / Stars)",
        "category": "Bots",
        "description_template": (
            "Добавить платные фичи в существующий Telegram-бот: товары, "
            "флоу инвойса, вебхук successful_payment, возвраты, чеки. "
            "Поддержать Telegram Payments (через Stripe) или Stars."
        ),
    },
    # ---------------- Mobile ----------------
    {
        "title": "MVP мобильного приложения (iOS+Android)",
        "category": "Mobile",
        "description_template": (
            "Кросс-платформенный мобильный MVP (React Native или Flutter). "
            "Авторизация, экран списка, детальный экран и 1 ключевое "
            "действие. Иконка приложения, splash и базовые экраны "
            "онбординга."
        ),
    },
    {
        "title": "Offline-first синхронизация для мобильного",
        "category": "Mobile",
        "description_template": (
            "Добавить offline-first поведение: локальная SQLite/WatermelonDB, "
            "оптимистичные записи, очередь синка при восстановлении связи, "
            "политика разрешения конфликтов. Применить к 2–3 самым "
            "используемым экранам."
        ),
    },
    {
        "title": "Push-уведомления (FCM + APNs)",
        "category": "Mobile",
        "description_template": (
            "End-to-end настройка пушей: сертификаты APNs, FCM, регистрация "
            "device-token, темы + персональные каналы, обработка deep-link, "
            "состояния foreground/background/quit. Тест-план прилагается."
        ),
    },
    {
        "title": "Подача в App Store и Play Store",
        "category": "Mobile",
        "description_template": (
            "Подготовить и подать существующий билд в оба стора: bundle-id, "
            "подпись, настройка App Store Connect / Play Console, скриншоты "
            "во всех нужных размерах, privacy-disclosures, ответы на "
            "ревью-фидбэк."
        ),
    },
    {
        "title": "iOS-виджет на главном экране",
        "category": "Mobile",
        "description_template": (
            "Нативный iOS-виджет (WidgetKit / Swift) для существующего "
            "RN/Flutter-приложения. Small + medium размеры, deep-link в "
            "приложение, обновление timeline каждые 15 минут, общий App "
            "Group для данных."
        ),
    },
    {
        "title": "In-app покупки и подписки",
        "category": "Mobile",
        "description_template": (
            "Добавить IAP через RevenueCat (или нативный StoreKit2 + "
            "Billing): 2 уровня подписки, бесплатный trial, восстановление "
            "покупок, валидация чека на сервере, синк прав доступа с "
            "бэкендом."
        ),
    },
    {
        "title": "Карты и геолокация",
        "category": "Mobile",
        "description_template": (
            "Экран с картой: маркеры, кластеризация, текущая локация, "
            "расстояние/ETA. Mapbox или Google Maps. Фоновое обновление "
            "локации с обоснованием разрешения и щадящими батарею "
            "настройками."
        ),
    },
    {
        "title": "Биометрическая авторизация и безопасное хранилище",
        "category": "Mobile",
        "description_template": (
            "Face ID / Touch ID / отпечаток для разблокировки приложения, "
            "фолбэк на PIN. Токены в Keychain / EncryptedSharedPreferences. "
            "Авто-блокировка после N минут в фоне."
        ),
    },
    {
        "title": "Запись аудио и видео в приложении",
        "category": "Mobile",
        "description_template": (
            "Запись аудио (опционально короткого видео) внутри приложения "
            "с волновой формой, паузой/возобновлением, тримом, загрузкой "
            "с прогрессом и резюмом. Корректная работа с разрешениями на "
            "iOS и Android."
        ),
    },
    {
        "title": "Апгрейд мажорной версии React Native / Flutter",
        "category": "Mobile",
        "description_template": (
            "Обновить RN (или Flutter) на 2+ мажорные версии. Обновить "
            "нативные зависимости, починить ломающие изменения, "
            "мигрировать deprecated API, прогнать smoke-тесты по всем "
            "экранам, выпустить билд в TestFlight + Play internal."
        ),
    },
    # ---------------- DevOps ----------------
    {
        "title": "DevOps: контейнеризация и деплой",
        "category": "DevOps",
        "description_template": (
            "Взять существующий репозиторий, контейнеризовать, настроить "
            "CI/CD и задеплоить в managed Kubernetes / Fly.io / Render. "
            "Включить health-чеки, секреты и one-click rollback."
        ),
    },
    {
        "title": "CI/CD пайплайн на GitHub Actions",
        "category": "DevOps",
        "description_template": (
            "Написать CI: lint, type-check, тесты (параллельно), сборка, "
            "публикация контейнера, деплой в staging на main и в prod по "
            "тегу. Кэширование, матричные сборки, обязательные проверки "
            "на PR."
        ),
    },
    {
        "title": "Миграция в Kubernetes",
        "category": "DevOps",
        "description_template": (
            "Перенести сервисы с VM / Docker Compose в managed Kubernetes "
            "(EKS / GKE / DOKS). Helm-чарты, ingress + TLS, HPA, секреты "
            "через External Secrets, план перехода без даунтайма."
        ),
    },
    {
        "title": "Terraform / IaC для облачной инфры",
        "category": "DevOps",
        "description_template": (
            "Описать нашу облачную инфру в Terraform: VPC, RDS, S3, IAM, "
            "ECR/ECS, DNS. Удалённый state, workspaces по окружениям, "
            "обнаружение drift, preview plan на PR через Atlantis или "
            "tfaction."
        ),
    },
    {
        "title": "Хранение секретов в Vault / SOPS",
        "category": "DevOps",
        "description_template": (
            "Вынести секреты из .env и CI-переменных в Vault (или SOPS + "
            "age). Ротация креденшелов, документация флоу для разработчиков, "
            "интеграция с деплоями."
        ),
    },
    {
        "title": "Стек наблюдаемости (Prom / Grafana / Loki)",
        "category": "DevOps",
        "description_template": (
            "Поднять метрики + логи + трейсы: Prometheus, дашборды Grafana "
            "(RED + USE), Loki для логов, Tempo или Jaeger для трейсов. "
            "Правила алертов по топ-5 сервисам, пейджинг через PagerDuty / "
            "Opsgenie."
        ),
    },
    {
        "title": "Аудит и оптимизация облачных расходов",
        "category": "DevOps",
        "description_template": (
            "Аудит счёта AWS / GCP. Топ-10 драйверов стоимости, предложения "
            "по rightsizing, savings plans / committed use, lifecycle S3, "
            "удаление простаивающих ресурсов. Письменный отчёт с "
            "посчитанной экономией."
        ),
    },
    {
        "title": "Blue/green или canary-деплои",
        "category": "DevOps",
        "description_template": (
            "Сделать деплой безопаснее: blue/green (через target-groups "
            "балансировщика) или canary (Argo Rollouts / Flagger). "
            "Автоматические health-чеки, авто-rollback при росте ошибок, "
            "runbook для ручного управления."
        ),
    },
    {
        "title": "On-call расписание и runbook-и",
        "category": "DevOps",
        "description_template": (
            "Завести on-call ротацию в PagerDuty / Opsgenie. Определить "
            "severity, эскалации, политики пейджинга. Написать runbook-и "
            "по топ-10 алертам. Шаблон постмортема + процесс blameless "
            "разбора."
        ),
    },
    {
        "title": "Disaster recovery и автобэкапы",
        "category": "DevOps",
        "description_template": (
            "Автоматизировать бэкапы (Postgres + объектное хранилище), "
            "зашифрованную offsite-копию, ежемесячно тестировать "
            "восстановление. Задокументировать RPO/RTO. Провести "
            "tabletop-учения по DR и зафиксировать выводы."
        ),
    },
    # ---------------- Data ----------------
    {
        "title": "Пайплайн данных (ETL)",
        "category": "Data",
        "description_template": (
            "Построить ETL-пайплайн, который тянет данные из {sources}, "
            "трансформирует и загружает в Postgres / BigQuery. Расписание "
            "по cron или Airflow. Ретраи, алерты на сбои и небольшой "
            "набор data-quality-тестов."
        ),
    },
    {
        "title": "dbt-модели и тесты для хранилища",
        "category": "Data",
        "description_template": (
            "Развернуть dbt поверх нашего хранилища (Snowflake / BigQuery "
            "/ Postgres). Слои staging + marts по 4–6 источникам, тесты "
            "на свежесть и схему, документация моделей с описаниями и "
            "exposures."
        ),
    },
    {
        "title": "Дашборды в Metabase / Superset",
        "category": "Data",
        "description_template": (
            "Поднять Metabase (или Superset), подключить к хранилищу, "
            "построить 5 управленческих дашбордов (выручка, воронка, "
            "удержание, поддержка, операционка) поверх согласованных "
            "метрик."
        ),
    },
    {
        "title": "Уборка и рефакторинг Airflow DAG-ов",
        "category": "Data",
        "description_template": (
            "Принять в наследство замусоренный Airflow. Разнести "
            "монолитные DAG-и, параметризовать через TaskFlow, добавить "
            "SLA и on-failure-колбэки, обновить до свежей стабильной "
            "версии Airflow, задокументировать каждый пайплайн."
        ),
    },
    {
        "title": "Мониторинг качества данных",
        "category": "Data",
        "description_template": (
            "Добавить проверки качества данных по критичным таблицам: "
            "свежесть, количество строк, доли null, уникальность, "
            "ссылочная целостность. Инструмент на выбор (Great "
            "Expectations, Soda, Elementary). Алерты в Slack."
        ),
    },
    {
        "title": "Пайплайн сегментации клиентов",
        "category": "Data",
        "description_template": (
            "Собрать пайплайн сегментации (активные / отвалившиеся / "
            "power-users и т. п.) из продуктовых событий, обновлять "
            "ежедневно, выложить как marts-таблицу и синкать в CRM и "
            "маркетинговый инструмент."
        ),
    },
    {
        "title": "Трекинг событий через Segment / RudderStack",
        "category": "Data",
        "description_template": (
            "Определить tracking plan, инструментировать web- и mobile-"
            "приложения через Segment или RudderStack, настроить "
            "приёмники (хранилище, GA4, маркетинг). Чек-лист QA и "
            "документация по трекингу."
        ),
    },
    {
        "title": "Reverse-ETL из хранилища в операционные инструменты",
        "category": "Data",
        "description_template": (
            "Синкать модели из хранилища (Customer 360, lead score, MRR) "
            "обратно в HubSpot / Salesforce / Intercom через Hightouch "
            "или Census. Определить расписание, обработку ошибок и "
            "источник правды по полям."
        ),
    },
    {
        "title": "ML feature store и пайплайн обучения",
        "category": "Data",
        "description_template": (
            "Поднять лёгкий feature store (Feast или внутри хранилища), "
            "построить end-to-end пайплайн обучения одной модели (данные → "
            "фичи → обучение → оценка → реестр) и задеплоить batch-"
            "скоринг."
        ),
    },
    {
        "title": "Синк Postgres → аналитическое хранилище",
        "category": "Data",
        "description_template": (
            "Реплицировать прод-Postgres в хранилище (BigQuery / Snowflake "
            "/ Redshift) через Fivetran / Airbyte / pg_logical. Бэкфилл, "
            "мониторинг лага, документация маппинга схемы."
        ),
    },
    # ---------------- Design ----------------
    {
        "title": "Редизайн UX/UI внутреннего инструмента",
        "category": "Design",
        "description_template": (
            "Провести аудит текущего UX, предложить редизайн, отдать "
            "макеты Figma по основным экранам и небольшую дизайн-систему. "
            "Хэндофф со спеками, состояниями и токенами, готовый к "
            "разработке."
        ),
    },
    {
        "title": "UX/UI мобильного приложения с нуля",
        "category": "Design",
        "description_template": (
            "Спроектировать мобильное приложение с нуля: пользовательские "
            "потоки, вайрфреймы, hi-fi UI в Figma для 10–15 экранов "
            "(iOS + Android, где они различаются), прототип и стартовая "
            "библиотека компонентов."
        ),
    },
    {
        "title": "Бутстрап дизайн-системы (Figma + токены)",
        "category": "Design",
        "description_template": (
            "Собрать дизайн-систему из текущего продукта: токены "
            "цвета/типографики/отступов, базовые компоненты (Button, "
            "Input, Card, Modal, Nav), документация в Figma и экспорт "
            "JSON-токенов для разработки."
        ),
    },
    {
        "title": "Редизайн лендинга под конверсию",
        "category": "Design",
        "description_template": (
            "Редизайн главного лендинга под конверсию в регистрацию. "
            "Включает короткий аудит (heatmap + аналитика), 2 hi-fi "
            "направления, доведённое выбранное направление и подробный "
            "хэндофф."
        ),
    },
    {
        "title": "Переработка информационной архитектуры дашборда",
        "category": "Design",
        "description_template": (
            "Переработать IA перегруженного дашборда: навигация, "
            "группировка, empty-states, плотность. На выходе вайрфреймы, "
            "провалидированные на 5 пользователях, затем hi-fi Figma и "
            "заметки по взаимодействиям."
        ),
    },
    {
        "title": "Дизайн онбординг-флоу",
        "category": "Design",
        "description_template": (
            "Спроектировать онбординг, ведущий пользователей к первой "
            "ценности быстро: welcome → шаги настройки → активация. "
            "Включить empty-states, тултипы/чек-листы и обоснование "
            "каждого шага."
        ),
    },
    {
        "title": "Сет иллюстраций и иконок",
        "category": "Design",
        "description_template": (
            "Авторский сет иллюстраций (~10 spot-иллюстраций) и пак из "
            "30 иконок под наш бренд. Сдача в Figma + SVG, светлый/"
            "тёмный варианты и конвенции наименования."
        ),
    },
    {
        "title": "Тёмная тема по существующему продукту",
        "category": "Design",
        "description_template": (
            "Провести аудит и сделать прогон под тёмную тему: цветовые "
            "токены, проверка контраста, обновлённые иллюстрации/иконки, "
            "крайние случаи (модалки, графики, hover) и хэндофф."
        ),
    },
    {
        "title": "Хэндофф Figma → дизайн-токены",
        "category": "Design",
        "description_template": (
            "Перестроить замусоренный Figma-файл со стилями и переменными, "
            "экспортировать дизайн-токены (Style Dictionary / Token "
            "Studio) и согласовать имена с настройкой Tailwind / CSS-vars "
            "на фронте."
        ),
    },
    {
        "title": "Дизайн-ревью по доступности (WCAG)",
        "category": "Design",
        "description_template": (
            "Проверить наши макеты по WCAG 2.1 AA с дизайнерской позиции: "
            "контраст, hit-area, состояния фокуса, motion, паттерны "
            "ошибок. На выходе приоритизированный список правок с "
            "примерами в Figma."
        ),
    },
    # ---------------- AI ----------------
    {
        "title": "Интеграция ИИ (LLM-фича)",
        "category": "AI",
        "description_template": (
            "Интегрировать LLM в существующий продукт для {feature}. "
            "Промпт-инжиниринг, оценка и базовые guardrails. Провайдер "
            "на выбор (Anthropic / OpenAI / open-weights)."
        ),
    },
    {
        "title": "RAG-ассистент по внутренней документации",
        "category": "AI",
        "description_template": (
            "Сделать retrieval-augmented ассистента по нашей документации "
            "/ wiki / тикетам поддержки. Ингест-пайплайн, чанкинг + "
            "эмбеддинги, гибридный поиск, ответы с цитатами, eval-сет на "
            "50 пар вопрос-ответ."
        ),
    },
    {
        "title": "Чат-бот клиентской поддержки с эскалацией",
        "category": "AI",
        "description_template": (
            "LLM-чат-бот первой линии поддержки: заземлён на нашем "
            "help-центре, умеет открывать/обновлять тикеты, эскалирует "
            "оператору с полным контекстом при низкой уверенности или по "
            "запросу пользователя."
        ),
    },
    {
        "title": "Голосовой агент для входящих звонков",
        "category": "AI",
        "description_template": (
            "Голосовой агент (Twilio / Vapi / LiveKit + LLM + TTS/STT), "
            "обрабатывающий типовые входящие звонки: запись на приём, "
            "проверка статуса, FAQ. Латентность < 1 с, сохранение "
            "транскрипта, эскалация на оператора."
        ),
    },
    {
        "title": "Fine-tune модели на доменных данных",
        "category": "AI",
        "description_template": (
            "Дообучить небольшую open-weights модель (Llama / Mistral / "
            "Qwen) на наших данных под {task}. Подготовка данных, "
            "обучение, оценка на отложенной выборке, сравнение с "
            "промпт-бейзлайном."
        ),
    },
    {
        "title": "Пайплайн генерации изображений",
        "category": "AI",
        "description_template": (
            "Пайплайн генерации изображений (SDXL / Flux / Imagen) под "
            "продуктовый кейс. Промпты + пресеты стилей, очередь для "
            "долгих запусков, хранение в S3, модерация и небольшая "
            "админка."
        ),
    },
    {
        "title": "AI-поиск / семантический поиск",
        "category": "AI",
        "description_template": (
            "Добавить семантический поиск по существующему каталогу. "
            "Эмбеддинги айтемов и запросов, vector-store (pgvector / "
            "Qdrant), реранкер, оценка на размеченном сете. Drop-in API "
            "для фронта."
        ),
    },
    {
        "title": "Eval-харнесс и guardrails для LLM-фичи",
        "category": "AI",
        "description_template": (
            "Сделать офлайн eval-харнесс для существующей LLM-фичи: "
            "golden-set, авто-оценивание по рубрикам, регрессия в CI, "
            "плюс рантайм-guardrails (PII-фильтр, защита от джейлбрейка, "
            "валидация вывода)."
        ),
    },
    {
        "title": "Оптимизация промптов и стоимости",
        "category": "AI",
        "description_template": (
            "Аудит наших LLM-вызовов: снизить расход токенов через "
            "кэширование, обрезку промптов, умный роутинг моделей "
            "(маленькая первой, эскалация при неуверенности). Цель — "
            "сокращение ≥ 40% без потери качества."
        ),
    },
    {
        "title": "Мультимодальный парсер документов",
        "category": "AI",
        "description_template": (
            "Парсить грязные PDF / сканы / изображения (инвойсы, "
            "контракты, чеки) в структурированный JSON с помощью vision-"
            "LLM + OCR-фолбэк. Оценка на размеченных образцах, scoring "
            "по уверенности, очередь на ручной разбор."
        ),
    },
    {
        "title": "AI-агент для внутренних воркфлоу",
        "category": "AI",
        "description_template": (
            "Сделать агента, который автоматизирует многошаговый "
            "внутренний воркфлоу (например, триаж лидов, "
            "категоризацию тикетов, еженедельную отчётность). Tool-use, "
            "guardrails, наблюдаемость и понятный human-in-the-loop "
            "чекпоинт."
        ),
    },
]
