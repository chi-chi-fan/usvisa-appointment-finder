#  🇨🇦 2025 US Visa Appointment Finder (Canada Edition) 😎

This script checks for available **US visa appointment slots** on [ais.usvisa-info.com](https://ais.usvisa-info.com) and notifies you via Telegram if any slots meet your criteria.

---

## 🚀 Features

- Parses appointment availability for **all Canadian consular cities**
- Sends instant alerts via **Telegram**
- Supports **multiple locations** (e.g., Vancouver, Calgary, Montreal, etc.)
- Configurable polling interval and date filter

---

## Installation

The recommended way to install ```
usvisa-appointment-finder```
 uses pip and add configuration to get started:

```bash
pip install -r requirements.txt
```

After creating telegram bot via `@botfather` and creating group, just add your bot to this group. To find `telegram_chat_id` parameter just add `@getidsbot` to your group.

## Configuration

Rename default config file `app-config-sample.properties` to `app-config.properties`

Here's a quick example:

```properties
username=name@email.com
password=qwerty
url_id=12345678
country_code=ca
facility_name=Vancouver
latest_notification_date=2026-05-01
seconds_between_checks=180
telegram_bot_token=12345:some_token
telegram_chat_id=12345
```

`url_id` needs to be grabbed from the url when you navigate to Reschedule Appointment page.

Example: <https://ais.usvisa-info.com/en-ca/niv/schedule/>**12345678**/appointment

## License

[MIT](./LICENSE)