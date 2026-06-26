DZ Nova - Royal Cars Design Update
=====================================

What was changed:
- Replaced the old dark/parallax interface with a Royal Cars-inspired automotive layout.
- Updated templates/base.html, templates/index.html and templates/diagnostic.html.
- Rebuilt static/css/style.css for the new car-service design.
- Updated static/js/diagnostic.js to keep the AI diagnosis flow stable.
- Kept the existing Flask routes, MySQL/XAMPP structure and /api/diagnose endpoint.
- Added Royal Cars images under static/img/royal/.
- Fixed the PDF export logic by using a safer print-window load flow.
- Preserved multilingual EN/FR/AR behavior and RTL support for Arabic.

Run steps:
1. Start XAMPP and enable MySQL.
2. Import database/schema.sql into phpMyAdmin if needed.
3. Install requirements: pip install -r requirements.txt
4. Run: python run.py
5. Open: http://127.0.0.1:5000

Important:
If results do not appear, check that /api/diagnose responds and that your MySQL service is running.
The frontend now sends data to /api/diagnose with: text, vehicle and lang.
