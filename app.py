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
QUIZ_DIR = "quiz_files"
DATA_FILE = "exhibits.json"
ALBUM_FILE = "album.json"
STATS_FILE = "site_stats.json"

os.makedirs(MEDIA_DIR, exist_ok=True)
os.makedirs(ALBUM_DIR, exist_ok=True)
os.makedirs(QUIZ_DIR, exist_ok=True)

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

# --- База вопросов квиза «Правнуки Победы: Бессмертие подвига» ---
QUIZ_QUESTIONS = [
    {
        "q": "Сколько стел в честь героев-земляков установлено на Аллее Героев в Парке Победы города Ачинска?",
        "options": ["18", "19", "20", "21"],
        "answer": "20",
        "hero_keyword": None,
        "info": "На Аллее Героев в Парке Победы г. Ачинска установлено 20 памятных стел: 18 в честь Героев Советского Союза и 2 в честь полных кавалеров ордена Славы (Г. Д. Садовникова и А. И. Чесных)."
    },
    {
        "q": "В каком роде войск во время Великой Отечественной войны служили Герои Советского Союза ачинцы Павел Семёнович Волков, Андрей Борисович Данилов, Фёдор Андреевич Колтыга и Валентин Ипполитович Манкевич?",
        "options": ["Кавалерия", "Стрелковые войска", "Инженерные войска", "Артиллерия"],
        "answer": "Артиллерия",
        "hero_keyword": "Колтыга",
        "info": "Все четверо прославленных ачинцев — П. С. Волков, А. Б. Данилов, Ф. А. Колтыга и В. И. Манкевич — были артиллеристами, проявившими исключительное мужество в боях с танками и пехотой противника."
    },
    {
        "q": "Какое учебное заведение в Ачинске стало Alma Mater для Героев Советского Союза Павла Семёновича Волкова и Василия Иннокентьевича Давыдова?",
        "options": ["Ачинское педагогическое училище", "Ачинский сельскохозяйственный техникум", "Ачинский техникум советской торговли", "Ачинский индустриальный техникум трудовых резервов"],
        "answer": "Ачинское педагогическое училище",
        "hero_keyword": None,
        "info": "Павел Семёнович Волков и Василий Иннокентьевич Давыдов до войны учились в Ачинском педагогическом училище."
    },
    {
        "q": "Какая военная специальность была у Михаила Лаврентьевича Ивченко и Михаила Ильича Суркова во время Великой Отечественной войны?",
        "options": ["Стрелок", "Пулемётчик", "Снайпер", "Связист"],
        "answer": "Снайпер",
        "hero_keyword": "Ивченко",
        "info": "Оба наших земляка были прославленными снайперами. М. Л. Ивченко сражался в Заполярье (закрыл телом амбразуру дзота), а М. И. Сурков стал одним из самых результативных снайперов войны."
    },
    {
        "q": "Михаил Андреевич Хлебников, Владимир Степанович Михайлов, Дмитрий Константинович Квитович, Андрей Васильевич Водянников и Александр Иосифович Парадович удостоены звания Героя Советского Союза за проявленное мужество в одной из самых масштабных операций ВОВ (24 августа – 23 декабря 1943 года). О какой операции идёт речь?",
        "options": ["Курская битва", "Сталинградская битва", "Форсирование Западной Двины", "Битва за Днепр"],
        "answer": "Битва за Днепр",
        "hero_keyword": None,
        "info": "Битва за Днепр (август — декабрь 1943 г.) стала одной из крупнейших операций в истории, за форсирование реки и удержание плацдармов звания Героя удостоились пятеро наших земляков."
    },
    {
        "q": "Одна из центральных улиц Ачинска с 1957 по 1980 годы носила название Абаканской, а к 35-летию Победы была переименована в честь Героя Советского Союза, отличившегося при форсировании рек Западный Буг, Сан, Висла и взятии города Сандомир. Чьё имя носит улица?",
        "options": [
            "улица имени Героя Советского Союза Назарова Александра Петровича",
            "проспект имени Героя Советского Союза Лапенкова Ивана Адамовича",
            "улица имени Героя Советского Союза Манкевича Валентина Ипполитовича",
            "улица имени Героя Советского Союза Лебеденко Никиты Федотовича"
        ],
        "answer": "проспект имени Героя Советского Союза Лапенкова Ивана Адамовича",
        "hero_keyword": "Лапенков",
        "info": "В 1980 году бывшая улица Абаканская была переименована в проспект имени Героя Советского Союза Ивана Адамовича Лапенкова."
    },
    {
        "q": "19 августа 1939 года Герой Советского Союза Никита Федотович Лебеденко был назначен командиром дивизии, сформированной в Ачинске, с которой в июле 1941 года вступил в Смоленское сражение. О каком военном формировании идёт речь?",
        "options": ["1-я мотострелковая дивизия", "2-я авиационная дивизия особого назначения", "91-я стрелковая дивизия", "50-я стрелковая дивизия"],
        "answer": "91-я стрелковая дивизия",
        "hero_keyword": "Лебеденко",
        "info": "91-я стрелковая дивизия была сформирована в Ачинске в 1939 году и под командованием Н. Ф. Лебеденко героически сражалась в Смоленском сражении и под Вязьмой."
    },
    {
        "q": "Один из Героев Советского Союза с Аллеи Героев Ачинска вспоминал в мемуарах, как мальчишкой впервые увидел приземлившийся на окраине Ачинска самолёт и прокатился в его кабине по полю. Как зовут этого прославленного лётчика-аса?",
        "options": ["Олейников Василий Семёнович", "Кожевников Анатолий Леонидович", "Голубев Георгий Гордеевич", "Никифоров Константин Степанович"],
        "answer": "Голубев Георгий Гордеевич",
        "hero_keyword": "Голубев",
        "info": "Георгий Гордеевич Голубев — воспитанник Ачинского аэроклуба, знаменитый лётчик-истребитель, постоянный ведомый А. И. Покрышкина."
    },
    {
        "q": "30 апреля 1945 года наш земляк, командир 1-го стрелкового батальона 674-го полка 150-й дивизии, вместе с батальонами Неустроева и Самсонова участвовал в штурме рейхстага и водружении над ним Знамени Победы. О ком идёт речь?",
        "options": [
            "Герой Советского Союза Кантария Мелитон Варламович",
            "Герой Советского Союза Егоров Михаил Алексеевич",
            "Герой Советского Союза Давыдов Василий Иннокентьевич",
            "Герой Советского Союза Шатилов Василий Митрофанович"
        ],
        "answer": "Герой Советского Союза Давыдов Василий Иннокентьевич",
        "hero_keyword": None,
        "info": "Капитан Василий Иннокентьевич Давыдов, выпускник Ачинского педучилища, командовал 1-м стрелковым батальоном 674-го полка при штурме рейхстага."
    },
    {
        "q": "Какое значение имели действия старшего лейтенанта Дмитрия Константиновича Квитовича 16 октября 1943 года во время битвы за Днепр у посёлка Радуль?",
        "options": [
            "Поддержание боевого духа всей команды в критический момент",
            "Создание важного плацдарма на западном берегу Днепра, что обеспечило успешную переправу всего батальона",
            "Организация эвакуации гражданского населения на восточный берег",
            "Проведение разведки боем"
        ],
        "answer": "Создание важного плацдарма на западном берегу Днепра, что обеспечило успешную переправу всего батальона",
        "hero_keyword": None,
        "info": "Переправившись на плотике с пятью бойцами, Д. К. Квитович захватил и удержал плацдарм на правом берегу Днепра, обеспечив переправу всего батальона."
    },
    {
        "q": "Акция «Бессмертный полк» впервые прошла 9 мая 2012 года в Томске. В составе инициативной группы был внук Героя Советского Союза, чьё имя связано с Ачинском. Как зовут внука нашего прославленного земляка?",
        "options": ["Сергей Колотовкин", "Игорь Дмитриев", "Геннадий Иванов", "Сергей Лапенков"],
        "answer": "Сергей Лапенков",
        "hero_keyword": "Лапенков",
        "info": "Одним из основателей движения «Бессмертный полк» стал журналист Сергей Лапенков — внук Героя Советского Союза Ивана Адамовича Лапенкова."
    },
    {
        "q": "Перед вами портрет нашего земляка, Героя Советского Союза, который 24–25 сентября 1943 года первым с пулемётом перешёл вброд старое русло Днепра на Киевском направлении, заменил раненого командира взвода и лично отбил 13 контратак противника. Назовите имя Героя:",
        "options": ["Михайлов Владимир Степанович", "Квитович Дмитрий Константинович", "Солонченко Владимир Данилович", "Хлебников Михаил Андреевич"],
        "answer": "Солонченко Владимир Данилович",
        "hero_keyword": "Солонченко",
        "info": "Старший сержант Владимир Данилович Солонченко в боях за Днепр уничтожил более 170 гитлеровцев и отбил 13 вражеских контратак."
    },
    {
        "q": "Каким героическим поступком Михаил Лаврентьевич Ивченко спас батальон от больших потерь в первый день Петсамо-Киркенесской наступательной операции (7 октября 1944 года)?",
        "options": [
            "Подавил вражеский дзот огнём из своего оружия",
            "Закрыл амбразуру дзота своим телом",
            "Вывел батальон из окружения под вражеским огнём",
            "Организовал контратаку, отвлекая огонь на себя"
        ],
        "answer": "Закрыл амбразуру дзота своим телом",
        "hero_keyword": "Ивченко",
        "info": "Ефрейтор М. Л. Ивченко повторил подвиг Александра Матросова в Заполярье, закрыв своим телом амбразуру вражеского дзота и обеспечив батальону прорыв обороны."
    },
    {
        "q": "8 мая 2025 года на Аллее Героев парка Победы Ачинска открыта стела полному кавалеру ордена Славы Григорию Даниловичу Садовникову. В каком населённом пункте Ачинского района в 2015 году открыта мемориальная доска в его честь?",
        "options": ["Ястребово", "Лапшиха", "Тарутино", "Тимонино"],
        "answer": "Лапшиха",
        "hero_keyword": None,
        "info": "Мемориальная доска в память о полном кавалере ордена Славы Г. Д. Садовникове торжественно открыта в селе Лапшиха Ачинского района."
    },
    {
        "q": "Какой подвиг совершил Герой Советского Союза гвардии капитан Валентин Ипполитович Манкевич в августе 1944 года на Сандомирском плацдарме?",
        "options": [
            "Организовал массовое спасение раненых солдат в бою",
            "Спас детей из горящего здания",
            "Вызвал огонь вражеского дивизиона на себя",
            "Доставил важную разведывательную информацию через линию фронта"
        ],
        "answer": "Вызвал огонь вражеского дивизиона на себя",
        "hero_keyword": "Манкевич",
        "info": "Оказавшись в окружении на наблюдательном пункте, В. И. Манкевич передал по рации координаты своей позиции и вызвал огонь советской артиллерии на себя."
    },
    {
        "q": "Герой Советского Союза Георгий Гордеевич Голубев сражался в паре с легендарным лётчиком-асом, трижды Героем Советского Союза, известным под позывным «Сотый». Кто из советских асов имел позывной «Сотый»?",
        "options": ["Иван Никитович Кожедуб", "Александр Иванович Покрышкин", "Кирилл Алексеевич Евстигнеев", "Алексей Петрович Маресьев"],
        "answer": "Александр Иванович Покрышкин",
        "hero_keyword": "Голубев",
        "info": "Позывной «Сотый» принадлежал маршалу авиации, трижды Герою Советского Союза Александру Ивановичу Покрышкину, ведомым которого летал ачинец Г. Г. Голубев."
    },
    {
        "q": "Перед вами портрет Героя Советского Союза, командира батареи 530-го истребительно-противотанкового артиллерийского полка, чья батарея 29–30 апреля 1945 года 40 часов удерживала рубеж и отразила 36 яростных атак врага, а сам комбат сражался до последнего патрона. Как зовут этого Героя?",
        "options": ["Данилов Андрей Борисович", "Волков Павел Семёнович", "Колтыга Фёдор Андреевич", "Манкевич Валентин Ипполитович"],
        "answer": "Волков Павел Семёнович",
        "hero_keyword": "Волков",
        "info": "Капитан Павел Семёнович Волков геройски погиб в конце апреля 1945 года на территории Германии, сражаясь в окружении до последнего патрона."
    },
    {
        "q": "Где установлен памятник Герою Советского Союза Михаилу Лаврентьевичу Ивченко?",
        "options": ["В Красноярске", "В Ачинске", "В селе Лапшиха Ачинского района", "В деревне Тимонино Ачинского района"],
        "answer": "В деревне Тимонино Ачинского района",
        "hero_keyword": "Ивченко",
        "info": "Памятник Герою Советского Союза М. Л. Ивченко установлен на его малой родине — в деревне Тимонино Ачинского района."
    },
    {
        "q": "В Красноярске в микрорайоне «Покровский» открыли памятник Герою Советского Союза Андрею Васильевичу Водянникову при активном участии сотрудников и ветеранов городской полиции. Почему они проявили особое внимание?",
        "options": [
            "Для обеспечения безопасности мероприятия",
            "Памятник посвящён Герою, который до войны был участковым милиционером",
            "Они сами организовали данное мероприятие",
            "Это было поручение городских властей"
        ],
        "answer": "Памятник посвящён Герою, который до войны был участковым милиционером",
        "hero_keyword": None,
        "info": "До ухода на фронт Андрей Васильевич Водянников служил участковым уполномоченным милиции в Красноярске."
    },
    {
        "q": "Назовите участника Великой Отечественной войны, командира сапёрного батальона, который под огнём переплыл реку Айвиексте в Латвии, зажав зубами телефонный кабель, и был награждён орденом Славы II степени:",
        "options": [
            "Герой Советского Союза Михаил Лаврентьевич Ивченко",
            "Герой Великой Отечественной войны Михаил Ильич Сурков",
            "Полный кавалер ордена Славы Григорий Данилович Садовников",
            "Полный кавалер ордена Славы Александр Иванович Честных"
        ],
        "answer": "Полный кавалер ордена Славы Александр Иванович Честных",
        "hero_keyword": None,
        "info": "Этот подвиг при форсировании реки Айвиексте совершил полный кавалер ордена Славы Александр Иванович Честных."
    },
    {
        "q": "Как называется масштабная битва лета 1943 года (операция вермахта «Цитадель»), в которой прославились герои-ачинцы Фёдор Андреевич Колтыга, Владимир Степанович Михайлов, Абрам Самуилович Сапожников и Семён Исакович Чубуков?",
        "options": ["Курская битва", "Сталинградская битва", "Форсирование Западной Двины", "Битва за Днепр"],
        "answer": "Курская битва",
        "hero_keyword": "Сапожников",
        "info": "В Курской битве (июль — август 1943 г.) проявили героизм сразу несколько наших земляков: артиллеристы Ф. А. Колтыга, А. С. Сапожников, А. Б. Данилов, танкист С. И. Чубуков и стрелок В. С. Михайлов."
    },
    {
        "q": "Один из наших героических земляков по праву считается самым результативным снайпером Великой Отечественной войны — на его официальном счету 702 уничтоженных солдата и офицера противника. Назовите имя Героя:",
        "options": ["Ивченко Михаил Лаврентьевич", "Охлопков Фёдор Матвеевич", "Сурков Михаил Ильич", "Кульбертинов Иван Николаевич"],
        "answer": "Сурков Михаил Ильич",
        "hero_keyword": "Сурков",
        "info": "Сибирский охотник Михаил Ильич Сурков уничтожил из снайперской винтовки 702 гитлеровца; о нём в 1942 году был снят фронтовой киножурнал."
    },
    {
        "q": "На фотографии Герой Советского Союза — артиллерист, который 7 августа 1943 года во время Белгородско-Харьковской операции лично уничтожил 14 гитлеровцев, 6 взял в плен, а огнём орудия подбил 2 танка, 2 самоходные пушки и 32 автомашины. Назовите имя Героя:",
        "options": ["Данилов Андрей Борисович", "Колтыга Фёдор Андреевич", "Волков Павел Семёнович", "Манкевич Валентин Ипполитович"],
        "answer": "Колтыга Фёдор Андреевич",
        "hero_keyword": "Колтыга",
        "info": "Этот выдающийся подвиг в ходе Белгородско-Харьковской операции совершил наш земляк Фёдор Андреевич Колтыга, имя которого носит школа № 11 и наш поисковый отряд."
    },
    {
        "q": "Григорий Данилович Садовников и Александр Иванович Чесных являются полными кавалерами ордена Славы. Сколько степеней включает орден Славы?",
        "options": ["Одну", "Две", "Три", "Четыре"],
        "answer": "Три",
        "hero_keyword": None,
        "info": "Орден Славы имеет три степени (I, II и III степени), награждение производилось последовательно от низшей III степени к высшей I степени."
    },
    {
        "q": "Назовите имя Героя Советского Союза, выпускника ачинской школы № 2, который пал смертью храбрых 24 июня 1944 года в ходе операции «Багратион» при форсировании реки Западная Двина:",
        "options": ["Назаров Александр Петрович", "Михайлов Владимир Степанович", "Солонченко Владимир Данилович", "Хлебников Михаил Андреевич"],
        "answer": "Назаров Александр Петрович",
        "hero_keyword": "Назаров",
        "info": "Младший лейтенант Александр Петрович Назаров погиб 24 июня 1944 года в бою на плацдарме на реке Западная Двина."
    },
    {
        "q": "Майор, агитатор политотдела 43-й армии 1-го Прибалтийского фронта, который при форсировании Западной Двины первым бросился вплавь со словами «Коммунисты, вперёд!», поднял за собой батальон и погиб от вражеской пули. Назовите имя Героя:",
        "options": ["Назаров Александр Петрович", "Солонченко Владимир Данилович", "Михайлов Владимир Степанович", "Хлебников Михаил Андреевич"],
        "answer": "Михайлов Владимир Степанович",
        "hero_keyword": "Михайлов",
        "info": "Майор Владимир Степанович Михайлов совершил этот подвиг при форсировании Западной Двины в июне 1944 года."
    },
    {
        "q": "Майор, командир 262-го танкового батальона 70-й танковой бригады, чей батальон в Курской битве вклинился на 25 км в тыл врага, освободил 7 деревень и уничтожил более 160 солдат и 11 орудий противника. Кто этот отважный командир?",
        "options": ["Басков Михаил Николаевич", "Чубуков Семён Исакович", "Чапаев Николай Сергеевич", "Назаренко Александр Константинович"],
        "answer": "Чубуков Семён Исакович",
        "hero_keyword": "Чубуков",
        "info": "Командир 262-го танкового батальона майор Семён Исакович Чубуков удостоен звания Героя Советского Союза за умелое руководство танковым рейдом в Курской битве."
    },
    {
        "q": "Гвардии сержант, помощник командира взвода 41-й гвардейской отдельной разведроты, который 24 октября 1943 года при форсировании Днепра южнее Днепропетровска первым прорвал проволочные заграждения и заменил погибшего офицера. Как звали Героя?",
        "options": ["Михайлов Владимир Степанович", "Квитович Дмитрий Константинович", "Хлебников Михаил Андреевич", "Парадович Александр Иосифович"],
        "answer": "Парадович Александр Иосифович",
        "hero_keyword": "Парадович",
        "info": "Гвардии сержант Александр Иосифович Парадович проявил героизм при форсировании Днепра и прошёл с боями до Польши."
    },
    {
        "q": "Сколько всего бойцов из Ачинска и Ачинского района, призванных Ачинским военкоматом, удостоились высокого звания Героя Советского Союза в годы Великой Отечественной войны?",
        "options": ["16", "17", "18", "21"],
        "answer": "18",
        "hero_keyword": None,
        "info": "18 земляков из Ачинска и Ачинского района были удостоены звания Героя Советского Союза (ещё 2 земляка стали полными кавалерами ордена Славы)."
    }
]

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

def find_hero_portrait(keyword, exhibits_list):
    """Ищет загруженный портрет Героя в базе музея по фамилии"""
    if not keyword:
        return None
    kw = keyword.lower()
    for item in exhibits_list:
        if kw in item.get("title", "").lower():
            img = fix_path(item.get("image"), MEDIA_DIR)
            if img:
                return img
    return None

if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False
if "candle_lit" not in st.session_state:
    st.session_state["candle_lit"] = False
if "show_login_box" not in st.session_state:
    st.session_state["show_login_box"] = False

# Состояния для интерактивного квиза
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
        # Если в музее загружен портрет этого Героя — показываем вопрос в две колонки с портретом
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
                    # Варианты ответов выводятся чистым текстом без цифр-номеров
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
