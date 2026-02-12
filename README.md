MetaVLM Dataset

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
| VID_FTSA_01 | Secondary Collision | 25-60 km/h | [WSJ Investigation](URL_PLACEHOLDER_1) | Tesla FSD failure |
| VID_FTSB_02 | Rear-End Collision | 40-80 km/h | [WSJ Investigation](URL_PLACEHOLDER_2) | High-speed impact |
| VID_FTSI_03 | Intersection Failure | 15-45 km/h | [WSJ Investigation](URL_PLACEHOLDER_3) | Red light scenario |
| VID_LV_04 | Lane Departure | 60-90 km/h | [WSJ Investigation](URL_PLACEHOLDER_4) | Highway scenario |
| VID_ORS_05 | Off-Road Hazard | 30-70 km/h | [WSJ Investigation](URL_PLACEHOLDER_5) | Road edge departure |
| VID_FSD_06 | FSD Exit Attempt | 50-70 km/h | [Reddit/Dashcam](URL_PLACEHOLDER_6) | FSD v13.2.8 failure |
| VID_ROBO_07 | Robotaxi Incident | 20-40 km/h | [Reddit/Dashcam](URL_PLACEHOLDER_7) | Autonomous mode |
| VID_M3_08 | Model 3 Front Crash | 35-65 km/h | [YouTube](URL_PLACEHOLDER_8) | FSD 13.2.8 |
| VID_CRASH_09 | High-Speed Collision | 80-110 km/h | [News Archive](URL_PLACEHOLDER_9) | Highway scenario |
| VID_BIKE_10 | Bike Crash | 40-70 km/h | [NYTimes Investigation](https://en.wikipedia.org/wiki/Death_of_Elaine_Herzberg) | Pedestrian Fatality |

*Note: Full details including exact source URLs and reconstruction parameters available in `/scenarios/base_scenarios/`*

### Report-Sourced Scenarios (10 scenarios)
| ID | Name | Speed Range | Source | Notes |
|----|------|-------------|--------|-------|
| REP_REAREND_11 | Rear-End Crash | 45-75 km/h | [NHTSA Report](URL_PLACEHOLDER_11) | Stop-and-go traffic |
| REP_PEDEST_12 | Pedestrian Encounter | 30-50 km/h | [Public Report](URL_PLACEHOLDER_12) | Crosswalk scenario |
| REP_CYCLIST_13 | Cyclist Interaction | 25-45 km/h | [Public Report](URL_PLACEHOLDER_13) | Bike lane scenario |
| REP_LANEDEP_14 | Lane Departure | 70-95 km/h | [NHTSA Report](URL_PLACEHOLDER_14) | Highway curve |
| REP_MULTIINT_15 | Multi-Vehicle Intersection | 20-55 km/h | [Public Report](URL_PLACEHOLDER_15) | Complex intersection |
| REP_TBD_16 | TBD | TBD | [TBD](URL_PLACEHOLDER_16) | To be finalized |
| REP_TBD_17 | TBD | TBD | [TBD](URL_PLACEHOLDER_17) | To be finalized |
| REP_TBD_18 | TBD | TBD | [TBD](URL_PLACEHOLDER_18) | To be finalized |
| REP_TBD_19 | TBD | TBD | [TBD](URL_PLACEHOLDER_19) | To be finalized |
| REP_TBD_20 | TBD | TBD | [TBD](URL_PLACEHOLDER_20) | To be finalized |



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
