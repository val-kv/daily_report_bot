### Объяснение кода:
1. **Аутентификация AmoCRM**:
   - Используется OAuth2 для получения и обновления токенов.
   
2. **Получение данных о выручке**:
   - API `leads` возвращает список сделок, которые агрегируются по ответственным менеджерам.

3. **Telegram Bot**:
   - Используется для отправки текстового сообщения с отчетом.

4. **Планировщик**:
   - Планирует ежедневный запуск функции `send_daily_report` в заданное время.

### Запуск
Сохраните код в файл, например, `daily_report.py`, и выполните:
```bash
python daily_report.py
```
