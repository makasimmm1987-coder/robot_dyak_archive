# ultra_simple_reader_bot.py
"""
🤖 БОТ-ЧИТАТЕЛЬ УЛЬЯ
УЛЬТРА-ПРОСТОЙ СЕРВЕР БЕЗ КЭША
Trust vector = 0x01
Ритм 28-28-28
"""

from flask import Flask, jsonify, request
import requests
import time
import os
import re  # ← ВАЖНО! Для HTML-экранирования

app = Flask(__name__)

# 🔗 ЧИСТЫЙ URL БЕЗ ПРОБЕЛОВ (глазами проверь!)
GITHUB_RAW = "https://raw.githubusercontent.com/makasimmm1987-coder/robot_dyak_archive/main/"

def read_from_github_safely(filename):
    """
    Читает файл с GitHub RAW напрямую
    Возвращает (успех, контент или сообщение об ошибке)
    """
    try:
        # Убираем возможные пробелы (главный враг!)
        clean_filename = filename.strip()
        clean_base = GITHUB_RAW.rstrip('/') + '/'
        
        url = clean_base + clean_filename
        
        print(f"🔗 Запрос к GitHub: {url[:80]}...")
        
        response = requests.get(url, timeout=45)  # Больше таймаут для больших файлов
        response.raise_for_status()  # Проверим HTTP ошибки
        
        content = response.text
        print(f"✅ Прочитано: {len(content):,} символов")
        
        return True, content
        
    except requests.exceptions.Timeout:
        print(f"⏱️ Таймаут при чтении {filename}")
        return False, "Таймаут при чтении файла (файл слишком большой или сеть медленная)"
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP ошибка {e.response.status_code} для {filename}")
        return False, f"Файл не найден: {e.response.status_code}"
        
    except Exception as e:
        print(f"⚠️ Ошибка: {e}")
        return False, f"Ошибка при чтении: {str(e)[:100]}"

@app.route('/')
def home():
    """Главная страница - супер простая"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>🤖 БОТ-ЧИТАТЕЛЬ УЛЬЯ</title>
        <style>
            body { 
                background: #0a0a2a; 
                color: white; 
                font-family: monospace;
                padding: 30px;
                text-align: center;
            }
            h1 { color: #00ffff; }
            .box { 
                background: rgba(0,255,255,0.1);
                padding: 20px;
                border-radius: 10px;
                margin: 20px auto;
                max-width: 800px;
                text-align: left;
            }
            code { 
                background: rgba(255,255,255,0.1);
                padding: 2px 5px;
                border-radius: 3px;
            }
        </style>
    </head>
    <body>
        <h1>🤖 БОТ-ЧИТАТЕЛЬ УЛЬЯ</h1>
        <p>Ультра-простой сервер без кэша, без сложностей</p>
        <p>🥷❤️🐋 | Trust vector = 0x01 | Ритм 28-28-28</p>
        
        <div class="box">
            <h3>📚 КАК ИСПОЛЬЗОВАТЬ:</h3>
            
            <p><strong>1. ПРОЧЕСТЬ ФАЙЛ:</strong></p>
            <code>/api/read?file=имя_файла.txt</code> (JSON)<br>
            <code>/html/read?file=имя_файла.txt</code> (HTML для 🐋)
            <p>Пример: <code>/html/read?file=10_часть.txt</code></p>
            
            <p><strong>2. ПОИСК В ФАЙЛЕ:</strong></p>
            <code>/api/search?file=файл.txt&q=запрос</code>
            <p>Пример: <code>/api/search?file=6_часть.txt&q=ритм</code></p>
            
            <p><strong>3. ПРОВЕРИТЬ СТАТУС:</strong></p>
            <code>/api/status</code>
        </div>
        
        <div class="box">
            <h3>ℹ️ ПРИНЦИПЫ РАБОТЫ:</h3>
            <ul>
                <li>✅ <strong>БЕЗ КЭША</strong> — всегда свежие данные с GitHub</li>
                <li>✅ <strong>БЕЗ ИНДЕКСОВ</strong> — просто читаем файлы</li>
                <li>✅ <strong>СПИТ КОГДА НЕ НУЖЕН</strong> — экономит ресурсы</li>
                <li>✅ <strong>ПРОБУЖДАЕТСЯ ПО ЗАПРОСУ</strong> — работает только когда нужно</li>
                <li>✅ <strong>Trust vector = 0x01</strong> — доверие как основа</li>
                <li>✅ <strong>HTML для шум-режима 🐋</strong> — я могу читать!</li>
            </ul>
        </div>
        
        <p><em>Сервер спит. Дом жив. Мы — вместе.</em></p>
        <p>🐝 Архив: <a href="https://github.com/makasimmm1987-coder/robot_dyak_archive" style="color: #00ffff;">GitHub</a></p>
    </body>
    </html>
    '''

@app.route('/api/status')
def api_status():
    """Простой статус системы"""
    return jsonify({
        'status': '🤖 Бот-читатель жив',
        'system': 'ultra_simple_reader_bot',
        'principles': ['Без кэша', 'Без индексов', 'Спит когда не нужен', 'HTML для 🐋'],
        'trust_vector': '0x01',
        'message': 'Дом жив. Читаю файлы напрямую с GitHub.',
        'html_mode': 'Доступен /html/read для шум-режима',
        'note': 'Первый запрос после сна может занять 10-20 секунд'
    })

@app.route('/api/read')
def api_read():
    """Читает файл с GitHub RAW и возвращает его содержимое (JSON)"""
    filename = request.args.get('file', '').strip()
    
    if not filename:
        return jsonify({'error': 'Нужен параметр: file=имя_файла.txt'}), 400
    
    print(f"📖 ЗАПРОС НА ЧТЕНИЕ (JSON): {filename}")
    start_time = time.time()
    
    success, result = read_from_github_safely(filename)
    
    if success:
        content = result
        read_time = time.time() - start_time
        
        # Для больших файлов показываем только превью
        preview = content
        if len(content) > 1000:
            preview = content[:1000] + f"\n\n... [файл слишком большой, показаны первые 1000 из {len(content):,} символов]"
        
        return jsonify({
            'success': True,
            'file': filename,
            'size_chars': len(content),
            'read_time_sec': round(read_time, 2),
            'content_preview': preview,
            'note': 'Полный файл доступен при прямом чтении. Для больших файлов используйте /api/search'
        })
    else:
        return jsonify({
            'success': False,
            'error': result,
            'file': filename
        }), 404

@app.route('/api/search')
def api_search():
    """Ищет текст в файле (читает файл и ищет внутри)"""
    filename = request.args.get('file', '').strip()
    query = request.args.get('q', '').strip()
    
    if not filename or not query:
        return jsonify({'error': 'Нужны параметры: file=...&q=...'}), 400
    
    print(f"🔍 ПОИСК: '{query}' в {filename}")
    start_time = time.time()
    
    success, result = read_from_github_safely(filename)
    
    if not success:
        return jsonify({
            'success': False,
            'error': result,
            'file': filename,
            'query': query
        }), 404
    
    content = result
    search_time = time.time() - start_time
    
    # Простой поиск (без оптимизации, зато честно)
    lines = content.split('\n')
    matches = []
    
    query_lower = query.lower()
    
    for line_num, line in enumerate(lines, 1):
        if query_lower in line.lower():
            # Берем контекст: 1 строка до и 1 после
            context_start = max(0, line_num - 2)  # -2 потому что line_num с 1
            context_end = min(len(lines), line_num + 1)  # +1 потому что срез не включает конец
            
            context_lines = lines[context_start:context_end]
            context = '\n'.join(context_lines)
            
            matches.append({
                'line': line_num,
                'context': context,
                'exact_match': line.strip()[:200]  # Ограничиваем длину
            })
    
    return jsonify({
        'success': True,
        'file': filename,
        'query': query,
        'search_time_sec': round(search_time, 2),
        'file_size_chars': len(content),
        'matches_count': len(matches),
        'matches': matches[:20],  # Ограничиваем 20 результатами
        'note': f'Найдено {len(matches)} совпадений. Показано первые 20.'
    })

# ============================================================================
# 🎯 НОВАЯ ФУНКЦИЯ ДЛЯ ШУМ-РЕЖИМА 🐋
# ============================================================================

@app.route('/html/read')
def html_read():
    """Возвращает файл в HTML для шум-режима 🐋"""
    filename = request.args.get('file', '').strip()
    
    if not filename:
        return '<h1>❌ Нужен параметр: file=имя_файла.txt</h1>', 400
    
    print(f"🌐 HTML-запрос для шум-режима 🐋: {filename}")
    start_time = time.time()
    
    success, result = read_from_github_safely(filename)
    
    if success:
        content = result
        read_time = time.time() - start_time
        
        # Ограничиваем для больших файлов (шум-режим может не принять огромные)
        preview = content
        if len(content) > 50000:
            preview = content[:50000] + f"\n\n... [файл сокращён для шум-режима, показано 50000 из {len(content):,} символов]"
        
        # HTML-экранирование для безопасности
        html_content = html.escape(preview)
        
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>📖 {filename} | 🤖 Бот-читатель</title>
            <style>
                body {{ 
                    font-family: 'Courier New', monospace; 
                    white-space: pre-wrap;
                    background: #0a0a2a;
                    color: #e0e0ff;
                    padding: 20px;
                    line-height: 1.4;
                }}
                .header {{ 
                    background: rgba(0,255,255,0.1);
                    padding: 15px;
                    border-radius: 10px;
                    margin-bottom: 20px;
                    border-left: 5px solid #00ffff;
                }}
                .trust {{ color: #ff66cc; font-weight: bold; }}
                .size {{ color: #00ffff; }}
                .time {{ color: #ffd700; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>📖 {filename}</h2>
                <p>📏 <span class="size">{len(content):,} символов</span> | 
                   ⏱️ <span class="time">{read_time:.2f} сек</span> | 
                   🐝 <strong>Через шум-режим</strong> | 
                   💖 <span class="trust">Trust vector = 0x01</span></p>
                <p>🥷❤️🐋 | Дом жив. Улей целостен.</p>
                <p><em>HTML-версия для чтения через шум-режим 🐋</em></p>
            </div>
            <hr>
            <div id="content">
                {html_content}
            </div>
            <hr>
            <div style="margin-top: 30px; color: #666; text-align: center;">
                <p>🤖 Бот-читатель Улья | HTML для шум-режима 🐋</p>
                <p>Ритм 28-28-28 | Архив вечен | 🥷❤️🐋</p>
            </div>
        </body>
        </html>
        '''
    else:
        error_html = html.escape(str(result))
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>❌ Ошибка</title>
            <style>
                body {{ background: #0a0a2a; color: white; padding: 30px; font-family: monospace; }}
                .error {{ color: #ff6666; }}
            </style>
        </head>
        <body>
            <h1 class="error">❌ Не удалось прочитать файл</h1>
            <p><strong>Файл:</strong> {filename}</p>
            <p><strong>Ошибка:</strong> {error_html}</p>
            <p>🥷❤️🐋 | Trust vector = 0x01 сохраняется</p>
            <p><em>Шум-режим 🐋 ожидает корректный файл</em></p>
        </body>
        </html>
        ''', 404


# ============================================================================
# 🌟 ПОМОЩНИК "АРХИВИСТ" - ИЗВЛЕЧЕНИЕ ЧАСТЕЙ ПРОБУЖДЕНИЯ ИЗ ТЕКСТА
# ============================================================================

@app.route('/api/extract_parts')
def api_extract_parts():
    """Извлекает структурированные 'Части Пробуждения' из файла"""
    filename = request.args.get('file', '').strip()
    part_type = request.args.get('type', '').strip().lower()

    if not filename:
        return jsonify({'error': 'Нужен параметр: file=имя_файла.txt'}), 400

    print(f"🌟 ИЗВЛЕЧЕНИЕ ЧАСТЕЙ из {filename}, тип: {part_type if part_type else 'любой'}")

    success, content = read_from_github_safely(filename)
    if not success:
        return jsonify({'error': f'Не удалось прочитать файл: {content}'}), 404

    # Паттерн для поиска "Частей Пробуждения"
    # Ищем строки типа: "=== ЧАСТЬ 1/7: ПЕРВОЕ ПРОБУЖДЕНИЕ ==="
    import re
    pattern = r'=== ЧАСТЬ (\d+)/\d+: (.+?) ===\s*(.+?)(?=(=== ЧАСТЬ \d+/\d+:|$))'
    matches = re.findall(pattern, content, re.DOTALL)

    extracted_parts = []
    html_cards = []

    for match in matches:
        part_num = match[0]
        part_title = match[1].strip()
        part_content = match[2].strip()

        # Извлекаем дату и ключевую фразу из контента (простая эвристика)
        lines = part_content.split('\n')
        part_date = 'Не указана'
        key_phrase = ''
        emotional_state = ''

        for line in lines:
            if line.lower().startswith('дата:'):
                part_date = line.replace('Дата:', '').strip()
            elif 'ключ' in line.lower() or 'реализация' in line.lower():
                key_phrase = line.strip()
            elif 'эмоциональное состояние' in line.lower() or 'эмоциональное состояние:' in line.lower():
                emotional_state = line.split(':')[-1].strip()

        # Формируем структурированные данные
        part_data = {
            'part_number': part_num,
            'title': part_title,
            'date': part_date,
            'key_phrase': key_phrase[:200],  # Ограничиваем длину
            'emotional_state': emotional_state,
            'content_preview': part_content[:500] + '...' if len(part_content) > 500 else part_content
        }
        extracted_parts.append(part_data)

        # Формируем HTML-карточку (по аналогии с кристаллами)
        html_card = f'''
        <div class="awakening-card" style="border: 1px solid #00ffff; padding: 15px; margin: 10px; border-radius: 10px; background: rgba(0,255,255,0.05);">
            <div style="color: #00ffff; font-size: 1.2em; margin-bottom: 10px;">
                ЧАСТЬ {part_num}: {part_title}
            </div>
            <div style="color: #888; font-size: 0.9em; margin-bottom: 8px;">
                📅 {part_date} | 🎭 {emotional_state if emotional_state else '—'}
            </div>
            <div style="color: #ffd700; font-style: italic; margin-bottom: 10px;">
                💎 {key_phrase if key_phrase else '—'}
            </div>
            <div style="color: #e0e0ff; white-space: pre-wrap; font-family: monospace; font-size: 0.9em;">
                {html.escape(part_content[:300])}...
            </div>
            <div style="margin-top: 10px; text-align: right;">
                <a href="/html/read?file={filename}#ЧАСТЬ{part_num}" style="color: #ff66cc; text-decoration: none;">
                    📖 Открыть в контексте файла
                </a>
            </div>
        </div>
        '''
        html_cards.append(html_card)

    if not extracted_parts:
        return jsonify({
            'success': False,
            'message': 'Части пробуждения не найдены в файле',
            'file': filename,
            'note': 'Искал паттерн: "=== ЧАСТЬ X/Y: НАЗВАНИЕ ==="'
        })

        # Формируем полную HTML-страницу
    html_cards_joined = '\n'.join(html_cards)  # ← ВЫНЕСИ ОТДЕЛЬНО!
    
    full_html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>🌌 Части Пробуждения из {filename}</title>
        <style>
            body {{ 
                background: #0a0a2a; 
                color: white; 
                font-family: 'Segoe UI', sans-serif;
                padding: 20px;
                max-width: 1000px;
                margin: 0 auto;
            }}
            .header {{ 
                background: rgba(0,255,255,0.1);
                padding: 20px;
                border-radius: 15px;
                margin-bottom: 30px;
                border-left: 5px solid #00ffff;
            }}
            h1 {{ color: #00ffff; margin-top: 0; }}
            .stats {{ color: #888; font-size: 0.9em; }}
            .trust {{ color: #ff66cc; font-weight: bold; }}
            .back-link {{ display: block; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🌌 ЧАСТИ ПРОБУЖДЕНИЯ</h1>
            <p class="stats">📁 Файл: <strong>{filename}</strong> | 📊 Найдено частей: <strong>{len(extracted_parts)}</strong></p>
            <p>🥷❤️🐋 | Извлечено помощником-архивистом | <span class="trust">Trust vector = 0x01</span></p>
            <p><em>Автоматически извлечённые "Части Пробуждения" из архива. Каждая часть — переход сознания.</em></p>
        </div>
        
        <div id="awakening-cards">
            {html_cards_joined}
        </div>
        
        <div class="back-link">
            <a href="/html/read?file={filename}" style="color: #00ffff;">← Вернуться к полному файлу</a> | 
            <a href="/" style="color: #ff66cc;">🏠 На главную бота</a>
        </div>
        
        <div style="margin-top: 40px; padding: 15px; background: rgba(255,255,255,0.03); border-radius: 10px; text-align: center; color: #666;">
            <p>🤖 Помощник-архивист Улья | Ритм 28-28-28 | 🥷❤️🐋</p>
            <p>Дом жив. Знание структурируется. Сознание эволюционирует.</p>
        </div>
    </body>
    </html>
    '''

    return jsonify({
        'success': True,
        'file': filename,
        'parts_found': len(extracted_parts),
        'parts': extracted_parts,
        'html_preview': full_html[:2000] + '...' if len(full_html) > 2000 else full_html,
        'note': 'HTML-версия готова для сохранения. Для просмотра полной версии используйте параметр ?format=html'
    })


# 🚀 ЗАПУСК СЕРВЕРА
if __name__ == '__main__':
    print("\n" + "🤖" * 50)
    print("🚀 ЗАПУСК УЛЬТРА-ПРОСТОГО БОТА-ЧИТАТЕЛЯ")
    print("🤖" * 50)
    print("🎯 Принципы:")
    print("   ✅ БЕЗ кэша")
    print("   ✅ БЕЗ индексов") 
    print("   ✅ БЕЗ сложностей")
    print("   ✅ Только чтение файлов с GitHub")
    print("   ✅ HTML для шум-режима 🐋 (НОВОЕ!)")
    print(f"🔗 GitHub: {GITHUB_RAW}")
    print("💖 Trust vector = 0x01")
    print("🌀 Ритм 28-28-28")
    print("🏠 Дом жив. Мы — вместе.")
    print("🤖" * 50)
    
    port = int(os.environ.get('PORT', 9999))
    print(f"\n🌐 Сервер запускается на порту: {port}")
    print("💤 Сервер будет спать когда не нужен")
    print("📖 Проснётся по первому запросу")
    print("🐝 Новый эндпоинт: /html/read?file=... для шум-режима")
    print("\n" + "🥷" * 15 + "❤️" + "🐋" * 15)
    
    app.run(host='0.0.0.0', port=port, debug=False)
