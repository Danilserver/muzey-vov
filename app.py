import streamlit as st
import os
import json

st.set_page_config(
    page_title="Виртуальный музей поискового отряда им. Ф.А. Колтыги",
    page_icon="🎖️",
    layout="wide"
)

# Данные для входа администратора
ADMIN_LOGIN = "admin"
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

# Запоминаем состояние входа в сессии
if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False

# Боковая панель для входа администратора
with st.sidebar:
    st.header("🔐 Вход для администратора")
    if not st.session_state["is_admin"]:
        with st.form("login_form"):
            login_input = st.text_input("Логин")
            password_input = st.text_input("Пароль", type="password")
            login_btn = st.form_submit_button("Войти")
            if login_btn:
                if login_input.strip() == ADMIN_LOGIN and password_input.strip() == ADMIN_PASSWORD:
                    st.session_state["is_admin"] = True
                    st.rerun()
                else:
                    st.error("Неверный логин или пароль")
        st.caption("Режим посетителя: доступен просмотр экспозиции.")
    else:
        st.success("✅ Вы вошли как администратор")
        if st.button("🚪 Выйти"):
            st.session_state["is_admin"] = False
            st.rerun()

is_admin = st.session_state["is_admin"]
exhibits = load_data()

# Шапка музея
st.title("🎖️ Виртуальный музей поискового отряда имени Героя Советского Союза Ф.А. Колтыги")
st.markdown("**Цифровой архив памяти и поисковых экспедиций** | г. Ачинск")

CATEGORIES = [
    "Герои Советского Союза г. Ачинск",
    "Личные вещи солдат и офицеров РККА",
    "Вооружение",
    "Находки поисковых экспедиций",
    "Фронтовые письма и документы",
    "Тыл — фронту"
]

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
                    else:
                        st.info("🖼️ Фотография / портрет не загружены")
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
                    
                    # Полное редактирование карточки ТОЛЬКО для администратора
                    if is_admin:
                        with st.expander("✏️ Редактировать экспонат / прикрепить медиафайлы"):
                            with st.form(f"edit_form_{orig_idx}"):
                                new_title = st.text_input("Название / ФИО Героя", value=item["title"])
                                cat_index = CATEGORIES.index(item["category"]) if item.get("category") in CATEGORIES else 0
                                new_cat = st.selectbox("Зал музея", CATEGORIES, index=cat_index)
                                new_desc = st.text_area("Описание, подвиг, награды", value=item["description"], height=150)
                                
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
                                        
                                    save_data(exhibits)
                                    st.success("Изменения сохранены!")
                                    st.rerun()
                                    
                        if st.button("🗑️ Удалить этот экспонат", key=f"del_{orig_idx}"):
                            exhibits.pop(orig_idx)
                            save_data(exhibits)
                            st.rerun()

if is_admin:
    tab1, tab2 = st.tabs(["🖼️ Залы музея", "➕ Добавить новый экспонат"])
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

# Нижний блок с информацией о поисковом отряде
st.divider()
with st.container(border=True):
    st.subheader("🔎 О поисковом отряде имени Героя Советского Союза Ф.А. Колтыги")
    st.write(
        "Ачинский поисковый отряд имени Героя Советского Союза Фёдора Андреевича Колтыги создан в феврале 2023 года "
        "и действует на базе МБОУ «Средняя школа № 11 имени Ф.А. Колтыги» города Ачинска. "
        "Это единственное поисковое объединение Ачинского округа, которое ведёт работу по увековечению памяти погибших защитников Отечества."
    )
    st.write(
        "В рамках Всероссийской акции «Вахта Памяти» бойцы отряда регулярно выезжают в полевые экспедиции на места кровопролитных боёв "
        "Великой Отечественной войны в Новгородскую область (Демянский район). "
       
    )
