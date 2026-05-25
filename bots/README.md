# Bots — aiogram 3

Three independent processes, all importing from the backend's `app` package
for models and services.

```
bots/
├── common/          shared helpers (db, auth lookup, notifications loop)
├── doers_bot/       DoingsForDoersBot (specialist) — Mini App + notifications
├── customers_bot/   DoingsForCustomersBot (customer) — Mini App + notifications
└── referee_bot/     RefereeBot — full anonymous chat relay + select-specialist
```

## Bot responsibilities

| Bot              | Inline buttons                        | Notifications listened to                                  |
| ---------------- | ------------------------------------- | ---------------------------------------------------------- |
| **DoersBot**     | Open Mini App (?role=specialist)      | application_accepted/rejected, project_completed, direct_offer_received, new_review |
| **CustomersBot** | Open Mini App (?role=customer)        | new_application, specialist_selected, direct_offer_answered, new_review |
| **RefereeBot**   | Pick project → see applicants → chat → select | (none — fully interactive)                         |

## Notification fan-out

Backend `app/services/notifications.py` writes a `notifications` row and
`PUBLISH notify:{user_id} {...}` on Redis. Each bot process runs
`bots/common/notifications.run_notification_loop()` which `PSUBSCRIBE
notify:*` and forwards the message to its audience (filtered by role via
`chat_id_for_user_id(..., role=…)`).

## RefereeBot anonymous flow

1. `/start` links the Telegram account → `chat_id` is stored.
2. **Customer** picks an open project → sees applicants as
   "Specialist #1 / #2 / …" (no PII).
3. Tapping **💬 Chat #N** opens (or reuses) a `chat_threads` row scoped to
   `(project_id, customer_id, specialist_id)` and enters an FSM state.
4. Each non-command text typed by either side is persisted to `messages`
   and forwarded to the counterparty's `chat_id`, prefixed only with
   `Customer:` or `Specialist:` — names are never relayed.
5. **✅ Select #N** calls `app.services.projects.select_specialist(...)`
   which marks the project `in_progress`, rejects other applications, and
   auto-closes the other chat threads (`closed=true`).

The bot never duplicates business rules — selection, chat persistence, and
all validations go through the backend `services` package.
