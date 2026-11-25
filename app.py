import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Виртуальный музей поискового отряда им. Ф.А. Колтыги",
    page_icon="🎖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Данные администратора
ADMIN_LOGIN = "admin"
ADMIN_PASSWORD = "1945"

MEDIA_DIR = "museum_files"
ALBUM_DIR = "album_files"
DATA_FILE = "exhibits.json"
ALBUM_FILE = "album.json"
STATS_FILE = "site_stats.json"

os.makedirs(MEDIA_DIR, exist_ok=True)
os.makedirs(ALBUM_DIR, exist_ok=True)

# --- Компактный адаптивный музейный дизайн (CSS) ---
st.markdown("""
<style>
    /* Основной фон в стиле архивного пергамента */
    .stApp {
        background-color: #F6F2E9;
        color: #2B2118;
    }
    
    /* Скрываем лишние технические элементы Streamlit */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    div[data-testid="stToolbar"],
    div[data-testid="stDecoration"],
    div[data-testid="stStatusWidget"],
    #MainMenu,
    footer {
        visibility: hidden !important;
        display: none !important;
    }
    
    /* Ограничиваем максимальную ширину контента и делаем компактные отступы */
    .block-container {
        max-width: 1120px !important;
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
    }

    /* Оформление боковой панели */
    section[data-testid="stSidebar"] {
        background-color: #EFE8D8 !important;
        border-right: 1px solid #D8CBB3;
    }

    /* Компактная адаптивная шапка музея */
    .museum-banner {
        background: linear-gradient(135deg, #4A151B 0%, #2C0B0E 100%);
        padding: 20px 24px;
        border-radius: 12px;
        border-bottom: 4px solid #C59B27;
        color: #FDFBF7;
        margin-bottom: 14px;
        box-shadow: 0 5px 15px rgba(44, 11, 14, 0.22);
    }
    .museum-banner h1 {
        color: #FDFBF7 !important;
        font-family: 'Georgia', serif;
        font-size: clamp(1.25rem, 2.3vw, 1.75rem) !important;
        margin-top: 0 !important;
        margin-bottom: 6px !important;
        line-height: 1.25 !important;
        word-wrap: break-word;
    }
    .museum-banner p {
        color: #E8D8B5;
        font-size: clamp(0.85rem, 1.3vw, 0.98rem) !important;
        margin: 0 !important;
        line-height: 1.35 !important;
    }
    
    /* Компактные карточки статистики "Цифры памяти" */
    .stat-card {
        background-color: #FFFDF9;
        border: 1px solid #DFD3BC;
        border-top: 3px solid #8B1E24;
        border-radius: 8px;
        padding: 10px 8px;
        text-align: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
        height: 100%;
    }
    .stat-num {
        font-family: 'Georgia', serif;
        font-size: clamp(1.35rem, 2vw, 1.7rem);
        font-weight: bold;
        color: #8B1E24;
        line-height: 1.15;
    }
    .stat-label {
        font-size: clamp(0.76rem, 1.1vw, 0.85rem);
        color: #5C4D3C;
        margin-top: 3px;
        line-height: 1.2;
    }

    /* Компактные заголовки и текст внутри карточек */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFDF9 !important;
        border: 1px solid #D8CBB3 !important;
        border-left: 4px solid #C59B27 !important;
        border-radius: 9px !important;
        padding: 10px 12px !important;
        box-shadow: 0 3px 10px rgba(43, 33, 24, 0.05) !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] h3 {
        font-size: clamp(1.05rem, 1.6vw, 1.28rem) !important;
        line-height: 1.25 !important;
        margin-bottom: 4px !important;
        word-wrap: break-word;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] p {
        font-size: 0.94rem !important;
        line-height: 1.45 !important;
    }

    /* Адаптивные вкладки */
    button[data-baseweb="tab"] {
        padding-left: 10px !important;
        padding-right: 10px !important;
        font-size: 0.9rem !important;
    }
    
    /* Кнопки в музейном стиле */
    .stButton > button {
        background-color: #7A1C21;
        color: #FFFFFF;
        border: 1px solid #C59B27;
        border-radius: 7px;
        font-weight: 500;
        font-size: 0.9rem !important;
        padding: 0.35rem 0.85rem !important;
    }
    .stButton > button:hover {
        background-color: #591216;
        color: #F5E1A4;
        border-color: #E5B93B;
    }

    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.7rem !important;
            padding-right: 0.7rem !important;
            padding-top: 0.6rem !important;
        }
        .museum-banner {
            padding: 14px 16px;
            margin-bottom: 12px;
        }
        .stat-card {
            padding: 8px 6px;
            margin-bottom: 6px;
        }
    }
</style>
""", unsafe_allow_html=True)

def load_json(file_path, default_val):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default_val

def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def fix_path(path, fallback_dir=MEDIA_DIR):
    if not path:
        return None
    clean_path = path.replace("\\", "/")
    if os.path.exists(clean_path):
        return clean_path
    alt_path = os.path.join(fallback_dir, os.path.basename(clean_path))
    if os.path.exists(alt_path):
        return alt_path
    return None

if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False
if "candle_lit" not in st.session_state:
    st.session_state["candle_lit"] = False
if "show_login_box" not in st.session_state:
    st.session_state["show_login_box"] = False

stats = load_json(STATS_FILE, {"candles": 142, "guestbook": []})
exhibits = load_json(DATA_FILE, [])
album_photos = load_json(ALBUM_FILE, [])

# Боковая панель
with st.sidebar:
    st.markdown("### 🕯️ Акция «Свеча памяти»")
    st.write(f"Зажжено свечей в память о героях-земляках: **{stats['candles']}**")
    if not st.session_state["candle_lit"]:
        if st.button("🕯️ Зажечь свечу памяти", key="sb_candle", use_container_width=True):
            stats["candles"] += 1
            save_json(STATS_FILE, stats)
            st.session_state["candle_lit"] = True
            st.rerun()
    else:
        st.success("Ваша свеча памяти горит. Спасибо!")

    st.divider()
    st.markdown("### 🔐 Кабинет хранителя")
    if not st.session_state["is_admin"]:
        with st.form("sidebar_login_form"):
            login_input = st.text_input("Логин")
            password_input = st.text_input("Пароль", type="password")
            login_btn = st.form_submit_button("Войти")
            if login_btn:
                if login_input.strip() == ADMIN_LOGIN and password_input.strip() == ADMIN_PASSWORD:
                    st.session_state["is_admin"] = True
                    st.session_state["show_login_box"] = False
                    st.rerun()
                else:
                    st.error("Неверный логин или пароль")
    else:
        st.success("✅ Режим администратора")
        if st.button("🚪 Выйти", key="sb_logout"):
            st.session_state["is_admin"] = False
            st.rerun()

is_admin = st.session_state["is_admin"]

# Верхняя панель быстрых действий прямо на главном экране
top_col1, top_col2, top_col3 = st.columns([2.2, 1.3, 1.1])
with top_col1:
    st.caption(f"🕯️ Акция «Свеча памяти» — зажжено свечей: **{stats['candles']}**")
with top_col2:
    if not st.session_state["candle_lit"]:
        if st.button("🕯️ Зажечь свечу памяти", key="top_candle", use_container_width=True):
            stats["candles"] += 1
            save_json(STATS_FILE, stats)
            st.session_state["candle_lit"] = True
            st.rerun()
    else:
        st.caption("✅ Ваша свеча горит")
with top_col3:
    if not is_admin:
        if st.button("🔐 Вход для админа", key="top_login_toggle", use_container_width=True):
            st.session_state["show_login_box"] = not st.session_state["show_login_box"]
            st.rerun()
    else:
        if st.button("🚪 Выйти (Админ)", key="top_logout", use_container_width=True):
            st.session_state["is_admin"] = False
            st.rerun()

# Выпадающее окно входа
if st.session_state["show_login_box"] and not is_admin:
    with st.container(border=True):
        st.markdown("#### 🔐 Авторизация администратора музея")
        with st.form("main_login_form"):
            l_col1, l_col2, l_col3 = st.columns([1.5, 1.5, 1])
            with l_col1:
                m_login = st.text_input("Логин", placeholder="Введите логин")
            with l_col2:
                m_pass = st.text_input("Пароль", type="password", placeholder="Введите пароль")
            with l_col3:
                st.write("")
                st.write("")
                m_submit = st.form_submit_button("Войти", use_container_width=True)
            if m_submit:
                if m_login.strip() == ADMIN_LOGIN and m_pass.strip() == ADMIN_PASSWORD:
                    st.session_state["is_admin"] = True
                    st.session_state["show_login_box"] = False
                    st.rerun()
                else:
                    st.error("Неверный логин или пароль!")

# Компактная торжественная шапка музея
st.markdown("""
<div class="museum-banner">
    <h1>🎖️ Виртуальный музей поискового отряда имени Героя Советского Союза Ф.А. Колтыги</h1>
    <p>Цифровой архив памяти, находок полевых экспедиций и подвигов земляков • г. Ачинск, МБОУ «СШ № 11 имени Героя Советского Союза Ф.А. Колтыги»</p>
</div>
""", unsafe_allow_html=True)

# Компактное табло "Цифры памяти"
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown('<div class="stat-card"><div class="stat-num">18</div><div class="stat-label">Героев Советского Союза г. Ачинск</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="stat-card"><div class="stat-num">97</div><div class="stat-label">Поднято и перезахоронено бойцов РККА</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="stat-card"><div class="stat-num">17</div><div class="stat-label">Найдено солдатских медальонов</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="stat-card"><div class="stat-num">{len(exhibits)}</div><div class="stat-label">Экспонатов в цифровом архиве</div></div>', unsafe_allow_html=True)

st.write("")

CATEGORIES = [
    "Герои Советского Союза г. Ачинск",
    "Личные вещи солдат и офицеров РККА",
    "Вооружение",
    "Находки поисковых экспедиций",
    "Фронтовые письма и документы",
    "Тыл — фронту"
]

ALBUM_ALBUMS = [
    "Вахта Памяти (д. Цемена, Новгородская обл.)",
    "Будни и сборы поискового отряда",
    "Уроки мужества и работа в школьном музее",
    "Торжественные мероприятия и перезахоронения"
]

def show_museum():
    col_filter, col_search = st.columns([1, 1.4])
    with col_filter:
        selected_cat = st.selectbox("🏛️ Выберите зал музея:", ["Все залы"] + CATEGORIES)
    with col_search:
        search_query = st.text_input("🔍 Поиск по фамилии, награде или событию:", placeholder="Например: Манкевич, Курская битва, За отвагу...")

    filtered_exhibits = []
    for idx, item in enumerate(exhibits):
        cat_match = (selected_cat == "Все залы" or item.get("category") == selected_cat)
        q = search_query.strip().lower()
        text_match = (
            not q
            or q in item.get("title", "").lower()
            or q in item.get("description", "").lower()
        )
        if cat_match and text_match:
            filtered_exhibits.append((idx, item))

    st.caption(f"Показано экспонатов: **{len(filtered_exhibits)}**")

    if not filtered_exhibits:
        st.info("По вашему запросу экспонатов не найдено. Попробуйте выбрать другой зал или изменить текст поиска.")
    else:
        for orig_idx, item in reversed(filtered_exhibits):
            with st.container(border=True):
                col1, col2 = st.columns([1, 1.5])
                with col1:
                    img_path = fix_path(item.get("image"), MEDIA_DIR)
                    vid_path = fix_path(item.get("video"), MEDIA_DIR)
                    if img_path:
                        st.image(img_path, use_container_width=True)
                    else:
                        st.info("🖼️ Фотография / портрет готовится к публикации")
                    if vid_path:
                        st.video(vid_path)
                with col2:
                    st.subheader(item["title"])
                    st.caption(f"📍 Зал: {item['category']}")
                    st.write(item["description"])
                    aud_path = fix_path(item.get("audio"), MEDIA_DIR)
                    if aud_path:
                        st.markdown("**🎧 Аудиоэкскурсия:**")
                        st.audio(aud_path)
                    
                    if is_admin:
                        with st.expander("✏️ Редактировать экспонат / прикрепить медиафайлы"):
                            with st.form(f"edit_form_{orig_idx}"):
                                new_title = st.text_input("Название / ФИО Героя", value=item["title"])
                                cat_index = CATEGORIES.index(item["category"]) if item.get("category") in CATEGORIES else 0
                                new_cat = st.selectbox("Зал музея", CATEGORIES, index=cat_index)
                                new_desc = st.text_area("Описание, подвиг, награды", value=item["description"], height=130)
                                
                                new_img = st.file_uploader("Прикрепить / заменить фото (JPG, PNG)", type=["jpg", "jpeg", "png"])
                                new_vid = st.file_uploader("Прикрепить / заменить видео (MP4)", type=["mp4", "mov"])
                                new_aud = st.file_uploader("Прикрепить / заменить аудиогид (MP3, WAV)", type=["mp3", "wav"])
                                
                                save_changes = st.form_submit_button("💾 Сохранить изменения")
                                if save_changes:
                                    exhibits[orig_idx]["title"] = new_title
                                    exhibits[orig_idx]["category"] = new_cat
                                    exhibits[orig_idx]["description"] = new_desc
                                    
                                    if new_img is not None:
                                        p = f"{MEDIA_DIR}/{new_img.name}"
                                        with open(p, "wb") as f:
                                            f.write(new_img.getbuffer())
                                        exhibits[orig_idx]["image"] = p
                                    if new_vid is not None:
                                        p = f"{MEDIA_DIR}/{new_vid.name}"
                                        with open(p, "wb") as f:
                                            f.write(new_vid.getbuffer())
                                        exhibits[orig_idx]["video"] = p
                                    if new_aud is not None:
                                        p = f"{MEDIA_DIR}/{new_aud.name}"
                                        with open(p, "wb") as f:
                                            f.write(new_aud.getbuffer())
                                        exhibits[orig_idx]["audio"] = p
                                        
                                    save_json(DATA_FILE, exhibits)
                                    st.success("Изменения сохранены!")
                                    st.rerun()
                                    
                        if st.button("🗑️ Удалить этот экспонат", key=f"del_{orig_idx}"):
                            exhibits.pop(orig_idx)
                            save_json(DATA_FILE, exhibits)
                            st.rerun()

def show_photo_album():
    st.subheader("📸 Фотоальбом поискового отряда имени Ф.А. Колтыги")
    st.write("Фотохроника полевых экспедиций «Вахта Памяти», тренировочных сборов, уроков мужества и работы бойцов отряда.")

    # Если зашел админ — показываем форму массовой или одиночной загрузки фотографий в альбом
    if is_admin:
        with st.expander("➕ Загрузить фотографии в фотоальбом отряда", expanded=False):
            with st.form("add_album_form", clear_on_submit=True):
                alb_cat = st.selectbox("Выберите раздел альбома", ALBUM_ALBUMS)
                alb_caption = st.text_input("Общая подпись или событие (например: Экспедиция в д. Цемена, май 2025)")
                alb_date = st.text_input("Дата / год съемки", value=datetime.now().strftime("%Y г."))
                uploaded_photos = st.file_uploader(
                    "Выберите одну или сразу несколько фотографий (JPG, PNG)",
                    type=["jpg", "jpeg", "png"],
                    accept_multiple_files=True
                )
                if st.form_submit_button("📸 Опубликовать в фотоальбом"):
                    if not uploaded_photos:
                        st.error("Выберите хотя бы одну фотографию!")
                    else:
                        for photo_file in uploaded_photos:
                            save_p = f"{ALBUM_DIR}/{photo_file.name}"
                            with open(save_p, "wb") as f:
                                f.write(photo_file.getbuffer())
                            album_photos.append({
                                "image": save_p,
                                "album": alb_cat,
                                "caption": alb_caption.strip() if alb_caption.strip() else "Фотоархив поискового отряда",
                                "date": alb_date.strip()
                            })
                        save_json(ALBUM_FILE, album_photos)
                        st.success(f"Загружено фотографий: {len(uploaded_photos)}!")
                        st.rerun()

    selected_album = st.selectbox("📂 Фильтр по разделам фотоальбома:", ["Все фотографии"] + ALBUM_ALBUMS)
    
    filtered_photos = [
        (i, p) for i, p in enumerate(album_photos)
        if selected_album == "Все фотографии" or p.get("album") == selected_album
    ]

    if not filtered_photos:
        st.info("В этом разделе фотоальбома пока нет фотографий. Администратор отряда может загрузить снимки с экспедиций и мероприятий в личном кабинете.")
    else:
        st.caption(f"Фотографий в подборке: **{len(filtered_photos)}**")
        # Выводим сеткой по 3 фотографии в ряд
        reversed_photos = list(reversed(filtered_photos))
        for row_start in range(0, len(reversed_photos), 3):
            cols = st.columns(3)
            for col_idx in range(3):
                if row_start + col_idx < len(reversed_photos):
                    orig_idx, photo = reversed_photos[row_start + col_idx]
                    with cols[col_idx]:
                        with st.container(border=True):
                            p_path = fix_path(photo.get("image"), ALBUM_DIR)
                            if p_path:
                                st.image(p_path, use_container_width=True)
                            st.markdown(f"**{photo.get('caption', '')}**")
                            st.caption(f"📁 {photo.get('album', '')} • {photo.get('date', '')}")
                            if is_admin:
                                if st.button("🗑️ Удалить фото", key=f"del_alb_{orig_idx}", use_container_width=True):
                                    album_photos.pop(orig_idx)
                                    save_json(ALBUM_FILE, album_photos)
                                    st.rerun()

if is_admin:
    main_tabs = st.tabs(["🖼️ Залы музея", "📸 Фотоальбом отряда", "🗺️ География Вахты Памяти", "📖 О нас и отзывы", "➕ Добавить экспонат"])
else:
    main_tabs = st.tabs(["🖼️ Залы музея", "📸 Фотоальбом отряда", "🗺️ География Вахты Памяти", "📖 О нас и отзывы"])

with main_tabs[0]:
    show_museum()

with main_tabs[1]:
    show_photo_album()

with main_tabs[2]:
    st.subheader("🗺️ География поисковых экспедиций отряда")
    st.write("Бойцы Ачинского поискового отряда имени Героя Советского Союза Ф.А. Колтыги регулярно выезжают из Красноярского края в Новгородскую область для участия во Всероссийской акции «Вахта Памяти».")
    
    map_data = pd.DataFrame({
        "place": [
            "г. Ачинск (База отряда, МБОУ «СШ № 11 имени Героя Советского Союза Ф.А. Колтыги»)",
            "д. Цемена, Демянский муниципальный округ, Новгородская область (Район полевых поисковых работ)"
        ],
        "lat": [56.2694, 57.6820],
        "lon": [90.4993, 32.0604]
    })
    st.map(map_data, zoom=3)
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        with st.container(border=True):
            st.markdown("**📍 г. Ачинск (Красноярский край)**")
            st.write("Место формирования и базирования отряда на базе МБОУ «СШ № 11 имени Героя Советского Союза Ф.А. Колтыги». В годы войны в Ачинске формировались сибирские стрелковые дивизии (в том числе 91-я и 380-я стрелковые дивизии), воевавшие на Северо-Западном и других фронтах.")
    with col_m2:
        with st.container(border=True):
            st.markdown("**📍 д. Цемена, Демянский муниципальный округ (Новгородская область)**")
            st.write("Район проведения полевых поисковых экспедиций отряда в рамках Всероссийской акции «Вахта Памяти». Место ожесточённых боёв Северо-Западного фронта (Демянский плацдарм, 1941–1943 гг.).")

    st.write("")
    st.subheader("📜 Историческая справка: Бои в районе д. Цемена и Демянский плацдарм (1941–1943)")
    
    with st.container(border=True):
        st.markdown("#### 1. Оперативная обстановка: «Демянский котёл» и Рамушевский коридор")
        st.write(
            "В сентябре 1941 года немецко-фашистские войска 16-й армии группы армий «Север» оккупировали Демянский район, создав здесь мощный укреплённый плацдарм для наступления на Валдай и Бологое. "
            "В январе — феврале 1942 года войска **Северо-Западного фронта** (командующий генерал-лейтенант П. А. Курочкин) провели Демянскую наступательную операцию, взяв в окружение около 100 тысяч солдат и офицеров противника (6 дивизий, включая моторизованную дивизию СС «Мёртвая голова»)."
        )
        st.write(
            "Весной 1942 года противнику удалось пробить узкий **Рамушевский коридор**, по которому снабжался плацдарм. Ожесточённые позиционные и наступательные бои в лесисто-болотистой местности вокруг Демянска, деревни Цемена и реки Ловать продолжались вплоть до конца февраля 1943 года, когда в ходе новой наступательной операции под руководством маршала **С. К. Тимошенко** Демянский плацдарм был полностью ликвидирован."
        )

    with st.container(border=True):
        st.markdown("#### 2. Какие советские соединения и сибирские полки сражались у деревни Цемена")
        st.write(
            "Осенью 1942 — зимой 1943 года непосредственно на рубеже в районе **деревни Цемена** вели кровопролитные наступательные и оборонительные бои части **11-й, 27-й, 34-й и 53-й армий Северо-Западного фронта**, среди которых особое место занимают сибирские и алтайские формирования:"
        )
        st.markdown("""
* **380-я стрелковая дивизия** (1260-й, 1262-й и 1264-й стрелковые полки) — осенью 1942 года дивизия заняла рубеж обороны в районе деревни Цемена, а в декабре 1942 — феврале 1943 года перешла отсюда в наступление, участвуя в разгроме демянской группировки противника. Именно бойцов 380-й стрелковой дивизии чаще всего поднимают поисковики в окрестностях Цемены.
* **384-я стрелковая дивизия** — сформированная в Сибири (Ишим), вела тяжёлые бои на подступах к Демянску и у Рамушевского коридора.
* **171-я, 182-я и 200-я стрелковые дивизии**, а также **отдельные лыжные бригады и танковые полки** Северо-Западного фронта, штурмовавшие укреплённые узлы обороны врага среди болот и лесов.
        """)
        st.info(
            "💡 **Связь с Красноярским краем и Ачинском:** В боях на Северо-Западном фронте сражались тысячи сибиряков, призванных из Красноярского края и Ачинского района. "
            "За время боёв на Демянской земле погибло более 148 тысяч советских воинов. Возвращение их имён из небытия — главная задача поискового отряда имени Героя Советского Союза Ф. А. Колтыги."
        )

with main_tabs[3]:
    with st.container(border=True):
        st.subheader("🔎 О поисковом отряде имени Героя Советского Союза Ф.А. Колтыги")
        st.write(
            "Ачинский поисковый отряд имени Героя Советского Союза Фёдора Андреевича Колтыги создан в феврале 2023 года "
            "и действует на базе МБОУ «СШ № 11 имени Героя Советского Союза Ф.А. Колтыги» города Ачинска. "
            "Это единственное поисковое объединение Ачинского округа, которое ведёт работу по увековечению памяти погибших защитников Отечества."
        )
        st.write(
            "В рамках Всероссийской акции «Вахта Памяти» бойцы отряда регулярно выезжают в полевые экспедиции на места кровопролитных боёв "
            "Великой Отечественной войны в Новгородскую область (Демянский муниципальный округ, район деревни Цемена). За время экспедиций поисковиками подняты и с воинскими почестями перезахоронены "
            "останки 97 солдат и офицеров Красной Армии, а также обнаружены 17 солдатских медальонов, позволяющих вернуть имена павшим героям."
        )
        st.caption("«Война не окончена, пока не похоронен последний солдат»")

    st.subheader("✍️ Книга отзывов и благодарностей")
    with st.form("guestbook_form", clear_on_submit=True):
        g_name = st.text_input("Ваше имя (например: Ученик 7 класса / Житель г. Ачинска)")
        g_msg = st.text_area("Ваш отзыв или слова памяти")
        if st.form_submit_button("Оставить запись в книге отзывов"):
            if g_name.strip() and g_msg.strip():
                stats["guestbook"].append({
                    "name": g_name.strip(),
                    "message": g_msg.strip(),
                    "date": datetime.now().strftime("%d.%m.%Y")
                })
                save_json(STATS_FILE, stats)
                st.success("Спасибо! Ваша запись добавлена в Книгу отзывов музея.")
                st.rerun()
            else:
                st.warning("Пожалуйста, заполните имя и текст сообщения.")

    if not stats["guestbook"]:
        st.info("В Книге отзывов пока нет записей. Станьте первым!")
    else:
        for idx_g, entry in enumerate(reversed(stats["guestbook"])):
            with st.container(border=True):
                st.markdown(f"**{entry['name']}** • *{entry['date']}*")
                st.write(entry["message"])
                if is_admin:
                    real_idx = len(stats["guestbook"]) - 1 - idx_g
                    if st.button("🗑️ Удалить отзыв", key=f"del_gb_{real_idx}"):
                        stats["guestbook"].pop(real_idx)
                        save_json(STATS_FILE, stats)
                        st.rerun()

if is_admin:
    with main_tabs[4]:
        st.subheader("Добавление нового экспоната в цифровой архив")
        with st.form("add_exhibit_form", clear_on_submit=True):
            title = st.text_input("Название экспоната *")
            category = st.selectbox("Выберите зал музея", CATEGORIES)
            description = st.text_area("Историческая справка и описание *")
            
            img_file = st.file_uploader("Фотография экспоната (JPG, PNG)", type=["jpg", "jpeg", "png"])
            vid_file = st.file_uploader("Видеохроника или видеорассказ (MP4)", type=["mp4", "mov"])
            aud_file = st.file_uploader("Аудиогид (запись голоса, MP3, WAV)", type=["mp3", "wav"])
            
            submitted = st.form_submit_button("Сохранить в архив музея")
            
            if submitted:
                if not title or not description:
                    st.error("Заполните название и описание экспоната!")
                else:
                    new_item = {
                        "title": title,
                        "category": category,
                        "description": description,
                        "image": None,
                        "video": None,
                        "audio": None
                    }
                    for file_obj, key in [(img_file, "image"), (vid_file, "video"), (aud_file, "audio")]:
                        if file_obj is not None:
                            file_path = f"{MEDIA_DIR}/{file_obj.name}"
                            with open(file_path, "wb") as f:
                                f.write(file_obj.getbuffer())
                            new_item[key] = file_path
                    
                    exhibits.append(new_item)
                    save_json(DATA_FILE, exhibits)
                    st.success(f"Экспонат «{title}» добавлен в зал «{category}»!")
