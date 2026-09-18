# Joy Taxi — the site

Live at **https://joytaxi.cierp.uk/** (Arabic: **/ar/**).

Two hand-written HTML files. No build step, no framework, no CDN, no fonts to
download, no trackers, no cookies, no backend. You can open `index.html` from a
USB stick on a laptop with no internet and it works. That is deliberate: the
person loading this is usually standing on a street at night on one bar of 3G.

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

Drop JPGs into `photos/` named `car-1.jpg`, `car-2.jpg`, `car-3.jpg`.

That is the whole procedure. The gallery section is **hidden** until at least
one of those files actually loads, so the page never shows a broken image and
never shows a stranger's car. Add one photo, one section appears. Add none, the
page is still complete — nothing about the design depends on photography.

Want different filenames or more of them? Add them to `photos:` in `CFG`.

Good photos to take, roughly in order of how much they earn:

1. The car, clean, shot at night with the interior light on. Night is the whole
   proposition — sell it.
2. The driver, outside the car, looking at the camera. A face beats a vehicle.
3. The back seat, clean and empty. This is the thing passengers are actually
   deciding about.

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

There is a "What regulars say" section on the page, and it currently holds
three **placeholders** — dashed outline, "First name", and a line underneath
saying so. That is deliberate. Invented testimonials on a real business's site
are illegal to publish as genuine in most places, and they are the one thing on
this page a customer could act on and be wrong about.

Replacing them is one edit. In `CFG`, in both files:

```js
voices: [
  { quote: 'He picked me up at 3am from the airport when nobody else answered.', name: 'Rita', place: 'Jbeil' },
  ...
],
```

Drop `placeholder: true` and the dashed styling and the note under the section
both disappear on their own — the note only renders while *every* card is still
a placeholder, so it cannot accidentally go live.

Setting `voices: []` hides the section entirely.

Ask three regulars on WhatsApp tonight. It takes an evening, and it is the
single highest-converting thing this page is missing.

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
