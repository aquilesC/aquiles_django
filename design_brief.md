# Design Brief 

## Purpose & Positioning

- **Primary goal**: Establish authority, trust, and clarity. The site should immediately communicate *who I am*, *why I exist*, and *how I help*.  
- **Secondary goals**:  
  1. Drive people into deeper engagement (courses, assessments, podcast).  
  2. Showcase thought leadership (articles, stories).  
  3. Facilitate conversions (sign ups, course purchases, contact).  
  4. Serve as a long-tail content platform (searchable, evergreen).

## Visual & Interaction Tone

- Clean, spacious layout; avoid clutter.  
- Emphasis on readability and calm confidence, not flashiness.  
- Subtle transitions / motion (fade, slide) to guide attention, not distract.  
- Visual hierarchy should lead with “why” / mission statements.  
- Use hero video or immersive media above the fold (if feasible) but not at the cost of clarity or performance.

## Structure & Content Flow (Home / Key Entry)

1. **Hero / above-the-fold**  
   - Big headline articulating mission / promise.  
   - Subheading that narrows into the “how.”  
   - Primary CTA (e.g. “Learn More” / “Start Assessment”)  
   - Optional background video / imagery, but dimmed or overlaid to preserve text legibility.

2. **“Why We Do What We Do” Section**  
   - A succinct mission / belief statement (1-2 sentences).  
   - Supporting lines or bullet ideas.  
   - Possibly a link to “Our WHY” deeper page.

3. **The Offer Grid / Segment Entry**  
   - Cards or blocks: e.g. “Take the Assessment,” “Courses & Library,” “Master Presenting,” “Leadership Frameworks.”  
   - Each card: icon / small visual + title + 1-line descriptive sentence + CTA.

4. **Content / Thought Leadership Feed**  
   - Latest blog / story / article previews (image + headline + short excerpt).  
   - “What’s New” label or accent to show freshness.

5. **Social Proof / Logos / Trust**  
   - Logos of well-known clients, media placements, organizations.  
   - Testimonials or quotes.  
   - Possibly a “Trusted by …” line.

6. **Email / Newsletter / Lead Magnet CTA**  
   - Simple email field + short promise of value (e.g. exclusive content).  
   - Light incentive (e.g. “join optimism insights”) but not pushy.

7. **Footer / Navigation + Supplemental Links**  
   - Top-level menus: About, Courses / Offerings, Podcast, Stories, Shop, Login.  
   - Legal: privacy, terms, contact.  
   - Social links, minor extras (search, login, dashboard).

## Typography & Text Styling

- Base font size comfortable for reading (e.g. ≈ 18px or equivalent).  
- Line-length controlled (≈ 45–75 characters).  
- Line-height generous (≈ 1.5).  
- Headlines: bold, strong contrasts. Use size scaling (H1, H2, H3) with clear spacing.  
- A “voice” style: warm, conversational but polished.  
- Use short paragraphs, pull quotes, inline emphasis to break monotony.

## Color, Contrast & Imagery

- A neutral palette (whites / off-whites, soft greys) as base.  
- One strong accent / brand color (for links, CTAs, highlights).  
- Medium contrast typography (dark text on light background).  
- Imagery: high quality, aspirational but not over-the-top.  
- Videos or hero visuals: muted overlays or dark tint so text remains legible.

## Components & Design Tokens

- Predefined token system: spacing (e.g. 16/24/32/48/64), radius, elevation (shadows)  
- Cards, grids, section containers, utility classes.  
- Negative / white (empty) space is a design element.  
- Hover / focus / active states defined for clickable elements.  
- Dark mode support or alternate palette (optional but desirable).  

## Responsive & Performance

- Mobile-first design; ensure hero header is legible on mobile (text, CTA).  
- Collapse navigation (hamburger) on small screens; sticky or slim nav on scroll.  
- Lazy load images, optimize video backgrounds.  
- Minimize critical CSS, avoid render-blocking.  
- Ensure fast load on slow connections.

## Conversion & Engagement Strategy

- CTAs prioritized above the fold (primary) + repeated in mid / bottom sections.  
- Use micro-commitments: assessments, quiz, “learn more” instead of always “buy now.”  
- Gate some premium content behind registration / email capture.  
- Track user flows: which CTAs are clicked; refine accordingly.  
- Use storytelling content (stories, articles) to draw people inward before selling.

## Brand Voice & Messaging Guidelines

- Use “we / us” when referring to mission; “you / your” when addressing visitor.  
- Avoid jargon; prefer clear, resonant metaphors.  
- Be aspirational but grounded — speak to transformation, not hero fantasy.  
- Use narrative (stories, metaphors) in articles / “stories” to humanize.  
- Provide variety: short punchy lines, medium supportive copy, occasional long-form stories.

## Accessibility & Inclusivity

- WCAG AA contrast for all text / interactive elements.  
- Keyboard navigation, focus outlines.  
- Alt text for images, captions for video.  
- Responsive semantics (proper heading order, landmark regions).  
- Avoid color-only indicators; include icons/text if needed.

## Design Restrictions / Guardrails

- No arbitrary HEX or CSS overrides outside token set.  
- Only use one accent color.  
- Use consistent corner radii (small set).  
- Restrict hero visuals to a set of quality videos / images approved.  
- No more than two typeface families.  
- Avoid decorative flourishes that don’t amplify message.

---

You can paste this into your Cursor prompt so every generated page or component is constrained by these rules. It captures the spirit of *simplicity + clarity + brand-forward persuasion* that simonsinek.com embodies.  

If you like, I can also generate a *“simonsinek-style template* (Hero + Offer Grid + Stories feed) in React / Tailwind code you can plug into your stack. Want me to generate that next?
::contentReference[oaicite:1]{index=1}
