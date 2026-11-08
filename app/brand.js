/* Brand settings — the ONLY file that changes to re-skin this app for another taxi company.
   Name, logo, colors, areas, phone numbers, backend address and map start point all live here. */
window.BRAND = {
  name: 'Joy Taxi',
  words: ['JOY', 'TAXI'],
  mark: '/app/logo-mark.png',
  tagline: { en: ['Your Ride,', 'Our Priority'], ar: ['مشوارك،', 'أولويتنا'] },
  api: 'https://joytaxi-api.cierp.uk',
  wa: '96171056677',
  phones: ['71 056 677', '81 686 839'],
  tel: '+96171056677', tel2: '+96181686839',
  colors: { primary: '#FFC800', primaryDark: '#E4B000', ink: '#111114' },
  map: { center: [33.96, 35.58], zoom: 10 },
  currency: '$',
  // name (en/ar), map point, airport:true marks the fixed-price airport place
  areas: [
    { en: 'Beirut', ar: 'بيروت', ll: [33.8938, 35.5018] },
    { en: 'Beirut Airport', ar: 'مطار بيروت', ll: [33.8209, 35.4884], airport: true },
    { en: 'Hamra', ar: 'الحمرا', ll: [33.8959, 35.4829] },
    { en: 'Achrafieh', ar: 'الأشرفية', ll: [33.8886, 35.5199] },
    { en: 'Metn North', ar: 'المتن الشمالي', ll: [33.94, 35.58] },
    { en: 'Bsalim', ar: 'بصاليم', ll: [33.9017, 35.6044] },
    { en: 'Jounieh', ar: 'جونية', ll: [33.9808, 35.6178] },
    { en: 'Jbeil', ar: 'جبيل', ll: [34.123, 35.6519] }
  ],
  cars: [
    { key: 'Economy', icon: '🚗', en: 'Economy', ar: 'اقتصادية', seats: 4 },
    { key: 'Comfort', icon: '🚙', en: 'Comfort', ar: 'مريحة', seats: 4 },
    { key: 'Van', icon: '🚐', en: 'Van', ar: 'فان', seats: 7 }
  ],
  powered: {
    name: 'Ci', by: 'Crispin intelligence · CCG', url: 'https://ci-ccg.com',
    cta: { en: 'Own a taxi company? Get your own app built with Ci', ar: 'عندك شركة تاكسي؟ اطلب تطبيقك الخاص من Ci' }
  }
};
(function () {
  var c = window.BRAND.colors, r = document.documentElement.style;
  r.setProperty('--y', c.primary); r.setProperty('--yd', c.primaryDark); r.setProperty('--ink', c.ink);
})();
