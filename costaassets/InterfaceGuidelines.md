# Interface guidelines

What was learned building **CostaGuestForms**, written down so the next tool of
its kind does not have to learn it again.

This is not a style guide for a website. It is the interface of a tool used by
one person, standing up, with a member of the public in front of them, on a
machine they did not choose, to produce a document that is legally binding. Most
of what follows exists because that sentence is true.

The companion document `SchemaDiProgetto.docx` covers the method: how the
project was framed, verified and handed over. This one covers only what the
operator sees and touches.

---

## 1. Three facts that decide everything else

**There is someone waiting.** The guest is standing at the counter. Every second
of hesitation is a second of silence between two people. This rules out anything
that has to be learned, looked up, or read twice.

**A mistake has a victim.** The document is one person's declaration. Sending it
to the wrong address is not a failed delivery. It is a stranger receiving
somebody's name, cabin and telephone number. Confirmations are not friction
here; they are the point.

**The tool must never be the reason work stops.** A reception desk cannot wait
for a service to come back. Every path that can fail needs a path that cannot:
if sending fails, saving and printing still work; if the signature pad is
absent, the screen takes the signature; if the signature cannot be taken at all,
the printed copy gets signed by pen.

---

## 2. Principles

### Say what happened and what to do about it

An error that says "operation failed" makes the operator guess whether the fix
is theirs. Every failure is classified into what the person in front of the
screen should now do:

| The operator can fix it, now | Somebody else has to fix it |
|---|---|
| the address is wrong → correct it and retry | the sending program is down |
| the document is too heavy → remove a photo | this workstation is not authorised |
| | the server refused the message |

Each case gets a **title** naming what happened, **one line** saying what to do,
and the technical text folded away underneath for whoever will read it later.
Three sentences, not a paragraph.

### Never hide a function to indicate a problem

An earlier version removed the send button when the bridge was not configured.
At the desk this reads as "the tool is broken and I don't know why". The button
now always appears, and pressing it produces the reason. **A control that
disappears cannot explain itself.**

### Text under a field is glanced at, not read

`"The form is right. Whether the mailbox exists cannot be known from here: read
it back to the guest."` became `"Format correct."` Two or three words. The long
version was true and useless: nobody reads a sentence while typing an address
with someone watching.

Long explanations belong in the information panel, where somebody has chosen to
go and read.

### State the limit rather than hiding it

The tool reports "handed over to the shipboard server", not "sent to the guest",
because the second is not known. Where a residual risk exists it is written on
the screen and in the documentation, not smoothed over. An interface that
overstates what it knows is worse than one that admits the boundary.

### One primary action per screen

Exactly one yellow button. Everything else is neutral. If two actions look
equally important, the screen has not decided what it is for.

---

## 3. Visual system

### Colour

Institutional colours, and a rule about where they may appear:

```
--brand   #0071A3   bar, links, focus rings, selected state on light ground
--sel     #F9B000   the one primary action, and selection
--ink     #0A2A38   body text, never the brand blue, which reads as a link
--muted   #5F7079   secondary text
--faint   #94A6AE   captions, disabled
```

Status colours always come as a triple (background, border, ink) so a notice
is readable in both themes:

```
warn   #FFF8E8 / #F7DFA6 / #6B4E00
bad    #FCF2F0 / #EFCFC8 / #B3402E
good   #F1F9F5 / #C9E5D6 / #1F7A54
```

**Text on the accent colour is dark, never white.** White on `#F9B000` gives a
contrast ratio near 2:1, below every legibility threshold; the dark navy gives
about 8:1. This is the single most common way a brand palette produces an
unreadable button.

### Two themes, one set of tokens

Every colour is a custom property defined once on `:root` and redefined for the
dark theme. No component knows which theme is active. Adding a colour outside
the token set means it will be wrong in one of the two, and nobody will notice
until a night shift.

### Type

One family (Poppins), subset to the characters actually used, embedded. A
monospace family for anything that must be read character by character: document
codes, addresses, file names, versions. **If a value can be mistyped, it is
monospaced** — that is what the distinction is for, not decoration.

### Shape

One radius token. One border colour, one lighter one for internal divisions, one
darker for hover. Shadows only where something genuinely floats above the page:
panels and the bar. Everything else is separated by a line.

---

## 4. Layout

### The shell does not move

```
bar          fixed
progress     fixed
content      the only thing that scrolls
actions      fixed
```

The operator's eyes should not have to find the buttons again after scrolling.
Two consequences that are easy to miss:

- the scrolling area needs `overscroll-behavior: contain`, or reaching the end
  passes the scroll to the page and the whole interface appears to move — which
  is exactly what a user reports as "everything scrolls";
- hiding a shell row (a mode without the progress bar, say) means changing the
  grid rows at the same time, or the content lands in the wrong row and the page
  collapses upwards.

### Line length is a constraint, not a leftover

Content is capped at 680 px, or 820 px when a side panel is closed — not the
full screen. A 1600 px-wide form is harder to fill in than a narrow one, because
the eye loses the line between label and field.

### The live preview

Where a tool produces a document, showing the document as it is built removes
an entire class of error: what you see is what will be signed. Two rules earned
the hard way:

- it must be closable, because on long forms it is in the way — and while
  closed the document must not be built at all, since that is the most
  expensive work on the page, and rebuilding it for a panel nobody is looking at
  is precisely what closing it was meant to avoid;
- reopening it must redraw immediately, with whatever was typed meanwhile.

---

## 5. Components

### The step path

Four steps, always the same four, always in the same order, with the current one
marked. The number of steps is fixed: a path that grows and shrinks cannot be
learned.

### Fields

Label above, control, hint below. The hint is where the field talks: empty it
invites, wrong it says what is wrong, right it confirms in two words. It changes
**as you type**.

The critical implementation rule: **updating a hint must never re-render the
form**. Rebuilding the DOM while someone is typing moves the caret and loses the
word. In this project that mistake was made four times, in four different
places, and each time it was found by a person typing rather than by a test.
Update the specific element; re-render only when the shape of the screen
changes.

### Blocking and what is missing

A disabled "Next" that does not say what it is waiting for is the most
frustrating control at a counter: you press it, nothing happens, and twenty
fields are equally suspect.

Beside the button, a list of what is missing, **each entry a target**: tapping
it scrolls to that field and focuses it. The field flashes once and returns to
normal — a colour that stays on an empty field looks like an error, and it is
not one; the user simply has not got there yet.

Do not list what is missing when it is obvious. On a screen showing five large
cards, "missing: form" adds nothing to what the eye already sees.

### Notices

Four kinds, and the kind carries meaning:

```
plain   a fact
warn    something to check before continuing
bad     it did not work, and here is what to do
good    it worked
```

Never two at once. Never a `bad` for something the operator cannot act on
without also saying who can.

### Panels

Settings that are set once belong in a centred modal, over a scrim: it is a
decision, and it deserves the screen. Reference material (help, credits, the changelog) belongs in a side drawer:
it accompanies the work rather than interrupting it.

Both scroll internally, with the header and footer fixed, and both must be
usable on a short screen. Verify the panel body scrolls and the page does not.

### Collapsible sections

A reference panel is a wall of text until it is divided. Use native `<details>`:
the browser opens and closes it, and keyboard and screen readers already know
how. One section open — the one somebody opening the panel needs first.

Every section must earn its place. "This copy" listing version, build date and a
service address was three facts nobody needed as a section; they became one line
of small monospace at the foot of the panel.

### Drop zones

Where a file is the input, the dashed border says "leave something here", which
is a different statement from "choose". Dropping should go straight to the work,
with the file already loaded — not to a screen that then asks for the file.

Always call `preventDefault` on `dragover`. Without it the browser leaves the
page and opens the dropped file, discarding everything the operator had typed.

### Full-screen signature

When a device is handed to a member of the public, the screen should contain one
thing. Not only for comfort: **no other control should be reachable** while the
device is in the hands of someone who does not know the tool. Verify this by
asking which element responds to a touch at the coordinates of the controls
that should be covered — visibility checks will say a buried button is visible.

Include what is being signed, by whom, at the top. Include the baseline with the
cross, as on paper: it tells the signer where, without anyone having to say it.

Offer "cancel" as well as "done", and make cancel restore the previous state
exactly.

---

## 6. Touch

### Recognise the device, do not ask

`(pointer: coarse)` describes how the screen is touched, which is the right
question: a 27-inch touch monitor should behave like a tablet, a tablet with a
mouse attached should not. Screen width is the wrong question and always was.

Recognise it **on every open, storing nothing**. Storing the answer on first run
means the same file copied from a desk to a tablet carries the wrong answer with
it. Keep a manual override for the cases the test gets wrong, such as a laptop with
a touch screen that reports coarse while having a mouse; and when the override
is active, say so, rather than letting the operator believe the device was
recognised.

### Beyond bigger buttons

Larger targets are the least of it. What actually changes:

| | |
|---|---|
| Targets | 52 px, not the 44 px minimum: the operator has someone waiting and cannot repeat gestures |
| Field text | **16 px minimum**, or mobile browsers zoom the page on focus and leave it zoomed |
| Columns | one in portrait, two in landscape; the side preview closes in portrait, where it cannot fit |
| Attachments | open the camera, not the file browser: the damage is on the counter |
| Long content | collapsible, so what comes after it is reachable without scrolling back |
| Absent hardware | remove its whole interface. A status dot and a "connect" button for a device that cannot exist on this machine is noise that describes nothing |

### Capturing a signature on glass

This deserves its own section, because it is where the most instructive bug of
the project lived.

**A signature is not one stroke.** People lift the pen between letters. The
first implementation committed the signature on every `pointerup`: it captured
the image, re-rendered the card, and rebuilt the canvas, while the pen was
already coming back down. The next stroke landed on a canvas that had just been
created, or was lost. At the desk this reads as "the signature field doesn't
work", and it is completely invisible to a test that draws one stroke.

The rules:

1. **Finish on idle, not on lift.** Half a second of no pen is the end of a
   signature. Any lift shorter than that is part of it.
2. **Committing must not re-render.** Update the status text and the clear
   button; leave the canvas alone. The pen may still be resting on it.
3. **`touch-action: none` on the canvas**, or the browser treats the stroke as a
   scroll gesture and no move events arrive.
4. **Reject the palm.** After a pen has been seen, ignore touch contacts for a
   couple of seconds: resting a hand on the glass while signing is normal.
5. **Capture the pointer**, and also listen on the window, in case capture
   fails and the pen is lifted outside the box.
6. **Remove the previous window listener** when rebinding. A day at the counter
   otherwise accumulates dozens, all attached to canvases that no longer exist.

---

## 7. Accessibility, treated as ordinary work

- every icon-only control has an `aria-label` and a `title`, both from the same
  string as the tooltip;
- state is expressed with `aria-pressed` on toggles and real `<button>`
  elements, never a `div` with a click handler;
- the focus ring is visible and never removed: on a shared machine the keyboard
  is often faster than the mouse;
- icons are drawn as SVG, not emoji: emoji arrive in colour and with different
  metrics on every system, and it shows in a toolbar;
- colour is never the only carrier of meaning: a status has a colour, a word,
  and usually a shape.

---

## 8. Language

Both languages are complete or the tool is broken in one of them. A string
present in only one appears as `undefined` to whoever works in the other, and
the person who notices is usually the customer.

**Verify it automatically at build time.** A dozen lines that compare the two
key sets caught three omissions in a single working day. Any check that is
cheap and catches a class of error belongs in the build, not in a habit.

Write in the second person, plainly, in the operator's vocabulary. No
"an error occurred". No "please". Say what happened and what to do.

---

## 9. Verification

What matters is not that the interface works, but that it is seen to fail when
it is broken.

- **Drive the real thing.** Open the built file in a real browser and click what
  a person clicks. Screenshots are for judging composition; assertions are for
  behaviour.
- **Break every new guard on purpose** and watch the test fail before keeping
  it. A check that has never been seen to fail is not a check. In this project
  a first attempt at breaking one broke nothing: the guard was untested and
  looked fine.
- **Check what responds, not what is visible.** `elementFromPoint` at the centre
  of a control answers "can this be clicked", which is the real question. A
  panel that is under its own scrim, or a button buried beneath an overlay, both
  pass a visibility check.
- **Two things about test mechanics** that cost hours: pointer coordinates are
  viewport coordinates, so scroll the target into view before drawing on it; and
  accented characters may be composed or decomposed: `sé` written two ways
  looks identical and never matches. Normalise before comparing.

---

## 10. The short version

If only one page of this survives:

1. One primary action per screen. Everything else is quiet.
2. Errors say what to do, not that something failed.
3. Nothing disappears to signal a problem.
4. Never re-render while someone is typing.
5. Recognise the device; do not ask, and do not remember the answer.
6. A signature ends when the pen rests, not when it lifts.
7. Both languages, checked by the build.
8. Break each guard once, on purpose, before trusting it.
