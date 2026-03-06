# 06. Highway — FSD v13.2.8 Exit Attempt Failure

**ID:** `06_VID_FSD` | **Date:** Unknown | **Location:** Highway

## Incident Summary

| Field | Detail |
|-------|--------|
| Vehicle | Tesla Model Y LR |
| AV System | FSD Supervised |
| AV Version | v13.2.8 |
| Speed at Impact | ~35.9 mph (~58 km/h) |
| Original Weather | Clear |
| Original Lighting | Daylight |
| Video Duration | 13 sec @ 30 fps (1920×1080) |
| CARLA Map | Town04 |

![Simulation GIF](assets/gifs/06_VID_FSD.gif)

> *Simulation GIF to be generated from `Videos/06_VID_FSD/VID_FSD_06.mp4`.*

A Tesla Model Y LR operating under FSD Supervised v13.2.8 attempted to take an incorrect highway exit, executing an unexpected and unsafe lane maneuver. The driver-recorded footage was shared on Reddit as an example of FSD supervised mode making an erroneous exit decision at highway speed.

**Notes:** Reddit dashcam — FSD supervised mode failure.

**Source:** [Reddit — FSD Supervised v13.2.8 tried to exit when it shouldn't](https://www.reddit.com/r/SelfDrivingCars/comments/1ixjpgk/fsd_supervised_v1328_mylr_2023_tried_to_exit_when/#lightbox)

---

## CARLA Simulation

| Parameter | Value |
|-----------|-------|
| Map | Town04 |
| Origin | `x=-59.96, y=380.10, z=2.06, yaw=-44.06, pitch=-6.83, roll=0.00` |
| Destination | `x=10.72, y=306.18, z=1.97, yaw=-35.75, pitch=-4.14, roll=0.00` |

### Environmental Variations

> *CARLA simulation screenshots coming soon.*

---

[Back to Dataset Overview](../README.md)
