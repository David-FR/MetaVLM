# 02. I-5 — High-Speed Rear-End Collision

**ID:** `02_VID_FTSB` | **Date:** June 22, 2023 | **Location:** Highway I-5

## Incident Summary

| Field | Detail |
|-------|--------|
| Vehicle | Tesla Model Y |
| AV System | Autopilot |
| Speed at Impact | ~45.43 mph (~73 km/h) |
| Original Weather | Clear |
| Original Lighting | Daylight |
| Video Duration | 2 sec @ 30 fps (985×720) |
| CARLA Map | Town04 |

![Simulation GIF](../assets/gifs/02_VID_FTSB.gif)


A Tesla Model Y on Autopilot rear-ended another vehicle at highway speed on Interstate I-5. The system failed to detect or respond to the slower vehicle ahead in time to avoid the collision. This incident was documented as part of the WSJ investigation into Tesla Autopilot crash patterns.

**Notes:** WSJ Investigation — Original video 2.

**Source:** [WSJ — Tesla Autopilot Crash Investigation](https://www.wsj.com/business/autos/tesla-autopilot-crash-investigation-997b0129)

---

## CARLA Simulation

| Parameter | Value |
|-----------|-------|
| Map | Town04 |
| Origin | x=9, y=30, z=2 |
| Destination | x=5, y=-143, z=2 |

### Environmental Variations

| Noon — Clear | Noon — Rain | Noon — Fog |
|:---:|:---:|:---:|
| ![](../assets/screenshots/02_VID_FSB_Noon_Clear.png) | ![](../assets/screenshots/02_VID_FSB_Noon_Rain.png) | ![](../assets/screenshots/02_VID_FSB_Noon_Fog.png) |

| Twilight — Clear | Twilight — Rain | Twilight — Fog |
|:---:|:---:|:---:|
| ![](../assets/screenshots/02_VID_FSB_Twilight_Clear.png) | ![](../assets/screenshots/02_VID_FSB_Noon_Rain.png) | ![](../assets/screenshots/02_VID_FSB_Twilight_Fog.png) |

| Night — Clear | Night — Rain | Night — Fog |
|:---:|:---:|:---:|
| ![](../assets/screenshots/02_VID_FSB_Night_Clear.png) | ![](../assets/screenshots/02_VID_FSB_Night_Rain.png) | ![](../assets/screenshots/02_VID_FSB_Night_Fog.png) |

---

[Back to Dataset Overview](../README.md)
