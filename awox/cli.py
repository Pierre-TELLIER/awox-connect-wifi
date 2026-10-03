import argparse
from logging import error, debug

from awox.config import load_config
from awox.controls.light import Light
from awox.mqtt.client import MQTTClient
from awox.provisioning.provisioner import Provisioner
from awox.state import load_state, clear_state


def select_device(state):
    devices = list(state.devices.items())

    if not devices:
        raise RuntimeError("No devices found")

    print("\nAvailable devices:")

    for index, (device_id, device) in enumerate(devices, start=1):
        print(f"  {index}. {device.config.friendly_name} ({device_id})")

    while True:
        try:
            choice = int(input("\nSelect device: "))
            if choice <= 0:
                raise ValueError
            device_id, device = devices[choice - 1]
            return device_id, device
        except (ValueError, IndexError):
            error("Invalid selection")


def interactive_mode(config, state):
    device_id, device = select_device(state)

    # For now, all L4HActuator devices are lights.
    if device_id.startswith("L4HActuator_"):

        mqtt = MQTTClient(
            config,
            device,
        )
        mqtt.connect()
        light = Light(
            mqtt=mqtt,
            device_id=device_id,
            device=device,
        )

        print(
            "\nCommands: "
            "on | off | bright <0-100> | temp <0-100> | "
            "color <r> <g> <b> | showstate | quit"
        )

        while True:
            try:
                cmd = input("> ").strip().lower().split()

                if not cmd:
                    continue

                if cmd[0] == "on":
                    light.turn_on()

                elif cmd[0] == "off":
                    light.turn_off()

                elif cmd[0] == "bright" and len(cmd) == 2:
                    light.set_brightness(int(cmd[1]))

                elif cmd[0] == "color" and len(cmd) == 4:
                    light.set_color(
                        int(cmd[1]),
                        int(cmd[2]),
                        int(cmd[3]),
                    )

                elif cmd[0] == "temp" and len(cmd) == 2:
                    light.set_temperature(int(cmd[1]))

                elif cmd[0] in ("quit", "exit", "q"):
                    break
                elif cmd[0] == "showstate":
                    print(device.state)
                else:
                    print("Unknown command")

            except KeyboardInterrupt or EOFError:
                break

            except Exception as e:
                print(f"Error: {e}")

        mqtt.close()

    else:
        raise RuntimeError(
            f"Unsupported device type: {device_id}"
        )


def non_interactive_mode(config, state, args):
    device_id = args.device
    device_state = [x[1] for x in state.devices.items() if x[0] == device_id]

    if len(device_state) == 0:
        error("Device not found")
        error(f"available devices: {', '.join(state.devices)}")
        exit(1)

    device_state = device_state[0]
    mqtt = MQTTClient(
        config,
        device_state,
    )
    mqtt.connect()
    light = Light(
        mqtt=mqtt,
        device_id=device_id,
        device=device_state,
    )
    if args.off:
        light.turn_off()
    elif args.on:
        light.turn_on()

    if args.brightness is not None:
        light.set_brightness(args.brightness)

    if args.temperature is not None:
        light.set_temperature(args.temperature)

    if args.color:
        r, g, b = args.color.split(",")
        light.set_color(int(r), int(g), int(b))

    mqtt.close()


def build_parser():
    parser = argparse.ArgumentParser(
        prog='Awox CLI',
        description='Control your AWOX smart wifi devices.')
    parser.add_argument('-d', '--device',
                        help="Set selected device ID eg. L4HActuator_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
    parser.add_argument('-b', '--brightness', help="0-100", type=int)
    parser.add_argument('-t', '--temperature', help="0-100", type=int)
    parser.add_argument('-c', '--color', help="'<r>,<g>,<b>' with r, g and b between 0 and 255")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--on', action="store_true", help="Turn on")
    group.add_argument('--off', action="store_true", help="Turn off")
    parser.add_argument('--reprovision', action="store_true", help="restart provisioning")
    return parser


def main(args=None):
    if args is None:
        args = build_parser().parse_args()
    config = load_config()
    if args.reprovision:
        clear_state(config.storage.state_file)

    state = load_state(config.storage.state_file)

    if not state.provisioned:
        debug("Device is not provisioned.")
        provisioner = Provisioner(config, state)
        state = provisioner.provision()

    if args.device:
        non_interactive_mode(config, state, args)
    else:
        interactive_mode(config, state)


if __name__ == "__main__":
    main()
