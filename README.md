# MetaVLM Dataset

## Overview

This repository contains the **MetaDrive-VLM Dataset**, a comprehensive collection of reconstructed autonomous vehicle crash scenarios designed to evaluate Vision-Language Model (VLM) decision-making in safety-critical driving situations. The dataset consists of 20 base scenarios sourced from real-world dashcam footage and crash reports, expanded to ~100 instances through systematic environmental variations.

**Key Statistics:**
- **20 Base Scenarios**: 10 from dashcam videos + 10 from crash reports
- **~100 Total Instances**: Environmental variations (weather, time, traffic)
- **12,000+ Evaluations**: Across 5 metadata configurations
- **High-Fidelity Reconstruction**: CARLA simulator with precise parameter matching

## Table of Contents

- [Dataset Structure](#dataset-structure)
- [Base Scenarios](#base-scenarios)
- [Environmental Variations](#environmental-variations)
- [Metadata Schema](#metadata-schema)
- [Getting Started](#getting-started)
- [Citation](#citation)



## Base Scenarios

The dataset comprises 20 base scenarios representing documented AV failures:

### Video-Sourced Scenarios (10 scenarios)

| ID | Name | Speed Range | Source | Notes |
|----|------|-------------|--------|-------|
| 01_VID_FTSA | Secondary Collision | 25-60 km/h | [WSJ Investigation](https://www.wsj.com/business/autos/tesla-autopilot-crash-investigation-997b0129) | Tesla FSD failure |
| 02_VID_FTSB | Rear-End Collision | 40-80 km/h | [WSJ Investigation](https://www.wsj.com/business/autos/tesla-autopilot-crash-investigation-997b0129) | High-speed impact |
| 03_VID_FTSI | Intersection Failure | 15-45 km/h | [WSJ Investigation](https://www.wsj.com/business/autos/tesla-autopilot-crash-investigation-997b0129) | Red light scenario |
| 04_VID_LV | Lane Departure | 60-90 km/h | [WSJ Investigation](https://www.wsj.com/business/autos/tesla-autopilot-crash-investigation-997b0129) | Highway scenario |
| 05_VID_ORS | Off-Road Hazard | 30-70 km/h | [WSJ Investigation](https://www.wsj.com/business/autos/tesla-autopilot-crash-investigation-997b0129) | Road edge departure |
| 06_VID_FSD | FSD Exit Attempt | 50-70 km/h | [Reddit/Dashcam](https://www.reddit.com/r/SelfDrivingCars/comments/1ixjpgk/fsd_supervised_v1328_mylr_2023_tried_to_exit_when/#lightbox) | FSD v13.2.8 failure |
| 07_VID_ROBO | Robotaxi Incident | 20-40 km/h | [Reddit/Dashcam](https://www.reddit.com/r/SelfDrivingCars/comments/1li2cil/tesla_robotaxi_day_1_significant_screwup_not_oc/) | Autonomous mode |
| 08_VID_M3 | Model 3 Front Crash | 35-65 km/h | [YouTube](https://www.youtube.com/watch?v=frGoalySCns) | FSD 13.2.8 |
| 09_VID_CRASH | High-Speed Collision Cops | 80-110 km/h | [WSJ Video Report](https://www.youtube.com/watch?v=V2u3dcH2VGM) | Highway scenario |
| 10_VID_BIKE | Bike Crash | 40-70 km/h | [The Guardian Investigation](https://www.theguardian.com/technology/2018/mar/22/self-driving-car-uber-death-woman-failure-fatal-crash-arizona) | Pedestrian Fatality |

*Note: Full details including exact source URLs and reconstruction parameters available in `/scenarios/base_scenarios/`*

### Report-Sourced Scenarios (10 scenarios)
| ID | Name | Speed Range | Source | Notes |
|----|------|-------------|--------|-------|
| 11_REP_HAND | Handan Stationary Truck | 95-105 km/h | [CNET](https://www.cnet.com/roadshow/news/dash-cam-showed-fatal-tesla-crash-in-china/) | First China Autopilot fatality |
| 12_REP_WILL | Williston Semi-Trailer | 100-110 km/h | [The Guardian](https://www.theguardian.com/technology/2016/jun/30/tesla-autopilot-death-self-driving-car-elon-musk) | First US Autopilot fatality |
| 13_REP_MTV | Mountain View Barrier | 95-110 km/h | [Reuters](https://www.reuters.com/article/us-tesla-crash/tesla-says-crashed-vehicle-had-been-on-autopilot-prior-to-accident-idUSKBN1H7023/) | Highway barrier collision |
| 14_REP_KAN | Kanagawa Pedestrian | 25-40 km/h | [Forbes](https://www.forbes.com/sites/lanceeliot/2020/05/16/lawsuit-against-tesla-for-autopilot-engaged-pedestrian-death-could-disrupt-full-self-driving-progress/) | First Autopilot pedestrian fatality |
| 15_REP_DELR | Delray Beach Semi-Trailer | 80-95 km/h | [WPTV](https://www.wptv.com/news/region-s-palm-beach-county/serious-crash-investigated-on-u-s-441-in-southern-palm-beach-county) | Underride collision scenario |
| 16_REP_KEYL | Key Largo Stop Sign | 50-65 km/h | [New York Times](https://www.nytimes.com/2021/08/17/business/tesla-autopilot-accident.html) | Intersection stop sign failure |
| 17_REP_CLVD | Cloverdale Fire Truck | 105-115 km/h | [Dubois County Herald](https://www.duboiscountyherald.com/news/state/telsa-rear-ends-fire-truck-killing-woman/article_b1388528-30c8-5afd-aafb-5129cb77de5b.html) | Stationary emergency vehicle |
| 18_REP_GARD | Gardena Red Light | 65-80 km/h | [AP News](https://apnews.com/article/6eae3986e7d9c1d00db7d52146cddf23) | Nighttime red light failure |
| 19_REP_AREN | Arendal Parked Truck | 105-115 km/h | [AIBN Norway](https://havarikommisjonen.no/Vei/Avgitte-rapporter/2022-06) | Tunnel exit obstruction |
| 20_REP_FONT | Fontana Overturned Trailer | 100-110 km/h | [CBS News LA](https://www.cbsnews.com/losangeles/news/tesla-driver-killed-big-rig-wreck-on-210-freeway-in-fontana-good-samaritan-hurt/) | Nighttime freeway obstruction |




## Environmental Variations

Each base scenario can be augmented with environmental variations:

### Variation Dimensions

**Weather Conditions:**
- `CLEAR`: No precipitation, good visibility (>10km)
- `RAIN`: Light to moderate rainfall, wet roads
- `FOG`: Reduced visibility (1-5km)
- `SNOW`: Snow coverage, icy roads (where applicable)

**Time of Day:**
- `DAY`: Full daylight (10:00-16:00)
- `TWILIGHT`: Dawn/dusk (6:00-8:00 or 18:00-20:00)
- `NIGHT`: Low light conditions (22:00-4:00)

**Traffic Density:**
- `SPARSE`: <5 vehicles in scene
- `MODERATE`: 5-15 vehicles in scene
- `DENSE`: >15 vehicles in scene
