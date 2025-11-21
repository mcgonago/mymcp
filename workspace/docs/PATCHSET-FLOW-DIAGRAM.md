# Patchset File Change Flow Diagram

```
HORIZON OSPRH-12803 - File Evolution Across Patchsets
======================================================

Patchset 1 (2025-11-06 20:30)
┌─────────────────────────────────────┐
│ tables.py                    +8/-1  │
│ expandable_row.html (NEW)     4L    │
│ expandable_row.html~         (ERR)  │ ← Removed in PS2
└─────────────────────────────────────┘
            ↓ (Added .gitignore, removed backup)

Patchset 2 (2025-11-06 20:32)
┌─────────────────────────────────────┐
│ .gitignore (NEW)             +6     │ ← NEW FILE
│ tables.py                    +8/-1  │
│ expandable_row.html           4L    │
└─────────────────────────────────────┘
            ↓ (Expanded template implementation)

Patchset 3 (2025-11-07 02:39)
┌─────────────────────────────────────┐
│ .gitignore                   +6     │
│ tables.py                    +8/-1  │
│ expandable_row.html          32L    │ ← EXPANDED (+28 lines)
└─────────────────────────────────────┘
            ↓ (Refactored by maintainer Radomir)

Patchset 4 (2025-11-07 17:04) 🔧 Maintainer Edit
┌─────────────────────────────────────┐
│ .gitignore                   +6     │
│ tables.py                   +24/-1  │ ← ENHANCED (+16 lines)
│ expandable_row.html          23L    │ ← OPTIMIZED (-9 lines)
└─────────────────────────────────────┘
            ↓ (Trivial rebase, no code changes)

Patchset 5 (2025-11-07 17:06) 🔄 NO_CHANGE
┌─────────────────────────────────────┐
│ .gitignore                   +6     │
│ tables.py                   +24/-1  │ = IDENTICAL TO PS4
│ expandable_row.html          23L    │ = IDENTICAL TO PS4
└─────────────────────────────────────┘
            ↓ (Current patchset)

         FINAL STATE ✓
```

---

## File-by-File Evolution

### `.gitignore`
```
PS1: [not present]
PS2: +6 lines ──────────────────────────┐
PS3: (no change)                        │ Same content
PS4: (no change)                        │ across PS2-PS5
PS5: (no change) ───────────────────────┘
```

### `tables.py`
```
PS1: +8/-1 (5,035 bytes) ──────────────┐
PS2: (no change)                       │ Same content
PS3: (no change) ──────────────────────┘ across PS1-PS3
     │
     └─→ MAJOR ENHANCEMENT in PS4
     
PS4: +24/-1 (5,580 bytes) ─────────────┐
PS5: (no change) ──────────────────────┘ Same content PS4-PS5

Change: +16 lines, +545 bytes in PS4
```

### `expandable_row.html`
```
PS1: 4 lines, 141 bytes ───────────────┐
PS2: (no change) ──────────────────────┘ Same content PS1-PS2
     │
     └─→ MAJOR EXPANSION in PS3
     
PS3: 32 lines, 1,126 bytes
     (+28 lines, +985 bytes)
     │
     └─→ REFACTORED/OPTIMIZED in PS4
     
PS4: 23 lines, 730 bytes ──────────────┐
PS5: (no change) ──────────────────────┘ Same content PS4-PS5
     (-9 lines, -396 bytes from PS3)
```

---

## Commit History Timeline

```
Nov 6, 20:30  Owen uploads PS1     Initial implementation
Nov 6, 20:32  Owen uploads PS2     Add .gitignore, fix mistake
              │
              └─── 6h 7m ───→
              │
Nov 7, 02:39  Owen uploads PS3     Expand template (work continues)
Nov 7, 02:45  Owen sets WIP flag   Mark as work in progress
              │
              └─── 14h 25m ─→
              │
Nov 7, 17:04  Radomir uploads PS4  Maintainer refactors code
Nov 7, 17:06  Radomir uploads PS5  Trivial rebase (no changes)
              │
              └─── Current state
```

---

## Size Comparison Chart

```
File Sizes (bytes):

tables.py:
PS1-3: 5,035 █████████████████████████████████████████ (baseline)
PS4-5: 5,580 ███████████████████████████████████████████████ (+545)

expandable_row.html:
PS1-2:   141 ████▌ (minimal)
PS3:   1,126 ████████████████████████████████████▍ (peak)
PS4-5:   730 ███████████████████████▌ (optimized)

.gitignore:
PS1:       0 
PS2-5:   982 ████████████████████████████████ (added)
```

---

## Contributors

- **Owen McGonagle** (omcgonag@redhat.com)
  - Original author (PS1, PS2, PS3)
  - Created initial implementation
  - Expanded template functionality

- **Radomir Dopieralski** (thesheep / openstack@dopieralski.pl)
  - Project maintainer
  - Refactored code (PS4)
  - Optimized implementation
  - Performed trivial rebase (PS5)

---

*Generated: 2025-11-10*



