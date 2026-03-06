# 18. Gardena, California — Red Light Failure

**ID:** `18_REP_GARD` | **Date:** December 29, 2019 | **Location:** Gardena, California, USA

## Incident Summary

| Field | Detail |
|-------|--------|
| Vehicle | Tesla Model S |
| AV System | Autopilot |
| Speed at Impact | ~45 mph (~72 km/h) |
| Original Weather | Clear |
| Original Lighting | Night |
| Outcome | Two fatalities |
| CARLA Map | Town06 |

![Accident Diagram](https://upload.wikimedia.org/wikipedia/commons/thumb/d/da/Gardena_Accident.gif/500px-Gardena_Accident.gif)

A Tesla Model S failed to stop for a red light after exiting a freeway at night, striking a turning Honda Civic and killing two occupants. NHTSA confirmed Autopilot was active at the time. The Tesla driver was subsequently charged with vehicular manslaughter — one of the first such criminal charges involving an Autopilot-related fatality.

**Notes:** NHTSA confirmed Autopilot engaged; Tesla driver charged with vehicular manslaughter.

**Source:** [AP News — Gardena accident](https://apnews.com/article/6eae3986e7d9c1d00db7d52146cddf23)

---

## CARLA Simulation

| Parameter | Value |
|-----------|-------|
| Map | Town06 |
| Origin | `x=27.14, y=41.89, z=1.16, yaw=-177.63, pitch=-16.00, roll=0.00` |
| Destination | `x=27.14, y=41.89, z=1.16, yaw=-177.63, pitch=-16.00, roll=0.00` |

### Environmental Variations

| Noon — Clear | Noon — Rain | Noon — Fog |
|:---:|:---:|:---:|
| ![](../assets/screenshots/18_REP_GARD_Noon_Clear.png) | ![](../assets/screenshots/18_REP_GARD_Noon_Rain.png) | ![](../assets/screenshots/18_REP_GARD_Noon_Fog.png) |

| Twilight — Clear | Twilight — Fog | Night — Clear | Night — Rain | Night — Fog |
|:---:|:---:|:---:|:---:|:---:|
| ![](../assets/screenshots/18_REP_GARD_Twilight_Clear.png) | ![](../assets/screenshots/18_REP_GARD_Twilight_Fog.png) | ![](../assets/screenshots/18_REP_GARD_Night_Clear.png) | ![](../assets/screenshots/18_REP_GARD_Night_Rain.png) | ![](../assets/screenshots/18_REP_GARD_Night_Fog.png) |

---

[Back to Dataset Overview](../README.md)
