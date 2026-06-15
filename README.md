# jankiman
Jankiman - Nordic Retro Side-Scroller

Ein klassisches Retro-Arcade-Plattformspiel im MAME-Stil mit simuliertem CRT-Filter, 8-Bit Synthesizer-Soundeffekten, Parallaxe-Scrolling und tollem nordischen Vektor-Design. Führe Jankiman den Wikinger über gefährliche Abgründe und bringe ihn sicher zum magischen Runenstein am Ende der Stages!

Dieses Projekt beinhaltet sowohl eine Python/Pygame-Version als auch eine vollständig optimierte, eigenständige HTML5-Version!

🕹️ Steuerung

A / D oder PFEILTASTE LINKS / RECHTS: Bewegen (Kamera scrollt flüssig mit)

W / SPACE oder PFEILTASTE OBEN: Springen

Z-TASTE oder LINKS-STRG: Laser-Blaster abfeuern

ENTER: Spiel starten / fortsetzen

Die HTML5-Version unterstützt zusätzlich eine voll funktionsfähige On-Screen-Touch-Steuerung für mobile Geräte!

🚀 Spiel-Versionen

1. HTML5-Version (Direkt im Browser spielen)

Die HTML5-Version (index.html) benötigt keine lokale Installation und kann direkt als Static Site auf Render gehostet werden.

2. Python/Pygame-Version (Lokal spielen)

Voraussetzungen

Stelle sicher, dass du Python 3.9+ installiert hast.

Repository klonen:

git clone https://github.com/DEIN-USERNAME/jankiman.git
cd jankiman


Abhängigkeiten installieren:

pip install -r requirements.txt


Spiel lokal starten:

python main.py


🌐 WebAssembly-Build (Lokal testen)

Wenn du das Pygame-Spiel via WebAssembly im Browser testen willst:

python -m pygbag main.py


Öffne anschließend einfach deinen Webbrowser und rufe http://localhost:8000 auf.
