# GhostCam Studio — Real-Time Webcam VFX & Virtual Camera Engine

**GhostCam Studio** is a real-time computer-vision webcam effects engine powered by MediaPipe and OpenCV. All video processing runs 100% locally on your machine with clean, overlay-free output to both the local preview window and your Virtual Camera (Microsoft Teams, Google Meet, Zoom, Discord, OBS Studio).

> 🇧🇷 Documentação em Português do Brasil: [README_PT-BR.md](README_PT-BR.md)

---

## ✨ 5 Built-in Visual Effects

You can select an effect from the launcher menu **or switch effects on the fly at any time** while the camera is running by pressing keys **`1` through `5`**:

| Key | Mode | Hand Gesture Trigger | Visual & Audio Effect |
| :---: | :--- | :--- | :--- |
| **`1`** | **Instant Teleport** | Hold **index + middle fingers together on your forehead** for 1.0s | Anime speed lines & spatial compression vanish you with a synthesized teleport chirp; repeat the gesture to teleport back in reverse. |
| **`2`** | **Cosmic Disintegration** | Make a **V-sign (peace gesture)** | Your silhouette shatters into drifting wind fragments and glowing embers over 2.15 seconds. |
| **`3`** | **Ninja Smoke Bomb** | Bring **both open palms together** in front of your chest | Volumetric smoke puffs erupt around you while a procedural ninja decoy scroll drops to the floor. |
| **`4`** | **Optical Stealth Cloak** | Raise an **open 5-finger palm** | Predator / Cyberpunk glass refraction bends the background across your silhouette with a neon holographic scanline rim. |
| **`5`** | **Dimensional Portal** | Make a **Rock-On / Horns gesture** (index + pinky extended) | A swirling energy vortex opens behind you, pulls your silhouette into its center with a spiral twist, and snaps shut. |

Every effect includes its own procedurally synthesized stereo sound effect generated automatically by `ghostcam/audio.py` — no external audio files required.

---

## 🚀 Quick Start

1. Double-click **`start_studio.bat`**.
2. Choose your initial effect (`1` – `5`) in the **GhostCam Studio** launcher window.
3. **Step out of the camera frame for 4 seconds** while the empty background is captured.
4. Step back into the frame and trigger your effect using its hand gesture or press **`V`**!

### Launch a specific mode directly from the terminal:
```powershell
.\start_studio.bat --mode teleport
.\start_studio.bat --mode disintegration
.\start_studio.bat --mode smoke
.\start_studio.bat --mode stealth
.\start_studio.bat --mode portal
```

---

## 🎥 Using with Microsoft Teams, Meet, Zoom, Discord & OBS

1. Ensure [OBS Studio](https://obsproject.com/) (which provides the **OBS Virtual Camera** driver) or [Unity Capture](https://github.com/schellingb/UnityCapture) is installed:
   ```powershell
   winget install OBSProject.OBSStudio
   ```
2. Start **`start_studio.bat`** (or **`start_virtual_cam.bat`**) first, before turning on the camera in Teams.
3. In Microsoft Teams / Meet / Zoom / Discord, select **`OBS Virtual Camera`** as your camera device.

---

## ⌨️ Keyboard Shortcuts (in Live Feed window)

- **`1` – `5`**: Switch between the 5 effect modes immediately without restarting.
- **`SPACE`**: Recapture the empty background (step out of the frame for 4 seconds).
- **`V`**: Manually trigger the active vanish effect.
- **`R`**: Reappear in the camera (triggers reverse animation for Teleport, Stealth, and Portal).
- **`F`**: Toggle fullscreen preview.
- **`Q` / `ESC`**: Quit and release camera resources.

---

## 🗂️ Project Architecture

```text
ghostcam_studio/
├── main.py                        # CLI entrypoint & self-test runner
├── start_studio.bat               # One-click Windows launcher
├── start_virtual_cam.bat          # Virtual camera launcher
├── requirements.txt               # Python dependencies
├── ghostcam/
│   ├── config.py                  # Studio settings & effect catalog
│   ├── models.py                  # MediaPipe model downloader & vision pipeline
│   ├── gestures.py                # Hand & face landmark gesture detectors
│   ├── audio.py                   # Procedural stereo WAV sound synthesizer & mixer
│   ├── ui.py                      # Interactive 5-card graphical mode selector
│   ├── engine.py                  # Real-time capture, calibration & virtual camera loop
│   └── effects/
│       ├── teleport.py            # Mode 1: Instant Teleport
│       ├── disintegration.py      # Mode 2: Cosmic Disintegration
│       ├── smoke_bomb.py          # Mode 3: Ninja Smoke Bomb
│       ├── stealth_cloak.py       # Mode 4: Optical Stealth Cloak
│       └── portal.py              # Mode 5: Dimensional Portal
└── tests/
    └── test_ghostcam.py           # Automated unit test suite
```
