"""Ключові слова, за якими новина потрапляє в категорію.

Це регулярні вирази (без урахування регістру). Для української та
російської беремо початок слова, щоб ловити всі відмінки:
"Україн" знайде "Україна", "України", "Україні"...
"""

# Країни-фокуси: США, Китай, Україна, Росія
COUNTRIES = {
    "uk": {
        "us": r"\bСША\b|\bАмерик|американськ|\bТрамп|Вашингтон|Білий дім|Білого дому|Білому домі|Пентагон|Конгрес[іу]? США",
        "cn": r"\bКита[йюїє]|китайськ|\bКНР\b|Пекін|Сі Цзіньпін|Гонконг|Тайван",
        "ua": r"Україн|українськ|\bКи[їє]в|Зеленськ|\bЗСУ\b|Харків|Одес|Дніпр|Львів|Запоріж|Херсон|Донеч|Донбас|(?-i:Сум[иаі]?\b)|Сумщин|Сумськ|Чернігів|Миколаїв|Житомир|Полтав|Вінниц|(?-i:Рівне\b|Рівного|Рівному)|Рівненщин|Хмельниць|Кривий Ріг|Кривому Розі",
        "ru": r"\bРосі|російськ|\bросіян|\bРФ\b|Москв|Кремл|Путін|\bПєсков",
    },
    "ru": {
        "us": r"\bСША\b|\bАмерик|американск|\bТрамп|Вашингтон|Белый дом|Белого дома|Белом доме|Пентагон|Конгресс[еа]? США",
        "cn": r"\bКита[йяею](?!-город)|китайск|\bКНР\b|Пекин|Си Цзиньпин|Гонконг|Тайван",
        "ua": r"Украин|украинск|\bКиев|Зеленск|\bВСУ\b|Харьков|Одесс|Днепр|Львов|Запорож|Херсон|Донец|Донбасс",
        "ru": r"\bРосси|российск|\bроссиян|\bРФ\b|Москв|Кремл|Путин|Песков|Госдум",
    },
    "en": {
        "us": r"(?-i:\bUS\b|\bU\.S\.|\bUSA\b)|United States|\bAmerica|Washington|\bTrump|White House|Pentagon|Congress|Senate|Democrats|Republicans",
        "cn": r"\bChina\b|Chinese|Beijing|Xi Jinping|\bPRC\b|Hong Kong|Taiwan",
        "ua": r"Ukrain|\bKyiv|\bKiev|Zelensky|Kharkiv|Odesa|Dnipro|Lviv|Zaporizhzhia|Kherson|Donbas|Donetsk",
        "ru": r"Russia|Moscow|Kremlin|Putin|Peskov|Lavrov",
    },
    "zh": {
        "us": r"美国|美方|美军|美俄|美中|中美|美乌|美伊|特朗普|川普|白宫|华盛顿|五角大楼",
        "cn": r"中国|中方|中共|北京|习近平|香港|台湾|两岸|大陆|解放军",
        "ua": r"乌克兰|基辅|泽连斯基|俄乌|乌军|哈尔科夫|敖德萨",
        "ru": r"俄罗斯|俄国|俄方|俄军|俄乌|美俄|莫斯科|克里姆林宫|普京|普丁",
    },
}

# Інші країни Європи та Азії (без чотирьох країн-фокусів)
EURASIA = {
    "uk": r"Європ|\bЄС\b|Євросоюз|Німеч|Франц|Британ|Лондон|Париж|Берлін|Польщ|Польськ|Варшав|Італі|Іспані|Нідерланд|Бельгі|Швеці|Норвег|Фінлянд|Данії|Данія|Угорщ|Румун|Молдов|Чехі|Словаччин|Австрі|Швейцар|Греці|Туреччин|Сербі|Литв|Латві|Естоні|Білорус|Лукашенк|Португал|Ірланд|Болгар|Хорват|Словені|\bГрузі[яїю]|Вірмен|Азербайдж|НАТО|Японі|Корей|КНДР|\bІнді[яїю]|Пакистан|\bІран|Ізраїл|(?-i:Газ[иіа]\b)|Сектор[іу]? Газ|ХАМАС|\b(?-i:Сирі[яїю])|Ірак|Саудівськ|Афганістан|В'єтнам|Таїланд|Індонезі|Філіппін|Малайзі|Казахстан|Узбекистан|М'янм|Бангладеш|Сінгапур|Близьк[ий]+ Сход|Ліван",
    "ru": r"Европ|\bЕС\b|Евросоюз|Германи|Франци|Британ|Лондон|Париж|Берлин|Польш|Польск|Варшав|Итали|Испани|Нидерланд|Бельги|Швеци|Норвеги|Финлянд|\bДани[ия]|Венгр|Румын|Молдов|Чехи|Словаки|Австри|Швейцар|Греци|Турци|Серби|Литв|Латви|Эстони|Беларус|Белорус|Лукашенк|Португал|Ирланд|Болгар|Хорват|Словени|\b(?-i:Грузи[яию])|Армени|Азербайдж|НАТО|Япони|\bКоре[яиюй]|КНДР|\bИнди[яию]|Пакистан|\bИран|Израил|(?-i:Газ[аы]\b)|Сектор[ае]? Газ|ХАМАС|\bСири[яиюй]|\bИрак|Саудовск|Афганистан|Вьетнам|Таиланд|Индонези|Филиппин|Малайзи|Казахстан|Узбекистан|Мьянм|Бангладеш|Сингапур|Ближн[ие]+ Восток|Ливан",
    "en": r"Europe|\bEU\b|Brussels|German|France|French|\bUK\b|Britain|British|London|Paris|Berlin|Poland|(?-i:Polish)|Warsaw|\bItal|Spain|Spanish|Netherlands|Dutch|Belgi|Swed|Norw|Finland|Finnish|Denmark|Danish|Hungar|Romania|Moldova|Czech|Slovak|Austria|Switzerland|Swiss|Greece|Greek|Turk|Serbia|Lithuania|Latvia|Estonia|Belarus|Lukashenko|Portugal|Ireland|Irish|Bulgaria|Croatia|Slovenia|Georgia|Armenia|Azerbaijan|NATO|Japan|Korea|\bIndia\b|\bIndian\b|Pakistan|\bIran|Israel|Gaza|Hamas|Syria|\bIraq|Saudi|Afghan|Vietnam|Thailand|Indonesia|Philippine|Malaysia|Kazakhstan|Uzbekistan|Myanmar|Bangladesh|Singapore|Middle East|Lebanon",
    "zh": r"欧洲|欧盟|德国|法国|英国|伦敦|巴黎|柏林|波兰|意大利|西班牙|荷兰|比利时|瑞典|挪威|芬兰|丹麦|匈牙利|罗马尼亚|摩尔多瓦|捷克|斯洛伐克|奥地利|瑞士|希腊|土耳其|塞尔维亚|立陶宛|拉脱维亚|爱沙尼亚|白俄罗斯|卢卡申科|葡萄牙|爱尔兰|保加利亚|克罗地亚|格鲁吉亚|亚美尼亚|阿塞拜疆|北约|日本|韩国|朝鲜|印度|巴基斯坦|伊朗|以色列|加沙|哈马斯|叙利亚|伊拉克|沙特|阿富汗|越南|泰国|印尼|印度尼西亚|菲律宾|马来西亚|哈萨克斯坦|缅甸|孟加拉|新加坡|中东|黎巴嫩",
}

# Службові слова, які не допомагають зрозуміти, що дві новини про одне
STOPWORDS = {
    "uk": set("після через щодо також перед проти буде будуть може можуть було були який яка яке які який його її їхні цього цієї того тому тоді коли який який ніж який який один одна одне вони вона воно нього неї між серед понад близько майже лише навіть заявив заявила заявили каже кажуть новини сьогодні вчора ночі вночі році року роки днів тисяч мільйонів".split()),
    "ru": set("после через также перед против будет будут может могут было были который которая которое которые его её их этого этой того тому тогда когда чем один одна одно они она оно него неё между среди более около почти лишь даже заявил заявила заявили говорит новости сегодня вчера ночью году года годы дней тысяч миллионов".split()),
    "en": set("after with from that this have has had will would could should about into over than they their them there when what which while were been being also says said amid against more most just only some such news year years week weeks first last told".split()),
    "zh": set(),
}


# Теми. Перевіряються англійською (у кожної новини є англійський заголовок — оригінал або переклад).
TOPICS = {
    "science": r"\b(scientists?|researchers?|study (finds|shows|suggests)|NASA|ESA|astronaut|space (station|telescope|mission)|telescope|astronom|asteroid|comet|galaxy|planet|physicist|physics|biolog|genome|DNA|species|fossil|dinosaur|archaeolog|climate (change|scientists)|glacier|volcano|earthquake|vaccine trial|cancer (drug|research|treatment)|clinical trial)",
    "tech": r"\b(AI|A\.I\.|artificial intelligence|chatbot|ChatGPT|OpenAI|Anthropic|Gemini|Copilot|Nvidia|Apple|iPhone|iOS|Android|Google|Microsoft|Meta|Instagram|TikTok|YouTube|Tesla|SpaceX|Starlink|smartphone|laptop|semiconductor|chips?|chipmaker|software|apps?|cyber ?attack|hackers?|data breach|startup|robots?|humanoid|drones? (maker|startup|technology)|quantum computing|tech)\b",
    "crime": r"\b(murder(ed|er)?|homicide|shooting|gunman|stabb(ing|ed)|arrested|arrests?|sentenced|jailed|prison|trial|convicted|fraud|corruption|bribe(ry)?|smuggl|kidnap|robbery|theft|stolen|terror attack|suspects?|detained|prosecutors?|police|gang|cartel|drug traffick)",
    "sport": r"\b(football|soccer|Premier League|Champions League|Europa League|La Liga|Bundesliga|Serie A|NBA|NFL|NHL|MLB|tennis|Wimbledon|ATP|WTA|Olympic|Olympics|boxing|boxer|UFC|MMA|Formula (1|One)|F1|Grand Prix|MotoGP|cricket|rugby|golf|chess|biathlon|hockey|athletics|marathon|cyclist|Tour de France|world cup|striker|midfielder|goalkeeper|head coach|transfer window|match|tournament|championship)",
    "economy": r"\b(economy|economic|economists?|inflation|recession|GDP|interest rates?|central bank|Federal Reserve|Fed|ECB|NBU|stocks?|shares|stock market|Wall Street|Dow|Nasdaq|S&P|oil prices?|gas prices?|budget|taxes|tariffs?|trade (deal|war)|exports?|imports?|banks?|banking|currency|dollar|hryvnia|bitcoin|crypto|cryptocurrency|IMF|World Bank|investors?|investment|profits?|revenue|earnings|layoffs?|jobs report|unemployment|bonds?)\b",
    "games": r"\b(video ?games?|gaming|gamers?|PlayStation|PS5|PS6|Xbox|Nintendo|Switch 2|Steam|esports?|GTA|Grand Theft Auto|Call of Duty|Fortnite|Minecraft|Roblox|game (studio|developer|publisher|trailer|release)|DLC|console)\b",
}
