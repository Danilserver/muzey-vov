import streamlit as st
import os
import json

st.set_page_config(page_title="Виртуальный музей ВОВ", page_icon="🎖️", layout="wide")

# Пароль администратора (можете заменить на свой внутри кавычек)
ADMIN_PASSWORD = "1945"

MEDIA_DIR = "museum_files"
DATA_FILE = "exhibits.json"
os.makedirs(MEDIA_DIR, exist_ok=True)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def fix_path(path):
    if not path:
        return None
    clean_path = path.replace("\\", "/")
    if os.path.exists(clean_path):
        return clean_path
    alt_path = os.path.join(MEDIA_DIR, os.path.basename(clean_path))
    if os.path.exists(alt_path):
        return alt_path
    return None

# Боковая панель для входа администратора
with st.sidebar:
    st.header("🔐 Вход для хранителя музея")
    password_input = st.text_input("Пароль администратора", type="password")
    is_admin = (password_input == ADMIN_PASSWORD)
    if is_admin:
        st.success("Режим администратора включен")
    elif password_input:
        st.error("Неверный пароль")
    else:
        st.info("Вы в режиме посетителя (только просмотр)")

exhibits = load_data()

st.title("🎖️ Виртуальный музей Великой Отечественной войны")
st.markdown("**Проект по технологии: «Технологии прошлого – традиции будущего»** | Цифровой архив памяти")

CATEGORIES = [
    "Герои нашей семьи и края",
    "Фронтовые письма и документы",
    "Награды и личные вещи солдат",
    "Военная техника и связь",
    "Тыл — фронту"
]

# Функция для отображения залов музея
def show_museum():
    selected_cat = st.selectbox("Выберите зал для просмотра:", ["Все залы"] + CATEGORIES)
    
    filtered_exhibits = [
        (idx, item) for idx, item in enumerate(exhibits)
        if selected_cat == "Все залы" or item.get("category") == selected_cat
    ]

    if not filtered_exhibits:
        st.info("В этом зале пока нет экспонатов.")
    else:
        for orig_idx, item in reversed(filtered_exhibits):
            with st.container(border=True):
                col1, col2 = st.columns(2)
                with col1:
                    img_path = fix_path(item.get("image"))
                    vid_path = fix_path(item.get("video"))
                    if img_path:
                        st.image(img_path, use_container_width=True)
                    if vid_path:
                        st.video(vid_path)
                with col2:
                    st.subheader(item["title"])
                    st.caption(f"📍 Зал: {item['category']}")
                    st.write(item["description"])
                    aud_path = fix_path(item.get("audio"))
                    if aud_path:
                        st.markdown("**🎧 Аудиоэкскурсия:**")
                        st.audio(aud_path)
                    
                    # Кнопка удаления видна ТОЛЬКО администратору
                    if is_admin:
                        if st.button("🗑️ Удалить экспонат", key=f"del_{orig_idx}"):
                            exhibits.pop(orig_idx)
                            save_data(exhibits)
                            st.rerun()

# Разделение интерфейса: админ видит 2 вкладки, посетитель — только экспозицию
if is_admin:
    tab1, tab2 = st.tabs(["🖼️ Залы музея", "➕ Добавить экспонат"])
    with tab1:
        show_museum()
    with tab2:
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
                    save_data(exhibits)
                    st.success(f"Экспонат «{title}» добавлен в зал «{category}»!")
else:
    show_museum()
