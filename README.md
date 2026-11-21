# 🔐 Secure Shop Lab - Termux

معمل اختبار اختراق عملي على موبايل - Flask + SQLite

## 🛡️ الحماية المطبقة
| الهجمة | الحماية |
| :--- | :--- |
| SQLi | Parameterized Queries |
| XSS | html.escape + textContent |
| Password | scrypt hashing |
| Session | HttpOnly + SameSite + Logout |
| IDOR | orders by session user_id |

## 🚀 التشغيل
```bash
pip install Flask
python app.py
