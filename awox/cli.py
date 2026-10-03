from awox.config import load_config
from awox.controls.light import Light
from awox.mqtt.client import MQTTClient
from awox.provisioning.provisioner import Provisioner
from awox.state import load_state


def select_device(state):
    devices = list(state.devices.items())

    if not devices:
        raise RuntimeError("No devices found")

    print("\nAvailable devices:")

    for index, (device_id, device) in enumerate(devices, start=1):
        print(f"  {index}. {device_id}")

    while True:
        try:
            choice = int(input("\nSelect device: "))
            device_id, device = devices[choice - 1]
            return device_id, device
        except (ValueError, IndexError):
            print("Invalid selection")


def main():
    config = load_config()
    state = load_state(config.storage.state_file)

    if not state.provisioned:
        print("Device is not provisioned.")
        provisioner = Provisioner(config, state)
        state = provisioner.provision()

    device_id, device_state = select_device(state)

    # For now, all L4HActuator devices are lights.
    if device_id.startswith("L4HActuator_"):

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

        print(
            "\nCommands: "
            "on | off | bright <0-100> | temp <0-100> | "
            "color <r> <g> <b> | quit"
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

                else:
                    print("Unknown command")

            except KeyboardInterrupt:
                break

            except Exception as e:
                print(f"Error: {e}")

        mqtt.close()

    else:
        raise RuntimeError(
            f"Unsupported device type: {device_id}"
        )


if __name__ == "__main__":
    main()
