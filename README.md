# Control Panel Module

The Control Panel overlay is the main control unit for the steerable vehicle. It visualizes the vehicle's most important settings and provides insights into steering and speed behavior. Additionally, the overlay includes a timer that can be started for time measurement purposes.

## Usage

The Control Panel is launched via the Module Manager and can be found under the name "Control Panel".

## Structure

The visualized driver data is **received** from the `driver_input_reader` module via the `pynng` address:  
```
ipc:///tmp/RAAI/driver_input_reader.ipc
```

The throttle data controlled by the Control Panel is then **sent** via the address:  
```
ipc:///tmp/RAAI/control_panel.ipc
``` 
