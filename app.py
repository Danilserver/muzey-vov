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

# Компактная торжественная шапка музея с фирменной эмблемой поискового отряда
st.markdown("""
<div class="museum-banner" style="display: flex; align-items: center; gap: 20px; flex-wrap: wrap;">
    <img src="data:image/png;base64,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" alt="Эмблема поискового отряда" style="width: 92px; height: 92px; border-radius: 50%; border: 2px solid #C59B27; box-shadow: 0 3px 10px rgba(0,0,0,0.35); flex-shrink: 0; object-fit: cover;">
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
