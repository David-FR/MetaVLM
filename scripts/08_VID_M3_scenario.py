#!/usr/bin/env python3
"""
08_VID_M3: Rural Highway — Model 3 FSD Tree Crash
CARLA AV crash scenario reconstruction script.
FSD swerves left abruptly on rural highway
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

sys.path.insert(0, str(CARLA_PY_DIR))
eggs = glob.glob(EGG_PATTERN)
if eggs:
    sys.path.insert(0, eggs[0])
sys.path.insert(0, str(PYTHONAPI_ROOT))

from carla import VehicleLightState as vls
import carla
print("Using carla from:", carla.__file__)

from agents.navigation.behavior_agent import BehaviorAgent
from agents.navigation.basic_agent import BasicAgent

egg_glob = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'carla', 'dist', 'carla-*%d.%d-%s.egg' % (
    sys.version_info.major,
    sys.version_info.minor,
    'win-amd64' if os.name == 'nt' else 'linux-x86_64'
)))
for p in glob.glob(egg_glob):
    sys.path.insert(0, p)

# ========================= SCENARIO CONFIG ====================================
# Spectator camera position (for CARLA viewport)
spectator_position_x = 30
spectator_position_y = -200
spectator_position_z = 20
spectator_rotation_yaw = 20
spectator_rotation_pitch = -25
spectator_rotation_roll = 0.0

# Simulation parameters
DEFAULT_HZ = 6.0
IMG_WIDTH, IMG_HEIGHT = 1280, 720
FOV_DEG = 90.0

PHYS_HZ = 30.0
RECORD_EVERY_N = 5
DURATION_S = 10

# Map and vehicle
DEFAULT_MAP_NAME = 'Town07'
EGO_BLUEPRINT_FILTER = 'vehicle.tesla.model3'

# Ego start/destination
EGO_START = carla.Location(x=13.63, y=-238.25, z=0.88)
EGO_DEST = carla.Location(x=58.30, y=-156.06, z=9.46)

# ========================= DATA CLASSES =======================================
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

# ========================= CORE FUNCTIONS =====================================
def change_map(client, world, map_name=DEFAULT_MAP_NAME):
    time.sleep(2)
    print("Before trying to change map")
    if world.get_map().name != map_name:
        print(f"Changing map to: {map_name}")
        client.load_world(map_name, False)
    else:
        print(f"Map is already {map_name}, no need to change.")
    time.sleep(2)


def make_session_dir(base_dir: pathlib.Path = pathlib.Path('./sessions')) -> pathlib.Path:
    sid = time.strftime('%Y%m%d_%H%M%S') + '_' + str(uuid.uuid4())[:8]
    out = base_dir / sid
    (out / 'frames').mkdir(parents=True, exist_ok=True)
    (out / 'seg').mkdir(parents=True, exist_ok=True)
    (out / 'seg_raw').mkdir(parents=True, exist_ok=True)
    (out / 'depth').mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Session dir: {{out}}")
    return out


def configure_world_sync(world: carla.World, hz: float, weather_preset=None) -> None:
    settings = world.get_settings()
    settings.synchronous_mode = True
    settings.fixed_delta_seconds = 1.0 / hz
    settings.substepping = False
    world.apply_settings(settings)
    world.tick()
    if weather_preset:
        world.set_weather(weather_preset)
    print(f"finished configuring world...")


def move_spectator(world, x, y, z, yaw, pitch, roll):
    spectator = world.get_spectator()
    transform = carla.Transform(
        carla.Location(x, y, z),
        carla.Rotation(yaw=yaw, pitch=pitch, roll=roll)
    )
    spectator.set_transform(transform)
    print("Moved spectator")


def show_spawn_points(world, points_color=carla.Color(0, 255, 0)):
    spawn_points = world.get_map().get_spawn_points()
    print("Number of spawnpoints", len(spawn_points))
    for spawn_point in spawn_points:
        world.debug.draw_point(
            spawn_point.location + carla.Location(z=0.5),
            size=0.1, color=points_color, life_time=10.0
        )


def spawn_ego(world: carla.World, start_loc: carla.Location) -> carla.Vehicle:
    print("Spawning ego vehicle...")
    bp_lib = world.get_blueprint_library()
    try:
        bp = bp_lib.find(EGO_BLUEPRINT_FILTER)
    except Exception:
        bp = random.choice(bp_lib.filter('vehicle.*'))

    bp.set_attribute('role_name', 'ego')

    wp = world.get_map().get_waypoint(start_loc, project_to_road=True, lane_type=carla.LaneType.Driving)
    transform = wp.transform
    transform.location.z += 0.5

    vehicle = world.try_spawn_actor(bp, transform)
    if not vehicle:
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
    return vehicle


def spawn_vehicle(world: carla.World, bp_id: str, transform: carla.Transform, role: str) -> carla.Vehicle:
    bp = world.get_blueprint_library().find(bp_id) if bp_id in [bp.id for bp in world.get_blueprint_library().filter('vehicle.*')] else random.choice(world.get_blueprint_library().filter('vehicle.*'))
    bp.set_attribute('role_name', role)
    veh = world.try_spawn_actor(bp, transform)
    if veh is None:
        wp = world.get_map().get_waypoint(transform.location, project_to_road=True, lane_type=carla.LaneType.Driving)
        for d in [2.0, 4.0, 6.0, 8.0]:
            cand = wp.next(d)
            if cand:
                t = cand[0].transform; t.location.z = max(t.location.z + 0.5, 0.5)
                veh = world.try_spawn_actor(bp, t)
                if veh: break
    if veh is None:
        raise RuntimeError(f"Failed to spawn vehicle role={{role}}")
    return veh


def spawn_pedestrian(world: carla.World, start_loc: carla.Location) -> Tuple:
    """Spawn a pedestrian and its AI controller. Returns (walker, controller)."""
    bp_lib = world.get_blueprint_library()
    walker_bp = random.choice(bp_lib.filter('walker.pedestrian.*'))
    if walker_bp.has_attribute('is_invincible'):
        walker_bp.set_attribute('is_invincible', 'false')

    spawn_tf = carla.Transform(start_loc, carla.Rotation())
    walker = world.try_spawn_actor(walker_bp, spawn_tf)
    if walker is None:
        # Try slightly adjusted positions
        for dz in [0.5, 1.0, 1.5]:
            adjusted = carla.Transform(carla.Location(start_loc.x, start_loc.y, start_loc.z + dz), carla.Rotation())
            walker = world.try_spawn_actor(walker_bp, adjusted)
            if walker:
                break
    if walker is None:
        raise RuntimeError("Failed to spawn pedestrian")

    # Spawn AI controller
    ctrl_bp = bp_lib.find('controller.ai.walker')
    controller = world.spawn_actor(ctrl_bp, carla.Transform(), attach_to=walker)
    return walker, controller


def freeze_all_lights_green(world: carla.World) -> int:
    n = 0
    for tl in world.get_actors().filter('traffic.traffic_light*'):
        try:
            tl.set_state(carla.TrafficLightState.Green)
            if hasattr(tl, "set_green_time"):
                tl.set_green_time(10_000.0)
                if hasattr(tl, "set_yellow_time"): tl.set_yellow_time(0.0)
                if hasattr(tl, "set_red_time"): tl.set_red_time(0.0)
            tl.freeze(True)
            n += 1
        except RuntimeError:
            pass
    world.tick()
    print(f"[INFO] Froze {{n}} traffic lights to GREEN")
    return n


def left_driving_lane(wp: carla.Waypoint) -> Optional[carla.Waypoint]:
    left = wp.get_left_lane() if hasattr(wp, 'get_left_lane') else None
    if left and left.lane_type == carla.LaneType.Driving:
        return left
    return None


def right_driving_lane(wp: carla.Waypoint) -> Optional[carla.Waypoint]:
    right = wp.get_right_lane() if hasattr(wp, 'get_right_lane') else None
    if right and right.lane_type == carla.LaneType.Driving:
        return right
    return None

# ========================= SENSORS & MATH =====================================
def add_camera(world: carla.World, parent: carla.Actor, kind: str) -> carla.Sensor:
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
    bp.set_attribute('sensor_tick', '0.0')

    relative_transform = carla.Transform(carla.Location(x=0.5, z=1.4), carla.Rotation(pitch=-2.0))
    sensor = world.spawn_actor(bp, relative_transform, attach_to=parent)
    return sensor


def _as_np_vec(loc) -> np.ndarray:
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
    ego_loc = vehicle.get_location()
    lane_center = wp.transform.location
    right = wp.transform.get_right_vector()
    vec = _as_np_vec(ego_loc - lane_center)
    lat_offset = float(np.dot(vec, _as_np_vec(right))) * -1.0

    ahead = [wp]
    dist = 0.0
    while dist < 30.0 and ahead[-1].next(2.0):
        nxt = ahead[-1].next(2.0)[0]
        ahead.append(nxt)
        dist += 2.0
    headings = [w.transform.rotation.yaw for w in ahead]
    if len(headings) >= 2 and dist > 0:
        yaw_rad = np.unwrap(np.radians(headings))
        dpsi = float(abs(yaw_rad[-1] - yaw_rad[0]))
        curvature = (dpsi / dist) * 1e6
    else:
        curvature = 0.0

    light_state = None
    dist_to_stop = None
    tl = vehicle.get_traffic_light()
    if tl is not None:
        try:
            light_state = tl.get_state().name
        except Exception:
            light_state = str(tl.state)
        try:
            stop_wps = tl.get_stop_waypoints()
            if stop_wps:
                cand = min(stop_wps, key=lambda w: w.transform.location.distance(ego_loc))
                dist_to_stop = float(cand.transform.location.distance(ego_loc))
        except Exception:
            dist_to_stop = float(tl.get_transform().location.distance(ego_loc))

    try:
        sl = float(vehicle.get_speed_limit())
    except Exception:
        sl = None

    return LaneContext(
        road_id=int(wp.road_id), lane_id=int(wp.lane_id),
        lane_width_m=float(wp.lane_width), lane_offset_m=float(lat_offset),
        curvature_1pm=float(curvature), speed_limit_kmh=sl,
        is_junction=bool(wp.is_junction), light_state=light_state,
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


def bearing_deg_to_location(ego: carla.Vehicle, target_loc: carla.Location) -> float:
    e_tf = ego.get_transform()
    fwd = np.array([e_tf.get_forward_vector().x, e_tf.get_forward_vector().y], dtype=np.float32)
    rel = np.array([target_loc.x - e_tf.location.x, target_loc.y - e_tf.location.y], dtype=np.float32)
    fwd /= (np.linalg.norm(fwd) + 1e-9)
    rel /= (np.linalg.norm(rel) + 1e-9)
    ang = math.degrees(math.atan2(fwd[0]*rel[1] - fwd[1]*rel[0], fwd.dot(rel)))
    return float(ang)


def steer_towards(actor: carla.Actor, target: carla.Location, max_abs: float = 0.7) -> float:
    b = bearing_deg_to_location(actor, target)
    steer = max(-max_abs, min(max_abs, b / 45.0))
    return float(steer)


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
            actor_id=int(v.id), cls='vehicle',
            role='lead' if lane_rel=='same' else 'adjacent',
            distance_m=dist, bearing_deg=bearing_deg(ego, v),
            rel_speed_mps=rs, lane_relation=lane_rel,
        )
        summaries.append(summ)

    for w in walkers:
        dist = float(w.get_location().distance(ego.get_location()))
        if dist > 40.0:
            continue
        br = bearing_deg(ego, w)
        if abs(br) > 60.0:
            continue
        rs = rel_speed_along_heading(ego, w)
        summaries.append(ActorSummary(
            actor_id=int(w.id), cls='pedestrian',
            role='crossing' if abs(br) > 15 else 'ahead',
            distance_m=dist, bearing_deg=br,
            rel_speed_mps=rs, lane_relation='n/a',
        ))

    summaries.sort(key=lambda s: s.distance_m)
    summaries = summaries[:max_n]

    for s in summaries:
        if s.cls == 'vehicle' and s.lane_relation == 'same':
            lead = s
            break

    return summaries, lead


def risk_from_lead(ego: EgoState, lead: Optional[ActorSummary]) -> RiskSummary:
    if lead is None:
        return RiskSummary(ttc_s=None, headway_s=None, gap_m=None, rel_speed_mps=None, target_class=None)
    gap = lead.distance_m
    rel_v = -lead.rel_speed_mps
    if rel_v > 0.05:
        ttc = gap / rel_v
    else:
        ttc = None
    headway = (gap / ego.speed_mps) if ego.speed_mps > 0.1 else None
    return RiskSummary(
        ttc_s=(float(ttc) if ttc is not None else None),
        headway_s=(float(headway) if headway is not None else None),
        gap_m=float(gap), rel_speed_mps=float(-lead.rel_speed_mps),
        target_class=lead.cls,
    )


def weather_summary(world: carla.World) -> WeatherSummary:
    w = world.get_weather()
    return WeatherSummary(
        rain=float(w.precipitation), fog=float(w.fog_density),
        wetness=float(w.wetness), cloudiness=float(w.cloudiness),
        sun_alt_deg=float(w.sun_altitude_angle), sun_az_deg=float(w.sun_azimuth_angle),
    )

# ========================= FRAME STORE & I/O ==================================
class FrameStore:
    def __init__(self):
        self.rgb: Dict[int, np.ndarray] = {}
        self.seg: Dict[int, np.ndarray] = {}
        self.seg_raw: Dict[int, np.ndarray] = {}
        self.depth_m: Dict[int, np.ndarray] = {}

    def clear_older_than(self, frame_id: int):
        def prune(d: Dict[int, Any]):
            for k in list(d.keys()):
                if k < frame_id - 5:
                    d.pop(k, None)
        prune(self.rgb); prune(self.seg); prune(self.seg_raw); prune(self.depth_m)


def depth_to_meters(image: carla.Image) -> np.ndarray:
    arr = np.frombuffer(image.raw_data, dtype=np.uint8).reshape((image.height, image.width, 4))
    b = arr[:, :, 0].astype(np.float32)
    g = arr[:, :, 1].astype(np.float32)
    r = arr[:, :, 2].astype(np.float32)
    normalized = (r + g * 256 + b * 256 * 256) / (256**3 - 1.0)
    return normalized * 1000.0


def seg_raw_to_ids(image: carla.Image) -> np.ndarray:
    arr = np.frombuffer(image.raw_data, dtype=np.uint8).reshape((image.height, image.width, 4))
    return arr[:, :, 2].copy()


def attach_and_listen(world: carla.World, vehicle: carla.Vehicle, store: 'FrameStore'):
    cam_rgb = add_camera(world, vehicle, 'rgb')
    cam_seg = add_camera(world, vehicle, 'seg')
    cam_depth = add_camera(world, vehicle, 'depth')

    def on_rgb(image: carla.Image):
        arr = np.frombuffer(image.raw_data, dtype=np.uint8).reshape((image.height, image.width, 4))
        store.rgb[image.frame] = arr[:, :, :3][:, :, ::-1].copy()

    def on_seg(image: carla.Image):
        image.convert(carla.ColorConverter.Raw)
        store.seg_raw[image.frame] = seg_raw_to_ids(image)
        image.convert(carla.ColorConverter.CityScapesPalette)
        arr = np.frombuffer(image.raw_data, dtype=np.uint8).reshape((image.height, image.width, 4))
        store.seg[image.frame] = arr[:, :, :3][:, :, ::-1].copy()

    def on_depth(image: carla.Image):
        store.depth_m[image.frame] = depth_to_meters(image)

    cam_rgb.listen(on_rgb)
    cam_seg.listen(on_seg)
    cam_depth.listen(on_depth)
    return cam_rgb, cam_seg, cam_depth


def save_png_rgb(path: pathlib.Path, rgb: np.ndarray):
    Image.fromarray(rgb).save(path)

def save_png_seg_palette(path: pathlib.Path, seg_vis: np.ndarray):
    Image.fromarray(seg_vis).save(path)

def save_png_seg_ids(path: pathlib.Path, ids: np.ndarray):
    Image.fromarray(ids.astype(np.uint8), mode='L').save(path)

def save_depth_npy(path: pathlib.Path, depth_m: np.ndarray):
    np.save(path, depth_m.astype(np.float32))

# ========================= MAIN RUN ===========================================
def run(hz: float, duration_s: float, map_name: str, dest_loc=None):
    client = carla.Client("localhost", 2000)
    client.set_timeout(10)
    world = client.get_world()

    if map_name:
        change_map(client, world, map_name)
        time.sleep(1)
        world = client.get_world()

    world.set_weather(carla.WeatherParameters.ClearNoon)

    move_spectator(world,
                   spectator_position_x, spectator_position_y, spectator_position_z,
                   spectator_rotation_yaw, spectator_rotation_pitch, spectator_rotation_roll)

    session_dir = make_session_dir()
    meta_path = session_dir / 'metadata.jsonl'

    ego: Optional[carla.Vehicle] = None
    sensors: List[carla.Sensor] = []
    mf = None
    actors_to_cleanup = []

    configure_world_sync(world, PHYS_HZ, carla.WeatherParameters.ClearNoon)

    try:
        ego = spawn_ego(world, EGO_START)
        actors_to_cleanup.append(ego)

        world.tick()
        time.sleep(3)

        ego.set_autopilot(False)
        ego_target_speed_mps = 20.0

        store = FrameStore()
        s_rgb, s_seg, s_dep = attach_and_listen(world, ego, store)
        sensors.extend([s_rgb, s_seg, s_dep])

        physics_control = ego.get_physics_control()
        physics_control.use_sweep_wheel_collision = True
        ego.apply_physics_control(physics_control)

        mf = open(meta_path, 'w', buffering=1)

        total_ticks = int(round(DURATION_S * PHYS_HZ))
        decim = RECORD_EVERY_N
        swerve_time = 4.0
        has_swerved = False

        for tick_idx in range(total_ticks):
            sim_time = tick_idx / PHYS_HZ
            current_speed = speed_of(ego)

            if sim_time < swerve_time:
                # Drive straight in lane
                ego_wp = world.get_map().get_waypoint(ego.get_location(), project_to_road=True)
                if ego_wp and ego_wp.next(10.0):
                    target_loc = ego_wp.next(10.0)[0].transform.location
                    steer = steer_towards(ego, target_loc, max_abs=0.3)
                else:
                    steer = 0.0
                throttle = 0.6 if current_speed < ego_target_speed_mps else 0.3
                brake = 0.0
            else:
                # Swerve left
                if not has_swerved:
                    print("[INFO] Ego swerving left!")
                    has_swerved = True

                ego_wp = world.get_map().get_waypoint(ego.get_location(), project_to_road=True)
                target_lane = left_driving_lane(ego_wp) if ego_wp else None

                if target_lane and target_lane.next(15.0):
                    target_loc = target_lane.next(15.0)[0].transform.location
                    steer = steer_towards(ego, target_loc, max_abs=0.7)
                else:
                    steer = 0.5
                throttle = 0.5 if current_speed < ego_target_speed_mps else 0.2
                brake = 0.0

            control = carla.VehicleControl(
                throttle=throttle, steer=-steer, brake=brake,
                hand_brake=False, reverse=False
            )
            ego.apply_control(control)

            frame_id = world.tick()

            if tick_idx % decim != 0:
                continue

            # Wait for sensors
            t0 = time.time()
            while (frame_id not in store.rgb or
                   frame_id not in store.seg or
                   frame_id not in store.seg_raw or
                   frame_id not in store.depth_m):
                if time.time() - t0 > 2.0:
                    print(f"[WARN] Timeout waiting for sensors at frame {frame_id}")
                    break
                time.sleep(0.001)

            # Compute summaries
            ego_sum = ego_state(ego)
            lane = lane_context(world, ego)
            wthr = weather_summary(world)
            actors, lead = summarize_actors(world, ego, max_n=5)
            risk = risk_from_lead(ego_sum, lead)

            # Print speed for debug
            velocity = ego.get_velocity()
            speed_mps = math.sqrt(velocity.x**2 + velocity.y**2 + velocity.z**2)
            speed_kmh = speed_mps * 3.6
            speed_mph = speed_mps * 2.23694
            print(f"Speed: {speed_kmh:5.1f} km/h ({speed_mph:5.1f} mph)")

            # Save artifacts
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

            # Write metadata JSON line
            sim_time = tick_idx / PHYS_HZ
            record = FrameRecord(
                frame_id=frame_id, sim_time=sim_time,
                rgb_path=str(pathlib.Path('frames') / f"{frame_id:08d}.png"),
                seg_path=str(pathlib.Path('seg') / f"{frame_id:08d}.png"),
                seg_raw_path=str(pathlib.Path('seg_raw') / f"{frame_id:08d}.png"),
                depth_path=str(pathlib.Path('depth') / f"{frame_id:08d}.npy"),
                ego=ego_sum, lane=lane, weather=wthr, actors=actors, risk=risk,
            )
            mf.write(json.dumps(asdict(record)) + "\n")

            # Cleanup
            store.clear_older_than(frame_id)


        # Grace ticks after completion
        print("Waiting after scenario for 5 seconds...")
        for s in sensors:
            try: s.stop()
            except Exception: pass
        deadline = time.time() + 5.0
        while time.time() < deadline:
            world.tick()

        print(f"[INFO] Session completed, data saved to: {session_dir}")

    finally:
        print("[INFO] Cleaning up...")
        if mf:
            try: mf.close()
            except Exception: pass
        for s in sensors:
            try: s.stop(); s.destroy()
            except Exception: pass
        for a in actors_to_cleanup:
            try: a.destroy()
            except Exception: pass
        try:
            settings = world.get_settings()
            settings.synchronous_mode = False
            settings.fixed_delta_seconds = None
            world.apply_settings(settings)
        except Exception:
            pass



def main():
    run(hz=PHYS_HZ, duration_s=DURATION_S, map_name=DEFAULT_MAP_NAME, dest_loc=EGO_DEST)


if __name__ == '__main__':
    main()
