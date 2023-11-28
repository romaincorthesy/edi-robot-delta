# edi-robot-delta

# Setup
Install python modules **without sudo**:
```sh
$ cd /home/EDI_pi_delta/edi-robot-delta
$ python3 -m pip -r requirements.txt
```
Install missing fonts:
```sh
$ sudo apt-get install python3-sdl2
```

## Launching the program
Run the file `/home/EDI_pi_delta/edi-robot-delta/game.py` without any arguments to run in standard mode.

The script can be optionnaly run with one of these flags:

`-u, --user-follows` : try to follow the robot as fast as you can. The homing sequence WILL be run.\
`-r, --robot-follows` : try to outspeed the robot. The homing sequence WILL be run.\
`-t, --test-cmd` : send commands to test that the robot is working as intended. The homing sequence WILL NOT be run.\
`without args` : run in standard use (expo). The homing sequence WILL be run.

## Writing paths for the robot to follow
The paths are stored in a json file of the following structure:
```json
{
"path_scale_x": 1,
"path_scale_y": 1,
"points": [
    [-330,562],
    [-330,521],
    [-330,479]
}
```
With `points` being an array of coordinates [x,y] with (0,0) being in the center of the robot working area.

You can use Inkscape to generate the list of points: first using the built-in extension `Add Nodes...` to add a bunch of nodes along the path, the exporting the multiple nodes coordinates with an extension of your choosing, `Export XY` (hard to make it work but works in the end) or [Nodes to CSV](https://github.com/camrbuss/nodes_to_csv) (untested).

## Troubleshooting the launch
### CAN
The script starts by connecting the pi to the robot through CAN. If it fails, the usb cable is probably disconnected. One or more of these error messages will be shown:
- `AttributeError: 'DeltaRobot' object has no attribute '_notifier'`
- `can.exceptions.CanOperationError: Could not write to serial device`
- `FileNotFoundError: [Errno 2] No such file or directory: '/dev/ttyACM0'`
- `serial.serialutil.SerialException: [Errno 2] could not open port /dev/ttyACM0`

### Display
If you're trying to run the python script from a ssh or vnc session, depending on the type of display you're using you must explicitly set the `DISPLAY` environnement variable to the currently connected display.

Use this command to set the `DISPLAY` environnement variable to the default display value (`:0`):
```sh
$ export DISPLAY=:0
```
Then check the list of environnement variable to confirm:
```sh
$ export
declare -x BROWSER="/home/EDI_pi_delta/.vscode-server/bin/1a5daa3a0231a0fbba4f14db7ec463cf99d7768e/bin/helpers/browser.sh"
declare -x COLORTERM="truecolor"
declare -x DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/1000/bus"
declare -x DISPLAY=":0"
declare -x GIT_ASKPASS="/home/EDI_pi_delta/.vscode-server/bin/1a5daa3a0231a0fbba4f14db7ec463cf99d7768e/extensions/git/dist/askpass.sh"
declare -x HOME="/home/EDI_pi_delta"
declare -x LANG="en_GB.UTF-8"
declare -x LOGNAME="EDI_pi_delta"
...
```
If you forget to do so, the following error message (or equivalent) will be shown on run attempt: `pygame.error: Unable to open a console terminal`

## Autostart
Add `@lxterminal -e python3 /home/EDI_pi_delta/edi-robot-delta/game.py` to the file `/etc/xdg/lxsession/LXDE-pi/autostart`:
```sh
$ sudo nano /etc/xdg/lxsession/LXDE-pi/autostart
```
It becomes
```ini
@lxpanel --profile LXDE-pi
@pcmanfm --desktop --profile LXDE-pi
@xscreensaver -no-splash
@lxterminal -e python3 /home/EDI_pi_delta/edi-robot-delta/game.py
```
The script will be run on login (5 tries because of the `@`) and will start the game in standard (expo) mode (without any flags). It will start the python script in a terminal so the logs can be seen.

## IP config
Added to `/etc/dhcpcd.conf`:
```ini
interface eth0
request 172.17.200.55
```
It'll ask the dhcp server to give the pi this ip but if it's already assigned, it'll give us another one.