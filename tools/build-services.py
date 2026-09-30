#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build the service pages (three services, two languages) and fold them into
sitemap.xml.

Joy Taxi does more than point-to-point rides, and until now the site said none of
it: full-day tours across Lebanon, school and student runs, and shared commutes.
Each is a different customer searching different words, so each gets its own page
rather than a paragraph on the homepage.

    python3 tools/build-services.py      # after build-areas.py

Shares area.css and the page shape with the area pages; build-areas.py owns both.
"""
import io, os, sys, importlib.util

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location('ba', os.path.join(ROOT, 'tools', 'build-areas.py'))
ba = importlib.util.module_from_spec(spec); spec.loader.exec_module(ba)

SITE, WA, TEL1, TEL2, DSP1, DSP2 = ba.SITE, ba.WA, ba.TEL1, ba.TEL2, ba.DSP1, ba.DSP2
esc, jesc, urlenc = ba.esc, ba.jesc, ba.urlenc

SERVICES = [
 dict(slug='tours', schema='TouristTrip',
   en=dict(
     name='Day tours',
     title='Lebanon Day Tours by Car — Joy Taxi | From $120 a day',
     h1='A car and a driver,<br>for the whole day.',
     desc='Full-day tours of Lebanon with your own driver, from $120 a day. Baalbek, Jeita Grotto, Byblos, Faraya, Harissa. Up to 7 seats. WhatsApp 71 056 677.',
     lede='Baalbek in the morning, Jeita after lunch, back before dark — with the same driver and the same car all day. From $120 a day, up to seven seats.',
     kicker='Long trips and full-day tours',
     wa='I would like a full day tour',
     rows=[('Baalbek','the Roman temples, about two hours out'),
           ('Jeita Grotto','and Harissa on the same run'),
           ('Byblos · Jbeil','old souk, the port, the castle'),
           ('Faraya','and the snow, in season'),
           ('Harissa','the cable car and the bay'),
           ('The Cedars','and the north, on a long day'),
           ('Anywhere else','tell us and we will say whether the day works')],
     rows_k='Where people go', rows_h='A day, not a drop-off.',
     body='A tour day is not a taxi ride with a bigger bill on it. You keep the car and the driver from the time you are picked up until you are dropped home, you decide the order, and you can change your mind at lunch. The driver waits while you are inside — that is the point of it.\n\nThe day starts at $120 and depends on how far you go, not on how long you take. Baalbek and the Bekaa is a longer day than Jbeil and the coast. You are told the figure for your specific plan before the day is booked, and it does not change afterwards.\n\nUp to seven seats, so a family or a small group travels in one car rather than two. Tell us how many people and we will say which car comes.',
     faqs=[('How much is a full day tour in Lebanon?',
            'Days start at $120. What yours costs depends on the distance the plan covers rather than the hours — Baalbek and the Bekaa is a longer day than Byblos and the coast. Send the places you want to see and you get the figure before you book, and it does not change on the day.'),
           ('Can we choose where we go?',
            'Yes. Most people name two or three places and let the driver order them sensibly around traffic and opening times. If you would rather have it planned for you, say what interests you — ruins, mountains, sea, food — and you will get a suggested day back.'),
           ('How many people fit?',
            'Up to seven. Tell us the number when you book and the right car comes; a family of five and a group of seven are not the same vehicle.'),
           ('Does the driver wait while we visit?',
            'Yes, all day. The car and the driver are yours from pickup to drop-off, including waiting at each stop. There is no meter running and no second fare for the way back.')]),
   ar=dict(
     name='رحلات يومية',
     title='رحلات يوم بلبنان — جوي تاكسي | من ١٢٠$ باليوم',
     h1='سيارة وسوّاق،<br>طول النهار.',
     desc='رحلات يوم كامل بلبنان مع سوّاقك الخاص، من ١٢٠$ باليوم. بعلبك، مغارة جعيتا، جبيل، فقرا، حريصا. لغاية ٧ ركاب. واتساب 71 056 677.',
     lede='بعلبك الصبح، جعيتا بعد الضهر، ورجعة قبل ما يعتم — بنفس السيارة ونفس السوّاق. من ١٢٠$ باليوم، لغاية ٧ ركاب.',
     kicker='رحلات طويلة ويوم كامل',
     wa='بدي رحلة يوم كامل',
     rows=[('بعلبك','القلعة الرومانية، ساعتين تقريباً'),
           ('مغارة جعيتا','وحريصا بنفس النهار'),
           ('جبيل','السوق القديم، المرفأ، القلعة'),
           ('فقرا','والتلج، بموسمه'),
           ('حريصا','التلفريك والخليج'),
           ('الأرز','والشمال، بيوم طويل'),
           ('أي مكان تاني','قلّنا ومنقلك إذا النهار بيمشي')],
     rows_k='على وين بيروحوا', rows_h='نهار كامل، مش توصيلة.',
     body='يوم الرحلة ما هو توصيلة بفاتورة أكبر. السيارة والسوّاق إلك من وقت ما نلقطك لوقت ما نرجّعك، وإنت بتقرّر الترتيب، وفيك تغيّر رأيك عالغدا. السوّاق بينطرك وقت إنت جوّا — هيدا كل الموضوع.\n\nالنهار بيبلّش من ١٢٠$ وبيعتمد عالمسافة مش عالوقت. بعلبك والبقاع نهار أطول من جبيل والساحل. بتعرف الرقم لخطتك قبل ما تحجز، وما بيتغيّر بعدين.\n\nلغاية ٧ ركاب، فالعيلة أو المجموعة بتروح بسيارة وحدة مش تنتين. قلّنا كم واحد ومنقلك أيّا سيارة بتيجي.',
     faqs=[('قدّيش رحلة اليوم الكامل بلبنان؟',
            'النهار بيبلّش من ١٢٠$. قدّيش بيكلّف بيعتمد عالمسافة مش عالساعات — بعلبك والبقاع أطول من جبيل والساحل. ابعت الأماكن يلي بدك تشوفها وبيجيك الرقم قبل ما تحجز، وما بيتغيّر بالنهار.'),
           ('فينا نختار على وين نروح؟',
            'إيه. أكتر الناس بتقول محلّين أو تلاتة وبتخلّي السوّاق يرتّبهن عالزحمة وأوقات الفتح. وإذا بتفضّل نخطّطلك، قلّنا شو بيعجبك — آثار، جبل، بحر، أكل — وبيجيك اقتراح للنهار.'),
           ('كم شخص بيركب؟',
            'لغاية ٧. قلّنا العدد وقت تحجز وبتيجي السيارة المناسبة؛ عيلة من خمسة ومجموعة من سبعة ما هنّن نفس السيارة.'),
           ('السوّاق بينطرنا وقت نزور؟',
            'إيه، طول النهار. السيارة والسوّاق إلك من اللقطة للرجعة، والانتظار عند كل محل محسوب. ما في عدّاد شغّال ولا أجرة تانية للرجعة.')])),

 dict(slug='school-transport', schema='Service',
   en=dict(
     name='School and student runs',
     title='School & Student Transport — Joy Taxi | Beirut & Metn',
     h1='Getting them there,<br>and back.',
     desc='School and university transport across Beirut, Metn North and Jounieh. Up to 7 seats, the same driver each day, live location on WhatsApp. Call 71 056 677.',
     lede='A regular run to school or university, with the same driver each day and their live location on WhatsApp while the car is moving.',
     kicker='For parents',
     wa='I need regular school transport',
     rows=[('The same driver','not a different stranger each morning'),
           ('Live location','shared on WhatsApp while the car is moving'),
           ('Up to 7 seats','so friends or siblings share one car'),
           ('A set time','the same pickup every day, agreed once'),
           ('Metn North','Antelias, Dbayeh, Jal el Dib, Bsalim'),
           ('Jounieh','Kaslik, Zouk, Sarba'),
           ('Beirut','and the universities')],
     rows_k='What a regular run means', rows_h='The bit parents actually worry about.',
     body='The thing that makes a school run work is that it is the same person every day. Your child learns who is picking them up, you learn the car, and nobody is deciding at 7am whether to get in with a stranger.\n\nWhile the car is moving, the driver shares live location on WhatsApp. It is not an app and there is nothing to install — it is the same live location anybody can send in a chat, and it stops when the trip does. You watch the car approach and you know when they have arrived.\n\nUp to seven seats, which is usually cheaper per family once two or three children from the same street travel together. Tell us the school, the time and the pickup points and you get one figure for the week.',
     faqs=[('Is it the same driver every day?',
            'Yes, that is the point of a regular run. You meet the driver and the car before the first day, and the arrangement stays the same unless you change it.'),
           ('How do I know where they are?',
            'The driver shares live location on WhatsApp while the trip is running. There is no app and nothing to install — it is the ordinary WhatsApp live location, and it ends when the trip does.'),
           ('Can several children share the car?',
            'Yes, up to seven seats. Children from the same street or school sharing one car is the usual arrangement and it costs each family less than separate runs.'),
           ('How do I pay for a regular run?',
            'Cash to the driver, in US dollars or Lebanese lira. For a weekly or monthly arrangement the figure is agreed up front so there is nothing to work out each morning.')]),
   ar=dict(
     name='نقل الطلاب',
     title='نقل طلاب ومدارس — جوي تاكسي | بيروت، المتن، جونية',
     h1='نوصّلهن ونرجّعهن.',
     desc='نقل مدارس وجامعات ببيروت، المتن الشمالي وجونية. لغاية ٧ ركاب، نفس السوّاق كل يوم، موقع مباشر عالواتساب. اتصل 71 056 677.',
     lede='توصيلة يومية عالمدرسة أو الجامعة، بنفس السوّاق كل يوم وموقعو مباشر عالواتساب وقت السيارة ماشية.',
     kicker='للأهل',
     wa='بدي توصيلة مدرسة يومية',
     rows=[('نفس السوّاق','مش واحد غريب كل صبح'),
           ('موقع مباشر','عالواتساب وقت السيارة ماشية'),
           ('لغاية ٧ ركاب','رفاق أو إخوة بسيارة وحدة'),
           ('وقت ثابت','نفس الساعة كل يوم، بيتفق عليها مرّة'),
           ('المتن الشمالي','أنطلياس، ضبية، جل الديب، بصاليم'),
           ('جونية','الكسليك، الذوق، صربا'),
           ('بيروت','والجامعات')],
     rows_k='شو بتعني توصيلة ثابتة', rows_h='الشي يلي بيهمّ الأهل.',
     body='يلي بيخلّي توصيلة المدرسة تمشي هو إنو نفس الشخص كل يوم. ولدك بيعرف مين عم يلقطو، وإنت بتعرف السيارة، وما حدا عم يقرّر الساعة ٧ إذا بيطلع مع غريب.\n\nوقت السيارة ماشية، السوّاق بيبعت موقعو المباشر عالواتساب. ما في تطبيق ولا شي تنزّلو — هي نفس خاصية الموقع المباشر يلي بيبعتا أي حدا بالشات، وبتوقف وقت تخلص الرحلة.\n\nلغاية ٧ ركاب، وعادة بيطلع أرخص للعيلة لمّا تلاتة ولاد من نفس الشارع يروحوا سوا. قلّنا المدرسة والوقت ونقاط اللقط وبيجيك رقم واحد للأسبوع.',
     faqs=[('نفس السوّاق كل يوم؟',
            'إيه، هيدا كل فكرة التوصيلة الثابتة. بتتعرّف عالسوّاق وعالسيارة قبل أول يوم، والترتيب بيضل نفسو إلا إذا غيّرتو.'),
           ('كيف بعرف وين صاروا؟',
            'السوّاق بيبعت موقعو المباشر عالواتساب طول الرحلة. ما في تطبيق ولا شي تنزّلو — هي خاصية الموقع المباشر العادية، وبتوقف وقت تخلص الرحلة.'),
           ('فينا كم ولد يركبوا سوا؟',
            'إيه، لغاية ٧ ركاب. ولاد من نفس الشارع أو المدرسة بسيارة وحدة هي الترتيب العادي، وبيكلّف كل عيلة أقل من توصيلات منفصلة.'),
           ('كيف بدفع عالتوصيلة الثابتة؟',
            'كاش للسوّاق، بالدولار أو بالليرة. للترتيب الأسبوعي أو الشهري بيتفق عالرقم من البداية فما بيبقى شي تحسبو كل صبح.')])),

 dict(slug='shared-rides', schema='Service',
   en=dict(
     name='Shared rides',
     title='Shared Rides to Work & University — Joy Taxi',
     h1='Share the car,<br>split the fare.',
     desc='Daily shared rides to work and university across Beirut, Metn North and Jounieh. Two or more split one fare. Up to 7 seats. WhatsApp 71 056 677.',
     lede='The same run every morning, with a colleague or a classmate, and one fare between you instead of two.',
     kicker='Daily commute',
     wa='I want to arrange a shared daily ride',
     rows=[('One fare, split','between two people or seven'),
           ('The same time daily','agreed once, not rebooked each morning'),
           ('Up to 7 seats','colleagues, classmates, neighbours'),
           ('To work','offices across Beirut and the Metn'),
           ('To university','and back at the end of the day'),
           ('The same driver','who learns the route and the traffic')],
     rows_k='How sharing works', rows_h='Cheaper than going alone.',
     body='Two people going the same way at the same time every morning are paying twice for one journey. Share the car and there is one fare between you, agreed at the start and split however you like.\n\nIt works best as a standing arrangement: the same pickup points, the same time, the same driver. Nobody books anything each morning and nobody waits. Up to seven seats, so a group from one office or one campus travels together.\n\nTell us the pickups, the destination and the time, and you get one figure for the run. What each person pays is then simple arithmetic you do between yourselves.',
     faqs=[('How does splitting the fare work?',
            'You are quoted one figure for the journey, not a price per person. How you divide it between you is up to you — most groups simply split it evenly, and the driver is paid once at the end.'),
           ('Do we need to book every day?',
            'No. A standing arrangement is agreed once — pickup points, time, destination — and then it simply runs. Message us when something changes.'),
           ('How many can share one car?',
            'Up to seven. Colleagues from one office, students from one campus, or neighbours from one street are the usual groups.'),
           ('What if one person cannot travel one day?',
            'Tell the driver and the run continues for everyone else. The fare is for the journey, so how the remaining passengers divide it is between you.')]),
   ar=dict(
     name='رحلات مشتركة',
     title='رحلات مشتركة عالعمل والجامعة — جوي تاكسي',
     h1='شارك السيارة،<br>واقتسم التسعيرة.',
     desc='رحلات يومية مشتركة عالعمل والجامعة ببيروت، المتن وجونية. تنين أو أكتر بيقتسموا تسعيرة وحدة. لغاية ٧ ركاب. واتساب 71 056 677.',
     lede='نفس الطريق كل صبح، مع زميل أو رفيق، وتسعيرة وحدة بيناتكن بدل تنتين.',
     kicker='الطريق اليومي',
     wa='بدي رحلة يومية مشتركة',
     rows=[('تسعيرة وحدة مقسومة','بين تنين أو سبعة'),
           ('نفس الوقت يومياً','بيتفق عليه مرّة'),
           ('لغاية ٧ ركاب','زملاء، رفاق، جيران'),
           ('عالعمل','مكاتب ببيروت والمتن'),
           ('عالجامعة','ورجعة بآخر النهار'),
           ('نفس السوّاق','بيحفظ الطريق والزحمة')],
     rows_k='كيف بتمشي', rows_h='أرخص من ما تروح لحالك.',
     body='تنين رايحين عنفس المكان بنفس الوقت كل صبح عم يدفعوا مرتين لنفس الطريق. شاركوا السيارة وبتصير تسعيرة وحدة بيناتكن، متفق عليها من البداية ومقسومة متل ما بدكن.\n\nبتمشي أحسن كترتيب ثابت: نفس نقاط اللقط، نفس الوقت، نفس السوّاق. ما حدا بيحجز كل صبح وما حدا بينطر. لغاية ٧ ركاب، فمجموعة من مكتب واحد أو جامعة وحدة بتروح سوا.\n\nقلّنا نقاط اللقط والوجهة والوقت، وبيجيك رقم واحد للطريق. وقدّيش بيدفع كل واحد بيصير حساب بسيط بيناتكن.',
     faqs=[('كيف بتنقسم التسعيرة؟',
            'بيجيك رقم واحد للطريق، مش سعر لكل شخص. كيف بتقسموه بيناتكن متروك إلكن — أكتر المجموعات بتقسمو بالتساوي، والسوّاق بياخد مرّة وحدة بالآخر.'),
           ('لازم نحجز كل يوم؟',
            'لأ. الترتيب بيتفق عليه مرّة — نقاط اللقط، الوقت، الوجهة — وبعدين بيمشي لحالو. ابعتلنا وقت بيتغيّر شي.'),
           ('كم واحد بيقدر يشارك؟',
            'لغاية ٧. زملاء من مكتب واحد، طلاب من جامعة وحدة، أو جيران من نفس الشارع.'),
           ('شو إذا واحد ما فيه يروح يوم؟',
            'قلّول للسوّاق والطريق بتكمّل للباقيين. التسعيرة للطريق، فكيف بيقسموها الباقيين متروك إلكن.')])),
]


L = {
 'en': dict(lang='en', dir='ltr', oglocale='en_US', up='../', base=SITE + '/',
   skip='Skip to booking', nav=[('Book', '#book'), ('Areas', '#areas'),
        ('How it works', '#how'), ('Questions', '#faq')],
   call='Call', home='Joy Taxi', langlink='عربي', langcode='ar',
   services='Services', faq_k='Before you book', faq_h='Straight answers.',
   others_k='Also from Joy Taxi', others_h='The other things we do.',
   areas_link='All areas we cover',
   close_h='Save the number<br>before you need it.',
   close_p='One tap now is one less problem later.',
   wa='WhatsApp', callnow='Call now', open247='Open 24/7',
   foot_p='Taxi and private hire along the coast road. Twenty-four hours, every day of the year.',
   foot_call='Call or message', foot_services='Services',
   trust=['24 hours, every day', 'Up to 7 seats', 'Cash, dollars or lira'],
   vcard='Save to contacts', crumb_home='Joy Taxi'),
 'ar': dict(lang='ar', dir='rtl', oglocale='ar_LB', up='../../', base=SITE + '/ar/',
   skip='روح عالحجز', nav=[('احجز', '#book'), ('المناطق', '#areas'),
        ('كيف بتمشي', '#how'), ('أسئلة', '#faq')],
   call='اتصل', home='جوي تاكسي', langlink='EN', langcode='en',
   services='الخدمات', faq_k='قبل ما تحجز', faq_h='جواب مباشر.',
   others_k='كمان من جوي تاكسي', others_h='الأشيا التانية يلي منعملا.',
   areas_link='كل المناطق يلي منغطّيا',
   close_h='خبّي الرقم<br>قبل ما تحتاجو.',
   close_p='ضغطة هلّق بتوفّر عليك مشكلة بعدين.',
   wa='واتساب', callnow='اتصل هلّق', open247='فاتحين ٢٤/٧',
   foot_p='تاكسي وتوصيلات خاصة على طريق الساحل. ٢٤ ساعة، كل يوم بالسنة.',
   foot_call='اتصل أو ابعت', foot_services='الخدمات',
   trust=['٢٤ ساعة، كل يوم', 'لغاية ٧ ركاب', 'كاش، دولار أو ليرة'],
   vcard='خبّي بالأسماء', crumb_home='جوي تاكسي'),
}


def page(svc, lc):
    w, d = L[lc], svc[lc]
    slug, up, hup = svc['slug'], w['up'], '../'
    canon = (SITE + '/' + slug + '/') if lc == 'en' else (SITE + '/ar/' + slug + '/')
    en_url, ar_url = SITE + '/' + slug + '/', SITE + '/ar/' + slug + '/'
    wa_href = 'https://wa.me/%s?text=%s' % (WA, urlenc(d['wa']))
    others = [s for s in SERVICES if s['slug'] != slug]
    H = []; A = H.append
    A('<!DOCTYPE html>'); A('<html lang="%s" dir="%s">' % (w['lang'], w['dir'])); A('<head>')
    A('<meta charset="utf-8">')
    A('<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">')
    A('<title>%s</title>' % esc(d['title']))
    A('<meta name="description" content="%s">' % esc(d['desc']))
    A('<meta name="theme-color" content="#08080A">')
    A('<script>'); A(ba.THEME_BOOT); A('</script>')
    A('<link rel="canonical" href="%s">' % canon)
    A('<link rel="alternate" hreflang="en" href="%s">' % en_url)
    A('<link rel="alternate" hreflang="ar" href="%s">' % ar_url)
    A('<link rel="alternate" hreflang="x-default" href="%s">' % en_url)
    A('<link rel="icon" href="%sfavicon.svg" type="image/svg+xml">' % up)
    A('<link rel="apple-touch-icon" href="%sicon-180.png">' % up)
    A('<meta property="og:type" content="website">')
    A('<meta property="og:site_name" content="Joy Taxi">')
    A('<meta property="og:locale" content="%s">' % w['oglocale'])
    A('<meta property="og:url" content="%s">' % canon)
    A('<meta property="og:title" content="%s">' % esc(d['title'].split(' — ')[0]))
    A('<meta property="og:description" content="%s">' % esc(d['desc']))
    A('<meta property="og:image" content="%s/og.png">' % SITE)
    A('<meta property="og:image:width" content="1200">')
    A('<meta property="og:image:height" content="630">')
    A('<meta name="twitter:card" content="summary_large_image">')
    A('<link rel="stylesheet" href="%sarea.css">' % up)
    A('<noscript><style>.rv{opacity:1;transform:none}</style></noscript>')
    A('</head>'); A('<body>')
    A('<a class="skip" href="#book">%s</a>' % esc(w['skip']))
    A('<header id="top">'); A('  <div class="wrap bar">')
    A('    <a class="mark" href="%s" aria-label="%s">' % (hup, esc(w['home'])))
    A('      ' + ba.MARK); A('    </a>')
    A('    <nav aria-label="Main">')
    for lbl, href in w['nav']:
        A('      <a href="%s%s">%s</a>' % (hup, href, esc(lbl)))
    A('    </nav>')
    A('    <div class="bar-end">')
    A('      <button type="button" class="theme" id="theme" aria-label="%s">'
      % ('Day or night' if lc == 'en' else 'نهار أو ليل'))
    A('        ' + ba.THEME_SVGS); A('      </button>')
    A('      <a class="lang" href="%s" hreflang="%s" lang="%s">%s</a>'
      % ((('../ar/%s/' % slug) if lc == 'en' else ('../../%s/' % slug)),
         w['langcode'], w['langcode'], esc(w['langlink'])))
    A('      <a class="btn btn-amber" href="tel:%s" style="padding:11px 18px;font-size:.88rem">' % TEL1)
    A('        ' + ba.ICO_CALL); A('        %s' % esc(w['call'])); A('      </a>')
    A('    </div>'); A('  </div>'); A('</header>'); A('<main>')
    A('<div class="wrap">')
    A('  <nav class="crumb" aria-label="%s">' % ('Breadcrumb' if lc == 'en' else 'مسار'))
    A('    <ol>')
    A('      <li><a href="%s">%s</a></li>' % (hup, esc(w['crumb_home'])))
    A('      <li><span aria-current="page">%s</span></li>' % esc(d['name']))
    A('    </ol>'); A('  </nav>'); A('</div>')
    A('<section class="hero" id="book" style="padding-top:clamp(12px,2vw,20px)">')
    A('  <div class="wrap">')
    A('    <p class="kicker">%s</p>' % esc(d['kicker']))
    A('    <h1 class="h1-area" style="margin:14px 0 0">%s</h1>' % d['h1'])
    A('    <p class="lede">%s</p>' % esc(d['lede']))
    A('    <div class="cta-btns cta-start">')
    A('      <a class="btn btn-wa btn-lg" href="%s" data-ev="whatsapp">' % esc(wa_href))
    A('        ' + ba.ICO_WA); A('        %s' % esc(w['wa'])); A('      </a>')
    A('      <a class="btn btn-ghost btn-lg" href="tel:%s" data-ev="call">%s</a>' % (TEL1, DSP1))
    A('      <a class="btn btn-ghost btn-lg" href="tel:%s" data-ev="call">%s</a>' % (TEL2, DSP2))
    A('    </div>')
    A('    <div class="trust">')
    for t in w['trust']:
        A('      <span>%s</span>' % esc(t))
    A('    </div>'); A('  </div>'); A('</section>')
    A('<section>'); A('  <div class="wrap">')
    A('    <div class="head rv">')
    A('      <p class="kicker">%s</p>' % esc(d['rows_k']))
    A('      <h2 class="h2">%s</h2>' % esc(d['rows_h']))
    A('    </div>')
    A('    <ul class="hoods rv">')
    for n, note in d['rows']:
        A('      <li>%s <span>%s</span></li>' % (esc(n), esc(note)))
    A('    </ul>')
    A('    <div class="prose rv" style="margin-top:28px">')
    for para in d['body'].split('\n\n'):
        A('      <p>%s</p>' % esc(para))
    A('    </div>'); A('  </div>'); A('</section>')
    A('<section id="faq" style="background:var(--ink-2);border-block:1px solid var(--line)">')
    A('  <div class="wrap">')
    A('    <div class="head rv">')
    A('      <p class="kicker">%s</p>' % esc(w['faq_k']))
    A('      <h2 class="h2">%s</h2>' % esc(w['faq_h']))
    A('    </div>')
    A('    <div class="faq rv">')
    for q, a in d['faqs']:
        A('      <details>'); A('        <summary>%s</summary>' % esc(q))
        A('        <p>%s</p>' % esc(a)); A('      </details>')
    A('    </div>'); A('  </div>'); A('</section>')
    A('<section id="areas">'); A('  <div class="wrap">')
    A('    <div class="head rv">')
    A('      <p class="kicker">%s</p>' % esc(w['others_k']))
    A('      <h2 class="h2">%s</h2>' % esc(w['others_h']))
    A('    </div>')
    A('    <ul class="arealinks rv">')
    for o in others:
        A('      <li><a href="../%s/">%s</a></li>' % (o['slug'], esc(o[lc]['name'])))
    A('      <li><a href="%s#areas">%s</a></li>' % (hup, esc(w['areas_link'])))
    A('    </ul>'); A('  </div>'); A('</section>')
    A('<section style="padding-top:0">')
    A('  <div class="wrap" style="text-align:center">')
    A('    <h2 class="h2">%s</h2>' % w['close_h'])
    A('    <p class="lede" style="margin-inline:auto">%s</p>' % esc(w['close_p']))
    A('    <div class="cta-btns">')
    A('      <a class="btn btn-wa btn-lg" href="%s" data-ev="whatsapp">%s</a>' % (esc(wa_href), esc(w['wa'])))
    A('      <a class="btn btn-amber btn-lg" href="tel:%s" data-ev="call">%s</a>' % (TEL1, esc(w['callnow'])))
    A('    </div>')
    A('    <a class="vcard" href="%sjoy-taxi.vcf" download>%s</a>' % (up, esc(w['vcard'])))
    A('  </div>'); A('</section>'); A('</main>')
    A('<footer>'); A('  <div class="wrap">'); A('    <div class="fgrid">')
    A('      <div>')
    A('        <a class="mark" href="%s" style="margin-bottom:16px" aria-label="%s">' % (hup, esc(w['home'])))
    A('          <span class="lamp" aria-hidden="true"></span><b>JOY TAXI</b>')
    A('        </a>')
    A('        <p style="color:var(--muted);margin:0;max-width:34ch;font-size:.93rem">%s</p>' % esc(w['foot_p']))
    A('      </div>')
    A('      <div>'); A('        <h4>%s</h4>' % esc(w['foot_call'])); A('        <ul>')
    A('          <li><a class="tel" href="tel:%s">%s</a></li>' % (TEL1, DSP1))
    A('          <li><a class="tel" href="tel:%s">%s</a></li>' % (TEL2, DSP2))
    A('          <li><a href="%s">%s</a></li>' % (esc(wa_href), esc(w['wa'])))
    A('        </ul>'); A('      </div>')
    A('      <div>'); A('        <h4>%s</h4>' % esc(w['foot_services'])); A('        <ul>')
    for s2 in SERVICES:
        A('          <li><a href="../%s/">%s</a></li>' % (s2['slug'], esc(s2[lc]['name'])))
    A('        </ul>'); A('      </div>')
    A('    </div>'); A('    <div class="legal">')
    A('      <span>&copy; <span id="yr">2026</span> %s &middot; %s</span>'
      % (esc(w['home']), 'Lebanon' if lc == 'en' else 'لبنان'))
    A('      <span><a href="%s" hreflang="%s" lang="%s">%s</a> &middot; %s</span>'
      % ((('../ar/%s/' % slug) if lc == 'en' else ('../../%s/' % slug)),
         w['langcode'], w['langcode'], esc(w['langlink']), esc(w['open247'])))
    A('    </div>'); A('  </div>'); A('</footer>')
    A('<div class="dock" role="group" aria-label="%s">'
      % ('Quick contact' if lc == 'en' else 'تواصل سريع'))
    A('  <a class="btn btn-wa" href="%s" data-ev="whatsapp">%s</a>' % (esc(wa_href), esc(w['wa'])))
    A('  <a class="btn btn-amber" href="tel:%s" data-ev="call">%s</a>' % (TEL1, esc(w['callnow'])))
    A('</div>')
    faq_items = ',\n      '.join(
        '{"@type":"Question","name":"%s","acceptedAnswer":{"@type":"Answer","text":"%s"}}'
        % (jesc(q), jesc(a)) for q, a in d['faqs'])
    A('<script type="application/ld+json">'); A('{')
    A('  "@context":"https://schema.org",'); A('  "@graph":[')
    A('    {'); A('      "@type":"Service",'); A('      "@id":"%s#service",' % canon)
    A('      "name":"%s",' % jesc(d['title'].split(' — ')[0]))
    A('      "serviceType":"%s",' % jesc(d['name']))
    A('      "url":"%s",' % canon)
    A('      "description":"%s",' % jesc(d['desc']))
    A('      "provider":{"@type":"TaxiService","@id":"%s/#business","name":"Joy Taxi",' % SITE)
    A('        "url":"%s/","telephone":["%s","%s"]},' % (SITE, TEL1, TEL2))
    A('      "areaServed":{"@type":"Country","name":"Lebanon"},')
    A('      "availableLanguage":["ar","en"],')
    A('      "availableChannel":{"@type":"ServiceChannel",')
    A('        "servicePhone":{"@type":"ContactPoint","telephone":"%s"},' % TEL1)
    A('        "serviceUrl":"%s"}' % canon)
    A('    },')
    A('    {'); A('      "@type":"FAQPage",'); A('      "@id":"%s#faq",' % canon)
    A('      "mainEntity":['); A('      %s' % faq_items); A('      ]'); A('    },')
    A('    {'); A('      "@type":"BreadcrumbList",'); A('      "@id":"%s#breadcrumb",' % canon)
    A('      "itemListElement":[')
    A('        {"@type":"ListItem","position":1,"name":"%s","item":"%s"},'
      % (jesc(w['crumb_home']), w['base']))
    A('        {"@type":"ListItem","position":2,"name":"%s","item":"%s"}' % (jesc(d['name']), canon))
    A('      ]'); A('    }'); A('  ]'); A('}'); A('</script>')
    A('<script>'); A(ba.TAIL_JS); A('</script>'); A('</body>'); A('</html>')
    return '\n'.join(H) + '\n'



def build_sitemap():
    """Full sitemap: both homepages, twelve area pages, six service pages."""
    LASTMOD = os.environ.get('LASTMOD', '2026-09-30')
    def block(loc, en, ar, pri):
        return ('  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n'
                '    <changefreq>monthly</changefreq>\n    <priority>%s</priority>\n'
                '    <xhtml:link rel="alternate" hreflang="en" href="%s"/>\n'
                '    <xhtml:link rel="alternate" hreflang="ar" href="%s"/>\n  </url>'
                % (loc, LASTMOD, pri, en, ar))
    rows = [block(SITE + '/', SITE + '/', SITE + '/ar/', '1.0'),
            block(SITE + '/ar/', SITE + '/', SITE + '/ar/', '1.0')]
    for a in ba.AREAS:
        en, ar = SITE + '/' + a['slug'] + '/', SITE + '/ar/' + a['slug'] + '/'
        rows += [block(en, en, ar, '0.8'), block(ar, en, ar, '0.8')]
    for s in SERVICES:
        en, ar = SITE + '/' + s['slug'] + '/', SITE + '/ar/' + s['slug'] + '/'
        rows += [block(en, en, ar, '0.9'), block(ar, en, ar, '0.9')]
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
           '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
           + '\n'.join(rows) + '\n</urlset>\n')
    io.open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8').write(xml)
    return len(rows)

if __name__ == '__main__':
    for s in SERVICES:
        for lc in ('en', 'ar'):
            dd = os.path.join(ROOT, s['slug']) if lc == 'en' else os.path.join(ROOT, 'ar', s['slug'])
            os.path.isdir(dd) or os.makedirs(dd)
            fp = os.path.join(dd, 'index.html')
            io.open(fp, 'w', encoding='utf-8').write(page(s, lc))
            print('  %-34s %6d bytes' % (os.path.relpath(fp, ROOT), os.path.getsize(fp)))
    print('sitemap.xml     %d urls' % build_sitemap())
