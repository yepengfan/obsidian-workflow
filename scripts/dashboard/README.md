# Home and module dashboards

`Home.md` is the compact overview and entry point. Its 14 cards open dedicated module dashboards. Feeds is omitted from Home; its pipelines and history are unchanged.

All dashboards use `ui/view.js` and `ui/view.css` for one visual language: Home navigation, the same module icon, a single title, accent color, typography, 12px card corners, metric cards, and keyboard focus styles. Wrappers use `cssclasses: [dashboard, module-dashboard]` to hide Obsidian's duplicate filename title. Styles are scoped to dashboard pages.

## Audit and resulting behavior

| Page            | Issue addressed                                       | Result                                                                                                    |
| --------------- | ----------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| Home            | Full components crowded the entry page                | Compact cards, true counts and mini charts; shared header and icons                                       |
| Practice Review | Empty today queue hid upcoming work                   | Due/overdue metrics, seven-day schedule, stages and composable queue filters                              |
| Task Board      | Different controls and fixed desktop matrix           | Shared shell, labeled inputs, explicit importance state, narrow-pane stacking                             |
| Journal         | Repeated titles and different navigation              | Shared shell, consistent labels; preserves calendar, entry creation and pending followups                 |
| Learning        | Archived plan default and truncated activity filters  | Active-first plan cards; search and filter the full weekly log collection                                 |
| Books           | Duplicate shelves and tables; mixed progress concepts | One filtered library; reading channel, chapter understanding and live WeRead percentage stay distinct     |
| Algorithm       | Long category and atom tables; redundant links        | Searchable, paged patterns, atoms and logs; compact weekly activity                                       |
| System Design   | Separate queue and inconsistent pattern views         | Roadmap-ordered sessions with progress/canvas links; shared library controls                              |
| Frontend        | Separate visual conventions                           | Same practice summary, library and log browsing as other practice domains                                 |
| Zettelkasten    | Unbounded cards; unclear link counts                  | Status/topic/search filters, pagination, update ordering, explicit reference counts and candidate actions |
| Articles        | Unlimited title list and source dropdown only         | Totals, source/search filters, update dates and pagination                                                |
| Essays          | Bare index without consistent navigation              | Shared summary and searchable writing library                                                             |
| Work            | Large repeated time summaries and embedded sessions   | Today, searchable projects and dated notes; explicit links to time views and Brownbag                     |
| Brownbag        | Bare table without progress browsing                  | Acceptance-based totals and status filter; session template entry                                         |
| Profile         | Tiny labels and motion-heavy card                     | Readable static card, full profile entry, and labeled assessment dimensions                               |

## Runtime ownership

- `home/`: compact cards and summary calculations.
- `ui/`: shell, SVG icons, metrics, charts, safe internal links, filters and pagination. Collection filters run before the 20-row page is selected. Changing a filter resets pagination; Reset clears all filters.
- `practice/`: shared Algorithm, System Design and Frontend dashboards; domain directories forward to it.
- Other module directories: module-specific data and presentation.
- `../journal/`: journal parsing, entry launch and calendar refresh.

The shared shell is presentation only. Copy actions explicitly copy an agent command; they do not launch workflows. Review browsing never records attempts or changes scheduling. Task editing retains stale-write guards and undo. Zettelkasten candidate actions verify the current status before writing.

## Content and privacy

Only generic dashboard wrappers are tracked in the Essays and Work directories. Their records, projects and session folders remain ignored. `Tasks/Board.md` contains private records and remains ignored; mirror its wrapper in `Templates/Task Board.md`. Work and Home wrappers are mirrored in their reference templates with dated design decisions.

Do not edit plugin-synced Matter, Instapaper, WeRead or Apple Books highlights. The dashboards only read those sources. Books count chapter understanding only when the progress tracker says `done`, independently of the reading percentage. Archived plans and review items remain available through their filters/history.

Dataview custom views execute in an isolated scope. Import Obsidian APIs in the Markdown wrapper and inject them through `input`. For the synchronous shared shell, pass a mutable object to `dv.view("scripts/dashboard/ui", shared)` and use `shared.ui` afterward. Avoid a top-level asynchronous step in shell initialization: the installed Dataview release does not return the generated async wrapper's promise.

## Validation

```sh
node --test scripts/dashboard/ui/view.test.cjs scripts/dashboard/home/view.test.cjs scripts/dashboard/practice-review/view.test.cjs scripts/journal/view.test.cjs scripts/test_home_task_drag.cjs
npx prettier --check scripts/dashboard
```

Also inspect in Obsidian: Home-to-module navigation, source/domain/status/search filters, empty results, next page, command copy, and narrow split panes. Use “Dataview: Rebuild current view” after script-only edits if the current page still shows cached content.
