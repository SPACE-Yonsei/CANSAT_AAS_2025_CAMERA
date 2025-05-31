# Python FSW V2 Camera App
# Author : Hyeon Lee

# for priority management, import os
import os

from lib import appargs
from lib import msgstructure
from lib import logging
from lib import events
from lib import types

import signal
from multiprocessing import Queue, connection
import threading
import time

# Runstatus of application. Application is terminated when false
CAMERAAPP_RUNSTATUS = True

######################################################
## FUNDEMENTAL METHODS                              ##
######################################################

# SB Methods
# Methods for sending/receiving/handling SB messages

# Handles received message
def command_handler (recv_msg : msgstructure.MsgStructure):
    global CAMERAAPP_RUNSTATUS

    if recv_msg.MsgID == appargs.MainAppArg.MID_TerminateProcess:
        # Change Runstatus to false to start termination process
        events.LogEvent(appargs.CameraAppArg.AppName, events.EventType.info, f"CAMERAAPP TERMINATION DETECTED")
        CAMERAAPP_RUNSTATUS = False

    # When received activate camera
    elif recv_msg.MsgID == appargs.CommAppArg.MID_RouteCmd_CAM:
        events.LogEvent(appargs.CameraAppArg.AppName, events.EventType.info, f"CAMERA {recv_msg.data} COMMAND RECEIVED")
        if recv_msg.data == "ON":
            picam_start_recording()
            fit0892_start_recording()
        elif recv_msg.data == "OFF":
            picam_stop_recording()
            fit0892_stop_recording()
    
    elif recv_msg.MsgID == appargs.FlightlogicAppArg.MID_SendCameraActivateToCam:
        events.LogEvent(appargs.CameraAppArg.AppName, events.EventType.info, f"CAMERA ACTIVATION BY LOGIC")
        picam_start_recording()
        fit0892_start_recording()

    else:
        events.LogEvent(appargs.CameraAppArg.AppName, events.EventType.error, f"MID {recv_msg.MsgID} not handled")
        
    return

def send_hk(Main_Queue : Queue):
    global CAMERAAPP_RUNSTATUS
    while CAMERAAPP_RUNSTATUS:
        cameraHK = msgstructure.MsgStructure()
        msgstructure.send_msg(Main_Queue, cameraHK, appargs.CameraAppArg.AppID, appargs.HkAppArg.AppID, appargs.CameraAppArg.MID_SendHK, str(CAMERAAPP_RUNSTATUS))
        time.sleep(1)
    return

######################################################
## INITIALIZATION, TERMINATION                      ##
######################################################

# Initialization
def cameraapp_init():
    global CAMERAAPP_RUNSTATUS

    picam_instance = None
    picamencoder_instance = None

    # Disable Keyboardinterrupt since Termination is handled by parent process
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    events.LogEvent(appargs.CameraAppArg.AppName, events.EventType.info, "Initializating cameraapp")

    ## User Defined Initialization goes HERE

    # Initialization of picamera
    try:
        picam_instance, picamencoder_instance = picam.init_cam()
    except Exception as e:
        events.LogEvent(appargs.CameraAppArg.AppName, events.EventType.error, f"Error Initializing picam : {e}")

    # Initially start the cameras
    picam_start_recording() # Turns the recording flag to True
    fit0892_start_recording() # Spawns the recording subprocess

    events.LogEvent(appargs.CameraAppArg.AppName, events.EventType.info, "Cameraapp Initialization Complete")

    return picam_instance, picamencoder_instance

# Termination
def cameraapp_terminate(picam_instance):
    global CAMERAAPP_RUNSTATUS

    CAMERAAPP_RUNSTATUS = False
    events.LogEvent(appargs.CameraAppArg.AppName, events.EventType.info, "Terminating cameraapp")

    # Termination Process Comes Here

    # Terminating fit0892 process
    fit0892_stop_recording()
    picam_stop_recording()
    
    # Terminating picam
    picam.terminate(picam_instance)

    # Join Each Thread to make sure all threads terminates
    for thread_name in thread_dict:
        events.LogEvent(appargs.CameraAppArg.AppName, events.EventType.info, f"Terminating thread {thread_name}")
        thread_dict[thread_name].join()
        events.LogEvent(appargs.CameraAppArg.AppName, events.EventType.info, f"Terminating thread {thread_name} Complete")

    # The termination flag should switch to false AFTER ALL TERMINATION PROCESS HAS ENDED
    events.LogEvent(appargs.CameraAppArg.AppName, events.EventType.info, "Terminating cameraapp complete")
    return

######################################################
## USER METHOD                                      ##
######################################################
from camera import fit0892
from camera import picam

CAMERA_RECORD_SEC = 7

PICAM_RECORDING = False

# Simple wrapup function for managing camera
def picam_start_recording():
    global PICAM_RECORDING
    PICAM_RECORDING = True
    picam.PICAM_RECORDING = True
    
    events.LogEvent(appargs.CameraAppArg.AppName, events.EventType.info, f"Picam recording flag is TRUE")
    return

def picam_stop_recording():
    global PICAM_RECORDING
    PICAM_RECORDING = False
    picam.PICAM_RECORDING = False

    events.LogEvent(appargs.CameraAppArg.AppName, events.EventType.info, f"Picam recording flag is FALSE")
    return

def fit0892_start_recording():
    fit0892.fit0892_start_recording_process(CAMERA_RECORD_SEC)
    events.LogEvent(appargs.CameraAppArg.AppName, events.EventType.info, f"Fit0892 recording process started")

def fit0892_stop_recording():
    fit0892.fit0892_terminate_recording_process()
    events.LogEvent(appargs.CameraAppArg.AppName, events.EventType.info, f"Fit0892 recording process stopped")


def picam_record_thread(picam_instance, picamencoder_instance):
    global CAMERAAPP_RUNSTATUS

    if picam_instance == None:
        events.LogEvent(appargs.CameraAppArg.AppName, events.EventType.error, f"Picam not initialized! Terminating thread")

    while CAMERAAPP_RUNSTATUS:
        if PICAM_RECORDING == True:
            try:
                events.LogEvent(appargs.CameraAppArg.AppName, events.EventType.info, f"Picam Recording Start")
                picam.record(picam_instance, picamencoder_instance, CAMERA_RECORD_SEC)
                events.LogEvent(appargs.CameraAppArg.AppName, events.EventType.info, f"Picam Recording End")

            except Exception as e:
                events.LogEvent(appargs.CameraAppArg.AppName, events.EventType.error, f"Error Recording picam : {e}")
                time.sleep(1)
        else:
            # Wait until Picam recording flag
            time.sleep(0.1)

    return
# Put user-defined methods here!

######################################################
## MAIN METHOD                                      ##
######################################################

thread_dict = dict[str, threading.Thread]()

from lib import config

# This method is called from main app. Initialization, runloop process
def cameraapp_main(Main_Queue : Queue, Main_Pipe : connection.Connection):

    # Camera app is not used in Container, Rocket
    if config.FSW_CONF == config.CONF_ROCKET or config.FSW_CONF == config.CONF_CONTAINER:
        events.LogEvent(appargs.CameraAppArg.AppName, events.EventType.info, f"Camera is only used in payload. Terminating")
        return
    
    global CAMERAAPP_RUNSTATUS
    CAMERAAPP_RUNSTATUS = True

    # Initialization Process
    picam_instance, picamencoder_instance = cameraapp_init()

    # Spawn SB Message Listner Thread
    thread_dict["HKSender_Thread"] = threading.Thread(target=send_hk, args=(Main_Queue, ), name="HKSender_Thread")
    thread_dict["PicamRecorder_Thread"]  = threading.Thread(target=picam_record_thread, args=(picam_instance, picamencoder_instance), name="PicamRecorder_Thread")

    # Spawn Each Threads
    for thread_name in thread_dict:
        thread_dict[thread_name].start()

    try:
        while CAMERAAPP_RUNSTATUS:
            # Receive Message From Pipe
            message = Main_Pipe.recv()
            recv_msg = msgstructure.MsgStructure()

            # Unpack Message, Skip this message if unpacked message is not valid
            if msgstructure.unpack_msg(recv_msg, message) == False:
                continue
            
            # Validate Message, Skip this message if target AppID different from cameraapp's AppID
            # Exception when the message is from main app
            if recv_msg.receiver_app == appargs.CameraAppArg.AppID or recv_msg.receiver_app == appargs.MainAppArg.AppID:
                # Handle Command According to Message ID
                command_handler(recv_msg)
            else:
                events.LogEvent(appargs.CameraAppArg.AppName, events.EventType.error, "Receiver MID does not match with cameraapp MID")

    # If error occurs, terminate app
    except Exception as e:
        events.LogEvent(appargs.CameraAppArg.AppName, events.EventType.error, f"cameraapp error : {e}")
        CAMERAAPP_RUNSTATUS = False

    # Termination Process after runloop
    cameraapp_terminate(picam_instance)

    return
