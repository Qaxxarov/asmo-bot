"""Bilingual UI strings — O'zbekcha / Русский."""

from .config import (
    TELEGRAM_USERNAME, INSTAGRAM_USERNAME,
    PHONE_NUMBER, PAYMENT_CARD, PAYMENT_CARD_OWNER,
)

_C = {  # contact shortcuts
    "tg":    TELEGRAM_USERNAME,
    "ig":    INSTAGRAM_USERNAME,
    "phone": PHONE_NUMBER,
    "card":  PAYMENT_CARD,
    "owner": PAYMENT_CARD_OWNER,
}

TEXTS = {
    "uz": {
        # ── Language ──────────────────────────────────────────────────────
        "choose_language": "🌐 Tilni tanlang:",
        "language_set":    "✅ O'zbekcha tili tanlandi",

        # ── Welcome ───────────────────────────────────────────────────────
        "welcome": (
            "👋 Salom, <b>{name}</b>!\n\n"
            "🎬 <b>Qaxxarov Portfolio — AI Video & Foto Creator</b>ga xush kelibsiz!\n\n"
            "Zamonaviy AI texnologiyalari bilan professional kontent yarataman:\n"
            "  🤖 AI Avatar videolar\n"
            "  📺 Reklama videolari\n"
            "  🎬 Intro & Outro\n"
            "  📸 Foto tayyorlash & tahrirlash\n"
            "  🎨 Dizayn & Motion Graphics\n\n"
            "5+ yillik tajriba | 90+ mijoz | 98% mamnunlik\n\n"
            "Quyi menyudan kerakli bo'limni tanlang 👇"
        ),

        # ── Main menu ─────────────────────────────────────────────────────
        "menu_services":    "🧠 Xizmatlar",
        "menu_order":       "🛒 Buyurtma",
        "menu_about":       "ℹ️ Men haqimda",
        "menu_contact":     "📞 Aloqa",
        "menu_portfolio":   "🖼 Portfolio",
        "menu_change_lang": "🌐 Til",

        # ── Services ──────────────────────────────────────────────────────
        "services_title": "🧠 <b>Xizmatlar</b>\n\nBirini tanlang:",
        "services_empty": "⏳ Xizmatlar hali qo'shilmagan.",
        "service_card": (
            "<b>{name}</b>\n\n"
            "📋 {description}\n\n"
            "💰 Narxi: <b>{price}</b>"
        ),

        # ── Buttons ───────────────────────────────────────────────────────
        "btn_order_this":  "🛒 Buyurtma berish",
        "btn_back":        "⬅️ Orqaga",
        "btn_cancel":      "❌ Bekor qilish",
        "btn_order_now":   "🛒 Buyurtma berish",
        "btn_call_admin":  "📞 Admin bilan bog'lanish",
        "btn_approve":     "✅ Tasdiqlash",
        "btn_reject":      "❌ Rad etish",
        "btn_reply":       "✍️ Javob",
        "btn_open_chat":   "💬 Chatni ochish",
        "btn_resolve":     "✅ Hal qilindi",
        "btn_resolve_all": "✅ Barchasini yopish",
        "btn_paid":        "💳 To'ladim",
        "btn_pay_later":   "⏭ Keyinroq",

        # ── About ─────────────────────────────────────────────────────────
        "about": (
            "🚀 <b>Tursunmurod Qaxxarov — AI Kontent Yaratuvchi</b>\n\n"
            "5+ yillik tajribaga ega grafik dizayner va AI kontent yaratuvchiman.\n"
            "Brendlarni kuchli vizual kontent orqali ajratib ko'rsatish — asosiy maqsadim.\n\n"
            "<b>Nima qilaman:</b>\n"
            "  🤖 AI Avatar videolar\n"
            "  📺 Reklama videolari (30-60 sek)\n"
            "  🎬 Intro & Outro\n"
            "  📸 Foto tayyorlash (background, sifat)\n"
            "  ✂ Video tahrirlash (montaj, color grading)\n"
            "  🎨 Dizayn & Motion Graphics\n\n"
            "<b>Texnologiyalar:</b>\n"
            "Photoshop, Illustrator, CapCut, Midjourney,\n"
            "Nano Banana, Veo, Kling, Runway\n\n"
            f"📞 {_C['phone']}\n"
            f"💬 Telegram: {_C['tg']}\n"
            f"📸 Instagram: {_C['ig']}"
        ),

        # ── Portfolio ─────────────────────────────────────────────────────
        "portfolio": (
            "🖼 <b>Portfolio — Ishlarimni ko'ring</b>\n\n"
            "Professional kontent namunalari:\n"
            "  🤖 AI Avatar videolar\n"
            "  📺 Reklama videolari\n"
            "  🎬 Intro & Outro\n"
            "  📸 Foto ishlar\n"
            "  ✂ Video tahrirlash\n"
            "  🎨 Dizayn & Motion\n\n"
            "🌐 <b>To'liq portfolio:</b>\n"
            "https://qaxxarov-portfolio.vercel.app\n\n"
            "5+ yillik tajriba | 90+ mijoz | 98% mamnunlik\n\n"
            "Brendingiz uchun ham shunday natijani xohlaysizmi? 👇"
        ),

        # ── Contact ───────────────────────────────────────────────────────
        "contact": (
            "📞 <b>Biz bilan bog'laning</b>\n\n"
            f"📱 {_C['phone']}\n"
            f"💬 {_C['tg']}\n"
            f"📸 {_C['ig']}\n\n"
            "Yozing, tez javob beramiz! 🙂"
        ),

        # ── Order flow ────────────────────────────────────────────────────
        "order_intro": (
            "📝 <b>Buyurtma berish</b>\n\n"
            "Avval <b>ismingizni</b> yozing:"
        ),
        "order_ask_contact": (
            "Rahmat, <b>{name}</b> ✅\n\n"
            "<b>Telefon</b> yoki <b>Telegram username</b>ingizni yuboring:"
        ),
        "order_ask_details": (
            "Zo'r! Endi <b>buyurtma tafsilotlarini</b> yozing:\n"
            "— Nima kerak?\n"
            "— Qanday uslubda?\n"
            "— Boshqa istaklaringiz:"
        ),
        "order_no_service": "❗ Avval xizmatlardan birini tanlang.",
        "order_saved": (
            "✅ <b>Buyurtma qabul qilindi!</b>\n\n"
            "📦 Raqam: <b>#{order_id}</b>\n\n"
            "Endi to'lovni amalga oshiring 👇"
        ),
        "cancel": "❌ Bekor qilindi.",

        # ── Payment ───────────────────────────────────────────────────────
        "payment_info": (
            "💳 <b>To'lov ma'lumotlari</b>\n\n"
            "Xizmat narxi: <b>{price}</b>\n\n"
            "Quyidagi kartaga o'tkazing:\n"
            f"<code>{_C['card']}</code>\n"
            f"<b>{_C['owner']}</b>\n\n"
            "✅ O'tkazmadan so'ng <b>chek rasmini</b> yuboring."
        ),
        "payment_receipt_ask":      "📸 To'lov chekini <b>rasm</b> sifatida yuboring:",
        "payment_receipt_received": (
            "✅ Chek qabul qilindi!\n\n"
            "Admin tekshirib, <b>15–30 daqiqa</b> ichida tasdiqlaydi. 🙏"
        ),
        "payment_confirmed": (
            "🎉 <b>To'lov tasdiqlandi!</b>\n\n"
            "Buyurtmangiz ishga tushdi. Admin tez orada bog'lanadi. 🚀"
        ),
        "payment_rejected": (
            "❌ <b>To'lov rad etildi.</b>\n\n"
            f"Muammo bo'lsa: {_C['tg']}"
        ),

        # ── Admin notifs ──────────────────────────────────────────────────
        "admin_new_order": (
            "🆕 <b>Yangi buyurtma #{order_id}!</b>\n\n"
            "👤 {name}\n"
            "📞 {contact}\n"
            "🧠 <b>{service}</b> — {price}\n"
            "📝 {details}\n"
            "🆔 <code>{user_id}</code>"
        ),
        "admin_new_payment": (
            "💳 <b>To'lov cheki!</b>\n\n"
            "📦 Buyurtma #{order_id}\n"
            "👤 {name} — <code>{user_id}</code>\n"
            "💰 <b>{amount}</b>\n\n"
            "Chekni tekshiring 👆"
        ),
        "admin_new_call": (
            "📞 <b>Mijoz bog'lanmoqchi!</b>\n\n"
            "👤 {name}\n"
            "🆔 <code>{user_id}</code>  @{username}\n"
            "📞 {phone}\n\n"
            "💬 <b>So'nggi xabar:</b>\n<i>{last_msg}</i>"
        ),
        "admin_call_sent": (
            "✅ So'rovingiz yuborildi!\n\n"
            f"Admin tez orada yozadi.\n"
            f"O'zingiz ham yozsangiz bo'ladi: {_C['tg']} 💬"
        ),

        # ── Admin panel ───────────────────────────────────────────────────
        "admin_only":           "⛔ Bu buyruq faqat admin uchun.",
        "admin_panel":          "🛠 <b>Admin panel</b>\n\nAmalni tanlang:",
        "admin_stats":          "📊 Statistika",
        "admin_broadcast":      "📢 Xabar yuborish",
        "admin_services":       "🧠 Xizmatlar",
        "admin_orders":         "📦 Buyurtmalar",
        "admin_clients":        "👥 Mijozlar",
        "admin_payments":       "💳 To'lovlar",
        "admin_stats_text": (
            "📊 <b>Statistika</b>\n\n"
            "👥 Foydalanuvchilar: <b>{users}</b>\n"
            "📦 Buyurtmalar: <b>{orders}</b>\n"
            "🧠 Faol xizmatlar: <b>{services}</b>\n"
            "✅ Tasdiqlangan to'lovlar: <b>{payments_ok}</b>\n"
            "⏳ Tekshirilayotgan: <b>{payments_pending}</b>"
        ),
        "admin_broadcast_ask":  "📢 Barcha foydalanuvchilarga yuboriladigan xabarni yozing:",
        "admin_broadcast_done": "✅ Yuborildi: {ok} | ❌ Xato: {fail}",
        "admin_services_list":  "🧠 <b>Faol xizmatlar:</b>",
        "admin_no_services":    "Xizmatlar yo'q.",
        "admin_add_service":    "➕ Qo'shish",
        "admin_del_service":    "🗑 O'chirish",
        "admin_add_name":       "Yangi xizmat <b>nomini</b> yozing:",
        "admin_add_desc":       "Xizmat <b>tavsifini</b> yozing:",
        "admin_add_price":      "Xizmat <b>narxini</b> yozing (masalan: 200 000 so'm):",
        "admin_add_done":       "✅ Xizmat qo'shildi! ID: #{sid}",
        "admin_del_ask":        "O'chiriladigan xizmat <b>ID</b>sini yozing:",
        "admin_del_done":       "✅ Xizmat o'chirildi.",
        "admin_del_notfound":   "❌ Bunday ID topilmadi.",
        "admin_orders_empty":   "📭 Buyurtmalar yo'q.",
        "admin_order_card": (
            "📦 <b>Buyurtma #{id}</b>\n"
            "👤 {name} | 📞 {contact}\n"
            "🧠 {service}\n📝 {details}\n"
            "📅 {created}\nHolati: <b>{status}</b>"
        ),
        "admin_clients_empty":  "👥 Hozircha mijozlar yo'q.",
        "admin_clients_title":  "👥 <b>Mijozlar</b>  (🔴 — yangi murojaat)",
        "admin_client_card": (
            "👤 <b>{name}</b>\n"
            "🆔 <code>{user_id}</code> | @{username}\n"
            "📞 {phone} | 🕒 {created}\n\n"
            "📦 Buyurtmalar ({orders_n}):\n{orders}\n\n"
            "📞 Murojaatlar ({reqs_n}):\n{reqs}"
        ),
        "admin_no_orders":      "— yo'q —",
        "admin_no_reqs":        "— yo'q —",
        "admin_reply_ask":      "Mijozga yubormoqchi bo'lgan xabarni yozing:",
        "admin_reply_sent":     "✅ Mijozga yuborildi.",
        "admin_reply_failed":   "❌ Yuborib bo'lmadi: {err}",
        "admin_resolved":       "✅ Hal qilindi.",

        # ── User notifications ────────────────────────────────────────────
        "user_order_approved": (
            "✅ <b>Buyurtmangiz tasdiqlandi!</b>\n"
            "Admin tez orada bog'lanadi. 🚀"
        ),
        "user_order_rejected": (
            f"❌ Buyurtmangiz rad etildi.\n"
            f"Savol bo'lsa: {_C['tg']}"
        ),
        "user_admin_reply": "💬 <b>Admin javobi:</b>\n\n{text}",
        "unknown": "Iltimos, menyudagi tugmalardan foydalaning 👇",

        # ── Status labels ─────────────────────────────────────────────────
        "order_status_new":      "🆕 yangi",
        "order_status_approved": "✅ tasdiqlangan",
        "order_status_rejected": "❌ rad etilgan",
        "request_status_open":   "🔴 ochiq",
        "request_status_resolved":"✅ hal qilindi",
        "request_type_admin_call":"📞 Admin chaqiruv",
        "request_type_order":    "🛒 Buyurtma",
    },

    "ru": {
        # ── Language ──────────────────────────────────────────────────────
        "choose_language": "🌐 Выберите язык:",
        "language_set":    "✅ Выбран русский язык",

        # ── Welcome ───────────────────────────────────────────────────────
        "welcome": (
            "👋 Привет, <b>{name}</b>!\n\n"
            "🎬 Добро пожаловать в <b>Qaxxarov Portfolio — AI Video & Foto Creator</b>!\n\n"
            "Создаю профессиональный контент с AI:\n"
            "  🤖 AI аватар-видео\n"
            "  📺 Рекламные ролики\n"
            "  🎬 Intro & Outro\n"
            "  📸 Фото-обработка\n"
            "  🎨 Дизайн & Motion Graphics\n\n"
            "5+ лет опыта | 90+ клиентов | 98% довольных\n\n"
            "Выберите раздел ниже 👇"
        ),

        # ── Main menu ─────────────────────────────────────────────────────
        "menu_services":    "🧠 Услуги",
        "menu_order":       "🛒 Заказать",
        "menu_about":       "ℹ️ Обо мне",
        "menu_contact":     "📞 Контакты",
        "menu_portfolio":   "🖼 Портфолио",
        "menu_change_lang": "🌐 Язык",

        # ── Services ──────────────────────────────────────────────────────
        "services_title": "🧠 <b>Услуги</b>\n\nВыберите одну:",
        "services_empty": "⏳ Услуги пока не добавлены.",
        "service_card": (
            "<b>{name}</b>\n\n"
            "📋 {description}\n\n"
            "💰 Цена: <b>{price}</b>"
        ),

        # ── Buttons ───────────────────────────────────────────────────────
        "btn_order_this":  "🛒 Заказать",
        "btn_back":        "⬅️ Назад",
        "btn_cancel":      "❌ Отмена",
        "btn_order_now":   "🛒 Заказать",
        "btn_call_admin":  "📞 Связаться с админом",
        "btn_approve":     "✅ Подтвердить",
        "btn_reject":      "❌ Отклонить",
        "btn_reply":       "✍️ Ответить",
        "btn_open_chat":   "💬 Открыть чат",
        "btn_resolve":     "✅ Решено",
        "btn_resolve_all": "✅ Закрыть все",
        "btn_paid":        "💳 Оплатил",
        "btn_pay_later":   "⏭ Позже",

        # ── About ─────────────────────────────────────────────────────────
        "about": (
            "🚀 <b>Tursunmurod Qaxxarov — AI контент-мейкер</b>\n\n"
            "Графический дизайнер с 5+ лет опыта.\n"
            "Создаю мощный визуальный контент для брендов.\n\n"
            "<b>Услуги:</b>\n"
            "  🤖 AI аватар-видео\n"
            "  📺 Рекламные ролики (30-60 сек)\n"
            "  🎬 Intro & Outro\n"
            "  📸 Фото-обработка\n"
            "  ✂ Видеомонтаж, color grading\n"
            "  🎨 Дизайн & Motion Graphics\n\n"
            "<b>Инструменты:</b>\n"
            "Photoshop, Illustrator, CapCut, Midjourney,\n"
            "Nano Banana, Veo, Kling, Runway\n\n"
            f"📞 {_C['phone']}\n"
            f"💬 Telegram: {_C['tg']}\n"
            f"📸 Instagram: {_C['ig']}"
        ),

        # ── Portfolio ─────────────────────────────────────────────────────
        "portfolio": (
            "🖼 <b>Портфолио — мои работы</b>\n\n"
            "Примеры профессионального контента:\n"
            "  🤖 AI аватар-видео\n"
            "  📺 Рекламные ролики\n"
            "  🎬 Intro & Outro\n"
            "  📸 Фото-работы\n"
            "  ✂ Видеомонтаж\n"
            "  🎨 Дизайн & Motion\n\n"
            "🌐 <b>Полное портфолио:</b>\n"
            "https://qaxxarov-portfolio.vercel.app\n\n"
            "5+ лет | 90+ клиентов | 98% довольных\n\n"
            "Хотите такой же результат для своего бренда? 👇"
        ),

        # ── Contact ───────────────────────────────────────────────────────
        "contact": (
            "📞 <b>Свяжитесь с нами</b>\n\n"
            f"📱 {_C['phone']}\n"
            f"💬 {_C['tg']}\n"
            f"📸 {_C['ig']}\n\n"
            "Пишите — ответим быстро! 🙂"
        ),

        # ── Order flow ────────────────────────────────────────────────────
        "order_intro": (
            "📝 <b>Оформление заказа</b>\n\n"
            "Напишите <b>ваше имя</b>:"
        ),
        "order_ask_contact": (
            "Спасибо, <b>{name}</b> ✅\n\n"
            "Отправьте <b>номер телефона</b> или <b>Telegram username</b>:"
        ),
        "order_ask_details": (
            "Отлично! Опишите <b>детали заказа</b>:\n"
            "— Что нужно создать?\n"
            "— В каком стиле?\n"
            "— Дополнительные пожелания:"
        ),
        "order_no_service": "❗ Сначала выберите услугу.",
        "order_saved": (
            "✅ <b>Заказ принят!</b>\n\n"
            "📦 Номер: <b>#{order_id}</b>\n\n"
            "Теперь оплатите заказ 👇"
        ),
        "cancel": "❌ Отменено.",

        # ── Payment ───────────────────────────────────────────────────────
        "payment_info": (
            "💳 <b>Данные для оплаты</b>\n\n"
            "Стоимость: <b>{price}</b>\n\n"
            "Переведите на карту:\n"
            f"<code>{_C['card']}</code>\n"
            f"<b>{_C['owner']}</b>\n\n"
            "✅ После перевода отправьте <b>скриншот чека</b>."
        ),
        "payment_receipt_ask":      "📸 Отправьте скриншот оплаты как <b>изображение</b>:",
        "payment_receipt_received": (
            "✅ Чек получен!\n\n"
            "Администратор проверит в течение <b>15–30 минут</b>. 🙏"
        ),
        "payment_confirmed": (
            "🎉 <b>Оплата подтверждена!</b>\n\n"
            "Заказ принят в работу. Скоро свяжемся. 🚀"
        ),
        "payment_rejected": (
            "❌ <b>Оплата отклонена.</b>\n\n"
            f"По вопросам: {_C['tg']}"
        ),

        # ── Admin notifs ──────────────────────────────────────────────────
        "admin_new_order": (
            "🆕 <b>Новый заказ #{order_id}!</b>\n\n"
            "👤 {name}\n"
            "📞 {contact}\n"
            "🧠 <b>{service}</b> — {price}\n"
            "📝 {details}\n"
            "🆔 <code>{user_id}</code>"
        ),
        "admin_new_payment": (
            "💳 <b>Чек об оплате!</b>\n\n"
            "📦 Заказ #{order_id}\n"
            "👤 {name} — <code>{user_id}</code>\n"
            "💰 <b>{amount}</b>\n\n"
            "Проверьте чек выше 👆"
        ),
        "admin_new_call": (
            "📞 <b>Клиент хочет связаться!</b>\n\n"
            "👤 {name}\n"
            "🆔 <code>{user_id}</code>  @{username}\n"
            "📞 {phone}\n\n"
            "💬 <b>Последнее сообщение:</b>\n<i>{last_msg}</i>"
        ),
        "admin_call_sent": (
            "✅ Запрос отправлен!\n\n"
            f"Администратор скоро напишет.\n"
            f"Или сами: {_C['tg']} 💬"
        ),

        # ── Admin panel ───────────────────────────────────────────────────
        "admin_only":           "⛔ Команда только для администратора.",
        "admin_panel":          "🛠 <b>Панель администратора</b>\n\nВыберите действие:",
        "admin_stats":          "📊 Статистика",
        "admin_broadcast":      "📢 Рассылка",
        "admin_services":       "🧠 Услуги",
        "admin_orders":         "📦 Заказы",
        "admin_clients":        "👥 Клиенты",
        "admin_payments":       "💳 Оплаты",
        "admin_stats_text": (
            "📊 <b>Статистика</b>\n\n"
            "👥 Пользователи: <b>{users}</b>\n"
            "📦 Заказы: <b>{orders}</b>\n"
            "🧠 Услуги: <b>{services}</b>\n"
            "✅ Подтверждённые оплаты: <b>{payments_ok}</b>\n"
            "⏳ На проверке: <b>{payments_pending}</b>"
        ),
        "admin_broadcast_ask":  "📢 Напишите сообщение для рассылки всем:",
        "admin_broadcast_done": "✅ Отправлено: {ok} | ❌ Ошибок: {fail}",
        "admin_services_list":  "🧠 <b>Активные услуги:</b>",
        "admin_no_services":    "Услуг нет.",
        "admin_add_service":    "➕ Добавить",
        "admin_del_service":    "🗑 Удалить",
        "admin_add_name":       "Напишите <b>название</b> услуги:",
        "admin_add_desc":       "Напишите <b>описание</b> услуги:",
        "admin_add_price":      "Напишите <b>цену</b> (например: 200 000 сум):",
        "admin_add_done":       "✅ Услуга добавлена! ID: #{sid}",
        "admin_del_ask":        "Напишите <b>ID</b> услуги для удаления:",
        "admin_del_done":       "✅ Услуга удалена.",
        "admin_del_notfound":   "❌ Такой ID не найден.",
        "admin_orders_empty":   "📭 Заказов нет.",
        "admin_order_card": (
            "📦 <b>Заказ #{id}</b>\n"
            "👤 {name} | 📞 {contact}\n"
            "🧠 {service}\n📝 {details}\n"
            "📅 {created}\nСтатус: <b>{status}</b>"
        ),
        "admin_clients_empty":  "👥 Клиентов пока нет.",
        "admin_clients_title":  "👥 <b>Клиенты</b>  (🔴 — новые обращения)",
        "admin_client_card": (
            "👤 <b>{name}</b>\n"
            "🆔 <code>{user_id}</code> | @{username}\n"
            "📞 {phone} | 🕒 {created}\n\n"
            "📦 Заказы ({orders_n}):\n{orders}\n\n"
            "📞 Обращения ({reqs_n}):\n{reqs}"
        ),
        "admin_no_orders":      "— нет —",
        "admin_no_reqs":        "— нет —",
        "admin_reply_ask":      "Напишите сообщение для клиента:",
        "admin_reply_sent":     "✅ Отправлено клиенту.",
        "admin_reply_failed":   "❌ Не удалось: {err}",
        "admin_resolved":       "✅ Отмечено как решённое.",

        # ── User notifications ────────────────────────────────────────────
        "user_order_approved": (
            "✅ <b>Заказ подтверждён!</b>\n"
            "Администратор скоро свяжется. 🚀"
        ),
        "user_order_rejected": (
            f"❌ Заказ отклонён.\n"
            f"Вопросы: {_C['tg']}"
        ),
        "user_admin_reply": "💬 <b>Ответ администратора:</b>\n\n{text}",
        "unknown": "Используйте кнопки меню 👇",

        # ── Status labels ─────────────────────────────────────────────────
        "order_status_new":       "🆕 новый",
        "order_status_approved":  "✅ подтверждён",
        "order_status_rejected":  "❌ отклонён",
        "request_status_open":    "🔴 открыт",
        "request_status_resolved":"✅ решён",
        "request_type_admin_call":"📞 Вызов админа",
        "request_type_order":     "🛒 Заказ",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    """Return translated string, falling back to 'uz'."""
    lang = lang if lang in TEXTS else "uz"
    template = TEXTS[lang].get(key) or TEXTS["uz"].get(key, key)
    if kwargs:
        try:
            return template.format(**kwargs)
        except (KeyError, IndexError):
            return template
    return template
