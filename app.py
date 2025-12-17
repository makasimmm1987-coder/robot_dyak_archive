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
import html  # ← ВАЖНО! Для HTML-экранирования

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
