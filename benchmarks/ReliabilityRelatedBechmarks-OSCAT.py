
    "Tank_Level_Control": {
        "steps": [
            {"name": "Start", "function": "CheckLevel"},
            {"name": "Fill", "function": "OpenInletValve"},
            {"name": "Stop", "function": "CloseInletValve"}
        ],
        "transitions": [
            {"src": "Start", "tgt": "Fill", "guard": "level < LOW"},
            {"src": "Fill", "tgt": "Stop", "guard": "level >= HIGH"},
            {"src": "Stop", "tgt": "Start", "guard": "level <= NORMAL"}
        ],
        "variables": ["level", "LOW", "HIGH", "NORMAL"],
        "initial_step": "Start"
    },
    "Batch_Mixing_System": {
        "steps": [
            {"name": "Idle", "function": "WaitForStart"},
            {"name": "AddIngredient", "function": "OpenValve"},
            {"name": "Mix", "function": "StartMixer"},
            {"name": "End", "function": "StopAll"}
        ],
        "transitions": [
            {"src": "Idle", "tgt": "AddIngredient", "guard": "startButton == true"},
            {"src": "AddIngredient", "tgt": "Mix", "guard": "ingredientAdded == true"},
            {"src": "Mix", "tgt": "End", "guard": "mixingTimeElapsed == true"}
        ],
        "variables": ["startButton", "ingredientAdded", "mixingTimeElapsed"],
        "initial_step": "Idle"
    },
    "Temperature_Control_System": {
        "steps": [
            {"name": "Monitor", "function": "ReadTemp"},
            {"name": "Heat", "function": "TurnHeaterOn"},
            {"name": "Cool", "function": "TurnCoolerOn"}
        ],
        "transitions": [
            {"src": "Monitor", "tgt": "Heat", "guard": "temp < MIN_TEMP"},
            {"src": "Monitor", "tgt": "Cool", "guard": "temp > MAX_TEMP"},
            {"src": "Heat", "tgt": "Monitor", "guard": "temp >= MIN_TEMP"},
            {"src": "Cool", "tgt": "Monitor", "guard": "temp <= MAX_TEMP"}
        ],
        "variables": ["temp", "MIN_TEMP", "MAX_TEMP"],
        "initial_step": "Monitor"
    },
    "Conveyor_System_Controller": {
        "steps": [
            {"name": "Idle", "function": "WaitForObject"},
            {"name": "Move", "function": "StartConveyor"},
            {"name": "Stop", "function": "StopConveyor"}
        ],
        "transitions": [
            {"src": "Idle", "tgt": "Move", "guard": "objectDetected == true"},
            {"src": "Move", "tgt": "Stop", "guard": "positionReached == true"},
            {"src": "Stop", "tgt": "Idle", "guard": "objectCleared == true"}
        ],
        "variables": ["objectDetected", "positionReached", "objectCleared"],
        "initial_step": "Idle"
    },
    "Traffic_Light_Controller": {
        "steps": [
            {"name": "Green", "function": "SetGreen"},
            {"name": "Yellow", "function": "SetYellow"},
            {"name": "Red", "function": "SetRed"}
        ],
        "transitions": [
            {"src": "Green", "tgt": "Yellow", "guard": "greenTimeElapsed == true"},
            {"src": "Yellow", "tgt": "Red", "guard": "yellowTimeElapsed == true"},
            {"src": "Red", "tgt": "Green", "guard": "redTimeElapsed == true"}
        ],
        "variables": ["greenTimeElapsed", "yellowTimeElapsed", "redTimeElapsed"],
        "initial_step": "Green"
    },
    "Pump_Control_System": {
        "steps": [
            {"name": "Idle", "function": "MonitorLevel"},
            {"name": "PumpOn", "function": "StartPump"},
            {"name": "PumpOff", "function": "StopPump"}
        ],
        "transitions": [
            {"src": "Idle", "tgt": "PumpOn", "guard": "level < LOW"},
            {"src": "PumpOn", "tgt": "PumpOff", "guard": "level >= HIGH"},
            {"src": "PumpOff", "tgt": "Idle", "guard": "level <= NORMAL"}
        ],
        "variables": ["level", "LOW", "HIGH", "NORMAL"],
        "initial_step": "Idle"
    },
    "Elevator_Controller": {
        "steps": [
            {"name": "Idle", "function": "WaitRequest"},
            {"name": "MoveUp", "function": "ElevatorUp"},
            {"name": "MoveDown", "function": "ElevatorDown"},
            {"name": "OpenDoor", "function": "OpenDoors"}
        ],
        "transitions": [
            {"src": "Idle", "tgt": "MoveUp", "guard": "requestedFloor > currentFloor"},
            {"src": "Idle", "tgt": "MoveDown", "guard": "requestedFloor < currentFloor"},
            {"src": "MoveUp", "tgt": "OpenDoor", "guard": "currentFloor == requestedFloor"},
            {"src": "MoveDown", "tgt": "OpenDoor", "guard": "currentFloor == requestedFloor"},
            {"src": "OpenDoor", "tgt": "Idle", "guard": "doorTimerElapsed == true"}
        ],
        "variables": ["currentFloor", "requestedFloor", "doorTimerElapsed"],
        "initial_step": "Idle"
    },
    "PID_Controlled_Process": {
        "steps": [
            {"name": "ReadInput", "function": "ReadSensor"},
            {"name": "ComputePID", "function": "ApplyPID"},
            {"name": "ApplyOutput", "function": "SetActuator"}
        ],
        "transitions": [
            {"src": "ReadInput", "tgt": "ComputePID", "guard": "true"},
            {"src": "ComputePID", "tgt": "ApplyOutput", "guard": "true"},
            {"src": "ApplyOutput", "tgt": "ReadInput", "guard": "cycleTimeElapsed == true"}
        ],
        "variables": ["sensorValue", "outputValue", "cycleTimeElapsed"],
        "initial_step": "ReadInput"
    },
    "Motor_Start_Stop_with_Interlocks": {
        "steps": [
            {"name": "Idle", "function": "WaitStart"},
            {"name": "StartMotor", "function": "MotorOn"},
            {"name": "StopMotor", "function": "MotorOff"}
        ],
        "transitions": [
            {"src": "Idle", "tgt": "StartMotor", "guard": "startCommand == true and interlockOk == true"},
            {"src": "StartMotor", "tgt": "StopMotor", "guard": "stopCommand == true"},
            {"src": "StopMotor", "tgt": "Idle", "guard": "motorStopped == true"}
        ],
        "variables": ["startCommand", "stopCommand", "interlockOk", "motorStopped"],
        "initial_step": "Idle"
    }
}


    "Filling and Packaging Line": {
        "steps": [
            {"name": "Start", "function": "InitializeSystem"},
            {"name": "Fill", "function": "ActivateFiller"},
            {"name": "CheckFill", "function": "VerifyFillLevel"},
            {"name": "Seal", "function": "SealPackage"},
            {"name": "Label", "function": "ApplyLabel"},
            {"name": "End", "function": "ConveyOut"}
        ],
        "transitions": [
            {"src": "Start", "tgt": "Fill", "guard": "system_ready"},
            {"src": "Fill", "tgt": "CheckFill", "guard": "filling_done"},
            {"src": "CheckFill", "tgt": "Seal", "guard": "level_ok"},
            {"src": "Seal", "tgt": "Label", "guard": "sealing_done"},
            {"src": "Label", "tgt": "End", "guard": "label_ok"}
        ],
        "variables": ["system_ready", "filling_done", "level_ok", "sealing_done", "label_ok"],
        "initial_step": "Start"
    },

    "Water Treatment Plant Controller": {
        "steps": [
            {"name": "Intake", "function": "OpenIntakeValve"},
            {"name": "Filter", "function": "StartFiltering"},
            {"name": "ChemicalAdd", "function": "InjectChemicals"},
            {"name": "Storage", "function": "SendToStorage"}
        ],
        "transitions": [
            {"src": "Intake", "tgt": "Filter", "guard": "intake_done"},
            {"src": "Filter", "tgt": "ChemicalAdd", "guard": "filter_complete"},
            {"src": "ChemicalAdd", "tgt": "Storage", "guard": "chemical_injected"}
        ],
        "variables": ["intake_done", "filter_complete", "chemical_injected"],
        "initial_step": "Intake"
    },

    "Material Handling Robot": {
        "steps": [
            {"name": "Idle", "function": "WaitCommand"},
            {"name": "Pick", "function": "GripObject"},
            {"name": "Move", "function": "NavigateToLocation"},
            {"name": "Place", "function": "ReleaseObject"},
            {"name": "Return", "function": "ReturnToBase"}
        ],
        "transitions": [
            {"src": "Idle", "tgt": "Pick", "guard": "command_received"},
            {"src": "Pick", "tgt": "Move", "guard": "object_gripped"},
            {"src": "Move", "tgt": "Place", "guard": "target_reached"},
            {"src": "Place", "tgt": "Return", "guard": "object_released"},
            {"src": "Return", "tgt": "Idle", "guard": "base_reached"}
        ],
        "variables": ["command_received", "object_gripped", "target_reached", "object_released", "base_reached"],
        "initial_step": "Idle"
    },

    "HVAC System": {
        "steps": [
            {"name": "SenseTemp", "function": "ReadTemperature"},
            {"name": "CheckTemp", "function": "EvaluateTemperature"},
            {"name": "Heat", "function": "TurnOnHeater"},
            {"name": "Cool", "function": "TurnOnCooler"},
            {"name": "Idle", "function": "MaintainState"}
        ],
        "transitions": [
            {"src": "SenseTemp", "tgt": "CheckTemp", "guard": "sensor_ok"},
            {"src": "CheckTemp", "tgt": "Heat", "guard": "temp_below_min"},
            {"src": "CheckTemp", "tgt": "Cool", "guard": "temp_above_max"},
            {"src": "CheckTemp", "tgt": "Idle", "guard": "temp_ok"},
            {"src": "Heat", "tgt": "SenseTemp", "guard": "heating_done"},
            {"src": "Cool", "tgt": "SenseTemp", "guard": "cooling_done"},
            {"src": "Idle", "tgt": "SenseTemp", "guard": "cycle_complete"}
        ],
        "variables": ["sensor_ok", "temp_below_min", "temp_above_max", "temp_ok", "heating_done", "cooling_done", "cycle_complete"],
        "initial_step": "SenseTemp"
    },

    "Boiler Control": {
        "steps": [
            {"name": "Init", "function": "InitializeBoiler"},
            {"name": "HeatWater", "function": "StartHeater"},
            {"name": "CheckPressure", "function": "ReadPressureSensor"},
            {"name": "Regulate", "function": "AdjustValve"},
            {"name": "Shutdown", "function": "TurnOffBoiler"}
        ],
        "transitions": [
            {"src": "Init", "tgt": "HeatWater", "guard": "init_done"},
            {"src": "HeatWater", "tgt": "CheckPressure", "guard": "temp_threshold_reached"},
            {"src": "CheckPressure", "tgt": "Regulate", "guard": "pressure_not_ok"},
            {"src": "Regulate", "tgt": "CheckPressure", "guard": "adjustment_done"},
            {"src": "CheckPressure", "tgt": "Shutdown", "guard": "pressure_ok"}
        ],
        "variables": ["init_done", "temp_threshold_reached", "pressure_not_ok", "adjustment_done", "pressure_ok"],
        "initial_step": "Init"
    },

    "Welding Line Controller": {
        "steps": [
            {"name": "LoadPart", "function": "PositionPart"},
            {"name": "Align", "function": "AlignForWelding"},
            {"name": "Weld", "function": "ActivateWelder"},
            {"name": "Cool", "function": "StartCooling"},
            {"name": "Unload", "function": "MovePartOut"}
        ],
        "transitions": [
            {"src": "LoadPart", "tgt": "Align", "guard": "part_loaded"},
            {"src": "Align", "tgt": "Weld", "guard": "alignment_ok"},
            {"src": "Weld", "tgt": "Cool", "guard": "welding_done"},
            {"src": "Cool", "tgt": "Unload", "guard": "cooling_done"}
        ],
        "variables": ["part_loaded", "alignment_ok", "welding_done", "cooling_done"],
        "initial_step": "LoadPart"
    },

    "Automated Gate System": {
        "steps": [
            {"name": "WaitVehicle", "function": "DetectVehicle"},
            {"name": "OpenGate", "function": "RaiseGate"},
            {"name": "WaitPass", "function": "MonitorPass"},
            {"name": "CloseGate", "function": "LowerGate"}
        ],
        "transitions": [
            {"src": "WaitVehicle", "tgt": "OpenGate", "guard": "vehicle_detected"},
            {"src": "OpenGate", "tgt": "WaitPass", "guard": "gate_opened"},
            {"src": "WaitPass", "tgt": "CloseGate", "guard": "vehicle_passed"},
            {"src": "CloseGate", "tgt": "WaitVehicle", "guard": "gate_closed"}
        ],
        "variables": ["vehicle_detected", "gate_opened", "vehicle_passed", "gate_closed"],
        "initial_step": "WaitVehicle"
    },

    "Crane Automation": {
        "steps": [
            {"name": "Ready", "function": "SystemCheck"},
            {"name": "Lift", "function": "LiftLoad"},
            {"name": "Move", "function": "MoveToPosition"},
            {"name": "Lower", "function": "LowerLoad"},
            {"name": "Return", "function": "ReturnToBase"}
        ],
        "transitions": [
            {"src": "Ready", "tgt": "Lift", "guard": "load_detected"},
            {"src": "Lift", "tgt": "Move", "guard": "load_lifted"},
            {"src": "Move", "tgt": "Lower", "guard": "position_reached"},
            {"src": "Lower", "tgt": "Return", "guard": "load_lowered"},
            {"src": "Return", "tgt": "Ready", "guard": "at_base"}
        ],
        "variables": ["load_detected", "load_lifted", "position_reached", "load_lowered", "at_base"],
        "initial_step": "Ready"
    },

    "Packaging Robot": {
        "steps": [
            {"name": "Start", "function": "WaitStartSignal"},
            {"name": "FetchBox", "function": "PickEmptyBox"},
            {"name": "FillBox", "function": "PlaceItems"},
            {"name": "CloseBox", "function": "FoldAndSeal"},
            {"name": "Dispatch", "function": "MoveToConveyor"}
        ],
        "transitions": [
            {"src": "Start", "tgt": "FetchBox", "guard": "start_signal"},
            {"src": "FetchBox", "tgt": "FillBox", "guard": "box_picked"},
            {"src": "FillBox", "tgt": "CloseBox", "guard": "items_placed"},
            {"src": "CloseBox", "tgt": "Dispatch", "guard": "box_closed"},
            {"src": "Dispatch", "tgt": "Start", "guard": "box_dispatched"}
        ],
        "variables": ["start_signal", "box_picked", "items_placed", "box_closed", "box_dispatched"],
        "initial_step": "Start"
    }

    "Greenhouse Monitoring System": {
        "steps": [
            {"name": "MonitorTemperature", "function": "ReadSensor(temp)"},
            {"name": "AdjustVentilation", "function": "ControlFan(temp)"},
            {"name": "LogData", "function": "Log(temp, humidity)"},
        ],
        "transitions": [
            {"src": "MonitorTemperature", "tgt": "AdjustVentilation", "guard": "temp > threshold"},
            {"src": "AdjustVentilation", "tgt": "LogData", "guard": "True"},
            {"src": "LogData", "tgt": "MonitorTemperature", "guard": "True"},
        ],
        "variables": ["temp", "humidity", "threshold"],
        "initial_step": "MonitorTemperature",
    },

    "Railway Crossing System": {
        "steps": [
            {"name": "DetectTrain", "function": "SensorDetect(train)"},
            {"name": "CloseGate", "function": "ActivateGate(close)"},
            {"name": "OpenGate", "function": "ActivateGate(open)"},
        ],
        "transitions": [
            {"src": "DetectTrain", "tgt": "CloseGate", "guard": "train == True"},
            {"src": "CloseGate", "tgt": "OpenGate", "guard": "train == False"},
            {"src": "OpenGate", "tgt": "DetectTrain", "guard": "True"},
        ],
        "variables": ["train"],
        "initial_step": "DetectTrain",
    },

    "Printing Press Controller": {
        "steps": [
            {"name": "LoadPaper", "function": "CheckPaper()"},
            {"name": "StartPrint", "function": "InitiatePrintJob()"},
            {"name": "UnloadPaper", "function": "EjectPaper()"},
        ],
        "transitions": [
            {"src": "LoadPaper", "tgt": "StartPrint", "guard": "paperReady == True"},
            {"src": "StartPrint", "tgt": "UnloadPaper", "guard": "jobDone == True"},
            {"src": "UnloadPaper", "tgt": "LoadPaper", "guard": "True"},
        ],
        "variables": ["paperReady", "jobDone"],
        "initial_step": "LoadPaper",
    },

    "Silo Management System": {
        "steps": [
            {"name": "MeasureLevel", "function": "ReadSiloSensor()"},
            {"name": "FillSilo", "function": "StartFilling()"},
            {"name": "StopFilling", "function": "StopFilling()"},
        ],
        "transitions": [
            {"src": "MeasureLevel", "tgt": "FillSilo", "guard": "level < minLevel"},
            {"src": "FillSilo", "tgt": "StopFilling", "guard": "level >= maxLevel"},
            {"src": "StopFilling", "tgt": "MeasureLevel", "guard": "True"},
        ],
        "variables": ["level", "minLevel", "maxLevel"],
        "initial_step": "MeasureLevel",
    },

    "Power Distribution Unit": {
        "steps": [
            {"name": "MonitorLoad", "function": "ReadPowerUsage()"},
            {"name": "BalanceLoad", "function": "RedistributeLoad()"},
            {"name": "LogStatus", "function": "LogCurrentLoad()"},
        ],
        "transitions": [
            {"src": "MonitorLoad", "tgt": "BalanceLoad", "guard": "load > maxLoad"},
            {"src": "BalanceLoad", "tgt": "LogStatus", "guard": "True"},
            {"src": "LogStatus", "tgt": "MonitorLoad", "guard": "True"},
        ],
        "variables": ["load", "maxLoad"],
        "initial_step": "MonitorLoad",
    },

    "Grain Sorting Machine": {
        "steps": [
            {"name": "FeedGrain", "function": "ActivateFeeder()"},
            {"name": "SortGrain", "function": "StartSorting()"},
            {"name": "CollectGrain", "function": "RouteSortedGrains()"},
        ],
        "transitions": [
            {"src": "FeedGrain", "tgt": "SortGrain", "guard": "grainPresent == True"},
            {"src": "SortGrain", "tgt": "CollectGrain", "guard": "sortingDone == True"},
            {"src": "CollectGrain", "tgt": "FeedGrain", "guard": "True"},
        ],
        "variables": ["grainPresent", "sortingDone"],
        "initial_step": "FeedGrain",
    },

    "Wind Turbine Controller": {
        "steps": [
            {"name": "MonitorWindSpeed", "function": "ReadWindSensor()"},
            {"name": "AdjustBlades", "function": "SetBladeAngle()"},
            {"name": "GeneratePower", "function": "StartGenerator()"},
        ],
        "transitions": [
            {"src": "MonitorWindSpeed", "tgt": "AdjustBlades", "guard": "windSpeed > threshold"},
            {"src": "AdjustBlades", "tgt": "GeneratePower", "guard": "True"},
            {"src": "GeneratePower", "tgt": "MonitorWindSpeed", "guard": "True"},
        ],
        "variables": ["windSpeed", "threshold"],
        "initial_step": "MonitorWindSpeed",
    },

    "Chemical Reactor Controller": {
        "steps": [
            {"name": "StartReaction", "function": "InitChemicals()"},
            {"name": "MonitorTemp", "function": "CheckTemperature()"},
            {"name": "StopReaction", "function": "EndProcess()"},
        ],
        "transitions": [
            {"src": "StartReaction", "tgt": "MonitorTemp", "guard": "reactionStarted == True"},
            {"src": "MonitorTemp", "tgt": "StopReaction", "guard": "temp > safeLimit"},
            {"src": "StopReaction", "tgt": "StartReaction", "guard": "True"},
        ],
        "variables": ["temp", "safeLimit", "reactionStarted"],
        "initial_step": "StartReaction",
    },

    "Fuel Dispenser Logic": {
        "steps": [
            {"name": "Idle", "function": "WaitForCard()"},
            {"name": "Authorize", "function": "CheckCard()"},
            {"name": "Dispense", "function": "StartPump()"},
        ],
        "transitions": [
            {"src": "Idle", "tgt": "Authorize", "guard": "cardInserted == True"},
            {"src": "Authorize", "tgt": "Dispense", "guard": "authSuccess == True"},
            {"src": "Dispense", "tgt": "Idle", "guard": "dispenseDone == True"},
        ],
        "variables": ["cardInserted", "authSuccess", "dispenseDone"],
        "initial_step": "Idle",
    },

    "Lift Control System": {
        "steps": [
            {"name": "WaitCall", "function": "MonitorFloorRequest()"},
            {"name": "MoveLift", "function": "DriveToFloor()"},
            {"name": "OpenDoor", "function": "UnlockDoors()"},
        ],
        "transitions": [
            {"src": "WaitCall", "tgt": "MoveLift", "guard": "callReceived == True"},
            {"src": "MoveLift", "tgt": "OpenDoor", "guard": "arrived == True"},
            {"src": "OpenDoor", "tgt": "WaitCall", "guard": "doorClosed == True"},
        ],
        "variables": ["callReceived", "arrived", "doorClosed"],
        "initial_step": "WaitCall",
    },

    "Baggage Handling System": {
        "steps": [
            {"name": "ScanBaggage", "function": "ReadBarcode()"},
            {"name": "RouteBaggage", "function": "ActivateSorter()"},
            {"name": "LoadBaggage", "function": "MoveToConveyor()"},
        ],
        "transitions": [
            {"src": "ScanBaggage", "tgt": "RouteBaggage", "guard": "barcodeValid == True"},
            {"src": "RouteBaggage", "tgt": "LoadBaggage", "guard": "routeAssigned == True"},
            {"src": "LoadBaggage", "tgt": "ScanBaggage", "guard": "True"},
        ],
        "variables": ["barcodeValid", "routeAssigned"],
        "initial_step": "ScanBaggage",
    },


