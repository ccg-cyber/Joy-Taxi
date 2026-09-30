# Joy Taxi — the site

Live at **https://joytaxi.cierp.uk/** (Arabic: **/ar/**).

Two hand-written HTML files, plus eighteen generated area and service pages. No
build step at serve time, no framework, no CDN, no trackers, no cookies, no backend.
The only extra files are six self-hosted fonts in `fonts/` (about 190 KB in all, and
a page only downloads the ones it uses).

**The design.** A private driver on the coast road: midnight navy, warm ivory and
one brushed gold, used sparingly. Bodoni Moda for display, Jost for reading; in
Arabic, Amiri for display and IBM Plex Sans Arabic for reading. The hero is the
coast road at night, drawn in SVG — no photograph — and the only thing that moves
in it is the slow light trails, which stop for anyone who has reduced motion on.

**The design lives in one place: the `<style>` block in `index.html`.** Change it
there and run `python3 tools/build-areas.py` — that copies it into `ar/index.html`
and `area.css`, together with the night-road hero (between `<!--night-->` markers),
so every page on the site follows.

---

## The one thing to change first

Open `index.html`, search for `var CFG = {`. Everything a non-programmer would
ever want to change is in that one block:

```js
whatsapp: '96171056677',   // the number WhatsApp bookings go to
from: [...],               // the pickup buttons
to:   [...],               // the destination buttons
photos: [...],             // filenames looked for in photos/
```

The same block exists near the bottom of `ar/index.html`, with the Arabic
labels. Change both.

Phone numbers also appear as real `tel:` links throughout both files — search
for `96171056677` and `96181686839` to change them everywhere.

---

## Adding the real photos

Drop JPGs into `photos/` with any of these names:

    car-1.jpg  car-2.jpg  car-3.jpg  interior.jpg  driver.jpg
    coast.jpg  jounieh-bay.jpg  byblos-port.jpg

That is the whole procedure. The gallery section is **hidden** until at least
one of those files actually loads, so the page never shows a broken image and
never shows a stranger's car. Add one photo, one section appears. Add none, the
page is still complete — nothing about the design depends on photography.
(The files are only looked for once a visitor scrolls towards that part of the
page, so an empty folder costs the first screen nothing.)

Want different filenames or more of them? Add them to `photos:` in `CFG`.

Good photos to take, roughly in order of how much they earn:

1. The car, clean, shot at night with the interior light on. Night is the whole
   proposition — sell it.
2. The driver, outside the car, looking at the camera. A face beats a vehicle.
3. The back seat, clean and empty. This is the thing passengers are actually
   deciding about.
4. Scenery on the route — the coast road, Jounieh bay, Byblos port — only your
   own shots, never stock.

Shoot them on a phone, landscape, in the ten minutes after sunset. They will
look better than anything a model can invent, because they are true.

---

## Switching the fare estimator on

Pick a pickup and a destination and the booker works out roughly how far the ride
is and shows it. Distance is real: great-circle between two known points, scaled
by `roadFactor` because roads are not straight lines. Checked against the runs
that matter — Beirut to Jbeil comes out 38km against a true 37, Jounieh to Jbeil
21 against 19. It is shown as "about", never as a promise.

**The price is not guessed, and right now it is not quoted at all.** The owner
confirmed he prices each job himself rather than running a formula, so the site
shows the distance and says the price is confirmed on WhatsApp. That is a
deliberate setting, not a gap: `CFG.rates` is left null and the estimator stays
in distance-only mode.

It is also the right call commercially. A quoted number the driver then talks
up is worse than no number; distance plus a fast human answer is honest and
still faster than any competitor's contact form.

He also confirmed **a night rate exists** and that **airport runs are priced
separately**. Both are stated on the page in words; neither is given a figure,
because no figure was supplied. The "no surge at two in the morning" line that
used to sit in the price band has been removed — it was written before that was
known, and it was false.

To quote numbers, fill these in (both files):

```js
rates: {
  base: 5,          // what every ride starts at
  perKm: 0.9,       // added per kilometre
  minimum: 7,       // never quote below the published "from $7"
  nightFrom: 23,    // night rate begins at 23:00
  nightTo: 5,       // ...and ends at 05:00
  nightExtra: 1.25, // 25% more at night
  airport: { 'Bsalim': 30, 'Jbeil': 45 },   // fixed airport prices, or null
  spread: 0.12,     // metered rides quote as a ±12% range
},
```

Two behaviours worth knowing:

- A **metered** fare quotes as a range, because traffic and route genuinely vary.
  Quoting one exact number and then charging another is how a customer stops
  trusting the page.
- An **airport** price from that table is quoted **exactly** — no range, no night
  multiplier. That is what a fixed price means, and putting a spread around it
  hands back the certainty it exists to give.

Whatever it shows, the estimate travels into the WhatsApp message, so the driver
answers against the same number the passenger saw rather than a different one.

---

## What I did not invent

I wrote this from what was already published on the old page: the name, 24/7,
the five areas, both numbers, and "from $7". Everything else is presentation.

There are **no fake reviews, no invented ratings, no made-up fleet size, no
years-in-business, and no fare table.** On a real business's first website those
are a liability, not a shortcut — a customer who is quoted $12 by a site that
promised $9 does not come back.

Two things to confirm before sending the link to a customer:

- **Is 71 056 677 on WhatsApp?** The entire booking flow points at it. If it is
  not, put the number that is into `CFG.whatsapp` in both files.
- **Beirut Airport** appears as a destination button and in the Beirut area
  line. If airport runs are not something Joy Taxi does, delete it from `to:` in
  both `CFG` blocks and from the `<li>Beirut …</li>` line.

## The three quotes

There is a "What regulars say" section on the page, and while its entries are
still **placeholders** (`placeholder: true`) the section stays hidden — an empty
testimonial does not belong on the live page. Invented testimonials on a real
business's site are illegal to publish as genuine in most places, so nothing is
written for them.

Switching it on is one edit. In `CFG`, in both files:

```js
voices: [
  { quote: 'He picked me up at 3am from the airport when nobody else answered.', name: 'Rita', place: 'Jbeil' },
  ...
],
```

Any entry without `placeholder: true` is shown, and the section appears.

Ask three regulars on WhatsApp tonight. It takes an evening, and it is the
single highest-converting thing this page is missing.

---

## The area pages

Twelve pages, six areas in two languages:

    /taxi-beirut/          /ar/taxi-beirut/
    /taxi-beirut-airport/  /ar/taxi-beirut-airport/
    /taxi-metn/            /ar/taxi-metn/
    /taxi-bsalim/          /ar/taxi-bsalim/
    /taxi-jounieh/         /ar/taxi-jounieh/
    /taxi-jbeil/           /ar/taxi-jbeil/

They exist to be found. Somebody typing "taxi jounieh" into a phone should land
on a page that names Kaslik and Maameltein, shows both numbers, and has a
WhatsApp button already holding "I need a taxi in Jounieh" — not on a homepage
they then have to navigate. Each page carries `TaxiService`, `FAQPage` and
`BreadcrumbList` structured data, a canonical URL, and `hreflang` pointing at
its opposite-language twin.

**Do not edit those twelve files by hand.** They are written by:

    python3 tools/build-areas.py

That script holds the areas, the neighbourhood lists and every line of copy in
one table at the top. Adding a seventh area is three lines there and one run —
both languages, the cross-links on all the other pages, and `sitemap.xml` all
update themselves. Editing a page directly means the next run overwrites you.

Nothing at runtime depends on the script. It writes static files, those files
are committed, and GitHub Pages serves them as-is — so the site keeps its
no-build-step promise; the script is just how the files get written.

`area.css` is generated too, extracted from `index.html`'s own `<style>` block
plus a short addendum for the pieces only these pages use. That keeps
`index.html` the single source of truth for the design: change a colour there,
re-run the scripts, and every page follows. The order is:

    python3 tools/build-areas.py      # area.css, ar/index.html styles, 12 area pages
    python3 tools/build-services.py   # 6 service pages and the full sitemap.xml
    python3 tools/build-home-faq.py   # FAQ schema on both homepages The homepages keep their
CSS inline (one request, instant first paint); the area pages share one cached
stylesheet instead of carrying twelve copies of it.

The four questions on every area page — how to book, what it costs, whether we
run at night, how to pay — are the four people actually ask. The price answer
says fares start at $7 and that the number is agreed before the car moves. It
quotes no figure beyond the published $7, for the same reason the homepage
does not.

---

## The homepage FAQ schema

The seven questions on each homepage are also marked up as `FAQPage` structured
data, which is what lets them appear as expandable answers in a search result.

Google requires the marked-up answer to match the words a visitor actually reads,
so the schema is not written by hand next to the questions — it is parsed out of
them:

    python3 tools/build-home-faq.py

Edit a question or an answer in `index.html` or `ar/index.html`, run that, and the
schema follows. It cannot drift out of sync with the page, which is the usual way
this kind of markup turns into a penalty rather than a feature. The script is
idempotent: it replaces its own block on each run.

---

## How it is deployed, and how to update it

This repository **is** the site. No build step. GitHub Pages serves the
`gh-pages` branch exactly as it is.

**To change anything live:** edit a file, push to `gh-pages`, and it is live
within a minute.

**Custom domain** — `joytaxi.cierp.uk`: the `CNAME` file at the root of this
branch tells GitHub the domain; the matching record in Cloudflare is
`CNAME joytaxi → ccg-cyber.github.io` (DNS only). GitHub issues the certificate
itself once both exist.
