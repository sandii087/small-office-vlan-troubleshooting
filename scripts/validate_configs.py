#!/usr/bin/env python3
"""Offline consistency checks for the documented Cisco IOS lab configs."""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
ROUTER = (ROOT / "configs/R1-router.txt").read_text()
SWITCH = (ROOT / "configs/SW1-switch.txt").read_text()


def require(condition: bool, message: str) -> None:
    if not condition:
        print(f"FAIL: {message}", file=sys.stderr)
        raise SystemExit(1)


for vlan, subnet, gateway in (
    (10, "192.168.10.0 255.255.255.0", "192.168.10.1"),
    (20, "192.168.20.0 255.255.255.0", "192.168.20.1"),
):
    require(f"encapsulation dot1Q {vlan}" in ROUTER, f"router VLAN {vlan} subinterface is missing")
    require(f"ip address {gateway} 255.255.255.0" in ROUTER, f"VLAN {vlan} gateway is wrong or missing")
    require(f"network {subnet}" in ROUTER, f"VLAN {vlan} DHCP network is wrong or missing")
    require(f"default-router {gateway}" in ROUTER, f"VLAN {vlan} DHCP gateway is wrong or missing")
    require(re.search(rf"(?m)^vlan {vlan}$", SWITCH) is not None, f"switch VLAN {vlan} is missing")

require("switchport trunk allowed vlan 10,20" in SWITCH, "router trunk must allow VLANs 10 and 20")
require("interface range FastEthernet0/1 - 2" in SWITCH and "switchport access vlan 10" in SWITCH,
        "IT endpoint ports must be assigned to VLAN 10")
require("interface range FastEthernet0/3 - 4" in SWITCH and "switchport access vlan 20" in SWITCH,
        "Operations endpoint ports must be assigned to VLAN 20")
require("no shutdown" in ROUTER, "router parent interface must be enabled")
require("write memory" in ROUTER and "write memory" in SWITCH, "baseline configs should save their changes")

print("PASS: router, DHCP, VLAN, access-port, and trunk configuration checks")
