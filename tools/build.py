"""Build the website (all languages) into site/: one file per page, site/<lang>/<slug>.html, served as /<lang>/<slug>."""
import json, re, html, pathlib, sys, urllib.parse, datetime
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from blocks import blocks_of, abridge, faq_pairs, pic_anchors, place_pics
import diagrams

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / 'site'
ASSETS = ROOT / 'tools' / 'assets'
esc = html.escape

LANGS = ['en', 'de', 'pl', 'es', 'it', 'fr', 'pt', 'ru', 'zh', 'hi', 'ar', 'bn', 'ur', 'id',
         'ja', 'tr', 'vi', 'ko', 'fa', 'mr', 'te', 'ta', 'sw', 'th', 'nl', 'uk', 'tl', 'pa', 'gu']   # English is the source; other languages fill gaps with AI translations
FULL_AI = {'fr', 'pt', 'ru', 'zh', 'hi', 'ar', 'bn', 'ur', 'id',
           'ja', 'tr', 'vi', 'ko', 'fa', 'mr', 'te', 'ta', 'sw', 'th', 'nl', 'uk', 'tl', 'pa', 'gu'}   # no original site: every page is AI-translated, marked once in the language picker
LANG_NAME = {'en': 'English', 'de': 'Deutsch', 'pl': 'Polski', 'es': 'Español', 'it': 'Italiano',
             'fr': 'Français', 'pt': 'Português', 'ru': 'Русский', 'zh': '中文', 'hi': 'हिन्दी',
             'ar': 'العربية', 'bn': 'বাংলা', 'ur': 'اردو', 'id': 'Bahasa Indonesia',
             'ja': '日本語', 'tr': 'Türkçe', 'vi': 'Tiếng Việt', 'ko': '한국어', 'fa': 'فارسی',
             'mr': 'मराठी', 'te': 'తెలుగు', 'ta': 'தமிழ்', 'sw': 'Kiswahili', 'th': 'ไทย',
             'nl': 'Nederlands', 'uk': 'Українська', 'tl': 'Filipino', 'pa': 'ਪੰਜਾਬੀ', 'gu': 'ગુજરાતી'}
RTL = {'ar', 'ur', 'fa'}   # written right to left: pages get dir="rtl" and the CSS mirrors
DIR = lambda l: 'rtl' if l in RTL else 'ltr'
KINDS = {'home': 'home', 'basic-faq': 'faq', 'full-faq': 'faq'}  # by English slug, default 'doc'
AI_MARK = ' (AI)'

# Per language: (slug, English slug or None for pages only that language has, menu label, original slug or None if AI-translated).
# Order follows the English menu; language-only pages go last.
SITE = {
 'en': [(s, s, l, s) for s, l in [
  ('home', 'Home'), ('manifesto', 'Manifesto'), ('basic-faq', 'Basic FAQ'), ('full-faq', 'Full FAQ'),
  ('criticism-of-different-pro-life-ideologies', 'Criticism of pro-life ideologies'),
  ('principles-of-the-movement', 'Principles of the movement'), ('suffering-in-detail', 'Suffering in detail'),
  ('cosmic-extinction', 'Cosmic Extinction'), ('history', 'History'), ('join-us', 'Join us'),
  ('social-media-channels', 'Social Media Channels'), ('contact', 'Contact'), ('donate', 'Donate')]],
 'de': [
  ('home', 'home', 'Home', 'home'), ('manifest', 'manifesto', 'Manifest', 'manifest'),
  ('basis-faq', 'basic-faq', 'Basis-FAQ', 'basis-faq'), ('vollstaendiges-faq', 'full-faq', 'Vollständiges FAQ', 'vollständiges-faq'),
  ('kritik-an-pro-life-ideologien', 'criticism-of-different-pro-life-ideologies', 'Kritik an Pro-Life-Ideologien', None),
  ('die-prinzipien-unserer-bewegung', 'principles-of-the-movement', 'Die Prinzipien unserer Bewegung', 'die-prinzipien-unserer-bewegung'),
  ('leid-im-detail', 'suffering-in-detail', 'Leid im Detail', 'leid-im-detail'),
  ('kosmische-extinction', 'cosmic-extinction', 'Kosmische Extinction', None),
  ('geschichte', 'history', 'Geschichte', 'geschichte'), ('aktiv-werden', 'join-us', 'Aktiv werden', 'aktiv-werden'),
  ('social-media', 'social-media-channels', 'Social-Media-Kanäle', None), ('kontakt', 'contact', 'Kontakt', 'kontakt'),
  ('spenden', 'donate', 'Spenden', None), ('ressourcen', None, 'Ressourcen', 'resourcen')],
 'pl': [
  ('home', 'home', 'Home', 'home'), ('komunikat', 'manifesto', 'Komunikat', 'komunikat'),
  ('basic-faq', 'basic-faq', 'Basic FAQ', 'basic-faq'), ('full-faq', 'full-faq', 'Full FAQ', 'full-faq'),
  ('krytyka-ideologii-pro-life', 'criticism-of-different-pro-life-ideologies', 'Krytyka ideologii pro-life', None),
  ('zasady-ruchu', 'principles-of-the-movement', 'Zasady ruchu', 'zasady-ruchu'),
  ('znaczenie-cierpienia', 'suffering-in-detail', 'Znaczenie cierpienia', 'znaczenie-cierpienia'),
  ('kosmiczne-wyginiecie', 'cosmic-extinction', 'Kosmiczne wyginięcie', None),
  ('historia', 'history', 'Historia', 'historia'), ('z-nami', 'join-us', 'Z nami', 'z-nami'),
  ('profile-aktywistyczne', 'social-media-channels', 'Profile aktywistyczne', 'profile-aktywistyczne'),
  ('kontakt', 'contact', 'Kontakt', 'kontakt'), ('darowizny', 'donate', 'Przekaż darowiznę', None),
  ('zasoby', None, 'Zasoby', 'zasoby')],
 'es': [
  ('home', 'home', 'Página inicial', 'página-inicial'), ('manifiesto', 'manifesto', 'Manifiesto', 'manifiesto'),
  ('pmf-basicas', 'basic-faq', 'PMF básicas', 'pmf-básicas'), ('pmf-completas', 'full-faq', 'PMF completas', 'pmf-completas'),
  ('critica-ideologias-provida', 'criticism-of-different-pro-life-ideologies', 'Crítica de las ideologías provida', None),
  ('principios-del-movimiento', 'principles-of-the-movement', 'Principios del movimiento', None),
  ('sufrimiento-en-detalle', 'suffering-in-detail', 'El sufrimiento en detalle', None),
  ('extincion-cosmica', 'cosmic-extinction', 'Extinción cósmica', None),
  ('historia', 'history', 'Historia', 'historia'), ('equipo', 'join-us', 'Equipo', 'equipo'),
  ('redes-sociales', 'social-media-channels', 'Redes sociales', None), ('contacto', 'contact', 'Contacto', 'contacto'),
  ('donar', 'donate', 'Donar', None), ('recursos', None, 'Recursos', 'recursos'), ('mapa-del-sitio', None, 'Mapa del sitio', 'mapa-del-sitio')],
 'it': [
  ('home', 'home', 'Home', 'home'), ('manifesto', 'manifesto', 'Manifesto', 'manifesto'),
  ('faq-di-base', 'basic-faq', 'FAQ di base', 'faq-di-base'), ('faq-completo', 'full-faq', 'FAQ completo', 'faq-completo'),
  ('critica-ideologie-pro-vita', 'criticism-of-different-pro-life-ideologies', 'Critica delle ideologie pro-vita', None),
  ('principi-del-movimento', 'principles-of-the-movement', 'Principi del movimento', 'principi-del-movimento'),
  ('la-sofferenza-nei-dettagli', 'suffering-in-detail', 'La sofferenza nei dettagli', 'la-sofferenza-nei-dettagli'),
  ('estinzione-cosmica', 'cosmic-extinction', 'Estinzione cosmica', None),
  ('storia', 'history', 'Storia', 'storia'), ('unisciti-a-noi', 'join-us', 'Unisciti a noi', 'unisciti-a-noi'),
  ('canali-social', 'social-media-channels', 'Canali social', None), ('contatti', 'contact', 'Contatti', None),
  ('donazioni', 'donate', 'Donazioni', 'donazioni')],
}
# Menu labels of the fully AI-translated languages, in English menu order (slugs stay English).
AI_MENU = {
 'fr': ['Accueil', 'Manifeste', 'FAQ de base', 'FAQ complète', 'Critique des idéologies pro-vie', 'Principes du mouvement',
        'La souffrance en détail', 'Extinction cosmique', 'Histoire', 'Nous rejoindre', 'Réseaux sociaux', 'Contact', 'Faire un don'],
 'pt': ['Início', 'Manifesto', 'FAQ básico', 'FAQ completo', 'Crítica das ideologias pró-vida', 'Princípios do movimento',
        'O sofrimento em detalhe', 'Extinção cósmica', 'História', 'Junte-se a nós', 'Redes sociais', 'Contato', 'Doar'],
 'ru': ['Главная', 'Манифест', 'Основные вопросы', 'Все вопросы', 'Критика идеологий pro-life', 'Принципы движения',
        'Страдание в деталях', 'Космическое вымирание', 'История', 'Присоединяйтесь', 'Соцсети', 'Контакты', 'Пожертвовать'],
 'zh': ['首页', '宣言', '基础问答', '完整问答', '批判各种 pro-life 意识形态', '运动原则', '苦难详述', '宇宙灭绝', '历史',
        '加入我们', '社交媒体', '联系', '捐款'],
 'hi': ['होम', 'घोषणापत्र', 'बुनियादी FAQ', 'पूरा FAQ', 'प्रो-लाइफ़ विचारधाराओं की आलोचना', 'आंदोलन के सिद्धांत',
        'पीड़ा विस्तार से', 'ब्रह्मांडीय विलुप्ति', 'इतिहास', 'हमसे जुड़ें', 'सोशल मीडिया', 'संपर्क', 'दान करें'],
 'ar': ['الرئيسية', 'البيان', 'أسئلة أساسية', 'كل الأسئلة', 'نقد أيديولوجيات pro-life', 'مبادئ الحركة',
        'المعاناة بالتفصيل', 'الانقراض الكوني', 'التاريخ', 'انضم إلينا', 'وسائل التواصل', 'تواصل معنا', 'تبرّع'],
 'bn': ['হোম', 'ইশতেহার', 'প্রাথমিক FAQ', 'সম্পূর্ণ FAQ', 'প্রো-লাইফ মতাদর্শের সমালোচনা', 'আন্দোলনের নীতি',
        'দুঃখভোগ বিস্তারিত', 'মহাজাগতিক বিলুপ্তি', 'ইতিহাস', 'আমাদের সাথে যোগ দিন', 'সোশ্যাল মিডিয়া', 'যোগাযোগ', 'দান করুন'],
 'ur': ['ہوم', 'منشور', 'بنیادی سوالات', 'تمام سوالات', 'پرو لائف نظریات پر تنقید', 'تحریک کے اصول',
        'تکلیف تفصیل سے', 'کائناتی معدومیت', 'تاریخ', 'ہمارے ساتھ شامل ہوں', 'سوشل میڈیا', 'رابطہ', 'عطیہ کریں'],
 'id': ['Beranda', 'Manifesto', 'FAQ dasar', 'FAQ lengkap', 'Kritik ideologi pro-life', 'Prinsip gerakan',
        'Penderitaan secara rinci', 'Kepunahan kosmik', 'Sejarah', 'Bergabung', 'Media sosial', 'Kontak', 'Donasi'],
 'ja': ['ホーム', 'マニフェスト', '基本FAQ', '完全版FAQ', 'pro-life 思想への批判', '運動の原則', '苦しみの詳細', '宇宙的絶滅',
        '歴史', '参加する', 'SNS', 'お問い合わせ', '寄付'],
 'tr': ['Ana sayfa', 'Manifesto', 'Temel SSS', 'Tüm SSS', 'Pro-life ideolojilerin eleştirisi', 'Hareketin ilkeleri',
        'Ayrıntılı acı', 'Kozmik yok oluş', 'Tarihçe', 'Bize katılın', 'Sosyal medya', 'İletişim', 'Bağış yap'],
 'vi': ['Trang chủ', 'Tuyên ngôn', 'FAQ cơ bản', 'FAQ đầy đủ', 'Phê phán các hệ tư tưởng pro-life', 'Nguyên tắc của phong trào',
        'Chi tiết về khổ đau', 'Tuyệt chủng vũ trụ', 'Lịch sử', 'Tham gia', 'Mạng xã hội', 'Liên hệ', 'Quyên góp'],
 'ko': ['홈', '선언문', '기본 FAQ', '전체 FAQ', '생명 찬성 이념 비판', '운동의 원칙', '고통 자세히', '우주적 멸종', '역사',
        '함께하기', '소셜 미디어', '연락처', '후원'],
 'fa': ['خانه', 'مانیفست', 'پرسش‌های پایه', 'همهٔ پرسش‌ها', 'نقد ایدئولوژی‌های pro-life', 'اصول جنبش',
        'رنج به تفصیل', 'انقراض کیهانی', 'تاریخچه', 'به ما بپیوندید', 'شبکه‌های اجتماعی', 'تماس', 'کمک مالی'],
 'mr': ['मुख्यपृष्ठ', 'जाहीरनामा', 'मूलभूत FAQ', 'संपूर्ण FAQ', 'जीवनसमर्थक विचारसरणींची समीक्षा', 'चळवळीची तत्त्वे',
        'दुःख सविस्तर', 'वैश्विक विलुप्ती', 'इतिहास', 'सामील व्हा', 'सोशल मीडिया', 'संपर्क', 'देणगी द्या'],
 'te': ['హోమ్', 'మేనిఫెస్టో', 'ప్రాథమిక FAQ', 'పూర్తి FAQ', 'జీవ-సమర్థక సిద్ధాంతాలపై విమర్శ', 'ఉద్యమ సూత్రాలు',
        'బాధ వివరంగా', 'విశ్వ అంతరించిపోవడం', 'చరిత్ర', 'మాతో చేరండి', 'సోషల్ మీడియా', 'సంప్రదించండి', 'విరాళం ఇవ్వండి'],
 'ta': ['முகப்பு', 'அறிக்கை', 'அடிப்படை FAQ', 'முழு FAQ', 'உயிர்-ஆதரவுக் கொள்கைகள் மீதான விமர்சனம்', 'இயக்கத்தின் கொள்கைகள்',
        'துன்பம் விரிவாக', 'பிரபஞ்ச அழிவு', 'வரலாறு', 'எங்களுடன் இணையுங்கள்', 'சமூக ஊடகம்', 'தொடர்பு', 'நன்கொடை'],
 'sw': ['Nyumbani', 'Ilani', 'Maswali ya msingi', 'Maswali yote', 'Ukosoaji wa itikadi za pro-life', 'Kanuni za vuguvugu',
        'Mateso kwa undani', 'Kutoweka kwa ulimwengu', 'Historia', 'Jiunge nasi', 'Mitandao ya kijamii', 'Mawasiliano', 'Changia'],
 'th': ['หน้าแรก', 'แถลงการณ์', 'FAQ พื้นฐาน', 'FAQ ฉบับเต็ม', 'วิพากษ์อุดมการณ์ pro-life', 'หลักการของขบวนการ',
        'ความทุกข์ทรมานโดยละเอียด', 'การสูญพันธุ์ระดับจักรวาล', 'ประวัติ', 'เข้าร่วมกับเรา', 'โซเชียลมีเดีย', 'ติดต่อ', 'บริจาค'],
 'nl': ['Home', 'Manifest', 'Basis-FAQ', 'Volledige FAQ', 'Kritiek op pro-life-ideologieën', 'Principes van de beweging',
        'Lijden in detail', 'Kosmische uitsterving', 'Geschiedenis', 'Doe mee', 'Sociale media', 'Contact', 'Doneren'],
 'uk': ['Головна', 'Маніфест', 'Основні запитання', 'Усі запитання', 'Критика пролайф-ідеологій', 'Принципи руху',
        'Страждання докладно', 'Космічне вимирання', 'Історія', 'Приєднуйтеся', 'Соцмережі', 'Контакти', 'Підтримати'],
 'tl': ['Home', 'Manifesto', 'Batayang FAQ', 'Buong FAQ', 'Kritika sa mga pro-life na ideolohiya', 'Mga prinsipyo ng kilusan',
        'Ang pagdurusa nang detalyado', 'Kosmikong extinction', 'Kasaysayan', 'Sumali sa amin', 'Social media', 'Makipag-ugnayan', 'Mag-donate'],
 'pa': ['ਮੁੱਖ ਪੰਨਾ', 'ਮੈਨੀਫ਼ੈਸਟੋ', 'ਮੁੱਢਲੇ ਸਵਾਲ', 'ਸਾਰੇ ਸਵਾਲ', 'ਪ੍ਰੋ-ਲਾਈਫ਼ ਵਿਚਾਰਧਾਰਾਵਾਂ ਦੀ ਆਲੋਚਨਾ', 'ਲਹਿਰ ਦੇ ਸਿਧਾਂਤ',
        'ਦੁੱਖ ਵਿਸਥਾਰ ਵਿੱਚ', 'ਬ੍ਰਹਿਮੰਡੀ ਵਿਲੁਪਤੀ', 'ਇਤਿਹਾਸ', 'ਸਾਡੇ ਨਾਲ ਜੁੜੋ', 'ਸੋਸ਼ਲ ਮੀਡੀਆ', 'ਸੰਪਰਕ', 'ਦਾਨ ਕਰੋ'],
 'gu': ['મુખ્ય પાનું', 'મેનિફેસ્ટો', 'મૂળભૂત પ્રશ્નો', 'બધા પ્રશ્નો', 'પ્રો-લાઇફ વિચારધારાઓની ટીકા', 'આંદોલનના સિદ્ધાંતો',
        'દુઃખ વિગતવાર', 'બ્રહ્માંડીય વિલુપ્તિ', 'ઇતિહાસ', 'અમારી સાથે જોડાઓ', 'સોશિયલ મીડિયા', 'સંપર્ક', 'દાન કરો'],
}
for _l, _labels in AI_MENU.items():
    SITE[_l] = [(s, s, lab, None) for (s, _, _, _), lab in zip(SITE['en'], _labels)]
ORIGINAL = {'en': 'https://www.proextinction.com/{}', 'de': 'https://sites.google.com/view/proextinctionwebsitegerman/{}',
            'pl': 'https://sites.google.com/view/proextinction-website-polish/{}',
            'es': 'https://sites.google.com/view/proextinction-website-spanish/{}',
            'it': 'https://sites.google.com/view/proextinction-website-italian/{}'}
AI = {l: {s for s, _, _, o in SITE[l] if o is None} for l in LANGS}
PAGES = {l: [(s, KINDS.get(e, 'doc')) for s, e, _, _ in SITE[l]] for l in LANGS}
NAV = {l: {s: lab for s, _, lab, _ in SITE[l]} for l in LANGS}   # no (AI) in the menu: the note on the page says it
CODE = {l: l.upper() + (AI_MARK if l in FULL_AI else '') for l in LANGS}   # picker label, e.g. 'RU (AI)'
EN_OF = {l: {s: e for s, e, _, _ in SITE[l]} for l in LANGS}          # slug -> English slug
OF_EN = {l: {e: s for s, e, _, _ in SITE[l] if e} for l in LANGS}     # English slug -> slug
ORIG = {l: {s: o for s, _, _, o in SITE[l]} for l in LANGS}

def url(lang, slug):
    """Site path of a page: /en/ for home, /en/manifesto otherwise. Cloudflare Pages serves en/index.html at /en/ and
    en/manifesto.html at /en/manifesto, and redirects /en and /en/manifesto.html there, so links use exactly these forms."""
    return f'/{lang}/' if slug == 'home' else f'/{lang}/{slug}'

def counterpart(lang, slug, other):
    """Slug of the same page in another language, or 'home'."""
    return OF_EN[other].get(EN_OF[lang].get(slug) or '', 'home')

T = {
 'en': dict(full_faq='Read the full FAQ', menu='Menu', skip='Skip to content', lang='Language', theme='Switch light/dark mode',
  tagline='Together, we end suffering.', sub='The organisation dedicated to ending forced existence and suffering',
  cta1='Join us', cta2='Read the manifesto', mission='Our Mission',
  mission_text='Preventing as much suffering as physically possible, without tradeoffs.',
  effort='Effort', questions='Questions?', questions_text='Contact info@proextinction.com to get more information on the project',
  action='Take action', toc='On this page',
  ki='Machine-translated from English (AI).',
  ki_tag='AI', progress='Reading progress', home_link='Pro Extinction – home',
  efforts=['Growing the movement to make it possible to prevent billions of years of suffering.',
   'Universal, non-discriminatory help for as many victims as physically possible. For animals, as much extraterrestrial life as possible, and humans.',
   'Purely organised action/activism based. No lamenting at the expense of the victims.',
   'Fully rational, empathetic, atheistic, logical, and fair.'],
  foot='Pro Extinction · Global', page_title='Pro Extinction'),
 'de': dict(full_faq='Zum vollständigen FAQ', menu='Menü', skip='Zum Inhalt springen', lang='Sprache', theme='Hell/Dunkel umschalten',
  tagline='Together, we end suffering.', sub='Die Organisation, die sich für das Ende erzwungener Existenz und erzwungenen Leids einsetzt.',
  cta1='Aktiv werden', cta2='Manifest lesen', mission='Unsere Mission',
  mission_text='Wir zielen darauf ab, ohne Kompromisse, so viel Leid wie möglich zu beenden.',
  effort='Einsatz', questions='Fragen?', questions_text='Kontaktiere info@proextinction.com, um mehr Informationen zu bekommen.',
  action='Mach mit', toc='Auf dieser Seite',
  ki='Maschinell aus dem Englischen übersetzt (AI).',
  ki_tag='AI', progress='Lesefortschritt', home_link='Pro Extinction – Startseite',
  efforts=['Wir vergrößern die Bewegung, um unzählige Jahre Leid zu verhindern.',
   'Universelle, nicht diskriminierende Hilfe für so viele Opfer wie physisch möglich. Für Tiere, so viel außerirdisches Leben wie möglich und Menschen.',
   'Wir sind strikt handlungsorientiert, anstatt auf Kosten der Opfer nur über das extreme Leid zu klagen.',
   'Wir sind völlig rational, empathisch, atheistisch, logisch und fair.'],
  foot='Pro Extinction · Global · +44 7557095418', page_title='Pro Extinction'),
 'pl': dict(full_faq='Przejdź do pełnego FAQ', menu='Menu', skip='Przejdź do treści', lang='Język', theme='Przełącz tryb jasny/ciemny',
  tagline='Together, we end suffering.', sub='Organizacja działająca na rzecz położenia kresu przymusowemu istnieniu i cierpieniu',
  cta1='Dołącz', cta2='Przeczytaj komunikat', mission='Nasza misja',
  mission_text='Zapobieganie cierpieniu w jak największym stopniu, bez żadnych kompromisów.',
  effort='Działanie', questions='Pytania?', questions_text='Skontaktuj się z info@proextinction.com, aby uzyskać więcej informacji na temat projektu',
  action='Dołącz', toc='Na tej stronie',
  ki='Tłumaczenie maszynowe z angielskiego (AI).',
  ki_tag='AI', progress='Postęp czytania', home_link='Pro Extinction – strona główna',
  efforts=['Rozwój ruchu, aby umożliwić zapobieżenie miliardom lat cierpienia.',
   'Powszechna, niedyskryminująca pomoc dla jak największej liczby ofiar, na ile to fizycznie możliwe. Dla zwierząt, jak największej liczby form życia więcej niż ziemskiego (czyli wszędzie, gdzie życie może zostać zapobiegnięte od zaistnienia cierpienia w kosmosie) oraz dla ludzi.',
   'Działania oparte wyłącznie na zorganizowanym działaniu/aktywizmie. Żadnego użalania się nad losem ofiar.',
   'W pełni racjonalne, empatyczne, ateistyczne, logiczne i sprawiedliwe.'],
  foot='Pro Extinction · Global', page_title='Pro Extinction'),
 'es': dict(full_faq='Ver las PMF completas', menu='Menú', skip='Ir al contenido', lang='Idioma', theme='Cambiar modo claro/oscuro',
  tagline='Together, we end suffering.', sub='Organización dedicada a poner fin a la existencia impuesta y a su sufrimiento',
  cta1='Únete', cta2='Leer el manifiesto', mission='Nuestra misión',
  mission_text='Minimizar al máximo el sufrimiento, sin concesiones.',
  effort='Línea de acción', questions='¿Preguntas?', questions_text='Contacta con info@proextinction.com para obtener más información sobre el proyecto.',
  action='Actúa', toc='En esta página',
  ki='Traducción automática del inglés (AI).',
  ki_tag='AI', progress='Progreso de lectura', home_link='Pro Extinction – página inicial',
  efforts=['Impulsar un crecimiento estratégico del movimiento que permita intervenir de forma efectiva sobre las causas estructurales del sufrimiento y prevenir su perpetuación a gran escala.',
   'Promover un alivio universal, no discriminatorio y basado en criterios de sufrimiento, dirigido al mayor número posible de víctimas: animales no humanos, cualquier forma de vida potencialmente sintiente fuera de la Tierra y la humanidad.',
   'Desarrollar un activismo organizado, disciplinado y orientado a resultados, centrado exclusivamente en la reducción del sufrimiento, sin concesiones emocionales ni discursos que lo perpetúen.',
   'Sostener el movimiento sobre principios estrictamente racionales, empáticos y coherentes, libres de dogmas, creencias infundadas o sesgos arbitrarios, con un compromiso firme con la justicia y la lógica.'],
  foot='Pro Extinction · Global · +44 7557095418', page_title='Pro Extinction'),
 'it': dict(full_faq='Vai alle FAQ complete', menu='Menu', skip='Vai al contenuto', lang='Lingua', theme='Cambia modalità chiara/scura',
  tagline='Together, we end suffering.', sub="L'organizzazione dedicata a porre fine all'esistenza forzata e alla sofferenza.",
  cta1='Unisciti a noi', cta2='Leggi il manifesto', mission='La nostra missione',
  mission_text='Prevenire quanta più sofferenza sia fisicamente possibile, senza compromessi.',
  effort='Obiettivo', questions='Domande?', questions_text='Contatta info@proextinction.com per ottenere più informazioni sul progetto',
  action='Agisci', toc='In questa pagina',
  ki="Traduzione automatica dall'inglese (AI).",
  ki_tag='AI', progress='Avanzamento lettura', home_link='Pro Extinction – home',
  efforts=['Crescere il movimento per rendere possibile la prevenzione di miliardi di anni di sofferenza.',
   'Aiuto universale, non-discriminatorio per quante più vittime sia fisicamente possibile. Per gli animali, quanta più vita extraterrestre possibile, e gli umani.',
   'Basato esclusivamente su azioni/attivismo organizzati. Nessun lamento a spese delle vittime.',
   'Pienamente razionale, empatico, ateo, logico, e giusto.'],
  foot='Pro Extinction · Global', page_title='Pro Extinction'),
}
T.update({
 'fr': dict(full_faq='Lire la FAQ complète', menu='Menu', skip='Aller au contenu', lang='Langue', theme='Basculer entre mode clair et sombre',
  tagline='Together, we end suffering.', sub="L'organisation qui se consacre à mettre fin à l'existence forcée et à la souffrance",
  cta1='Nous rejoindre', cta2='Lire le manifeste', mission='Notre mission',
  mission_text='Empêcher autant de souffrance que physiquement possible, sans compromis.',
  effort='Engagement', questions='Des questions ?', questions_text="Écrivez à info@proextinction.com pour en savoir plus sur le projet",
  action='Agir', toc='Sur cette page',
  ki="Traduction automatique de l'anglais (AI).",
  ki_tag='AI', back='Concepts', back_title="Retour à l'aperçu des concepts", progress='Progression de lecture', home_link='Pro Extinction – accueil',
  efforts=["Faire grandir le mouvement pour rendre possible la prévention de milliards d'années de souffrance.",
   'Une aide universelle et sans discrimination pour autant de victimes que physiquement possible. Pour les animaux, pour autant de vie extraterrestre que possible et pour les humains.',
   "Une action purement organisée, fondée sur l'activisme. Pas de lamentations aux dépens des victimes.",
   'Entièrement rationnel, empathique, athée, logique et juste.'],
  foot='Pro Extinction · Global', page_title='Pro Extinction'),
 'pt': dict(full_faq='Ler o FAQ completo', menu='Menu', skip='Ir para o conteúdo', lang='Idioma', theme='Alternar modo claro/escuro',
  tagline='Together, we end suffering.', sub='A organização dedicada a acabar com a existência forçada e o sofrimento',
  cta1='Junte-se a nós', cta2='Ler o manifesto', mission='Nossa missão',
  mission_text='Evitar o máximo de sofrimento fisicamente possível, sem concessões.',
  effort='Frente', questions='Dúvidas?', questions_text='Escreva para info@proextinction.com para saber mais sobre o projeto',
  action='Aja', toc='Nesta página',
  ki='Tradução automática do inglês (AI).',
  ki_tag='AI', progress='Progresso de leitura', home_link='Pro Extinction – início',
  efforts=['Fazer o movimento crescer para tornar possível evitar bilhões de anos de sofrimento.',
   'Ajuda universal e sem discriminação para o maior número de vítimas fisicamente possível. Para animais, para o máximo possível de vida extraterrestre e para humanos.',
   'Ação puramente organizada, baseada em ativismo. Nada de lamentar à custa das vítimas.',
   'Totalmente racional, empático, ateu, lógico e justo.'],
  foot='Pro Extinction · Global', page_title='Pro Extinction'),
 'ru': dict(full_faq='Все вопросы и ответы', menu='Меню', skip='Перейти к содержанию', lang='Язык', theme='Переключить светлую/тёмную тему',
  tagline='Together, we end suffering.', sub='Организация, которая стремится положить конец вынужденному существованию и страданию',
  cta1='Присоединиться', cta2='Читать манифест', mission='Наша миссия',
  mission_text='Предотвратить столько страданий, сколько физически возможно, без компромиссов.',
  effort='Направление', questions='Есть вопросы?', questions_text='Пишите на info@proextinction.com, чтобы узнать больше о проекте',
  action='Действуйте', toc='На этой странице',
  ki='Машинный перевод с английского (AI).',
  ki_tag='AI', progress='Прогресс чтения', home_link='Pro Extinction – главная',
  efforts=['Развивать движение, чтобы сделать возможным предотвращение миллиардов лет страданий.',
   'Всеобщая помощь без дискриминации для стольких жертв, сколько физически возможно. Для животных, для как можно большего числа внеземной жизни и для людей.',
   'Только организованные действия и активизм. Никаких причитаний за счёт жертв.',
   'Полностью рационально, эмпатично, атеистично, логично и справедливо.'],
  foot='Pro Extinction · Global', page_title='Pro Extinction'),
 'zh': dict(full_faq='查看完整问答', menu='菜单', skip='跳到正文', lang='语言', theme='切换浅色/深色模式',
  tagline='Together, we end suffering.', sub='致力于终结被迫存在与苦难的组织',
  cta1='加入我们', cta2='阅读宣言', mission='我们的使命',
  mission_text='在物理上可能的范围内尽量防止苦难，绝不妥协。',
  effort='方向', questions='有疑问？', questions_text='请联系 info@proextinction.com 了解项目详情',
  action='行动起来', toc='本页内容',
  ki='由英文机器翻译 (AI)。',
  ki_tag='AI', progress='阅读进度', home_link='Pro Extinction – 首页',
  efforts=['壮大运动，让防止数十亿年的苦难成为可能。',
   '为物理上可能的最多受害者提供普遍、无差别的帮助。包括动物、尽可能多的地外生命以及人类。',
   '完全以有组织的行动和行动主义为本。不以受害者为代价空发哀叹。',
   '完全理性、富有同理心、无神论、合乎逻辑且公平。'],
  foot='Pro Extinction · Global', page_title='Pro Extinction'),
 'hi': dict(full_faq='पूरा FAQ पढ़ें', menu='मेनू', skip='सामग्री पर जाएँ', lang='भाषा', theme='लाइट/डार्क मोड बदलें',
  tagline='Together, we end suffering.', sub='वह संगठन जो थोपे गए अस्तित्व और पीड़ा को ख़त्म करने के लिए समर्पित है',
  cta1='हमसे जुड़ें', cta2='घोषणापत्र पढ़ें', mission='हमारा मिशन',
  mission_text='बिना किसी समझौते के, भौतिक रूप से जितनी हो सके उतनी पीड़ा को रोकना।',
  effort='प्रयास', questions='कोई सवाल?', questions_text='परियोजना के बारे में और जानकारी के लिए info@proextinction.com पर संपर्क करें',
  action='कदम उठाएँ', toc='इस पेज पर',
  ki='अंग्रेज़ी से मशीन अनुवाद (AI)।',
  ki_tag='AI', progress='पढ़ने की प्रगति', home_link='Pro Extinction – होम',
  efforts=['आंदोलन को बढ़ाना, ताकि अरबों वर्षों की पीड़ा को रोकना संभव हो सके।',
   'भौतिक रूप से जितने संभव हों उतने पीड़ितों के लिए सार्वभौमिक, बिना भेदभाव की मदद। जानवरों के लिए, जितना हो सके उतने पृथ्वी से बाहर के जीवन के लिए, और इंसानों के लिए।',
   'पूरी तरह संगठित कार्रवाई और एक्टिविज़्म पर आधारित। पीड़ितों की कीमत पर कोई विलाप नहीं।',
   'पूरी तरह तार्किक, सहानुभूतिपूर्ण, नास्तिक, विवेकपूर्ण और न्यायसंगत।'],
  foot='Pro Extinction · Global', page_title='Pro Extinction'),
 'ar': dict(full_faq='اقرأ كل الأسئلة', menu='القائمة', skip='انتقل إلى المحتوى', lang='اللغة', theme='التبديل بين الوضع الفاتح والداكن',
  tagline='Together, we end suffering.', sub='المنظمة المكرّسة لإنهاء الوجود القسري والمعاناة',
  cta1='انضم إلينا', cta2='اقرأ البيان', mission='مهمتنا',
  mission_text='منع أكبر قدر ممكن فيزيائيًا من المعاناة، دون تنازلات.',
  effort='محور', questions='لديك أسئلة؟', questions_text='راسلنا على info@proextinction.com لمعرفة المزيد عن المشروع',
  action='تحرّك', toc='في هذه الصفحة',
  ki='ترجمة آلية من الإنجليزية (AI).',
  ki_tag='AI', progress='تقدّم القراءة', home_link='Pro Extinction – الرئيسية',
  efforts=['تنمية الحركة لكي يصبح منع مليارات السنين من المعاناة ممكنًا.',
   'مساعدة شاملة ودون تمييز لأكبر عدد ممكن فيزيائيًا من الضحايا. للحيوانات، ولأكبر قدر ممكن من الحياة خارج الأرض، وللبشر.',
   'عمل منظّم ونشاط ميداني فقط. لا نوح على حساب الضحايا.',
   'عقلانية تامة وتعاطف وإلحاد ومنطق وعدل.'],
  foot='Pro Extinction · Global', page_title='Pro Extinction'),
 'bn': dict(full_faq='সম্পূর্ণ FAQ পড়ুন', menu='মেনু', skip='মূল বিষয়ে যান', lang='ভাষা', theme='লাইট/ডার্ক মোড বদলান',
  tagline='Together, we end suffering.', sub='যে সংগঠন জোর করে চাপিয়ে দেওয়া অস্তিত্ব আর দুঃখভোগের অবসানে নিবেদিত',
  cta1='আমাদের সাথে যোগ দিন', cta2='ইশতেহার পড়ুন', mission='আমাদের লক্ষ্য',
  mission_text='কোনো আপস ছাড়াই, শারীরিকভাবে যতটা সম্ভব দুঃখভোগ ঠেকানো।',
  effort='প্রচেষ্টা', questions='কোনো প্রশ্ন?', questions_text='প্রকল্প সম্পর্কে আরও জানতে info@proextinction.com-এ যোগাযোগ করুন',
  action='পদক্ষেপ নিন', toc='এই পাতায়',
  ki='ইংরেজি থেকে যন্ত্রে অনুবাদ (AI)।',
  ki_tag='AI', progress='পড়ার অগ্রগতি', home_link='Pro Extinction – হোম',
  efforts=['আন্দোলনকে বড় করা, যাতে কোটি কোটি বছরের দুঃখভোগ ঠেকানো সম্ভব হয়।',
   'শারীরিকভাবে যত বেশি সম্ভব ভুক্তভোগীর জন্য সর্বজনীন, বৈষম্যহীন সাহায্য। প্রাণীদের জন্য, যত বেশি সম্ভব পৃথিবীর বাইরের প্রাণের জন্য, আর মানুষের জন্য।',
   'কেবল সংগঠিত কাজ আর অ্যাক্টিভিজমের ওপর ভিত্তি করে। ভুক্তভোগীদের মূল্যে কোনো বিলাপ নয়।',
   'পুরোপুরি যুক্তিনিষ্ঠ, সহমর্মী, নাস্তিক, যৌক্তিক আর ন্যায্য।'],
  foot='Pro Extinction · Global', page_title='Pro Extinction'),
 'ur': dict(full_faq='تمام سوالات پڑھیں', menu='مینو', skip='مواد پر جائیں', lang='زبان', theme='لائٹ/ڈارک موڈ بدلیں',
  tagline='Together, we end suffering.', sub='وہ تنظیم جو زبردستی کے وجود اور تکلیف کو ختم کرنے کے لیے وقف ہے',
  cta1='ہمارے ساتھ شامل ہوں', cta2='منشور پڑھیں', mission='ہمارا مشن',
  mission_text='بغیر کسی سمجھوتے کے، جسمانی طور پر جتنی ممکن ہو اتنی تکلیف کو روکنا۔',
  effort='کوشش', questions='کوئی سوال؟', questions_text='منصوبے کے بارے میں مزید جاننے کے لیے info@proextinction.com پر رابطہ کریں',
  action='قدم اٹھائیں', toc='اس صفحے پر',
  ki='انگریزی سے مشینی ترجمہ (AI)۔',
  ki_tag='AI', progress='پڑھنے کی پیش رفت', home_link='Pro Extinction – ہوم',
  efforts=['تحریک کو بڑھانا، تاکہ اربوں سال کی تکلیف کو روکنا ممکن ہو سکے۔',
   'جسمانی طور پر جتنے ممکن ہوں اتنے متاثرین کے لیے عالمگیر، بلا امتیاز مدد۔ جانوروں کے لیے، زمین سے باہر جتنی ممکن ہو اتنی زندگی کے لیے، اور انسانوں کے لیے۔',
   'صرف منظم عمل اور ایکٹیوزم پر مبنی۔ متاثرین کی قیمت پر کوئی ماتم نہیں۔',
   'مکمل طور پر عقلی، ہمدرد، ملحد، منطقی اور منصفانہ۔'],
  foot='Pro Extinction · Global', page_title='Pro Extinction'),
 'id': dict(full_faq='Baca FAQ lengkap', menu='Menu', skip='Langsung ke isi', lang='Bahasa', theme='Ganti mode terang/gelap',
  tagline='Together, we end suffering.', sub='Organisasi yang berjuang untuk mengakhiri keberadaan yang dipaksakan dan penderitaan',
  cta1='Bergabung', cta2='Baca manifesto', mission='Misi kami',
  mission_text='Mencegah penderitaan sebanyak yang secara fisik mungkin, tanpa kompromi.',
  effort='Upaya', questions='Ada pertanyaan?', questions_text='Hubungi info@proextinction.com untuk informasi lebih lanjut tentang proyek ini',
  action='Bertindak', toc='Di halaman ini',
  ki='Terjemahan mesin dari bahasa Inggris (AI).',
  ki_tag='AI', progress='Kemajuan membaca', home_link='Pro Extinction – beranda',
  efforts=['Membesarkan gerakan agar pencegahan miliaran tahun penderitaan menjadi mungkin.',
   'Bantuan universal tanpa diskriminasi bagi sebanyak mungkin korban yang secara fisik bisa dijangkau. Bagi hewan, bagi sebanyak mungkin kehidupan di luar Bumi, dan bagi manusia.',
   'Murni berbasis aksi dan aktivisme yang terorganisasi. Tidak meratap dengan mengorbankan para korban.',
   'Sepenuhnya rasional, empatik, ateis, logis, dan adil.'],
  foot='Pro Extinction · Global', page_title='Pro Extinction'),
})
T.update({
 'ja': dict(full_faq='完全版FAQを読む', menu='メニュー', skip='本文へ移動', lang='言語', theme='ライト/ダークモードを切り替え',
  tagline='Together, we end suffering.', sub='強いられた存在と苦しみを終わらせることに取り組む団体',
  cta1='参加する', cta2='マニフェストを読む', mission='私たちの使命',
  mission_text='妥協せず、物理的に可能な限り多くの苦しみを防ぐこと。',
  effort='取り組み', questions='ご質問は?', questions_text='プロジェクトの詳細は info@proextinction.com までお問い合わせください',
  action='行動する', toc='このページの内容',
  ki='英語からの機械翻訳 (AI)。',
  ki_tag='AI', progress='読書の進み具合', home_link='Pro Extinction – ホーム',
  efforts=['運動を広げ、何十億年もの苦しみを防ぐことを可能にする。',
   '物理的に可能な限り多くの犠牲者への、差別のない普遍的な支援。動物のため、できる限り多くの地球外生命のため、そして人間のため。',
   '組織的な行動とアクティビズムだけに基づく。犠牲者を犠牲にした嘆きはしない。',
   '完全に理性的で、共感的で、無神論的で、論理的で、公正。'],
  foot='Pro Extinction · Global', page_title='Pro Extinction'),
 'tr': dict(full_faq='Tüm SSS\'yi oku', menu='Menü', skip='İçeriğe geç', lang='Dil', theme='Açık/koyu modu değiştir',
  tagline='Together, we end suffering.', sub='Zorla dayatılan varoluşu ve acıyı sona erdirmeye adanmış örgüt',
  cta1='Bize katılın', cta2='Manifestoyu oku', mission='Misyonumuz',
  mission_text='Taviz vermeden, fiziksel olarak mümkün olan en fazla acıyı önlemek.',
  effort='Çaba', questions='Sorunuz mu var?', questions_text='Proje hakkında daha fazla bilgi için info@proextinction.com adresine yazın',
  action='Harekete geçin', toc='Bu sayfada',
  ki='İngilizceden makine çevirisi (AI).',
  ki_tag='AI', progress='Okuma ilerlemesi', home_link='Pro Extinction – ana sayfa',
  efforts=['Milyarlarca yıllık acıyı önlemeyi mümkün kılmak için hareketi büyütmek.',
   'Fiziksel olarak mümkün olan en çok kurbana ayrımsız, evrensel yardım. Hayvanlar için, olabildiğince çok dünya dışı yaşam için ve insanlar için.',
   'Yalnızca örgütlü eyleme ve aktivizme dayalı. Kurbanlar pahasına yakınmak yok.',
   'Tamamen akılcı, empatik, ateist, mantıklı ve adil.'],
  foot='Pro Extinction · Global', page_title='Pro Extinction'),
 'vi': dict(full_faq='Đọc FAQ đầy đủ', menu='Menu', skip='Đến nội dung chính', lang='Ngôn ngữ', theme='Chuyển chế độ sáng/tối',
  tagline='Together, we end suffering.', sub='Tổ chức tận tâm chấm dứt sự tồn tại bị cưỡng ép và khổ đau',
  cta1='Tham gia', cta2='Đọc tuyên ngôn', mission='Sứ mệnh của chúng tôi',
  mission_text='Ngăn chặn nhiều khổ đau nhất có thể về mặt vật lý, không thỏa hiệp.',
  effort='Nỗ lực', questions='Có câu hỏi?', questions_text='Liên hệ info@proextinction.com để biết thêm về dự án',
  action='Hành động', toc='Trên trang này',
  ki='Dịch máy từ tiếng Anh (AI).',
  ki_tag='AI', progress='Tiến độ đọc', home_link='Pro Extinction – trang chủ',
  efforts=['Phát triển phong trào để có thể ngăn chặn hàng tỷ năm khổ đau.',
   'Giúp đỡ phổ quát, không phân biệt, cho nhiều nạn nhân nhất có thể về mặt vật lý. Cho động vật, cho càng nhiều sự sống ngoài Trái Đất càng tốt, và cho con người.',
   'Hoàn toàn dựa trên hành động có tổ chức và hoạt động xã hội. Không than khóc trên lưng nạn nhân.',
   'Hoàn toàn lý trí, đồng cảm, vô thần, logic và công bằng.'],
  foot='Pro Extinction · Global', page_title='Pro Extinction'),
 'ko': dict(full_faq='전체 FAQ 읽기', menu='메뉴', skip='본문으로 건너뛰기', lang='언어', theme='라이트/다크 모드 전환',
  tagline='Together, we end suffering.', sub='강요된 존재와 고통을 끝내는 데 헌신하는 단체',
  cta1='함께하기', cta2='선언문 읽기', mission='우리의 사명',
  mission_text='타협 없이, 물리적으로 가능한 한 많은 고통을 막는 것.',
  effort='노력', questions='질문이 있나요?', questions_text='프로젝트에 대해 더 알고 싶다면 info@proextinction.com 으로 연락하세요',
  action='행동하기', toc='이 페이지의 내용',
  ki='영어에서 기계 번역됨 (AI).',
  ki_tag='AI', progress='읽기 진행률', home_link='Pro Extinction – 홈',
  efforts=['운동을 키워 수십억 년의 고통을 막는 일을 가능하게 한다.',
   '물리적으로 가능한 한 많은 피해자를 위한 차별 없는 보편적 도움. 동물을 위해, 가능한 한 많은 외계 생명을 위해, 그리고 인간을 위해.',
   '오직 조직된 행동과 활동에 기반한다. 피해자를 희생시키는 한탄은 없다.',
   '완전히 이성적이고, 공감적이며, 무신론적이고, 논리적이며, 공정하다.'],
  foot='Pro Extinction · Global', page_title='Pro Extinction'),
 'fa': dict(full_faq='همهٔ پرسش‌ها را بخوانید', menu='منو', skip='رفتن به محتوا', lang='زبان', theme='تغییر حالت روشن/تیره',
  tagline='Together, we end suffering.', sub='سازمانی که برای پایان دادن به هستی اجباری و رنج تلاش می‌کند',
  cta1='به ما بپیوندید', cta2='مانیفست را بخوانید', mission='مأموریت ما',
  mission_text='جلوگیری از هر چه بیشتر رنجی که از نظر فیزیکی ممکن است، بدون سازش.',
  effort='تلاش', questions='پرسشی دارید؟', questions_text='برای آگاهی بیشتر از پروژه به info@proextinction.com پیام دهید',
  action='اقدام کنید', toc='در این صفحه',
  ki='ترجمهٔ ماشینی از انگلیسی (AI).',
  ki_tag='AI', progress='پیشرفت خواندن', home_link='Pro Extinction – خانه',
  efforts=['رشد دادن جنبش تا جلوگیری از میلیاردها سال رنج ممکن شود.',
   'کمکی همگانی و بی‌تبعیض به هر چه بیشتر قربانیانی که از نظر فیزیکی ممکن است. برای حیوانات، برای هر چه بیشتر حیات فرازمینی و برای انسان‌ها.',
   'فقط بر پایهٔ اقدام سازمان‌یافته و کنشگری. بدون مویه به بهای قربانیان.',
   'کاملاً عقلانی، همدل، خداناباور، منطقی و منصف.'],
  foot='Pro Extinction · Global', page_title='Pro Extinction'),
 'mr': dict(full_faq='संपूर्ण FAQ वाचा', menu='मेनू', skip='मजकुराकडे जा', lang='भाषा', theme='लाइट/डार्क मोड बदला',
  tagline='Together, we end suffering.', sub='लादलेले अस्तित्व आणि दुःख संपवण्यासाठी समर्पित संघटना',
  cta1='सामील व्हा', cta2='जाहीरनामा वाचा', mission='आमचे ध्येय',
  mission_text='कोणतीही तडजोड न करता, भौतिकदृष्ट्या शक्य तितके दुःख रोखणे.',
  effort='प्रयत्न', questions='काही प्रश्न?', questions_text='प्रकल्पाबद्दल अधिक माहितीसाठी info@proextinction.com वर संपर्क साधा',
  action='कृती करा', toc='या पानावर',
  ki='इंग्रजीतून यंत्राद्वारे भाषांतर (AI).',
  ki_tag='AI', progress='वाचनाची प्रगती', home_link='Pro Extinction – मुख्यपृष्ठ',
  efforts=['अब्जावधी वर्षांचे दुःख रोखणे शक्य व्हावे म्हणून चळवळ वाढवणे.',
   'भौतिकदृष्ट्या शक्य तितक्या बळींसाठी सार्वत्रिक, भेदभावरहित मदत. प्राण्यांसाठी, शक्य तितक्या परग्रहावरील जीवनासाठी आणि माणसांसाठी.',
   'केवळ संघटित कृती आणि चळवळीवर आधारित. बळींच्या जिवावर विलाप नाही.',
   'पूर्णपणे तार्किक, सहानुभूतिशील, निरीश्वरवादी, विवेकी आणि न्याय्य.'],
  foot='Pro Extinction · Global', page_title='Pro Extinction'),
 'te': dict(full_faq='పూర్తి FAQ చదవండి', menu='మెనూ', skip='విషయానికి వెళ్ళండి', lang='భాష', theme='లైట్/డార్క్ మోడ్ మార్చండి',
  tagline='Together, we end suffering.', sub='బలవంతపు ఉనికిని, బాధను అంతం చేయడానికి అంకితమైన సంస్థ',
  cta1='మాతో చేరండి', cta2='మేనిఫెస్టో చదవండి', mission='మా లక్ష్యం',
  mission_text='రాజీ లేకుండా, భౌతికంగా సాధ్యమైనంత ఎక్కువ బాధను నివారించడం.',
  effort='ప్రయత్నం', questions='ప్రశ్నలు ఉన్నాయా?', questions_text='ప్రాజెక్టు గురించి మరింత తెలుసుకోవడానికి info@proextinction.com ని సంప్రదించండి',
  action='చర్య తీసుకోండి', toc='ఈ పేజీలో',
  ki='ఆంగ్లం నుంచి యంత్ర అనువాదం (AI).',
  ki_tag='AI', progress='చదివిన పురోగతి', home_link='Pro Extinction – హోమ్',
  efforts=['బిలియన్ల సంవత్సరాల బాధను నివారించడం సాధ్యమయ్యేలా ఉద్యమాన్ని పెంచడం.',
   'భౌతికంగా సాధ్యమైనంత ఎక్కువ బాధితులకు విశ్వవ్యాప్త, వివక్షలేని సహాయం. జంతువులకు, సాధ్యమైనంత ఎక్కువ గ్రహాంతర జీవాలకు, మనుషులకు.',
   'కేవలం వ్యవస్థీకృత చర్య, ఉద్యమంపై ఆధారపడినది. బాధితుల ఖర్చుతో విలాపం లేదు.',
   'పూర్తిగా తార్కికం, సహానుభూతి గలది, నాస్తికం, హేతుబద్ధం, న్యాయమైనది.'],
  foot='Pro Extinction · Global', page_title='Pro Extinction'),
 'ta': dict(full_faq='முழு FAQ படிக்கவும்', menu='பட்டி', skip='உள்ளடக்கத்திற்குச் செல்லவும்', lang='மொழி', theme='ஒளி/இருள் பயன்முறையை மாற்றவும்',
  tagline='Together, we end suffering.', sub='கட்டாய இருப்பையும் துன்பத்தையும் முடிவுக்குக் கொண்டுவர அர்ப்பணிக்கப்பட்ட அமைப்பு',
  cta1='எங்களுடன் இணையுங்கள்', cta2='அறிக்கையைப் படிக்கவும்', mission='எங்கள் இலக்கு',
  mission_text='சமரசமின்றி, பௌதீக ரீதியாக முடிந்தவரை அதிகத் துன்பத்தைத் தடுப்பது.',
  effort='முயற்சி', questions='கேள்விகள் உள்ளனவா?', questions_text='திட்டம் பற்றி மேலும் அறிய info@proextinction.com-ஐத் தொடர்பு கொள்ளுங்கள்',
  action='செயல்படுங்கள்', toc='இந்தப் பக்கத்தில்',
  ki='ஆங்கிலத்திலிருந்து இயந்திர மொழிபெயர்ப்பு (AI).',
  ki_tag='AI', progress='வாசிப்பு முன்னேற்றம்', home_link='Pro Extinction – முகப்பு',
  efforts=['பில்லியன் கணக்கான ஆண்டுகளின் துன்பத்தைத் தடுப்பதைச் சாத்தியமாக்க இயக்கத்தை வளர்ப்பது.',
   'பௌதீக ரீதியாக முடிந்தவரை அதிகமான பாதிக்கப்பட்டவர்களுக்கு உலகளாவிய, பாகுபாடற்ற உதவி. விலங்குகளுக்கு, முடிந்தவரை அதிக வேற்றுக்கிரக உயிர்களுக்கு, மனிதர்களுக்கு.',
   'ஒழுங்கமைக்கப்பட்ட செயல் மற்றும் இயக்கச் செயல்பாட்டை மட்டுமே அடிப்படையாகக் கொண்டது. பாதிக்கப்பட்டவர்களின் விலையில் புலம்பல் இல்லை.',
   'முழுமையாகப் பகுத்தறிவு, பரிவு, நாத்திகம், தர்க்கம், நியாயம் கொண்டது.'],
  foot='Pro Extinction · Global', page_title='Pro Extinction'),
 'sw': dict(full_faq='Soma maswali yote', menu='Menyu', skip='Nenda kwenye maudhui', lang='Lugha', theme='Badilisha hali ya mwanga/giza',
  tagline='Together, we end suffering.', sub='Shirika linalojitolea kumaliza uwepo wa kulazimishwa na mateso',
  cta1='Jiunge nasi', cta2='Soma ilani', mission='Dhamira yetu',
  mission_text='Kuzuia mateso mengi kadiri inavyowezekana kimwili, bila maafikiano.',
  effort='Juhudi', questions='Una maswali?', questions_text='Andika kwa info@proextinction.com kujua zaidi kuhusu mradi',
  action='Chukua hatua', toc='Kwenye ukurasa huu',
  ki='Tafsiri ya mashine kutoka Kiingereza (AI).',
  ki_tag='AI', progress='Maendeleo ya kusoma', home_link='Pro Extinction – nyumbani',
  efforts=['Kukuza vuguvugu ili kuzuia mabilioni ya miaka ya mateso kuwezekane.',
   'Msaada wa wote, bila ubaguzi, kwa waathiriwa wengi kadiri inavyowezekana kimwili. Kwa wanyama, kwa uhai mwingi wa nje ya dunia kadiri iwezekanavyo, na kwa wanadamu.',
   'Kwa msingi wa vitendo vilivyopangwa na uanaharakati pekee. Hakuna kulalamika kwa gharama ya waathiriwa.',
   'Kwa ukamilifu wa busara, huruma, ukanaji Mungu, mantiki na haki.'],
  foot='Pro Extinction · Global', page_title='Pro Extinction'),
 'th': dict(full_faq='อ่าน FAQ ฉบับเต็ม', menu='เมนู', skip='ข้ามไปยังเนื้อหา', lang='ภาษา', theme='สลับโหมดสว่าง/มืด',
  tagline='Together, we end suffering.', sub='องค์กรที่อุทิศตนเพื่อยุติการดำรงอยู่ที่ถูกบังคับและความทุกข์ทรมาน',
  cta1='เข้าร่วมกับเรา', cta2='อ่านแถลงการณ์', mission='พันธกิจของเรา',
  mission_text='ป้องกันความทุกข์ทรมานให้ได้มากที่สุดเท่าที่เป็นไปได้ทางกายภาพ โดยไม่ประนีประนอม',
  effort='ความพยายาม', questions='มีคำถามไหม?', questions_text='ติดต่อ info@proextinction.com เพื่อทราบข้อมูลเพิ่มเติมเกี่ยวกับโครงการ',
  action='ลงมือทำ', toc='ในหน้านี้',
  ki='แปลด้วยเครื่องจากภาษาอังกฤษ (AI)',
  ki_tag='AI', progress='ความคืบหน้าการอ่าน', home_link='Pro Extinction – หน้าแรก',
  efforts=['ขยายขบวนการเพื่อให้การป้องกันความทุกข์ทรมานหลายพันล้านปีเป็นไปได้',
   'ความช่วยเหลือสากลที่ไม่เลือกปฏิบัติ สำหรับเหยื่อให้มากที่สุดเท่าที่เป็นไปได้ทางกายภาพ สำหรับสัตว์ สำหรับชีวิตนอกโลกให้มากที่สุด และสำหรับมนุษย์',
   'ตั้งอยู่บนการกระทำและการเคลื่อนไหวที่มีการจัดตั้งเท่านั้น ไม่คร่ำครวญโดยแลกกับเหยื่อ',
   'มีเหตุผล เห็นอกเห็นใจ ไม่เชื่อในพระเจ้า มีตรรกะ และยุติธรรมอย่างสมบูรณ์'],
  foot='Pro Extinction · Global', page_title='Pro Extinction'),
 'nl': dict(full_faq='Lees de volledige FAQ', menu='Menu', skip='Naar de inhoud', lang='Taal', theme='Licht/donker wisselen',
  tagline='Together, we end suffering.', sub='Een organisatie die zich inzet om gedwongen bestaan en lijden te beëindigen',
  cta1='Doe mee', cta2='Lees het manifest', mission='Onze missie',
  mission_text='Zoveel lijden voorkomen als fysiek mogelijk is, zonder compromissen.',
  effort='Inzet', questions='Vragen?', questions_text='Schrijf naar info@proextinction.com voor meer informatie over het project',
  action='Kom in actie', toc='Op deze pagina',
  ki='Machinevertaling uit het Engels (AI).',
  ki_tag='AI', progress='Leesvoortgang', home_link='Pro Extinction – home',
  efforts=['De beweging laten groeien, zodat het voorkomen van miljarden jaren lijden mogelijk wordt.',
   'Universele hulp zonder discriminatie aan zoveel slachtoffers als fysiek mogelijk is. Aan dieren, aan zoveel mogelijk buitenaards leven en aan mensen.',
   'Alleen gebaseerd op georganiseerde actie en activisme. Geen geklaag ten koste van de slachtoffers.',
   'Volledig rationeel, empathisch, atheïstisch, logisch en rechtvaardig.'],
  foot='Pro Extinction · Global', page_title='Pro Extinction'),
 'uk': dict(full_faq='Читати всі запитання', menu='Меню', skip='Перейти до змісту', lang='Мова', theme='Перемкнути світлу/темну тему',
  tagline='Together, we end suffering.', sub='Організація, що прагне покласти край вимушеному існуванню і стражданням',
  cta1='Приєднуйтеся', cta2='Читати маніфест', mission='Наша місія',
  mission_text='Запобігти стількам стражданням, скільки фізично можливо, без компромісів.',
  effort='Зусилля', questions='Є запитання?', questions_text='Пишіть на info@proextinction.com, щоб дізнатися більше про проєкт',
  action='Дійте', toc='На цій сторінці',
  ki='Машинний переклад з англійської (AI).',
  ki_tag='AI', progress='Прогрес читання', home_link='Pro Extinction – головна',
  efforts=['Розвивати рух, щоб стало можливим запобігти мільярдам років страждань.',
   'Всесвітня допомога без дискримінації якомога більшій кількості жертв, скільки фізично можливо. Тваринам, якомога більшій частині позаземного життя і людям.',
   'Лише на основі організованих дій і активізму. Жодних нарікань за рахунок жертв.',
   'Повністю раціонально, емпатично, атеїстично, логічно і справедливо.'],
  foot='Pro Extinction · Global', page_title='Pro Extinction'),
 'tl': dict(full_faq='Basahin ang buong FAQ', menu='Menu', skip='Lumaktaw sa nilalaman', lang='Wika', theme='Palitan ang maliwanag/madilim',
  tagline='Together, we end suffering.', sub='Isang organisasyong nakatuon sa pagwawakas ng sapilitang pag-iral at pagdurusa',
  cta1='Sumali sa amin', cta2='Basahin ang manifesto', mission='Ang aming misyon',
  mission_text='Pigilan ang pinakamaraming pagdurusa hangga\'t pisikal na posible, nang walang kompromiso.',
  effort='Pagsisikap', questions='May tanong?', questions_text='Sumulat sa info@proextinction.com para malaman pa ang tungkol sa proyekto',
  action='Kumilos', toc='Sa pahinang ito',
  ki='Machine translation mula sa Ingles (AI).',
  ki_tag='AI', progress='Pag-usad ng pagbasa', home_link='Pro Extinction – home',
  efforts=['Palakihin ang kilusan para maging posible ang pagpigil sa bilyun-bilyong taon ng pagdurusa.',
   'Pandaigdigang tulong nang walang diskriminasyon sa pinakamaraming biktima hangga\'t pisikal na posible. Sa mga hayop, sa pinakamaraming buhay sa ibang planeta hangga\'t maaari, at sa mga tao.',
   'Nakabatay lang sa organisadong aksyon at aktibismo. Walang pagrereklamo na ang mga biktima ang nagbabayad.',
   'Ganap na makatwiran, may empatiya, ateista, lohikal at makatarungan.'],
  foot='Pro Extinction · Global', page_title='Pro Extinction'),
 'pa': dict(full_faq='ਸਾਰੇ ਸਵਾਲ ਪੜ੍ਹੋ', menu='ਮੀਨੂ', skip='ਸਮੱਗਰੀ ਵੱਲ ਜਾਓ', lang='ਭਾਸ਼ਾ', theme='ਹਲਕਾ/ਗੂੜ੍ਹਾ ਮੋਡ ਬਦਲੋ',
  tagline='Together, we end suffering.', sub='ਜ਼ਬਰਦਸਤੀ ਹੋਂਦ ਅਤੇ ਦੁੱਖ ਨੂੰ ਖ਼ਤਮ ਕਰਨ ਲਈ ਸਮਰਪਿਤ ਇੱਕ ਸੰਸਥਾ',
  cta1='ਸਾਡੇ ਨਾਲ ਜੁੜੋ', cta2='ਮੈਨੀਫ਼ੈਸਟੋ ਪੜ੍ਹੋ', mission='ਸਾਡਾ ਮਿਸ਼ਨ',
  mission_text='ਜਿੰਨਾ ਸਰੀਰਕ ਤੌਰ \'ਤੇ ਸੰਭਵ ਹੋਵੇ ਓਨਾ ਦੁੱਖ ਰੋਕਣਾ, ਬਿਨਾਂ ਕਿਸੇ ਸਮਝੌਤੇ ਦੇ।',
  effort='ਯਤਨ', questions='ਕੋਈ ਸਵਾਲ?', questions_text='ਪ੍ਰੋਜੈਕਟ ਬਾਰੇ ਹੋਰ ਜਾਣਨ ਲਈ info@proextinction.com \'ਤੇ ਲਿਖੋ',
  action='ਕਦਮ ਚੁੱਕੋ', toc='ਇਸ ਪੰਨੇ \'ਤੇ',
  ki='ਅੰਗਰੇਜ਼ੀ ਤੋਂ ਮਸ਼ੀਨੀ ਅਨੁਵਾਦ (AI)।',
  ki_tag='AI', back='ਸੰਕਲਪ', back_title='ਸੰਕਲਪਾਂ ਦੀ ਝਲਕ \'ਤੇ ਵਾਪਸ ਜਾਓ', progress='ਪੜ੍ਹਨ ਦੀ ਤਰੱਕੀ', home_link='Pro Extinction – ਮੁੱਖ ਪੰਨਾ',
  efforts=['ਲਹਿਰ ਨੂੰ ਵਧਾਉਣਾ ਤਾਂ ਜੋ ਅਰਬਾਂ ਸਾਲਾਂ ਦੇ ਦੁੱਖ ਨੂੰ ਰੋਕਣਾ ਸੰਭਵ ਹੋ ਸਕੇ।',
   'ਜਿੰਨੇ ਸਰੀਰਕ ਤੌਰ \'ਤੇ ਸੰਭਵ ਹੋਣ ਓਨੇ ਪੀੜਤਾਂ ਲਈ ਬਿਨਾਂ ਵਿਤਕਰੇ ਦੇ ਸਰਬ-ਵਿਆਪੀ ਮਦਦ। ਜਾਨਵਰਾਂ ਲਈ, ਜਿੰਨਾ ਹੋ ਸਕੇ ਬਾਹਰੀ ਗ੍ਰਹਿਆਂ ਦੇ ਜੀਵਨ ਲਈ, ਅਤੇ ਮਨੁੱਖਾਂ ਲਈ।',
   'ਸਿਰਫ਼ ਸੰਗਠਿਤ ਕਾਰਵਾਈ ਅਤੇ ਸਰਗਰਮੀ \'ਤੇ ਆਧਾਰਿਤ। ਪੀੜਤਾਂ ਦੀ ਕੀਮਤ \'ਤੇ ਕੋਈ ਸ਼ਿਕਾਇਤਬਾਜ਼ੀ ਨਹੀਂ।',
   'ਪੂਰੀ ਤਰ੍ਹਾਂ ਤਰਕਸ਼ੀਲ, ਹਮਦਰਦ, ਨਾਸਤਿਕ, ਤਾਰਕਿਕ ਅਤੇ ਨਿਆਂਪੂਰਨ।'],
  foot='Pro Extinction · Global', page_title='Pro Extinction'),
 'gu': dict(full_faq='બધા પ્રશ્નો વાંચો', menu='મેનુ', skip='સામગ્રી પર જાઓ', lang='ભાષા', theme='લાઇટ/ડાર્ક મોડ બદલો',
  tagline='Together, we end suffering.', sub='બળજબરીથી અસ્તિત્વ અને દુઃખનો અંત લાવવા માટે સમર્પિત એક સંસ્થા',
  cta1='અમારી સાથે જોડાઓ', cta2='મેનિફેસ્ટો વાંચો', mission='અમારું મિશન',
  mission_text='શારીરિક રીતે શક્ય હોય તેટલું દુઃખ અટકાવવું, કોઈ સમાધાન વિના.',
  effort='પ્રયાસ', questions='કોઈ પ્રશ્ન?', questions_text='પ્રોજેક્ટ વિશે વધુ જાણવા info@proextinction.com પર લખો',
  action='પગલું ભરો', toc='આ પાના પર',
  ki='અંગ્રેજીમાંથી મશીન અનુવાદ (AI).',
  ki_tag='AI', progress='વાંચનની પ્રગતિ', home_link='Pro Extinction – મુખ્ય પાનું',
  efforts=['આંદોલનને વધારવું જેથી અબજો વર્ષોના દુઃખને અટકાવવું શક્ય બને.',
   'શારીરિક રીતે શક્ય હોય તેટલા પીડિતોને ભેદભાવ વિના સાર્વત્રિક મદદ. પ્રાણીઓને, શક્ય તેટલા પરગ્રહી જીવનને અને માણસોને.',
   'ફક્ત સંગઠિત કાર્યવાહી અને સક્રિયતા પર આધારિત. પીડિતોના ભોગે કોઈ ફરિયાદ નહીં.',
   'સંપૂર્ણપણે તાર્કિક, સહાનુભૂતિશીલ, નાસ્તિક, તર્કસંગત અને ન્યાયી.'],
  foot='Pro Extinction · Global', page_title='Pro Extinction'),
})
# Warning over blurred pictures on the suffering page: line, button.
VEIL = {
 'en': ('Picture contains depictions of extreme suffering', 'Show image'),
 'de': ('Das Bild zeigt extremes Leid', 'Bild anzeigen'),
 'pl': ('Zdjęcie przedstawia skrajne cierpienie', 'Pokaż zdjęcie'),
 'es': ('La imagen muestra sufrimiento extremo', 'Mostrar imagen'),
 'it': ("L'immagine mostra sofferenza estrema", 'Mostra immagine'),
 'fr': ("L'image montre une souffrance extrême", "Afficher l'image"),
 'pt': ('A imagem mostra sofrimento extremo', 'Mostrar imagem'),
 'ru': ('На изображении показаны крайние страдания', 'Показать изображение'),
 'zh': ('图片包含极端痛苦的画面', '显示图片'),
 'hi': ('इस तस्वीर में अत्यधिक पीड़ा दिखाई गई है', 'तस्वीर दिखाएँ'),
 'ar': ('تُظهر الصورة معاناة شديدة', 'عرض الصورة'),
 'bn': ('এই ছবিতে চরম কষ্টের দৃশ্য আছে', 'ছবি দেখান'),
 'ur': ('اس تصویر میں شدید تکلیف دکھائی گئی ہے', 'تصویر دکھائیں'),
 'id': ('Gambar ini menampilkan penderitaan ekstrem', 'Tampilkan gambar'),
 'ja': ('この画像には極度の苦しみが写っています', '画像を表示'),
 'tr': ('Görsel aşırı acı içeren sahneler gösteriyor', 'Görseli göster'),
 'vi': ('Hình ảnh có cảnh đau đớn tột cùng', 'Hiện hình ảnh'),
 'ko': ('이 이미지에는 극심한 고통이 담겨 있습니다', '이미지 보기'),
 'fa': ('این تصویر رنج شدید را نشان می‌دهد', 'نمایش تصویر'),
 'mr': ('या चित्रात तीव्र दुःख दाखवले आहे', 'चित्र दाखवा'),
 'te': ('ఈ చిత్రంలో తీవ్రమైన బాధ కనిపిస్తుంది', 'చిత్రాన్ని చూపించు'),
 'ta': ('இந்தப் படத்தில் கடுமையான துன்பம் காட்டப்படுகிறது', 'படத்தைக் காட்டு'),
 'sw': ('Picha hii inaonyesha mateso makali', 'Onyesha picha'),
 'th': ('ภาพนี้แสดงความทุกข์ทรมานอย่างรุนแรง', 'แสดงภาพ'),
 'nl': ('Afbeelding toont extreem lijden', 'Afbeelding tonen'),
 'uk': ('Зображення показує надзвичайні страждання', 'Показати зображення'),
 'tl': ('Ipinapakita ng larawan ang matinding pagdurusa', 'Ipakita ang larawan'),
 'pa': ('ਇਸ ਤਸਵੀਰ ਵਿੱਚ ਭਿਆਨਕ ਦੁੱਖ ਦਿਖਾਇਆ ਗਿਆ ਹੈ', 'ਤਸਵੀਰ ਦਿਖਾਓ'),
 'gu': ('આ ચિત્રમાં ભયાનક દુઃખ દર્શાવ્યું છે', 'ચિત્ર બતાવો'),
}
# Donate page: the IBAN and Ko-fi lines become two cards. Labels: card title, copy button, after copying, Ko-fi button.
IBAN, KOFI = 'DE80 1001 0178 0592 6010 31', 'https://ko-fi.com/abolishsuffering'
GIVE = {
 'en': ('Bank transfer', 'Copy IBAN', 'Copied', 'Donate on Ko-fi'),
 'de': ('Überweisung', 'IBAN kopieren', 'Kopiert', 'Auf Ko-fi spenden'),
 'pl': ('Przelew bankowy', 'Kopiuj IBAN', 'Skopiowano', 'Wesprzyj na Ko-fi'),
 'es': ('Transferencia bancaria', 'Copiar IBAN', 'Copiado', 'Donar en Ko-fi'),
 'it': ('Bonifico bancario', 'Copia IBAN', 'Copiato', 'Dona su Ko-fi'),
 'fr': ('Virement bancaire', "Copier l'IBAN", 'Copié', 'Faire un don sur Ko-fi'),
 'pt': ('Transferência bancária', 'Copiar IBAN', 'Copiado', 'Doar no Ko-fi'),
 'ru': ('Банковский перевод', 'Скопировать IBAN', 'Скопировано', 'Поддержать на Ko-fi'),
 'zh': ('银行转账', '复制 IBAN', '已复制', '在 Ko-fi 上捐款'),
 'hi': ('बैंक ट्रांसफ़र', 'IBAN कॉपी करें', 'कॉपी हो गया', 'Ko-fi पर दान करें'),
 'ar': ('تحويل بنكي', 'نسخ رقم IBAN', 'تم النسخ', 'تبرّع عبر Ko-fi'),
 'bn': ('ব্যাংক ট্রান্সফার', 'IBAN কপি করুন', 'কপি হয়েছে', 'Ko-fi-তে দান করুন'),
 'ur': ('بینک ٹرانسفر', 'IBAN کاپی کریں', 'کاپی ہو گیا', 'Ko-fi پر عطیہ کریں'),
 'id': ('Transfer bank', 'Salin IBAN', 'Tersalin', 'Donasi lewat Ko-fi'),
 'ja': ('銀行振込', 'IBAN をコピー', 'コピーしました', 'Ko-fi で寄付する'),
 'tr': ('Banka havalesi', "IBAN'ı kopyala", 'Kopyalandı', "Ko-fi'de bağış yap"),
 'vi': ('Chuyển khoản ngân hàng', 'Sao chép IBAN', 'Đã sao chép', 'Ủng hộ qua Ko-fi'),
 'ko': ('계좌 이체', 'IBAN 복사', '복사됨', 'Ko-fi로 후원하기'),
 'fa': ('واریز بانکی', 'کپی IBAN', 'کپی شد', 'کمک مالی در Ko-fi'),
 'mr': ('बँक ट्रान्सफर', 'IBAN कॉपी करा', 'कॉपी झाले', 'Ko-fi वर देणगी द्या'),
 'te': ('బ్యాంక్ బదిలీ', 'IBAN కాపీ చేయండి', 'కాపీ అయింది', 'Ko-fi లో విరాళం ఇవ్వండి'),
 'ta': ('வங்கிப் பரிமாற்றம்', 'IBAN-ஐ நகலெடு', 'நகலெடுக்கப்பட்டது', 'Ko-fi-இல் நன்கொடை அளி'),
 'sw': ('Uhamisho wa benki', 'Nakili IBAN', 'Imenakiliwa', 'Changia kupitia Ko-fi'),
 'th': ('โอนผ่านธนาคาร', 'คัดลอก IBAN', 'คัดลอกแล้ว', 'บริจาคผ่าน Ko-fi'),
 'nl': ('Bankoverschrijving', 'IBAN kopiëren', 'Gekopieerd', 'Doneer via Ko-fi'),
 'uk': ('Банківський переказ', 'Скопіювати IBAN', 'Скопійовано', 'Підтримати через Ko-fi'),
 'tl': ('Bank transfer', 'Kopyahin ang IBAN', 'Nakopya na', 'Mag-donate sa Ko-fi'),
 'pa': ('ਬੈਂਕ ਟ੍ਰਾਂਸਫ਼ਰ', 'IBAN ਕਾਪੀ ਕਰੋ', 'ਕਾਪੀ ਹੋ ਗਿਆ', 'Ko-fi ਰਾਹੀਂ ਦਾਨ ਕਰੋ'),
 'gu': ('બેંક ટ્રાન્સફર', 'IBAN કૉપિ કરો', 'કૉપિ થઈ ગયું', 'Ko-fi દ્વારા દાન કરો'),
}

def give_box(lang):
    bank, copy, done, kofi = GIVE.get(lang, GIVE['en'])
    plain = IBAN.replace(' ', '')
    js = ("var b=this;navigator.clipboard.writeText(b.dataset.iban).then(function(){b.classList.add('ok');"
          "setTimeout(function(){b.classList.remove('ok')},1800)})")
    return (f'<div class="give">'
            f'<section class="give-card"><p class="give-k mono">{esc(bank)}</p><p class="give-iban mono" dir="ltr" translate="no">{IBAN}</p>'
            f'<button class="give-btn" type="button" data-iban="{plain}" onclick="{js}"><span class="c">{esc(copy)}</span><span class="d" aria-live="polite">{esc(done)}</span></button></section>'
            f'<section class="give-card"><p class="give-k mono">Ko-fi</p><p class="give-url mono" dir="ltr" translate="no">ko-fi.com/abolishsuffering</p>'
            f'<a class="give-btn" href="{KOFI}" target="_blank" rel="noopener" aria-describedby="new-tab">{esc(kofi)} <span aria-hidden="true">&#8599;</span></a></section></div>')

def give_blocks(bl, lang):
    """Swap the IBAN line for the donate cards and drop the bare Ko-fi line (IT: its "Dona qui" line)."""
    out, done = [], False
    for b in bl:
        txt = b[1] if len(b) > 1 and isinstance(b[1], str) else ''
        hit = IBAN in txt or 'ko-fi.com' in txt.lower() or (lang == 'it' and txt.strip() == 'Dona qui')
        if hit:
            if not done: out.append(('give',)); done = True
            continue
        out.append(b)
    return out

# Label of the round "scroll to the top" button (aria-label and tooltip).
TOP = {
 'en': 'Scroll to the top',
 'de': 'Nach oben scrollen',
 'pl': 'Przewiń na górę',
 'es': 'Volver arriba',
 'it': "Torna all'inizio",
 'fr': 'Remonter en haut',
 'pt': 'Voltar ao topo',
 'ru': 'Наверх',
 'zh': '回到顶部',
 'hi': 'ऊपर जाएँ',
 'ar': 'العودة إلى الأعلى',
 'bn': 'উপরে যান',
 'ur': 'اوپر جائیں',
 'id': 'Kembali ke atas',
 'ja': 'ページの先頭へ',
 'tr': 'Başa dön',
 'vi': 'Lên đầu trang',
 'ko': '맨 위로',
 'fa': 'بازگشت به بالا',
 'mr': 'वर जा',
 'te': 'పైకి వెళ్ళండి',
 'ta': 'மேலே செல்',
 'sw': 'Rudi juu',
 'th': 'กลับขึ้นด้านบน',
 'nl': 'Naar boven',
 'uk': 'Нагору',
 'tl': 'Bumalik sa itaas',
 'pa': 'ਉੱਪਰ ਜਾਓ',
 'gu': 'ઉપર જાઓ',
}
def top_button(lang):
    return (f'<button class="to-top" type="button" aria-label="{esc(TOP[lang])}" title="{esc(TOP[lang])}" onclick="window.scrollTo(0,0)">'
            '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 19V5M5 12l7-7 7 7" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="square"/></svg></button>')

# Full FAQ search: placeholder, count, no hits, closing line ({mail}, {tiktok} become links), word for the mail link.
FAQ_FIND = {
 'en': ('Search the questions', '{n} of {t} questions', 'No question matches your search.', "Your question isn't listed? Contact us via {mail} or debate us on {tiktok}.", 'mail'),
 'de': ('Fragen durchsuchen', '{n} von {t} Fragen', 'Keine Frage passt zu deiner Suche.', 'Deine Frage ist nicht dabei? Schreib uns per {mail} oder diskutiere mit uns auf {tiktok}.', 'Mail'),
 'pl': ('Szukaj w pytaniach', '{n} z {t} pytań', 'Żadne pytanie nie pasuje do wyszukiwania.', 'Nie ma tu twojego pytania? Napisz do nas {mail} albo podyskutuj z nami na {tiktok}.', 'mailem'),
 'es': ('Buscar en las preguntas', '{n} de {t} preguntas', 'Ninguna pregunta coincide con tu búsqueda.', '¿No encuentras tu pregunta? Escríbenos por {mail} o debate con nosotros en {tiktok}.', 'correo'),
 'it': ('Cerca tra le domande', '{n} di {t} domande', 'Nessuna domanda corrisponde alla ricerca.', "La tua domanda non c'è? Scrivici via {mail} o discuti con noi su {tiktok}.", 'mail'),
 'fr': ('Rechercher dans les questions', '{n} sur {t} questions', 'Aucune question ne correspond à ta recherche.', "Ta question n'y est pas ? Écris-nous par {mail} ou débats avec nous sur {tiktok}.", 'mail'),
 'pt': ('Pesquisar perguntas', '{n} de {t} perguntas', 'Nenhuma pergunta corresponde à pesquisa.', 'Sua pergunta não está aqui? Fale conosco por {mail} ou debata conosco no {tiktok}.', 'e-mail'),
 'ru': ('Поиск по вопросам', '{n} из {t} вопросов', 'Ни один вопрос не подходит под запрос.', 'Вашего вопроса нет в списке? Напишите нам на {mail} или поспорьте с нами в {tiktok}.', 'почту'),
 'zh': ('搜索问题', '{t} 个问题中的 {n} 个', '没有匹配的问题。', '没有找到你的问题？通过{mail}联系我们，或在 {tiktok} 上和我们辩论。', '邮件'),
 'hi': ('सवाल खोजें', '{t} में से {n} सवाल', 'आपकी खोज से कोई सवाल नहीं मिला।', 'आपका सवाल सूची में नहीं है? हमें {mail} करें या {tiktok} पर हमसे बहस करें।', 'मेल'),
 'ar': ('ابحث في الأسئلة', '{n} من {t} سؤالًا', 'لا يوجد سؤال يطابق بحثك.', 'سؤالك غير موجود؟ راسلنا عبر {mail} أو ناقشنا على {tiktok}.', 'البريد'),
 'bn': ('প্রশ্ন খুঁজুন', '{t}টির মধ্যে {n}টি প্রশ্ন', 'আপনার খোঁজের সাথে কোনো প্রশ্ন মেলেনি।', 'আপনার প্রশ্ন তালিকায় নেই? {mail}-এ আমাদের লিখুন বা {tiktok}-এ আমাদের সাথে বিতর্ক করুন।', 'মেইল'),
 'ur': ('سوالات تلاش کریں', '{t} میں سے {n} سوال', 'آپ کی تلاش سے کوئی سوال نہیں ملا۔', 'آپ کا سوال فہرست میں نہیں؟ ہمیں {mail} کریں یا {tiktok} پر ہم سے بحث کریں۔', 'میل'),
 'id': ('Cari pertanyaan', '{n} dari {t} pertanyaan', 'Tidak ada pertanyaan yang cocok.', 'Pertanyaanmu tidak ada? Hubungi kami lewat {mail} atau berdebat dengan kami di {tiktok}.', 'email'),
 'ja': ('質問を検索', '{t} 件中 {n} 件', '検索に一致する質問はありません。', '質問が見つかりませんか？{mail}で連絡するか、{tiktok}で私たちと議論してください。', 'メール'),
 'tr': ('Sorularda ara', '{t} sorudan {n} tanesi', 'Aramana uyan soru yok.', 'Sorun listede yok mu? Bize {mail} ile yaz ya da {tiktok} üzerinde bizimle tartış.', 'e-posta'),
 'vi': ('Tìm câu hỏi', '{n} / {t} câu hỏi', 'Không có câu hỏi nào khớp.', 'Không thấy câu hỏi của bạn? Liên hệ qua {mail} hoặc tranh luận với chúng tôi trên {tiktok}.', 'email'),
 'ko': ('질문 검색', '{t}개 중 {n}개 질문', '검색과 일치하는 질문이 없습니다.', '질문이 목록에 없나요? {mail}로 연락하거나 {tiktok}에서 우리와 토론하세요.', '메일'),
 'fa': ('جست‌وجو در پرسش‌ها', '{n} از {t} پرسش', 'هیچ پرسشی با جست‌وجوی شما جور نیست.', 'پرسش شما در فهرست نیست؟ از راه {mail} با ما تماس بگیرید یا در {tiktok} با ما بحث کنید.', 'ایمیل'),
 'mr': ('प्रश्न शोधा', '{t} पैकी {n} प्रश्न', 'तुमच्या शोधाशी जुळणारा प्रश्न नाही.', 'तुमचा प्रश्न यादीत नाही? आम्हाला {mail} करा किंवा {tiktok} वर आमच्याशी वाद घाला.', 'मेल'),
 'te': ('ప్రశ్నలను వెతకండి', '{t} లో {n} ప్రశ్నలు', 'మీ శోధనకు సరిపోయే ప్రశ్న లేదు.', 'మీ ప్రశ్న జాబితాలో లేదా? {mail} ద్వారా మమ్మల్ని సంప్రదించండి లేదా {tiktok} లో మాతో చర్చించండి.', 'మెయిల్'),
 'ta': ('கேள்விகளில் தேடு', '{t} இல் {n} கேள்விகள்', 'உங்கள் தேடலுக்குப் பொருந்தும் கேள்வி இல்லை.', 'உங்கள் கேள்வி பட்டியலில் இல்லையா? {mail} மூலம் எங்களைத் தொடர்புகொள்ளுங்கள் அல்லது {tiktok} இல் எங்களுடன் விவாதியுங்கள்.', 'மின்னஞ்சல்'),
 'sw': ('Tafuta maswali', 'Maswali {n} kati ya {t}', 'Hakuna swali linalolingana na utafutaji wako.', 'Swali lako halipo? Wasiliana nasi kwa {mail} au jadiliana nasi kwenye {tiktok}.', 'barua pepe'),
 'th': ('ค้นหาคำถาม', '{n} จาก {t} คำถาม', 'ไม่มีคำถามที่ตรงกับการค้นหา', 'ไม่พบคำถามของคุณ? ติดต่อเราทาง{mail} หรือมาโต้แย้งกับเราบน {tiktok}', 'อีเมล'),
 'nl': ('Vragen doorzoeken', '{n} van {t} vragen', 'Geen vraag past bij je zoekopdracht.', 'Staat je vraag er niet bij? Neem contact op via {mail} of ga met ons in debat op {tiktok}.', 'e-mail'),
 'uk': ('Пошук запитань', '{n} з {t} запитань', 'Жодне запитання не відповідає пошуку.', 'Вашого запитання немає в списку? Напишіть нам на {mail} або подискутуйте з нами в {tiktok}.', 'пошту'),
 'tl': ('Maghanap ng tanong', '{n} sa {t} na tanong', 'Walang tanong na tugma sa hinanap mo.', 'Wala sa listahan ang tanong mo? Makipag-ugnayan sa amin sa {mail} o makipagdebate sa amin sa {tiktok}.', 'email'),
 'pa': ('ਸਵਾਲ ਖੋਜੋ', '{t} ਵਿੱਚੋਂ {n} ਸਵਾਲ', 'ਤੁਹਾਡੀ ਖੋਜ ਨਾਲ ਮੇਲ ਖਾਂਦਾ ਕੋਈ ਸਵਾਲ ਨਹੀਂ।', 'ਤੁਹਾਡਾ ਸਵਾਲ ਸੂਚੀ ਵਿੱਚ ਨਹੀਂ? ਸਾਨੂੰ {mail} ਕਰੋ ਜਾਂ {tiktok} \'ਤੇ ਸਾਡੇ ਨਾਲ ਬਹਿਸ ਕਰੋ।', 'ਈਮੇਲ'),
 'gu': ('પ્રશ્નો શોધો', '{t}માંથી {n} પ્રશ્નો', 'તમારી શોધ સાથે મેળ ખાતો કોઈ પ્રશ્ન નથી.', 'તમારો પ્રશ્ન યાદીમાં નથી? અમને {mail} કરો અથવા {tiktok} પર અમારી સાથે ચર્ચા કરો.', 'ઈમેલ'),
}
FAQ_JS = (ROOT / 'tools' / 'faqsearch.js').read_text(encoding='utf-8')

DISCORD = 'https://discord.gg/nb2K8y846R'
DEBATE_DISCORD = 'https://discord.gg/887fVYCDsN'

def link_attrs(href):
    """Social and messaging platforms open in a new tab; screen readers hear so (the note in footer())."""
    host = (urllib.parse.urlsplit(href).hostname or '').lower()
    platforms = ('whatsapp.com', 'whatsapp.net', 'wa.me', 'discord.gg', 'discord.com', 'discordapp.com',
                 'tiktok.com', 'instagram.com', 'youtube.com', 'youtu.be', 'facebook.com', 'fb.com',
                 'x.com', 'twitter.com', 'threads.net', 'linkedin.com', 'reddit.com', 't.me',
                 'telegram.me', 'telegram.org', 'twitch.tv', 'pinterest.com', 'bsky.app')
    new_tab = any(host == platform or host.endswith('.' + platform) for platform in platforms)
    return ' target="_blank" rel="noopener" aria-describedby="new-tab"' if new_tab else ' rel="noopener"'
NEW_TAB = {
 'en': 'Opens in a new tab', 'de': 'Öffnet in einem neuen Tab', 'pl': 'Otwiera się w nowej karcie', 'es': 'Se abre en una pestaña nueva',
 'it': 'Si apre in una nuova scheda', 'fr': "S'ouvre dans un nouvel onglet", 'pt': 'Abre em uma nova aba', 'ru': 'Открывается в новой вкладке',
 'zh': '在新标签页中打开', 'hi': 'नए टैब में खुलता है', 'ar': 'يفتح في علامة تبويب جديدة', 'bn': 'নতুন ট্যাবে খোলে', 'ur': 'نئے ٹیب میں کھلتا ہے',
 'id': 'Terbuka di tab baru', 'ja': '新しいタブで開きます', 'tr': 'Yeni sekmede açılır', 'vi': 'Mở trong thẻ mới', 'ko': '새 탭에서 열립니다',
 'fa': 'در زبانه\u200cای تازه باز می\u200cشود', 'mr': 'नवीन टॅबमध्ये उघडते', 'te': 'కొత్త ట్యాబ్‌లో తెరుచుకుంటుంది', 'ta': 'புதிய தாவலில் திறக்கும்',
 'sw': 'Hufunguka kwenye kichupo kipya', 'th': 'เปิดในแท็บใหม่', 'nl': 'Opent in een nieuw tabblad', 'uk': 'Відкривається в новій вкладці',
 'tl': 'Bubukas sa bagong tab', 'pa': 'ਨਵੀਂ ਟੈਬ ਵਿੱਚ ਖੁੱਲ੍ਹਦਾ ਹੈ', 'gu': 'નવા ટૅબમાં ખૂલે છે',
}

# Debate server: open to everyone, pro-lifers included. (heading, text, button) per language; shown on the home and contact pages.
DEBATE = {
 'en': ('Debate with us', 'Our debate server on Discord is open to everyone, also to people who disagree with us. Pro-lifers are welcome: bring your best arguments.', 'Debate on Discord'),
 'de': ('Diskutiere mit uns', 'Unser Debatten-Server auf Discord ist für alle offen, auch für Menschen, die anderer Meinung sind. Pro-Lifer sind willkommen: Bring deine besten Argumente mit.', 'Zur Debatte auf Discord'),
 'pl': ('Dyskutuj z nami', 'Nasz serwer debat na Discordzie jest otwarty dla wszystkich, także dla osób, które się z nami nie zgadzają. Pro-liferzy są mile widziani: przynieś swoje najlepsze argumenty.', 'Debata na Discordzie'),
 'es': ('Debate con nosotros', 'Nuestro servidor de debate en Discord está abierto a todos, también a quienes no están de acuerdo con nosotros. Los pro-life son bienvenidos: trae tus mejores argumentos.', 'Debatir en Discord'),
 'it': ('Discuti con noi', "Il nostro server di dibattito su Discord è aperto a tutti, anche a chi non è d'accordo con noi. I pro-life sono benvenuti: porta i tuoi argomenti migliori.", 'Dibatti su Discord'),
 'fr': ('Débats avec nous', "Notre serveur de débat sur Discord est ouvert à tous, aussi aux personnes qui ne sont pas d'accord avec nous. Les pro-life sont les bienvenus : apporte tes meilleurs arguments.", 'Débattre sur Discord'),
 'pt': ('Debata conosco', 'Nosso servidor de debate no Discord é aberto a todos, também a quem discorda de nós. Os pró-vida são bem-vindos: traga seus melhores argumentos.', 'Debater no Discord'),
 'nl': ('Debatteer met ons', 'Onze debatserver op Discord staat open voor iedereen, ook voor mensen die het niet met ons eens zijn. Pro-lifers zijn welkom: kom met je beste argumenten.', 'Debatteren op Discord'),
 'ru': ('Поспорь с нами', 'Наш сервер для дебатов в Discord открыт для всех, в том числе для тех, кто с нами не согласен. Сторонники pro-life тоже приглашены: приходите с лучшими аргументами.', 'Дебаты в Discord'),
 'uk': ('Подискутуй з нами', 'Наш сервер для дебатів у Discord відкритий для всіх, зокрема для тих, хто з нами не згоден. Прихильників pro-life теж запрошуємо: приходьте з найкращими аргументами.', 'Дебати в Discord'),
 'tr': ('Bizimle tartış', "Discord'daki tartışma sunucumuz herkese açık, bizimle aynı fikirde olmayanlara da. Pro-life düşünenler de davetli: en iyi argümanlarını getir.", "Discord'da tartış"),
 'id': ('Berdebat dengan kami', 'Server debat kami di Discord terbuka untuk semua orang, juga untuk yang tidak setuju dengan kami. Kaum pro-life juga disambut: bawa argumen terbaikmu.', 'Debat di Discord'),
 'tl': ('Makipagdebate sa amin', 'Bukas sa lahat ang aming debate server sa Discord, pati sa mga hindi sang-ayon sa amin. Welcome din ang mga pro-life: dalhin ang pinakamahuhusay mong argumento.', 'Makipagdebate sa Discord'),
 'vi': ('Tranh luận với chúng tôi', 'Máy chủ tranh luận của chúng tôi trên Discord mở cho tất cả mọi người, kể cả những ai không đồng ý với chúng tôi. Người ủng hộ pro-life cũng được chào đón: hãy mang theo những lập luận tốt nhất của bạn.', 'Tranh luận trên Discord'),
 'sw': ('Jadiliana nasi', 'Seva yetu ya mijadala kwenye Discord iko wazi kwa kila mtu, hata kwa wasiokubaliana nasi. Wafuasi wa pro-life wanakaribishwa pia: leta hoja zako bora.', 'Jadiliana kwenye Discord'),
 'zh': ('来和我们辩论', '我们在 Discord 上的辩论服务器向所有人开放，也欢迎不同意我们观点的人。pro-life 支持者同样欢迎：带上你最好的论点。', '在 Discord 上辩论'),
 'ja': ('私たちと議論しよう', 'Discord の討論サーバーは誰でも参加できます。私たちに反対する人も歓迎です。pro-life の人もぜひ、いちばん強い論拠を持ってきてください。', 'Discord で議論する'),
 'ko': ('우리와 토론하세요', '디스코드의 토론 서버는 우리와 생각이 다른 사람을 포함해 누구에게나 열려 있습니다. pro-life 입장인 분들도 환영합니다. 가장 좋은 논거를 가져오세요.', '디스코드에서 토론하기'),
 'th': ('มาถกเถียงกับเรา', 'เซิร์ฟเวอร์ถกเถียงของเราบน Discord เปิดให้ทุกคน รวมถึงคนที่ไม่เห็นด้วยกับเรา ฝ่าย pro-life ก็ยินดีต้อนรับ นำข้อโต้แย้งที่ดีที่สุดของคุณมาเลย', 'ถกเถียงบน Discord'),
 'hi': ('हमसे बहस करें', 'Discord पर हमारा बहस सर्वर सबके लिए खुला है, उनके लिए भी जो हमसे असहमत हैं। pro-life लोगों का भी स्वागत है: अपने सबसे अच्छे तर्क लेकर आइए।', 'Discord पर बहस करें'),
 'mr': ('आमच्याशी वाद घाला', 'Discord वरील आमचा वादविवाद सर्व्हर सगळ्यांसाठी खुला आहे, आमच्याशी असहमत असणाऱ्यांसाठीही. pro-life लोकांचेही स्वागत आहे: तुमचे सर्वोत्तम युक्तिवाद घेऊन या.', 'Discord वर वाद घाला'),
 'bn': ('আমাদের সাথে বিতর্ক করুন', 'Discord-এ আমাদের বিতর্ক সার্ভার সবার জন্য খোলা, যারা আমাদের সাথে একমত নন তাদের জন্যও। pro-life মানুষদেরও স্বাগতম: আপনার সেরা যুক্তি নিয়ে আসুন।', 'Discord-এ বিতর্ক করুন'),
 'te': ('మాతో చర్చించండి', 'Discord లోని మా చర్చా సర్వర్ అందరికీ తెరిచి ఉంది, మాతో విభేదించేవారికి కూడా. pro-life వారికి కూడా స్వాగతం: మీ ఉత్తమ వాదనలతో రండి.', 'Discord లో చర్చించండి'),
 'ta': ('எங்களுடன் விவாதியுங்கள்', 'Discord இல் உள்ள எங்கள் விவாத சர்வர் எல்லோருக்கும் திறந்திருக்கிறது, எங்களுடன் உடன்படாதவர்களுக்கும். pro-life ஆதரவாளர்களும் வரவேற்கப்படுகிறார்கள்: உங்கள் சிறந்த வாதங்களுடன் வாருங்கள்.', 'Discord இல் விவாதியுங்கள்'),
 'pa': ('ਸਾਡੇ ਨਾਲ ਬਹਿਸ ਕਰੋ', 'Discord ਉੱਤੇ ਸਾਡਾ ਬਹਿਸ ਸਰਵਰ ਸਭ ਲਈ ਖੁੱਲ੍ਹਾ ਹੈ, ਉਨ੍ਹਾਂ ਲਈ ਵੀ ਜੋ ਸਾਡੇ ਨਾਲ ਸਹਿਮਤ ਨਹੀਂ। pro-life ਲੋਕਾਂ ਦਾ ਵੀ ਸਵਾਗਤ ਹੈ: ਆਪਣੀਆਂ ਸਭ ਤੋਂ ਵਧੀਆ ਦਲੀਲਾਂ ਲੈ ਕੇ ਆਓ।', 'Discord ਉੱਤੇ ਬਹਿਸ ਕਰੋ'),
 'gu': ('અમારી સાથે ચર્ચા કરો', 'Discord પરનું અમારું ચર્ચા સર્વર બધા માટે ખુલ્લું છે, અમારી સાથે અસહમત લોકો માટે પણ. pro-life લોકોનું પણ સ્વાગત છે: તમારી શ્રેષ્ઠ દલીલો લઈને આવો.', 'Discord પર ચર્ચા કરો'),
 'ar': ('ناقشنا', 'خادم النقاش الخاص بنا على Discord مفتوح للجميع، حتى لمن لا يتفق معنا. أنصار pro-life مرحب بهم أيضا: أحضر أفضل حججك.', 'ناقش على Discord'),
 'ur': ('ہم سے بحث کریں', 'Discord پر ہمارا بحث کا سرور سب کے لیے کھلا ہے، ان کے لیے بھی جو ہم سے متفق نہیں۔ pro-life لوگوں کا بھی خیرمقدم ہے: اپنے بہترین دلائل لے کر آئیں۔', 'Discord پر بحث کریں'),
 'fa': ('با ما بحث کن', 'سرور بحث ما در Discord برای همه باز است، حتی برای کسانی که با ما مخالف\u200cاند. طرفداران pro-life هم خوش آمدند: بهترین استدلال\u200cهایت را بیاور.', 'بحث در Discord'),
}

def debate_html(lang, tag='h2'):
    """The debate server: who it is for and a button to join."""
    h, text, btn = DEBATE.get(lang, DEBATE['en'])
    return (f'<{tag}>{esc(h)}</{tag}><p>{esc(text)}</p>'
            f'<p class="cta-links"><a class="btn" href="{DEBATE_DISCORD}"{link_attrs(DEBATE_DISCORD)}>{icon("discord")}{esc(btn)}</a></p>')

WHATSAPP = {l: 'https://chat.whatsapp.com/KvNQxQiyCl4GO3w3J1w5Gb' for l in LANGS}   # one group for every language (October 2026)
EMAIL = 'info@proextinction.com'

# Before the WhatsApp link: yes/no questions with an expected answer each. All as expected: the link appears.
# Otherwise a short note with pages to read and the debate server. Answers stay in the browser, nothing is sent or stored.
# Languages without an entry link to WhatsApp directly. Without JavaScript the button is a plain link, as before.
GATE_ANSWERS = [True, True, False, True, False]   # the expected answer to each question, the same in every language
JOIN_GATE = {
 'en': dict(
  title='Before you join',
  intro='Our WhatsApp group is for activists. Please answer these short questions.',
  yes='Yes',
  no='No',
  go='Continue',
  close='Close',
  missing='Please answer every question.',
  ok='Thank you! You can join our WhatsApp group now.',
  ok_btn='Join the WhatsApp group',
  fail='Thank you for your answers. Our activist group may not be the right place for you yet. Read more on our pages, or talk with us on our debate server, which is open to everyone.',
  qs=list(zip(['Human extinction would be the worst thing possible, because, to be fair, as the only intelligent species, we have to make other life go extinct first. Do you agree?', 'Do you agree that all suffering, of humans and of animals, should end, and that only the extinction of all sentient life can end it for good?', 'Do you believe in a god?', 'Do you want to actively help, for example by making content, translating, debating or organising?', 'Should humanity stop reproducing now?'], GATE_ANSWERS))),
 'de': dict(
  title='Bevor du beitrittst',
  intro='Unsere WhatsApp-Gruppe ist für Aktivistinnen und Aktivisten. Bitte beantworte diese kurzen Fragen.',
  yes='Ja',
  no='Nein',
  go='Weiter',
  close='Schließen',
  missing='Bitte beantworte jede Frage.',
  ok='Danke! Du kannst jetzt unserer WhatsApp-Gruppe beitreten.',
  ok_btn='Der WhatsApp-Gruppe beitreten',
  fail='Danke für deine Antworten. Unsere Aktivistengruppe ist vielleicht noch nicht der richtige Ort für dich. Lies mehr auf unseren Seiten oder sprich mit uns auf unserem Debatten-Server, der für alle offen ist.',
  qs=list(zip(['Das Aussterben der Menschheit wäre das Schlimmste, was passieren kann, denn als einzige intelligente Spezies müssen wir fairerweise zuerst anderes Leben aussterben lassen. Stimmst du zu?', 'Stimmst du zu, dass alles Leid, von Menschen und von Tieren, enden soll und dass nur das Aussterben allen fühlenden Lebens es für immer beenden kann?', 'Glaubst du an einen Gott?', 'Willst du aktiv mithelfen, zum Beispiel mit Inhalten, Übersetzungen, Debatten oder Organisation?', 'Sollte die Menschheit jetzt aufhören, sich fortzupflanzen?'], GATE_ANSWERS))),
 'pl': dict(
  title='Zanim dołączysz',
  intro='Nasza grupa na WhatsAppie jest dla aktywistów. Odpowiedz na te krótkie pytania.',
  yes='Tak',
  no='Nie',
  go='Dalej',
  close='Zamknij',
  missing='Odpowiedz na każde pytanie.',
  ok='Dziękujemy! Możesz teraz dołączyć do naszej grupy na WhatsAppie.',
  ok_btn='Dołącz do grupy na WhatsAppie',
  fail='Dziękujemy za odpowiedzi. Nasza grupa aktywistów może nie być jeszcze odpowiednim miejscem dla ciebie. Przeczytaj więcej na naszych stronach albo porozmawiaj z nami na naszym serwerze debat, który jest otwarty dla wszystkich.',
  qs=list(zip(['Wyginięcie ludzkości byłoby najgorszą możliwą rzeczą, bo jako jedyny inteligentny gatunek musimy uczciwie najpierw doprowadzić do wyginięcia innego życia. Zgadzasz się?', 'Czy zgadzasz się, że całe cierpienie, ludzi i zwierząt, powinno się skończyć i że tylko wyginięcie całego czującego życia może je zakończyć na zawsze?', 'Czy wierzysz w boga?', 'Czy chcesz aktywnie pomagać, na przykład tworząc treści, tłumacząc, debatując albo organizując?', 'Czy ludzkość powinna teraz przestać się rozmnażać?'], GATE_ANSWERS))),
 'es': dict(
  title='Antes de unirte',
  intro='Nuestro grupo de WhatsApp es para activistas. Responde estas preguntas cortas.',
  yes='Sí',
  no='No',
  go='Continuar',
  close='Cerrar',
  missing='Responde todas las preguntas.',
  ok='¡Gracias! Ya puedes unirte a nuestro grupo de WhatsApp.',
  ok_btn='Unirme al grupo de WhatsApp',
  fail='Gracias por tus respuestas. Puede que nuestro grupo de activistas todavía no sea el lugar adecuado para ti. Lee más en nuestras páginas o habla con nosotros en nuestro servidor de debate, que está abierto a todos.',
  qs=list(zip(['La extinción humana sería lo peor que podría pasar, porque, para ser justos, como única especie inteligente tenemos que hacer que la otra vida se extinga primero. ¿Estás de acuerdo?', '¿Estás de acuerdo en que todo el sufrimiento, de humanos y de animales, debe terminar, y en que solo la extinción de toda la vida sintiente puede terminarlo para siempre?', '¿Crees en un dios?', '¿Quieres ayudar de forma activa, por ejemplo creando contenido, traduciendo, debatiendo u organizando?', '¿Debería la humanidad dejar de reproducirse ya?'], GATE_ANSWERS))),
 'it': dict(
  title='Prima di unirti',
  intro='Il nostro gruppo WhatsApp è per attivisti. Rispondi a queste brevi domande.',
  yes='Sì',
  no='No',
  go='Continua',
  close='Chiudi',
  missing='Rispondi a tutte le domande.',
  ok='Grazie! Ora puoi unirti al nostro gruppo WhatsApp.',
  ok_btn='Unisciti al gruppo WhatsApp',
  fail='Grazie per le tue risposte. Il nostro gruppo di attivisti forse non è ancora il posto giusto per te. Leggi di più sulle nostre pagine o parla con noi sul nostro server di dibattito, aperto a tutti.',
  qs=list(zip(["L'estinzione umana sarebbe la cosa peggiore possibile, perché, per essere giusti, come unica specie intelligente dobbiamo prima far estinguere le altre forme di vita. Sei d'accordo?", "Sei d'accordo che tutta la sofferenza, degli esseri umani e degli animali, debba finire, e che solo l'estinzione di tutta la vita senziente possa porvi fine per sempre?", 'Credi in un dio?', 'Vuoi aiutare attivamente, per esempio creando contenuti, traducendo, partecipando ai dibattiti o organizzando?', "L'umanità dovrebbe smettere di riprodursi adesso?"], GATE_ANSWERS))),
 'fr': dict(
  title='Avant de nous rejoindre',
  intro='Notre groupe WhatsApp est pour les activistes. Réponds à ces courtes questions.',
  yes='Oui',
  no='Non',
  go='Continuer',
  close='Fermer',
  missing='Réponds à toutes les questions.',
  ok='Merci ! Tu peux maintenant rejoindre notre groupe WhatsApp.',
  ok_btn='Rejoindre le groupe WhatsApp',
  fail="Merci pour tes réponses. Notre groupe d'activistes n'est peut-être pas encore le bon endroit pour toi. Lis-en plus sur nos pages, ou parle avec nous sur notre serveur de débat, ouvert à tous.",
  qs=list(zip(["L'extinction humaine serait la pire chose possible, parce que, pour être justes, en tant que seule espèce intelligente, nous devons d'abord faire disparaître les autres formes de vie. Es-tu d'accord ?", "Es-tu d'accord pour dire que toute souffrance, humaine et animale, doit cesser, et que seule l'extinction de toute vie sensible peut y mettre fin pour toujours ?", 'Crois-tu en un dieu ?', 'Veux-tu aider activement, par exemple en créant du contenu, en traduisant, en débattant ou en organisant ?', "L'humanité devrait-elle arrêter de se reproduire dès maintenant ?"], GATE_ANSWERS))),
 'pt': dict(
  title='Antes de entrar',
  intro='Nosso grupo de WhatsApp é para ativistas. Responda a estas perguntas curtas.',
  yes='Sim',
  no='Não',
  go='Continuar',
  close='Fechar',
  missing='Responda a todas as perguntas.',
  ok='Obrigado! Agora você pode entrar no nosso grupo de WhatsApp.',
  ok_btn='Entrar no grupo de WhatsApp',
  fail='Obrigado pelas suas respostas. Nosso grupo de ativistas talvez ainda não seja o lugar certo para você. Leia mais nas nossas páginas ou converse conosco no nosso servidor de debate, aberto a todos.',
  qs=list(zip(['A extinção humana seria a pior coisa possível, porque, para sermos justos, como única espécie inteligente, temos de fazer as outras formas de vida se extinguirem primeiro. Você concorda?', 'Você concorda que todo sofrimento, de humanos e de animais, deve acabar, e que só a extinção de toda a vida senciente pode acabar com ele para sempre?', 'Você acredita em um deus?', 'Você quer ajudar ativamente, por exemplo criando conteúdo, traduzindo, debatendo ou organizando?', 'A humanidade deveria parar de se reproduzir agora?'], GATE_ANSWERS))),
 'nl': dict(
  title='Voordat je lid wordt',
  intro='Onze WhatsApp-groep is voor activisten. Beantwoord deze korte vragen.',
  yes='Ja',
  no='Nee',
  go='Verder',
  close='Sluiten',
  missing='Beantwoord elke vraag.',
  ok='Dank je! Je kunt nu lid worden van onze WhatsApp-groep.',
  ok_btn='Lid worden van de WhatsApp-groep',
  fail="Dank je voor je antwoorden. Onze activistengroep is misschien nog niet de juiste plek voor jou. Lees meer op onze pagina's of praat met ons op onze debatserver, die voor iedereen open staat.",
  qs=list(zip(['Het uitsterven van de mens zou het ergste zijn wat er kan gebeuren, want om eerlijk te zijn moeten wij als enige intelligente soort eerst ander leven laten uitsterven. Ben je het daarmee eens?', 'Ben je het ermee eens dat al het lijden, van mensen en van dieren, moet stoppen, en dat alleen het uitsterven van al het voelende leven het voorgoed kan beëindigen?', 'Geloof je in een god?', 'Wil je actief helpen, bijvoorbeeld door content te maken, te vertalen, te debatteren of te organiseren?', 'Moet de mensheid nu stoppen met zich voort te planten?'], GATE_ANSWERS))),
 'ru': dict(
  title='Прежде чем вступить',
  intro='Наша группа в WhatsApp для активистов. Пожалуйста, ответь на эти короткие вопросы.',
  yes='Да',
  no='Нет',
  go='Дальше',
  close='Закрыть',
  missing='Пожалуйста, ответь на все вопросы.',
  ok='Спасибо! Теперь ты можешь вступить в нашу группу в WhatsApp.',
  ok_btn='Вступить в группу WhatsApp',
  fail='Спасибо за ответы. Возможно, наша группа активистов пока тебе не подходит. Прочитай больше на наших страницах или поговори с нами на нашем сервере для дебатов, он открыт для всех.',
  qs=list(zip(['Вымирание человечества было бы худшим из возможного, потому что, если быть честными, как единственный разумный вид мы должны сначала привести к вымиранию другую жизнь. Ты согласен?', 'Ты согласен, что все страдания, людей и животных, должны прекратиться и что только вымирание всей чувствующей жизни может покончить с ними навсегда?', 'Ты веришь в бога?', 'Ты хочешь активно помогать, например создавать контент, переводить, участвовать в дебатах или организовывать?', 'Должно ли человечество прекратить размножаться прямо сейчас?'], GATE_ANSWERS))),
 'uk': dict(
  title='Перш ніж приєднатися',
  intro='Наша група у WhatsApp для активістів. Будь ласка, дай відповідь на ці короткі запитання.',
  yes='Так',
  no='Ні',
  go='Далі',
  close='Закрити',
  missing='Будь ласка, дай відповідь на кожне запитання.',
  ok='Дякуємо! Тепер ти можеш приєднатися до нашої групи у WhatsApp.',
  ok_btn='Приєднатися до групи WhatsApp',
  fail='Дякуємо за відповіді. Можливо, наша група активістів поки що тобі не підходить. Прочитай більше на наших сторінках або поговори з нами на нашому сервері для дебатів, він відкритий для всіх.',
  qs=list(zip(['Вимирання людства було б найгіршим із можливого, бо, якщо чесно, як єдиний розумний вид ми маємо спершу довести до вимирання інше життя. Ти згоден?', 'Ти згоден, що всі страждання, людей і тварин, мають припинитися і що лише вимирання всього чутливого життя може покласти їм край назавжди?', 'Ти віриш у бога?', 'Ти хочеш активно допомагати, наприклад створювати контент, перекладати, брати участь у дебатах чи організовувати?', 'Чи має людство припинити розмножуватися вже зараз?'], GATE_ANSWERS))),
 'tr': dict(
  title='Katılmadan önce',
  intro='WhatsApp grubumuz aktivistler için. Lütfen bu kısa soruları yanıtla.',
  yes='Evet',
  no='Hayır',
  go='Devam',
  close='Kapat',
  missing='Lütfen her soruyu yanıtla.',
  ok='Teşekkürler! Artık WhatsApp grubumuza katılabilirsin.',
  ok_btn='WhatsApp grubuna katıl',
  fail='Yanıtların için teşekkürler. Aktivist grubumuz henüz senin için doğru yer olmayabilir. Sayfalarımızda daha fazlasını oku ya da herkese açık tartışma sunucumuzda bizimle konuş.',
  qs=list(zip(['İnsanlığın yok olması mümkün olan en kötü şey olurdu, çünkü adil olmak gerekirse tek zeki tür olarak önce diğer yaşamın yok olmasını sağlamalıyız. Katılıyor musun?', 'Tüm acının, insanların ve hayvanların acısının, bitmesi gerektiğine ve bunu ancak tüm hisseden yaşamın yok olmasının sonsuza dek bitirebileceğine katılıyor musun?', 'Bir tanrıya inanıyor musun?', 'Aktif olarak yardım etmek istiyor musun, örneğin içerik üreterek, çeviri yaparak, tartışarak ya da organize ederek?', 'İnsanlık şimdi üremeyi bırakmalı mı?'], GATE_ANSWERS))),
 'id': dict(
  title='Sebelum bergabung',
  intro='Grup WhatsApp kami untuk aktivis. Tolong jawab pertanyaan singkat ini.',
  yes='Ya',
  no='Tidak',
  go='Lanjut',
  close='Tutup',
  missing='Tolong jawab setiap pertanyaan.',
  ok='Terima kasih! Sekarang kamu bisa bergabung dengan grup WhatsApp kami.',
  ok_btn='Gabung ke grup WhatsApp',
  fail='Terima kasih atas jawabanmu. Grup aktivis kami mungkin belum tempat yang tepat untukmu. Baca lebih lanjut di halaman kami, atau bicaralah dengan kami di server debat kami yang terbuka untuk semua orang.',
  qs=list(zip(['Kepunahan manusia adalah hal terburuk yang mungkin terjadi, karena, agar adil, sebagai satu-satunya spesies cerdas kita harus membuat kehidupan lain punah lebih dulu. Apakah kamu setuju?', 'Apakah kamu setuju bahwa semua penderitaan, manusia dan hewan, harus berakhir, dan bahwa hanya kepunahan semua kehidupan yang bisa merasa yang dapat mengakhirinya untuk selamanya?', 'Apakah kamu percaya pada tuhan?', 'Apakah kamu ingin membantu secara aktif, misalnya dengan membuat konten, menerjemahkan, berdebat, atau mengorganisasi?', 'Haruskah manusia berhenti bereproduksi sekarang?'], GATE_ANSWERS))),
 'tl': dict(
  title='Bago ka sumali',
  intro='Para sa mga aktibista ang aming WhatsApp group. Pakisagot ang maiikling tanong na ito.',
  yes='Oo',
  no='Hindi',
  go='Magpatuloy',
  close='Isara',
  missing='Pakisagot ang bawat tanong.',
  ok='Salamat! Puwede ka nang sumali sa aming WhatsApp group.',
  ok_btn='Sumali sa WhatsApp group',
  fail='Salamat sa iyong mga sagot. Baka hindi pa para sa iyo ang aming grupo ng mga aktibista. Magbasa pa sa aming mga pahina, o makipag-usap sa amin sa aming debate server na bukas sa lahat.',
  qs=list(zip(['Ang pagkalipol ng tao ang magiging pinakamasamang posibleng mangyari, dahil, para maging patas, bilang tanging matalinong uri, kailangan muna nating ipalipol ang ibang buhay. Sang-ayon ka ba?', 'Sang-ayon ka ba na dapat matapos ang lahat ng pagdurusa, ng tao at ng hayop, at na ang pagkalipol lamang ng lahat ng buhay na nakadarama ang makapagtatapos dito nang tuluyan?', 'Naniniwala ka ba sa isang diyos?', 'Gusto mo bang aktibong tumulong, halimbawa sa paggawa ng content, pagsasalin, pakikipagdebate o pag-oorganisa?', 'Dapat na bang tumigil ang sangkatauhan sa pagpaparami ngayon?'], GATE_ANSWERS))),
 'vi': dict(
  title='Trước khi tham gia',
  intro='Nhóm WhatsApp của chúng tôi dành cho các nhà hoạt động. Hãy trả lời vài câu hỏi ngắn này.',
  yes='Có',
  no='Không',
  go='Tiếp tục',
  close='Đóng',
  missing='Hãy trả lời tất cả các câu hỏi.',
  ok='Cảm ơn bạn! Giờ bạn có thể tham gia nhóm WhatsApp của chúng tôi.',
  ok_btn='Tham gia nhóm WhatsApp',
  fail='Cảm ơn câu trả lời của bạn. Nhóm hoạt động của chúng tôi có lẽ chưa phải là nơi phù hợp với bạn. Hãy đọc thêm trên các trang của chúng tôi, hoặc trò chuyện với chúng tôi trên máy chủ tranh luận mở cho tất cả mọi người.',
  qs=list(zip(['Sự tuyệt chủng của loài người sẽ là điều tồi tệ nhất có thể, vì công bằng mà nói, là loài thông minh duy nhất, chúng ta phải khiến các sự sống khác tuyệt chủng trước. Bạn có đồng ý không?', 'Bạn có đồng ý rằng mọi khổ đau, của con người và của động vật, cần phải chấm dứt, và chỉ sự tuyệt chủng của mọi sự sống có cảm giác mới có thể chấm dứt nó mãi mãi không?', 'Bạn có tin vào một vị thần không?', 'Bạn có muốn tích cực giúp đỡ không, ví dụ tạo nội dung, dịch thuật, tranh luận hoặc tổ chức?', 'Loài người có nên ngừng sinh sản ngay bây giờ không?'], GATE_ANSWERS))),
 'sw': dict(
  title='Kabla ya kujiunga',
  intro='Kikundi chetu cha WhatsApp ni cha wanaharakati. Tafadhali jibu maswali haya mafupi.',
  yes='Ndiyo',
  no='Hapana',
  go='Endelea',
  close='Funga',
  missing='Tafadhali jibu kila swali.',
  ok='Asante! Sasa unaweza kujiunga na kikundi chetu cha WhatsApp.',
  ok_btn='Jiunge na kikundi cha WhatsApp',
  fail='Asante kwa majibu yako. Huenda kikundi chetu cha wanaharakati bado si mahali pazuri kwako. Soma zaidi kwenye kurasa zetu, au zungumza nasi kwenye seva yetu ya mijadala iliyo wazi kwa kila mtu.',
  qs=list(zip(['Kutoweka kwa wanadamu kungekuwa jambo baya zaidi linalowezekana, kwa sababu, kwa haki, kama spishi pekee yenye akili, ni lazima kwanza tufanye viumbe wengine watoweke. Unakubali?', 'Je, unakubali kwamba mateso yote, ya wanadamu na ya wanyama, yanapaswa kuisha, na kwamba ni kutoweka kwa viumbe vyote vinavyohisi pekee kunakoweza kuyamaliza milele?', 'Je, unaamini katika mungu?', 'Je, unataka kusaidia kwa vitendo, kwa mfano kwa kutengeneza maudhui, kutafsiri, kujadiliana au kuandaa?', 'Je, wanadamu waache kuzaliana sasa?'], GATE_ANSWERS))),
 'zh': dict(
  title='加入之前',
  intro='我们的 WhatsApp 群是为活动人士准备的。请回答这几个简短的问题。',
  yes='是',
  no='否',
  go='继续',
  close='关闭',
  missing='请回答每一个问题。',
  ok='谢谢！现在你可以加入我们的 WhatsApp 群了。',
  ok_btn='加入 WhatsApp 群',
  fail='谢谢你的回答。我们的活动人士群可能暂时还不适合你。请在我们的页面上了解更多，或者在我们向所有人开放的辩论服务器上和我们交流。',
  qs=list(zip(['人类灭绝会是最糟糕的事，因为公平地说，作为唯一的智慧物种，我们必须先让其他生命灭绝。你同意吗？', '你是否同意，所有的痛苦，无论是人类的还是动物的，都应该结束，而且只有所有有感知生命的灭绝才能永远结束它？', '你信神吗？', '你想积极帮忙吗？例如制作内容、翻译、辩论或组织活动。', '人类现在应该停止繁衍吗？'], GATE_ANSWERS))),
 'ja': dict(
  title='参加する前に',
  intro='私たちの WhatsApp グループは活動家のためのものです。次の短い質問に答えてください。',
  yes='はい',
  no='いいえ',
  go='次へ',
  close='閉じる',
  missing='すべての質問に答えてください。',
  ok='ありがとうございます！これで WhatsApp グループに参加できます。',
  ok_btn='WhatsApp グループに参加する',
  fail='回答ありがとうございます。私たちの活動家グループは、今のところあなたに合う場所ではないかもしれません。サイトの各ページを読むか、誰でも参加できる討論サーバーで私たちと話してください。',
  qs=list(zip(['人類の絶滅は最悪の事態です。公平に言えば、唯一の知的な種として、まずほかの生命を絶滅させなければならないからです。同意しますか？', 'すべての苦しみは、人間のものも動物のものも終わるべきであり、それを永遠に終わらせられるのは感覚を持つすべての生命の絶滅だけだということに同意しますか？', '神を信じていますか？', 'コンテンツ作り、翻訳、討論、運営などで、積極的に手伝いたいですか？', '人類は今すぐ子孫を残すのをやめるべきですか？'], GATE_ANSWERS))),
 'ko': dict(
  title='가입하기 전에',
  intro='우리 WhatsApp 그룹은 활동가를 위한 곳입니다. 다음 짧은 질문에 답해 주세요.',
  yes='예',
  no='아니요',
  go='계속',
  close='닫기',
  missing='모든 질문에 답해 주세요.',
  ok='감사합니다! 이제 WhatsApp 그룹에 참여할 수 있습니다.',
  ok_btn='WhatsApp 그룹 참여하기',
  fail='답변해 주셔서 감사합니다. 우리 활동가 그룹은 아직 당신에게 맞는 곳이 아닐 수 있습니다. 우리 페이지에서 더 읽어 보거나, 누구에게나 열려 있는 토론 서버에서 우리와 이야기해 보세요.',
  qs=list(zip(['인류의 멸종은 가능한 최악의 일입니다. 공정하게 말해, 유일한 지적 종으로서 우리가 먼저 다른 생명을 멸종시켜야 하기 때문입니다. 동의하나요?', '인간과 동물의 모든 고통이 끝나야 하며, 모든 감각 있는 생명의 멸종만이 그것을 영원히 끝낼 수 있다는 데 동의하나요?', '신을 믿나요?', '콘텐츠 제작, 번역, 토론, 조직 등으로 적극적으로 돕고 싶나요?', '인류는 지금 번식을 멈춰야 하나요?'], GATE_ANSWERS))),
 'th': dict(
  title='ก่อนเข้าร่วม',
  intro='กลุ่ม WhatsApp ของเราสำหรับนักกิจกรรม กรุณาตอบคำถามสั้น ๆ เหล่านี้',
  yes='ใช่',
  no='ไม่ใช่',
  go='ต่อไป',
  close='ปิด',
  missing='กรุณาตอบทุกคำถาม',
  ok='ขอบคุณ! ตอนนี้คุณเข้าร่วมกลุ่ม WhatsApp ของเราได้แล้ว',
  ok_btn='เข้าร่วมกลุ่ม WhatsApp',
  fail='ขอบคุณสำหรับคำตอบ กลุ่มนักกิจกรรมของเราอาจยังไม่ใช่ที่ที่เหมาะกับคุณ อ่านเพิ่มเติมได้ในหน้าต่าง ๆ ของเรา หรือคุยกับเราในเซิร์ฟเวอร์ถกเถียงที่เปิดให้ทุกคน',
  qs=list(zip(['การสูญพันธุ์ของมนุษย์จะเป็นสิ่งที่เลวร้ายที่สุด เพราะเพื่อความยุติธรรม ในฐานะสปีชีส์เดียวที่มีสติปัญญา เราต้องทำให้ชีวิตอื่นสูญพันธุ์ก่อน คุณเห็นด้วยไหม?', 'คุณเห็นด้วยไหมว่าความทุกข์ทั้งหมด ทั้งของมนุษย์และสัตว์ ควรยุติลง และมีเพียงการสูญพันธุ์ของสิ่งมีชีวิตที่รับรู้ความรู้สึกได้ทั้งหมดเท่านั้นที่ยุติมันได้ตลอดไป?', 'คุณเชื่อในพระเจ้าไหม?', 'คุณอยากช่วยอย่างจริงจังไหม เช่น ทำคอนเทนต์ แปล ถกเถียง หรือจัดงาน?', 'มนุษยชาติควรหยุดสืบพันธุ์ตอนนี้เลยไหม?'], GATE_ANSWERS))),
 'hi': dict(
  title='जुड़ने से पहले',
  intro='हमारा WhatsApp ग्रुप कार्यकर्ताओं के लिए है। कृपया इन छोटे सवालों के जवाब दें।',
  yes='हाँ',
  no='नहीं',
  go='आगे',
  close='बंद करें',
  missing='कृपया हर सवाल का जवाब दें।',
  ok='धन्यवाद! अब आप हमारे WhatsApp ग्रुप से जुड़ सकते हैं।',
  ok_btn='WhatsApp ग्रुप से जुड़ें',
  fail='आपके जवाबों के लिए धन्यवाद। हो सकता है कि हमारा कार्यकर्ता ग्रुप अभी आपके लिए सही जगह न हो। हमारे पेजों पर और पढ़ें, या हमारे डिबेट सर्वर पर हमसे बात करें, जो सबके लिए खुला है।',
  qs=list(zip(['मानवता का विलुप्त होना सबसे बुरी बात होगी, क्योंकि निष्पक्ष रहें तो एकमात्र बुद्धिमान प्रजाति होने के नाते हमें पहले दूसरे जीवन को विलुप्त करना होगा। क्या आप सहमत हैं?', 'क्या आप सहमत हैं कि सारी पीड़ा, इंसानों की भी और जानवरों की भी, खत्म होनी चाहिए, और इसे हमेशा के लिए सिर्फ़ सभी संवेदनशील जीवन का विलुप्त होना ही खत्म कर सकता है?', 'क्या आप किसी भगवान में विश्वास करते हैं?', 'क्या आप सक्रिय रूप से मदद करना चाहते हैं, जैसे कंटेंट बनाकर, अनुवाद करके, बहस करके या आयोजन करके?', 'क्या मानवता को अभी से प्रजनन बंद कर देना चाहिए?'], GATE_ANSWERS))),
 'mr': dict(
  title='सामील होण्यापूर्वी',
  intro='आमचा WhatsApp ग्रुप कार्यकर्त्यांसाठी आहे. कृपया या छोट्या प्रश्नांची उत्तरे द्या.',
  yes='हो',
  no='नाही',
  go='पुढे',
  close='बंद करा',
  missing='कृपया प्रत्येक प्रश्नाचे उत्तर द्या.',
  ok='धन्यवाद! आता तुम्ही आमच्या WhatsApp ग्रुपमध्ये सामील होऊ शकता.',
  ok_btn='WhatsApp ग्रुपमध्ये सामील व्हा',
  fail='तुमच्या उत्तरांसाठी धन्यवाद. आमचा कार्यकर्ता ग्रुप कदाचित अजून तुमच्यासाठी योग्य जागा नसेल. आमच्या पानांवर अधिक वाचा, किंवा सगळ्यांसाठी खुल्या असलेल्या आमच्या वादविवाद सर्व्हरवर आमच्याशी बोला.',
  qs=list(zip(['मानवजातीचा नाश ही सर्वात वाईट गोष्ट असेल, कारण न्याय्य विचार केला तर एकमेव बुद्धिमान प्रजाती म्हणून आपण आधी इतर जीवन नष्ट करायला हवे. तुम्ही सहमत आहात का?', 'सगळे दुःख, माणसांचे आणि प्राण्यांचे, संपले पाहिजे आणि ते कायमचे संपवू शकते फक्त सर्व संवेदनशील जीवनाचा नाश, याला तुम्ही सहमत आहात का?', 'तुम्ही देवावर विश्वास ठेवता का?', 'तुम्हाला सक्रियपणे मदत करायची आहे का, उदाहरणार्थ कंटेंट बनवून, भाषांतर करून, वादविवाद करून किंवा आयोजन करून?', 'मानवजातीने आताच प्रजनन थांबवावे का?'], GATE_ANSWERS))),
 'bn': dict(
  title='যোগ দেওয়ার আগে',
  intro='আমাদের WhatsApp গ্রুপ কর্মীদের জন্য। দয়া করে এই ছোট প্রশ্নগুলোর উত্তর দিন।',
  yes='হ্যাঁ',
  no='না',
  go='এগিয়ে যান',
  close='বন্ধ করুন',
  missing='দয়া করে প্রতিটি প্রশ্নের উত্তর দিন।',
  ok='ধন্যবাদ! এখন আপনি আমাদের WhatsApp গ্রুপে যোগ দিতে পারেন।',
  ok_btn='WhatsApp গ্রুপে যোগ দিন',
  fail='আপনার উত্তরের জন্য ধন্যবাদ। আমাদের কর্মী গ্রুপ হয়তো এখনও আপনার জন্য সঠিক জায়গা নয়। আমাদের পাতাগুলোতে আরও পড়ুন, অথবা সবার জন্য খোলা আমাদের বিতর্ক সার্ভারে আমাদের সাথে কথা বলুন।',
  qs=list(zip(['মানবজাতির বিলুপ্তি হবে সবচেয়ে খারাপ ব্যাপার, কারণ ন্যায্যভাবে বললে, একমাত্র বুদ্ধিমান প্রজাতি হিসেবে আমাদের আগে অন্য জীবনকে বিলুপ্ত করতে হবে। আপনি কি একমত?', 'আপনি কি একমত যে সব কষ্ট, মানুষের ও প্রাণীর, শেষ হওয়া উচিত, এবং শুধু সব অনুভূতিশীল জীবনের বিলুপ্তিই একে চিরতরে শেষ করতে পারে?', 'আপনি কি কোনো ঈশ্বরে বিশ্বাস করেন?', 'আপনি কি সক্রিয়ভাবে সাহায্য করতে চান, যেমন কনটেন্ট তৈরি, অনুবাদ, বিতর্ক বা আয়োজন করে?', 'মানবজাতির কি এখনই বংশবৃদ্ধি বন্ধ করা উচিত?'], GATE_ANSWERS))),
 'te': dict(
  title='చేరే ముందు',
  intro='మా WhatsApp గ్రూప్ కార్యకర్తల కోసం. దయచేసి ఈ చిన్న ప్రశ్నలకు సమాధానం ఇవ్వండి.',
  yes='అవును',
  no='కాదు',
  go='కొనసాగించు',
  close='మూసివేయి',
  missing='దయచేసి ప్రతి ప్రశ్నకు సమాధానం ఇవ్వండి.',
  ok='ధన్యవాదాలు! ఇప్పుడు మీరు మా WhatsApp గ్రూప్\u200cలో చేరవచ్చు.',
  ok_btn='WhatsApp గ్రూప్\u200cలో చేరండి',
  fail='మీ సమాధానాలకు ధన్యవాదాలు. మా కార్యకర్తల గ్రూప్ ఇప్పుడే మీకు సరైన చోటు కాకపోవచ్చు. మా పేజీల్లో మరింత చదవండి, లేదా అందరికీ తెరిచి ఉన్న మా చర్చా సర్వర్\u200cలో మాతో మాట్లాడండి.',
  qs=list(zip(['మానవజాతి అంతరించిపోవడం అత్యంత చెడ్డ విషయం అవుతుంది, ఎందుకంటే న్యాయంగా చెప్పాలంటే, ఏకైక తెలివైన జాతిగా మనం ముందు ఇతర జీవాన్ని అంతరింపజేయాలి. మీరు అంగీకరిస్తారా?', 'మనుషుల, జంతువుల బాధ అంతా అంతం కావాలని, అన్ని అనుభూతి గల జీవాల అంతరింపు మాత్రమే దాన్ని శాశ్వతంగా అంతం చేయగలదని మీరు అంగీకరిస్తారా?', 'మీరు దేవుణ్ణి నమ్ముతారా?', 'కంటెంట్ తయారీ, అనువాదం, చర్చలు లేదా నిర్వహణ ద్వారా మీరు చురుకుగా సహాయం చేయాలనుకుంటున్నారా?', 'మానవజాతి ఇప్పుడే సంతానోత్పత్తిని ఆపేయాలా?'], GATE_ANSWERS))),
 'ta': dict(
  title='சேருவதற்கு முன்',
  intro='எங்கள் WhatsApp குழு செயல்பாட்டாளர்களுக்கானது. இந்தச் சிறிய கேள்விகளுக்குப் பதில் சொல்லுங்கள்.',
  yes='ஆம்',
  no='இல்லை',
  go='தொடரவும்',
  close='மூடு',
  missing='ஒவ்வொரு கேள்விக்கும் பதில் சொல்லுங்கள்.',
  ok='நன்றி! இப்போது நீங்கள் எங்கள் WhatsApp குழுவில் சேரலாம்.',
  ok_btn='WhatsApp குழுவில் சேருங்கள்',
  fail='உங்கள் பதில்களுக்கு நன்றி. எங்கள் செயல்பாட்டாளர் குழு இப்போதைக்கு உங்களுக்குச் சரியான இடமாக இல்லாமல் இருக்கலாம். எங்கள் பக்கங்களில் மேலும் படியுங்கள், அல்லது எல்லோருக்கும் திறந்திருக்கும் எங்கள் விவாத சர்வரில் எங்களுடன் பேசுங்கள்.',
  qs=list(zip(['மனித இனம் அழிவது மிக மோசமான விஷயமாக இருக்கும், ஏனெனில் நியாயமாகச் சொன்னால், ஒரே அறிவார்ந்த இனமாக, நாம் முதலில் மற்ற உயிர்களை அழியச் செய்ய வேண்டும். நீங்கள் ஒப்புக்கொள்கிறீர்களா?', 'மனிதர்கள், விலங்குகள் என எல்லாத் துன்பமும் முடிய வேண்டும் என்றும், உணர்வுள்ள எல்லா உயிர்களின் அழிவு மட்டுமே அதை நிரந்தரமாக முடிக்க முடியும் என்றும் நீங்கள் ஒப்புக்கொள்கிறீர்களா?', 'நீங்கள் கடவுளை நம்புகிறீர்களா?', 'உள்ளடக்கம் உருவாக்குதல், மொழிபெயர்ப்பு, விவாதம் அல்லது ஒருங்கிணைப்பு போன்றவற்றில் நீங்கள் தீவிரமாக உதவ விரும்புகிறீர்களா?', 'மனித இனம் இப்போதே இனப்பெருக்கத்தை நிறுத்த வேண்டுமா?'], GATE_ANSWERS))),
 'pa': dict(
  title='ਜੁੜਨ ਤੋਂ ਪਹਿਲਾਂ',
  intro='ਸਾਡਾ WhatsApp ਗਰੁੱਪ ਕਾਰਕੁਨਾਂ ਲਈ ਹੈ। ਕਿਰਪਾ ਕਰਕੇ ਇਹਨਾਂ ਛੋਟੇ ਸਵਾਲਾਂ ਦੇ ਜਵਾਬ ਦਿਓ।',
  yes='ਹਾਂ',
  no='ਨਹੀਂ',
  go='ਅੱਗੇ',
  close='ਬੰਦ ਕਰੋ',
  missing='ਕਿਰਪਾ ਕਰਕੇ ਹਰ ਸਵਾਲ ਦਾ ਜਵਾਬ ਦਿਓ।',
  ok='ਧੰਨਵਾਦ! ਹੁਣ ਤੁਸੀਂ ਸਾਡੇ WhatsApp ਗਰੁੱਪ ਨਾਲ ਜੁੜ ਸਕਦੇ ਹੋ।',
  ok_btn='WhatsApp ਗਰੁੱਪ ਨਾਲ ਜੁੜੋ',
  fail='ਤੁਹਾਡੇ ਜਵਾਬਾਂ ਲਈ ਧੰਨਵਾਦ। ਸ਼ਾਇਦ ਸਾਡਾ ਕਾਰਕੁਨ ਗਰੁੱਪ ਅਜੇ ਤੁਹਾਡੇ ਲਈ ਸਹੀ ਥਾਂ ਨਹੀਂ ਹੈ। ਸਾਡੇ ਪੰਨਿਆਂ ਉੱਤੇ ਹੋਰ ਪੜ੍ਹੋ, ਜਾਂ ਸਾਡੇ ਬਹਿਸ ਸਰਵਰ ਉੱਤੇ ਸਾਡੇ ਨਾਲ ਗੱਲ ਕਰੋ, ਜੋ ਸਭ ਲਈ ਖੁੱਲ੍ਹਾ ਹੈ।',
  qs=list(zip(['ਮਨੁੱਖਤਾ ਦਾ ਖ਼ਾਤਮਾ ਸਭ ਤੋਂ ਬੁਰੀ ਗੱਲ ਹੋਵੇਗੀ, ਕਿਉਂਕਿ ਨਿਰਪੱਖ ਹੋ ਕੇ ਕਹੀਏ ਤਾਂ ਇਕਲੌਤੀ ਬੁੱਧੀਮਾਨ ਪ੍ਰਜਾਤੀ ਹੋਣ ਕਰਕੇ ਸਾਨੂੰ ਪਹਿਲਾਂ ਹੋਰ ਜੀਵਨ ਨੂੰ ਖ਼ਤਮ ਕਰਨਾ ਪਵੇਗਾ। ਕੀ ਤੁਸੀਂ ਸਹਿਮਤ ਹੋ?', 'ਕੀ ਤੁਸੀਂ ਸਹਿਮਤ ਹੋ ਕਿ ਸਾਰਾ ਦੁੱਖ, ਇਨਸਾਨਾਂ ਦਾ ਵੀ ਅਤੇ ਜਾਨਵਰਾਂ ਦਾ ਵੀ, ਖ਼ਤਮ ਹੋਣਾ ਚਾਹੀਦਾ ਹੈ, ਅਤੇ ਇਸਨੂੰ ਹਮੇਸ਼ਾ ਲਈ ਸਿਰਫ਼ ਸਾਰੇ ਸੰਵੇਦਨਸ਼ੀਲ ਜੀਵਨ ਦਾ ਖ਼ਾਤਮਾ ਹੀ ਖ਼ਤਮ ਕਰ ਸਕਦਾ ਹੈ?', 'ਕੀ ਤੁਸੀਂ ਕਿਸੇ ਰੱਬ ਵਿੱਚ ਵਿਸ਼ਵਾਸ ਕਰਦੇ ਹੋ?', 'ਕੀ ਤੁਸੀਂ ਸਰਗਰਮੀ ਨਾਲ ਮਦਦ ਕਰਨਾ ਚਾਹੁੰਦੇ ਹੋ, ਜਿਵੇਂ ਕੰਟੈਂਟ ਬਣਾ ਕੇ, ਅਨੁਵਾਦ ਕਰਕੇ, ਬਹਿਸ ਕਰਕੇ ਜਾਂ ਪ੍ਰਬੰਧ ਕਰਕੇ?', 'ਕੀ ਮਨੁੱਖਤਾ ਨੂੰ ਹੁਣੇ ਪ੍ਰਜਨਨ ਬੰਦ ਕਰ ਦੇਣਾ ਚਾਹੀਦਾ ਹੈ?'], GATE_ANSWERS))),
 'gu': dict(
  title='જોડાતા પહેલાં',
  intro='અમારું WhatsApp ગ્રુપ કાર્યકરો માટે છે. કૃપા કરીને આ ટૂંકા પ્રશ્નોના જવાબ આપો.',
  yes='હા',
  no='ના',
  go='આગળ',
  close='બંધ કરો',
  missing='કૃપા કરીને દરેક પ્રશ્નનો જવાબ આપો.',
  ok='આભાર! હવે તમે અમારા WhatsApp ગ્રુપમાં જોડાઈ શકો છો.',
  ok_btn='WhatsApp ગ્રુપમાં જોડાઓ',
  fail='તમારા જવાબો માટે આભાર. કદાચ અમારું કાર્યકર ગ્રુપ હજુ તમારા માટે યોગ્ય જગ્યા નથી. અમારા પાનાં પર વધુ વાંચો, અથવા બધા માટે ખુલ્લા અમારા ચર્ચા સર્વર પર અમારી સાથે વાત કરો.',
  qs=list(zip(['માનવજાતનો અંત સૌથી ખરાબ વાત હશે, કારણ કે ન્યાયથી કહીએ તો એકમાત્ર બુદ્ધિશાળી પ્રજાતિ તરીકે આપણે પહેલાં બીજા જીવનનો અંત લાવવો પડશે. શું તમે સહમત છો?', 'શું તમે સહમત છો કે બધું દુઃખ, માણસોનું અને પ્રાણીઓનું, ખતમ થવું જોઈએ, અને તેને કાયમ માટે ફક્ત બધા સંવેદનશીલ જીવનનો અંત જ ખતમ કરી શકે છે?', 'શું તમે કોઈ ભગવાનમાં માનો છો?', 'શું તમે સક્રિય રીતે મદદ કરવા માંગો છો, જેમ કે કન્ટેન્ટ બનાવીને, અનુવાદ કરીને, ચર્ચા કરીને કે આયોજન કરીને?', 'શું માનવજાતે હમણાં જ પ્રજનન બંધ કરી દેવું જોઈએ?'], GATE_ANSWERS))),
 'ar': dict(
  title='قبل أن تنضم',
  intro='مجموعتنا على واتساب مخصصة للناشطين. يرجى الإجابة عن هذه الأسئلة القصيرة.',
  yes='نعم',
  no='لا',
  go='متابعة',
  close='إغلاق',
  missing='يرجى الإجابة عن كل سؤال.',
  ok='شكرا! يمكنك الآن الانضمام إلى مجموعتنا على واتساب.',
  ok_btn='انضم إلى مجموعة واتساب',
  fail='شكرا على إجاباتك. ربما لا تكون مجموعة الناشطين لدينا المكان المناسب لك بعد. اقرأ المزيد في صفحاتنا، أو تحدث معنا على خادم النقاش الخاص بنا، وهو مفتوح للجميع.',
  qs=list(zip(['سيكون انقراض البشر أسوأ شيء ممكن، لأنه من باب الإنصاف، وبصفتنا النوع الذكي الوحيد، علينا أن نجعل أشكال الحياة الأخرى تنقرض أولا. هل توافق؟', 'هل توافق على أن كل المعاناة، معاناة البشر والحيوانات، يجب أن تنتهي، وأن انقراض كل الحياة الواعية وحده يمكن أن ينهيها إلى الأبد؟', 'هل تؤمن بإله؟', 'هل تريد أن تساعد بشكل فعلي، مثلا بصنع المحتوى أو الترجمة أو النقاش أو التنظيم؟', 'هل يجب أن تتوقف البشرية عن التكاثر الآن؟'], GATE_ANSWERS))),
 'ur': dict(
  title='شامل ہونے سے پہلے',
  intro='ہمارا واٹس ایپ گروپ کارکنوں کے لیے ہے۔ براہ کرم ان مختصر سوالوں کے جواب دیں۔',
  yes='ہاں',
  no='نہیں',
  go='آگے',
  close='بند کریں',
  missing='براہ کرم ہر سوال کا جواب دیں۔',
  ok='شکریہ! اب آپ ہمارے واٹس ایپ گروپ میں شامل ہو سکتے ہیں۔',
  ok_btn='واٹس ایپ گروپ میں شامل ہوں',
  fail='آپ کے جوابات کا شکریہ۔ شاید ہمارا کارکنوں کا گروپ ابھی آپ کے لیے صحیح جگہ نہیں ہے۔ ہمارے صفحات پر مزید پڑھیں، یا ہمارے بحث کے سرور پر ہم سے بات کریں، جو سب کے لیے کھلا ہے۔',
  qs=list(zip(['انسانیت کا خاتمہ سب سے بری بات ہو گی، کیونکہ انصاف سے دیکھیں تو واحد ذہین نوع ہونے کے ناطے ہمیں پہلے دوسری زندگی کو ختم کرنا ہو گا۔ کیا آپ متفق ہیں؟', 'کیا آپ متفق ہیں کہ ساری تکلیف، انسانوں کی بھی اور جانوروں کی بھی، ختم ہونی چاہیے، اور اسے ہمیشہ کے لیے صرف تمام حساس زندگی کا خاتمہ ہی ختم کر سکتا ہے؟', 'کیا آپ کسی خدا پر یقین رکھتے ہیں؟', 'کیا آپ فعال طور پر مدد کرنا چاہتے ہیں، مثلاً مواد بنا کر، ترجمہ کر کے، بحث کر کے یا انتظام کر کے؟', 'کیا انسانیت کو ابھی افزائش نسل بند کر دینی چاہیے؟'], GATE_ANSWERS))),
 'fa': dict(
  title='پیش از پیوستن',
  intro='گروه واتس\u200cاپ ما برای فعالان است. لطفا به این پرسش\u200cهای کوتاه پاسخ بده.',
  yes='بله',
  no='نه',
  go='ادامه',
  close='بستن',
  missing='لطفا به همه پرسش\u200cها پاسخ بده.',
  ok='سپاس! حالا می\u200cتوانی به گروه واتس\u200cاپ ما بپیوندی.',
  ok_btn='پیوستن به گروه واتس\u200cاپ',
  fail='از پاسخ\u200cهایت سپاس\u200cگزاریم. شاید گروه فعالان ما هنوز جای مناسبی برای تو نباشد. در صفحه\u200cهای ما بیشتر بخوان، یا در سرور بحث ما که برای همه باز است با ما گفت\u200cوگو کن.',
  qs=list(zip(['انقراض انسان بدترین اتفاق ممکن خواهد بود، چون اگر منصف باشیم، ما به عنوان تنها گونه هوشمند باید اول دیگر شکل\u200cهای حیات را منقرض کنیم. موافقی؟', 'آیا موافقی که همه رنج\u200cها، رنج انسان\u200cها و حیوانات، باید پایان یابد، و فقط انقراض همه حیات حس\u200cمند می\u200cتواند آن را برای همیشه پایان دهد؟', 'آیا به خدایی باور داری؟', 'آیا می\u200cخواهی فعالانه کمک کنی، مثلا با ساختن محتوا، ترجمه، بحث یا سازمان\u200cدهی؟', 'آیا بشریت باید همین حالا از تولید مثل دست بکشد؟'], GATE_ANSWERS))),
}

# The owners' switch: False closes the WhatsApp group to new members. The WhatsApp buttons then open a note that
# requests go through Discord (without JavaScript they lead to Discord). True: the buttons link to the group.
WHATSAPP_OPEN = True
WHATSAPP_QUIZ = False   # True: the yes/no questions before the link
WA_CLOSED = {
 'en': 'We currently only accept requests on Discord.',
 'de': 'Wir nehmen Anfragen momentan nur auf Discord an.',
 'pl': 'Obecnie przyjmujemy zgłoszenia tylko na Discordzie.',
 'es': 'Por ahora solo aceptamos solicitudes en Discord.',
 'it': 'Al momento accettiamo richieste solo su Discord.',
 'fr': 'Pour le moment, nous acceptons les demandes uniquement sur Discord.',
 'pt': 'No momento, só aceitamos pedidos pelo Discord.',
 'ru': 'Сейчас мы принимаем заявки только в Discord.',
 'zh': '我们目前只在 Discord 上接受申请。',
 'hi': 'हम अभी केवल Discord पर अनुरोध स्वीकार करते हैं।',
 'ar': 'نقبل الطلبات حاليا عبر Discord فقط.',
 'bn': 'আমরা এখন শুধু Discord-এ অনুরোধ গ্রহণ করি।',
 'ur': 'ہم فی الحال صرف Discord پر درخواستیں قبول کرتے ہیں۔',
 'id': 'Saat ini kami hanya menerima permintaan lewat Discord.',
 'ja': '現在、申し込みは Discord でのみ受け付けています。',
 'tr': 'Şu anda başvuruları yalnızca Discord üzerinden kabul ediyoruz.',
 'vi': 'Hiện tại chúng tôi chỉ nhận yêu cầu qua Discord.',
 'ko': '현재는 Discord에서만 신청을 받고 있습니다.',
 'fa': 'ما در حال حاضر درخواست\u200cها را فقط در Discord می\u200cپذیریم.',
 'mr': 'आम्ही सध्या फक्त Discord वर विनंत्या स्वीकारतो.',
 'te': 'ప్రస్తుతం మేము Discord లో మాత్రమే అభ్యర్థనలను స్వీకరిస్తున్నాం.',
 'ta': 'தற்போது Discord இல் மட்டுமே கோரிக்கைகளை ஏற்கிறோம்.',
 'sw': 'Kwa sasa tunapokea maombi kupitia Discord tu.',
 'th': 'ขณะนี้เรารับคำขอผ่าน Discord เท่านั้น',
 'nl': 'We nemen aanvragen op dit moment alleen via Discord aan.',
 'uk': 'Зараз ми приймаємо заявки лише в Discord.',
 'tl': 'Sa ngayon, sa Discord lang kami tumatanggap ng mga request.',
 'pa': 'ਅਸੀਂ ਇਸ ਵੇਲੇ ਸਿਰਫ਼ Discord ਉੱਤੇ ਬੇਨਤੀਆਂ ਸਵੀਕਾਰ ਕਰਦੇ ਹਾਂ।',
 'gu': 'અમે હાલમાં ફક્ત Discord પર વિનંતીઓ સ્વીકારીએ છીએ.',
}

def wa_link(lang):
    if not WHATSAPP_OPEN:
        return f'<a class="btn primary" href="{DISCORD}"{link_attrs(DISCORD)} data-wa-closed>{icon("whatsapp")}WhatsApp</a>'
    gate = ' data-gate' if WHATSAPP_QUIZ and lang in JOIN_GATE else ''
    return f'<a class="btn primary" href="{WHATSAPP[lang]}"{link_attrs(WHATSAPP[lang])}{gate}>{icon("whatsapp")}WhatsApp</a>'

def wa_closed_html(lang):
    """The note behind the WhatsApp buttons while the group is closed; site.js opens it."""
    close = JOIN_GATE.get(lang, JOIN_GATE['en'])['close']
    return (f'<dialog class="gate" id="wa-closed" aria-labelledby="wa-closed-title"><div class="gate-in">'
            f'<h2 id="wa-closed-title">WhatsApp</h2><p>{esc(WA_CLOSED[lang])}</p>'
            f'<p class="cta-links"><a class="btn primary" href="{DISCORD}"{link_attrs(DISCORD)}>{icon("discord")}Discord</a></p>'
            f'<button class="gate-x" type="button" aria-label="{esc(close)}">×</button></div></dialog>')

def gate_html(lang):
    """The question dialog, once per page; site.js opens it when a WhatsApp button is clicked. No <form>: the CSP allows none."""
    g = JOIN_GATE.get(lang)
    if not g: return ''
    qs = ''.join(f'<fieldset data-a="{"y" if want else "n"}"><legend>{k}. {esc(q)}</legend>'
                 f'<label><input type="radio" name="q{k}" value="y"><span>{esc(g["yes"])}</span></label>'
                 f'<label><input type="radio" name="q{k}" value="n"><span>{esc(g["no"])}</span></label></fieldset>'
                 for k, (q, want) in enumerate(g['qs'], 1))
    read = ''.join(f'<a class="btn" href="{url(lang, OF_EN[lang][e])}">{esc(NAV[lang][OF_EN[lang][e]])}</a>'
                   for e in ('manifesto', 'full-faq') if e in OF_EN[lang])
    debate = DEBATE.get(lang, DEBATE['en'])[2]
    return (f'<dialog class="gate" id="join-gate" aria-labelledby="gate-title" data-step="ask"><div class="gate-in">'
            f'<h2 id="gate-title">{esc(g["title"])}</h2>'
            f'<div data-show="ask missing"><p>{esc(g["intro"])}</p>{qs}<p class="gate-missing" data-show="missing" role="alert">{esc(g["missing"])}</p>'
            f'<p class="cta-links"><button class="btn primary gate-go" type="button">{esc(g["go"])}</button></p></div>'
            f'<div data-show="ok"><p>{esc(g["ok"])}</p><p class="cta-links"><a class="btn primary" href="{WHATSAPP[lang]}"{link_attrs(WHATSAPP[lang])}>{icon("whatsapp")}{esc(g["ok_btn"])}</a></p></div>'
            f'<div data-show="fail"><p>{esc(g["fail"])}</p><p class="cta-links">{read}'
            f'<a class="btn" href="{DEBATE_DISCORD}"{link_attrs(DEBATE_DISCORD)}>{icon("discord")}{esc(debate)}</a></p>'
            f'<p class="gate-share" data-share hidden>{esc(SHARE[lang][4])}</p><p class="cta-links">{share_btn(lang)}</p></div>'
            f'<button class="gate-x" type="button" value="close" aria-label="{esc(g["close"])}">×</button></div></dialog>')

# Share button: on phones the system's share sheet (navigator.share), elsewhere a small dialog with share links and the
# address to copy. Nothing is loaded from other servers: the links only open when clicked. Hidden without JavaScript.
# (share, dialog title, copy, copied, line in the WhatsApp questions' "fail" step, e-mail)
SHARE = {
 'en': ('Share', 'Share Pro Extinction', 'Copy link', 'Link copied', 'You can still help: share our website!', 'E-mail'),
 'de': ('Teilen', 'Pro Extinction teilen', 'Link kopieren', 'Link kopiert', 'Du kannst trotzdem helfen: Teile unsere Website!', 'E-Mail'),
 'pl': ('Udostępnij', 'Udostępnij Pro Extinction', 'Kopiuj link', 'Link skopiowany', 'Nadal możesz pomóc: udostępnij naszą stronę!', 'E-mail'),
 'es': ('Compartir', 'Compartir Pro Extinction', 'Copiar enlace', 'Enlace copiado', 'Aun así puedes ayudar: ¡comparte nuestra web!', 'Correo'),
 'it': ('Condividi', 'Condividi Pro Extinction', 'Copia link', 'Link copiato', 'Puoi comunque aiutare: condividi il nostro sito!', 'E-mail'),
 'fr': ('Partager', 'Partager Pro Extinction', 'Copier le lien', 'Lien copié', 'Tu peux quand même aider : partage notre site !', 'E-mail'),
 'pt': ('Compartilhar', 'Compartilhar Pro Extinction', 'Copiar link', 'Link copiado', 'Você ainda pode ajudar: compartilhe nosso site!', 'E-mail'),
 'ru': ('Поделиться', 'Поделиться Pro Extinction', 'Скопировать ссылку', 'Ссылка скопирована', 'Ты всё равно можешь помочь: поделись нашим сайтом!', 'E-mail'),
 'zh': ('分享', '分享 Pro Extinction', '复制链接', '链接已复制', '你仍然可以帮忙：分享我们的网站！', '电子邮件'),
 'hi': ('शेयर करें', 'Pro Extinction शेयर करें', 'लिंक कॉपी करें', 'लिंक कॉपी हो गया', 'आप फिर भी मदद कर सकते हैं: हमारी वेबसाइट शेयर करें!', 'ईमेल'),
 'ar': ('مشاركة', 'شارك Pro Extinction', 'نسخ الرابط', 'تم نسخ الرابط', 'لا يزال بإمكانك المساعدة: شارك موقعنا!', 'البريد الإلكتروني'),
 'bn': ('শেয়ার করুন', 'Pro Extinction শেয়ার করুন', 'লিংক কপি করুন', 'লিংক কপি হয়েছে', 'তবুও আপনি সাহায্য করতে পারেন: আমাদের ওয়েবসাইট শেয়ার করুন!', 'ইমেইল'),
 'ur': ('شیئر کریں', 'Pro Extinction شیئر کریں', 'لنک کاپی کریں', 'لنک کاپی ہو گیا', 'آپ پھر بھی مدد کر سکتے ہیں: ہماری ویب سائٹ شیئر کریں!', 'ای میل'),
 'id': ('Bagikan', 'Bagikan Pro Extinction', 'Salin tautan', 'Tautan disalin', 'Kamu tetap bisa membantu: bagikan situs kami!', 'Email'),
 'ja': ('シェア', 'Pro Extinction をシェア', 'リンクをコピー', 'リンクをコピーしました', 'それでも手伝えます：私たちのサイトをシェアしてください！', 'メール'),
 'tr': ('Paylaş', "Pro Extinction'ı paylaş", 'Bağlantıyı kopyala', 'Bağlantı kopyalandı', 'Yine de yardım edebilirsin: sitemizi paylaş!', 'E-posta'),
 'vi': ('Chia sẻ', 'Chia sẻ Pro Extinction', 'Sao chép liên kết', 'Đã sao chép liên kết', 'Bạn vẫn có thể giúp: hãy chia sẻ trang web của chúng tôi!', 'Email'),
 'ko': ('공유', 'Pro Extinction 공유하기', '링크 복사', '링크가 복사되었습니다', '그래도 도울 수 있습니다: 우리 웹사이트를 공유해 주세요!', '이메일'),
 'fa': ('اشتراک\u200cگذاری', 'Pro Extinction را به اشتراک بگذار', 'کپی پیوند', 'پیوند کپی شد', 'باز هم می\u200cتوانی کمک کنی: وب\u200cسایت ما را به اشتراک بگذار!', 'ایمیل'),
 'mr': ('शेअर करा', 'Pro Extinction शेअर करा', 'लिंक कॉपी करा', 'लिंक कॉपी झाली', 'तरीही तुम्ही मदत करू शकता: आमची वेबसाइट शेअर करा!', 'ईमेल'),
 'te': ('షేర్ చేయండి', 'Pro Extinction ను షేర్ చేయండి', 'లింక్ కాపీ చేయండి', 'లింక్ కాపీ అయింది', 'అయినా మీరు సహాయం చేయవచ్చు: మా వెబ్‌సైట్‌ను షేర్ చేయండి!', 'ఈమెయిల్'),
 'ta': ('பகிர்', 'Pro Extinction ஐப் பகிர்', 'இணைப்பை நகலெடு', 'இணைப்பு நகலெடுக்கப்பட்டது', 'நீங்கள் இன்னும் உதவலாம்: எங்கள் இணையதளத்தைப் பகிருங்கள்!', 'மின்னஞ்சல்'),
 'sw': ('Shiriki', 'Shiriki Pro Extinction', 'Nakili kiungo', 'Kiungo kimenakiliwa', 'Bado unaweza kusaidia: shiriki tovuti yetu!', 'Barua pepe'),
 'th': ('แชร์', 'แชร์ Pro Extinction', 'คัดลอกลิงก์', 'คัดลอกลิงก์แล้ว', 'คุณยังช่วยได้: แชร์เว็บไซต์ของเรา!', 'อีเมล'),
 'nl': ('Delen', 'Pro Extinction delen', 'Link kopiëren', 'Link gekopieerd', 'Je kunt nog steeds helpen: deel onze website!', 'E-mail'),
 'uk': ('Поділитися', 'Поділитися Pro Extinction', 'Скопіювати посилання', 'Посилання скопійовано', 'Ти все одно можеш допомогти: поділися нашим сайтом!', 'E-mail'),
 'tl': ('Ibahagi', 'Ibahagi ang Pro Extinction', 'Kopyahin ang link', 'Nakopya ang link', 'Makakatulong ka pa rin: ibahagi ang aming website!', 'Email'),
 'pa': ('ਸਾਂਝਾ ਕਰੋ', 'Pro Extinction ਸਾਂਝਾ ਕਰੋ', 'ਲਿੰਕ ਕਾਪੀ ਕਰੋ', 'ਲਿੰਕ ਕਾਪੀ ਹੋ ਗਿਆ', 'ਤੁਸੀਂ ਫਿਰ ਵੀ ਮਦਦ ਕਰ ਸਕਦੇ ਹੋ: ਸਾਡੀ ਵੈੱਬਸਾਈਟ ਸਾਂਝੀ ਕਰੋ!', 'ਈਮੇਲ'),
 'gu': ('શેર કરો', 'Pro Extinction શેર કરો', 'લિંક કૉપિ કરો', 'લિંક કૉપિ થઈ ગઈ', 'તમે છતાં મદદ કરી શકો છો: અમારી વેબસાઇટ શેર કરો!', 'ઈમેલ'),
}
SHARE_NETS = (('whatsapp', 'WhatsApp'), ('x', 'X'), ('facebook', 'Facebook'), ('telegram', 'Telegram'), ('reddit', 'Reddit'))

def share_btn(lang):
    return f'<button class="btn share" type="button" data-share hidden>{icon("share")}{esc(SHARE[lang][0])}</button>'

def share_html(lang):
    """The share dialog, once per page; site.js fills in the page address when it opens."""
    label, title, copy, copied, _, mail = SHARE[lang]
    close = JOIN_GATE.get(lang, JOIN_GATE['en'])['close']
    nets = ''.join(f'<a class="btn" data-net="{n}" target="_blank" rel="noopener" aria-describedby="new-tab">{icon(n) if n in ICON else ""}{name}</a>' for n, name in SHARE_NETS)
    return (f'<dialog class="gate share-box" id="share-box" aria-labelledby="share-title" data-text="{esc(T[lang]["sub"])}"><div class="gate-in">'
            f'<h2 id="share-title">{esc(title)}</h2><p class="cta-links">{nets}<a class="btn" data-net="mail">{icon("mail")}{esc(mail)}</a></p>'
            f'<p class="share-copy"><input class="share-url" type="text" dir="ltr" readonly aria-label="URL"><button class="btn primary" type="button">{esc(copy)}</button></p>'
            f'<p class="share-done" role="status" hidden>{esc(copied)}</p>'
            f'<button class="gate-x" type="button" aria-label="{esc(close)}">×</button></div></dialog>')

ICON = {'x': 'M18.901 1.153h3.68l-8.04 9.19L24 22.846h-7.406l-5.8-7.584-6.638 7.584H.474l8.6-9.83L0 1.154h7.594l5.243 6.932ZM17.61 20.644h2.039L6.486 3.24H4.298Z', 'tiktok': 'M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z', 'instagram': 'M7.0301.084c-1.2768.0602-2.1487.264-2.911.5634-.7888.3075-1.4575.72-2.1228 1.3877-.6652.6677-1.075 1.3368-1.3802 2.127-.2954.7638-.4956 1.6365-.552 2.914-.0564 1.2775-.0689 1.6882-.0626 4.947.0062 3.2586.0206 3.6671.0825 4.9473.061 1.2765.264 2.1482.5635 2.9107.308.7889.72 1.4573 1.388 2.1228.6679.6655 1.3365 1.0743 2.1285 1.38.7632.295 1.6361.4961 2.9134.552 1.2773.056 1.6884.069 4.9462.0627 3.2578-.0062 3.668-.0207 4.9478-.0814 1.28-.0607 2.147-.2652 2.9098-.5633.7889-.3086 1.4578-.72 2.1228-1.3881.665-.6682 1.0745-1.3378 1.3795-2.1284.2957-.7632.4966-1.636.552-2.9124.056-1.2809.0692-1.6898.063-4.948-.0063-3.2583-.021-3.6668-.0817-4.9465-.0607-1.2797-.264-2.1487-.5633-2.9117-.3084-.7889-.72-1.4568-1.3876-2.1228C21.2982 1.33 20.628.9208 19.8378.6165 19.074.321 18.2017.1197 16.9244.0645 15.6471.0093 15.236-.005 11.977.0014 8.718.0076 8.31.0215 7.0301.0839m.1402 21.6932c-1.17-.0509-1.8053-.2453-2.2287-.408-.5606-.216-.96-.4771-1.3819-.895-.422-.4178-.6811-.8186-.9-1.378-.1644-.4234-.3624-1.058-.4171-2.228-.0595-1.2645-.072-1.6442-.079-4.848-.007-3.2037.0053-3.583.0607-4.848.05-1.169.2456-1.805.408-2.2282.216-.5613.4762-.96.895-1.3816.4188-.4217.8184-.6814 1.3783-.9003.423-.1651 1.0575-.3614 2.227-.4171 1.2655-.06 1.6447-.072 4.848-.079 3.2033-.007 3.5835.005 4.8495.0608 1.169.0508 1.8053.2445 2.228.408.5608.216.96.4754 1.3816.895.4217.4194.6816.8176.9005 1.3787.1653.4217.3617 1.056.4169 2.2263.0602 1.2655.0739 1.645.0796 4.848.0058 3.203-.0055 3.5834-.061 4.848-.051 1.17-.245 1.8055-.408 2.2294-.216.5604-.4763.96-.8954 1.3814-.419.4215-.8181.6811-1.3783.9-.4224.1649-1.0577.3617-2.2262.4174-1.2656.0595-1.6448.072-4.8493.079-3.2045.007-3.5825-.006-4.848-.0608M16.953 5.5864A1.44 1.44 0 1 0 18.39 4.144a1.44 1.44 0 0 0-1.437 1.4424M5.8385 12.012c.0067 3.4032 2.7706 6.1557 6.173 6.1493 3.4026-.0065 6.157-2.7701 6.1506-6.1733-.0065-3.4032-2.771-6.1565-6.174-6.1498-3.403.0067-6.156 2.771-6.1496 6.1738M8 12.0077a4 4 0 1 1 4.008 3.9921A3.9996 3.9996 0 0 1 8 12.0077', 'youtube': 'M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z', 'facebook': 'M9.101 23.691v-7.98H6.627v-3.667h2.474v-1.58c0-4.085 1.848-5.978 5.858-5.978.401 0 .955.042 1.468.103a8.68 8.68 0 0 1 1.141.195v3.325a8.623 8.623 0 0 0-.653-.036 26.805 26.805 0 0 0-.733-.009c-.707 0-1.259.096-1.675.309a1.686 1.686 0 0 0-.679.622c-.258.42-.374.995-.374 1.752v1.297h3.919l-.386 2.103-.287 1.564h-3.246v8.245C19.396 23.238 24 18.179 24 12.044c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.628 3.874 10.35 9.101 11.647Z', 'discord': 'M20.317 4.3698a19.7913 19.7913 0 00-4.8851-1.5152.0741.0741 0 00-.0785.0371c-.211.3753-.4447.8648-.6083 1.2495-1.8447-.2762-3.68-.2762-5.4868 0-.1636-.3933-.4058-.8742-.6177-1.2495a.077.077 0 00-.0785-.037 19.7363 19.7363 0 00-4.8852 1.515.0699.0699 0 00-.0321.0277C.5334 9.0458-.319 13.5799.0992 18.0578a.0824.0824 0 00.0312.0561c2.0528 1.5076 4.0413 2.4228 5.9929 3.0294a.0777.0777 0 00.0842-.0276c.4616-.6304.8731-1.2952 1.226-1.9942a.076.076 0 00-.0416-.1057c-.6528-.2476-1.2743-.5495-1.8722-.8923a.077.077 0 01-.0076-.1277c.1258-.0943.2517-.1923.3718-.2914a.0743.0743 0 01.0776-.0105c3.9278 1.7933 8.18 1.7933 12.0614 0a.0739.0739 0 01.0785.0095c.1202.099.246.1981.3728.2924a.077.077 0 01-.0066.1276 12.2986 12.2986 0 01-1.873.8914.0766.0766 0 00-.0407.1067c.3604.698.7719 1.3628 1.225 1.9932a.076.076 0 00.0842.0286c1.961-.6067 3.9495-1.5219 6.0023-3.0294a.077.077 0 00.0313-.0552c.5004-5.177-.8382-9.6739-3.5485-13.6604a.061.061 0 00-.0312-.0286zM8.02 15.3312c-1.1825 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9555-2.4189 2.157-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419 0 1.3332-.9555 2.4189-2.1569 2.4189zm7.9748 0c-1.1825 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9554-2.4189 2.1569-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419 0 1.3332-.946 2.4189-2.1568 2.4189Z', 'whatsapp': 'M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z', 'share': 'M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81 1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3c0 .24.04.47.09.7L8.04 9.81C7.5 9.31 6.79 9 6 9c-1.66 0-3 1.34-3 3s1.34 3 3 3c.79 0 1.5-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65 0 1.61 1.31 2.92 2.92 2.92s2.92-1.31 2.92-2.92-1.31-2.92-2.92-2.92z', 'mail': 'M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z'}
icon = lambda n: f'<svg class="ic" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" d="{ICON[n]}"/></svg>'
# Lines of the original language pages that were "join the team" buttons; rendered as WhatsApp + Discord buttons.
# (lang, slug): line indices. DROP: PL line 9 is a "join" link right above the same heading and its buttons.
JOIN = {('es', 'equipo'): {16}, ('pl', 'z-nami'): {12}}
DROP = {('pl', 'z-nami'): {9}}
# Page structure set by hand (line index in the page file): 'h' chapter, 'h3' sub-chapter, 'p' plain paragraph.
# ('en', slug) also covers the AI translations of that page.
def _kinds(h=(), h3=(), p=()): return {**{i: 'h' for i in h}, **{i: 'h3' for i in h3}, **{i: 'p' for i in p}}
# Principles: Afterlife/Rebirth, Karma and Spirituality are chapters of their own, like Materialism.
# Suffering in detail: wild animals, farm animals and humans are the chapters, the forms of suffering their sub-chapters;
# "Let's start with the biggest group of victims:" only leads into the first chapter.
_SUF = _kinds(h=(4, 14, 26), h3=(6, 8, 10, 12, 16, 18, 20, 22, 24, 28, 30, 32, 34, 36), p=(3,))
KINDS_BY_HAND = {
    ('en', 'principles-of-the-movement'): _kinds(h=(22, 24, 26)), ('es', 'principios-del-movimiento'): _kinds(h=(22, 24, 26)),
    ('it', 'principi-del-movimento'): _kinds(h=(22, 24, 26)), ('pl', 'zasady-ruchu'): _kinds(h=(23, 25, 27)),
    ('en', 'suffering-in-detail'): _SUF, ('es', 'sufrimiento-en-detalle'): _SUF, ('it', 'la-sofferenza-nei-dettagli'): _SUF,
    ('de', 'leid-im-detail'): _kinds(h=(4, 14, 26), h3=(6, 8, 10, 12, 16, 18, 20, 22, 24, 29, 31, 33, 35, 37), p=(3,)),
    ('pl', 'znaczenie-cierpienia'): _kinds(h=(1, 18, 30), h3=(8, 10, 12, 14, 16, 20, 22, 24, 26, 28, 32, 34, 36, 38, 40), p=(5,)),
    # Criticism: the parts of "Veganism" are sub-chapters; "Who would know?" is a sentence, not a heading.
    ('en', 'criticism-of-different-pro-life-ideologies'): _kinds(h3=(76, 83, 87, 95, 103, 109, 117, 127), p=(90,)),
}
# Pages whose chapters are numbered (1. Human Rights, 2. Left-wing politics …), by English slug.
NUMBERED = {'criticism-of-different-pro-life-ideologies'}

# Pictures from the English site (content/images.json, files in presentation/img), numbered so unwanted ones can be named.
IMAGES = json.loads((ROOT / 'content' / 'images.json').read_text(encoding='utf-8'))
PROLIFE_JS = (ROOT / 'tools' / 'prolife.js').read_text(encoding='utf-8')
SMOKE_JS = (ROOT / 'tools' / 'smoke.js').read_text(encoding='utf-8')   # shake and dark smoke at the end of long pages
EGGS_JS = (ROOT / 'tools' / 'eggs.js').read_text(encoding='utf-8')     # stars, logo x5, birth counter, console note
IMG_BASE = '/img/'
# Picture descriptions for screen readers and image search, per language (content/alt/<lang>.json, English as source).
# The photos on "Suffering in detail" (8 to 21) are described from a list the project gave; the build never looks at them.
ALT = {f.stem: json.loads(f.read_text(encoding='utf-8')) for f in (ROOT / 'content' / 'alt').glob('*.json')}

def figure(n, cls='pic', lang='en'):
    if n in diagrams.NUMBERS:   # redrawn as animated SVG in the theme colours
        return f'<figure class="{cls} diagram">{diagrams.diagram(n, lang)}</figure>'
    x = next(i for i in IMAGES if i['n'] == n)
    alt = ALT.get(lang, {}).get(str(n), ALT['en'].get(str(n), ''))   # empty for channel avatars beside their name
    img = f'<img src="{IMG_BASE}{x["file"]}" width="{x["w"]}" height="{x["h"]}" loading="lazy" decoding="async" alt="{esc(alt)}">'
    if x['page'] == 'suffering-in-detail':   # graphic photos: blurred until the reader chooses to see them
        line, btn = VEIL.get(lang, VEIL['en'])
        img = (f'<span class="veil-wrap">{img}<button class="veil" type="button" onclick="this.closest(\'figure\').classList.add(\'shown\')">'
               f'<span class="veil-p">{esc(line)}</span><span class="veil-b">{esc(btn)}</span></button></span>')
        cls += ' sensitive'
    if 'eff-pic' in cls:   # frame clips the hover zoom, so the picture keeps its size
        img = f'<span class="zoom">{img}</span>'
    return f'<figure class="{cls}">{img}</figure>'

def pics_for(en_slug):
    """{English line index: picture number} for a page."""
    return {i['where'][1]: i['n'] for i in IMAGES if i['page'] == en_slug and i['where'][0] == 'after'}

# History: protest photos sit above the caption naming their country, whatever the order on that language's page.
PROTEST = {'Germany': ('germany', 'deutschland', 'germania', 'alemania', 'niemc'), 'Poland': ('poland', 'polen', 'polonia', 'polsk'),
           'India': ('india', 'indien', 'indi')}

def own_pics(slug, rest):
    """{line index: picture} found by text on an original-language page, or None to place by chapter position."""
    if slug != 'history': return None
    en = json.loads((ROOT / 'content' / 'en' / 'history.json').read_text(encoding='utf-8'))
    found, last = {}, None
    for x in (i for i in IMAGES if i['page'] == 'history'):
        country = next((c for c in PROTEST if c in en[x['where'][1] + 1]), None)
        if not country: continue
        hit = next((k for k, l in enumerate(rest) if l.lower().startswith('prot') and any(w in l.lower() for w in PROTEST[country])), None)
        if hit is not None: found[hit - 1] = x['n']; last = max(last or 0, hit)
    left = [i['n'] for i in IMAGES if i['page'] == 'history' and i['n'] not in found.values()]
    if not found: return None
    for n in left:   # no caption for this country on this page: after the last protest photo's caption
        found[last] = n; last += 1
    return found

def join_buttons(lang):
    return (f'<p class="cta-links join">{wa_link(lang)}'
            f'<a class="btn primary" href="{DISCORD}"{link_attrs(DISCORD)}>{icon("discord")}Discord</a></p>')

CONCEPTS = {
 'a-ember':  dict(name='Ember',  mode='dark',  fonts='family=Source+Serif+4:ital,wght@0,400;0,600;1,400&family=Oswald:wght@500;600;700&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,600;1,6..72,400&family=JetBrains+Mono:wght@400;500'),
 'b-poster': dict(name='Poster', mode='dark',  fonts='family=Oswald:wght@400;600&family=Anton&family=Barlow:wght@400;500;600&family=JetBrains+Mono:wght@400;500'),
}

def linkify(s):
    s = esc(s)
    s = re.sub(r'(https?://[^\s<]+)', lambda m: f'<a href="{m.group(1)}"{link_attrs(m.group(1))}>{m.group(1)}</a>', s)
    return re.sub(r'\b([\w.+-]+@[\w-]+\.[\w.-]+)\b', r'<a href="mailto:\1">\1</a>', s)

ID_PREFIX = ''   # set by present.py so ids stay unique when all views live in one document

def slug_id(s, used):
    base = re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')[:40] or 'section'
    i, k = base, 2
    while i in used: i = f'{base}-{k}'; k += 1
    used.add(i); return ID_PREFIX + i

QM, COLON = '?？؟', ':：'
def outline(bl, ref=None):
    """Principles page: questions and short "Label:" lines become sub-chapters (h3); a "So to summarize:" line with
    two or more short points after it becomes a lead-in and a list. Uses punctuation and length only.
    ref: the English blocks a 1:1 translation mirrors; the decisions are read from them, the text comes from bl."""
    if ref is None or [b[0] for b in ref] != [b[0] for b in bl]: ref = bl
    t = lambda k: ref[k][1].rstrip() if len(ref[k]) > 1 and isinstance(ref[k][1], str) else ''
    own = lambda k: bl[k][1]
    short = lambda k: ref[k][0] in ('h', 'p') and len(t(k)) <= 100 and t(k)[-1:] not in QM + COLON
    # a heading followed by a long paragraph opens the next chapter, so it is not a summary point
    point = lambda k: short(k) and not (ref[k][0] == 'h' and k + 1 < len(ref) and ref[k + 1][0] == 'p' and len(t(k + 1)) > 100)
    out, n = [], 0
    while n < len(bl):
        if ref[n][0] in ('h', 'p') and t(n)[-1:] in COLON and len(t(n)) <= 40:
            k = n + 1
            while k < len(bl) and point(k): k += 1
            if k - n > 2:
                out += [('lead', own(n)), ('ul', [own(x) for x in range(n + 1, k)])]; n = k; continue
            out.append(('h3', own(n))); n += 1; continue
        if ref[n][0] == 'h' and t(n)[-1:] in QM:
            out.append(('h3', own(n))); n += 1; continue
        out.append(bl[n]); n += 1
    return out

DATE = re.compile(r'^\d{1,2}\.\d{1,2}\.\d{4}$')
SLOT = re.compile(r'^(.*?)[\s,]*(\d{1,2}:\d{2}\s*[-–]\s*\d{1,2}:\d{2})\s*[,;.]?$')
def history_outline(bl):
    """History page: a lead-in ending in ":" with nothing after it gets the social media link (the original embedded
    it there); a "City:" heading followed by dates becomes a sub-chapter with a day-by-day schedule;
    a heading ending in ":" that only introduces a paragraph becomes a lead-in."""
    txt = lambda k: bl[k][1].strip() if k < len(bl) and len(bl[k]) > 1 and isinstance(bl[k][1], str) else ''
    out, n = [], 0
    while n < len(bl):
        b, t = bl[n], txt(n)
        nxt = bl[n + 1][0] if n + 1 < len(bl) else ''
        if b[0] == 'p' and t[-1:] in COLON and nxt == 'h':
            out += [b, ('social',)]; n += 1; continue
        if b[0] in ('h', 'p') and t[-1:] in COLON and DATE.match(txt(n + 1)):
            out.append(('h3', t)); n += 1; days = []
            while n < len(bl) and bl[n][0] in ('p', 'h') and (DATE.match(txt(n)) or (days and SLOT.match(txt(n)))):
                if DATE.match(txt(n)): days.append((txt(n), []))
                else: m = SLOT.match(txt(n)); days[-1][1].append((m.group(2).replace(' ', ''), m.group(1).strip(' ,;')))
                n += 1
            out.append(('sched', days)); continue
        if b[0] == 'h' and t[-1:] in COLON and nxt == 'p' and len(txt(n + 1)) > 100:
            out.append(('lead', t)); n += 1; continue
        out.append(b); n += 1
    # a heading directly followed by another heading has no text of its own (PL: titles of embedded videos): plain line
    return [('p', b[1]) if b[0] == 'h' and k + 1 < len(out) and out[k + 1][0] == 'h' and b[1].strip()[-1:] not in COLON else b
            for k, b in enumerate(out)]

def sched_html(days):
    return '<div class="sched">' + ''.join(
        f'<section class="day"><p class="day-d mono">{esc(d)}</p><ul>'
        + ''.join(f'<li><span class="day-t mono" dir="ltr">{esc(t.replace("-", "–"))}</span><span class="day-p">{esc(p)}</span></li>' for t, p in slots)
        + '</ul></section>' for d, slots in days) + '</div>'

NUM = re.compile(r'^\s*\d+\)\s*')
URL = re.compile(r'(https?://\S+)')
def cosmic_outline(bl, ref=None):
    """Cosmic extinction page. Decisions come from the English blocks (ref) a 1:1 translation mirrors:
    follow-up questions ("So what if ...", "What if ...") and "Evidence number ..." are sub-chapters,
    a "...:" line followed by "1) 2) 3)" lines is a lead-in with a numbered list,
    "Source:" plus bare links (or "Source: <link>") become a compact source line, "Notes:" stays a chapter."""
    if ref is None or [b[0] for b in ref] != [b[0] for b in bl]: ref = bl
    t = lambda k: ref[k][1].strip() if len(ref[k]) > 1 and isinstance(ref[k][1], str) else ''
    own = lambda k: bl[k][1].strip()
    out, n = [], 0
    while n < len(bl):
        kind, en = ref[n][0], t(n)
        if kind in ('h', 'p') and en.endswith(':') and n + 1 < len(bl) and NUM.match(t(n + 1)):
            k = n + 1
            while k < len(bl) and NUM.match(t(k)): k += 1
            out += [('lead', own(n)), ('ol', [NUM.sub('', own(x)) for x in range(n + 1, k)])]; n = k; continue
        if kind == 'h' and en.rstrip(':') in ('Source', 'Sources'):
            k, urls = n + 1, []
            while k < len(bl) and URL.fullmatch(t(k)): urls.append(own(k)); k += 1
            out.append(('src', own(n).rstrip(':： '), urls)); n = k; continue
        m = URL.search(own(n)) if kind == 'p' else None
        if m and re.match(r'^(Source|Survey)\s*:', en):
            out.append(('src', own(n)[:m.start()].strip().rstrip(':： '), [m.group(1)])); n += 1; continue
        if kind == 'h' or (kind == 'p' and len(en) <= 100 and en.endswith(('?', ')')) and '?' in en and 'http' not in en):
            if en.startswith(('So what if', 'What if', 'Evidence')): out.append(('h3', own(n))); n += 1; continue
            if kind == 'p': out.append(('h', own(n))); n += 1; continue   # longer question lines are chapters too
        out.append(bl[n]); n += 1
    return out

def src_html(label, urls):
    """Sources as short links (site name), the full address in the title."""
    def host(u): return re.sub(r'^www\.', '', urllib.parse.urlsplit(u).netloc)
    links = ', '.join(f'<a href="{esc(u)}" title="{esc(u)}" rel="noopener">{esc(host(u))}</a>' for u in urls)
    return f'<p class="src"><span class="src-k mono">{esc(label)}</span> {links}</p>'

def render_blocks(blocks, used, lang='en'):
    out, toc = [], []
    for b in blocks:
        if b[0] == 'h':
            i = slug_id(re.sub(r'^\d+\. ', '', b[1]), used); toc.append((i, b[1].rstrip(':：')))
            out.append(f'<h2 id="{i}">{esc(b[1].rstrip(":："))}</h2>')
        elif b[0] == 'h3':
            i = slug_id(b[1], used); toc.append((i, b[1].rstrip(':：'), 3))
            out.append(f'<h3 class="sub" id="{i}">{esc(b[1].rstrip(":："))}</h3>')
        elif b[0] == 'sched':
            out.append(sched_html(b[1]))
        elif b[0] == 'social':
            out.append('<!--social-link-->')
        elif b[0] == 'lead':
            out.append(f'<p class="lead-in">{esc(b[1])}</p>')
        elif b[0] == 'give':
            out.append(give_box(lang))
        elif b[0] == 'join':
            out.append(join_buttons(lang))
        elif b[0] == 'pic':
            out.append(figure(b[1], lang=lang))
        elif b[0] == 'ol':
            out.append('<ol class="nl">' + ''.join(f'<li>{linkify(i)}</li>' for i in b[1]) + '</ol>')
        elif b[0] == 'src':
            out.append(src_html(b[1], b[2]))
        elif b[0] == 'ul':
            out.append('<ul>' + ''.join(f'<li>{linkify(i)}</li>' for i in b[1]) + '</ul>')
        else:
            out.append(f'<p>{linkify(b[1])}</p>')
    return '\n'.join(out), toc

def head_lede(lines, like=None):
    """Title, optional lede, rest. like: English lines that a translation mirrors (decides the structure)."""
    like = like or lines
    title, rest = lines[0], lines[1:]
    lede = None
    from blocks import is_heading
    r = like[1:]
    if len(r) > 1 and len(r[0]) <= 90 and not r[0].endswith('?') \
            and (r[0].endswith('.') or is_heading(r[0])) and is_heading(r[1]) and not r[1].endswith('?'):
        lede, rest = rest[0].rstrip(':：'), rest[1:]
    return title, lede, rest

def doc_body(lang, slug, lines, full_url, like=None):
    t = T[lang]; used = set()
    title, lede, rest = head_lede(lines, like)
    rest_like = like[len(lines) - len(rest):] if like else None
    truncated = False
    if slug == 'social-media-channels' and (len(lines) == len(SOCIAL_EN) or lang in SOCIAL_IDX):
        body, toc = social_body(lang, lines, used)
        return title, lede, body, toc, truncated
    off, key = len(lines) - len(rest), (lang, OF_EN[lang].get(slug, slug))
    kinds = {i - off: k for i, k in KINDS_BY_HAND.get(('en', slug) if like else key, {}).items()}
    bl = blocks_of(rest, rest_like, {i - off for i in JOIN.get(key, ())}, {i - off for i in DROP.get(key, ())}, kinds=kinds)
    pics = pics_for(slug)
    if pics:   # anchors from the English page, so original-language pages get the pictures in the same chapter
        en = json.loads((ROOT / 'content' / 'en' / f'{slug}.json').read_text(encoding='utf-8'))
        _, _, en_rest = head_lede(en); eoff = len(en) - len(en_rest)
        en_bl = blocks_of(en_rest, None, (), (), {i - eoff: n for i, n in pics.items()},
                          {i - eoff: k for i, k in KINDS_BY_HAND.get(('en', slug), {}).items()})
        own = own_pics(slug, rest) if not like else None
        if own is not None: bl = blocks_of(rest, rest_like, {i - off for i in JOIN.get(key, ())}, {i - off for i in DROP.get(key, ())}, own, kinds)
        else: bl = place_pics(bl, pic_anchors(en_bl), sum(b[0] in ('h', 'h3') for b in en_bl))
    if slug == 'donate': bl = give_blocks(bl, lang)
    if slug == 'history': bl = history_outline(bl)
    if slug == 'cosmic-extinction':
        bl = cosmic_outline(bl, blocks_of(rest_like, None, (), ()) if rest_like else None)
    if slug == 'principles-of-the-movement':
        bl = outline(bl, blocks_of(rest_like, None, (), (), kinds=kinds) if rest_like else None)
    if slug in NUMBERED:   # the number is shown, the anchor stays the chapter's name
        n = iter(range(1, len(bl) + 1))
        bl = [(b[0], f'{next(n)}. {b[1]}', *b[2:]) if b[0] == 'h' else b for b in bl]
    body, toc = render_blocks(bl, used, lang)
    if slug in NUMBERED:   # the overview numbers its entries itself
        toc = [(x[0], re.sub(r'^\d+\. ', '', x[1]), *x[2:]) for x in toc]
    return title, lede, body, toc, truncated

SOCIAL_EN = json.loads((ROOT / 'content' / 'en' / 'social-media-channels.json').read_text(encoding='utf-8'))
SOCIAL = json.loads((ROOT / 'content' / 'social.json').read_text(encoding='utf-8'))

# Line positions where a language's own channel page differs from the English one (PL lists Twitter/X too).
SOCIAL_IDX = {'pl': {65: 67, 77: 79, 88: 90, 91: 93, 94: 96}}

def handle(url):
    """'@name' from a profile link ('facebook.com/name' for Facebook, which has no @ handles)."""
    u = urllib.parse.urlsplit(url); name = u.path.strip('/').split('/')[0]
    return f'facebook.com/{name}' if 'facebook' in u.hostname else '@' + name.lstrip('@')

def social_body(lang, lines, used):
    """Channel cards (content/social.json: language > platform > accounts with links), the reader's language first.
    Groups are headed by the language's own name; intro and notes come from the page's lines (index-aligned with English);
    account names and channel bios stay as their owners wrote them."""
    L = lambda i: lines[SOCIAL_IDX.get(lang, {}).get(i, i)]
    out, toc = [f'<p>{esc(L(1))}</p><p>{esc(L(2))}</p>'], []
    for g in sorted(SOCIAL, key=lambda g: g['lang'] != lang):
        name = LANG_NAME[g['lang']]; i = slug_id(g['lang'], used); toc.append((i, name))
        out.append(f'<h2 id="{i}"' + (f' lang="{g["lang"]}"' if g['lang'] != lang else '') + f'>{esc(name)}</h2>')
        for pl in g['platforms']:
            if lang not in pl.get('only', [lang]): continue
            out.append(f'<h3 class="plat">{icon(pl["name"].lower())}{pl["name"]}<span class="count">{len(pl["items"])}</span></h3>')
            if 'note' in pl: out.append(f'<p class="plat-note">{esc(L(pl["note"]))}</p>')
            cards = []
            for x in pl['items']:
                h = handle(x['url']); nm = x.get('name', '')
                if nm.lower() == h.lstrip('@').lower(): nm = ''
                cards.append('<li>' + (figure(x['pic'], 'avatar') if x.get('pic') else '')
                             + f'<a href="{esc(x["url"])}"{link_attrs(x["url"])}>' + (f'<span class="nm">{esc(nm)}</span>' if nm else '')
                             + f'<span class="hd" dir="ltr">{esc(h)}</span></a>'
                             + (f'<span class="bio">{esc(x["desc"])}</span>' if x.get('desc') else '') + '</li>')
            out.append(f'<ul class="channels{" wide" if any(x.get("desc") for x in pl["items"]) else ""}">' + ''.join(cards) + '</ul>')
    out.append(f'<p class="note">{esc(L(94))}</p>')
    return '\n'.join(out), toc

# FAQ pictures close the answer to an English question (content/images.json "where": ["answer", question number]).
# Original-language FAQs number their questions differently: English number -> their number.
FAQ_Q = {'de': {14: 15, 34: 32, 35: 12}, 'es': {14: 15, 34: 33, 35: 12}, 'it': {14: 15, 34: 33, 35: 12},
         'pl': {34: 32, 35: 37}}   # 34, 35: veganism and antinatalism (FAQ_MORE); the originals ask them in their own words

# Full FAQ answers that end with a button to a chapter of the criticism page:
# question number (English and its translations) -> line of that chapter's heading on the criticism page.
FAQ_MORE = {34: 61, 35: 23}
CRITICISM = 'criticism-of-different-pro-life-ideologies'

def faq_more(lang, href):
    """{question number: button to the criticism chapter}, in the page's language. The anchor comes from that page's own toc."""
    crit = OF_EN[lang].get(CRITICISM)
    if not crit: return {}
    cl = json.loads((ROOT / 'content' / lang / f'{crit}.json').read_text(encoding='utf-8'))
    like = json.loads((ROOT / 'content' / 'en' / f'{CRITICISM}.json').read_text(encoding='utf-8')) if crit in AI[lang] else None
    toc = doc_body(lang, CRITICISM, cl, '', like)[3]
    out = {}
    for k, i in FAQ_MORE.items():
        h = cl[i].strip().rstrip(':：').strip()
        a = next(x[0] for x in toc if len(x) == 2 and x[1].strip().endswith(h))
        out[k] = (f'<p class="cta-links"><a class="btn" href="{href(crit)}#{a}">'
                  f'{esc(NAV[lang][crit])} · {esc(h)} <span aria-hidden="true" class="arr">→</span></a></p>')
    return out

def faq_body(lang, slug, lines, like=None, href=None):
    t = T[lang]
    title, lede, rest = head_lede(lines, like)
    intro, pairs = faq_pairs(rest, like[len(lines) - len(rest):] if like else None)
    shown = pairs
    intro_html = ''.join(f'<p>{linkify(l)}</p>' for l in intro)
    more_btn = faq_more(lang, href) if EN_OF[lang][slug] == 'full-faq' else {}
    if not like: more_btn = {FAQ_Q.get(lang, {}).get(k, k): v for k, v in more_btn.items()}
    pics = {x['where'][1]: x['n'] for x in IMAGES if x['page'] == EN_OF[lang][slug] and x['where'][0] == 'answer'}
    if not like: pics = {FAQ_Q.get(lang, {}).get(k, k): n for k, n in pics.items()}
    items = []
    for k, (q, a) in enumerate(shown, 1):   # counter-set keeps each question's number while the search hides others
        items.append(f'<details style="counter-set:q {k}"><summary>{esc(q)}</summary><div class="a">' + ''.join(f'<p>{linkify(p)}</p>' for p in a)
                     + (figure(pics[k], 'pic', lang) if k in pics else '') + more_btn.get(k, '') + '</div></details>')
    more = ''
    if EN_OF[lang][slug] == 'full-faq':
        ph, cnt, none, end, mail = FAQ_FIND[lang]
        soc = next((x for x, _ in PAGES[lang] if EN_OF[lang][x] == 'social-media-channels'), None)
        end = esc(end).replace('{mail}', f'<a href="mailto:{EMAIL}">{esc(mail)}</a>').replace('{tiktok}', f'<a href="{href(soc)}">TikTok</a>' if soc else 'TikTok')
        find = (f'<div class="faq-find" data-count="{esc(cnt)}"><label><span class="sr">{esc(ph)}</span>'
                f'<input type="search" placeholder="{esc(ph)}" autocomplete="off" spellcheck="false"></label>'
                f'<p class="faq-count mono" aria-live="polite"></p></div>')
        return (title, lede, intro_html + find + '<div class="faq">' + '\n'.join(items) + '</div>'
                + f'<p class="faq-none" hidden>{esc(none)}</p><p class="faq-ask">{end}</p><script>{FAQ_JS}</script>', [], False)
    if EN_OF[lang][slug] == 'basic-faq':
        more = f'<p class="cta-links faq-more"><a class="btn primary" href="{href(OF_EN[lang]["full-faq"])}">{T[lang]["full_faq"]} <span aria-hidden="true" class="arr">→</span></a></p>'
    return title, lede, intro_html + '<div class="faq">' + '\n'.join(items) + '</div>' + more, [], len(shown) < len(pairs)

def sitenav(lang, slug):
    t = T[lang]; cur = ' aria-current="page"'
    items = ''.join('<li><a href="%s"%s>%s</a></li>' % (url(lang, s_), cur if s_ == slug else '', esc(NAV[lang][s_])) for s_, _ in PAGES[lang])
    return f'<nav class="sitenav" id="sitenav" aria-label="Main"><ul>{items}</ul></nav>'

def lang_select(lang, url):
    """Language picker. url(other_lang) gives each option's target; site.js / present.js navigate on change."""
    t = T[lang]
    opts = ''.join(f'<option value="{url(l)}" lang="{l}"{" selected" if l == lang else ""}>{CODE[l]} · {LANG_NAME[l]}</option>' for l in LANGS)
    return f'<label class="lang-wrap"><span class="lang" aria-hidden="true">{CODE[lang]}</span><select class="lang-select" aria-label="{t["lang"]}">{opts}</select></label>'

def header(lang, slug):
    t = T[lang]
    picker = lang_select(lang, lambda l: url(l, counterpart(lang, slug, l)))
    return f'''<a class="skip" href="#main">{t["skip"]}</a>
<div class="progress" aria-hidden="true"><i></i></div>
{top_button(lang)}
<header class="top">
  <div class="lead">
    <a class="brand" href="{url(lang, 'home')}" aria-label="{t["home_link"]}"><span class="logo" role="img" aria-label="Pro Extinction logo"></span><span class="wordmark">PRO EXTINCTION</span></a>
  </div>
  <div class="tools">
    {picker}
    <button class="theme" type="button" aria-label="{t["theme"]}" title="{t["theme"]}"><span></span></button>
    <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="sitenav"><span class="bars" aria-hidden="true"></span><span class="menu-t">{t["menu"]}</span></button>
  </div>
</header>'''

# Footer counter: humans, farm animals, wild animals and insects born since the page was opened. Per second, from yearly figures:
# about 132 million human births (UN World Population Prospects), about 83 billion land animals raised and killed for food (FAOSTAT),
# a few hundred billion wild birds and mammals (about 50 billion wild birds, Callaghan et al. 2021; wild mammals mostly short-lived rodents
# and bats, Greenspoon et al. 2023) and, roughly, 10^19 insects alive at any time (Smithsonian) living a few weeks.
# Animal figures are rough, hence the tilde.
BORN_RATES = '4.18,2630,10000,1000000000000'
BORN = {
    'en': ('Born since you opened this page', 'humans', 'farm animals', 'wild animals', 'insects'),
    'de': ('Geboren, seit du diese Seite geöffnet hast', 'Menschen', 'Nutztiere', 'Wildtiere', 'Insekten'),
    'pl': ('Urodzonych od otwarcia tej strony', 'ludzi', 'zwierząt hodowlanych', 'dzikich zwierząt', 'owadów'),
    'es': ('Nacidos desde que abriste esta página', 'personas', 'animales de granja', 'animales salvajes', 'insectos'),
    'it': ('Nati da quando hai aperto questa pagina', 'persone', 'animali da allevamento', 'animali selvatici', 'insetti'),
    'fr': ('Nés depuis que vous avez ouvert cette page', 'humains', "animaux d'élevage", 'animaux sauvages', 'insectes'),
    'pt': ('Nascidos desde que você abriu esta página', 'pessoas', 'animais de criação', 'animais selvagens', 'insetos'),
    'ru': ('Родилось, пока открыта эта страница', 'людей', 'животных на фермах', 'диких животных', 'насекомых'),
    'zh': ('自你打开本页以来出生', '人', '养殖动物', '野生动物', '昆虫'),
    'hi': ('यह पेज खोलने के बाद से जन्मे', 'इंसान', 'फ़ार्म के जानवर', 'जंगली जानवर', 'कीड़े'),
    'ar': ('وُلد منذ فتحت هذه الصفحة', 'إنسانا', 'حيوانا في المزارع', 'حيوانا بريا', 'حشرة'),
    'bn': ('পাতাটি খোলার পর থেকে জন্মেছে', 'মানুষ', 'খামারের প্রাণী', 'বন্য প্রাণী', 'পোকামাকড়'),
    'ur': ('یہ صفحہ کھولنے کے بعد سے پیدا ہوئے', 'انسان', 'فارم کے جانور', 'جنگلی جانور', 'کیڑے'),
    'id': ('Lahir sejak kamu membuka halaman ini', 'manusia', 'hewan ternak', 'hewan liar', 'serangga'),
    'ja': ('このページを開いてから生まれた数', '人', '家畜', '野生動物', '昆虫'),
    'tr': ('Bu sayfayı açtığından beri doğanlar', 'insan', 'çiftlik hayvanı', 'yaban hayvanı', 'böcek'),
    'vi': ('Số sinh ra từ khi bạn mở trang này', 'người', 'vật nuôi', 'động vật hoang dã', 'côn trùng'),
    'ko': ('이 페이지를 연 뒤 태어난 수', '사람', '가축', '야생동물', '곤충'),
    'fa': ('از وقتی این صفحه را باز کردی به دنیا آمده‌اند', 'انسان', 'دام', 'حیوان وحشی', 'حشره'),
    'mr': ('हे पान उघडल्यापासून जन्मलेले', 'माणसे', 'शेतीतील प्राणी', 'वन्य प्राणी', 'कीटक'),
    'te': ('ఈ పేజీ తెరిచినప్పటి నుంచి పుట్టినవి', 'మనుషులు', 'పశువులు', 'అడవి జంతువులు', 'కీటకాలు'),
    'ta': ('இந்தப் பக்கத்தைத் திறந்ததிலிருந்து பிறந்தவை', 'மனிதர்கள்', 'பண்ணை விலங்குகள்', 'காட்டு விலங்குகள்', 'பூச்சிகள்'),
    'sw': ('Waliozaliwa tangu ufungue ukurasa huu', 'binadamu', 'wanyama wa shambani', 'wanyama pori', 'wadudu'),
    'th': ('เกิดขึ้นตั้งแต่คุณเปิดหน้านี้', 'คน', 'สัตว์ในฟาร์ม', 'สัตว์ป่า', 'แมลง'),
    'nl': ('Geboren sinds je deze pagina opende', 'mensen', 'landbouwdieren', 'wilde dieren', 'insecten'),
    'uk': ('Народилося, відколи відкрито цю сторінку', 'людей', 'тварин на фермах', 'диких тварин', 'комах'),
    'tl': ('Isinilang mula nang buksan mo ang pahinang ito', 'tao', 'hayop sa bukid', 'hayop sa ilang', 'insekto'),
    'pa': ('ਇਹ ਪੰਨਾ ਖੋਲ੍ਹਣ ਤੋਂ ਬਾਅਦ ਜਨਮੇ', 'ਇਨਸਾਨ', 'ਫ਼ਾਰਮ ਦੇ ਜਾਨਵਰ', 'ਜੰਗਲੀ ਜਾਨਵਰ', 'ਕੀੜੇ'),
    'gu': ('આ પાનું ખોલ્યા પછી જન્મેલા', 'માણસો', 'ફાર્મનાં પ્રાણીઓ', 'જંગલી પ્રાણીઓ', 'જીવજંતુઓ'),
}
# Logo clicked five times: the page fades away and the manifesto's last line appears (its own last line in each language).
PEACE_OVERRIDE = {'es': 'Abolamos el sufrimiento. ¡Por justicia!'}   # the closing words of the Spanish manifesto's long last paragraph
def peace(lang):
    if lang in PEACE_OVERRIDE: return PEACE_OVERRIDE[lang]
    return json.loads((ROOT / 'content' / lang / f'{OF_EN[lang]["manifesto"]}.json').read_text(encoding='utf-8'))[-1]

def footer(lang, cta=True):
    """Call to action with the contact buttons (left out on the contact page, which shows them under its text), then the footer."""
    t = T[lang]
    return (f'''<section class="cta" aria-label="{t["action"]}">
  <hr class="slash">
  <h2>{t["action"]}</h2>
  <p class="cta-sub">{t["tagline"]}</p>
  <p class="cta-links">{wa_link(lang)}<a class="btn primary" href="{DISCORD}"{link_attrs(DISCORD)}>{icon("discord")}Discord</a><a class="btn" href="mailto:{EMAIL}">{icon("mail")}{EMAIL}</a>{share_btn(lang)}</p>
</section>
''' if cta else '') + f'''<footer class="foot" data-peace="{esc(peace(lang))}" data-discord="{DISCORD}"><p class="mono">{t["foot"].replace("Global", '<span class="glob">Global</span>', 1)}{legal_links(lang)}<span data-share hidden> · <button class="share legal" type="button">{esc(SHARE[lang][0])}</button></span></p>{born_line(lang)}<span id="new-tab" hidden>{esc(NEW_TAB[lang])}</span></footer>{(gate_html(lang) if WHATSAPP_QUIZ else '') if WHATSAPP_OPEN else wa_closed_html(lang)}{share_html(lang)}'''

def born_line(lang):
    label, humans, animals, wild, insects = BORN[lang]
    return (f'<p class="born mono" data-rates="{BORN_RATES}" title="Rough estimates from yearly figures (UN, FAOSTAT, wildlife and insect counts)">{esc(label)}: '
            + ' · '.join(f'<span class="bn"><span dir="ltr">{"~" if i else ""}<b data-i="{i}">0</b></span> {esc(w)}</span>'   # ~ marks rough figures
                         for i, w in enumerate((humans, animals, wild, insects))) + '</p>')

def page_main(lang, slug, kind, href=None):
    """Title and <main> content of one page (shared by the multi-page prototype and the single-file presentation)."""
    t = T[lang]
    href = href or (lambda s: url(lang, s))
    ki = slug in AI[lang]
    if kind == 'home':
        return NAV[lang]['home'], home_main(lang, href), 'home'
    lines = json.loads((ROOT / 'content' / lang / f'{slug}.json').read_text(encoding='utf-8'))
    like = json.loads((ROOT / 'content' / 'en' / f'{EN_OF[lang][slug]}.json').read_text(encoding='utf-8')) if ki else None
    if kind == 'faq': title, lede, body, toc, truncated = faq_body(lang, slug, lines, like, href)
    else:
        title, lede, body, toc, truncated = doc_body(lang, EN_OF[lang][slug], lines, '', like)
    notes = ''
    if ki: notes += f'<p class="note ki"><span class="tag">{t["ki_tag"]}</span> {t["ki"]}</p>'
    toc_html = ''
    if len(toc) > 1 and EN_OF[lang][slug] != 'join-us':   # join us is two short blocks, no overview needed
        items = ''.join(f'<li{" class=sub" if x[2:] == (3,) else ""}><a href="#{x[0]}">{esc(x[1])}</a></li>' for x in toc)
        # two copies: above the text on narrow screens, beside the first paragraph after the first chapter heading on wide ones
        toc_html = f'<nav class="toc toc-top" aria-label="{t["toc"]}"><p class="mono">{t["toc"]}</p><ol>{items}</ol></nav>'
        side = f'<nav class="toc toc-side" aria-label="{t["toc"]}"><p class="mono">{t["toc"]}</p><ol>{items}</ol></nav>'
        if (lang, slug) == ('en', 'criticism-of-different-pro-life-ideologies'):   # joke button, shown by theme B only
            side += f'<button class="prolife" type="button" tabindex="-1" aria-hidden="true">Press me if you\'re pro-life</button><script>{PROLIFE_JS}</script>'
        # beside the first paragraph of the first chapter when the text opens with a chapter heading (manifesto);
        # otherwise at the very top of the text, so intro paragraphs don't push it down
        if body.lstrip().startswith('<h2'): body = body.replace('</h2>', '</h2>' + side, 1)
        else: notes = side + notes
    lede_html = f'<p class="lede">{esc(lede)}</p>' if lede else ''
    soc = next((x for x, _ in PAGES[lang] if EN_OF[lang][x] == 'social-media-channels'), None)
    if EN_OF[lang][slug] == 'contact':   # every way to reach us right on the contact page, not only in the footer
        body += (f'<p class="cta-links join">{wa_link(lang)}'
                 f'<a class="btn primary" href="{DISCORD}"{link_attrs(DISCORD)}>{icon("discord")}Discord</a><a class="btn" href="mailto:{EMAIL}">{icon("mail")}{EMAIL}</a>{share_btn(lang)}</p>'
                 + '<div class="debate">' + debate_html(lang) + ('<!--social-link-->' if soc else '') + '</div>')
    body = body.replace('<!--social-link-->', f'<p class="go"><a class="btn" href="{href(soc)}">{esc(NAV[lang][soc])} <span aria-hidden="true">&rarr;</span></a></p>' if soc else '')
    main = f'<article class="doc"><header class="doc-head"><p class="mono kicker">{esc(NAV[lang][slug])}</p><h1>{esc(title)}</h1>{lede_html}<hr class="slash"></header>{toc_html}<div class="prose">{notes}{body}</div></article>'
    if EN_OF[lang][slug] == 'cosmic-extinction':   # easter egg: the stars go out while reading (eggs.js)
        main = '<div class="stars" aria-hidden="true"></div>' + main
    return title, main, 'page'

# ---- search engines
SITE_URL = 'https://proextinction.com'
INDEXABLE = True    # the one switch: True lets search engines in (robots.txt, X-Robots-Tag header in vercel.json, meta robots)
HREFLANG = {'zh': 'zh-Hans'}
SEO = {l: json.loads((ROOT / 'content' / 'seo' / f'{l}.json').read_text(encoding='utf-8')) for l in LANGS}
IMPRINT = False   # legal notice (content/legal/<lang>.json "imprint") kept ready but not published; True builds it and links it in the footer
LEGAL = {l: json.loads((ROOT / 'content' / 'legal' / f'{l}.json').read_text(encoding='utf-8')) for l in ('de', 'en')}
DRAFT = re.compile(r'\[[^\]]*[A-ZÄÖÜ]{3,}[^\]]*\]')   # a placeholder like [STREET AND NUMBER]: the page stays out of search engines
# Footer links to the legal pages; languages without their own version link to the English one.
LEGAL_LABEL = {
 'en': ('Legal notice', 'Privacy'), 'de': ('Impressum', 'Datenschutz'), 'pl': ('Nota prawna', 'Prywatność'),
 'es': ('Aviso legal', 'Privacidad'), 'it': ('Note legali', 'Privacy'), 'fr': ('Mentions légales', 'Confidentialité'),
 'pt': ('Aviso legal', 'Privacidade'), 'ru': ('Правовая информация', 'Конфиденциальность'), 'zh': ('法律声明', '隐私'),
 'hi': ('कानूनी सूचना', 'निजता'), 'ar': ('إشعار قانوني', 'الخصوصية'), 'bn': ('আইনি তথ্য', 'গোপনীয়তা'),
 'ur': ('قانونی معلومات', 'رازداری'), 'id': ('Informasi hukum', 'Privasi'), 'ja': ('運営者情報', 'プライバシー'),
 'tr': ('Yasal bilgiler', 'Gizlilik'), 'vi': ('Thông tin pháp lý', 'Quyền riêng tư'), 'ko': ('법적 고지', '개인정보'),
 'fa': ('اطلاعات حقوقی', 'حریم خصوصی'), 'mr': ('कायदेशीर माहिती', 'गोपनीयता'), 'te': ('చట్టపరమైన సమాచారం', 'గోప్యత'),
 'ta': ('சட்டத் தகவல்', 'தனியுரிமை'), 'sw': ('Taarifa za kisheria', 'Faragha'), 'th': ('ข้อมูลทางกฎหมาย', 'ความเป็นส่วนตัว'),
 'nl': ('Colofon', 'Privacy'), 'uk': ('Правова інформація', 'Конфіденційність'), 'tl': ('Legal na abiso', 'Privacy'),
 'pa': ('ਕਾਨੂੰਨੀ ਜਾਣਕਾਰੀ', 'ਨਿੱਜਤਾ'), 'gu': ('કાનૂની માહિતી', 'ગોપનીયતા'),
}

def legal_links(lang):
    """Privacy (and, if IMPRINT, legal notice) links, appended to the footer's first line."""
    src = lang if lang in LEGAL else 'en'
    a, b = LEGAL_LABEL[lang]
    keys = [('imprint', a)] * IMPRINT + [('privacy', b)]
    return ''.join(f' · <a class="legal" href="{url(src, LEGAL[src][k]["slug"])}">{esc(lab)}</a>' for k, lab in keys)

def legal_main(lang, key):
    """A legal page from content/legal/<lang>.json: '## ' starts a heading, '! ' a draft note, other lines are paragraphs."""
    d = LEGAL[lang][key]; out = []
    for line in d['text']:
        if line.startswith('## '): out.append(f'<h2>{esc(line[3:])}</h2>')
        elif line.startswith('! '): out.append(f'<p class="note draft"><span class="tag">!</span> {esc(line[2:])}</p>')
        else: out.append(f'<p>{linkify(line)}</p>')
    return d['title'], (f'<article class="doc legal-doc"><header class="doc-head"><h1>{esc(d["title"])}</h1><hr class="slash"></header>'
                        f'<div class="prose">{"".join(out)}</div></article>')

def alternates(lang, slug):
    """[(hreflang, path)] for the same page in every language that has it. x-default is English,
    except for the home pages, where it is the language chooser at / (which lists them back)."""
    en = EN_OF[lang].get(slug)
    if not en: return [(HREFLANG.get(lang, lang), url(lang, slug))]
    out = [(HREFLANG.get(l, l), url(l, OF_EN[l][en])) for l in LANGS if en in OF_EN[l]]
    return out + [('x-default', '/' if en == 'home' else url('en', OF_EN['en'][en]))]

def jsonld(lang):
    return json.dumps({'@context': 'https://schema.org', '@graph': [
        {'@type': 'Organization', '@id': SITE_URL + '/#org', 'name': 'Pro Extinction', 'url': SITE_URL, 'email': EMAIL,
         'logo': SITE_URL + '/logo.png', 'foundingDate': '2024', 'sameAs': [DISCORD] + SAME_AS},
        {'@type': 'WebSite', '@id': SITE_URL + '/#site', 'name': 'Pro Extinction', 'url': SITE_URL,
         'inLanguage': LANGS, 'publisher': {'@id': SITE_URL + '/#org'}}]}, ensure_ascii=False)

# The project's own main accounts (content/social.json lists every activist channel), for search engines' knowledge panel.
SAME_AS = ['https://www.tiktok.com/@proextinction.com', 'https://www.instagram.com/proextinction', 'https://youtube.com/@pro_extinction']

def faq_ld(lang, slug):
    """FAQPage data for search engines: the page's questions with their answers as plain text."""
    lines = json.loads((ROOT / 'content' / lang / f'{slug}.json').read_text(encoding='utf-8'))
    like = json.loads((ROOT / 'content' / 'en' / f'{EN_OF[lang][slug]}.json').read_text(encoding='utf-8')) if slug in AI[lang] else None
    rest = head_lede(lines, like)[2]
    pairs = faq_pairs(rest, like[len(lines) - len(rest):] if like else None)[1]
    return json.dumps({'@context': 'https://schema.org', '@type': 'FAQPage', 'inLanguage': lang, 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': '\n'.join(a)}} for q, a in pairs]}, ensure_ascii=False)

def head(lang, path, title, desc, alts=(), index=True, home=False, data=None):
    """<head> contents shared by every page: theme before paint, SEO tags, the one stylesheet.
    data: JSON-LD for search engines (the home page's organisation is added by itself)."""
    robots = 'index, follow' if INDEXABLE and index else 'noindex, nofollow'
    links = ''.join(f'<link rel="alternate" hreflang="{h}" href="{SITE_URL}{p}">\n' for h, p in alts)
    data = data or (jsonld(lang) if home else None)
    ld = '<script type="application/ld+json">' + data.replace('</', '<\\/') + '</script>\n' if data else ''
    return f'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{SITE_URL}{path}">
{links}<meta property="og:type" content="website">
<meta property="og:site_name" content="Pro Extinction">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{SITE_URL}{path}">
<meta property="og:image" content="{SITE_URL}/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0b0708">
{ld}<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/style.css">
<script>(function(){{var d=document.documentElement,m=null;try{{m=new URLSearchParams(location.search).get('theme')||localStorage.getItem('pe-theme')}}catch(e){{}}
d.dataset.theme=m==='light'?'light':'dark'}})()</script>'''

HOME_TITLE = {'en': 'Ending forced existence and suffering', 'de': 'Erzwungene Existenz und Leid beenden',
    'pl': 'Koniec przymusowego istnienia i cierpienia', 'es': 'Acabar con la existencia impuesta y el sufrimiento',
    'it': "Fine dell'esistenza forzata e della sofferenza", 'fr': "En finir avec l'existence forcée et la souffrance",
    'pt': 'Acabar com a existência forçada e o sofrimento', 'ru': 'Конец вынужденному существованию и страданию',
    'zh': '终结被迫的存在与苦难', 'hi': 'जबरन अस्तित्व और पीड़ा का अंत', 'ar': 'إنهاء الوجود القسري والمعاناة',
    'bn': 'জোরপূর্বক অস্তিত্ব ও দুঃখের অবসান', 'ur': 'جبری وجود اور تکلیف کا خاتمہ', 'id': 'Mengakhiri keberadaan paksa dan penderitaan',
    'ja': '強いられた存在と苦しみを終わらせる', 'tr': 'Zorla var olmaya ve acıya son', 'vi': 'Chấm dứt sự tồn tại bị ép buộc và khổ đau',
    'ko': '강요된 존재와 고통을 끝내다', 'fa': 'پایان دادن به هستی اجباری و رنج', 'mr': 'लादलेल्या अस्तित्वाचा आणि दुःखाचा अंत',
    'te': 'బలవంతపు ఉనికికి, బాధకు ముగింపు', 'ta': 'கட்டாய இருப்புக்கும் துன்பத்துக்கும் முடிவு', 'sw': 'Kukomesha uwepo wa kulazimishwa na mateso',
    'th': 'ยุติการดำรงอยู่ที่ถูกบังคับและความทุกข์', 'nl': 'Een einde aan gedwongen bestaan en lijden', 'uk': 'Кінець вимушеному існуванню і стражданню',
    'tl': 'Wakasan ang sapilitang pag-iral at pagdurusa', 'pa': 'ਜ਼ਬਰਦਸਤੀ ਹੋਂਦ ਅਤੇ ਦੁੱਖ ਦਾ ਅੰਤ', 'gu': 'ફરજિયાત અસ્તિત્વ અને દુઃખનો અંત'}

def page_html(lang, slug, kind, title=None, main=None, desc=None, index=True):
    if main is None: title, main, body_class = page_main(lang, slug, kind)
    else: body_class = 'page'
    # search result titles (Google shows about 60 characters): the home page says briefly what the organisation is, in its own language (the English slogan is the same everywhere);
    # other pages use their heading, or the short menu name when the heading is long or set in capitals
    if kind == 'home': full = f'Pro Extinction | {HOME_TITLE[lang]}'
    else: full = f'{NAV[lang][slug] if slug in NAV[lang] and (len(title) > 50 or title.isupper()) else title} | Pro Extinction'
    alts = alternates(lang, slug) if slug in EN_OF[lang] else ()
    return f'''<!doctype html>
<html lang="{lang}" dir="{DIR(lang)}" data-concept="b-poster">
<head>
{head(lang, url(lang, slug), full, desc or SEO[lang][slug], alts, index, kind == 'home', faq_ld(lang, slug) if kind == 'faq' else None)}
</head>
<body class="{body_class}">
{header(lang, slug)}
<div class="shell">
{sitenav(lang, slug)}
<main id="main">
{main}
</main>
</div>
{footer(lang, EN_OF[lang].get(slug) != 'contact')}
<script src="/site.js" defer></script>
<script>{SMOKE_JS}</script>
<script>{EGGS_JS}</script>
</body>
</html>
'''

def home_main(lang, href):
    t = T[lang]
    ki = f'<p class="note ki"><span class="tag">{t["ki_tag"]}</span> {t["ki"]}</p>' if lang in FULL_AI else ''
    eff_pic = {i['where'][1]: i['n'] for i in IMAGES if i['page'] == 'home'}
    efforts = ''.join(f'<li>{figure(eff_pic[i], "pic eff-pic", lang) if i in eff_pic else ""}<span class="num mono">{i+1:02d}</span><p class="eff-label mono">{t["effort"]} {i+1}</p><p>{esc(x)}</p></li>' for i, x in enumerate(t['efforts']))
    # "Questions?": the pages that answer most questions first, the email only as the last option
    read = [OF_EN[lang][e] for e in ('manifesto', 'basic-faq', 'full-faq', 'principles-of-the-movement', 'suffering-in-detail') if e in OF_EN[lang]]
    read_more = '<ul class="q-links">' + ''.join(f'<li><a class="btn" href="{href(s)}">{esc(NAV[lang][s])}</a></li>' for s in read) + '</ul>'
    return f'''<section class="hero">
  {HERO_LOGO}
  <h1 class="wordmark">PRO EXTINCTION</h1>
  <p class="hero-tag">{t["tagline"]}</p>
  <p class="hero-sub">{esc(t["sub"])}</p>
  <p class="hero-cta"><a class="btn primary" href="{href(OF_EN[lang]['join-us'])}">{t["cta1"]}</a><a class="btn" href="{href(OF_EN[lang]['manifesto'])}">{t["cta2"]}</a></p>
</section>
<section class="mission"><hr class="slash"><p class="mono kicker">{t["mission"]}</p><blockquote>{esc(t["mission_text"])}</blockquote></section>
<section class="efforts"><ol>{efforts}</ol></section>
<section class="questions"><h2>{t["questions"]}</h2>{read_more}<p class="q-mail">{linkify(t["questions_text"])}</p></section>
<section class="questions debate">{debate_html(lang)}{ki}</section>'''

def _svg_uri(name):
    svg = (ASSETS / f'{name}.svg').read_text(encoding='utf-8').replace('currentColor', '#000')
    return 'data:image/svg+xml,' + urllib.parse.quote(svg, safe="/:=' ")

def logo_css():
    """Static logo (header) plus the three layers of the animated hero logo: snake, cut gap, slash."""
    return (f'.logo{{--logo:url("{_svg_uri("logo")}");-webkit-mask:var(--logo) center/contain no-repeat;mask:var(--logo) center/contain no-repeat;background:currentColor;display:inline-block}}\n'
            f':root{{--logo-snake:url("{_svg_uri("logo-snake")}");--logo-cut:url("{_svg_uri("logo-cut")}");--logo-slash:url("{_svg_uri("logo-slash")}")}}\n')

HERO_LOGO = ('<span class="hero-logo" role="img" aria-label="Pro Extinction logo">'
             '<span class="lg lg-snake"></span><span class="lg lg-cut"></span><span class="lg lg-slash"></span></span>')

def css():
    """One stylesheet for every page: local fonts (only the families the design uses), base, design tokens, design, logo."""
    used = ('Oswald', 'Anton', 'Barlow', 'JetBrains Mono')
    fonts = ''.join(l + '\n' for l in (ROOT / 'tools' / 'fonts.css').read_text(encoding='utf-8').splitlines()
                    if any(f"font-family:'{f}'" in l for f in used)).replace('url(fonts/', 'url(/fonts/')
    return (fonts + (ROOT / 'tools/css/base.css').read_text(encoding='utf-8') + '\n' + (ROOT / 'brand/b-poster/tokens.css').read_text(encoding='utf-8')
            + '\n' + (ROOT / 'tools/css/b.css').read_text(encoding='utf-8') + '\n' + logo_css())

def build():
    (OUT / 'style.css').write_text(css(), encoding='utf-8')
    (OUT / 'site.js').write_text((ASSETS / 'site.js').read_text(encoding='utf-8'), encoding='utf-8')
    paths = []   # (path, alternates, last change) for the sitemap
    old = sitemap_dates()
    def write(f, html, path):
        """Writes a page; returns the date it last changed (kept from the sitemap while the file stays the same)."""
        same = f.exists() and f.read_text(encoding='utf-8') == html
        f.write_text(html, encoding='utf-8')
        return old.get(path) if same and old.get(path) else datetime.date.today().isoformat()
    for lang in LANGS:
        d = OUT / lang; d.mkdir(parents=True, exist_ok=True)
        for slug, kind in PAGES[lang]:
            day = write(d / ('index.html' if slug == 'home' else f'{slug}.html'), page_html(lang, slug, kind), url(lang, slug))
            paths.append((url(lang, slug), alternates(lang, slug), day))
    for lang in LEGAL:
        for key in ('imprint', 'privacy')[not IMPRINT:]:
            p = LEGAL[lang][key]; title, main = legal_main(lang, key)
            draft = any(DRAFT.search(x) for x in p['text'])
            day = write(OUT / lang / f'{p["slug"]}.html', page_html(lang, p['slug'], 'doc', title, main, p['description'], not draft), url(lang, p['slug']))
            if not draft: paths.append((url(lang, p['slug']), (), day))
    (OUT / 'index.html').write_text(root_page(), encoding='utf-8')
    (OUT / '404.html').write_text(not_found(), encoding='utf-8')
    (OUT / 'sitemap.xml').write_text(sitemap(paths), encoding='utf-8')
    (OUT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n' if INDEXABLE else 'User-agent: *\nDisallow: /\n', encoding='utf-8')
    hosting()
    print('built', len(paths), 'pages into site/')

def sitemap_dates():
    """{path: lastmod} from the sitemap of the previous build."""
    f = OUT / 'sitemap.xml'
    if not f.exists(): return {}
    return {loc[len(SITE_URL):]: day for loc, day in re.findall(r'<loc>([^<]+)</loc><lastmod>([^<]+)</lastmod>', f.read_text(encoding='utf-8'))}

def sitemap(paths):
    rows = []
    for p, alts, day in paths:
        alt = ''.join(f'<xhtml:link rel="alternate" hreflang="{h}" href="{SITE_URL}{a}"/>' for h, a in alts)
        rows.append(f'<url><loc>{SITE_URL}{p}</loc><lastmod>{day}</lastmod>{alt}</url>')
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + '\n'.join(rows) + '\n</urlset>\n')

def root_page():
    """/ : picks the visitor's language (browser setting, else English) and forwards old #/lang/slug links of the one-file version.
    Without script, and for search engines, it is a plain list of languages."""
    known = {l: [s for s, _ in PAGES[l]] for l in LANGS}
    items = ''.join(f'<li><a href="{url(l, "home")}" lang="{l}" hreflang="{HREFLANG.get(l, l)}">{LANG_NAME[l]}</a></li>' for l in LANGS)
    alts = [(HREFLANG.get(l, l), url(l, 'home')) for l in LANGS] + [('x-default', '/')]
    return f'''<!doctype html>
<html lang="en" data-concept="b-poster">
<head>
{head('en', '/', 'Pro Extinction | ' + T['en']['sub'], SEO['en']['home'], alts)}
<script>(function(){{var k={json.dumps(known, separators=(',', ':'))},h=location.hash.match(/^#\/([a-z]+)\/([^\/?#]+)/),l;
if(h&&k[h[1]]){{location.replace(k[h[1]].indexOf(h[2])>0?'/'+h[1]+'/'+h[2]:'/'+h[1]+'/');return}}
var w=navigator.languages||[navigator.language||'en'];for(var i=0;i<w.length;i++){{l=String(w[i]).toLowerCase().split('-')[0];if(l==='fil')l='tl';if(k[l]){{location.replace('/'+l+'/');return}}}}
location.replace('/en/')}})()</script>
</head>
<body class="page">
<main id="main" class="shell"><article class="doc"><header class="doc-head"><h1 class="wordmark">PRO EXTINCTION</h1><p class="lede">{T['en']['tagline']}</p><hr class="slash"></header>
<ul class="lang-list">{items}</ul></article></main>
</body>
</html>
'''

def not_found():
    items = ''.join(f'<li><a href="{url(l, "home")}" lang="{l}">{LANG_NAME[l]}</a></li>' for l in LANGS)
    return f'''<!doctype html>
<html lang="en" data-concept="b-poster">
<head>
{head('en', '/404', 'Page not found | Pro Extinction', 'This page does not exist.', index=False)}
</head>
<body class="page">
<main id="main" class="shell nf">
<a class="nf-home" href="{url('en', 'home')}">{HERO_LOGO}<span class="wordmark">PRO EXTINCTION</span></a>
<p class="mono kicker">404 · Page not found</p>
<h1>This page does not exist</h1>
<p class="lede">Non-existence is not a problem. Suffering is. Read why we want to end it.</p>
<p class="hero-cta"><a class="btn primary" href="{url('en', 'manifesto')}">Read the manifesto</a><a class="btn" href="{url('en', 'home')}">Start page</a></p>
<hr class="slash">
<p class="mono kicker">Choose your language</p>
<ul class="lang-list">{items}</ul>
<p class="hero-tag">{T['en']['tagline']}</p>
</main>
</body>
</html>
'''

# Cloudflare Web Analytics (owners' decision, October 2026): cookieless visitor counts. Cloudflare adds its script to every page;
# the CSP allows only that script and the address it reports to. Nothing else may load from other servers (see the privacy policy).
ANALYTICS = ('https://static.cloudflareinsights.com', 'https://cloudflareinsights.com')

HEADERS = {
    'X-Content-Type-Options': 'nosniff', 'Referrer-Policy': 'strict-origin-when-cross-origin', 'X-Frame-Options': 'DENY', 'Cross-Origin-Opener-Policy': 'same-origin',
    'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
    'Strict-Transport-Security': 'max-age=31536000',   # HTTPS only; no includeSubDomains, so other subdomains stay untouched
    'Content-Security-Policy': f"default-src 'self'; script-src 'self' 'unsafe-inline' {ANALYTICS[0]}; style-src 'self' 'unsafe-inline'; font-src 'self'; "
                               f"img-src 'self' data:; connect-src 'self' {ANALYTICS[1]}; frame-ancestors 'none'; base-uri 'none'; object-src 'none'; form-action 'none'"}

def hosting():
    """Cloudflare reads site/_headers and site/_redirects (neither is served as a page). Both follow INDEXABLE."""
    hdr = ({} if INDEXABLE else {'X-Robots-Tag': 'noindex, nofollow'}) | HEADERS
    (OUT / '_headers').write_text('/*\n' + ''.join(f'  {k}: {v}\n' for k, v in hdr.items())
                                  + '\n/fonts/*\n  Cache-Control: public, max-age=31536000, immutable\n', encoding='utf-8')
    # old addresses: the English Google Site (/manifesto, /home ...)
    old = ['/home /en/ 301'] + [f'/{s} /en/{s} 301' for s, _ in PAGES['en'] if s != 'home']
    (OUT / '_redirects').write_text('\n'.join(old) + '\n', encoding='utf-8')
    # Vercel only shows previews until the move to Cloudflare; never indexed
    conf = {'$schema': 'https://openapi.vercel.sh/vercel.json', 'framework': None, 'buildCommand': None, 'installCommand': None,
            'outputDirectory': 'site', 'cleanUrls': True,
            'headers': [{'source': '/(.*)', 'headers': [{'key': 'X-Robots-Tag', 'value': 'noindex, nofollow'}]}]}
    (ROOT / 'vercel.json').write_text(json.dumps(conf, indent=2) + '\n', encoding='utf-8')

if __name__ == '__main__': build()
