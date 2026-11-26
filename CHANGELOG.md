# Changelog

All notable changes to **Flame Auto Clicker** are documented in this file.

## [v2.0] — 2026-11-26

### Added
- **Flame Dark UI:** Full redesign using `CustomTkinter` (`#18181B`, `#222227`, `#FF5722`) with real-time CPS calculator and live `● Idle` / `● Clicking` status indicator.
- **Custom Dark Dropdowns (`FlameDropdown`):** Seamless dark dropdown menus without the legacy Windows white 3D border.
- **0 ms Burst Mode:** Pre-built Win32 `SendInput` batch arrays (8 single clicks or 4 double clicks per call) for maximum throughput when interval is `0`.
- **Random Jitter (`±1% – ±50%`):** Optional random interval variation for human-like click timing.
- **FPS-Safe Corner Failsafe `(0, 0)`:** Stops clicking when the visible cursor reaches `(0, 0)` without triggering when the cursor is hidden in FPS games.
- **Internal PC Limit Benchmark:** Safely measures your PC's real minimum timed interval (`measure_pc_floor`) with live amber warnings and a `Re-test` button in Settings.
- **Live Opacity Preview (`10% – 100%`):** Adjust transparency in real time directly from Settings.
- **Single-Instance Guard (`CreateMutexW`):** Prevents accidentally launching duplicate copies of the app.
- **HiDPI Taskbar & Window Icons:** Crisp multi-resolution Flame icon support via Win32 `LoadImageW` + `WM_SETICON`.

### Changed
- **Zero Idle CPU Architecture:** Replaced `PySimpleGUI`, `mouse`, and `keyboard` with native Win32 `ctypes` (`SendInput`, `RegisterHotKey`, `GetMessageW`, `winmm.timeBeginPeriod`).
- **Instant Settings Apply:** Settings are now saved to a single `config.json` file and applied live without restarting the application.
- Reduced external dependencies in `requirements.txt` to just `customtkinter`.

### Removed
- Removed obsolete `v1.x` helper files (`flame-restart.bat`, `restart-link.vbs`, `opacity.txt`, `start_key.txt`, `stop_key.txt`).
