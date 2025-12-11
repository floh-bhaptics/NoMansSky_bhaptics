
# /// script
# dependencies = ["pymhf==0.1.11.dev27"]
#
# [tool.uv.sources]
# pymhf = { index = "pypi_test" }
#
# [[tool.uv.index]]
# name = "pypi_test"
# url = "https://test.pypi.org/simple/"
# explicit = true
# 
# [tool.pymhf]
# exe = "NMS.exe"
# steam_gameid = 275850
# start_paused = false
# 
# [tool.pymhf.logging]
# log_dir = "."
# log_level = "info"
# window_name_override = "No Mans Sky bhaptics mod"
# ///



import threading
import ctypes
from typing import Annotated, Optional
import time
import logging

from pymhf import Mod, load_mod_file, FUNCDEF
from pymhf.core.memutils import get_addressof
from pymhf.core.hooking import static_function_hook
from pymhf.core.hooking import function_hook, Structure
from pymhf.core.memutils import map_struct, get_addressof
from pymhf.utils.partial_struct import partial_struct, Field
from pymhf.extensions.cpptypes import std
from pymhf.core.utils import set_main_window_active
from pymhf.gui.decorators import gui_button
from bhaptics_library import bhaptics_suit, TimerController


# logging.basicConfig(filename='myapp.log', level=logging.INFO)
logger = logging.getLogger("NMS_bhaptics")

class cTkVector4f(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
        ("z", ctypes.c_float),
        ("w", ctypes.c_float),
    ]

@partial_struct
class TkAudioID(ctypes.Structure):
    mpacName: Annotated[Optional[str], Field(ctypes.c_char_p)]
    muID: Annotated[int, Field(ctypes.c_uint32)]
    mbValid: Annotated[bool, Field(ctypes.c_bool)]

class cGcPlayer(Structure):
    @function_hook("48 8B C4 48 89 58 ?? 4C 89 48 ?? 44 89 40 ?? 55 56 57 41 54 41 55 41 56 41 57 48 8D A8")
    def TakeDamage(self, this: ctypes.c_uint64,damageAmount:ctypes.c_float, damageType:ctypes.c_uint32, damageId:ctypes.c_char_p, dir_:ctypes.POINTER(cTkVector4f), owner:ctypes.c_ulonglong, effectsDamageMultipliers:ctypes.c_ulonglong):
        pass

    @function_hook("40 53 48 81 EC E0 00 00 00 48 8B D9 E8 ?? ?? ?? ?? 83 78 10 05")
    def OnEnteredCockpit(self, this: ctypes.c_uint64):
        pass

    @function_hook("40 53 48 83 EC 20 48 8B 1D ?? ?? ?? ?? E8 ?? ?? ?? ?? 83 78 10 05 75 ?? 48 8B")
    def GetDominantHand(self, this: ctypes.c_uint64 ,_result_:ctypes.c_int64) -> ctypes.c_int64:
        pass

class cTkAudioManager(Structure):
    @function_hook("48 83 EC ? 33 C9 4C 8B D2 89 4C 24 ? 49 8B C0 48 89 4C 24 ? 45 33 C9")
    def Play(
        self,
        this: ctypes.c_ulonglong,
        event: ctypes.c_ulonglong,
        object: ctypes.c_int64,
    ) -> ctypes.c_bool:
        pass

class cGcLaserBeam(Structure):
    @function_hook("48 89 5C 24 10 57 48 83 EC 50 48 83 B9")
    def Fire(self, this: ctypes.c_uint64):
        pass

class cGcTerrainEditorBeam(Structure):
    @function_hook("48 8B C4 48 89 58 18 48 89 70 20 55 57 41 54 41 55 41 57 48 8D A8 ?? ?? FF FF")
    def Fire(self, this: ctypes.c_uint64):
        pass  

    @function_hook("48 8B C4 48 89 58 10 48 89 70 18 55 57 41 56 48 8D 68 A1 48 81 EC ?? 00 00 00 8B")
    def StartEffect(self, this: ctypes.c_uint64):
        pass  

    @function_hook("4C 89 44 24 18 55 53 56 57 41 54 41 55 41 56 48 8D AC 24 ?? FE FF FF 48")
    def ApplyTerrainEditStroke(self, this: ctypes.c_uint64):
        pass  

    @function_hook("48 8B C4 4C 89 40 18 48 89 48 08 55 53 56 57 41 56 41 57 48 8D A8")
    def ApplyTerrainEditFlatten(self, this: ctypes.c_uint64):
        pass  

class cGcNetworkWeapon(Structure):
    @function_hook("40 53 41 56 41 57 48 81 EC E0 00 00 00 8D 41 ?? 4D 8B D1")
    def FireRemote(self, this: ctypes.c_uint64):
        pass  

class cGcLocalPlayerCharacterInterface(Structure):
    @function_hook("40 53 48 83 EC 20 48 8B 1D ?? ?? ?? ?? 48 8D 8B ?? ?? ?? 00 E8 ?? ?? ?? 00")
    def IsJetpacking(self, this: ctypes.c_uint64,result: ctypes.c_ubyte,_result_:ctypes.c_ubyte) ->  ctypes.c_ubyte:
        pass  

class cGcSpaceshipComponent(Structure):
    @function_hook("48 89 5C 24 18 48 89 54 24 10 57 48 83 EC 70 41 0F B6 F8")
    def Eject(self, this: ctypes.c_uint64):
        pass  

class cGcSpaceshipWarp(Structure):
    @function_hook("48 83 EC 38 48 8B 0D ?? ?? ?? ?? 41 B9 01 00 00 00 48 81 C1 30 B3 00 00 C7 44 24 20 FF FF FF FF BA 9A")
    def GetPulseDriveFuelFactor(self, this: ctypes.c_uint64,_result_:ctypes.c_float) -> ctypes.c_float:
        pass

class cGcSpaceshipWeapons(Structure):
    @function_hook("48 63 81 ?? ?? 00 00 80 BC 08 ?? ?? 00 00 00 74 12")
    def GetOverheatProgress(self, this: ctypes.c_uint64,_result_:ctypes.c_float) -> ctypes.c_float:
        pass 

    @function_hook("48 89 5C 24 08 57 48 83 EC 20 48 8B D9 48 8B 49 08 48 8B 01 FF 90 90 01 00 00 84 C0 0F 85 88 00 00 00")
    def GetCurrentShootPoints(self, this: ctypes.c_uint64):
        pass

class cGcPlayerCharacterComponent(Structure):
    @function_hook("48 8B C4 55 53 56 57 41 56 48 8D 68 A1 48 81 EC 90 00 00")
    def SetDeathState(self, this: ctypes.c_uint64):
        pass




class bHapticsMod(Mod):
    def __init__(self):
        super().__init__()
        self.isPistolLaserFire = False
        self.isInSpaceship = False
        self.isInSpaceJump = False
        self.lastFuelFactor = 1
        self.lastJetpackTime = 0
        self.lastLaserTime = 0
        self.playerHand = 0
        self.timerController = TimerController(self)
        time.sleep(5)
        logger.info("Initializing suit...")
        self.myTactsuit = bhaptics_suit(app_id="693ac4ffa277918a719a1bd8", api_key="uSEDPxsVOpRefEGM7FAc", app_name="No Man's Sky")


    def get_player_hand(self):
        return self.playerHand

    @cGcPlayerCharacterComponent.SetDeathState.after
    def SetDeathState(self, *args):
        # logger.info("PlayerDeath")
        self.myTactsuit.play_pattern("PlayerDeath")
        # logger.info(args)

    @cGcPlayer.TakeDamage.after
    def TakeDamage(self, this, damageAmount, damageType, damageId, dir_, owner, effectsDamageMultipliers):
        direction = dir_.contents
        if damageId == "LANDING":
            # logger.info("FallDamage")
            self.myTactsuit.play_pattern("FallDamage")
        else:
            # logger.info("DefaultDamage")
            self.myTactsuit.play_pattern("DefaultDamage")
        # logger.info(f"damageAmount: {damageAmount},damageType :{damageType}, damageId: {damageId} , direction ({direction.x}, {direction.y}, {direction.z})")

    @cGcPlayer.OnEnteredCockpit.after
    def OnEnteredCockpit(self, *args):
        # logger.info(f"GetOnSpaceship")        
        self.isInSpaceship = True
        if not self.isInSpaceJump:
            self.myTactsuit.play_pattern("GetOnSpaceship")
        # logger.info(args)

    @cGcPlayer.GetDominantHand.after
    def GetDominantHand(self, *args,_result_):
        self.playerHand = _result_
        # logger.info(f"GetDominantHand")
        # logger.info(f"Result:{_result_}")
        # logger.info(args)

    @cTkAudioManager.Play.after
    def after_play(self, this, event, object_):
        audioID = map_struct(event, TkAudioID)
        if audioID.muID == 2149772978:
            # logger.info(f"ScanWave")
            self.myTactsuit.play_pattern("ScanWave")
        elif audioID.muID == 2815161641:
            # logger.info(f"CollectItem")
            self.myTactsuit.play_pattern("CollectItem")
        elif audioID.muID == 3451007219:
            if not self.isInSpaceJump:
                # logger.info(f"SpaceshipSpeedUp")
                self.myTactsuit.play_pattern("SpaceshipSpeedUp")
        elif audioID.muID == 3903008093:
            # logger.info(f"SpaceshipOnGround")
            self.myTactsuit.play_pattern("SpaceshipOnGround")
        elif audioID.muID == 514090887:
            # logger.info(f"SpaceshipTakeOff")
            self.myTactsuit.play_pattern("SpaceshipTakeOff")
        elif audioID.muID == 1335995103:
            # logger.info(f"SpaceshipEnterGalaxyMap")
            self.myTactsuit.play_pattern("SpaceshipSpeedUp")
        elif audioID.muID == 1261594536:
            # logger.info(f"StartSpaceJump")
            self.isInSpaceJump = True
            self.timerController.start_spacejump()
        elif audioID.muID == 1511168854 or audioID.muID == 2852869421:
            # logger.info(f"StopSpaceJump")
            self.isInSpaceJump = False
            self.timerController.stop_spacejump()
        elif audioID.muID == 2223503391 or audioID.muID == 3201991932 or audioID.muID == 3141878185:
            # logger.info(f"StartPistolLaser")
            self.isPistolLaserFire = True
            self.timerController.start_pistol_laser()
        elif audioID.muID == 2191565963 or audioID.muID == 867290390 or audioID.muID == 2852869421:
            # logger.info(f"StopPistolLaser")
            self.isPistolLaserFire = False
            self.timerController.stop_pistol_laser()
        elif audioID.muID == 3315033225:
            # logger.info(f"StartScan")
            self.timerController.start_scan()
        elif audioID.muID == 290149060 or audioID.muID == 2852869421:
            # logger.info(f"StopScan")
            self.timerController.stop_scan()

    @cGcNetworkWeapon.FireRemote.after
    def FireRemote(self, *args):
        if self.isPistolLaserFire:
            return
        if self.isInSpaceship:
            # logger.info("SpaceshipWeaponShoot")
            self.myTactsuit.play_pattern("SpaceshipWeaponShoot")
        else:
            if self.playerHand == 0:
                # logger.info("RightHandPistolShoot")
                self.myTactsuit.play_pattern("RightHandPistolShoot")
            else:
                # logger.info("LeftHandPistolShoot")
                self.myTactsuit.play_pattern("LeftHandPistolShoot")

    @cGcLocalPlayerCharacterInterface.IsJetpacking.after
    def IsJetpacking(self,result, *args,_result_):
        if _result_ == 1:
            if time.perf_counter() - self.lastJetpackTime > 0.1:
                self.lastJetpackTime = time.perf_counter()
                # logger.info("PlayerUsingJetpack")
                self.myTactsuit.play_pattern("PlayerUsingJetpack")
        # logger.info(f"-----------------------------------------------")
        # logger.info(f"cGcLocalPlayerCharacterInterface::IsJetpacking")
        # logger.info(f"Result:{_result_}")
        # logger.info(f"cGcLocalPlayerCharacterInterface::IsJetpacking")
        # logger.info(args)
        
    @cGcSpaceshipComponent.Eject.after
    def Eject(self, *args):
        # logger.info(f"GetOffSpaceship")
        self.isInSpaceship = False
        self.myTactsuit.play_pattern("GetOffSpaceship")
        # logger.info(args)
    
    @cGcSpaceshipWarp.GetPulseDriveFuelFactor.after
    def GetPulseDriveFuelFactor(self,this, *args,_result_):
        if _result_ > self.lastFuelFactor:
            # logger.info(f"PulseEngineHealing")
            # self.myTactsuit.play_pattern("PulseEngineHealing")
            self.lastFuelFactor = _result_
            return
        if self.lastFuelFactor != _result_:
            if self.lastFuelFactor == 1 and _result_ < 0.95:
                self.lastFuelFactor = _result_
                return
            self.lastFuelFactor = _result_
            # logger.info(f"SpaceshipPulse")
            self.myTactsuit.play_pattern("SpaceshipPulse")
            # logger.info(f"Result:{_result_}")
            # logger.info(args)


if __name__ == "__main__":
    load_mod_file(__file__)

