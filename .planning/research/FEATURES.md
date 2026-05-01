# Feature Research — Wellness Buddy

**Domain:** Self-hosted nutrition/wellness tracking PWA (plan-driven, family-oriented)
**Researched:** 2026-05-01
**Confidence:** HIGH (multiple competitive apps verified, 2026 sources, alignment with PROJECT.md/PROMPT_CONTRACT explicit)

---

## Strategic Framing

The 2026 nutrition app market splits into two paradigms:

1. **Food-database-driven (rearview mirror):** MyFitnessPal, Cronometer, Lose It!, Lifesum, Yazio. User logs what they ate, app computes macros from a 20M+ item database. Strength: flexibility. Weakness: "5pm dinner question" — app knows your past, not your future.

2. **Plan-driven (windshield):** Eat This Much, Prospre, Plan to Eat, equ, FoodiePrep. User receives/configures a plan, app guides what to eat next, generates shopping list, tracks adherence. Strength: low friction once configured, decisional fatigue eliminated. Weakness: rigidity if no variant flexibility.

**Wellness Buddy is firmly in camp #2 with three sharp differentiators:**
- Markdown plan as **source of truth** (not in-app editing)
- **Multi-user family sync** with shared meals (rare — only AnyList, Plan to Eat, Nori address this and none combine it with prescribed nutrition plans)
- **Self-hosted privacy** (none of the leaders — all SaaS with cloud lock-in)

This positioning means the table-stakes list is **shorter** than a generic nutrition app (we don't need a food database, barcode scanner, recipe library, or wearable sync to be "complete") but the win-requisite UI/UX bar is **higher** because the app must feel premium against polished SaaS competitors.

---

## Feature Landscape

### Table Stakes (Users Expect These — Missing = Broken)

Features users assume exist in any nutrition/wellness app in 2026. For Wellness Buddy specifically (plan-driven, max 100 users, two-person family caso primario), the bar is **lower** than mass-market apps but higher than a hobby tracker.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **"Today" landing view** | Cognitive default — open app, see today's meals/workout/weight at a glance. Every leader (MyFitnessPal, Cronometer, Lifesum, Macrofactor) opens to "today." | LOW | Already in PROJECT.md as `/today`. Must load <1s, work offline. Hero element of UI. |
| **Meal completion checkmarks** | Adherence tracking implies marking a meal done. Lifesum, Eat This Much, Plan to Eat all use checkbox/swipe gesture. | LOW | Boolean per meal per day. Visual feedback critical for "playful" feel — checkmark celebration moment. |
| **Weight log with chart** | Universal table stakes since 2010. Line chart, ability to delete/edit points, date-aware. | LOW | Recharts in stack. Plot rilevazioni reali. |
| **Trend smoothing on weight chart** | Moving average is standard since Happy Scale (2012) and TrendWeight popularized it. Raw daily weights are noisy and demotivating — users expect a smoothed line. | MEDIUM | EWMA or simple 7-day moving average overlaid on raw points. PROJECT.md already specifies banda tolleranza ±0.5 kg/sett, this delivers it. |
| **Workout log (manual)** | All competitors offer at minimum a "did I work out today" toggle plus duration. PROJECT.md already covers boolean + duration + tipo + note. | LOW | No auto-detect needed — manual is acceptable per PROJECT.md "input manuale dall'utente". |
| **Shopping list with checkboxes** | Bring!, AnyList, Plan to Eat, FoodiePrep all have persistent checkbox state. Users expect items to stay checked when they close the app mid-shop. | LOW | Already in PROJECT.md. Persistent state via Dexie + sync. |
| **Shopping list categorization by aisle/section** | Listonic data: category-organized lists complete shopping 40% faster. AnyList, Bring!, Plan to Eat all auto-categorize. | LOW | PROJECT.md specifies Frigo&Freschi / Frutta&Verdura / Dispensa / Condimenti / Integratori — perfect 5-category Italian-supermarket layout. |
| **Offline-capable** | PWA promise. Users expect to open shopping list at supermarket where signal drops. Dexie+Workbox is the proven 2026 stack. | MEDIUM | Already in stack. Critical for shopping list and "today" view. Sync conflicts must be handled. |
| **Login with email/password** | Baseline auth. Users tolerate this if onboarding is fast. | LOW | JWT specified. No social auth required given private/invite-only nature. |
| **Mobile-first responsive** | 60%+ of nutrition app sessions are mobile. PROJECT.md mandates 390px-first. | MEDIUM | Tailwind + breakpoints. Every component designed mobile-first per PROJECT.md. |
| **Installable PWA (Add to Home Screen)** | Without this, app feels like a website. iOS Safari + Android Chrome both expected. | LOW | Vite PWA plugin handles. Manifest icons 192/512 required. |
| **Date-aware data entry** | Logging weight/workout for *today* is one tap; logging for yesterday must be possible without friction. | LOW | Date picker default to today, swipe/arrow back to prior days. |
| **Edit/delete entries** | Mistakes happen. Every competitor allows. Soft-delete preferable. | LOW | DELETE endpoints already in PROMPT_CONTRACT. |
| **Macro display per meal** | Plan-driven apps (Eat This Much, Prospre) all show kcal + protein/carbs/fat per meal card. Already in MD plan format. | LOW | Parsed from MD, displayed on MealCard. |
| **Light/dark mode** | 2026 baseline. iOS users especially expect respect for system theme. | LOW | Tailwind dark: utility classes. Critical for "elegance" perception. |
| **User profile with goals** | Username, current weight, target weight, goal date — visible somewhere. | LOW | Settings page. Most data already in MD plan, just surface it. |

### Differentiators (Competitive Advantage — Where We Win)

These align with Wellness Buddy's Core Value and the elegant+playful win requisite. **Don't try to differentiate on everything** — focus the bets.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Markdown plan as source of truth** | No nutrition app uses MD as the canonical plan format. Editable in any text editor, versionable in git, doesn't lock user into the app. Aligns with self-hosted ethos. | MEDIUM | Already PROJECT.md-specified. Differentiator vs. all SaaS competitors. |
| **Multi-user family meal sync** | **The strongest differentiator.** AnyList syncs shopping lists, Plan to Eat syncs recipes, but **none** sync prescribed-nutrition meal data with shared cene/pranzi between users with distinct plans. This is the Stefano+Marta primary use case and a market gap. | HIGH | Group entity in PROJECT.md. UI: badge "condiviso con [nome]" on shared meals. Edge case: variant disagreement (Stefano picks A, Marta picks B for same shared dinner) — resolution UI needed. |
| **Variant selector A/B/Pasta speciale** | Plan adherence reality: rigid plans get abandoned (S4H study: 30-day adherence cliff). Variant choice preserves autonomy → extends adherence. Eat This Much has "Fit Into Plan" (treats), Prospre has meal swaps, but A/B/special-pasta is more constrained and Italian-realistic. | MEDIUM | Already PROJECT.md. UX: thumb-friendly segmented control on MealCard. |
| **Auto-shopping-list from variant choices** | This is the **killer reactive feature**. User flips variant Tuesday → shopping list mutates instantly. Plan to Eat does this for recipes but not at this level of integration with a prescribed plan. | MEDIUM | Aggregation logic non-trivial (sum same ingredients across days, normalize units). Already PROJECT.md. |
| **Weight projection with tolerance band** | Most weight apps show a goal *line* but not an *expected curve* with tolerance. The MD plan provides projection data → app draws the corridor. Visual "in linea / sopra / sotto" status is a unique adherence metric. | MEDIUM | Recharts ReferenceArea for band. PROJECT.md ±0.5kg/sett. Color-coded delta indicator. |
| **Diff view between plan versions** | When plan is updated mid-cycle (real scenario per PROJECT.md), seeing what *changed* before applying prevents "wait, what happened to my Tuesday lunch?" confusion. Differentiator: no SaaS competitor does this because they don't have versioned plans. | MEDIUM | git-style additions/removals/changes. Pre-confirmation modal. |
| **Self-hosted + private** | All competitors are SaaS. For health data privacy-conscious users (and Italian families especially), running on own server is a legitimate value prop. | (Architecture, not feature) | Built into stack. Surface in marketing/landing only. |
| **Subtle gamification (no badges/leaderboards)** | The win-requisite "elegant+playful" balance. Apple's Activity Rings approach: simple, visual, emotionally immediate, no badges. Streak count + adherence % + micro-celebrations on completion. | MEDIUM | Single streak counter + weekly adherence ring + Lottie/CSS micro-animation on weekly weigh-in completion. NO points, NO badges, NO leaderboards (anti-pattern below). |
| **Lunedì rituale** | PROJECT.md: lunedì = pesata + reset settimana. Nutrition apps don't have a *named ritual day*. Branded "Lunedì check-in" creates anticipation — push notification + special UI state. | LOW | Notification scheduling + Monday-specific landing variant. Cheap, distinctive. |
| **Italian-first UX** | Competitors are English-first translations. Native Italian copy, Italian categorie spesa, Italian ingredient names, Italian meal patterns (colazione/pranzo/cena/spuntino vs. breakfast/lunch/dinner/snack). | LOW | Copy + i18n architecture. No translation layer needed if Italian is canonical. |
| **AI provider abstraction (Sprint 5)** | Provider pattern + on-prem Ollama option = no SaaS lock-in for AI features. Differentiator vs. competitors who bake in OpenAI/proprietary AI. | MEDIUM | Already architected. NullProvider Sprint 1, real implementations later. |

### Anti-Features (Deliberately NOT Built — Resist Scope Creep)

The most important section. Wellness Buddy's differentiation **depends** on saying no to these.

| Feature | Why Tempting | Why Wrong For Us | Alternative |
|---------|--------------|------------------|-------------|
| **Food database with calorie lookup** | "But MyFitnessPal has 20M items!" Users may request it. | (1) Out of scope per PROJECT.md. (2) Maintaining/licensing a food DB is huge work for 100 users. (3) The MD plan IS the source of macros. (4) Adding a DB invites scope creep into ad-hoc logging — destroys plan-driven discipline. | Macros come from MD plan parsing. If user wants to deviate, they note it in workout/journal field, not in a food log. |
| **Barcode scanner** | "Quick add" UX trope. Users will ask. | Same reasoning as food DB. Requires DB to be useful. | Don't build. Direct users to mark variant + note any deviation. |
| **Recipe library with photos** | Lifesum, Yazio, Plan to Eat lean on this hard. Visually appealing. | Plans are MD-defined. Adding a recipe library duplicates source of truth and creates maintenance burden (photos, normalization, search). | The MD plan can include recipe URLs/notes inline. Display as plain text. |
| **Calorie burn auto-calculation** | "Smart" feature that estimates from workout type/duration. | Per PROJECT.md: input manuale. Auto-calculation is unreliable without HR data, creates false precision, invites complaints when "wrong." | Manual input only. User can copy from watch if available. |
| **Wearable sync (Apple Watch, Garmin, Fitbit)** | All major competitors sync with at least Apple Health. | Out of scope per PROJECT.md (post-v1 evaluable). Each integration is OAuth + API maintenance + sync conflict resolution. For 100 users, ROI is tiny. | Manual workout entry. Future Sprint 6+ if validated demand. |
| **Public registration / signup forms** | Standard SaaS pattern. | Per PROJECT.md: invite-only, 100 users max. Public signup invites spam, abuse, compliance issues. | Admin generates invite token, shares link out-of-band. |
| **Social features (friends, feeds, sharing posts)** | Engagement boost trope. | Hard conflict with self-hosted privacy ethos. Family group is the only social unit. Fitness "feeds" feel cheesy and dilute the elegant aesthetic. | Multi-user family sync IS the social layer. Stop there. |
| **Badges, trophies, levels, XP** | Gamification = engagement, right? | **Research counter-evidence (2025/26):** apps with moderate gamification outperform over-designed systems. Badges feel infantilizing in an elegant UI. WHOOP/Apple don't use them. Conflicts with win requisite. | Streak counter + weekly adherence ring + tasteful micro-celebrations on milestones. No XP, no levels. |
| **Leaderboards / social ranking** | Drives engagement in some apps (Strava). | Comparing weight/adherence between family members is a relationship hazard. Health is not a competition. | Each user sees their own progress. Shared meals are *cooperative*, not competitive. |
| **Push notifications "you haven't logged today!"** | Re-engagement standard. | Annoyance pattern. Health-shaming users → uninstalls. Per research: irrelevant notifications drive uninstalls. | Only 1 scheduled notification: lunedì pesata reminder (opt-in). Maybe one celebratory weekly summary. That's it. |
| **AI calorie photo recognition** | NutriScan, Cal AI, Fud AI all do this. Hot 2026 feature. | Same reason as food DB — incompatible with plan-driven model. Photo recognition is impressive demo, low daily utility for prescribed plans. | If AI ships in Sprint 5, focus on chat/coaching/meal suggestions within plan, not free-form logging. |
| **In-app purchases / premium tier** | Standard monetization. | Per PROJECT.md: self-hosted free for famiglia. No billing system. | Single tier, all features. Hosting cost borne by self-hoster. |
| **Public meal/plan sharing community** | "Discover plans from other users." | Privacy/legal nightmare. Plans are personal medical-adjacent data. Out of scope. | Plans are private to user/group. |
| **Automatic workout detection** | Apple Watch can do this. | Requires wearable integration (out of scope) and would override the simple manual toggle which is the whole point. | Manual toggle. |
| **Detailed micronutrient tracking (vitamins, minerals)** | Cronometer's killer feature. | The MD plan operates at macro level (kcal, protein, carbs, fat). Going micro would require food DB to compute and conflict with plan-driven model. | Macros only. Supplementazione section in MD covers known gaps. |
| **Meal photo journal** | Engagement and "look back" appeal. | Storage cost, moderation burden, irrelevant to adherence tracking. Conflicts with plan-driven discipline. | If user wants memory, take photo with phone camera. Not in app. |
| **Recipe scaling / portion calculator** | Standard in recipe apps. | Plans specify portions. No scaling needed. | Edit MD plan if portions need to change. |

---

## Engagement Patterns (Elegant + Playful Balance)

Critical section per win-requisite. The brief: *"eleganza minimal + tocco giocoso/friendly"* without descending into gamification clichés.

### Approved Patterns

1. **Streak counter — single, prominent, restrained.** "🔥 12 days" or "12 giorni di fila" rendered in elegant typography, not pixel-art badges. One streak, not three. PROJECT.md already specifies streak allenamento.

2. **Weekly adherence ring (Apple-Activity-Rings-inspired).** A single ring showing % giorni con pasti registrati. Closing the ring = subtle haptic-feel CSS animation, no fanfare. Specifically NOT three rings — that's Apple's. Use one ring uniquely styled.

3. **Micro-celebrations on key milestones.**
   - First weight log: confetti for 600ms, then disappears.
   - 7-day streak: subtle sparkle on the streak badge.
   - Hit weekly weigh-in target: gentle gradient bloom on the chart.
   - **Rule:** ≤1 celebration per session, ≤800ms duration, never blocks user.

4. **Lunedì check-in ritual.** Monday landing has slightly different copy ("Buon lunedì, Stefano — è il giorno della pesata!"), an inviting weight-input CTA, optional motivational micro-illustration. Other days: standard view.

5. **Progress visualization that *feels* like progress.** Weight chart that "draws in" with animation on view, projection band that gently pulses when delta is concerning. Recharts + Framer Motion.

6. **Tone-of-voice in copy.** Italian, warm, slightly playful but never silly. "Hai segnato la pesata 💪" not "WOOHOO YOU LOGGED YOUR WEIGHT! +50 XP!". Use 1-2 emoji per screen max, in copy never in UI chrome.

7. **Custom illustrations over stock icons.** PROJECT.md mandates "illustrazioni custom." Empty states ("Nessun pasto ancora segnato oggi") deserve a small warm illustration, not a generic clipart.

8. **Tactile microinteractions.** Every tap has feedback: button presses scale 0.97 with 80ms ease, checkbox checks animate the tick path, swipes reveal actions smoothly. Cumulative effect = "polished" perception.

### Rejected Patterns (Do NOT Build)

- ❌ Badge collection / achievement gallery
- ❌ XP / leveling / rank system
- ❌ Leaderboards (even within family)
- ❌ Daily check-in pop-ups demanding attention
- ❌ "You haven't opened the app in 3 days!" guilt notifications
- ❌ Pseudo-social features (likes, hearts, comments)
- ❌ Cartoon mascot (would clash with elegance)
- ❌ Sound effects / audio cues
- ❌ Animated character coach
- ❌ Treasure-chest reveal animations

---

## Onboarding Flow

Research consensus (UXCam, VWO, Sendbird 2026): **3–5 screens, ≤2 minutes, value-first, ask only what's needed for first useful action.**

For Wellness Buddy specifically (invite-only, plan provided externally):

### Recommended Flow

1. **Invite landing (URL with token).** Headline "Sei stato invitato a Wellness Buddy" + brief value prop ("Il tuo piano nutrizionale, sempre con te").
2. **Account creation.** Email + password + nome (3 fields, that's it). No DOB, no bio, no goals — those come from the plan.
3. **Permission ask: PWA install prompt.** Soft-sell with screenshot ("Installalo come app per usarlo offline"). Skippable.
4. **Permission ask: Notifications (lunedì pesata).** Single permission, with explanation. Skippable. Don't ask permissions before asking for value-creation.
5. **First action: "Carica il tuo piano" OR "Aspetta che l'admin ti carichi il piano".** If admin pre-assigned plan, skip directly to /today. If not, drag-drop MD upload.
6. **/today landing with onboarding tooltips (≤3, dismissible).** "Qui vedi i pasti di oggi", "Segna la pesata cliccando qui", "La spesa si genera automaticamente."

### Anti-patterns

- ❌ Long questionnaire (age, weight, height, goals, dietary restrictions, allergies — all already in MD plan)
- ❌ Tutorial videos
- ❌ Mandatory profile photo
- ❌ Email verification block (use confirmation but allow first session)
- ❌ Forcing notifications permission upfront

---

## Offline Sync Strategy

Already covered in stack but feature-relevant patterns:

- **Optimistic writes:** save to Dexie immediately, fire async to API. User sees "saved" instantly. Pattern from wellally.tech (99.8% sync success across 500K+ users).
- **Sync indicator:** subtle status pip ("synced" / "pending" / "error") in corner of view. Never blocks UI.
- **Conflict resolution:** last-write-wins for personal data (weight, workout); for shopping list checkboxes (multi-user), merge with OR semantics (any user checking = checked).
- **Background sync via Workbox** when network returns. iOS Safari has limitations — fall back to sync-on-foreground.
- **Critical offline views:** /today, /shopping, /week. Charts can be online-only with graceful fallback.

---

## Notification Strategy

Research consensus: **3–4 max per week, value-only, skippable.** For Wellness Buddy:

| Notification | Frequency | Trigger | Content | Opt-in? |
|--------------|-----------|---------|---------|---------|
| Lunedì pesata reminder | Weekly, Mon ~07:30 (configurable) | Scheduled | "Buon lunedì! È il momento della pesata 💪" | YES (asked once during onboarding) |
| Weekly summary (optional, future) | Weekly, Sun evening | Scheduled | "Settimana completata: +0.3kg dalla proiezione, 4 allenamenti su 5" | YES, off by default |
| Plan updated by admin | Event-triggered | Admin uploads new plan | "Stefano ha aggiornato il tuo piano. Vedi le differenze." | YES, on by default |

**That is the entire list.** Resist:
- Daily meal reminders (annoying)
- Streak-warning notifications ("don't lose your streak!")
- Engagement-pull notifications ("you haven't logged in 3 days")
- Promotional content (none — self-hosted, no sales)

---

## Feature Dependencies

```
[MD Plan Upload + Parsing]   ← FOUNDATIONAL (Sprint 1)
    ├──enables──> [/today view]
    ├──enables──> [/week view with variants]
    │              └──enables──> [Variant Selector A/B]
    │                            └──enables──> [Auto Shopping List]
    │                                          └──enables──> [PDF Export]
    ├──enables──> [Macro display per meal]
    └──enables──> [Weight projection (uses plan target curve)]

[Auth + JWT]   ← FOUNDATIONAL (Sprint 1)
    ├──enables──> [User Profile]
    ├──enables──> [Group entity (family)]
    │              └──enables──> [Multi-user Family Sync]
    │                            └──enables──> [Shared Meal Badge]
    └──enables──> [Admin Panel]
                  └──enables──> [Invite Token System]

[Weight Log]   ← FOUNDATIONAL (Sprint 1)
    ├──enables──> [Weight Chart]
    │              └──enables──> [Trend Smoothing]
    │              └──enables──> [Projection Band Overlay]
    └──enables──> [KPI Dashboard delta]

[Workout Log]   ← FOUNDATIONAL (Sprint 1)
    ├──enables──> [Streak Counter]
    └──enables──> [Calendar History View]

[Service Worker + Dexie]   ← FOUNDATIONAL (Sprint 1)
    └──enables──> [Offline /today + /shopping]
                  └──enables──> [Background Sync]

[AI Provider Abstract]   ← FOUNDATIONAL (Sprint 1, NullProvider)
    └──enables──> [Sprint 5 AI features]
                  ├──> [Meal Suggestion]
                  ├──> [Week Analysis]
                  └──> [Chat]

[Web Push Server (VAPID)]   ← Sprint 3
    └──enables──> [Lunedì Reminder Notification]
```

### Critical Path Notes

- **MD Parser is the keystone.** Everything visual flows from parsed plan data. Must be robust to parser variations (PROJECT.md: tollerante a heading variations).
- **Group entity must exist before family sync.** Defer multi-user sync to Sprint 2 (post-foundation).
- **Variant Selector enables Auto Shopping List.** Cannot ship shopping list without variants — they share the same data model.
- **Weight Projection requires both Weight Log AND parsed plan projection data.** Don't ship the chart in Sprint 1 without the band — looks generic.

---

## MVP Definition

### Launch With (v1 = Sprint 1)

Minimum to validate "il valore minimo è 'vedo cosa devo mangiare oggi e segno il peso'" (PROJECT.md Core Value).

- [x] **Auth + invite token** — gating
- [x] **MD plan upload + parser** — foundational
- [x] **/today view with meals (no variants yet)** — core value delivered
- [x] **Weight log + chart (basic, no projection band yet)** — Core Value second pillar
- [x] **Workout log toggle + duration + note** — third pillar
- [x] **PWA installable + offline /today** — platform credibility
- [x] **Light/dark mode + mobile-first 390px** — UI/UX baseline
- [x] **AIProvider abstract + NullProvider** — architectural debt avoided
- [x] **Deploy on Windows Server 2019** — operational viability

### Add After Validation (v1.x = Sprint 2–3)

Triggered by Sprint 1 successful pause-gate.

- [ ] **Variant selector A/B/Pasta** — adherence flexibility
- [ ] **Weekly view + week picker** — beyond daily horizon
- [ ] **Auto-shopping list with checkboxes + categories** — second killer feature
- [ ] **Shopping list PDF export** — practical
- [ ] **Multi-user family sync + shared meal badge** — primary differentiator
- [ ] **Weight projection band on chart** — premium polish
- [ ] **Streak counter + weekly adherence ring** — engagement (elegant)
- [ ] **KPI dashboard cards** — data overview
- [ ] **Lunedì pesata push notification (opt-in)** — ritual
- [ ] **Plan diff view + archive** — admin polish

### Future Consideration (v2+ = Sprint 4–5)

- [ ] **Admin panel polish** (Sprint 4)
- [ ] **AI meal suggestions** (Sprint 5, requires OllamaProvider)
- [ ] **AI weekly analysis** (Sprint 5)
- [ ] **AI chat widget** (Sprint 5, architecture pre-built)
- [ ] **AI shopping tips** (Sprint 5)

### Explicitly Deferred (Post-v2 or Never)

- Wearable integration (post-v1 evaluable per PROJECT.md)
- Recipe library (anti-feature)
- Food DB / barcode scanner (anti-feature)
- Public registration (anti-feature)
- Social features beyond family (anti-feature)

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| /today view with parsed meals | HIGH | LOW | **P1** |
| Weight log + basic chart | HIGH | LOW | **P1** |
| Workout log toggle | HIGH | LOW | **P1** |
| MD plan upload + parser | HIGH | MEDIUM | **P1** |
| Auth + invite token | HIGH | LOW | **P1** |
| PWA installable + offline | HIGH | MEDIUM | **P1** |
| Mobile-first responsive | HIGH | MEDIUM | **P1** |
| Light/dark mode | MEDIUM | LOW | **P1** |
| AI provider abstraction (Null) | MEDIUM | LOW | **P1** |
| Variant selector A/B/Pasta | HIGH | MEDIUM | **P2** |
| Auto-shopping list | HIGH | MEDIUM | **P2** |
| Multi-user family sync | HIGH | HIGH | **P2** |
| Weight projection band | HIGH | MEDIUM | **P2** |
| Shopping list PDF export | MEDIUM | LOW | **P2** |
| Streak + adherence ring | MEDIUM | LOW | **P2** |
| Lunedì push notification | MEDIUM | MEDIUM | **P2** |
| KPI dashboard | MEDIUM | LOW | **P2** |
| Plan diff view | MEDIUM | MEDIUM | **P2** |
| Admin panel polish | MEDIUM | MEDIUM | **P3** |
| AI meal suggestions | MEDIUM | HIGH | **P3** |
| AI chat | MEDIUM | HIGH | **P3** |
| AI week analysis | MEDIUM | HIGH | **P3** |
| Weekly summary notification | LOW | LOW | **P3** |

**Priority key:**
- **P1:** Sprint 1 — must ship for Core Value
- **P2:** Sprint 2–3 — competitive differentiation
- **P3:** Sprint 4–5 — polish + AI

---

## Competitor Feature Analysis

| Feature | MyFitnessPal | Cronometer | Lifesum | Yazio | Lose It! | Macrofactor | AnyList | Plan to Eat | Eat This Much | **Wellness Buddy** |
|---------|---|---|---|---|---|---|---|---|---|---|
| Food database | 20M | Verified | Curated | Mid | Big | None (intake-driven) | N/A | N/A | DB-backed | **NO (anti-feature)** |
| Barcode scanner | Y | Y | Y | Y | Y | N | N | N | N | **NO (anti-feature)** |
| Plan-driven | N | N | Themed plans | N | N | Adaptive macros | N | Recipes | YES | **YES (core)** |
| Variant selection per meal | N | N | N | N | N | N | N | N | "Fit Into Plan" | **YES (A/B/Pasta)** |
| Auto shopping list | N | N | Limited | Basic | N | N | Manual | YES | YES | **YES (from variants)** |
| Shared shopping list | N | N | N | N | N | N | YES (real-time) | YES | YES | **YES (family)** |
| Family/multi-user sync | N | N | N | N | N | N | Lists only | Recipes+lists | N | **YES (meals + shared)** |
| Wearable sync | YES (broad) | YES | YES | YES | YES | YES | N | N | N | **NO (anti-feature)** |
| Weight chart | Y (basic) | Y | Y | Y | Y | Y (advanced) | N | N | N | **YES + projection band** |
| Trend smoothing | N | N | N | N | N | YES | N | N | N | **YES (moving average)** |
| Projection curve | N | N | N | N | N | Forecast | N | N | N | **YES (from MD plan)** |
| Streak | YES | YES | YES | YES | YES | N | N | N | N | **YES (single, elegant)** |
| Badges | YES | Limited | YES | YES | YES | N | N | N | N | **NO (anti-feature)** |
| Leaderboards | YES | N | N | N | N | N | N | N | N | **NO (anti-feature)** |
| AI chat coach | Premium | N | Limited | N | N | N | N | N | N | **YES (Sprint 5)** |
| AI photo recognition | YES | N | N | N | N | N | N | N | N | **NO (anti-feature)** |
| Self-hosted | N | N | N | N | N | N | N | N | N | **YES (differentiator)** |
| Pricing | Freemium | $11/mo | Freemium | $12/mo | Freemium | $12/mo | $9/yr | $5/mo | Freemium | **Free (self-hosted)** |
| MD plan import | N | N | N | N | N | N | N | N | N | **YES (unique)** |

### Key Takeaways

- **Wellness Buddy doesn't compete on database breadth** — that's a different category.
- **Direct comparators are Plan to Eat + Eat This Much** for plan-driven, AnyList for shared lists, Macrofactor for projection chart sophistication.
- **The combination is unique:** plan-driven + family sync + self-hosted + privacy. No competitor has all four.

---

## Risk: Anti-Pattern Drift

The biggest threat to the Core Value is **gradual drift toward food-DB-driven**. Watch for these slippery requests:

1. *"Can I just log a quick snack that's not in the plan?"* → Risk: triggers food DB requirement.  **Resolution:** Free-text note field on day entry. No macros computed.
2. *"Can the app suggest substitutions if I'm out of an ingredient?"* → Risk: triggers ingredient DB. **Resolution:** Sprint 5 AI feature, no DB.
3. *"Can I share my plan with friends?"* → Risk: public meal sharing. **Resolution:** Group expansion, not public.
4. *"Can I scan my groceries to mark them off?"* → Risk: barcode scanner. **Resolution:** Tap to check is faster anyway at 100-user scale.
5. *"Can I see my weight on Apple Watch?"* → Risk: wearable integration. **Resolution:** PWA on iPhone is enough — Add to Home Screen.

**Anti-feature discipline is a recurring decision, not a one-time choice.** Document refusals; defend Core Value.

---

## Sources

### Competitive Analysis (2026)
- [Best Calorie Tracker Apps of 2026: MyFitnessPal vs Cronometer vs Lifesum vs Yazio (YouTube)](https://www.youtube.com/watch?v=2QZlcL7alP0)
- [Cronometer Alternatives: The Definitive 2026 Review — Hoot Fitness](https://www.hootfitness.com/blog/cronometer-alternatives-find-the-best-fit-for-your-tracking-style)
- [9 Best Macrofactor Alternatives — Hoot Fitness](https://www.hootfitness.com/blog/9-best-macrofactor-alternatives-for-smarter-simpler-nutrition-tracking)
- [Detailed MacroFactor vs Cronometer Review — Cal AI](https://www.calai.app/blog/macrofactor-vs-cronometer/)
- [Best Calorie Counter Apps (2026) — Fortune](https://fortune.com/article/best-calorie-counter-apps/)
- [Best Nutrition Apps (2026): Nutritionist Approved — Fortune](https://fortune.com/article/best-nutrition-apps/)

### Plan-Driven vs. Food-Logging
- [Best MyFitnessPal Alternative for Meal Planning in 2026 — MealThinker](https://mealthinker.com/blog/myfitnesspal-alternative)
- [The 2026 Levels Guide to food tracking apps](https://www.levels.com/blog/food-tracking-apps)
- [Eat This Much — The Automatic Meal Planner](https://www.eatthismuch.com/)
- [Prospre — Meal Planner App](https://www.prospre.io/)
- [equ — Personalised Weight Loss Meal Plans](https://joinequ.com/)

### Family / Shared Shopping Lists
- [Best Meal Planning Apps for Families 2026 — Ollie](https://ollie.ai/2025/10/29/best-meal-planning-apps-2025/)
- [Best Shared Grocery List App for Families 2026 — NestSync](https://nestsync.org/blog/best-shared-grocery-list-app)
- [AnyList Grocery Shopping List](https://apps.apple.com/us/app/anylist-grocery-shopping-list/id522167641)
- [Best Family Shopping List App 2026 — Nori](https://heynori.com/blog/best-family-shopping-list-app)
- [Plan to Eat — How families share recipes and lists](https://learn.plantoeat.com/help/organize-your-shopping-list-into-categories)

### Weight Tracking & Projection
- [Happy Scale — Tame the scale](https://happyscale.com/)
- [TrendWeight](https://trendweight.com/)
- [Luuze Trend Weight Tracker](https://apps.apple.com/us/app/luuze-trend-weight-tracker/id1514875885)

### Onboarding & UX
- [12 Apps with Great User Onboarding (2026) — UXCam](https://uxcam.com/blog/10-apps-with-great-user-onboarding/)
- [Ultimate Mobile App Onboarding Guide (2026) — VWO](https://vwo.com/blog/mobile-app-onboarding-guide/)
- [Top 6 onboarding examples — Sendbird](https://sendbird.com/blog/mobile-app-onboarding)
- [UI/UX Case Study: Nutrition Tracking App — Muzli](https://medium.muz.li/ui-ux-case-study-nutrition-tracking-app-5908c8df02c2)

### Gamification & Engagement
- [10 Best Fitness Apps Using Gamification 2026 — Yu-kai Chou](https://yukaichou.com/gamification-analysis/top-10-gamification-in-fitness/)
- [Best Gamified Fitness Apps 2026 Ranked — RazFit](https://razfit.app/gamification-fitness/best-gamified-workout-apps-2026/)
- [Best UX/UI practices for fitness apps — Dataconomy](https://dataconomy.com/2025/11/11/best-ux-ui-practices-for-fitness-apps-retaining-and-re-engaging-users/)
- [Adaptive Micro Rewards in Fitness Apps — the5krunner](https://the5krunner.com/2025/12/09/how-gamification-in-fitness-apps-uses-adaptive-micro-rewards-to-keep-runners-training-longer/)

### Offline / PWA Patterns
- [Build Offline-First PWA with React, Dexie.js & Workbox — wellally.tech](https://www.wellally.tech/blog/build-offline-pwa-react-dexie-workbox)
- [Dexie.js — Build Offline-First Apps](https://dexie.org/)
- [Offline data — web.dev](https://web.dev/learn/pwa/offline-data)

### Notifications
- [How often should your app send push notifications — Medium](https://appsexpert.medium.com/how-often-you-your-app-should-send-push-notifications-dd7f6cfd8038)
- [Harnessing Push Notifications for Fitness Apps — Sudor](https://www.sudorapps.com/blog/harnessing-the-power-of-push-notifications-to-elevate-your-fitness-app-ekyhz)
- [Push Notifications RCT — PMC NCBI](https://pmc.ncbi.nlm.nih.gov/articles/PMC7055755/)

### AI Integration
- [Best AI Meal Planning Apps 2026 — Melio](https://meal-plan.app/en/resources/guides/best-ai-meal-planning-apps/)
- [Top AI-Powered Nutrition Apps to Watch 2025 — Tribe AI](https://www.tribe.ai/applied-ai/ai-nutrition-apps)
- [How to Build an AI Nutritionist App 2026 — Lowcode Agency](https://www.lowcode.agency/blog/build-ai-nutritionist-app)
- [Fud AI — Open Source AI Calorie Tracker](https://www.fud-ai.app/)
- [ChatDiet — LLM-Augmented Framework (arXiv)](https://arxiv.org/html/2403.00781v2)

### Wearable Sync (for anti-feature reasoning)
- [Garmin Adds Food and Nutrition Logging to Connect+ — DC Rainmaker](https://www.dcrainmaker.com/2026/01/garmin-connect-nutrition-logging-connect.html)
- [5 Best Nutrition Apps That Sync With Your Fitness Tracker — Fitia](https://fitia.app/learn/article/best-calorie-tracking-apps-sync-fitness-tracker-2025/)

### Categorization
- [Power of Grocery Shopping Lists with Categories — Listonic](https://listonic.com/f/products-with-categories)

---
*Feature research for: Wellness Buddy self-hosted nutrition PWA*
*Researched: 2026-05-01*
*Confidence: HIGH — multiple 2026 sources, explicit anchoring to PROJECT.md/PROMPT_CONTRACT*
