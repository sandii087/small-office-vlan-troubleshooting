# Small Office VLAN & Network Troubleshooting Lab

A practical Cisco Packet Tracer lab for a junior network / IT support portfolio. It builds a small office with two departments, separates them with VLANs, routes between them with router-on-a-stick, and uses DHCP for client addressing.

> **Artifact status:** The lab was built in Cisco Packet Tracer 9.0.1 on macOS. The saved simulation is included as [`small-office-vlan-troubleshooting.pkt`](small-office-vlan-troubleshooting.pkt). See [`docs/verification-results.md`](docs/verification-results.md) for observed results and checks still awaiting evidence.

## What you will build

- **IT** — VLAN 10, `192.168.10.0/24`, gateway `192.168.10.1`
- **Operations** — VLAN 20, `192.168.20.0/24`, gateway `192.168.20.1`
- One Cisco 1941 router doing inter-VLAN routing and DHCP
- One Catalyst 2960 switch with an 802.1Q trunk to the router
- Four PCs, two in each department

```text
 IT-PC1  IT-PC2                         OPS-PC1  OPS-PC2
 VLAN 10  VLAN 10                       VLAN 20  VLAN 20
   | Fa0/1  | Fa0/2                       | Fa0/3  | Fa0/4
 +------------------------------------------------------+
 |                 SW1 — Catalyst 2960                 |
 +-------------------------- Gi0/1 ---------------------+
                            802.1Q trunk
                               |
                         R1 — Cisco 1941
                  Gi0/0.10: 192.168.10.1/24
                  Gi0/0.20: 192.168.20.1/24
```

The diagram source is [`docs/topology.svg`](docs/topology.svg). The baseline configurations are [`configs/R1-router.txt`](configs/R1-router.txt) and [`configs/SW1-switch.txt`](configs/SW1-switch.txt).

## Build the topology in Packet Tracer

1. Add one **1941** router, one **2960** switch, and four **PC-PT** endpoints. Rename them `R1`, `SW1`, `IT-PC1`, `IT-PC2`, `OPS-PC1`, and `OPS-PC2`.
2. Connect `R1 GigabitEthernet0/0` to `SW1 GigabitEthernet0/1` with a copper straight-through cable.
3. Connect the IT PCs to `SW1 FastEthernet0/1` and `FastEthernet0/2`; connect the Operations PCs to `FastEthernet0/3` and `FastEthernet0/4` (straight-through cables).
4. Open each device's CLI, answer the initial setup dialog `no`, then paste the corresponding baseline configuration. If your selected model presents different interface names, adjust the interface numbers consistently.
5. On each PC, open **Desktop → IP Configuration → DHCP**.
6. Save the file as `small-office-vlan-troubleshooting.pkt`.

## Verification checklist

Run these on `SW1`:

```text
show vlan brief
show interfaces trunk
show running-config
```

Expected: VLANs 10 and 20 exist; Fa0/1-2 are access ports in VLAN 10; Fa0/3-4 are access ports in VLAN 20; Gi0/1 is trunking and carries VLANs 10 and 20.

Run these on `R1`:

```text
show ip interface brief
show ip route
show ip dhcp binding
show running-config
```

Expected: both router subinterfaces are up/up, connected routes for both `/24` networks exist, and four DHCP leases appear after the PCs request addresses.

From the PCs, check addressing with **Desktop → Command Prompt → `ipconfig`**, then run:

| From | Test | Expected |
|---|---|---|
| IT-PC1 | `ping 192.168.10.1` | Success (local default gateway) |
| OPS-PC1 | `ping 192.168.20.1` | Success (local default gateway) |
| IT-PC1 | `ping <IT-PC2 address>` | Success (same VLAN) |
| IT-PC1 | `ping <OPS-PC1 address>` | Success (inter-VLAN routing) |

The first ping may time out while ARP resolves; repeat it once before treating it as a fault.

## Troubleshooting exercises

Save a copy of the working file before each exercise. Change one thing at a time, predict the symptom, locate the fault with show commands, restore the baseline, and retest.

| Injected fault | Likely symptom | Useful checks / correction |
|---|---|---|
| Move Fa0/3 into VLAN 10 | OPS-PC1 gets the wrong subnet / cannot reach its expected gateway | `show vlan brief`; restore Fa0/3 to access VLAN 20, renew DHCP |
| Remove VLAN 20 from the trunk allowed list | VLAN 20 gateway or remote pings fail | `show interfaces trunk`; permit VLANs 10,20 on Gi0/1 |
| Shut down router Gi0/0 | Both departments lose their gateway | `show ip interface brief`; `no shutdown` on Gi0/0 |
| Set a PC to a static address in the wrong subnet | That PC cannot reach its gateway | `ipconfig`; return the PC to DHCP |
| Put a PC on the wrong switch access port | It receives the other department's network | Trace the cable and check `show vlan brief`; correct the port assignment |

See [`docs/troubleshooting-notes.md`](docs/troubleshooting-notes.md) for a repeatable diagnosis workflow and evidence to capture for a portfolio.

## Repository contents

- `small-office-vlan-troubleshooting.pkt` — saved Packet Tracer simulation
- `vlan20-troubleshooting.pkt` — saved, repaired copy used for the VLAN 20 trunk troubleshooting exercise
- `docs/verification-results.md` — observed test results and remaining evidence
- `configs/` — complete baseline router and switch CLI configurations
- `docs/topology.svg` — topology diagram
- `docs/troubleshooting-notes.md` — troubleshooting workflow, fault exercises, and portfolio evidence checklist
- `scripts/validate_configs.py` — offline checks for required config elements and port/VLAN consistency

Run the repository checks with:

```bash
python3 scripts/validate_configs.py
```

## Limits and next step

The Python validator checks that the text configurations match the documented design; it is not a Cisco IOS emulator and does not replace Packet Tracer verification. The included `.pkt` preserves the built lab. The verification record distinguishes screenshot-confirmed results from user-reported results; the VLAN 20 trunk failure and repair have been completed, while additional screenshots and show-command evidence remain to be captured. No passwords, API keys, or other secrets belong in this repository.
