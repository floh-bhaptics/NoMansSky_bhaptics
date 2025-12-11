import bhaptics_python
import asyncio
import time
import threading
import logging

logging.basicConfig(filename='myapp.log', level=logging.INFO)
logger = logging.getLogger("NMS_bhaptics.bhaptics_library")


class bhaptics_suit:
    def __init__(self, app_id: str, api_key: str, app_name: str):
        super().__init__()
        self.app_id = app_id
        self.api_key = api_key
        self.app_name = app_name
        self.connected = False

    async def connect(self):
        try:
            result = await bhaptics_python.registry_and_initialize(self.app_id, self.api_key, self.app_name)
            if not result:
                logger.error("Failed to initialize bHaptics SDK")
            else:
                logger.info("bHaptics SDK initialized")
                self.play_pattern("heartbeat")
                self.connected = True
        except Exception as e:
            logger.error(f"Error initializing SDK: {e}")

    def play_pattern(self, pattern_name: str, intensity: int = 100):
        if not self.connected:
            logger.warn("Cannot send haptic signal: Suit not connected.")
            return

        try:
            if not isinstance(pattern_name, str):
                raise TypeError("Pattern name must be a string.")
            if not (0 <= intensity <= 100):
                raise ValueError("Intensity must be between 0 and 100.")

            request_id = bhaptics_python.play_event(pattern_name)
        except Exception as e:
            logger.warn(f"Failed to send haptic signal: {e}")



class TimerController:
    def __init__(self,bhaptics_mod_instance):
        self.pistol_laser_interval = 0.07
        self.pistol_laser_running = False
        self.pistol_laser_thread = None
        self.pistol_laser_lock = threading.Lock()

        self.scan_interval = 0.1  # 100ms
        self.scan_running = False
        self.scan_thread = None
        self.scan_lock = threading.Lock()

        self.spacejump_interval = 1  # 100ms
        self.spacejump_running = False
        self.spacejump_thread = None
        self.spacejump_lock = threading.Lock()

        self.bhaptics_mod = bhaptics_mod_instance
        self.myTactsuit = self.bhaptics_mod.myTactsuit
    
    def _pistol_laser_worker(self):
        while True:
            with self.pistol_laser_lock:
                if not self.pistol_laser_running:
                    break
            if self.bhaptics_mod.get_player_hand() == 0:
                # logger.info("RightHandPistolLaserShoot")
                self.myTactsuit.play_pattern("heartbeat")
            else:
                # logger.info("LeftHandPistolLaserShoot")
                self.myTactsuit.play_pattern("LeftHandPistolLaserShoot")
            time.sleep(self.pistol_laser_interval)
    
    def start_pistol_laser(self):
        with self.pistol_laser_lock:
            if self.pistol_laser_running:
                return
            self.pistol_laser_running = True
        
        self.pistol_laser_thread = threading.Thread(target=self._pistol_laser_worker, daemon=True,name="PistolLaserTimer")
        self.pistol_laser_thread.start()
    
    def stop_pistol_laser(self):
        with self.pistol_laser_lock:
            if not self.pistol_laser_running:
                return
            self.pistol_laser_running = False
        
        if self.pistol_laser_thread:
            self.pistol_laser_thread.join()

    def _scan_worker(self):
        while True:
            with self.scan_lock:
                if not self.scan_running:
                    break
            # logger.info("Scanning")
            self.myTactsuit.play_pattern("Scanning")
            time.sleep(self.scan_interval)
    
    def start_scan(self):
        with self.scan_lock:
            if self.scan_running:
                return
            self.scan_running = True
        
        self.scan_thread = threading.Thread(target=self._scan_worker, daemon=True,name="ScanTimer")
        self.scan_thread.start()
    
    def stop_scan(self):
        with self.scan_lock:
            if not self.scan_running:
                return
            self.scan_running = False
        
        if self.scan_thread:
            self.scan_thread.join()

    def _spacejump_worker(self):
        while True:
            with self.spacejump_lock:
                if not self.spacejump_running:
                    break
            # logger.info("SpaceJump")
            self.myTactsuit.play_pattern("SpaceshipPulse")
            time.sleep(self.spacejump_interval)
    
    def start_spacejump(self):
        with self.spacejump_lock:
            if self.spacejump_running:
                return
            self.spacejump_running = True
        
        self.spacejump_thread = threading.Thread(target=self._spacejump_worker, daemon=True,name="SpaceJumpTimer")
        self.spacejump_thread.start()
    
    def stop_spacejump(self):
        with self.spacejump_lock:
            if not self.spacejump_running:
                return
            self.spacejump_running = False
        
        if self.spacejump_thread:
            self.spacejump_thread.join()
