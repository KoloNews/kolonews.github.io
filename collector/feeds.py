"""Джерела новин сайту «Коло Новин», згруповані за мовою, якою пише видання.
Усі джерела зливаються в одну стрічку і перекладаються на всі 4 мови сайту.

Кожне джерело: (назва, адреса RSS, підказки).
Підказки: "eurasia" — стрічка про Європу/Азію, "us" — про США,
"trad" — китайський текст традиційними ієрогліфами.
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
    ],
    "ru": [
        ("Би-би-си", "https://feeds.bbci.co.uk/russian/rss.xml", []),
        ("DW", "https://rss.dw.com/rdf/rss-ru-all", []),
        ("Медуза", "https://meduza.io/rss/all", []),
        ("Радио Свобода", "https://www.svoboda.org/api/", []),
        ("Новая газета Европа", "https://novayagazeta.eu/feed/rss", []),
        ("RFI", "https://www.rfi.fr/ru/rss", []),
        ("Euronews", "https://ru.euronews.com/rss", []),
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
