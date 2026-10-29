# GhostCam Studio — Real-Time Webcam VFX & Virtual Camera Engine

**GhostCam Studio** is a standalone, real-time computer-vision webcam effects engine powered by MediaPipe and OpenCV. All video processing, sprites, and stereo sound effects are generated 100% locally on your machine with clean, overlay-free output to both the local preview window and your Virtual Camera (Microsoft Teams, Google Meet, Zoom, Discord, OBS Studio).

> 🇧🇷 Documentação em Português do Brasil: [README_PT-BR.md](README_PT-BR.md)

---

## ✨ 7 Built-in Visual Effects

You can select an effect from the launcher menu **or switch effects on the fly at any time** while the camera is running by pressing keys **`1` through `7`**:

| Key | Mode | Hand Gesture Trigger | Visual & Audio Effect |
| :---: | :--- | :--- | :--- |
| **`1`** | **Normal Vanish (`normal`)** | Make a **V-sign (peace gesture)** | Smooth top-to-bottom organic wave dissolve with a shimmering cyan-gold plasma edge over 3.6 seconds. |
| **`2`** | **Naruto Substitution (`naruto`)** | Bring **both open palms together** in front of your chest | **Kawarimi no Jutsu**: procedural chakra smoke cloud & swirling anime ribbons erupt with a synthesized smoke-burst & hollow-wood sound while a procedurally rendered wooden substitution log drops and bounces on the floor. |
| **`3`** | **Cosmic Particles (`particles`)** | Make a **V-sign (peace gesture)** | Your silhouette shatters into drifting colored wind fragments and glowing embers over 2.15 seconds. |
| **`4`** | **Goku Teleport (`goku`)** | Hold **index + middle fingers together on your forehead** for 1.0s | **Instant Transmission**: golden-white ki flash, horizontal spatial compression, and vertical anime speed lines vanish you with a synthesized DBZ teleport chirp; repeat the pose for 1.0s to teleport back in reverse! |
| **`5`** | **Optical Stealth Cloak (`stealth`)** | Raise an **open 5-finger palm** | Predator / Cyberpunk glass refraction bends the background across your silhouette with a neon holographic scanline rim. |
| **`6`** | **Dimensional Portal (`portal`)** | Make a **Rock-On / Horns gesture** (index + pinky extended) | A swirling energy vortex opens behind you, pulls your silhouette into its center with a spiral twist, and snaps shut. |
| **`7`** | **Ninja Smoke Scroll (`smoke`)** | Bring **both open palms together** in front of your chest | Volumetric smoke puffs erupt around you while a procedural crimson ninja decoy scroll drops to the floor. |

Every effect includes its own procedurally synthesized stereo `.wav` sound effect generated automatically by `ghostcam/audio.py` and procedural sprites generated in code — zero external image or audio assets required.

---

## 🚀 Quick Start

1. Double-click **`start_studio.bat`**.
2. Choose your initial effect (`1` – `7`) in the **GhostCam Studio** launcher window.
3. **Step out of the camera frame for 4 seconds** while the empty background is captured.
4. Step back into the frame and trigger your effect using its hand gesture or press **`V`**!

### Launch a specific mode directly from the terminal:
```powershell
.\start_studio.bat --mode normal
.\start_studio.bat --mode naruto
.\start_studio.bat --mode particles
.\start_studio.bat --mode goku
.\start_studio.bat --mode stealth
.\start_studio.bat --mode portal
.\start_studio.bat --mode smoke
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

- **`1` – `7`**: Switch between the 7 effect modes immediately without restarting.
- **`SPACE`**: Recapture the empty background (step out of the frame for 4 seconds).
- **`V`**: Manually trigger the active vanish effect.
- **`R`**: Reappear in the camera (triggers reverse animation for Goku/Teleport, Stealth, and Portal).
- **`F`**: Toggle fullscreen preview.
- **`Q` / `ESC`**: Quit and release camera resources.

---

## 📦 Building the Standalone Windows Executable (`GhostCamStudio.exe`)

To package the entire studio (including MediaPipe models and synthesized audio) into a single standalone `.exe` file (`dist\GhostCamStudio.exe`):

```powershell
.\build_exe.bat
```

---

## 🗂️ Project Architecture

```text
ghostcam_studio/
├── main.py                        # CLI entrypoint & self-test runner
├── start_studio.bat               # Standalone Windows launcher
├── start_virtual_cam.bat          # Virtual camera launcher
├── requirements.txt               # Python dependencies
├── ghostcam/
│   ├── config.py                  # Studio settings & 7-effect catalog
│   ├── models.py                  # MediaPipe model downloader & vision pipeline
│   ├── gestures.py                # Hand & face landmark gesture detectors
│   ├── audio.py                   # Procedural stereo WAV sound synthesizer & mixer
│   ├── ui.py                      # Interactive 7-card graphical mode selector
│   ├── engine.py                  # Real-time capture, calibration & virtual camera loop
│   └── effects/
│       ├── normal_dissolve.py     # Mode 1: Normal Vanish (Plasma Wave Dissolve)
│       ├── naruto.py              # Mode 2: Naruto Substitution (Procedural Log & Smoke)
│       ├── disintegration.py      # Mode 3: Cosmic Particles (Wind Dispersion)
│       ├── goku.py                # Mode 4: Goku Teleport (Instant Transmission)
│       ├── stealth_cloak.py       # Mode 5: Optical Stealth Cloak
│       ├── portal.py              # Mode 6: Dimensional Portal
│       ├── smoke_bomb.py          # Mode 7: Ninja Smoke Scroll
│       └── teleport.py            # Classic Teleport variant
└── tests/
    └── test_ghostcam.py           # Automated unit test suite
```
