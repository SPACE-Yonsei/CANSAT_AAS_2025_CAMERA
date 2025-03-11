# Python FSW V2 Camera App
# Author : Hyeon Lee

from lib import appargs
from lib import msgstructure
from lib import logging
from lib import events
from lib import types

import os
from multiprocessing import Queue, connection
import threading
import time
import sys

# Runstatus of application. Application is terminated when false
CAMERAAPP_RUNSTATUS = True

######################################################
## FUNDEMENTAL METHODS                              ##
######################################################

# SB Methods
# Methods for sending/receiving/handling SB messages

# This fuction is spawned as an independent thread
# Listens SB messages routed from main app using pipe
def SB_listner (Main_Pipe : connection.Connection):
    global CAMERAAPP_RUNSTATUS
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
    return

# Handles received message
def command_handler (recv_msg : msgstructure.MsgStructure):
    if recv_msg.MsgID == appargs.CameraAppArg.MID_SendHK:
        print(recv_msg.data)

    elif recv_msg.MsgID == appargs.MainAppArg.MID_TerminateProcess:
        # Change Runstatus to false to start termination process
        global CAMERAAPP_RUNSTATUS
        CAMERAAPP_RUNSTATUS = False

    else:
        events.LogEvent(appargs.CameraAppArg.AppName, events.EventType.error, f"MID {recv_msg.MsgID} not handled")
    return

# Send message to be routed
def send_message (Main_Queue : Queue, msg:str):
    Main_Queue.put(msg)
    return


######################################################
## INITIALIZATION, TERMINATION                      ##
######################################################

# Initialization
def cameraapp_init():
    events.LogEvent(appargs.CameraAppArg.AppName, events.EventType.info, "Starting cameraapp")
    ## User Defined Initialization goes HERE
    events.LogEvent(appargs.CameraAppArg.AppName, events.EventType.info, "cameraapp Started")

# Termination
def cameraapp_terminate():
    global CAMERAAPP_RUNSTATUS

    current_thread = threading.current_thread().name
        
    CAMERAAPP_RUNSTATUS = False
    events.LogEvent(appargs.CameraAppArg.AppName, events.EventType.info, "Terminating cameraapp")
    # Termination Process Comes Here

    # Join Each Thread to make sure all threads terminates
    for thread_name in thread_dict:
        events.LogEvent(appargs.CameraAppArg.AppName, events.EventType.info, f"Terminating thread {thread_name}")
        if thread_name != current_thread:
            thread_dict[thread_name].join()
        events.LogEvent(appargs.CameraAppArg.AppName, events.EventType.info, f"Terminating thread {thread_name} Complete")

    # The termination flag should switch to false AFTER ALL TERMINATION PROCESS HAS ENDED
    events.LogEvent(appargs.CameraAppArg.AppName, events.EventType.info, "Terminating cameraapp complete")
    sys.exit()
    return

######################################################
## USER METHOD                                      ##
######################################################

# Put user-defined methods here!

######################################################
## MAIN METHOD                                      ##
######################################################

thread_dict = dict[str, threading.Thread]()

# This method is called from main app. Initialization, runloop process
def cameraapp_main(Main_Queue : Queue, Main_Pipe : connection.Connection):
    global CAMERAAPP_RUNSTATUS
    CAMERAAPP_RUNSTATUS = True

    # Initialization Process
    cameraapp_init()

    # Spawn SB Message Listner Thread
    thread_dict["SBListner_Thread"] = threading.Thread(target=SB_listner, args=(Main_Pipe, ), name="SBListner_Thread")

    # Spawn Each Threads
    for thread_name in thread_dict:
        thread_dict[thread_name].start()

    try:
        # Runloop
        while CAMERAAPP_RUNSTATUS:
            cameraHK = msgstructure.MsgStructure
            msgstructure.fill_msg(cameraHK, appargs.CameraAppArg.AppID, appargs.HkAppArg.AppID, appargs.HkAppArg.MID_ReceiveHK, str(CAMERAAPP_RUNSTATUS))

            # Send Message
            send_message(Main_Queue, msgstructure.pack_msg(cameraHK))

            time.sleep(1)
    # If error occurs, terminate app
    except Exception as e:
        events.LogEvent(appargs.CameraAppArg.AppName, events.EventType.error, f"cameraapp error : {e}")
        CAMERAAPP_RUNSTATUS = False

    # Termination Process after runloop
    cameraapp_terminate()

    return