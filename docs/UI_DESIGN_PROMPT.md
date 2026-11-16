# HomeLens AI: UI design prompts

Two prompts. **A** is the original brief (dark liquid glass). **B** describes the site as it is built today (Daylight style) and can be pasted into another tool to reproduce or extend it.

---

## A. Original UI design prompt (dark liquid glass)

```
Act as a world-class, award-winning Principal Product Designer and Creative Technologist specializing in cutting-edge, high-trust AI systems. Design a flawless, ultra-sophisticated desktop dashboard for "HomeLens AI"—an NLP decision-support platform that transforms thousands of free-form customer reviews into structured risk intelligence for home-service executives.

The absolute core of this interface is a pervasive, visually stunning, and highly consistent "LIQUID GLASS" aesthetic. Every container, widget, and interface mechanism must look and feel like a dynamic, translucent organic membrane filled with fluid.

GLOBAL VISUAL AESTHETIC & PHYSICS-BASED ANIMATIONS:
- The Canvas & Background: A rich obsidian canvas (#0D0D11). Beneath the glass interface layer, a faint, slow-moving blurred aura of organic liquid globs morphs dynamically, subtly reacting to mouse movements across the screen.
- The Liquid Glass Substrate: All containers and cards are crafted from hyper-polished translucent glass (backdrop-filter: blur(24px) saturate(180%)) with a 1px soft, glowing border gradient mimicking a refracted prism edge.
- Fluid Micro-Interactions: Every interactive state rejects rigid geometric transitions. Hovering, clicking, or expanding items must trigger smooth, liquid-like easing curves (elastic and fluid deformation physics), making the glass boundaries warp, ripple, or morph organically.

THE LIQUID GLASS COMPONENT ARCHITECTURE:
1. Dynamic KPI Header with Mercury-Drop Sparklines:
   A top ribbon of floating, mercury-like glass pods showing core high-level metrics (Total Reviews Analyzed, Net Sentiment Shift, Critical Risk Escalations). Inside each pod, a miniature real-time sparkline flows smoothly like liquid metal. Hovering over a pod causes the capsule to expand organically like a fusing liquid cell, revealing detailed tooltip overlays.

2. Interactive Risk Leaderboard with Amorphous Rows (Center-Left):
   A beautifully structured leaderboard filtering providers with a minimum of 20 reviews. The table structure is built from stacked glass tabs. Rows utilize a conditional-formatting fluid color gradient to map fast-moving risk spikes. When a row is selected, it ripples outwards and smoothly melts/expands downwards to expose a deeper provider-trajectory view.

3. Interactive Amorphous "Aspect Radar" Blob (Center-Right):
   Instead of a traditional geometric wheel, the 8 extracted aspect classes (Workmanship, Reliability, Pricing, Communication, Timeliness, Professionalism, Warranty, Safety) are mapped onto a shifting, organic 3D liquid glass blob. Hovering over a specific aspect trigger causes the blob to morph dynamically, sending a visible pressure wave through the glass body and focusing its shape toward that specific vector while displaying its precise keyword cluster frequency in a floating liquid bubble.

4. Explainable NLP Ground Truth Feed (Bottom Full-Width Component):
   A dual-panel split view housed inside a massive, unified glass deck.
   - Left Panel (The Input): Raw customer review text. Sentences with negative sentiment are encapsulated inside floating, jelly-like transparent bounding boxes representing the DistilBERT layers.
   - Right Panel (The Evidence): A terminal view showing the exact "Evidence Sentence" extracted by spaCy. This sentence appears to float inside a viscous fluid column. Clicking "View Model Weights" triggers a cascading waterfall animation of transparent data pills dropping smoothly into place.

5. Viscous Action-Triage Dock (Persistent Contextual Component):
   A sleek, modern action drawer anchored in the bottom right. When a user selects a risk flag, this drawer surfaces gracefully, expanding like a liquid bubble breaking the surface tension of the interface. It displays translucent, highly interactive playbook buttons ("Triage Response Email," "Initiate Quality Audit") that bubble up smoothly on demand.

CRUCIAL UX SAFEGUARDS & DESIGN NUANCES:
- Allegation Disclaimer: Permanently etched into the footer as a subtle, translucent watermark that shifts slightly with parallax physics: "System architecture surfaces consumer allegation signals; does not compile verified legal findings."
- Total Visual Continuity: No hard edges, no abrupt flashing transitions, and no generic solid blocks. Every single tab, button, card, and indicator must adhere completely to the rules of light refraction, glass transparency, and fluid motion.
```

---

## B. Current UI design prompt (Daylight style, as built)

```
Design and build a sleek, fast, full product website for "HomeLens AI": an NLP decision-support product that turns customer reviews of home-service providers into review-level risk signals, explainable complaint aspects, provider monitoring and recommended management actions. The site has standard product pages plus a working live demo. Use Next.js (App Router, TypeScript).

VISUAL STYLE (Daylight-inspired, restrained, premium, never childish)
- Canvas: warm cream paper (#FFF4E0) with a static, very soft backdrop of peach, sun-yellow and periwinkle light. Ink is warm near-black (#1B1511).
- Type: Instrument Serif for headlines (light, tight, large; italic for the one emphasized word), JetBrains Mono for small uppercase numbered labels ("01 — FLAG", "WHY HOMELENS"), Inter for body and data.
- Accent: Daylight sun orange (#F5780F, gradient #FFB13D to #EE640A) for primary buttons only, with dark ink text on it. Sun yellow (#FFC933) for step cards. Periwinkle (#BCD0FF) band with a navy (#1C3A8F) serif headline.
- Risk tier colors are reserved for risk and always carry a text label: Stable green, Watch amber, Elevated deep rust (so it never reads as the orange accent), High concern red.
- Liquid glass, iOS-style but static and cheap: frosted warm-white panes, a bright refracted 1px rim lit from the top left, soft contact shadow, large radii (18 to 34 px). Real backdrop-filter blur ONLY on the floating nav bar, the demo bar, the mobile menu and the triage dock; every other pane fakes the look with gradients over the static backdrop.
- Imagery: full-bleed original dusk-over-a-neighborhood hero (dark, with power lines and a sun glow), a desert-sunset band behind three yellow numbered step cards, and a dark dusk photo CTA. No stock logos, fake customers or fake testimonials.
- Layout cues from Daylight: a floating rounded nav bar with logo, five links and an orange button; dark photographic hero with a centered serif headline; a periwinkle/navy split band with a photo on the left; brand sun-ray mark behind inner-page headlines.

PERFORMANCE RULES (the site must never feel laggy)
- No canvas, no infinite decorative animation, nothing that animates layout on hover. Motion is opacity/transform only and respects prefers-reduced-motion.
- Server-render marketing pages; client islands only for the nav, the analyzer and the demo. Self-host fonts with next/font. Lazy-load screenshots. Mount leaderboard row details only on first open. Pause the aspect radar off-screen and idle it at about 20 fps.

PAGES
Home (hero, stats strip, working paste-a-review analyzer, three-layer sunset step cards, leaderboard and evidence screenshots, eight aspect cards with real lift numbers, periwinkle Responsible AI band, dark CTA), Product, How it works (real model metrics table, data splits, score formula, tiers), Pricing (honest: free demo today, Pilot and Enterprise are roadmap notes, no invented prices), Responsible AI and privacy, Docs (the /api/analyze endpoint with a real response), About, FAQ, Contact (email and repo links only if configured), Changelog, Privacy, Terms, 404, sitemap, robots, social image, and /demo.

THE DEMO (/demo, same style)
1. Three KPI cards: Total Reviews Analyzed, Net Sentiment Shift, Critical Risk Escalations, each with a flowing sparkline and a dark tooltip on hover.
2. Risk leaderboard of anonymized Provider_XXXX codes with at least 20 reviews: tier filters, search, sort, risk bar, trend, top signal; a row opens into a yearly trajectory chart, facts and recommended action.
3. Amorphous eight-aspect radar blob (Workmanship, Reliability, Pricing, Communication, Timeliness, Professionalism, Warranty, Safety) with a pressure wave and a keyword-cluster tooltip on hover; selecting an aspect filters the leaderboard.
4. Explainable evidence feed: review text with flagged sentences boxed, a dark terminal pane with the evidence sentence and matched phrases, and a "View Model Weights" waterfall of term pills.
5. Action-triage dock (bottom right) with "Triage Response Email" and "Initiate Quality Audit" drafts. Drafts are for human review; nothing is sent.

CONTENT AND SAFETY RULES
- Say: review-based risk signal, management attention, operational concern, relative concern tier, complaint signal, human investigation. Never claim bankruptcy prediction, legal liability, verified misconduct, verified safety violation or fraud detection.
- Metrics come only from validated project data (artifacts/model_comparison.csv and the notebook facts); never invent or recompute performance numbers.
- Keep this disclaimer visible in the footer and the demo: "System architecture surfaces consumer allegation signals; does not compile verified legal findings."
- The website's live demo runs the TF-IDF logistic regression model; DistilBERT is the primary model in the notebook and the Streamlit app. Say so.
```
