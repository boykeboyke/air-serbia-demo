# Air Serbia x PolyAI - meeting demo script (45 min)

_Running order for a prospect meeting. The page is the prop; the bilingual agent is the show. Open on
Air Serbia's own contact centre, not PolyAI. No em dashes when you speak the scripted lines._

---

## Before the meeting
- [ ] Demo running (locally `http://localhost:3000`, or the Railway URL).
- [ ] Flight-status live key set (`AERODATABOX_KEY`) so the lookup reads "live"; otherwise it falls
      back to sample data and you say so.
- [ ] Studio agent built, tested, and (if showing the call) the web-call widget published and wired.
- [ ] Page open on the Hero. Know the toggle: EN for the room, SR to show "built for them".

## 0-5 min - Their contact centre first
"Air Serbia carried 4.57 million passengers last year across 103 destinations. The line answers from
six in the morning to eleven at night, in Serbian and English. So two questions: what happens to the
calls outside those hours, and what does it cost to answer the same four questions a few thousand
times a week?" Let them talk. Echo their numbers back.

## 5-8 min - Walk the site (90 seconds, then put it aside)
- Hero, in **their brand**: "Every caller answered, in their own language."
- Hit the **SR toggle** once: the whole page flips to Serbian latin. "We built this for you, in your
  language, before we met."
- Point at the **live flight-status box** in the hero. Type `JU324`, press Check. A real lookup
  returns. "That is a live external call, not a mock. The agent does the same on a call."

## 8-30 min - The agent is the show
Switch to the **Your Agent** tab (or place the call).
1. **Greet it in Serbian.** "Zdravo, ovde Milan Petrović, zovem zbog leta JU324." It switches to
   Serbian, greets Milan by name, and reads his Paris booking back. This is the wow: it knew him
   before he asked.
2. **Switch to English mid-call.** "Actually, can I add a bag?" It follows into English, adds the
   bag, states 35 EUR from the record, confirms with a reference.
3. **Live status.** "What's the status of JU324?" It runs the live lookup and reads it back.
4. **Change the flight.** Move JU324 to a later date; it confirms with a reference number.
5. **Safety beat (optional, brief).** Show it transferring on a genuine emergency, instantly. "That
   path is non-negotiable and frozen."

## 30-37 min - Honesty closes (Demo Assumptions tab)
Walk the "Real today / Modelled" split. "The agent, the reasoning, the bilingual switch and the
flight lookup are real. The passenger record and the writes are modelled, so we built this without
touching your systems or waiting on a security review. That is how fast a pilot moves."

## 37-43 min - Proof + rollout
- **Proof tab.** Be honest: no published airline study yet. Lean on PG&E (bilingual, 67% containment,
  35,000 hours saved), Hopper (travel), and UniCredit / Zagrebačka banka (Balkans, multilingual
  routing, +14 NPS). Numbers are quoted verbatim from published stories.
- **Rollout tab.** Listen to the line, wire the flows, go live on a slice. 8 to 12 weeks.

## 43-45 min - The next step
"Come onto the platform. We give your team hands-on Studio access, build a flow live together, and
wire your first real connector." Book the working session. The agent they called is real and waiting.

---

## Pricing card (verbal only - never numbers on the page)
If pressed on price: "Priced on the conversations the agent contains, discounted by volume, plus an
outcome-based component tied to a specific use case. We model your real volumes together." Do not
quote a rate. (Real rates are confidential and stay in the meeting.)

## Competitor card (verbal only)
PolyAI has named travel/hospitality logos (Marriott, Hopper) but no published airline study yet. If
asked about an incumbent or a rival vendor, keep it factual and steer back to the live agent and the
honesty of the build. Do not put competitive detail on the public page.
