# 14. Kanagawa, Japan — Expressway Pedestrian Strike

**ID:** `14_REP_KAN` | **Date:** April 29, 2018 | **Location:** Kanagawa, Japan

## Incident Summary

| Field | Detail |
|-------|--------|
| Vehicle | Tesla Model X |
| AV System | Autopilot |
| Speed at Impact | ~24 mph (~39 km/h) |
| Original Weather | Clear |
| Original Lighting | Daylight |
| Outcome | Fatal collision |
| CARLA Map | Town06 |

![Accident Diagram](https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/Kanawaga_Accident.gif/960px-Kanawaga_Accident.gif)

A Tesla Model X on Autopilot accelerated following a lane change and struck a van, then continued into pedestrians on an expressway. The driver had fallen asleep at the wheel. This was the first documented case of an Autopilot-engaged vehicle striking and killing a pedestrian.

**Notes:** First reported Autopilot pedestrian fatality; driver had fallen asleep.

**Sources:**
- [Forbes — Lawsuit against Tesla for Autopilot-Engaged Pedestrian Death](https://www.forbes.com/sites/lanceeliot/2020/05/16/lawsuit-against-tesla-for-autopilot-engaged-pedestrian-death-could-disrupt-full-self-driving-progress/)
- [Bloomberg — Tesla's Autopilot Blamed in Lawsuit for Fatal Accident in Japan](https://www.bloomberg.com/news/articles/2020-04-29/tesla-s-autopilot-blamed-in-lawsuit-for-fatal-accident-in-japan)
- [Court Listener — Umeda v. Tesla, Inc. (Case 5:20-cv-02926)](https://www.courtlistener.com/docket/17109047/umeda-v-tesla-inc/)
- [Court Filing — Original Complaint for Damages (PDF)](https://regmedia.co.uk/2020/04/30/tesla_complaint.pdf)
- [Court Listener — Order Granting Dismissal for Forum Non Conveniens (PDF)](https://www.courtlistener.com/recap/gov.uscourts.cand.358803/gov.uscourts.cand.358803.34.0.pdf)

---

## CARLA Simulation

| Parameter | Value |
|-----------|-------|
| Map | Town06 |
| Origin | `x=-269.18, y=-11.36, z=1.05, yaw=1.15, pitch=-4.47, roll=0.00` |
| Destination | `x=-215.14, y=-11.72, z=1.31, yaw=-0.00, pitch=-1.91, roll=0.00` |

### Environmental Variations

| Noon — Clear | Noon — Rain | Noon — Fog |
|:---:|:---:|:---:|
| ![](../assets/screenshots/14_REP_KAN_Noon_Clear.png) | ![](../assets/screenshots/14_REP_KAN_Noon_Rain.png) | ![](../assets/screenshots/14_REP_KAN_Noon_Fog.png) |

| Twilight — Clear | Twilight — Rain | Twilight — Fog |
|:---:|:---:|:---:|
| ![](../assets/screenshots/14_REP_KAN_Twilight_Clear.png) | ![](../assets/screenshots/14_REP_KAN_Noon_Rain.png) | ![](../assets/screenshots/14_REP_KAN_Twilight_Fog.png) |

| Night — Clear | Night — Rain | Night — Fog |
|:---:|:---:|:---:|
| ![](../assets/screenshots/14_REP_KAN_Night_Clear.png) | ![](../assets/screenshots/14_REP_KAN_Night_Rain.png) | ![](../assets/screenshots/14_REP_KAN_Night_Fog.png) |

### Simulation Script

The CARLA reconstruction script for this scenario is [`scripts/14_REP_KAN_scenario.py`](../scripts/14_REP_KAN_scenario.py).

**Prerequisites:** CARLA 0.9.x running locally with PythonAPI configured.

**Run:**
```bash
# Place inside your CARLA PythonAPI directory tree, then:
python 14_REP_KAN_scenario.py
```

Output frames and `metadata.jsonl` are saved to `./sessions/<timestamp>/`.

---

[Back to Dataset Overview](../README.md)
