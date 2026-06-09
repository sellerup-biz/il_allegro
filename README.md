# il_allegro — авторизация Allegro (автоматическая)

Страница идентификации и автоматическое получение/хранение **refresh token** для
магазина **IL_read** через Allegro OAuth. Никакого ручного копирования кодов.

## Как это работает

```
auth.html ──> вход в Allegro ──> callback.html ──┐
   (ввод GH PAT,                  (ловит ?code)   │ workflow_dispatch
    выбор магазина)                               ▼
                                   GitHub Actions: auth.yml
                                   └─ auth_exchange.py
                                        ├─ code → access + refresh token  (client_secret в Secrets)
                                        └─ refresh_token → GitHub Secrets (REFRESH_TOKEN_IL, зашифрован)
```

Client secret **никогда** не попадает в браузер — обмен кода идёт на сервере (в Actions).
На странице вводится только GitHub PAT (для запуска workflow), он не сохраняется.

## Использование

1. Открой **https://sellerup-biz.github.io/il_allegro/** (→ `auth.html`).
2. Вставь GitHub Personal Access Token (репозиторий `il_allegro`, Actions: read/write).
3. Войди в браузере в нужный аккаунт Allegro, нажми **«Авторизовать IL_read»**, подтверди доступ.
4. На `callback.html` дождись «✅ Refresh token сохранён». Готово.

Проверить связь: вкладка **Actions → «Allegro API — тест связи» → Run workflow**
(вызывает `GET /me` и обновляет токен).

## Redirect URI (в настройках приложения IL_read на apps.developer.allegro.pl)

```
https://sellerup-biz.github.io/il_allegro/callback.html
```

## GitHub Secrets (репозиторий → Settings → Secrets → Actions)

| Secret | Что это |
|--------|---------|
| `CLIENT_ID_IL` | Client ID приложения IL_read |
| `CLIENT_SECRET_IL` | Client Secret приложения IL_read |
| `GH_TOKEN` | PAT для сохранения/ротации секретов (Actions + Secrets: RW) |
| `REFRESH_TOKEN_IL` | refresh token — пишется автоматически |

## Файлы

| Файл | Назначение |
|------|-----------|
| `auth.html` | Стартовая страница (PAT + кнопка авторизации) |
| `callback.html` | Redirect URI: ловит `code`, запускает workflow |
| `auth_exchange.py` | Обмен `code` → refresh token, сохранение в Secrets |
| `api_test.py` | Тест: refresh → `GET /me` → сохранение нового refresh token |
| `gh_secret.py` | Шифрование и запись секрета через GitHub API |
| `.github/workflows/auth.yml` | Workflow обмена кода |
| `.github/workflows/test.yml` | Workflow проверки связи |
