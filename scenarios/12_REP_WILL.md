# 12. Williston, Florida — Left-Turning Semi-Trailer

**ID:** `12_REP_WILL` | **Date:** May 7, 2016 | **Location:** Williston, Florida, USA

## Incident Summary

| Field | Detail |
|-------|--------|
| Vehicle | Tesla Model S |
| AV System | Autopilot |
| Speed at Impact | ~65 mph (~105 km/h) |
| Original Weather | Clear |
| Original Lighting | Daylight |
| Outcome | Fatal collision |
| CARLA Map | Town04 |

![Accident Diagram](https://upload.wikimedia.org/wikipedia/commons/thumb/1/16/Williston_Accident.gif/960px-Williston_Accident.gif)

A Tesla Model S on Autopilot failed to brake for an 18-wheel tractor-trailer making a left turn across the highway at an intersection. The vehicle drove under the trailer at highway speed, resulting in a fatal collision. This was the first Autopilot fatality in the United States, prompting a formal NHTSA investigation.

**Notes:** First Autopilot fatality in the US; NHTSA formal investigation opened.

**Sources:**
- [The Guardian — Tesla driver dies in first fatal crash while using autopilot mode](https://www.theguardian.com/technology/2016/jun/30/tesla-autopilot-death-self-driving-car-elon-musk)
- [New York Times — Self-Driving Tesla Involved in Fatal Crash](https://www.nytimes.com/2016/07/01/business/self-driving-tesla-fatal-crash-investigation.html)
- [AP News — Tesla driver killed in crash while using car's 'Autopilot'](https://apnews.com/article/ee71bd075fb948308727b4bbff7b3ad8)
- [The Verge — Florida Highway Patrol full investigation report](https://www.theverge.com/2017/2/1/14458662/tesla-autopilot-crash-accident-florida-fatal-highway-patrol-report)
- [NHTSA — Special Crash Investigation Report DOT HS 812 481 (PDF)](https://crashstats.nhtsa.dot.gov/Api/Public/ViewPublication/812481)
- [NHTSA — PE 16-007 Closure Report (PDF)](https://static.nhtsa.gov/odi/inv/2016/INCLA-PE16007-7876.PDF)
- [NTSB — Accident Report HAR1702 (PDF)](https://www.ntsb.gov/investigations/AccidentReports/Reports/HAR1702.pdf)
- [Reuters — U.S. safety agency says did not assess Tesla Autopilot effectiveness](https://www.reuters.com/article/us-tesla-autopilot/u-s-safety-agency-says-did-not-assess-tesla-autopilot-effectiveness-idUSKBN1I334A)
- [The Verge — Fatal Tesla Autopilot accident investigation ends with no recall](https://www.theverge.com/2017/1/19/14323990/tesla-autopilot-fatal-accident-nhtsa-investigation-ends)
- [Tesla — 'A Tragic Loss' press release](https://www.teslamotors.com/blog/tragic-loss)
- [MIT Technology Review — Tesla's Dubious Claims About Autopilot Safety Record](https://www.technologyreview.com/s/601849/teslas-dubious-claims-about-autopilots-safety-record/)
- [Reuters — DVD player found in Tesla car in fatal May crash](https://www.reuters.com/article/us-tesla-autopilot-dvd-idUSKCN0ZH5BW)

---

## CARLA Simulation

| Parameter | Value |
|-----------|-------|
| Map | Town04 |
| Origin | `x=-321.29, y=6.77, z=1.42, yaw=179.26, pitch=-11.99, roll=0.00` |
| Destination | `x=-379.17, y=6.07, z=0.77, yaw=-179.82, pitch=-0.95, roll=0.00` |

### Environmental Variations

| Noon — Clear | Noon — Rain | Noon — Fog |
|:---:|:---:|:---:|
| ![](../assets/screenshots/12_REP_WILL_Noon_Clear.png) | ![](../assets/screenshots/12_REP_WILL_Noon_Rain.png) | ![](../assets/screenshots/12_REP_WILL_Noon_Fog.png) |

| Twilight — Clear | Twilight — Rain | Twilight — Fog |
|:---:|:---:|:---:|
| ![](../assets/screenshots/12_REP_WILL_Twilight_Clear.png) | ![](../assets/screenshots/12_REP_WILL_Noon_Rain.png) | ![](../assets/screenshots/12_REP_WILL_Twilight_Fog.png) |

| Night — Clear | Night — Rain | Night — Fog |
|:---:|:---:|:---:|
| ![](../assets/screenshots/12_REP_WILL_Night_Clear.png) | ![](../assets/screenshots/12_REP_WILL_Night_Rain.png) | ![](../assets/screenshots/12_REP_WILL_Night_Fog.png) |

### Simulation Script

The CARLA reconstruction script for this scenario is [`scripts/12_REP_WILL_scenario.py`](../scripts/12_REP_WILL_scenario.py).

**Prerequisites:** CARLA 0.9.x running locally with PythonAPI configured.

**Run:**
```bash
# Place inside your CARLA PythonAPI directory tree, then:
python 12_REP_WILL_scenario.py
```

Output frames and `metadata.jsonl` are saved to `./sessions/<timestamp>/`.

---

[Back to Dataset Overview](../README.md)
