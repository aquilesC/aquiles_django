# Aquiles Design System

A lightweight, opinionated design system for a Wagtail + TailwindCSS personal site. Built to be copy-paste friendly in Cursor and easy to evolve.

---

## 0) Design Principles

* **Clarity over cleverness**: prioritize legibility, structure, and honest content.
* **Scientific elegance**: minimal forms, precise spacing, restrained color, high contrast.
* **Composable**: small, reusable utility-first components.
* **Accessible by default**: AA/AAA contrast, keyboard-friendly, semantic HTML.
* **Performance-first**: minimal DOM, no unnecessary scripts, responsive images.

---

## 1) Brand Voice & Tone

* **Voice**: precise, candid, helpful; avoids hype.
* **Tone**: confident, friendly, pragmatic.
* **Language**: short sentences, active voice, concrete claims.
* **Microcopy**: plain and specific (e.g., “Get in touch” > “Learn more”).

---

## 2) Design Tokens

### Colors

> Neutral-first palette with a single accent. Suggesting a teal/blue accent; adjust tokens as needed.

* **Base**

  * `--bg`: `#ffffff`
  * `--bg-muted`: `#f7f7f8`
  * `--fg`: `#0f172a` (slate-900)
  * `--fg-muted`: `#334155` (slate-700)
  * `--border`: `#e5e7eb` (gray-200)

* **Accent**

  * `--primary`: `#0ea5a6` (teal-500)
  * `--primary-600`: `#0d9488`
  * `--primary-700`: `#0f766e`
  * `--primary-50`: `#f0fdfa`

* **Semantic**

  * `--success`: `#16a34a`
  * `--warning`: `#ca8a04`
  * `--danger`: `#dc2626`

> Tailwind mapping goes in the config section below.

### Typography

* **Headings**: Spectral (serif) or Merriweather; fallbacks `Georgia, Cambria, Times, serif`.
* **Body**: Inter; fallbacks `system-ui, -apple-system, Segoe UI, Roboto, sans-serif`.
* **Scale** (Tailwind):

  * `text-2xl/9` (H1), `text-xl/8` (H2), `text-lg/7` (H3), `text-base/7` (body), `text-sm/6` (meta)

### Spacing & Radii

* **Spacing scale**: Tailwind default; prefer `py-6/8`, `gap-6/8` for sections.
* **Container**: max-w `7xl`, padding `px-4 sm:px-6 lg:px-8`.
* **Radii**: `rounded-xl` (cards/inputs), `rounded-2xl` (hero images).
* **Shadows**: `shadow-sm` (interactive), `shadow-md` (cards hover), never more than `shadow-lg`.

### Breakpoints

* Use Tailwind defaults; design mobile-first.

### Motion

* Subtle only: `transition`, `duration-200`, `ease-out`, `hover:opacity-90`, `hover:translate-y-[-1px]`.
* Reduce motion: respect `prefers-reduced-motion` (no parallax/auto animations).

---

## 3) Tailwind Setup (Config Snippets)

**`tailwind.config.js`**

```js
module.exports = {
  content: [
    "./templates/**/*.html",
    "./**/*.py", // if components are rendered via template tags
  ],
  theme: {
    extend: {
      colors: {
        bg: "var(--bg)",
        "bg-muted": "var(--bg-muted)",
        fg: "var(--fg)",
        "fg-muted": "var(--fg-muted)",
        border: "var(--border)",
        primary: {
          DEFAULT: "var(--primary)",
          50: "var(--primary-50)",
          600: "var(--primary-600)",
          700: "var(--primary-700)",
        },
        success: "var(--success)",
        warning: "var(--warning)",
        danger: "var(--danger)",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "Segoe UI", "Roboto", "sans-serif"],
        serif: ["Spectral", "Merriweather", "Georgia", "serif"],
      },
      maxWidth: { 'measure': '65ch' },
    },
  },
  plugins: [require('@tailwindcss/typography'), require('@tailwindcss/forms')],
}
```

**`input.css`**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --bg: #ffffff;
  --bg-muted: #f7f7f8;
  --fg: #0f172a;
  --fg-muted: #334155;
  --border: #e5e7eb;
  --primary: #0ea5a6;
  --primary-50: #f0fdfa;
  --primary-600: #0d9488;
  --primary-700: #0f766e;
  --success: #16a34a;
  --warning: #ca8a04;
  --danger: #dc2626;
}

.prose { @apply text-fg; }
.prose a { @apply text-primary underline decoration-2 underline-offset-4 hover:no-underline; }
.prose h1, .prose h2, .prose h3 { @apply font-serif text-fg; }
.prose img { @apply rounded-xl; }
```

---

## 4) Layout Patterns

### App Shell

* **Header**: compact, left-aligned logo/name, right-aligned nav.
* **Footer**: light border top, 2–3 columns on desktop (About, Links, Social), single column on mobile.
* **Section**: `mx-auto max-w-7xl px-4 sm:px-6 lg:px-8` + `py-12 sm:py-16`.

### Grid & Density

* Cards use a 12-col grid on desktop: `grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8`.
* Keep line length to \~65–75ch (`max-w-measure`).

---

## 5) Components (HTML-first, Tailwind)

> Copy snippets into Django templates or Wagtail StreamField block templates.

### Buttons

```html
<a href="#" class="inline-flex items-center gap-2 rounded-lg border border-transparent bg-primary px-4 py-2 text-white text-sm font-medium shadow-sm transition hover:bg-primary-600 focus:outline-none focus:ring-2 focus:ring-primary-600 focus:ring-offset-2">
  <span>Get in touch</span>
</a>
```

**Secondary**

```html
<a href="#" class="inline-flex items-center gap-2 rounded-lg border border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-fg transition hover:bg-bg-muted focus:outline-none focus:ring-2 focus:ring-primary-600 focus:ring-offset-2">
  <span>Read more</span>
</a>
```

### Links (inline)

```html
<a href="#" class="text-primary underline decoration-2 underline-offset-4 hover:no-underline">Link</a>
```

### Navigation

```html
<nav class="flex items-center gap-6 text-sm">
  <a class="hover:text-primary" href="/work/">Work</a>
  <a class="hover:text-primary" href="/writing/">Writing</a>
  <a class="hover:text-primary" href="/offer/">Offer</a>
  <a class="hover:text-primary" href="/about/">About</a>
  <a class="hover:text-primary" href="/contact/">Contact</a>
</nav>
```

### Card

```html
<article class="group rounded-xl border border-border bg-white shadow-sm transition hover:shadow-md">
  <a href="#" class="block">
    <img src="/static/example.jpg" alt="" class="aspect-[16/9] w-full rounded-t-xl object-cover" />
    <div class="p-5">
      <h3 class="font-serif text-lg text-fg group-hover:text-primary">Card title</h3>
      <p class="mt-2 text-sm text-fg-muted">Short summary up to two lines.</p>
    </div>
  </a>
</article>
```

### Section Header

```html
<header class="mb-8">
  <h2 class="font-serif text-2xl text-fg">Recent Writing</h2>
  <p class="mt-2 max-w-measure text-fg-muted">Thoughts on deep-tech, product, and science entrepreneurship.</p>
</header>
```

### Badge / Tag

```html
<span class="inline-flex items-center rounded-full bg-primary-50 px-3 py-1 text-xs font-medium text-primary">Deep Tech</span>
```

### Prose (Articles)

```html
<article class="prose prose-slate max-w-none">
  <!-- Wagtail rich text / StreamField renders here -->
</article>
```

### Code Block (within prose)

```html
<pre class="not-prose rounded-xl border border-border bg-bg-muted p-4 text-sm overflow-x-auto"><code>pip install wagtail</code></pre>
```

### Pagination

```html
<nav class="mt-10 flex items-center justify-between" aria-label="Pagination">
  <a class="rounded-lg border px-3 py-2 text-sm hover:bg-bg-muted" href="#">Previous</a>
  <span class="text-sm text-fg-muted">Page 2 of 8</span>
  <a class="rounded-lg border px-3 py-2 text-sm hover:bg-bg-muted" href="#">Next</a>
</nav>
```

### Forms

```html
<form class="space-y-6">
  <div>
    <label class="block text-sm font-medium text-fg" for="name">Name</label>
    <input id="name" name="name" type="text" required class="mt-2 block w-full rounded-xl border-gray-300 focus:border-primary-600 focus:ring-primary-600" />
  </div>
  <div>
    <label class="block text-sm font-medium text-fg" for="email">Email</label>
    <input id="email" name="email" type="email" required class="mt-2 block w-full rounded-xl border-gray-300 focus:border-primary-600 focus:ring-primary-600" />
  </div>
  <div>
    <label class="block text-sm font-medium text-fg" for="message">Message</label>
    <textarea id="message" name="message" rows="5" class="mt-2 block w-full rounded-xl border-gray-300 focus:border-primary-600 focus:ring-primary-600"></textarea>
  </div>
  <button class="inline-flex items-center rounded-lg bg-primary px-4 py-2 text-white text-sm font-medium hover:bg-primary-600 focus:outline-none focus:ring-2 focus:ring-primary-600 focus:ring-offset-2">Send</button>
</form>
```

### Callout / Note

```html
<div class="not-prose mt-8 rounded-xl border-l-4 border-primary bg-primary-50 p-4">
  <p class="text-sm text-fg"><strong>Note:</strong> This post summarizes a talk given at TU Delft.</p>
</div>
```

---

## 6) Page Templates (Composition)

### HomePage

* **Hero**: name, short descriptor, primary CTA.
* **Featured Projects**: 3–6 cards.
* **Latest Writing**: 3–6 posts.
* **CTA band**: concise contact/offer.

### BlogIndexPage

* Intro/strapline, optional filters (tags).
* Grid of posts (cards). Pagination.

### BlogPage

* Hero image optional; otherwise clean title + meta.
* Article in `.prose`.
* Tags row + next/prev.

### ProjectsIndexPage

* Filterable grid (category/status optional).

### ProjectPage

* Title, meta (role, timeframe), hero.
* Summary → body (StreamField), gallery, external links.

### ServicesIndexPage

* Intro, service blocks (icon + body), FAQ snippet list.

### AboutPage

* Portrait, biography, highlights (badges), links.

### ContactPage

* Short intro + form + social links.

---

## 7) Wagtail Integration Notes

* **Images**: always use renditions, e.g. `{{ image.get_rendition:'width-1200 format-webp' }}`.
* **StreamField blocks**: map to component templates in `templates/components/`.
* **Snippets**: Navigation, SocialProfile, FAQItem/Category, Category.
* **SEO**: add fields for `seo_title`, `search_description`, `social_image` (1200×630) on base page model.
* **Sitemap/Robots**: enable `wagtail.contrib.sitemaps`; add `robots.txt` template.

---

## 8) Accessibility Checklist

* Semantic HTML5 tags (`header`, `main`, `nav`, `article`, `footer`).
* Focus styles visible; test keyboard-only navigation.
* Color contrast AA+; never rely on color alone.
* Provide `alt` text; decorative images `alt=""`.
* Form fields associated with labels; clear error messages.

---

## 9) Content Guidelines

* **Headings**: each page has one H1; start sections with H2.
* **Titles**: ≤ 60 chars (SEO snippet fit). Excerpts ≈ 160 chars.
* **Dates**: ISO-like “20 Aug 2025” (locale-aware).
* **CTAs**: one primary per view.
* **Images**: compress; descriptive filenames; set focal points.

---

## 10) Icons & Illustrations

* Use simple line icons (Lucide/Feather) sized `w-5 h-5`.
* Monochrome illustrations or subtle duotone with the primary color.