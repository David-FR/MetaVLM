# 20. Fontana, California — Overturned Freeway Trailer

**ID:** `20_REP_FONT` | **Date:** May 5, 2021 | **Location:** Fontana, California, USA

## Incident Summary

| Field | Detail |
|-------|--------|
| Vehicle | Tesla Model 3 |
| AV System | Autopilot |
| Speed at Impact | ~65 mph (~105 km/h) |
| Original Weather | Clear |
| Original Lighting | Night |
| Outcome | Driver fatality, bystander injured |
| CARLA Map | Town04 |

> *Accident diagram not available for this scenario.*

A Tesla Model 3 with automated driving engaged struck an overturned tractor-trailer blocking the freeway at night, fatally injuring the driver and injuring a bystander who had stopped to assist. The California Highway Patrol confirmed Autopilot was active at the time, and NHTSA initiated a formal investigation.

**Notes:** CHP confirmed Autopilot engaged; NHTSA investigation initiated.

**Sources:**
- [CBS Los Angeles — Tesla Driver Killed, 2 Seriously Hurt In Big-Rig Wreck on 210 Freeway](https://losangeles.cbslocal.com/2021/05/05/tesla-driver-killed-big-rig-wreck-on-210-freeway-in-fontana-good-samaritan-hurt/)
- [AP News — Officials: Tesla Autopilot probed in fatal California crash](https://apnews.com/article/california-business-technology-204e5600ec902d0bfda10feca74a9ed0)
- [AP News — Crash, arrest draw more scrutiny of Tesla Autopilot system](https://apnews.com/article/ca-state-wire-california-arrests-business-technology-388ae97b2c5c8a7ca7ae816323e7b829)
- [CBS Los Angeles — CHP Investigating Deadly Fontana Tesla Crash](https://losangeles.cbslocal.com/2021/05/14/chp-investigating-deadly-fontana-tesla-crash-to-see-if-self-driving-computer-played-part/)
- [NHTSA — SGO-2021-01 ADAS Incident Reports (CSV)](https://static.nhtsa.gov/odi/ffdd/sgo-2021-01/SGO-2021-01_Incident_Reports_ADAS.csv)

---

## CARLA Simulation

| Parameter | Value |
|-----------|-------|
| Map | Town04 |
| Origin | `x=-299.03, y=26.38, z=1.78, yaw=0.56, pitch=-1.15, roll=0.00` |
| Destination | `x=-219.47, y=26.94, z=5.34, yaw=-1.93, pitch=-7.84, roll=0.00` |

### Environmental Variations

| Noon — Clear | Noon — Rain | Noon — Fog |
|:---:|:---:|:---:|
| ![](../assets/screenshots/20_REP_Font_Noon_Clear.png) | ![](../assets/screenshots/20_REP_FONT_Noon_Rain.png) | ![](../assets/screenshots/20_REP_FONT_Noon_Fog.png) |

| Twilight — Clear | Twilight — Rain | Twilight — Fog |
|:---:|:---:|:---:|
| ![](../assets/screenshots/20_REP_FONT_Twilight_Clear.png) | ![](../assets/screenshots/20_REP_FONT_Noon_Rain.png) | ![](../assets/screenshots/20_REP_FONT_Twilight_Fog.png) |

| Night — Clear | Night — Rain | Night — Fog |
|:---:|:---:|:---:|
| ![](../assets/screenshots/20_REP_FONT_Night_Clear.png) | ![](../assets/screenshots/20_REP_FONT_Night_Rain.png) | ![](../assets/screenshots/20_REP_FONT_Night_Fog.png) |

### Simulation Script

The CARLA reconstruction script for this scenario is [`scripts/20_REP_FONT_scenario.py`](../scripts/20_REP_FONT_scenario.py).

**Prerequisites:** CARLA 0.9.x running locally with PythonAPI configured.

**Run:**
```bash
# Place inside your CARLA PythonAPI directory tree, then:
python 20_REP_FONT_scenario.py
```

Output frames and `metadata.jsonl` are saved to `./sessions/<timestamp>/`.

---

[Back to Dataset Overview](../README.md)
