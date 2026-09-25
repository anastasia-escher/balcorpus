# Перенос бэкенда на PHP (спецификация — php/ЗАГРУЗКА.md)

Всё PHP-шное лежит в `php/`: `php/httpdocs/`, `php/private/`, стенд.

- [x] Шаг 1. Локальная проверка: сервисы `php` (8.1) и `mariadb` (11.4) в `docker-compose.dev.yml`, независимые от остальных; доступ к `data/php_ready/`
- [ ] Шаг 2. `private/sql/schema.sql`: таблицы по `models.py`, уникальные ключи, индексы; сравнение `utf8mb4_uca1400_as_ci`
- [ ] Шаг 3. Загрузчик CSV (`private/upload/` + `httpdocs/upload/index.php`); поправить фразу про `--metadata` в ЗАГРУЗКА.md
- [ ] Шаг 4. Эндпоинты (лимиты: где хранить счётчики — решить до начала)
  - [ ] 4a. `texts` и `texts/coverage`
  - [ ] 4b. `tokens/search` (near_*, parent, пагинация)
  - [ ] 4c. `sentences/context`
  - [ ] 4d. `tokens/search/xlsx`
- [ ] Шаг 5. Сверка Django ↔ PHP скриптом на одинаковом наборе запросов
- [ ] Шаг 6. Аудит безопасности загрузчика и SQL

Отложено: сравнение на сервере — если MariaDB старше 10.10, то `utf8mb4_bin` + `LOWER()` + `(?i)` (ждём версию).
