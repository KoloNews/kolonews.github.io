"""Джерела новин сайту «Коло Новин», згруповані за мовою, якою пише видання.
Усі джерела зливаються в одну стрічку і перекладаються на всі 4 мови сайту.

Кожне джерело: (назва, адреса RSS, підказки).
Підказки: "eurasia" — стрічка про Європу/Азію, "us" — про США,
"trad" — китайський текст традиційними ієрогліфами,
"t:<тема>" — тематична стрічка (science, tech, crime, sport, economy, games).
Щоб додати чи прибрати джерело, достатньо змінити цей список.
"""

FEEDS = {
    "uk": [
        ("BBC News Україна", "https://feeds.bbci.co.uk/ukrainian/rss.xml", []),
        ("Укрінформ", "https://www.ukrinform.ua/rss/block-lastnews", []),
        ("Укрінформ", "https://www.ukrinform.ua/rss/rubric-world", []),
        ("Суспільне", "https://suspilne.media/rss/all.rss", []),
        ("Українська правда", "https://www.pravda.com.ua/rss/view_news/", []),
        ("Радіо Свобода", "https://www.radiosvoboda.org/api/zrqiteuuir", []),
        ("DW Україна", "https://rss.dw.com/rdf/rss-ukr-all", []),
        ("LB.ua", "https://lb.ua/rss/ukr/world.xml", []),
        ("Європейська правда", "https://www.eurointegration.com.ua/rss/view_news/", ["eurasia"]),
        # тематичні
        ("Економічна правда", "https://www.epravda.com.ua/rss/", ["t:economy"]),
        ("ITC.ua", "https://itc.ua/feed/", ["t:tech"]),
        ("dev.ua", "https://dev.ua/rss", ["t:tech"]),
        ("Куншт", "https://kunsht.com.ua/feed/", ["t:science"]),
        ("PlayUA", "https://playua.net/feed/", ["t:games"]),
        ("GameInside", "https://gameinside.ua/feed/", ["t:games"]),
    ],
    "en": [
        ("BBC News", "https://feeds.bbci.co.uk/news/world/rss.xml", []),
        ("BBC News", "https://feeds.bbci.co.uk/news/world/europe/rss.xml", ["eurasia"]),
        ("BBC News", "https://feeds.bbci.co.uk/news/world/asia/rss.xml", ["eurasia"]),
        ("BBC News", "https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml", ["us"]),
        ("The Guardian", "https://www.theguardian.com/world/rss", []),
        ("Al Jazeera", "https://www.aljazeera.com/xml/rss/all.xml", []),
        ("DW", "https://rss.dw.com/rdf/rss-en-all", []),
        ("NPR", "https://feeds.npr.org/1004/rss.xml", []),
        ("The Kyiv Independent", "https://kyivindependent.com/news-archive/rss/", []),
        ("South China Morning Post", "https://www.scmp.com/rss/91/feed", ["eurasia"]),
        # тематичні
        ("BBC News", "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml", ["t:science"]),
        ("BBC News", "https://feeds.bbci.co.uk/news/technology/rss.xml", ["t:tech"]),
        ("BBC News", "https://feeds.bbci.co.uk/news/business/rss.xml", ["t:economy"]),
        ("BBC Sport", "https://feeds.bbci.co.uk/sport/rss.xml", ["t:sport"]),
        ("The Guardian", "https://www.theguardian.com/science/rss", ["t:science"]),
        ("The Guardian", "https://www.theguardian.com/technology/rss", ["t:tech"]),
        ("The Guardian", "https://www.theguardian.com/business/rss", ["t:economy"]),
        ("The Guardian", "https://www.theguardian.com/sport/rss", ["t:sport"]),
        ("The Guardian", "https://www.theguardian.com/games/rss", ["t:games"]),
        ("The Guardian", "https://www.theguardian.com/uk/ukcrime/rss", ["t:crime"]),
        ("Phys.org", "https://phys.org/rss-feed/", ["t:science"]),
        ("ScienceDaily", "https://www.sciencedaily.com/rss/top/science.xml", ["t:science"]),
        ("The Verge", "https://www.theverge.com/rss/index.xml", ["t:tech"]),
        ("TechCrunch", "https://techcrunch.com/feed/", ["t:tech"]),
        ("PC Gamer", "https://www.pcgamer.com/rss/", ["t:games"]),
        ("Eurogamer", "https://www.eurogamer.net/feed", ["t:games"]),
        ("IGN", "https://feeds.feedburner.com/ign/all", ["t:games"]),
    ],
    "ru": [
        ("Би-би-си", "https://feeds.bbci.co.uk/russian/rss.xml", []),
        ("DW", "https://rss.dw.com/rdf/rss-ru-all", []),
        ("Медуза", "https://meduza.io/rss/all", []),
        ("Радио Свобода", "https://www.svoboda.org/api/", []),
        ("Новая газета Европа", "https://novayagazeta.eu/feed/rss", []),
        ("RFI", "https://www.rfi.fr/ru/rss", []),
        ("Euronews", "https://ru.euronews.com/rss", []),
        ("Хабр", "https://habr.com/ru/rss/news/", ["t:tech"]),
    ],
    "zh": [
        # BBC 中文 віддає традиційні ієрогліфи — підказка "trad": перекладаємо у спрощені
        ("BBC 中文", "https://feeds.bbci.co.uk/zhongwen/simp/rss.xml", ["trad"]),
        ("德国之声", "https://rss.dw.com/rdf/rss-chi-all", []),
        ("法广 RFI", "https://www.rfi.fr/cn/rss", []),
        ("法广 RFI", "https://www.rfi.fr/cn/中国/rss", []),
        ("法广 RFI", "https://www.rfi.fr/cn/亚洲/rss", ["eurasia"]),
        ("法广 RFI", "https://www.rfi.fr/cn/欧洲/rss", ["eurasia"]),
        ("法广 RFI", "https://www.rfi.fr/cn/美洲/rss", []),
        ("联合国新闻", "https://news.un.org/feed/subscribe/zh/news/all/rss.xml", []),
        ("纽约时报中文网", "https://cn.nytimes.com/rss/", []),
        ("美国之音", "https://www.voachinese.com/api/", []),
        ("自由亚洲电台", "https://www.rfa.org/mandarin/RSS", []),
    ],
}
