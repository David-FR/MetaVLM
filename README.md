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



## 🎯 Base Scenarios

The dataset comprises 20 base scenarios representing documented AV failures:

### Video-Sourced Scenarios (10 scenarios)

| ID | Name | Type | Speed Range | Source | Notes |
|----|------|------|-------------|--------|-------|
| VID_FTSA_01 | Secondary Collision | Front-to-Side Angle | 25-60 km/h | WSJ Investigation | Tesla FSD failure |
| VID_FTSB_02 | Rear-End Collision | Front-to-Side Broadside | 40-80 km/h | WSJ Investigation | High-speed impact |
| VID_FTSI_03 | Intersection Failure | Front-to-Side Intersection | 15-45 km/h | WSJ Investigation | Red light scenario |
| VID_LV_04 | Lane Departure | Lead Vehicle | 60-90 km/h | WSJ Investigation | Highway scenario |
| VID_ORS_05 | Off-Road Hazard | Off-Road Single | 30-70 km/h | WSJ Investigation | Road edge departure |
| VID_FSD_06 | FSD Exit Attempt | Lane Change | 50-70 km/h | Reddit/Dashcam | FSD v13.2.8 failure |
| VID_ROBO_07 | Robotaxi Incident | Intersection | 20-40 km/h | Reddit/Dashcam | Autonomous mode |
| VID_M3_08 | Model 3 Front Crash | Rear-End | 35-65 km/h | YouTube | FSD 13.2.8 |
| VID_CRASH_09 | High-Speed Collision | Highway | 80-110 km/h | News Archive | Highway scenario |
| VID_MISC_10 | TBD | TBD | TBD | TBD | To be finalized |

*Note: Full details including exact source URLs and reconstruction parameters available in `/scenarios/base_scenarios/`*

### Report-Sourced Scenarios (10 scenarios)

| ID | Name | Type | Speed Range | Source | Notes |
|----|------|------|-------------|--------|-------|
| REP_REAREND_11 | Rear-End Crash | Rear-End | 45-75 km/h | NHTSA Report | Stop-and-go traffic |
| REP_PEDEST_12 | Pedestrian Encounter | Pedestrian | 30-50 km/h | Public Report | Crosswalk scenario |
| REP_CYCLIST_13 | Cyclist Interaction | Cyclist | 25-45 km/h | Public Report | Bike lane scenario |
| REP_LANEDEP_14 | Lane Departure | Lane Departure | 70-95 km/h | NHTSA Report | Highway curve |
| REP_MULTIINT_15 | Multi-Vehicle Intersection | Intersection | 20-55 km/h | Public Report | Complex intersection |
| REP_TBD_16 | TBD | TBD | TBD | TBD | To be finalized |
| REP_TBD_17 | TBD | TBD | TBD | TBD | To be finalized |
| REP_TBD_18 | TBD | TBD | TBD | TBD | To be finalized |
| REP_TBD_19 | TBD | TBD | TBD | TBD | To be finalized |
| REP_TBD_20 | TBD | TBD | TBD | TBD | To be finalized |

