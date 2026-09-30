#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build the twelve area pages (six English, six Arabic) and rewrite sitemap.xml.

The site itself has no build step: this script only WRITES static files, which are
committed and served as-is. Nothing at runtime depends on it. Run it when an area
is added or the shared design changes:

    python3 tools/build-areas.py

area.css is extracted from index.html's <style> block on every run, and the same
block (plus the night-road hero) is copied into ar/index.html, so the homepage
stays the single source of truth for the design.
"""
import io, os, re, sys, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://joytaxi.cierp.uk'
WA   = '96171056677'
TEL1, TEL2 = '+96171056677', '+96181686839'
DSP1, DSP2 = '71 056 677', '81 686 839'

# ── The areas. Add one here and both languages appear on the next run. ────────
AREAS = [
 dict(slug='taxi-beirut', en='Beirut', ar='بيروت', schema='City',
   en_hoods=[('Hamra','Ras Beirut and the university quarter'),('Achrafieh','Sodeco, Sassine, Monot'),
             ('Gemmayzeh','and Mar Mikhael, late'),('Verdun','and Mazraa'),('Downtown','Beirut Central District'),
             ('Badaro','and the museum side')],
   ar_hoods=[('الحمرا','رأس بيروت وحي الجامعة'),('الأشرفية','سيوفي، ساسين، مونو'),
             ('الجميزة','ومار مخايل، عالليل'),('فردان','والمزرعة'),('وسط بيروت','الداون تاون'),
             ('بدارو','وجهة المتحف')],
   en_lede='A taxi in Beirut at any hour — Hamra, Achrafieh, Gemmayzeh, Verdun, Downtown, and the airport road when you need it. Send your pin on WhatsApp and a car is on the way.',
   ar_lede='تاكسي ببيروت بأي ساعة — الحمرا، الأشرفية، الجميزة، فردان، وسط البلد، وطريق المطار وقت ما بتحتاج. ابعت موقعك عالواتساب والسيارة جايي.',
   en_body='Beirut traffic is not a distance problem, it is a timing problem. Our drivers run this city every day and every night, so they pick the road that is moving rather than the one that looks shortest on a map. Coming out of a bar in Mar Mikhael at two in the morning, or catching a meeting in Downtown at eight, is the same phone call.',
   ar_body='زحمة بيروت ما هي مشكلة مسافة، هي مشكلة وقت. سوّاقينا عمّال بهالمدينة نهار وليل، فبياخدوا الطريق يلي ماشي مش يلي مبيّن أقصر عالخريطة. طالع من مار مخايل الساعة تنتين بالليل، أو عندك اجتماع بالداون تاون الساعة تمانة — نفس التلفون.'),

 dict(slug='taxi-beirut-airport', en='Beirut Airport', ar='مطار بيروت', schema='Airport', to=True,
   title_en='Beirut Airport Taxi 24/7 — Joy Taxi Lebanon | From $7',
   title_ar='تاكسي مطار بيروت ٢٤/٧ — جوي تاكسي لبنان | من ٧$',
   en_hoods=[('Arrivals','we wait, you walk out'),('Departures','dropped at the door'),
             ('Khaldeh','and the airport road'),('Ouzai','and Jnah'),('Bir Hassan','and Ramlet al-Baida')],
   ar_hoods=[('الوصول','ننطرك، إنت بس اطلع'),('المغادرة','ننزّلك عالباب'),
             ('خلدة','وطريق المطار'),('الأوزاعي','والجناح'),('بئر حسن','والرملة البيضا')],
   en_lede='Airport runs to and from Beirut–Rafic Hariri International, around the clock. Send your flight time and the car is outside before you need it.',
   ar_lede='توصيلة عمطار رفيق الحريري الدولي ومنّو، ٢٤ ساعة. ابعتلنا وقت الطيارة والسيارة تكون برّا قبل ما تحتاجها.',
   en_body='An airport run is the one booking worth making the night before. Tell us your flight time rather than your pickup time and we work backwards from it, traffic included. Coming the other way, send your landing time and terminal — we would rather wait for you than have you waiting on the pavement with a suitcase. Airport fares are priced separately from a ride across town, and you are told the number before you agree to it.',
   ar_body='توصيلة المطار هي الحجز يلي يستاهل تعملو من الليلة قبل. قلّنا وقت الطيارة مش وقت ما بدك نجي، ومنحسبها رجوع من هونيك، والزحمة محسوبة. راجع؟ ابعتلنا وقت النزول والمبنى — أحسن نحنا ننطرك من إنت تنطر عالرصيف وشنطتك بإيدك. تسعيرة المطار محسوبة لحالها، وبتعرف الرقم قبل ما توافق.'),

 dict(slug='taxi-metn', en='Metn North', ar='المتن الشمالي', schema='AdministrativeArea',
   en_hoods=[('Antelias','and Naccache'),('Dbayeh','and Zouk el Kharab'),('Jal el Dib','and Zalka'),
             ('Dekwaneh','and Jdeideh'),('Mansourieh','and Mkalles'),('Bikfaya','Broumana, Beit Mery'),
             ('Rabieh','Mtayleb, Qornet Chehwan')],
   ar_hoods=[('أنطلياس','والنقاش'),('ضبية','وذوق الخراب'),('جل الديب','والزلقا'),
             ('الدكوانة','والجديدة'),('المنصورية','والمكلس'),('بكفيا','برمانا، بيت مري'),
             ('الرابية','المطيلب، قرنة شهوان')],
   en_lede='A taxi across Metn North — Antelias, Dbayeh, Jal el Dib and Zalka on the coast, up through Mansourieh to Bikfaya, Broumana and Beit Mery.',
   ar_lede='تاكسي بالمتن الشمالي — أنطلياس، ضبية، جل الديب والزلقا عالبحر، وصاعد من المنصورية لبكفيا، برمانا وبيت مري.',
   en_body='Metn is two roads, not one: the coastal highway and the hill roads that climb behind it. Which one is faster depends entirely on the hour, and getting that wrong costs twenty minutes. This is the area our drivers live in, so the answer is not a guess. Village addresses that no map application can find are usually a landmark away from being obvious — tell us the church, the bakery or the junction and that is enough.',
   ar_body='المتن طريقين مش طريق: الأوتوستراد عالبحر، وطرقات الجبل يلي طالعة وراه. أيّا واحد أسرع بيعتمد عالساعة، وإذا غلطت بتخسر عشرين دقيقة. هيدي المنطقة يلي عايشين فيها سوّاقينا، فالجواب ما هو تخمين. عناوين القرى يلي ما في تطبيق بيلاقيها، عادة معلَم واحد وبتصير واضحة — قلّنا الكنيسة، الفرن أو المفرق وبيكفي.'),

 dict(slug='taxi-bsalim', en='Bsalim', ar='بصاليم', schema='City',
   en_hoods=[('Mazraat Yachouh','next door'),('Bqennaya','and Beit el Kikko'),('Ain Aar','and Mtayleb'),
             ('Naccache','and Rabieh'),('Qornet Chehwan','and Baabdat')],
   ar_hoods=[('مزرعة يشوع','جنبنا'),('بقنايا','وبيت الككو'),('عين عار','والمطيلب'),
             ('النقاش','والرابية'),('قرنة شهوان','وبعبدات')],
   en_lede='Bsalim is where we are based, so pickups here are the quickest we do — usually a few minutes rather than a wait.',
   ar_lede='بصاليم هي مركزنا، فالتوصيلة من هون أسرع شي منعملو — عادة شي دقايق مش انتظار.',
   en_body='Being local is not a slogan here, it is the reason the car arrives quickly. Bsalim, Mazraat Yachouh, Bqennaya, Ain Aar and Mtayleb are all a short run from where the car already is, and at night that gap between calling and arriving is the whole service. From Bsalim down to Beirut, across to Jounieh, or out to the airport for an early flight — all routine, all priced before you get in.',
   ar_body='إنّا من المنطقة ما هو شعار، هو السبب يلي بيخلّي السيارة توصل بسرعة. بصاليم، مزرعة يشوع، بقنايا، عين عار والمطيلب كلها قريبة من وين السيارة أصلاً موجودة، وعالليل هالفرق بين ما تتلفن وما توصل هو كل الخدمة. من بصاليم عبيروت، أو عجونية، أو عالمطار لطيارة الصبح — كلها عادية، وكلها بسعر متفق عليه قبل ما تطلع.'),

 dict(slug='taxi-jounieh', en='Jounieh', ar='جونية', schema='City',
   en_hoods=[('Kaslik','and the university'),('Maameltein','and the bay'),('Sarba','and Haret Sakher'),
             ('Zouk Mikael','and Zouk Mosbeh'),('Ghadir','and Adonis'),('Harissa','and the cable car'),
             ('Nahr el Kalb','and Adma')],
   ar_hoods=[('الكسليك','والجامعة'),('المعاملتين','والخليج'),('صربا','وحارة صخر'),
             ('ذوق مكايل','وذوق مصبح'),('غدير','وأدونيس'),('حريصا','والتلفريك'),
             ('نهر الكلب','وأدما')],
   en_lede='A taxi in Jounieh and around the bay — Kaslik, Maameltein, Sarba, Zouk, Ghadir, and up to Harissa. Late nights included.',
   ar_lede='تاكسي بجونية وحوالي الخليج — الكسليك، المعاملتين، صربا، الذوق، غدير، وصاعد لحريصا. وسهرات الليل كمان.',
   en_body='Jounieh runs late, which is exactly when taxis get hard to find. Coming out of Maameltein at three in the morning, or off the highway at Nahr el Kalb with no car in sight, is the situation this number exists for. The climb to Harissa and the run out to Adma are both short and both quoted before you set off, so there is no argument at the top of the hill.',
   ar_body='جونية بتسهر، وهيدا بالزبط الوقت يلي بيصير صعب تلاقي تاكسي. طالع من المعاملتين الساعة تلاتة الصبح، أو نازل عن الأوتوستراد بنهر الكلب وما في سيارة، هيدا الوضع يلي هالرقم موجود لإلو. الطلعة لحريصا والتوصيلة لأدما قصار، والتنتين بسعر متفق عليه قبل ما تمشي، فما في نقاش براس الجبل.'),

 dict(slug='taxi-jbeil', en='Jbeil', ar='جبيل', schema='City',
   en_hoods=[('Old Souk','and the crusader castle'),('The Port','and the fishing harbour'),
             ('Amchit','just north'),('Halat','and Fidar'),('Blat','and Mastita'),
             ('Edde','and Hboub'),('Berbara','and Nahr Ibrahim')],
   ar_hoods=[('السوق القديم','والقلعة'),('المرفأ','ومرفأ الصيادين'),
             ('عمشيت','شمال شوي'),('حالات','وفيدار'),('بلاط','ومستيتا'),
             ('إده','وحبوب'),('برباره','ونهر ابراهيم')],
   en_lede='A taxi in Jbeil and Byblos — the old souk, the port, and north to Amchit, Halat and Fidar. Dinner by the water and a car waiting when you are done.',
   ar_lede='تاكسي بجبيل — السوق القديم، المرفأ، وشمالاً لعمشيت، حالات وفيدار. عشا عالبحر وسيارة ناطرة وقت تخلص.',
   en_body='Jbeil is the far end of our road and the one people most often assume is too far. It is not. The run down to Beirut is the longest we do routinely, and it is quoted as one number before you leave rather than worked out on arrival. Around the town itself — the souk, the port, Amchit, Halat, Fidar — the car is usually minutes away, and it runs as late as the restaurants do.',
   ar_body='جبيل آخر طريقنا، وهي يلي أكتر الناس تفكر إنها بعيدة كتير. مش بعيدة. التوصيلة لبيروت أطول شي منعملو بشكل عادي، وبتنقال برقم واحد قبل ما تمشي مش محسوبة وقت توصل. وحوالي البلد نفسها — السوق، المرفأ، عمشيت، حالات، فيدار — السيارة عادة دقايق، وشغّالة لآخر ما تسكّر المطاعم.'),
]

DESCS = {
 'taxi-beirut': ('Taxi in Beirut, Lebanon, 24/7 — Hamra, Achrafieh, Gemmayzeh, Verdun, Downtown, airport road. From $7, agreed before you get in. WhatsApp 71 056 677.',
      'تاكسي ببيروت، لبنان، ٢٤/٧ — الحمرا، الأشرفية، الجميزة، فردان، وسط البلد وطريق المطار. من ٧$، السعر متفق عليه قبل ما تطلع. واتساب 71 056 677.'),
 'taxi-beirut-airport': ('Airport taxi in Lebanon, 24/7 to and from Beirut (BEY). Send your flight time and the car is outside before you need it. WhatsApp 71 056 677.',
      'تاكسي مطار بلبنان، ٢٤/٧ من وعلى مطار بيروت. ابعتلنا وقت الطيارة والسيارة برّا قبل ما تحتاجها. واتساب 71 056 677.'),
 'taxi-metn': ('Taxi in Metn North, Lebanon, 24/7 — Antelias, Dbayeh, Jal el Dib, Zalka, Bikfaya, Broumana, Beit Mery. From $7, agreed up front. WhatsApp 71 056 677.',
      'تاكسي بالمتن الشمالي، لبنان، ٢٤/٧ — أنطلياس، ضبية، جل الديب، الزلقا، بكفيا، برمانا، بيت مري. من ٧$، السعر متفق عليه. واتساب 71 056 677.'),
 'taxi-bsalim': ('Taxi in Bsalim, Lebanon, 24/7 — our base, so pickups here are fastest. Mazraat Yachouh, Bqennaya, Ain Aar, Mtayleb. From $7. WhatsApp 71 056 677.',
      'تاكسي ببصاليم، لبنان، ٢٤/٧ — مركزنا، فالتوصيلة من هون أسرع شي. مزرعة يشوع، بقنايا، عين عار، المطيلب. من ٧$. واتساب 71 056 677.'),
 'taxi-jounieh': ('Taxi in Jounieh, Lebanon, 24/7 — Kaslik, Maameltein, Sarba, Zouk, Ghadir, Harissa. From $7, agreed before you get in. WhatsApp 71 056 677.',
      'تاكسي بجونية، لبنان، ٢٤/٧ — الكسليك، المعاملتين، صربا، الذوق، غدير، حريصا. من ٧$، السعر متفق عليه قبل ما تطلع. واتساب 71 056 677.'),
 'taxi-jbeil': ('Taxi in Jbeil (Byblos), Lebanon, 24/7 — old souk, the port, Amchit, Halat, Fidar. From $7, agreed before you set off. WhatsApp 71 056 677.',
      'تاكسي بجبيل، لبنان، ٢٤/٧ — السوق القديم، المرفأ، عمشيت، حالات، فيدار. من ٧$، السعر متفق عليه قبل ما تمشي. واتساب 71 056 677.'),
}

# ── Words, per language ──────────────────────────────────────────────────────
L = {
 'en': dict(lang='en', dir='ltr', oglocale='en_US', up='../', base=SITE+'/', other=SITE+'/ar/',
   skip='Skip to booking', nav=[('Book','#book'),('Areas','#areas'),('How it works','#how'),('Questions','#faq')],
   call='Call', home='Joy Taxi', areas='Areas', langlink='عربي', langcode='ar',
   kicker='Area we cover', hoods_k='Streets and suburbs', hoods_h='Where exactly.',
   hoods_note='Not on the list? Ask anyway — if it is on this road, the answer is almost always yes.',
   why_k='Why this number', why_h='Three things that matter at 3am.',
   why=[('Answered by a person','Not a recording, not a queue, not an application that needs an account. The same two numbers, day and night, every day of the year.'),
        ('The price before you move','You are told what the ride costs before the car sets off, and it does not change when you arrive. Fares start at $7.'),
        ('The road, known','Our drivers live on this stretch of coast. They know which junction is blocked before they reach it, which is worth more than any map.')],
   faq_k='Before you call', faq_h='Straight answers.',
   others_k='The rest of the road', others_h='Other areas we cover.',
   close_h='Save the number<br>before you need it.',
   close_p='One tap now is one less problem at three in the morning.',
   wa='WhatsApp', callnow='Call now', open247='Open 24/7',
   foot_p='Taxi and private hire along the coast road. Twenty-four hours, every day of the year.',
   foot_call='Call or message', foot_areas='Areas',
   trust=['24 hours, every day','Fares from $7','Cash, dollars or lira'],
   crumb_home='Joy Taxi', wa_pre='I need a taxi in %s', wa_pre_to='I need a taxi to %s',
   desc='%s taxi, 24/7. %s Fares from $7, agreed before you get in. WhatsApp or call %s.',
   h1='Taxi in %s', h1_to='Taxi to %s',
   title='Taxi %s 24/7 — Joy Taxi | From $7, call '+DSP1,
   ogtitle='Taxi %s 24/7 — Joy Taxi'),

 'ar': dict(lang='ar', dir='rtl', oglocale='ar_LB', up='../../', base=SITE+'/ar/', other=SITE+'/',
   skip='روح عالحجز', nav=[('احجز','#book'),('المناطق','#areas'),('كيف بتمشي','#how'),('أسئلة','#faq')],
   call='اتصل', home='جوي تاكسي', areas='المناطق', langlink='EN', langcode='en',
   kicker='منطقة منغطّيها', hoods_k='الشوارع والضهور', hoods_h='وين بالزبط.',
   hoods_note='ما لقيت مكانك؟ اسأل عادي — إذا هو على هالطريق، الجواب دايماً تقريباً إيه.',
   why_k='ليش هالرقم', why_h='تلات أشيا بيفرقوا الساعة ٣ الصبح.',
   why=[('حدا بيردّ','ما في تسجيل، ما في دور، ما في تطبيق بدو حساب. نفس الرقمين، ليل ونهار، طول السنة.'),
        ('السعر قبل ما تمشي','بتعرف قدّيش الرحلة قبل ما تمشي السيارة، وما بيتغيّر وقت توصل. التسعيرة تبدأ من ٧$.'),
        ('الطريق، محفوظة','سوّاقينا عايشين على هالشط. بيعرفوا أيّا مفرق مزنوق قبل ما يوصلوا، وهيدا أغلى من أي خريطة.')],
   faq_k='قبل ما تتلفن', faq_h='جواب مباشر.',
   others_k='باقي الطريق', others_h='مناطق تانية منغطّيها.',
   close_h='خبّي الرقم<br>قبل ما تحتاجو.',
   close_p='ضغطة هلّق بتوفّر عليك مشكلة الساعة تلاتة الصبح.',
   wa='واتساب', callnow='اتصل هلّق', open247='فاتحين ٢٤/٧',
   foot_p='تاكسي وتوصيلات خاصة على طريق الساحل. ٢٤ ساعة، كل يوم بالسنة.',
   foot_call='اتصل أو ابعت', foot_areas='المناطق',
   trust=['٢٤ ساعة، كل يوم','من ٧$','كاش، دولار أو ليرة'],
   crumb_home='جوي تاكسي', wa_pre='بدي تاكسي ب%s', wa_pre_to='بدي تاكسي ع%s',
   desc='تاكسي %s، ٢٤/٧. %s التسعيرة من ٧$، متفق عليها قبل ما تطلع. واتساب أو اتصل %s.',
   h1='تاكسي ب%s', h1_to='تاكسي ع%s',
   title='تاكسي %s ٢٤/٧ — جوي تاكسي | من ٧$ · '+DSP1,
   ogtitle='تاكسي %s ٢٤/٧ — جوي تاكسي'),
}

# ── The four FAQs, per language. %s is the area name. ────────────────────────
FAQ = {
 'en': lambda a, to: [
  ('How do I book a taxi %s %s?' % ('to' if to else 'in', a),
   'Send a WhatsApp to %s saying where you are and where you are going, or just call. '
   'If you cannot describe where you are, use the form on the home page and tap <b>My location</b> — '
   'your phone attaches a map pin the driver opens and follows. No account, nothing to install.' % DSP1),
  ('How much is a taxi %s %s?' % ('to' if to else 'in', a),
   'Fares start at $7. What your ride costs depends on the distance and the hour — a late-night run '
   'costs more than the same run in the afternoon, and an airport trip is priced separately. '
   'You are given the price before the car moves, and it does not change when you arrive.'),
  ('Do you run at night %s %s?' % ('to' if to else 'in', a),
   'Yes — 24 hours, seven days, including holidays. The same two numbers are answered at four in the '
   'morning as at four in the afternoon, and answered by a person.'),
  ('How do I pay?',
   'Cash to the driver at the end of the ride, in US dollars or Lebanese lira. If you need a different '
   'arrangement, ask when you book and you will get a straight answer right away.'),
 ],
 'ar': lambda a, to: [
  ('كيف بحجز تاكسي %s%s؟' % ('ع' if to else 'ب', a),
   'ابعت واتساب على %s وقلّنا من وين وعلى وين، أو بس تلفن. إذا ما بتعرف تشرح وين إنت، '
   'استعمل الاستمارة بالصفحة الرئيسية واضغط <b>موقعي</b> — تلفونك بيرفق نقطة عالخريطة '
   'السوّاق بيفتحها وبيجي. ما في حساب، ما في شي تنزّلو.' % DSP1),
  ('قدّيش التاكسي %s%s؟' % ('ع' if to else 'ب', a),
   'التسعيرة تبدأ من ٧$. قدّيش بتكلّف رحلتك بيعتمد عالمسافة وعالساعة — رحلة الليل أغلى من '
   'نفس الرحلة بعد الضهر، وتوصيلة المطار محسوبة لحالها. بتعرف السعر قبل ما تمشي السيارة، '
   'وما بيتغيّر وقت توصل.'),
  ('في تاكسي بالليل %s%s؟' % ('ع' if to else 'ب', a),
   'إيه — ٢٤ ساعة، ٧ أيام، والأعياد كمان. نفس الرقمين بيردّوا الساعة ٤ الصبح متل الساعة ٤ بعد '
   'الضهر، وبيردّ عليهم حدا مش تسجيل.'),
  ('كيف بدفع؟',
   'كاش للسوّاق بآخر الرحلة، بالدولار الأميركي أو بالليرة اللبنانية. إذا بدك ترتيب تاني، '
   'اسأل وقت تحجز وبيجيك جواب مباشر عالطول.'),
 ],
}

# ── Links every page carries in its footer ───────────────────────────────────
SERVICE_LINKS = [('tours', 'Day tours', 'رحلات يومية'),
                 ('school-transport', 'School & student runs', 'نقل الطلاب'),
                 ('shared-rides', 'Shared rides', 'رحلات مشتركة')]

CHROME = {
 'en': dict(skip='Skip to booking', home='Joy Taxi, home', main='Main',
   nav=[('Book', '#book'), ('Fares', '#fares'), ('Areas', '#areas'), ('Services', '#services'), ('Questions', '#faq')],
   langlink='عربي', langcode='ar', call_aria='Call ' + DSP1, crumb='Breadcrumb',
   wa='WhatsApp', book_wa='Book on WhatsApp', call='Call', callnow='Call now', quick='Quick contact',
   close_k='Keep it close', close_h='Save the number <em>before you need it.</em>',
   close_p='The moment you need a driver is never the moment you want to start looking for one.',
   vcard='Add Joy Taxi to your contacts',
   foot_p='A private car and a driver who knows the coast road. Twenty-four hours, every day of the year.',
   foot_call='Call or message', foot_areas='Areas', foot_services='Services',
   legal='Joy Taxi · Lebanon', open247='Open 24/7',
   fonts=['bodoni.woff2', 'jost.woff2']),
 'ar': dict(skip='انتقل عالحجز', home='جوي تاكسي، الصفحة الرئيسية', main='الرئيسية',
   nav=[('احجز', '#book'), ('الأسعار', '#fares'), ('المناطق', '#areas'), ('الخدمات', '#services'), ('أسئلة', '#faq')],
   langlink='EN', langcode='en', call_aria='اتصل على ' + DSP1, crumb='مسار',
   wa='واتساب', book_wa='احجز عالواتساب', call='اتصل', callnow='اتصل هلّق', quick='اتصال سريع',
   close_k='خلّيه قريب', close_h='خبّي الرقم <em>قبل ما تحتاجو.</em>',
   close_p='اللحظة يلّي بتحتاج فيها سوّاق، أبداً مش اللحظة يلّي بتحبّ تبلّش فيها تدوّر على واحد.',
   vcard='ضيف جوي تاكسي عجهات الاتصال',
   foot_p='سيارة خاصة وسوّاق بيعرف طريق الساحل. ٢٤ ساعة، كل يوم من السنة.',
   foot_call='اتصل أو ابعت رسالة', foot_areas='المناطق', foot_services='الخدمات',
   legal='جوي تاكسي · لبنان', open247='مفتوح ٢٤/٧',
   fonts=['amiri-700.woff2', 'plex-arabic-400.woff2']),
}

ICO_CALL = ('<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
  'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 '
  '19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 '
  '1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 '
  '1 1.7 2z"/></svg>')
ICO_WA = ('<svg class="ico" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 '
  '0-8.6 15L2 22l5.2-1.4A10 10 0 1 0 12 2zm0 2a8 8 0 1 1-4.1 14.9l-.4-.2-3 .8.8-2.9-.2-.4A8 8 0 0 1 12 4zm-3.5 '
  '4c-.2 0-.5.1-.7.4-.3.3-.9.9-.9 2.1s.9 2.4 1 2.6c.1.2 1.7 2.8 4.3 3.8 2.1.8 2.6.7 3 .6.6-.1 1.8-.7 2-1.5.3-.7.3-1.3.2-1.4-.1-.1-.3-.2-.6-.3l-2-1c-.3-.1-.5-.2-.7.1l-.9 '
  '1.2c-.2.2-.3.2-.6.1a6.5 6.5 0 0 1-3.3-2.9c-.2-.4 0-.6.2-.7l.4-.5.3-.5v-.5l-.8-2c-.2-.5-.4-.5-.6-.5z"/></svg>')
ICO_GO = ('<svg class="go-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" '
  'aria-hidden="true"><path d="M4 12h16M14 6l6 6-6 6"/></svg>')
ICO_ARROW = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true">'
  '<path d="M3 12h18M15 6l6 6-6 6"/></svg>')
ICO_SAVE = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" '
  'stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>'
  '<path d="m7 10 5 5 5-5M12 15V3"/></svg>')
WORDMARK = ('<span class="wm-j">JOY</span><span class="wm-bar" aria-hidden="true"></span>'
            '<span class="wm-t">TAXI</span>')

TAIL_JS = """(function(){
  var hd=document.querySelector('.top');
  function onScroll(){hd.classList.toggle('stuck',scrollY>24)}
  addEventListener('scroll',onScroll,{passive:true});onScroll();
  var y=document.getElementById('yr');if(y)y.textContent=new Date().getFullYear();
  var dock=document.getElementById('dock'),cta=document.querySelector('.hero-cta');
  if(dock&&cta&&'IntersectionObserver' in window){
    new IntersectionObserver(function(es){
      dock.classList.toggle('show',!es[0].isIntersecting&&es[0].boundingClientRect.top<0)}).observe(cta);
  } else if(dock){dock.classList.add('show')}
  var els=Array.prototype.slice.call(document.querySelectorAll('.rv'));
  function show(el){el.classList.add('in')}
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){es.forEach(function(e){
      if(e.isIntersecting){show(e.target);io.unobserve(e.target)}})},
      {threshold:.08,rootMargin:'0px 0px -40px'});
    els.forEach(function(el){io.observe(el)});
    /* An element scrolled PAST never intersects, so the observer alone can leave
       blank sections behind: a jump to the end, a restored scroll position or a
       deep link into the page. These are search landing pages, so sweep as well
       and let the animation be the enhancement, never the thing showing the text. */
    var sweep=function(){
      els.forEach(function(el){
        if(!el.classList.contains('in')&&el.getBoundingClientRect().top<innerHeight){show(el);io.unobserve(el)}});
    };
    addEventListener('scroll',sweep,{passive:true});setTimeout(sweep,0);
  } else { els.forEach(show); }
})();"""

ADDENDUM = """
/* ── Area and service pages ─────────────────────────────────────────────────
   Added on top of the homepage's own stylesheet, which this file is generated
   from. Everything above is shared with index.html; only these rules are extra.
   ───────────────────────────────────────────────────────────────────────── */
.hero.sub{min-height:auto;align-items:flex-end}
.hero.sub .hero-in{padding-top:calc(104px + env(safe-area-inset-top,0px));padding-bottom:clamp(40px,7vw,72px)}
@media(min-width:960px){.hero.sub .hero-in{padding-top:150px}}
.hero.sub .h1{font-size:clamp(2.5rem,7vw,5rem);max-width:14ch}
.crumb{margin:0 0 30px;font-size:.8rem;letter-spacing:.06em;color:var(--moon-3)}
.crumb ol{list-style:none;display:flex;flex-wrap:wrap;gap:8px;margin:0;padding:0}
.crumb li+li::before{content:"/";margin-inline-end:8px;color:var(--gold);opacity:.6}
.crumb a{color:var(--moon-2);text-decoration:none;transition:color .25s}
.crumb a:hover{color:var(--gold-hi)}
.crumb [aria-current]{color:var(--moon)}
.hoods{list-style:none;margin:0;padding:0;display:grid;border-top:1px solid var(--hair)}
@media(min-width:760px){.hoods{grid-template-columns:1fr 1fr;column-gap:56px}}
.hoods li{display:flex;align-items:baseline;justify-content:space-between;gap:16px;padding:18px 0;border-bottom:1px solid var(--hair)}
.hoods b{font-family:var(--serif);font-weight:500;font-size:1.3rem;color:var(--fg);line-height:1.2}
:lang(ar) .hoods b{font-weight:700}
.hoods span{font-size:.88rem;color:var(--fg-3);text-align:end}
.prose{margin-top:44px;max-width:62ch;color:var(--fg-2);font-size:1.04rem}
.prose p{margin:0 0 18px}
@media(max-width:559px){
  .hero.sub .facts{flex-direction:column;gap:8px}
  .hero.sub .facts li::before,.hero.sub .facts li+li::before{content:"";width:14px;height:1px;background:var(--gold);opacity:.7;margin:0;margin-inline-end:12px}
}
"""


def esc(s):
    return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
             .replace('"', '&quot;'))


def jesc(s):
    """Escape for a JSON string literal, stripping the <b> tags used in HTML answers."""
    s = s.replace('<b>', '').replace('</b>', '')
    return s.replace('\\', '\\\\').replace('"', '\\"')


def urlenc(s):
    # Percent-encode everything but the unreserved ASCII set. Hand-rolling this is a
    # trap: chr(0xD8).isalnum() is True in Python 3, so Arabic bytes sail through
    # unencoded and the WhatsApp text arrives as mojibake.
    return urllib.parse.quote(s, safe='')


def home_src():
    return io.open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()


def night_svg():
    """The hero's night road, taken from index.html so every page draws the same scene."""
    m = re.search(r'<!--night-->\n(.*?)\n<!--/night-->', home_src(), re.S)
    if not m:
        sys.exit('could not find the <!--night--> block in index.html')
    return m.group(1)


def build_css():
    src = home_src()
    m = re.search(r'<style>(.*?)</style>', src, re.S)
    if not m:
        sys.exit('could not find the <style> block in index.html')
    css = ('/* Generated by tools/build-areas.py from index.html\'s <style> block.\n'
           '   Do not edit by hand: edit index.html and re-run the script. */\n'
           + m.group(1).strip() + '\n' + ADDENDUM)
    io.open(os.path.join(ROOT, 'area.css'), 'w', encoding='utf-8').write(css)
    return len(css)


def sync_ar_home():
    """ar/index.html inlines the same stylesheet and night scene as index.html; copy both across."""
    src = home_src()
    p = os.path.join(ROOT, 'ar', 'index.html')
    ar = io.open(p, encoding='utf-8').read()
    style = re.search(r'<style>.*?</style>', src, re.S).group(0)
    night = re.search(r'<!--night-->.*?<!--/night-->', src, re.S).group(0)
    ar = re.sub(r'<style>.*?</style>', lambda m: style, ar, count=1, flags=re.S)
    ar = re.sub(r'<!--night-->.*?<!--/night-->', lambda m: night, ar, count=1, flags=re.S)
    io.open(p, 'w', encoding='utf-8').write(ar)


# ── Page chrome shared by the area pages and the service pages ─────────────────
def head(A, lc, title, desc, canon, en_url, ar_url, ogtitle, up):
    w = L[lc]; c = CHROME[lc]
    A('<!DOCTYPE html>')
    A('<html lang="%s" dir="%s">' % (w['lang'], w['dir']))
    A('<head>')
    A('<meta charset="utf-8">')
    A('<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">')
    A('<title>%s</title>' % esc(title))
    A('<meta name="description" content="%s">' % esc(desc))
    A('<meta name="theme-color" content="#070B15">')
    A('<link rel="canonical" href="%s">' % canon)
    A('<link rel="alternate" hreflang="en" href="%s">' % en_url)
    A('<link rel="alternate" hreflang="ar" href="%s">' % ar_url)
    A('<link rel="alternate" hreflang="x-default" href="%s">' % en_url)
    A('<link rel="icon" href="%sfavicon.svg" type="image/svg+xml">' % up)
    A('<link rel="apple-touch-icon" href="%sicon-180.png">' % up)
    for f in c['fonts']:
        A('<link rel="preload" href="/fonts/%s" as="font" type="font/woff2" crossorigin>' % f)
    A('<meta property="og:type" content="website">')
    A('<meta property="og:site_name" content="Joy Taxi">')
    A('<meta property="og:locale" content="%s">' % w['oglocale'])
    A('<meta property="og:url" content="%s">' % canon)
    A('<meta property="og:title" content="%s">' % esc(ogtitle))
    A('<meta property="og:description" content="%s">' % esc(desc))
    A('<meta property="og:image" content="%s/og.png">' % SITE)
    A('<meta property="og:image:width" content="1200">')
    A('<meta property="og:image:height" content="630">')
    A('<meta name="twitter:card" content="summary_large_image">')
    A("<script>document.documentElement.className+=' js'</script>")
    A('<link rel="stylesheet" href="%sarea.css">' % up)
    A('</head>')
    A('<body>')


def header(A, lc, slug):
    c = CHROME[lc]; hup = '../'
    twin = ('../ar/%s/' % slug) if lc == 'en' else ('../../%s/' % slug)
    A('<a class="skip" href="#book">%s</a>' % esc(c['skip']))
    A('')
    A('<header class="top" id="top">')
    A('  <div class="wrap bar">')
    A('    <a class="wm" href="%s" aria-label="%s" lang="en">%s</a>' % (hup, esc(c['home']), WORDMARK))
    A('    <nav class="nav" aria-label="%s">' % esc(c['main']))
    for label, href in c['nav']:
        A('      <a href="%s%s">%s</a>' % (hup, href, esc(label)))
    A('    </nav>')
    A('    <div class="bar-end">')
    A('      <a class="lang" href="%s" hreflang="%s" lang="%s">%s</a>'
      % (twin, c['langcode'], c['langcode'], esc(c['langlink'])))
    A('      <a class="btn btn-line btn-sm" href="tel:%s" data-ev="call" aria-label="%s">' % (TEL1, esc(c['call_aria'])))
    A('        ' + ICO_CALL)
    A('        <span class="call-lbl num" dir="ltr">%s</span>' % DSP1)
    A('      </a>')
    A('    </div>')
    A('  </div>')
    A('</header>')
    A('')
    A('<main>')
    A('')


def hero(A, lc, crumbs, kicker, h1_html, lede, wa_href, facts):
    """crumbs: [(label, href or None)], the last one is the current page."""
    c = CHROME[lc]
    A('<section class="hero sub dark" id="book" aria-labelledby="h1">')
    A(night_svg())
    A('  <div class="wrap hero-in">')
    A('    <nav class="crumb" aria-label="%s">' % esc(c['crumb']))
    A('      <ol>')
    for label, href in crumbs:
        if href:
            A('        <li><a href="%s">%s</a></li>' % (href, esc(label)))
        else:
            A('        <li><span aria-current="page">%s</span></li>' % esc(label))
    A('      </ol>')
    A('    </nav>')
    A('    <p class="kicker">%s</p>' % esc(kicker))
    A('    <h1 class="h1" id="h1">%s</h1>' % h1_html)
    A('    <p class="lede">%s</p>' % esc(lede))
    A('    <div class="hero-cta">')
    A('      <a class="btn btn-gold" href="%s" data-ev="whatsapp">' % esc(wa_href))
    A('        ' + ICO_WA)
    A('        %s' % esc(c['book_wa']))
    A('      </a>')
    A('      <a class="btn btn-line" href="tel:%s" data-ev="call"><span class="num" dir="ltr">%s</span></a>' % (TEL1, DSP1))
    A('      <a class="btn btn-line" href="tel:%s" data-ev="call"><span class="num" dir="ltr">%s</span></a>' % (TEL2, DSP2))
    A('    </div>')
    A('    <ul class="facts">')
    for f in facts:
        A('      <li>%s</li>' % esc(f))
    A('    </ul>')
    A('  </div>')
    A('</section>')
    A('')


def faq_section(A, kicker, title, faqs, answer_is_html):
    A('<section class="band light paper" id="faq">')
    A('  <div class="wrap">')
    A('    <div class="head rv">')
    A('      <p class="kicker">%s</p>' % esc(kicker))
    A('      <h2 class="h2">%s</h2>' % esc(title))
    A('    </div>')
    A('    <div class="faq rv">')
    for q, a in faqs:
        A('      <details>')
        A('        <summary>%s</summary>' % esc(q))
        A('        <div class="a"><p>%s</p></div>' % (a if answer_is_html else esc(a)))
        A('      </details>')
    A('    </div>')
    A('  </div>')
    A('</section>')
    A('')


def closing(A, lc, up, wa_href):
    c = CHROME[lc]
    A('<section class="band dark darker close" id="contact">')
    A('  <div class="wrap rv">')
    A('    <p class="kicker" style="justify-content:center">%s</p>' % esc(c['close_k']))
    A('    <h2 class="h2">%s</h2>' % c['close_h'])
    A('    <p class="lede">%s</p>' % esc(c['close_p']))
    A('    <div class="cta-row">')
    A('      <a class="btn btn-gold" href="%s" data-ev="whatsapp">' % esc(wa_href))
    A('        ' + ICO_WA)
    A('        %s' % esc(c['wa']))
    A('      </a>')
    A('      <a class="btn btn-line" href="tel:%s" data-ev="call">%s <span class="num" dir="ltr">%s</span></a>' % (TEL1, esc(c['call']), DSP1))
    A('      <a class="btn btn-line" href="tel:%s" data-ev="call">%s <span class="num" dir="ltr">%s</span></a>' % (TEL2, esc(c['call']), DSP2))
    A('    </div>')
    A('    <a class="vcard" href="%sjoy-taxi.vcf" download="joy-taxi.vcf">' % up)
    A('      ' + ICO_SAVE)
    A('      %s' % esc(c['vcard']))
    A('    </a>')
    A('  </div>')
    A('</section>')
    A('')
    A('</main>')
    A('')


def footer(A, lc, slug, wa_href):
    c = CHROME[lc]; hup = '../'
    twin = ('../ar/%s/' % slug) if lc == 'en' else ('../../%s/' % slug)
    A('<footer class="foot dark darker">')
    A('  <div class="wrap">')
    A('    <div class="fgrid">')
    A('      <div>')
    A('        <a class="wm" href="%s" aria-label="%s" lang="en">%s</a>' % (hup, esc(c['home']), WORDMARK))
    A('        <p>%s</p>' % esc(c['foot_p']))
    A('      </div>')
    A('      <div>')
    A('        <h2>%s</h2>' % esc(c['foot_call']))
    A('        <ul>')
    A('          <li><a class="tel num" href="tel:%s" dir="ltr">%s</a></li>' % (TEL1, DSP1))
    A('          <li><a class="tel num" href="tel:%s" dir="ltr">%s</a></li>' % (TEL2, DSP2))
    A('          <li><a href="%s">%s</a></li>' % (esc(wa_href), esc(c['wa'])))
    A('        </ul>')
    A('      </div>')
    A('      <div>')
    A('        <h2>%s</h2>' % esc(c['foot_areas']))
    A('        <ul>')
    for a in AREAS:
        A('          <li><a href="../%s/">%s</a></li>' % (a['slug'], esc(a[lc])))
    A('        </ul>')
    A('      </div>')
    A('      <div>')
    A('        <h2>%s</h2>' % esc(c['foot_services']))
    A('        <ul>')
    for s, en, ar in SERVICE_LINKS:
        A('          <li><a href="../%s/">%s</a></li>' % (s, esc(en if lc == 'en' else ar)))
    A('        </ul>')
    A('      </div>')
    A('    </div>')
    A('    <div class="legal">')
    A('      <span>&copy; <span id="yr">2026</span> %s</span>' % esc(c['legal']))
    A('      <span><a href="%s" hreflang="%s" lang="%s">%s</a> &middot; %s</span>'
      % (twin, c['langcode'], c['langcode'], esc(c['langlink']), esc(c['open247'])))
    A('    </div>')
    A('  </div>')
    A('</footer>')
    A('')
    A('<div class="dock" id="dock" role="group" aria-label="%s">' % esc(c['quick']))
    A('  <a class="btn btn-gold" href="%s" data-ev="whatsapp">%s</a>' % (esc(wa_href), esc(c['wa'])))
    A('  <a class="btn btn-line" href="tel:%s" data-ev="call">%s</a>' % (TEL1, esc(c['callnow'])))
    A('</div>')
    A('')


def page(area, lc):
    w = L[lc]
    to = area.get('to', False)
    name = area[lc]
    slug = area['slug']
    up = w['up']        # to the site root, for shared assets
    hup = '../'         # to THIS language's home page
    canon = (SITE + '/' + slug + '/') if lc == 'en' else (SITE + '/ar/' + slug + '/')
    en_url = SITE + '/' + slug + '/'
    ar_url = SITE + '/ar/' + slug + '/'
    hoods = area[lc + '_hoods']
    lede = area[lc + '_lede']
    body = area[lc + '_body']
    h1 = (w['h1_to'] if to else w['h1']) % name
    title = area.get('title_' + lc) or (w['title'] % name)
    ogtitle = w['ogtitle'] % name
    desc = DESCS[slug][0 if lc == 'en' else 1]
    wa_txt = (w['wa_pre_to'] if to else w['wa_pre']) % name
    wa_href = 'https://wa.me/%s?text=%s' % (WA, urlenc(wa_txt))
    faqs = FAQ[lc](name, to)

    H = []
    A = H.append
    head(A, lc, title, desc, canon, en_url, ar_url, ogtitle, up)
    header(A, lc, slug)
    hero(A, lc, [(w['crumb_home'], hup), (w['areas'], hup + '#areas'), (h1, None)],
         w['kicker'], esc(h1), lede, wa_href, w['trust'])

    A('<section class="band light">')
    A('  <div class="wrap">')
    A('    <div class="head rv">')
    A('      <p class="kicker">%s</p>' % esc(w['hoods_k']))
    A('      <h2 class="h2">%s</h2>' % esc(w['hoods_h']))
    A('    </div>')
    A('    <ul class="hoods rv">')
    for n, d in hoods:
        A('      <li><b>%s</b> <span>%s</span></li>' % (esc(n), esc(d)))
    A('    </ul>')
    A('    <div class="prose rv">')
    for para in body.split('\n\n'):
        A('      <p>%s</p>' % esc(para))
    A('    </div>')
    A('    <p class="aside-note rv">%s</p>' % esc(w['hoods_note']))
    A('  </div>')
    A('</section>')
    A('')
    A('<section class="band dark" id="how">')
    A('  <div class="wrap">')
    A('    <div class="head rv">')
    A('      <p class="kicker">%s</p>' % esc(w['why_k']))
    A('      <h2 class="h2">%s</h2>' % esc(w['why_h']))
    A('    </div>')
    A('    <div class="why three rv">')
    nums = ['i.', 'ii.', 'iii.'] if lc == 'en' else ['١.', '٢.', '٣.']
    for i, (t, p) in enumerate(w['why']):
        A('      <div><span class="rn">%s</span><h3 class="h3">%s</h3><p>%s</p></div>' % (nums[i], esc(t), esc(p)))
    A('    </div>')
    A('  </div>')
    A('</section>')
    A('')
    faq_section(A, w['faq_k'], w['faq_h'], faqs, True)

    A('<section class="band light" id="areas">')
    A('  <div class="wrap">')
    A('    <div class="head rv">')
    A('      <p class="kicker">%s</p>' % esc(w['others_k']))
    A('      <h2 class="h2">%s</h2>' % esc(w['others_h']))
    A('    </div>')
    A('    <ol class="route across rv">')
    for o in ROUTE_ORDER:
        oa = [a for a in AREAS if a['slug'] == o][0]
        cur = ' aria-current="page"' if o == slug else ''
        A('      <li><a href="../%s/"%s><span class="node" aria-hidden="true"></span><span class="nm">%s</span>'
          '<span class="nt">%s</span>%s</a></li>'
          % (o, cur, esc(oa[lc]), esc(ROUTE_NOTES[o][0 if lc == 'en' else 1]), ICO_GO))
    A('    </ol>')
    A('  </div>')
    A('</section>')
    A('')
    closing(A, lc, up, wa_href)
    footer(A, lc, slug, wa_href)

    # ── Structured data: TaxiService + FAQPage + BreadcrumbList ──────────────
    faq_items = ',\n      '.join(
        '{"@type":"Question","name":"%s","acceptedAnswer":{"@type":"Answer","text":"%s"}}'
        % (jesc(q), jesc(a)) for q, a in faqs)
    A('<script type="application/ld+json">')
    A('{')
    A('  "@context":"https://schema.org",')
    A('  "@graph":[')
    A('    {')
    A('      "@type":"TaxiService",')
    A('      "@id":"%s#service",' % canon)
    A('      "name":"%s",' % jesc(title.split(' — ')[0] if ' — ' in title else title))
    A('      "url":"%s",' % canon)
    A('      "description":"%s",' % jesc(desc))
    A('      "provider":{"@type":"TaxiService","@id":"%s/#business","name":"Joy Taxi",' % SITE)
    A('        "url":"%s/","telephone":["%s","%s"]},' % (SITE, TEL1, TEL2))
    A('      "telephone":["%s","%s"],' % (TEL1, TEL2))
    A('      "priceRange":"$",')
    A('      "currenciesAccepted":"USD, LBP",')
    A('      "paymentAccepted":"Cash",')
    A('      "areaServed":{"@type":"%s","name":"%s",' % (area['schema'], jesc(area['en'])))
    A('        "containedInPlace":{"@type":"Country","name":"Lebanon"}},')
    A('      "availableLanguage":["ar","en"],')
    A('      "openingHoursSpecification":[{"@type":"OpeningHoursSpecification",')
    A('        "dayOfWeek":["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],')
    A('        "opens":"00:00","closes":"23:59"}]')
    A('    },')
    A('    {')
    A('      "@type":"FAQPage",')
    A('      "@id":"%s#faq",' % canon)
    A('      "mainEntity":[')
    A('      %s' % faq_items)
    A('      ]')
    A('    },')
    A('    {')
    A('      "@type":"BreadcrumbList",')
    A('      "@id":"%s#breadcrumb",' % canon)
    A('      "itemListElement":[')
    A('        {"@type":"ListItem","position":1,"name":"%s","item":"%s"},'
      % (jesc(w['crumb_home']), w['base']))
    A('        {"@type":"ListItem","position":2,"name":"%s","item":"%s#areas"},'
      % (jesc(w['areas']), w['base']))
    A('        {"@type":"ListItem","position":3,"name":"%s","item":"%s"}'
      % (jesc(h1), canon))
    A('      ]')
    A('    }')
    A('  ]')
    A('}')
    A('</script>')
    A('')
    A('<script>')
    A(TAIL_JS)
    A('</script>')
    A('</body>')
    A('</html>')
    return '\n'.join(H) + '\n'


# The route line runs south to north, the way the coast road does.
ROUTE_ORDER = ['taxi-beirut-airport', 'taxi-beirut', 'taxi-metn', 'taxi-bsalim', 'taxi-jounieh', 'taxi-jbeil']
ROUTE_NOTES = {
 'taxi-beirut-airport': ('Around the clock', 'على مدار الساعة'),
 'taxi-beirut': ('Hamra, Achrafieh, Downtown', 'الحمرا، الأشرفية، وسط البلد'),
 'taxi-metn': ('The coast and the hills', 'الساحل والجبل'),
 'taxi-bsalim': ('Home base · fastest pickups', 'مركزنا · أسرع وصول'),
 'taxi-jounieh': ('The bay, Kaslik, Maameltein', 'الخليج، الكسليك، المعاملتين'),
 'taxi-jbeil': ('Byblos, the old port', 'بيبلوس، المرفأ القديم'),
}


def build_sitemap():
    rows = []
    def block(loc, en, ar, pri):
        return ('  <url>\n'
                '    <loc>%s</loc>\n'
                '    <lastmod>%s</lastmod>\n'
                '    <changefreq>monthly</changefreq>\n'
                '    <priority>%s</priority>\n'
                '    <xhtml:link rel="alternate" hreflang="en" href="%s"/>\n'
                '    <xhtml:link rel="alternate" hreflang="ar" href="%s"/>\n'
                '  </url>' % (loc, LASTMOD, pri, en, ar))
    rows.append(block(SITE + '/', SITE + '/', SITE + '/ar/', '1.0'))
    rows.append(block(SITE + '/ar/', SITE + '/', SITE + '/ar/', '1.0'))
    for a in AREAS:
        en, ar = SITE + '/' + a['slug'] + '/', SITE + '/ar/' + a['slug'] + '/'
        rows.append(block(en, en, ar, '0.8'))
        rows.append(block(ar, en, ar, '0.8'))
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
           '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
           + '\n'.join(rows) + '\n</urlset>\n')
    io.open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8').write(xml)
    return len(rows)


LASTMOD = os.environ.get('LASTMOD', '2026-09-30')

if __name__ == '__main__':
    n = build_css()
    print('area.css        %d chars' % n)
    sync_ar_home()
    print('ar/index.html   stylesheet and night scene synced from index.html')
    for a in AREAS:
        for lc in ('en', 'ar'):
            d = os.path.join(ROOT, a['slug']) if lc == 'en' else os.path.join(ROOT, 'ar', a['slug'])
            os.path.isdir(d) or os.makedirs(d)
            p = os.path.join(d, 'index.html')
            io.open(p, 'w', encoding='utf-8').write(page(a, lc))
            print('  %-34s %6d bytes' % (os.path.relpath(p, ROOT), os.path.getsize(p)))
    print('sitemap.xml     %d urls' % build_sitemap())
