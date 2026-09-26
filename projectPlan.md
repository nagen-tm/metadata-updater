# Project Plan: MP3 Metadata Editor (macOS / Python)

## 1. Project Overview

### Project Description:
The MP3 MetaData Updater is a Python application that allows users to
update metadata of MP3 files. It will support updating tags like artist,
album, title, genre, and other relevant information.

### Key Features:
1. **Metadata Update**: Update metadata for MP3 files.
2. **Batch Processing**: Process multiple MP3 files in a batch.
3. **User Interface**: Provide a command-line interface for simplicity.
4. **Error Handling**: Handle file read/write errors, unsupported file
formats, and invalid metadata.
5. **Tag Support**: Support for various metadata tags (ID3, MP3, etc.).

### Requirements:
- **Python**: 3.6+
- **Libraries**: `mutagen` for handling MP3 metadata, `argparse` for
command-line argument parsing.

---

## 2. Key Technical Decisions

| Concern | Choice | Rationale |
|---|---|---|
| Tag read/write | `mutagen.id3` | Standard, handles ID3v2.2/v2.3/v2.4 |
| CLI framework | `click` | Clean subcommands, `--help` for free |
| GUI (optional) | `PyObjC` + `Cocoa` or `tkinter` | Native macOS feel;
PyObjC is better |
| Config / defaults | `pydantic` models + YAML | Type-safe, easy to
validate |
| Packaging / distribution | `py2app` or `briefcase` (BeeWare) | Native
`.app` bundle on macOS |
| Logging | `structlog` (structured JSON) | Easy to debug, pipe-friendly |
| Testing | `pytest` + `pytest-cov` | Standard |
| Linting / formatting | `ruff` + `mypy` | Single fast linter, static
types |
| Deps | `uv` (or `pdm`) | Fast resolver, lock file |

---

## 3. Architecture (High-Level)

```
mp3tag/
├── mp3tag/
│   ├── __init__.py
│   ├── cli/                  # Click subcommands
│   │   ├── __init__.py
│   │   ├── main.py           # Entry point, command group
│   │   ├── read.py           # `mp3tag read <file|dir>`
│   │   ├── write.py          # `mp3tag write <file|dir> --artist "..."`
│   │   ├── batch.py          # `mp3tag batch <dir> --from-csv
mapping.csv`
│   │   └── scan.py           # `mp3tag scan <dir>` (reportonly)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── tag_io.py         # Read/write via mutagen (the only file I/O)
│   │   ├── models.py         # Pydantic: TrackMeta, AlbumMeta
│   │   └── validation.py     # Filename parsing, CSV mapping, etc.
│   ├── gui/                  # Optional Phase 4
│   │   ├── app.py
│   │   └── views/
│   └── utils/
│       ├── logging.py
│       └── fs.py             # Safe path handling, batch discovery
├── tests/
│   ├── test_tag_io.py
│   ├── test_models.py
│   └── fixtures/             # Small synthetic .mp3 files
├── pyproject.toml
├── README.md
└── Makefile                  # make test, make lint, make app
```

**Key principle:** `core/` has **zero** CLI or GUI imports. All I/O
funnels through `tag_io.py`. This makes it testable and lets you swap CLI
↔ GUI freely.

---

## 4. Phased Milestones

### Phase 1 — Foundation (Est. 2–3 days)
- [ ] Scaffold project: `pyproject.toml`, `uv`/`pdm` env, `ruff`, `mypy`
- [ ] Create `core/models.py` — `TrackMeta` pydantic model (title, artist, album, album_artist, track_no, disc_no, year, genre, comment, picture_ref)
- [ ] Implement `core/tag_io.py`:
  - `read_tags(path) -> TrackMeta`
  - `write_tags(path, meta: TrackMeta)`
  - `read_tags_batch(paths: list) -> list[TrackMeta]` (parallel with `concurrent.futures`)
- [ ] Generate 3–5 small test `.mp3` fixtures (16 kb/s, 2 s, different ID3v2 versions)
- [ ] Unit tests for read/write round-trip (assert all fields survive)
- [ ] CI: GitHub Actions running `ruff check`, `mypy`, `pytest`

### Phase 2 — CLI (Est. 2–3 days)
- [ ] `mp3tag read <file|dir> [--json]` — pretty-print or JSON output
- [ ] `mp3tag write <file> --title "..." --artist "..." ...` — partial update (don't wipe other tags)
- [ ] `mp3tag batch <dir> --from-csv mapping.csv` — CSV columns: `filename, title, artist, album, track, year`
  - Support `--dry-run` flag (show diff, don't write)
  - Support `--tag-version {2.3, 2.4}` (default 2.4)
  - Support `--encoding {latin1, utf-8}` (legacy tags)
- [ ] `mp3tag scan <dir>` — report: missing tags, inconsistent album names, duplicate track numbers
- [ ] Shell completion for bash/zsh
- [ ] Integration tests: temp dir with 5 MP3s, run batch, verify

### Phase 3 — Quality & Edge Cases (Est. 2 days)
- [ ] Handle: ID3v2.2 files (2-char frame IDs), `TXXX` custom frames, embedded covers (`APIC`)
- [ ] Handle: paths with Unicode / spaces / emoji (macOS is HFS+ → APFS, but user files vary)
- [ ] Handle: non-MP3 files in a directory (graceful skip + warning)
- [ ] Handle: write failures (disk full, permissions) → collect errors, exit code 1, summary at end
- [ ] Add `--backup` flag: copy original to `<filename>.bak.mp3` before overwriting
- [ ] Add `--undo` support via a simple JSON operation log written to `~/.mp3tag/undo.log`
- [ ] Write `README.md` with all commands + examples
- [ ] `mypy --strict` passes on all modules

### Phase 4 — GUI (Optional, Est. 4–5 days)
- [ ] PyObjC `NSWindow` app:
  - Left pane: `NSTableView` showing folder tree + track list (title, artist, album, track#, duration)
  - Right pane: form fields bound to selected track
  - "Select Folder…" button (`NSOpenPanel`)
  - "Apply" / "Apply All" buttons
  - Inline validation (red border + tooltip)
- [ ] Multi-track select → edit shared fields (album, album artist) in one pass
- [ ] Drag-and-drop a folder onto the window
- [ ] `py2app` build → `mp3tag.app` in `/Applications`
- [ ] Optional: menu-bar item (status bar) for quick "fix tags in Downloads"

### Phase 5 — Polish & Release (Est. 1–2 days)
- [ ] `Makefile` targets: `make install`, `make test`, `make lint`, `make app`
- [ ] Version via `__version__` in `pyproject.toml`, shown by `mp3tag --version`
- [ ] Optional: Homebrew tap (`brew install mp3tag`)
- [ ] Optional: Sparkle auto-update (overkill but easy with `briefcase`)
- [ ] Tag `v1.0.0`, write short changelog

---

## 5. Testing Strategy

| Layer | What | Tool |
|---|---|---|
| Unit | `tag_io` read/write against fixture MP3s | `pytest` + `tmp_path`
|
| Unit | Pydantic model validation (bad track numbers, empty strings) |
`pytest` |
| Integration | Full CLI invocations via `subprocess.run` on a temp folder
| `pytest` + `click.testing.CliRunner` |
| Property / fuzz | Random metadata → write → read → compare |
`hypothesis` (optional) |
| Manual | 10 real MP3s from your own library, edge-case filenames |
checklists in README |

Target coverage: **≥ 90 %** on `core/`, **≥ 80 %** on `cli/`.

---

## 6. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| `mutagen` is essentially unmaintained (last release 2023) | Pin version;
wrap all calls in `tag_io.py` so you can swap to a `libid3` / `ffmpeg`
backend later |
| ID3v2.2 (legacy) frames have 2-char IDs and `latin-1` encoding |
Explicit `--tag-version` flag; test fixtures include v2.2 files |
| macOS Gatekeeper blocks unsigned `.app` | Ship unsigned for now;
document "right-click → Open" or `codesign` instructions |
| Large libraries (50 k+ files) → slow CLI | Batch reads with
`ThreadPoolExecutor(max_workers=os.cpu_count())`; show a `tqdm` progress bar |

---

## 7. Suggested Timeline (solo dev, ~2 h/day)

| Phase | Deliverable |
|---|---|
| Phase 1 | Repo scaffolded, core I/O working, CI green |
| Phase 2 | Full CLI usable on real MP3s |
| Phase 3 | Edge cases handled, `--undo` works, docs |
| Phase 4 | GUI app in `~/Applications` |
| Phase 5 | Tagged release, Homebrew tap (optional) |

