# Sprint North Star: unsourced-threshold-provenance-hook

**Status**: Locked — Danny-approved raw diff, 2026-09-06
**Date**: 2026-09-06 (rewrite; originally 2026-09-05)

Unsourced, threshold-shaped constants — the PROMOTED DEFAULT pattern, where an engineering value
silently becomes a scientific or safety-bearing parameter — are dangerous precisely because they
are invisible until something downstream depends on them being correct. Detecting them cannot
depend on a human remembering to look: it needs a mechanical check that runs at the moment a
constant is written, independent of whether that constant ever crosses a boundary between systems
or stays local to the file it was born in. A boundary crossing is one way this failure mode shows
up, not the defining condition for it. This sprint extends this project's existing
provenance-checking machinery so that it also catches threshold-shaped constants that never leave
their own file or module, closing the gap where a check scoped only to cross-system boundaries
misses the more common case of a constant that does its damage without ever being exported
anywhere.
