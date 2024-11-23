import requests
import json
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from telegram import Bot

# Конфигурация AmoCRM
AMOCRM_CLIENT_ID = "ваш_client_id"
AMOCRM_CLIENT_SECRET = "ваш_client_secret"
AMOCRM_REDIRECT_URL = "ваш_redirect_url"
AMOCRM_ACCESS_TOKEN = "ваш_access_token"
AMOCRM_REFRESH_TOKEN = "ваш_refresh_token"
AMOCRM_BASE_URL = "https://your-subdomain.amocrm.ru"

# Конфигурация Telegram
TELEGRAM_BOT_TOKEN = "ваш_telegram_bot_token"
TELEGRAM_CHAT_ID = "id_вашего_телеграм_чата"

# Telegram Bot
bot = Bot(token=TELEGRAM_BOT_TOKEN)


def refresh_amocrm_token():
    """Обновляет токен доступа AmoCRM."""
    url = f"{AMOCRM_BASE_URL}/oauth2/access_token"
    data = {
        "client_id": AMOCRM_CLIENT_ID,
        "client_secret": AMOCRM_CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": AMOCRM_REFRESH_TOKEN,
        "redirect_uri": AMOCRM_REDIRECT_URL
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        tokens = response.json()
        global AMOCRM_ACCESS_TOKEN, AMOCRM_REFRESH_TOKEN
        AMOCRM_ACCESS_TOKEN = tokens["access_token"]
        AMOCRM_REFRESH_TOKEN = tokens["refresh_token"]
    else:
        print(f"Ошибка обновления токена: {response.status_code} - {response.text}")


def get_revenue_by_manager():
    """Получает данные о выручке менеджеров из AmoCRM."""
    url = f"{AMOCRM_BASE_URL}/api/v4/leads"
    headers = {"Authorization": f"Bearer {AMOCRM_ACCESS_TOKEN}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 401:  # Если токен устарел
        refresh_amocrm_token()
        response = requests.get(url, headers={"Authorization": f"Bearer {AMOCRM_ACCESS_TOKEN}"})

    if response.status_code == 200:
        leads = response.json()["_embedded"]["leads"]
        revenue_by_manager = {}

        for lead in leads:
            manager_id = lead["responsible_user_id"]
            revenue = lead.get("price", 0)
            revenue_by_manager[manager_id] = revenue_by_manager.get(manager_id, 0) + revenue

        return revenue_by_manager
    else:
        print(f"Ошибка получения данных: {response.status_code} - {response.text}")
        return {}


def send_daily_report():
    """Отправляет ежедневный отчет в Telegram."""
    revenue_by_manager = get_revenue_by_manager()
    if not revenue_by_manager:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="Ошибка получения данных о выручке.")
        return

    report = "Ежедневный отчет по выручке менеджеров:\n"
    for manager_id, revenue in revenue_by_manager.items():
        report += f"Менеджер ID {manager_id}: {revenue} руб.\n"

    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=report)


# Планировщик
scheduler = BlockingScheduler()
scheduler.add_job(send_daily_report, 'cron', hour=9)  # Отправка отчета в 9 утра

if __name__ == "__main__":
    send_daily_report()  # Для теста можно запустить сразу
    scheduler.start()
