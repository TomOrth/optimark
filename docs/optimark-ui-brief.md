# Optimark UI Generation Brief

## Purpose
Use this document with AI UI generation tools such as Stitch to create candidate product UI concepts for Optimark.

This brief is intentionally design-oriented. It should be used alongside the broader product and architecture spec, but it is optimized for screen generation rather than backend planning.

Related docs:
- [Overall AI spec](./optimark-ai-spec.md)
- [ADR index](./adr/README.md)

## Product Summary
Optimark is an instructor-first assessment platform for courses, starting with coding assignments. Instructors create assignments, students submit code, the system runs autograding asynchronously, and instructors or TAs review, override, and release grades.

The initial product should feel:
- academic, credible, and operational
- modern and calm rather than playful
- dense enough for real work, but never cluttered
- more like Linear, Notion Calendar, or modern developer tooling than a generic LMS

## Visual Thesis
Design Optimark as a precise academic operations product: clean typography, restrained color, strong spacing, and a sense of trust and control. The UI should feel like serious assessment software for technical courses, with one clear accent color and a calm neutral system.

## Content Plan
- Primary workspace: course, assignment, submission, or gradebook content
- Secondary context: status, filters, metadata, due dates, run state, rubric summary
- Detail layer: submission history, artifacts, logs, comments, grading events
- Action layer: publish, submit, rerun, review, override, release

## Interaction Thesis
- Use subtle progressive disclosure instead of crowded default views.
- Use motion sparingly for state changes: status transitions, drawer reveals, and route changes.
- Make async grading feel legible with strong status treatment and timeline-like feedback.

## Design Direction
### Overall look
- Product UI, not marketing site
- Minimal chrome
- Layout-driven, not card-grid-driven
- Dense but readable tables and panels
- Strong typography hierarchy
- Calm surfaces with sparse use of borders

### Recommended palette
- Neutrals: warm white, graphite, slate
- Accent: deep blue or blue-green
- Success: green
- Warning: amber
- Error: muted red

Avoid:
- purple-heavy startup palettes
- rainbow status systems
- thick borders around every region
- dashboard-card mosaics

### Typography
- Use one expressive but disciplined sans-serif for UI and one optional secondary serif or monospace accent only if it adds purpose.
- Prioritize strong headings, compact metadata, and highly readable tables/forms.
- Use monospace selectively for code filenames, status ids, and technical submission artifacts.

## Product Personality
- Instructor-facing surfaces should feel powerful and structured.
- Student-facing surfaces should feel clear, lower-stress, and progress-oriented.
- TA review surfaces should feel analytical and efficient.
- Nothing should feel childish, gamified, or LMS-generic.

## Core Information Architecture
The v1 application should organize around these top-level areas:
- Courses
- Assignments
- Submissions
- Review
- Gradebook
- Settings or course configuration

Recommended primary navigation for staff:
- Global sidebar
- Course switcher near top-left
- Main workspace in center
- Context panel on right when needed

Recommended primary navigation for students:
- Simpler left navigation or top tabs
- Fewer administrative affordances
- Strong emphasis on due dates, submission state, and feedback

## Primary User Flows
### Instructor flow
1. Open course dashboard
2. View assignments and grading status
3. Create or edit coding assignment
4. Publish assignment
5. Monitor incoming submissions
6. Review autograde outcomes
7. Override or annotate as needed
8. Release grades

### Student flow
1. Open course
2. View assignment detail
3. Review instructions and starter materials
4. Upload submission
5. Watch grading state
6. View released result and feedback

### TA flow
1. Open review queue or assignment submissions
2. Inspect autograde result
3. Review code and artifacts
4. Apply rubric/comment adjustments
5. Save grading changes

## Screen List for v1 Concepts
Generate concepts for these screens first:
1. Instructor course dashboard
2. Assignment builder for a coding assignment
3. Student assignment detail and submission screen
4. Submission processing/status screen
5. Instructor or TA submission review screen
6. Gradebook screen

If the tool can generate more, also include:
7. Course assignments list
8. Student results view

## Screen-by-Screen Brief
### 1. Instructor Course Dashboard
Purpose:
- Give instructors a fast overview of a course and its assessment activity.

Primary content:
- course title and term
- assignment list
- counts for drafts, published assignments, pending review, and completed grading
- recent submission activity
- grading queue snapshot

Primary actions:
- create assignment
- open assignment
- open gradebook

Layout guidance:
- left sidebar for navigation
- central workspace with assignment table or structured list
- top row with course title, term, and primary actions
- one compact activity/status region, not a wall of KPIs

Tone:
- operational
- high signal
- no hero banner

### 2. Assignment Builder for Coding Assignment
Purpose:
- Let instructors create and edit a Python-first coding assignment without overwhelming them.

Primary content:
- assignment title
- description/instructions
- due date
- submission limit
- starter files or starter artifact section
- language indicator
- publish state

Primary actions:
- save draft
- publish
- unpublish or archive later

Layout guidance:
- form-first workspace
- left column for main fields
- right-side inspector for metadata, publish state, and quick summary
- use sections instead of cards when possible

Tone:
- calm and structured
- resembles a serious internal tool

### 3. Student Assignment Detail and Submission Screen
Purpose:
- Help students understand the assignment, what to submit, and their current status.

Primary content:
- assignment title
- due date and late-state messaging
- instructions
- starter materials
- submission requirements
- prior submissions

Primary actions:
- upload files or archive
- submit
- resubmit if allowed

Layout guidance:
- instructions dominate the main column
- submission panel remains obvious and always actionable
- status and due-date context visible without scrolling far
- student stress should be reduced through clarity, not decorative reassurance

Tone:
- clean
- readable
- direct

### 4. Submission Processing / Status Screen
Purpose:
- Make asynchronous grading legible and trustworthy.

Primary content:
- submission timestamp
- current state: queued, running, completed, failed
- autograde run timeline or status progression
- logs/artifacts summary
- score preview if appropriate

Primary actions:
- refresh or auto-updating status behavior
- view artifacts
- open final result when available

Layout guidance:
- strong central status treatment
- timeline or progressive state indicator
- supporting diagnostic details below
- avoid noisy system-monitor aesthetics

Tone:
- reassuring through precision
- technical but not intimidating

### 5. Instructor / TA Submission Review Screen
Purpose:
- Combine autograde output, submission artifacts, and manual review tools in one efficient workspace.

Primary content:
- student identity
- submission metadata
- autograde summary
- rubric or scoring controls
- comments/feedback
- artifact or code viewer region

Primary actions:
- adjust score
- apply rubric
- leave comment
- mark review complete
- release or queue for release depending on workflow

Layout guidance:
- main workspace for artifact/code/log review
- right-side inspector for rubric and grading controls
- top metadata row for student, assignment, status
- this screen may use panels, but not a grid of unrelated cards

Tone:
- analytical
- high-efficiency
- reviewer-focused

### 6. Gradebook Screen
Purpose:
- Let instructors and TAs scan grading progress and student performance quickly.

Primary content:
- student rows
- assignment columns or assignment-scoped row summaries
- released state
- missing/incomplete indicators
- review-needed indicators

Primary actions:
- filter
- sort
- open student submission
- open assignment submissions

Layout guidance:
- table-first design
- sticky headers where appropriate
- dense but readable
- prioritize scanability over decorative presentation

Tone:
- crisp
- academic
- spreadsheet-adjacent, but more refined

### 7. Course Assignments List
Purpose:
- Provide a clean index of assignments within a course.

Primary content:
- assignment name
- type
- publish state
- due date
- submission counts

Primary actions:
- create
- duplicate later
- open
- filter by state

### 8. Student Results View
Purpose:
- Show the released result clearly without exposing staff-only grading state.

Primary content:
- final grade
- rubric feedback
- released comments
- visible artifacts or logs if allowed
- submission history

Primary actions:
- view current submission
- switch to previous submission if exposed

## Shared Components and Patterns
Repeat these across designs:
- left navigation with course-aware context
- compact page header with title, metadata, and actions
- structured data tables
- status badges with restrained color use
- side inspector panels
- timeline or event list for grading lifecycle
- rubric list with editable score rows
- artifact/file list with clear filenames and states

## Data Density Expectations
- This should be a serious product UI, not a sparse marketing dashboard.
- Use whitespace well, but keep important operational data on screen.
- Staff views can be denser than student views.
- Do not rely on giant cards to separate everything.

## Mobile and Responsive Expectations
- Prioritize desktop and laptop first because grading and course management are work-heavy tasks.
- Student submission views should still work well on mobile.
- Gradebook and review screens may collapse into stacked panels on smaller screens, but should preserve hierarchy.
- Avoid designs that depend entirely on wide desktop tables without a responsive fallback.

## Accessibility and Legibility
- Strong contrast
- Large enough tap targets
- Color never as the only status signal
- Status text always explicit
- Dense tables must remain readable

## Sample Product Language
Use product-like copy, not marketing copy.

Good examples:
- Course assignments
- Pending review
- Grading in progress
- Submission history
- Released score
- Starter files
- Review summary
- Rerun queued

Avoid:
- transformative learning language
- generic SaaS hero copy
- motivational student slogans

## Candidate Concept Directions
Ask the UI tool for 3 distinct directions:

### Direction A: Calm Technical Workspace
- restrained palette
- strongest emphasis on data density and operational clarity
- closest to Linear or modern developer tooling

### Direction B: Academic Editorial
- cleaner whitespace
- slightly more refined typography
- still product-first, but with a more premium institutional tone

### Direction C: Review-Centric Lab
- emphasizes grading workflow, rubric panels, logs, and submission state
- best for stress-testing the coding-assignment review experience

## Prompt Format for UI Generation Tools
If the tool benefits from a direct prompt, use something close to this:

```text
Design a modern web application UI for Optimark, an instructor-first assessment platform similar in spirit to Gradescope, starting with coding assignments. The product serves instructors, TAs, and students. Instructors create coding assignments, students upload code submissions, the system autogrades asynchronously, and instructors or TAs review and release grades.

Visual direction: calm, credible, technical, academic, and premium. Avoid generic SaaS cards and avoid playful LMS styling. Use strong typography, sparse accent color, layout-based composition, and dense but readable operational UI. Think modern developer tools and serious academic workflows.

Generate desktop-first concepts for:
1. Instructor course dashboard
2. Coding assignment builder
3. Student assignment detail and submission screen
4. Submission processing/status screen
5. Instructor/TA submission review screen
6. Gradebook

Use:
- left navigation
- structured tables and panels
- side inspectors where useful
- explicit grading and status states
- minimal chrome

Do not use:
- marketing hero sections
- dashboard card mosaics
- rainbow color systems
- cluttered borders
- playful education branding
```

## Output Expectations
The best generated concepts should:
- clearly distinguish staff versus student surfaces
- make grading state easy to understand
- make the review screen feel like the product's center of gravity
- feel extensible to future PDF and quiz workflows
- avoid locking the product visually into a coding-only niche
