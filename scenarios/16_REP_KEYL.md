# 16. Key Largo, Florida — Stop Sign & Red Light Failure

**ID:** `16_REP_KEYL` | **Date:** April 25, 2019 | **Location:** Key Largo, Florida, USA

## Incident Summary

| Field | Detail |
|-------|--------|
| Vehicle | Tesla Model S |
| AV System | Autopilot |
| Speed at Impact | ~35 mph (~56 km/h) |
| Original Weather | Clear |
| Original Lighting | Daylight |
| Outcome | One fatality, two pedestrians injured |
| CARLA Map | Town07 |

![Accident Diagram](https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/Key_Largo_Tesla_Crash.gif/250px-Key_Largo_Tesla_Crash.gif)

A Tesla Model S on Autopilot ran through a stop sign and a flashing red light at a T-intersection, striking a parked SUV that was then pushed into two pedestrians, killing one. The driver had been distracted by a dropped phone. Autopilot was confirmed engaged at the time of the incident.

**Notes:** Driver distracted by dropped phone; confirmed Autopilot engaged at time of incident.

**Sources:**
- [New York Times — 'It Happened So Fast': Inside a Fatal Tesla Autopilot Accident](https://www.nytimes.com/2021/08/17/business/tesla-autopilot-accident.html)
- [NBC Miami — South Florida Man Wants Answers After Crash Killed Girlfriend](https://www.nbcmiami.com/news/local/man-wants-answers-after-deadly-crash/124944/)
- [PlainSite — Benavides v. Tesla, Inc. (civil lawsuit docket)](https://www.plainsite.org/dockets/4iolsjy43/county-court-in-and-for-miamidade-county-florida/neima-benavides-pr-v-tesla-inc/)
- [New York Times — Jury Says Tesla Was Partly to Blame for Fatal Crash (Aug 2025)](https://www.nytimes.com/2025/08/01/business/tesla-autopilot-federal-trial-verdict.html)

---

## CARLA Simulation

| Parameter | Value |
|-----------|-------|
| Map | Town07 |
| Origin | `x=-40.12, y=-156.59, z=3.07, yaw=-4.13, pitch=-12.17, roll=0.00` |
| Destination | `x=-5.30, y=-157.04, z=1.34, yaw=10.29, pitch=-3.01, roll=0.00` |

### Environmental Variations

| Noon — Clear | Noon — Rain | Noon — Fog |
|:---:|:---:|:---:|
| ![](../assets/screenshots/16_REP_KEYL_Noon_Clear.png) | ![](../assets/screenshots/16_REP_KEYL_Noon_Rain.png) | ![](../assets/screenshots/16_REP_KEYL_Noon_Fog.png) |

| Twilight — Clear | Twilight — Rain | Twilight — Fog |
|:---:|:---:|:---:|
| ![](../assets/screenshots/16_REP_KEYL_Twilight_Clear.png) | ![](../assets/screenshots/16_REP_KEYL_Noon_Rain.png) | ![](../assets/screenshots/16_REP_KEYL_Twilight_Fog.png) |

| Night — Clear | Night — Rain | Night — Fog |
|:---:|:---:|:---:|
| ![](../assets/screenshots/16_REP_KEYL_Night_Clear.png) | ![](../assets/screenshots/16_REP_KEYL_Night_Rain.png) | ![](../assets/screenshots/16_REP_KEYL_Night_Fog.png) |

---

[Back to Dataset Overview](../README.md)
