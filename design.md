# Design Guide

Companion to `styling-examples.md`. Read this before making visual decisions for a Molnify app.

Molnify apps are built by AI. Without deliberate design decisions, every app converges on the same generic look: teal accents on dark headers, centered text, uniform card grids, Inter or Roboto. This guide provides the principles to make each app feel intentionally designed for its purpose.

---

## Before You Style

Before writing any CSS, answer three questions:

1. **What is this app for, and who uses it?** A financial calculator for accountants needs calm authority. A sales demo needs energy. A factory floor tool needs density and clarity at arm's length.

2. **What is the aesthetic direction?** State it in 2-3 specific words. Not "clean and modern" - that's the absence of direction. Examples: *warm industrial*, *editorial*, *soft minimal*, *dense utilitarian*, *refined corporate*, *playful bold*. Every subsequent choice must serve this direction.

3. **What's the one thing someone will remember?** A distinctive color, an unusual font pairing, a bold layout choice. If nothing in the design is memorable, it needs a point of view.

---

## AI Design Tells

AI-generated interfaces converge on the same patterns. They signal "no designer was involved." Avoid these defaults:

### Typography Tells
- Inter, Roboto, Open Sans, or system fonts as the primary font
- Monospace used as shorthand for "technical" aesthetic
- All text centered

### Color Tells
- Cyan/teal on dark background (the "AI dashboard" palette)
- Purple-to-blue gradients
- Neon accents on dark backgrounds
- Pure black (`#000`) and pure white (`#fff`) everywhere
- Gradient text on headings or metrics

### Layout Tells
- Everything in cards with identical padding and rounded corners
- Identical card grid: icon + heading + text, repeated 3-6 times
- Same spacing everywhere - no rhythm, no grouping
- Everything centered with no asymmetry

### Detail Tells
- Glassmorphism (blur, glow borders) used decoratively
- Uniform drop shadows on every element
- Dark mode by default with glowing accents

### The Test
After styling, ask: "If someone said AI made this, would they immediately believe it?" If yes, identify which tells are present and replace them with intentional choices.

---

## Typography

Molnify provides `HeaderFont` and `BodyFont` metadata, both loading from Google Fonts. These two choices set the typographic personality of the entire app.

### Choosing Fonts

**Match the font to the screen.** Molnify apps render on screen, not print. Favor fonts designed for screen readability:
- **Sans-serif** generally reads better at body sizes on screen
- **Serif** works well for headers at larger sizes, and for apps going for editorial or refined aesthetics
- Avoid fonts designed for print (Garamond, Bodoni) at body sizes on screen

**Choose fonts with character.** The font should reflect the app's purpose and personality - not just be legible. A calculation tool for engineers feels different from a customer-facing quote builder.

**Avoid the defaults.** Inter, Roboto, Open Sans, and Arial are fine fonts, but they signal that no typographic decision was made. They're the equivalent of Times New Roman in a Word document.

### Pairing Rules

- **Maximum two font families** - one for headers, one for body
- **Pair serif + sans-serif**, not two serifs or two sans-serifs
- **Match letter structures** for harmony, or use extreme contrast. The awkward middle ground - two fonts that are somewhat similar - always fails. Compare the lowercase `n`: humanist fonts curve organically from the stem, geometric fonts have a symmetrical arch
- **Same designer shortcut**: fonts by the same designer pair well. Gill Sans + Joanna (both by Eric Gill) work because they share the same design philosophy

### Body Text Settings (via CSS metadata)

- Line-height 1.2-1.4em for body copy
- Left-align body text - ragged right is more readable than justified on screen
- Don't center body text. Centered paragraphs are harder to scan. Reserve centering for short, prominent elements like titles

---

## Color

### Build a Palette, Don't Pick Colors

Start from the desired mood and audience, then use color wheel relationships:

| Mood | Approach |
|------|----------|
| Calm, focused | Monochromatic (one hue, varied tints/shades) or analogous (3 adjacent hues) |
| Energetic, active | Complementary (opposite hues) or triadic (3 evenly spaced) |
| Sophisticated, muted | Low saturation with one strong accent |
| Trustworthy, professional | Cool blues/greens; avoid red in analytical contexts |
| Natural, earthy | Warm unsaturated tones - browns, greens, muted oranges |

### Color Principles

- **One dominant color, sharp accents.** A dominant color with one or two accent colors outperforms an evenly-distributed palette.
- **Warm advances, cool recedes.** Use warmer colors for elements that should draw attention; cooler colors for supporting elements.
- **Hue-shifted shadows, not black.** Shadows that skew cooler and highlights that skew warmer create richer depth than pure black/white overlays.
- **Functional colors follow convention.** Red = error/urgency. Green = success. Blue = links. Don't reverse these.
- **Red impairs analytical thinking.** In calculation-heavy apps, avoid red as a dominant color. It overloads the prefrontal cortex and reduces rational decision-making. Reserve it for errors and urgent alerts.
- **Test contrast.** Light text on light backgrounds and dark text on dark backgrounds are both invisible - if you lighten a default dark background, override its text color too.

### Molnify-Specific Defaults to Override

Molnify's defaults (teal output boxes/buttons, dark headers) are functional but generic - override them with the color metadata properties to match your aesthetic direction. For a cohesive palette, drive everything from CSS variables in the `CSS` metadata:

```css
:root {
  --primary: #2d5a7b;
  --primary-dark: #1a3a4a;
  --accent: #d4a574;
  --surface: #f8f6f3;
  --text: #2a2a2a;
  --text-muted: #6b7280;
}
```

---

## Visual Hierarchy

Establish importance through five factors, applied in order of subtlety. Use the minimum number needed - don't change everything at once.

### The Hierarchy of Hierarchy

1. **White space** - the most powerful and most overlooked. More space around an element signals importance. Less space between elements signals they're related. Use proportional spacing: tight within groups, generous between groups.

2. **Weight** - bold for primary elements, regular for secondary. If body text is bold, increase line-height to lighten the visual texture.

3. **Size** - differences must be meaningful. A 2px difference (13px vs 15px) is imperceptible. Use a proportional type scale and skip steps: 9, 12, 16, 21, 28 (3:4 ratio). Jump from 12 to 21 for real contrast, not 12 to 14.

4. **Color** - warm/dark colors for primary elements, cool/light for secondary. Temperature adds dimension beyond just size and weight.

5. **Ornamentation** - borders, backgrounds, icons. Use sparingly and only when the above factors are insufficient. Every decorative element competes with content.

### Tables

Remove unnecessary borders. Alignment and white space separate rows and columns more cleanly than rule lines on every cell. If you need help tracking across wide rows, use subtle alternating row backgrounds.

### The Squint Test

Blur your eyes (or step back from the screen). The dominant element should still be the first thing visible. If everything blurs into equal weight, the hierarchy is flat.

---

## Composition

### Dominance

Every layout needs one dominant element - the visual anchor that draws the eye first. In a Molnify app this might be a key output metric, a chart, or the app header. Make it dominant through size, color, or surrounding white space.

Without a dominant element, everything competes equally and nothing gets attention.

### Depth

Create foreground/background relationships. Not everything should sit on the same visual plane:
- Shadows of varying intensity (not identical on every card)
- Color intensity - bolder, more saturated elements feel closer
- Size - larger elements advance, smaller ones recede

### Direction

Guide the eye through the layout. Western users scan left-to-right, top-to-bottom. Place the most important content where the eye enters (top-left). Use alignment, progressive sizing, or color to create a deliberate reading path.

### Similarity

Repeat visual motifs for cohesion. If buttons are rounded, make panels rounded. If the accent color is warm amber, echo it in output box backgrounds and chart colors. A consistent shape language makes disparate elements feel unified.

---

## Proportions

Use proportional relationships instead of arbitrary pixel values.

### Proportional Systems

Pick a ratio and derive sizes from it:

| Ratio | Character | Use for |
|-------|-----------|---------|
| 3:4 | Compact, practical | Most apps - type scales, spacing, card proportions |
| 2:3 | Balanced, slightly more spacious | Dashboard layouts, content-heavy apps |
| Golden (1:1.618) | Elegant, open | Premium/luxury-feel apps |

### Type Scale (3:4 ratio)

Start with your body size and multiply by 0.75 repeatedly for smaller sizes, divide by 0.75 for larger:

`9 → 12 → 16 → 21 → 28 → 37 → 50`

Skip steps for meaningful contrast. A heading at 21px with body at 16px is subtle. A heading at 28px with body at 16px makes a statement.

### Spacing

Derive spacing from the same proportional system. If your base spacing is 16px:
- Tight (within groups): 8px
- Standard: 16px
- Generous (between sections): 32px or 48px

Proportional spacing creates rhythm. Arbitrary spacing creates unease.

---

## Design Review Checklist

Before considering an app's visual design complete:

- [ ] Aesthetic direction is stated in 2-3 words and every choice serves it
- [ ] Primary font is not Inter, Roboto, Open Sans, or Arial
- [ ] Color palette follows a color wheel relationship, not random picks or AI defaults
- [ ] One element is clearly dominant - the eye knows where to go first
- [ ] Layout includes variety, not identical cards repeated uniformly
- [ ] White space creates grouping: tight within related elements, generous between sections
- [ ] Type sizes differ by meaningful amounts (not 1-2px increments)
- [ ] Text color has sufficient contrast against its background
- [ ] Numbers are shown at a readable scale and precision - no excessive decimals, no 6-7 digit axis labels (scale to tSEK/MSEK/k/M with a unit in the title)
- [ ] The design wouldn't immediately be believed if someone said "AI made this"
- [ ] At least one choice is distinctive enough that a generic AI wouldn't produce it
