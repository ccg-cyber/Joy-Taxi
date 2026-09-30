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

Shares area.css and the page chrome (header, hero, closing, footer) with the area
pages; build-areas.py owns both.
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
 'en': dict(up='../', base=SITE + '/', crumb_home='Joy Taxi',
   faq_k='Before you book', faq_h='Straight answers.',
   others_k='Also from Joy Taxi', others_h='The other things we do.',
   areas_t='The coast road', areas_d='Beirut, the airport, Metn, Bsalim, Jounieh and Jbeil — every area we cover.',
   areas_k='Areas', explore='Explore',
   trust=['24 hours, every day', 'Up to 7 seats', 'Cash, dollars or lira']),
 'ar': dict(up='../../', base=SITE + '/ar/', crumb_home='جوي تاكسي',
   faq_k='قبل ما تحجز', faq_h='جواب مباشر.',
   others_k='كمان من جوي تاكسي', others_h='الأشيا التانية يلي منعملا.',
   areas_t='طريق الساحل', areas_d='بيروت، المطار، المتن، بصاليم، جونية وجبيل — كل المناطق يلي منغطّيا.',
   areas_k='المناطق', explore='اكتشف',
   trust=['٢٤ ساعة، كل يوم', 'لغاية ٧ ركاب', 'كاش، دولار أو ليرة']),
}


def page(svc, lc):
    w, d = L[lc], svc[lc]
    slug, up, hup = svc['slug'], w['up'], '../'
    canon = (SITE + '/' + slug + '/') if lc == 'en' else (SITE + '/ar/' + slug + '/')
    en_url, ar_url = SITE + '/' + slug + '/', SITE + '/ar/' + slug + '/'
    wa_href = 'https://wa.me/%s?text=%s' % (WA, urlenc(d['wa']))
    others = [s for s in SERVICES if s['slug'] != slug]
    H = []; A = H.append
    ba.head(A, lc, d['title'], d['desc'], canon, en_url, ar_url, d['title'].split(' — ')[0], up)
    ba.header(A, lc, slug)
    ba.hero(A, lc, [(w['crumb_home'], hup), (d['name'], None)], d['kicker'], d['h1'], d['lede'],
            wa_href, w['trust'])
    A('<section class="band light">'); A('  <div class="wrap">')
    A('    <div class="head rv">')
    A('      <p class="kicker">%s</p>' % esc(d['rows_k']))
    A('      <h2 class="h2">%s</h2>' % esc(d['rows_h']))
    A('    </div>')
    A('    <ul class="hoods rv">')
    for n, note in d['rows']:
        A('      <li><b>%s</b> <span>%s</span></li>' % (esc(n), esc(note)))
    A('    </ul>')
    A('    <div class="prose rv">')
    for para in d['body'].split('\n\n'):
        A('      <p>%s</p>' % esc(para))
    A('    </div>'); A('  </div>'); A('</section>'); A('')
    ba.faq_section(A, w['faq_k'], w['faq_h'], d['faqs'], False)
    A('<section class="band dark" id="services">'); A('  <div class="wrap">')
    A('    <div class="head rv">')
    A('      <p class="kicker">%s</p>' % esc(w['others_k']))
    A('      <h2 class="h2">%s</h2>' % esc(w['others_h']))
    A('    </div>')
    A('    <ul class="svc rv">')
    rows = [(o[lc]['kicker'], o[lc]['name'], o[lc]['lede'], '../%s/' % o['slug']) for o in others]
    rows.append((w['areas_k'], w['areas_t'], w['areas_d'], hup + '#areas'))
    for k, t, dd, href in rows:
        A('      <li><a href="%s"><span class="k">%s</span><span class="t">%s<span class="d">%s</span></span>'
          '<span class="arrow">%s%s</span></a></li>' % (href, esc(k), esc(t), esc(dd), esc(w['explore']), ba.ICO_ARROW))
    A('    </ul>'); A('  </div>'); A('</section>'); A('')
    ba.closing(A, lc, up, wa_href)
    ba.footer(A, lc, slug, wa_href)
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
    A(''); A('<script>'); A(ba.TAIL_JS); A('</script>'); A('</body>'); A('</html>')
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
