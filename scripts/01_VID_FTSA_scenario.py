#!/usr/bin/env python3
"""
01_VID_FTSA: CA-101 — FSD Secondary Collision
CARLA AV crash scenario reconstruction script.
Tesla FSD fails to respond to stopped vehicle ahead on Highway CA-101
"""

import os, sys, glob, pathlib
import random
import time
import math
import uuid
import numpy as np
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image
import json

# Paths
HERE = pathlib.Path(__file__).resolve()
PYTHONAPI_ROOT = HERE.parents[2]                 # .../PythonAPI
CARLA_PY_DIR    = PYTHONAPI_ROOT / 'carla'       # .../PythonAPI/carla
EGG_PATTERN     = str(CARLA_PY_DIR / 'dist' / f"carla-*{sys.version_info.major}.{sys.version_info.minor}-{'win-amd64' if os.name == 'nt' else 'linux-x86_64'}.egg")

# 1) Make 'agents' importable
sys.path.insert(0, str(CARLA_PY_DIR))            # so: from agents.navigation... works

# 2) Make compiled 'carla' importable
eggs = glob.glob(EGG_PATTERN)
if eggs:
    sys.path.insert(0, eggs[0])                  # so: import carla comes from the egg

# (Optional) also add PythonAPI root (examples/util helpers)
sys.path.insert(0, str(PYTHONAPI_ROOT))

from carla import VehicleLightState as vls
import carla
print("Using carla from:", carla.__file__)

# IMPORTANT: import from top-level 'agents', not 'carla.agents'
from agents.navigation.behavior_agent import BehaviorAgent
from agents.navigation.basic_agent import BasicAgent
#print(BehaviorAgent)

from carla import VehicleLightState as vls

"""
try:
    import pygame
    from pygame.locals import KMOD_CTRL
    from pygame.locals import K_ESCAPE
    from pygame.locals import K_q
except ImportError:
    raise RuntimeError('cannot import pygame, make sure pygame package is installed')
"""


egg_glob = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'carla', 'dist', 'carla-*%d.%d-%s.egg' % (
    sys.version_info.major,
    sys.version_info.minor,
    'win-amd64' if os.name == 'nt' else 'linux-x86_64'
)))
for p in glob.glob(egg_glob):
    sys.path.insert(0, p)


# Coordinates specific to the AVC_OCR map
spectator_position_x = 4
spectator_position_y = -72
spectator_position_z = 12
spectator_rotation_yaw = -87
spectator_rotation_pitch = -14
spectator_rotation_roll = 0.0

# ------------------ Config defaults  -------------------------------------
DEFAULT_HZ = 6.0 # Frames per second (set --hz to change)
IMG_WIDTH, IMG_HEIGHT = 1280, 720 # Camera resolution
FOV_DEG = 90.0 # Camera horizontal FOV

PHYS_HZ = 30.0 # simulation + controller + sensors run at 30Hz
RECORD_EVERY_N = 5 # save/record every 5th frame ()
DURATION_S = 20 # How long to record (set --duration)

# Spawn / map defaults (adjust to your map)
DEFAULT_MAP_NAME = 'Town04' # Use your map name or one in Content/Carla/Maps
#DEFAULT_MAP_NAME = 'Town04_FTSA' # Use your map name or one in Content/Carla/Maps
#DEFAULT_MAP_NAME = 'Town04_FTSA-C' # Use your map name or one in Content/Carla/Maps
EGO_BLUEPRINT_FILTER = 'vehicle.tesla.model3'

# Ego start/destination (example; tweak to your world)
EGO_START = carla.Location(x=4.48, y=184, z=1.9)
#EGO_DEST = carla.Location(x=297, y=144.15, z=0.1)
EGO_DEST = carla.Location(x=5, y=-143, z=2)

# --- Recording controls ---------------------------------------------------
RECORD_START_SPEED_KMH = 90.0        # start recording at/after this speed
RECORD_AFTER_TICK = 480              # or set to None to disable tick gate
TARGET_RECORD_FRAMES = 34  
#----------------------------------------------------------------------------
@dataclass
class EgoState:
    speed_mps: float
    accel_mps2: float
    yaw_rate_dps: float
    throttle: float
    steer: float
    brake: float


@dataclass
class LaneContext:
    road_id: int
    lane_id: int
    lane_width_m: float
    lane_offset_m: float
    curvature_1pm: float
    speed_limit_kmh: Optional[float]
    is_junction: bool
    light_state: Optional[str]
    dist_to_stopline_m: Optional[float]


@dataclass
class ActorSummary:
    actor_id: int
    cls: str
    role: str
    distance_m: float
    bearing_deg: float
    rel_speed_mps: float
    lane_relation: str


@dataclass
class RiskSummary:
    ttc_s: Optional[float]
    headway_s: Optional[float]
    gap_m: Optional[float]
    rel_speed_mps: Optional[float]
    target_class: Optional[str]


@dataclass
class WeatherSummary:
    rain: float
    fog: float
    wetness: float
    cloudiness: float
    sun_alt_deg: float
    sun_az_deg: float


@dataclass
class FrameRecord:
    frame_id: int
    sim_time: float
    rgb_path: str
    seg_path: str
    seg_raw_path: str
    depth_path: str
    ego: EgoState
    lane: LaneContext
    weather: WeatherSummary
    actors: List[ActorSummary]
    risk: RiskSummary

# ----------------------------------------------------------------------------
def change_map(client, world, map_name=DEFAULT_MAP_NAME):
    """
    # For debugging
    print("\nList of available maps:")
    for map in client.get_available_maps():
        print(map)
    print()

    """
    time.sleep(2)
    print("Before trying to change map")
    if world.get_map().name != map_name:
        print(f"Changing map to: {map_name}")
        client.load_world(map_name, False)
    else:
        print(f"Map is already {map_name}, no need to change.")
    time.sleep(2)    


# Creates and returns a new session directory with subdirs for frames, seg, depth
def make_session_dir(base_dir: pathlib.Path = pathlib.Path('./sessions')) -> pathlib.Path:
    sid = time.strftime('%Y%m%d_%H%M%S') + '_' + str(uuid.uuid4())[:8]
    out = base_dir / sid
    (out / 'frames').mkdir(parents=True, exist_ok=True)
    (out / 'seg').mkdir(parents=True, exist_ok=True)
    (out / 'seg_raw').mkdir(parents=True, exist_ok=True)
    (out / 'depth').mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Session dir: {out}")
    return out


def configure_world_sync(world: carla.World, hz: float) -> None:
    """Configure world for synchronous mode with fixed delta seconds"""
    settings = world.get_settings()
    settings.synchronous_mode = True # means simulation only advances when we call world.tick()
    settings.fixed_delta_seconds = 1.0 / hz
    settings.substepping = False
    #settings.max_substep_delta_time = settings.fixed_delta_seconds / 2.0
    #settings.max_substeps = 2
    world.apply_settings(settings)
    world.tick()
    
    # set weather
    weather = carla.WeatherParameters.ClearNight
    world.set_weather(weather)
    print(f"finished configuring world...")


def move_spectator(world, x, y, z, yaw, pitch, roll):
    spectator = world.get_spectator()
    transform = carla.Transform(
        carla.Location(x, y, z),  # Start high to view the map
        carla.Rotation(yaw=yaw, pitch=pitch, roll=roll)   # Look halfway down
    )
    spectator.set_transform(transform)
    print("Moved spectator")


def show_spawn_points(world, points_color=carla.Color(0, 255, 0)):
    # Get spawn points 
    spawn_points = world.get_map().get_spawn_points()
    print ("Number of spawnpoints", len(spawn_points))

    # To debug visualize spawn points
    for spawn_point in spawn_points:
        world.debug.draw_point(
            spawn_point.location + carla.Location(z=0.5),
            size=0.1,
            color=points_color,
            life_time=10.0
        )


def spawn_ego(world: carla.World, start_loc: carla.Location) -> carla.Vehicle:
    print("Spawning ego vehicle...")
    bp_lib = world.get_blueprint_library()
    #bp = bp_lib.find(EGO_BLUEPRINT_FILTER) if EGO_BLUEPRINT_FILTER in bp_lib else bp_lib.filter('vehicle.*')[0]
    try:
        bp = bp_lib.find(EGO_BLUEPRINT_FILTER)  # exact id like 'vehicle.tesla.model3'
    except Exception:
        bp = random.choice(bp_lib.filter('vehicle.*'))

    bp.set_attribute('role_name', 'ego')

    # Find nearest drivable waypoint and raise Z a bit to avoid ground collision
    wp = world.get_map().get_waypoint(start_loc, project_to_road=True, lane_type=carla.LaneType.Driving)
    transform = wp.transform
    transform.location.z += 0.5 

    """
    # For debugging visualize spawn location
    world.debug.draw_point(
        transform.location,
        size=0.1,
        color=carla.Color(0, 255, 0), 
        life_time=2.0
    )
    time.sleep(3)
    """

    vehicle = world.try_spawn_actor(bp, transform)
    if not vehicle:
        # Try a few nearby waypoints
        for d in [2.0, 4.0, 6.0, 8.0]:
            cand = wp.next(d)[0] if wp.next(d) else None
            if cand:
                t = cand.transform
                t.location.z = max(t.location.z + 0.5, 0.5)
                vehicle = world.try_spawn_actor(bp, t)
                if vehicle:
                    break
    else:
        print("Spawned on first try")
    if not vehicle:
        raise RuntimeError("Failed to spawn ego vehicle")


    """
    # Basic physics tweak
    pc = vehicle.get_physics_control()
    pc.use_sweep_wheel_collision = True
    vehicle.apply_physics_control(pc)
    """
    return vehicle
# ----------------------------------------------------------------------------

# --- Sensor construction --------------------------------------------------------
# Add a camera (sensor) of the given 'kind' to the vehicle
def add_camera(world: carla.World, parent: carla.Actor, kind: str) -> carla.Sensor:
    """kind in {'rgb', 'seg', 'depth'}"""
    bp_lib = world.get_blueprint_library()
    if kind == 'rgb':
        bp = bp_lib.find('sensor.camera.rgb')
    elif kind == 'seg':
        bp = bp_lib.find('sensor.camera.semantic_segmentation')
    elif kind == 'depth':
        bp = bp_lib.find('sensor.camera.depth')
    else:
        raise ValueError(kind)

    bp.set_attribute('image_size_x', str(IMG_WIDTH))
    bp.set_attribute('image_size_y', str(IMG_HEIGHT))
    bp.set_attribute('fov', str(FOV_DEG))
    bp.set_attribute('sensor_tick', '0.0') # produce every world tick

    # Mount on windshield
    relative_transform = carla.Transform(carla.Location(x=0.5, z=1.4), carla.Rotation(pitch=-2.0))
    sensor = world.spawn_actor(bp, relative_transform, attach_to=parent)
    return sensor


# ----------------------------------------------------------------------------
# --- Math / projection helpers -------------------------------------------------
def _as_np_vec(loc: carla.Vector3D) -> np.ndarray:
    return np.array([loc.x, loc.y, loc.z], dtype=np.float32)


def speed_of(actor: carla.Actor) -> float:
    v = actor.get_velocity()
    return float((v.x**2 + v.y**2 + v.z**2) ** 0.5)


def ego_state(vehicle: carla.Vehicle) -> EgoState:
    v = vehicle.get_velocity()
    a = vehicle.get_acceleration()
    w = vehicle.get_angular_velocity()
    ctrl = vehicle.get_control()
    return EgoState(
        speed_mps=float(np.linalg.norm([v.x, v.y, v.z])),
        accel_mps2=float(np.linalg.norm([a.x, a.y, a.z])),
        yaw_rate_dps=float(np.degrees(w.z)),
        throttle=float(ctrl.throttle),
        steer=float(ctrl.steer),
        brake=float(ctrl.brake),
)


def lane_context(world: carla.World, vehicle: carla.Vehicle) -> LaneContext:
    mp = world.get_map()
    wp = mp.get_waypoint(vehicle.get_location(), project_to_road=True, lane_type=carla.LaneType.Driving)
    # Lateral offset: signed distance from lane center (left positive)
    ego_loc = vehicle.get_location()
    lane_center = wp.transform.location
    forward = wp.transform.get_forward_vector()
    right = wp.transform.get_right_vector() # right-hand
    vec = _as_np_vec(ego_loc - lane_center)
    lat_offset = float(np.dot(vec, _as_np_vec(right))) * -1.0 # left positive

    # Curvature approximation: average heading change per meter over ~30 m
    ahead = [wp]
    dist = 0.0
    while dist < 30.0 and ahead[-1].next(2.0):
        nxt = ahead[-1].next(2.0)[0]
        ahead.append(nxt)
        dist += 2.0
    headings = [w.transform.rotation.yaw for w in ahead]
    if len(headings) >= 2 and dist > 0:
        # Unwrap yaw and compute total delta over path
        yaw_rad = np.unwrap(np.radians(headings))
        dpsi = float(abs(yaw_rad[-1] - yaw_rad[0]))
        curvature = (dpsi / dist) * 1e6 # 1 per million meters (1/pm)
    else:
        curvature = 0.0

    # Traffic light (if controlled)
    light_state = None
    dist_to_stop = None
    tl = vehicle.get_traffic_light()
    if tl is not None:
        try:
            light_state = tl.get_state().name
        except Exception:
            light_state = str(tl.state)
        # Try to estimate distance to stop line
        try:
            # Some versions expose stop waypoints
            stop_wps = tl.get_stop_waypoints() # type: ignore[attr-defined]
            if stop_wps:
                # Pick the one on our road/lane if possible
                cand = min(stop_wps, key=lambda w: w.transform.location.distance(ego_loc))
                dist_to_stop = float(cand.transform.location.distance(ego_loc))
        except Exception:
            # Fallback: distance to the light actor location
            dist_to_stop = float(tl.get_transform().location.distance(ego_loc))

    # Speed limit (if available)
    try:
        sl = float(vehicle.get_speed_limit())
    except Exception:
        sl = None


    return LaneContext(
        road_id=int(wp.road_id),
        lane_id=int(wp.lane_id),
        lane_width_m=float(wp.lane_width),
        lane_offset_m=float(lat_offset),
        curvature_1pm=float(curvature),
        speed_limit_kmh=sl,
        is_junction=bool(wp.is_junction),
        light_state=light_state,
        dist_to_stopline_m=dist_to_stop,
    )


def is_ahead(ego: carla.Vehicle, other: carla.Actor) -> bool:
    e_tf = ego.get_transform()
    fwd = e_tf.get_forward_vector()
    rel = other.get_location() - e_tf.location
    dot = fwd.x * rel.x + fwd.y * rel.y + fwd.z * rel.z
    return dot > 0.0


def same_lane(mp: carla.Map, a: carla.Actor, b: carla.Actor) -> bool:
    wa = mp.get_waypoint(a.get_location(), project_to_road=True, lane_type=carla.LaneType.Driving)
    wb = mp.get_waypoint(b.get_location(), project_to_road=True, lane_type=carla.LaneType.Driving)
    return (wa.road_id == wb.road_id) and (wa.lane_id == wb.lane_id)


def bearing_deg(ego: carla.Vehicle, other: carla.Actor) -> float:
    e_tf = ego.get_transform()
    fwd = np.array([e_tf.get_forward_vector().x, e_tf.get_forward_vector().y], dtype=np.float32)
    rel = np.array([other.get_location().x - e_tf.location.x,
    other.get_location().y - e_tf.location.y], dtype=np.float32)
    fwd /= (np.linalg.norm(fwd) + 1e-9)
    rel /= (np.linalg.norm(rel) + 1e-9)
    ang = math.degrees(math.atan2(fwd[0]*rel[1] - fwd[1]*rel[0], fwd.dot(rel)))
    return float(ang)


def rel_speed_along_heading(ego: carla.Vehicle, other: carla.Actor) -> float:
    e_tf = ego.get_transform()
    fwd = np.array([e_tf.get_forward_vector().x, e_tf.get_forward_vector().y, e_tf.get_forward_vector().z], dtype=np.float32)
    fwd /= (np.linalg.norm(fwd) + 1e-9)
    dv = np.array([other.get_velocity().x - ego.get_velocity().x,
    other.get_velocity().y - ego.get_velocity().y,
    other.get_velocity().z - ego.get_velocity().z], dtype=np.float32)
    return float(dv.dot(fwd))


def summarize_actors(world: carla.World, ego: carla.Vehicle, max_n: int = 5) -> Tuple[List[ActorSummary], Optional[ActorSummary]]:
    mp = world.get_map()
    all_actors = world.get_actors()
    vehicles = all_actors.filter('vehicle.*')
    walkers = all_actors.filter('walker.*')

    summaries: List[ActorSummary] = []
    lead: Optional[ActorSummary] = None

    # Vehicles
    for v in vehicles:
        if int(v.id) == int(ego.id):
            continue
        if not is_ahead(ego, v):
            continue
        dist = float(v.get_location().distance(ego.get_location()))
        if dist > 120.0:
            continue
        rs = rel_speed_along_heading(ego, v)
        lane_rel = 'same' if same_lane(mp, ego, v) else 'other'
        summ = ActorSummary(
            actor_id=int(v.id),
            cls='vehicle',
            role='lead' if lane_rel=='same' else 'adjacent',
            distance_m=dist,
            bearing_deg=bearing_deg(ego, v),
            rel_speed_mps=rs,
            lane_relation=lane_rel,
        )
        summaries.append(summ)

    # Pedestrians (within FOV ~ 60 deg and < 40 m)
    for w in walkers:
        dist = float(w.get_location().distance(ego.get_location()))
        if dist > 40.0:
            continue
        br = bearing_deg(ego, w)
        if abs(br) > 60.0:
            continue
        rs = rel_speed_along_heading(ego, w)
        summaries.append(ActorSummary(
            actor_id=int(w.id),
            cls='pedestrian',
            role='crossing' if abs(br) > 15 else 'ahead',
            distance_m=dist,
            bearing_deg=br,
            rel_speed_mps=rs,
            lane_relation='n/a',
        ))


    # Sort by distance and keep top-N
    summaries.sort(key=lambda s: s.distance_m)
    summaries = summaries[:max_n]

    # Pick lead in same lane if present
    for s in summaries:
        if s.cls == 'vehicle' and s.lane_relation == 'same':
            lead = s
            break

    return summaries, lead


def risk_from_lead(ego: EgoState, lead: Optional[ActorSummary]) -> RiskSummary:
    if lead is None:
        return RiskSummary(ttc_s=None, headway_s=None, gap_m=None, rel_speed_mps=None, target_class=None)
    gap = lead.distance_m
    rel_v = -lead.rel_speed_mps # positive if we are closing
    if rel_v > 0.05:
        ttc = gap / rel_v
    else:
        ttc = None
    headway = (gap / ego.speed_mps) if ego.speed_mps > 0.1 else None
    return RiskSummary(
        ttc_s=(float(ttc) if ttc is not None else None),
        headway_s=(float(headway) if headway is not None else None),
        gap_m=float(gap),
        rel_speed_mps=float(-lead.rel_speed_mps),
        target_class=lead.cls,
    )


def weather_summary(world: carla.World) -> WeatherSummary:
    w = world.get_weather()
    return WeatherSummary(
        rain=float(w.precipitation),
        fog=float(w.fog_density),
        wetness=float(w.wetness),
        cloudiness=float(w.cloudiness),
        sun_alt_deg=float(w.sun_altitude_angle),
        sun_az_deg=float(w.sun_azimuth_angle),
    )


# ----------------------------------------------------------------------------
# --- Sensor callbacks & conversion helpers ------------------------------------
class FrameStore:
    """Holds sensor payloads by frame id until the main loop consumes them"""
    # Four dictionaries for the three image types plus depth
    def __init__(self):
        self.rgb: Dict[int, np.ndarray] = {}
        self.seg: Dict[int, np.ndarray] = {}
        self.seg_raw: Dict[int, np.ndarray] = {}
        self.depth_m: Dict[int, np.ndarray] = {}

    # Method to drop stale frames (memory control)
    def clear_older_than(self, frame_id: int):
        def prune(d: Dict[int, Any]):
            for k in list(d.keys()):
                if k < frame_id -5:
                    d.pop(k, None)
        prune(self.rgb); prune(self.seg); prune(self.seg_raw); prune(self.depth_m)

# ----------------------------------------------------------------------------

# Depth decode: convert CARLA depth image (BGRA) to meters
# Formula from CARLA docs: normalized = (R + G*256 + B*256*2) / (256^3 - 1), distance_m = 1000 * normalized
# Note: image.raw_data is in BGRA order; we extract as uin8 then compute
def depth_to_meters(image: carla.Image) -> np.ndarray:
    arr = np.frombuffer(image.raw_data, dtype=np.uint8).reshape((image.height, image.width, 4))
    b = arr[:, :, 0].astype(np.float32)
    g = arr[:, :, 1].astype(np.float32)
    r = arr[:, :, 2].astype(np.float32)
    normalized = (r + g * 256 + b * 256 * 256) / (256**3 - 1.0)
    distance_m = normalized * 1000.0
    return distance_m

def seg_raw_to_ids(image: carla.Image) -> np.ndarray:
    # With ColorConverter.Raw, (applied in callback) the tag id is replicated in R,G,B
    arr = np.frombuffer(image.raw_data, dtype=np.uint8).reshape((image.height, image.width, 4))
    ids = arr[:, :, 2]
    return ids.copy()

# Spawn and attach cameras(RGB, Semantic segmentation and dept)
# set up callbacks to store data in this FrameStore
# The callbacks stuff per-frame results into a simple in-memory FrameStore dict keyed by image.frame (the CARLA frame id)
def attach_and_listen(world: carla.World, vehicle: carla.Vehicle, store: 'FrameStore'):
    cam_rgb = add_camera(world, vehicle, 'rgb')
    cam_seg = add_camera(world, vehicle, 'seg')
    cam_depth = add_camera(world, vehicle, 'depth')

    # RGB callback(store as uint8 array)
    # Converts raw BGRA bytes -> RGB uint8 array ands stores it 
    def on_rgb(image: carla.Image):
        arr = np.frombuffer(image.raw_data, dtype=np.uint8).reshape((image.height, image.width, 4))
        # Convert BGRA to RGB
        rgb = arr[:, :, :3][:, :, ::-1].copy()
        store.rgb[image.frame] = rgb
    
    # Segmentation callback; also keep a pallete visualization
    # Gets raw class IDs and stores a single-channel label map
    # Raw IDs is what we want for stats/analysis; pallete is just for visualization (humans)
    def on_seg(image: carla.Image):
        # 1) Convert to RAW IDs and extract the single-channel label map
        image.convert(carla.ColorConverter.Raw)
        store.seg_raw[image.frame] = seg_raw_to_ids(image)

        # 2) Convert the SAME image to CityScapes palette and extract the RGB viz
        image.convert(carla.ColorConverter.CityScapesPalette)
        arr = np.frombuffer(image.raw_data, dtype=np.uint8).reshape((image.height, image.width, 4))
        seg_vis = arr[:, :, :3][:, :, ::-1].copy()  # BGRA -> RGB
        store.seg[image.frame] = seg_vis
    
    # Depth meters callback
    def on_depth(image: carla.Image):
        store.depth_m[image.frame] = depth_to_meters(image)

    cam_rgb.listen(on_rgb)
    cam_seg.listen(on_seg)
    cam_depth.listen(on_depth)

    return cam_rgb, cam_seg, cam_depth

# ----------------------------------------------------------------------------
# --- Saving helpers ------------------------------------------------------------
# These methods write to disk in appropriate formats

def save_png_rgb(path: pathlib.Path, rgb: np.ndarray):
    Image.fromarray(rgb).save(path)


def save_png_seg_palette(path: pathlib.Path, seg_vis: np.ndarray):
    Image.fromarray(seg_vis).save(path)


def save_png_seg_ids(path: pathlib.Path, ids: np.ndarray):
    # Save single-channel ids as 8-bit PNG
    Image.fromarray(ids.astype(np.uint8), mode='L').save(path)


def save_depth_npy(path: pathlib.Path, depth_m: np.ndarray):
    np.save(path, depth_m.astype(np.float32))

# ----------------------------------------------------------------------------
# --- Main run ------------------------------------------------------------------

def run(hz: float, duration_s: float, map_name: str, dest_loc: Optional[carla.Location] = None):
    client = carla.Client("localhost", 2000)
    client.set_timeout(5)
    world = client.get_world()
    print("Got world after 5 sec timeout", world)
    print("world.get_map()", world.get_map())

    if map_name:
        change_map(client, world, map_name)
        time.sleep(1)
        world = client.get_world() # reload world ref after map change

    move_spectator(world,
                spectator_position_x,
                spectator_position_y,
                spectator_position_z,
                spectator_rotation_yaw,
                spectator_rotation_pitch,
                spectator_rotation_roll)
    

    session_dir = make_session_dir()
    meta_path = session_dir / 'metadata.jsonl'

    vehicle: Optional[carla.Vehicle] = None
    sensors: List[carla.Sensor] = []
    agent: Optional[BasicAgent] = None
    mf = None

    configure_world_sync(world, PHYS_HZ)    

    try:
        vehicle = spawn_ego(world, EGO_START)
        print(f"[INFO] Spawned ego vehicle id={vehicle.id} at {vehicle.get_location()}")

        # Setup vehicle details
        state = vls.Position | vls.LowBeam 
        vehicle.set_light_state(vls(state))

        world.tick()
        time.sleep(3)

        # Autopilot off; we use BasicAgent to drive
        vehicle.set_autopilot(False)

        # Attach sensors (start listening before we tick)
        store = FrameStore()
        s_rgb, s_seg, s_dep = attach_and_listen(world, vehicle, store)
        sensors.extend([s_rgb, s_seg, s_dep])

        # Physics tweak
        # Enable autopilot phisics for the vehicle
        physics_control = vehicle.get_physics_control()
        physics_control.use_sweep_wheel_collision = True
        vehicle.apply_physics_control(physics_control)
        
        # --- Planner: set destination or explicit route ---------------------------
        # Create a behavior agent
        #agent = BehaviorAgent(vehicle, behavior="aggressive")
        agent = BasicAgent(vehicle, target_speed=100)  # km/h
        agent.follow_speed_limits(False)

        # Get waypoints on the road
        waypoints = world.get_map().generate_waypoints(distance=2.0) # 2 meters between waypoints

        """
        # Fitler for drivable road waypoints only
        road_waypoints = [w for w in waypoints if w.lane_type == carla.LaneType.Driving]
        print ("Number of waypoints", len(road_waypoints))
        """

        # Destination ego vehicle location
        closest_spawn_point_destination_ego = world.get_map().get_waypoint(EGO_DEST,
                                                                            project_to_road=True, 
                                                                            lane_type=carla.LaneType.Driving)
        #closest_spawn_point_destination_ego = min(road_waypoints,
        #                                      key=lambda wp: wp.transform.location.distance(EGO_DEST))
        closest_spawn_point_destination_ego_transform = closest_spawn_point_destination_ego.transform
        #closest_spawn_point_destination_ego_transform.location.z += 0.5  # raise a bit to avoid collision with ground

        # For debugging visualize target end location
        world.debug.draw_point(
            closest_spawn_point_destination_ego_transform.location,
            size=0.1,
            color=carla.Color(255, 0, 0), 
            life_time=2.0
        )
        print("showing destination spawn point")
        world.tick()
        time.sleep(3)

        agent.set_destination(closest_spawn_point_destination_ego_transform.location,
                              start_location=vehicle.get_location())
        print(f"[INFO] Destination set to {closest_spawn_point_destination_ego_transform.location}")

        # -----------------------------------------------------------------------
        # Verify start and destinations waypoints are on the same directed lane
        mp = world.get_map()
        wp_start = mp.get_waypoint(EGO_START, project_to_road=True, lane_type=carla.LaneType.Driving)
        wp_end = mp.get_waypoint(EGO_DEST, project_to_road=True, lane_type=carla.LaneType.Driving)

        print(f"Start waypoint: road_id={wp_start.road_id}, lane_id={wp_start.lane_id}, yaw={wp_start.transform.rotation.yaw} is_junction={wp_start.is_junction}")
        print(f"End waypoint: road_id={wp_end.road_id}, lane_id={wp_end.lane_id}, yaw={wp_end.transform.rotation.yaw} is_junction={wp_end.is_junction}")

        # is the destination ahead along the lane direction?
        fwd = wp_start.transform.get_forward_vector()
        vec = wp_end.transform.location - wp_start.transform.location
        ahead = (fwd.x * vec.x + fwd.y * vec.y + fwd.z * vec.z) > 0.0
        print(f"Destination is ahead along lane direction: {ahead}")
        # -----------------------------------------------------------------------

        # --- SPEED CONTROL ------------------------------------------------------
        # In 0.9.15 BehaviorAgent overwrites planner speed each tick from its behavior profile.
        # So raise the profile cap *and* the planner speed together.
        TARGET_KMH = 91.454

        # Raise behavior-profile max (private attr but reliable in 0.9.15)
        if hasattr(agent, "_behavior") and hasattr(agent._behavior, "max_speed"):
            agent._behavior.max_speed = TARGET_KMH
            print(f"BehaviorAgent: _behavior.max_speed = {TARGET_KMH}")

        # Also set agent-level target speed (some versions honor this)
        if hasattr(agent, "set_target_speed"):
            agent.set_target_speed(TARGET_KMH)
            print(f"BehaviorAgent: set_target_speed({TARGET_KMH}) called")
        elif hasattr(agent, "set_speed"):
            agent.set_speed(TARGET_KMH)
            print(f"BehaviorAgent: set_speed({TARGET_KMH}) called")

        # And set the LocalPlanner speed (what run_step reads right now)
        lp = agent.get_local_planner()
        if hasattr(lp, "set_speed"):
            lp.set_speed(TARGET_KMH)
            print(f"LocalPlanner: set_speed({TARGET_KMH}) called")
        # --- END SPEED CONTROL ---

        print("Starting journey")
    
        # --- Main loop: drive to destination while recording data ----------------------
        # Open meta file
        mf = open(meta_path, 'w', buffering=1)

        # Time loop
        start = time.time()
        frames_to_record = int(duration_s * hz)
        print(f"[INFO] Starting drive + capture loop")
        print(f"[INFO] Recording {frames_to_record} frames at {hz} Hz (~{duration_s:.1f} s)")

        recording = False
        recorded_frames = 0

        #frame_idx = 0

        total_ticks = int(round(DURATION_S * PHYS_HZ))
        decim = RECORD_EVERY_N
        sim_time = 0.0

        for tick_idx in range(total_ticks):
            print(f"--- Frame {tick_idx+1}/{frames_to_record} ---")
            # 1) Decide & apply control for THIS step
            control = agent.run_step()
            vehicle.apply_control(control)

            # 2) Advance simulation one fixed step
            frame_id = world.tick()
            #sim_time = (i + 1) / hz

            # Only record on selected ticks (0, 5, 10, 15... for RECORD_EVERY_N=5)
            if tick_idx % decim != 0:
                continue

            
            # 3) Wait for sensors ONLY on recording ticks
            t0 = time.time()
            while (frame_id not in store.rgb or 
                frame_id not in store.seg or 
                frame_id not in store.seg_raw or
                frame_id not in store.depth_m):
                if time.time() - t0 > 2.0:
                    print(f"[WARN] Timeout waiting for sensors at frame {frame_id}")
                    break
                #world.wait_for_tick()
                time.sleep(0.001)

            # 4) Compute summaries
            ego = ego_state(vehicle)
            lane = lane_context(world, vehicle)
            weather = weather_summary(world)
            actors, lead = summarize_actors(world, vehicle, max_n=5)
            risk = risk_from_lead(ego, lead)

            # 4.5) print velocity for debug
            velocity = vehicle.get_velocity()
            speed_mps = math.sqrt(velocity.x**2 + velocity.y**2 + velocity.z**2)
            speed_kmh = speed_mps * 3.6
            speed_mph = speed_mps * 2.23694
            print(f"Speed: {speed_kmh:5.1f} km/h ({speed_mph:5.1f} mph)")

            # 5) Save artifacts
            rgb = store.rgb.get(frame_id)
            seg = store.seg.get(frame_id)
            seg_ids = store.seg_raw.get(frame_id)
            depth_m = store.depth_m.get(frame_id)

            if rgb is not None:
                save_png_rgb(session_dir / 'frames' / f"{frame_id:08d}.png", rgb)
            if seg is not None:
                save_png_seg_palette(session_dir / 'seg' / f"{frame_id:08d}.png", seg)
            if seg_ids is not None:
                save_png_seg_ids(session_dir / 'seg_raw' / f"{frame_id:08d}.png", seg_ids)
            if depth_m is not None:
                save_depth_npy(session_dir / 'depth' / f"{frame_id:08d}.npy", depth_m)
            
            # 6) Write metadata JSON line
            sim_time = tick_idx / PHYS_HZ
            record = FrameRecord(
                frame_id=frame_id,
                sim_time=sim_time,
                rgb_path=str(pathlib.Path('frames') / f"{frame_id:08d}.png"),
                seg_path=str(pathlib.Path('seg') / f"{frame_id:08d}.png"),
                seg_raw_path=str(pathlib.Path('seg_raw') / f"{frame_id:08d}.png"),
                depth_path=str(pathlib.Path('depth') / f"{frame_id:08d}.npy"),
                ego=ego,
                lane=lane,
                weather=weather,
                actors=actors,
                risk=risk,
            )

            if recorded_frames <= TARGET_RECORD_FRAMES and speed_kmh>=86:
                mf.write(json.dumps(asdict(record)) + "\n")
                recorded_frames += 1
                print(f"[INFO] Recorded frame {recorded_frames}/{TARGET_RECORD_FRAMES} frames; stopping.")

            # 7) Cleanup old frames from store and early-exit if arrived
            if agent.done():
                print("Destination reached")
                break
            store.clear_older_than(frame_id)
            #frame_idx += 1



         # Optional grace tick window after arrival
        print("Waiting after destination for 5 seconds...")
        # Stop the sensor listeners to avoid accumulating too many frames in the store
        for s in sensors:
            try:
                s.stop()
            except Exception:
                pass
        deadline = time.time() + 5.0
        while time.time() < deadline:
            world.tick()
        
        print(f"[INFO] Session completed, data saved to: {session_dir}")

    finally:
        print("[INFO] Cleaning up...")
        if mf:
            try: 
                mf.close()
            except Exception:
                pass
        for s in sensors:
            try:
                s.stop(); s.destroy()
            except Exception:
                pass
        if vehicle is not None:
            try:
                vehicle.destroy()
            except Exception:
                pass

        # Return world to async to not block other scripts
        try:
            settings = world.get_settings()
            settings.synchronous_mode = False
            settings.fixed_delta_seconds = None
            world.apply_settings(settings)
        except Exception:
            pass


def main():

    run(hz=PHYS_HZ, duration_s=DURATION_S, map_name=DEFAULT_MAP_NAME, dest_loc=EGO_DEST)


    #show_spawn_points(world, points_color=carla.Color(0, 255, 0))


if __name__ == '__main__':
    main()