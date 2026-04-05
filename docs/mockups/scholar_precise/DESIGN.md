```markdown
# Design System Specification: The Academic Precision Framework

## 1. Overview & Creative North Star
**Creative North Star: "The Curated Ledger"**

This design system rejects the "dashboard-mosaic" clutter of typical EdTech platforms. Instead, it adopts the persona of a high-end, digital ledger—precise, authoritative, and intellectually calm. We move beyond the "template" look by prioritizing **Negative Space as a Component** and **Tonal Depth over Structural Lines.**

The experience should feel like a custom-tooled developer environment (think Linear or modern IDEs) but refined for the academic world. We achieve this through:
*   **Intentional Asymmetry:** Off-setting content blocks to guide the eye chronologically.
*   **Typographic Authority:** Large, expressive headers contrasted with microscopic, utilitarian labels.
*   **Operational Silence:** Reducing visual noise by removing borders and "rainbow" status indicators.

---

## 2. Colors & Surface Philosophy

The palette is rooted in a "Warm Mineral" spectrum. It avoids the vibrating purples of SaaS startups in favor of grounded graphites, slates, and a singular, deep teal accent.

### Surface Hierarchy & Nesting (The "No-Line" Rule)
We prohibit the use of 1px solid borders for sectioning. Structural definition is achieved exclusively through **Tonal Layering**.

*   **The Foundation:** Use `background` (#f9f9f8) for the global canvas.
*   **The Content Layer:** Use `surface_container_low` (#f1f4f3) for primary work areas.
*   **The Interactive Layer:** Use `surface_container_lowest` (#ffffff) for active cards or input zones.
*   **The Navigation/Sidebar:** Use `surface_container` (#eaefee) to create a subtle, recessed feel.

### The "Glass & Gradient" Rule
To prevent the UI from feeling "flat" or "cheap," floating elements (modals, popovers) must use **Glassmorphism**:
*   **Token:** `surface_container_lowest` at 85% opacity.
*   **Effect:** `backdrop-blur: 12px`.
*   **CTAs:** Use a subtle linear gradient from `primary` (#306576) to `primary_dim` (#215969) to give buttons a "milled" or "etched" quality rather than a flat plastic look.

---

## 3. Typography
We utilize a dual-typeface system to balance "Academic Expression" with "Operational Utility."

*   **Display & Headlines (Manrope):** This is our "Expressive Sans." It is used for `display-` and `headline-` scales. Its geometric but open nature provides a modern, credible voice.
*   **Interface & Body (Inter):** Our "Workhorse." Used for `title-`, `body-`, and `label-` scales. Inter’s high x-height ensures readability in dense assessment data.

**Hierarchy Strategy:**
*   **The Power of Small Caps:** Use `label-sm` with 5% letter-spacing for secondary metadata to create an "archival" feel.
*   **High Contrast:** Pair a `headline-lg` title with `body-sm` metadata. The wide gap in scale creates a sophisticated, editorial rhythm.

---

## 4. Elevation & Depth

We achieve hierarchy through **Tonal Stacking** rather than traditional drop shadows.

*   **The Layering Principle:** Place a `surface_container_lowest` (#ffffff) card on a `surface_container_low` (#f1f4f3) background. The 3% shift in brightness is enough for the human eye to perceive a physical lift without needing a border.
*   **Ambient Shadows:** If an element must "float" (e.g., a command menu), use a "Natural Light" shadow:
    *   `box-shadow: 0 12px 40px rgba(44, 52, 51, 0.06);` (using `on_surface` for the shadow tint).
*   **The Ghost Border:** For accessibility in high-density tables, use a `outline_variant` (#abb4b3) at **15% opacity**. It should be felt, not seen.

---

## 5. Components

### Buttons
*   **Primary:** Gradient of `primary` to `primary_dim`. `md` (0.375rem) roundedness. No border.
*   **Secondary:** `surface_container_highest` background with `on_surface` text.
*   **Tertiary (Ghost):** No background. `on_surface_variant` text. High-contrast `on_surface` on hover.

### Assessment Inputs (Text Fields)
*   **Unfocused:** `surface_container_high` background, no border.
*   **Focused:** `surface_container_lowest` background, 1px `primary` border.
*   **Error:** Use `error` (#9f403d) text only; avoid "red boxes" unless the entire field is invalid.

### Chips & Badges
*   **Status:** Avoid "Traffic Light" colors. Use `secondary_container` for "In Progress" and `primary_container` for "Completed." Use `error_container` only for critical failures.
*   **Shape:** `full` (9999px) pill shape to contrast with the `md` corners of the rest of the UI.

### Data Lists & Cards
*   **The "No Divider" Rule:** Forbid 1px lines between list items. Use **Vertical Spacing** (16px–24px) or a 2% color shift on hover (`surface_dim`) to define rows.
*   **The "Instructor-First" View:** Maximize information density by using `label-md` for secondary student data, ensuring the "Grade" or "Assessment" remains the focal `title-md`.

### Professional Tooling: The "Command Bar"
*   Incorporate a floating `surface_container_lowest` bar at the bottom-center of the screen for quick actions (e.g., "Publish All," "Regrade"), using Glassmorphism and the Ambient Shadow spec.

---

## 6. Do's and Don'ts

### Do:
*   **Do** use asymmetrical margins. If a container is 800px wide, center it but give it a larger bottom margin to create "breathing room" for the next section.
*   **Do** use `primary` sparingly. It is a "surgical" accent, meant to draw the eye to the most important operational action.
*   **Do** use `surface_container_highest` for "Empty States" to make them feel like a natural part of the page rather than a missing piece.

### Don't:
*   **Don't** use pure black (#000000). Always use `on_surface` (#2c3433) for text to maintain the "warm graphite" feel.
*   **Don't** use cards-inside-cards-inside-cards. Use background color shifts to define nesting levels.
*   **Don't** use standard "Success Green." Use the `primary` (teal-blue) for success to maintain the "calm, academic" tone. Red is the only allowed "alert" color.
*   **Don't** use heavy shadows. If you think it needs a shadow, try giving it a lighter background color first.