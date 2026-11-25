import streamlit as st
import streamlit.components.v1 as components
import os
import json
import base64
import pandas as pd
from datetime import datetime
from quiz_data import QUIZ_QUESTIONS

st.set_page_config(
    page_title="Виртуальный музей поискового отряда им. Ф.А. Колтыги",
    page_icon="🎖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

ADMIN_LOGIN = "admin"
ADMIN_PASSWORD = "1945"

MEDIA_DIR = "museum_files"
ALBUM_DIR = "album_files"
DATA_FILE = "exhibits.json"
ALBUM_FILE = "album.json"
STATS_FILE = "site_stats.json"

os.makedirs(MEDIA_DIR, exist_ok=True)
os.makedirs(ALBUM_DIR, exist_ok=True)

st.markdown("""
<style>
    .stApp {
        background-color: #F6F2E9;
        color: #2B2118;
    }
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
    .block-container {
        max-width: 1120px !important;
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #EFE8D8 !important;
        border-right: 1px solid #D8CBB3;
    }
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
    button[data-baseweb="tab"] {
        padding-left: 10px !important;
        padding-right: 10px !important;
        font-size: 0.9rem !important;
    }
    .stButton > button {
        background-color: #7A1C21;
        color: #FFFFFF;
        border: 1px solid #C59B27;
        border-radius: 7px;
        font-weight: 500;
        font-size: 0.9rem !important;
        padding: 0.4rem 0.85rem !important;
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

def get_logo_html():
    logo_path = fix_path("logo.png", MEDIA_DIR)
    if not logo_path and os.path.exists("logo.png"):
        logo_path = "logo.png"
    if logo_path:
        with open(logo_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        return f'<img src="data:image/png;base64,{b64}" alt="Эмблема отряда" style="width: 90px; height: 90px; border-radius: 50%; border: 2px solid #C59B27; box-shadow: 0 3px 10px rgba(0,0,0,0.35); flex-shrink: 0; object-fit: cover;">'
    return '<div style="font-size: 3rem; flex-shrink: 0;">🎖️</div>'

def find_hero_portrait(keyword, exhibits_list):
    if not keyword:
        return None
    kw = keyword.lower()
    for item in exhibits_list:
        if kw in item.get("title", "").lower():
            img = fix_path(item.get("image"), MEDIA_DIR)
            if img:
                return img
    return None

def render_3d_viewer(glb_path):
    with open(glb_path, "rb") as f:
        glb_b64 = base64.b64encode(f.read()).decode("utf-8")
    html_code = f"""
    <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.4.0/model-viewer.min.js"></script>
    <div style="background: radial-gradient(circle, #38332B 0%, #1C1915 100%); border: 2px solid #C59B27; border-radius: 10px; padding: 8px; text-align: center;">
        <model-viewer
            src="data:model/gltf-binary;base64,{glb_b64}"
            alt="3D-модель экспоната"
            auto-rotate
            camera-controls
            shadow-intensity="1"
            style="width: 100%; height: 400px; background-color: transparent;">
        </model-viewer>
        <div style="color: #E8D8B5; font-family: sans-serif; font-size: 13px; margin-top: 6px;">
            🖱️ Удерживайте левую кнопку мыши (или палец на телефоне), чтобы вращать 3D-экспонат на 360° • Колёсико — приближение
        </div>
    </div>
    """
    components.html(html_code, height=445)

if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False
if "candle_lit" not in st.session_state:
    st.session_state["candle_lit"] = False
if "show_login_box" not in st.session_state:
    st.session_state["show_login_box"] = False
if "selected_exhibit_idx" not in st.session_state:
    st.session_state["selected_exhibit_idx"] = None

if "quiz_idx" not in st.session_state:
    st.session_state["quiz_idx"] = 0
if "quiz_score" not in st.session_state:
    st.session_state["quiz_score"] = 0
if "quiz_answered" not in st.session_state:
    st.session_state["quiz_answered"] = False
if "quiz_last_correct" not in st.session_state:
    st.session_state["quiz_last_correct"] = None
if "quiz_selected_opt" not in st.session_state:
    st.session_state["quiz_selected_opt"] = None

stats = load_json(STATS_FILE, {"candles": 142, "guestbook": []})
exhibits = load_json(DATA_FILE, [])
album_photos = load_json(ALBUM_FILE, [])

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

logo_html = get_logo_html()
st.markdown(f"""
<div class="museum-banner" style="display: flex; align-items: center; gap: 20px; flex-wrap: wrap;">
    {logo_html}
    <div style="flex: 1; min-width: 240px;">
        <h1>Виртуальный музей поискового отряда имени Героя Советского Союза Ф.А. Колтыги</h1>
        <p>Цифровой архив памяти, находок полевых экспедиций и подвигов земляков • г. Ачинск, МБОУ «СШ № 11 имени Героя Советского Союза Ф.А. Колтыги»</p>
    </div>
</div>
""", unsafe_allow_html=True)

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

def show_exhibit_detail(orig_idx):
    if orig_idx < 0 or orig_idx >= len(exhibits):
        st.session_state["selected_exhibit_idx"] = None
        st.rerun()
        return

    item = exhibits[orig_idx]
    if st.button("⬅️ Вернуться ко всем экспонатам зала", key="back_to_hall"):
        st.session_state["selected_exhibit_idx"] = None
        st.rerun()

    with st.container(border=True):
        st.markdown(f"## {item['title']}")
        st.caption(f"📍 Зал музея: **{item['category']}**")
        st.divider()

        col_left, col_right = st.columns([1.1, 1.4])
        with col_left:
            img_path = fix_path(item.get("image"), MEDIA_DIR)
            if img_path:
                st.image(img_path, caption="Основное изображение", use_container_width=True)
            else:
                st.info("🖼️ Основное фото готовится к публикации")

            aud_path = fix_path(item.get("audio"), MEDIA_DIR)
            if aud_path:
                st.markdown("**🎧 Аудиоэкскурсия по экспонату:**")
                st.audio(aud_path)

            vid_path = fix_path(item.get("video"), MEDIA_DIR)
            if vid_path:
                st.markdown("**🎬 Видеоматериал:**")
                st.video(vid_path)

        with col_right:
            st.markdown("### 📜 Краткая справка")
            st.write(item["description"])

            full_story = item.get("full_story", "").strip()
            if full_story:
                st.markdown("### 📖 Подробная история / Биография и боевой путь")
                st.write(full_story)

        # Блок 3D-модели экспоната
        model_path = fix_path(item.get("model_3d"), MEDIA_DIR)
        if model_path:
            st.divider()
            st.markdown("### 🧊 Интерактивная 3D-модель оцифрованного экспоната")
            render_3d_viewer(model_path)

        # Галерея дополнительных фотографий
        extra_imgs = item.get("extra_images", [])
        valid_extra = [fix_path(p, MEDIA_DIR) for p in extra_imgs if fix_path(p, MEDIA_DIR)]
        if valid_extra:
            st.divider()
            st.markdown(f"### 🖼️ Дополнительные фотографии и документы ({len(valid_extra)})")
            for row_i in range(0, len(valid_extra), 3):
                g_cols = st.columns(3)
                for c_i in range(3):
                    if row_i + c_i < len(valid_extra):
                        with g_cols[c_i]:
                            st.image(valid_extra[row_i + c_i], use_container_width=True)

        # Панель расширенного редактирования для администратора
        if is_admin:
            st.divider()
            with st.expander("✏️ Редактировать витрину (добавить подробный текст, доп. фото или 3D-модель .glb)"):
                with st.form(f"detail_edit_form_{orig_idx}"):
                    new_title = st.text_input("Название / ФИО Героя", value=item["title"])
                    cat_index = CATEGORIES.index(item["category"]) if item.get("category") in CATEGORIES else 0
                    new_cat = st.selectbox("Зал музея", CATEGORIES, index=cat_index)
                    new_desc = st.text_area("Краткое описание (для общей карточки)", value=item["description"], height=100)
                    new_full = st.text_area("Подробная биография / расширенная историческая справка", value=item.get("full_story", ""), height=180)

                    new_img = st.file_uploader("Заменить главное фото (JPG, PNG)", type=["jpg", "jpeg", "png"])
                    new_extra = st.file_uploader("Добавить дополнительные фото / архивные документы (можно выбрать несколько)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
                    new_3d = st.file_uploader("Загрузить 3D-модель оцифрованного экспоната (формат .glb)", type=["glb"])
                    new_vid = st.file_uploader("Прикрепить / заменить видео (MP4)", type=["mp4", "mov"])
                    new_aud = st.file_uploader("Прикрепить / заменить аудиогид (MP3, WAV)", type=["mp3", "wav"])

                    if st.form_submit_button("💾 Сохранить все изменения витрины"):
                        exhibits[orig_idx]["title"] = new_title
                        exhibits[orig_idx]["category"] = new_cat
                        exhibits[orig_idx]["description"] = new_desc
                        exhibits[orig_idx]["full_story"] = new_full

                        if new_img is not None:
                            p = f"{MEDIA_DIR}/{new_img.name}"
                            with open(p, "wb") as f:
                                f.write(new_img.getbuffer())
                            exhibits[orig_idx]["image"] = p

                        if new_extra:
                            curr_extra = exhibits[orig_idx].get("extra_images", [])
                            for ex_file in new_extra:
                                p = f"{MEDIA_DIR}/{ex_file.name}"
                                with open(p, "wb") as f:
                                    f.write(ex_file.getbuffer())
                                if p not in curr_extra:
                                    curr_extra.append(p)
                            exhibits[orig_idx]["extra_images"] = curr_extra

                        if new_3d is not None:
                            p = f"{MEDIA_DIR}/{new_3d.name}"
                            with open(p, "wb") as f:
                                f.write(new_3d.getbuffer())
                            exhibits[orig_idx]["model_3d"] = p

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
                        st.success("Витрина обновлена!")
                        st.rerun()

                if valid_extra:
                    if st.button("🧹 Очистить все дополнительные фото", key=f"clr_ex_{orig_idx}"):
                        exhibits[orig_idx]["extra_images"] = []
                        save_json(DATA_FILE, exhibits)
                        st.rerun()

def show_museum():
    if st.session_state["selected_exhibit_idx"] is not None:
        show_exhibit_detail(st.session_state["selected_exhibit_idx"])
        return

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
            or q in item.get("full_story", "").lower()
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
                    if img_path:
                        st.image(img_path, use_container_width=True)
                    else:
                        st.info("🖼️ Фотография / портрет готовится к публикации")
                with col2:
                    badges = []
                    if fix_path(item.get("model_3d"), MEDIA_DIR):
                        badges.append("🧊 3D-модель")
                    if item.get("extra_images"):
                        badges.append(f"🖼️ +{len(item['extra_images'])} фото")
                    if fix_path(item.get("audio"), MEDIA_DIR):
                        badges.append("🎧 Аудиогид")
                    badge_str = (" • " + " | ".join(badges)) if badges else ""

                    st.subheader(item["title"])
                    st.caption(f"📍 Зал: {item['category']}{badge_str}")
                    st.write(item["description"])

                    btn_c1, btn_c2 = st.columns([1.3, 1])
                    with btn_c1:
                        if st.button("🔍 Открыть экспонат подробнее", key=f"open_det_{orig_idx}", use_container_width=True):
                            st.session_state["selected_exhibit_idx"] = orig_idx
                            st.rerun()
                    if is_admin:
                        with btn_c2:
                            if st.button("🗑️ Удалить", key=f"del_{orig_idx}", use_container_width=True):
                                exhibits.pop(orig_idx)
                                save_json(DATA_FILE, exhibits)
                                st.rerun()

def show_quiz():
    st.subheader("🎯 Патриотический квиз «Правнуки Победы: Бессмертие подвига»")
    st.write("Проверьте свои знания о Героях Советского Союза и полных кавалерах ордена Славы города Ачинска и Ачинского района!")

    total_q = len(QUIZ_QUESTIONS)
    curr = st.session_state["quiz_idx"]

    if curr >= total_q:
        score = st.session_state["quiz_score"]
        percent = int((score / total_q) * 100)
        with st.container(border=True):
            st.markdown(f"### 🏆 Квиз завершён! Ваш результат: **{score} из {total_q}** ({percent}%)")
            if percent >= 85:
                st.success("⭐ **Звание: Знаток истории Ачинска и хранитель памяти!** Вы блестяще знаете подвиги наших земляков!")
            elif percent >= 60:
                st.info("🎖️ **Звание: Достойный правнук Победы!** Отличный результат, вы хорошо знакомы с историей родного края.")
            else:
                st.warning("📖 **Звание: Юный исследователь!** Рекомендуем заглянуть в зал «Герои Советского Союза г. Ачинск» и попробовать снова.")
            
            if st.button("🔄 Пройти квиз заново", key="restart_quiz"):
                st.session_state["quiz_idx"] = 0
                st.session_state["quiz_score"] = 0
                st.session_state["quiz_answered"] = False
                st.session_state["quiz_last_correct"] = None
                st.session_state["quiz_selected_opt"] = None
                st.rerun()
        return

    col_p1, col_p2 = st.columns([3, 1])
    with col_p1:
        st.progress(curr / total_q)
    with col_p2:
        st.markdown(f"**Вопрос {curr + 1} из {total_q}** | ⭐ Звёзд: **{st.session_state['quiz_score']}**")

    q_data = QUIZ_QUESTIONS[curr]
    hero_img = find_hero_portrait(q_data.get("hero_keyword"), exhibits)

    with st.container(border=True):
        if hero_img:
            q_col1, q_col2 = st.columns([1, 2.3])
            with q_col1:
                st.image(hero_img, use_container_width=True)
            with q_col2:
                st.markdown(f"#### {q_data['q']}")
        else:
            st.markdown(f"#### {q_data['q']}")

        st.write("")

        if not st.session_state["quiz_answered"]:
            opt_cols1 = st.columns(2)
            opt_cols2 = st.columns(2)
            all_cols = [opt_cols1[0], opt_cols1[1], opt_cols2[0], opt_cols2[1]]
            
            for i, opt_text in enumerate(q_data["options"]):
                with all_cols[i]:
                    if st.button(opt_text, key=f"q_{curr}_opt_{i}", use_container_width=True):
                        st.session_state["quiz_answered"] = True
                        st.session_state["quiz_selected_opt"] = opt_text
                        if opt_text == q_data["answer"]:
                            st.session_state["quiz_score"] += 1
                            st.session_state["quiz_last_correct"] = True
                        else:
                            st.session_state["quiz_last_correct"] = False
                        st.rerun()
        else:
            if st.session_state["quiz_last_correct"]:
                st.success(f"✅ **Верно!** Ваш ответ: *{st.session_state['quiz_selected_opt']}* (+1 звезда)")
            else:
                st.error(f"❌ **Неверно.** Вы выбрали: *{st.session_state['quiz_selected_opt']}*. Правильный ответ: **{q_data['answer']}**")
            
            st.info(f"📜 **Историческая справка:** {q_data['info']}")
            
            btn_label = "Следующий вопрос ➡️" if curr + 1 < total_q else "Посмотреть итоги 🏆"
            if st.button(btn_label, key=f"next_q_{curr}"):
                st.session_state["quiz_idx"] += 1
                st.session_state["quiz_answered"] = False
                st.session_state["quiz_last_correct"] = None
                st.session_state["quiz_selected_opt"] = None
                st.rerun()

def show_photo_album():
    st.subheader("📸 Фотоальбом поискового отряда имени Ф.А. Колтыги")
    st.write("Фотохроника полевых экспедиций «Вахта Памяти», тренировочных сборов, уроков мужества и работы бойцов отряда.")

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
    main_tabs = st.tabs(["🖼️ Залы музея", "🎯 Квиз: Герои Ачинска", "📸 Фотоальбом", "🗺️ География Вахты Памяти", "📖 О нас и отзывы", "➕ Добавить"])
else:
    main_tabs = st.tabs(["🖼️ Залы музея", "🎯 Квиз: Герои Ачинска", "📸 Фотоальбом", "🗺️ География Вахты Памяти", "📖 О нас и отзывы"])

with main_tabs[0]:
    show_museum()

with main_tabs[1]:
    show_quiz()

with main_tabs[2]:
    show_photo_album()

with main_tabs[3]:
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

with main_tabs[4]:
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
    with main_tabs[5]:
        st.subheader("Добавление нового экспоната в цифровой архив")
        with st.form("add_exhibit_form", clear_on_submit=True):
            title = st.text_input("Название экспоната *")
            category = st.selectbox("Выберите зал музея", CATEGORIES)
            description = st.text_area("Краткое описание (для общей карточки в зале) *")
            full_story = st.text_area("Подробная история / биография (откроется при нажатии на экспонат)")
            
            img_file = st.file_uploader("Главное фото экспоната (JPG, PNG)", type=["jpg", "jpeg", "png"])
            extra_files = st.file_uploader("Дополнительные фото и документы (можно выбрать несколько)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
            model_file = st.file_uploader("3D-модель оцифрованного экспоната (формат .glb)", type=["glb"])
            vid_file = st.file_uploader("Видеохроника или видеорассказ (MP4)", type=["mp4", "mov"])
            aud_file = st.file_uploader("Аудиогид (запись голоса, MP3, WAV)", type=["mp3", "wav"])
            
            submitted = st.form_submit_button("Сохранить в архив музея")
            
            if submitted:
                if not title or not description:
                    st.error("Заполните название и краткое описание экспоната!")
                else:
                    new_item = {
                        "title": title,
                        "category": category,
                        "description": description,
                        "full_story": full_story,
                        "image": None,
                        "extra_images": [],
                        "model_3d": None,
                        "video": None,
                        "audio": None
                    }
                    for file_obj, key in [(img_file, "image"), (model_file, "model_3d"), (vid_file, "video"), (aud_file, "audio")]:
                        if file_obj is not None:
                            file_path = f"{MEDIA_DIR}/{file_obj.name}"
                            with open(file_path, "wb") as f:
                                f.write(file_obj.getbuffer())
                            new_item[key] = file_path
                    
                    if extra_files:
                        for ex_f in extra_files:
                            ex_path = f"{MEDIA_DIR}/{ex_f.name}"
                            with open(ex_path, "wb") as f:
                                f.write(ex_f.getbuffer())
                            new_item["extra_images"].append(ex_path)
                    
                    exhibits.append(new_item)
                    save_json(DATA_FILE, exhibits)
                    st.success(f"Экспонат «{title}» добавлен в зал «{category}»!")
