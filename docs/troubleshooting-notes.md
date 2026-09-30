# Troubleshooting notes

## A reliable fault-isolation sequence

1. **Confirm the symptom and scope.** Is one device affected, one VLAN, or both departments? Record the PC, address, mask, gateway, and exact failed test.
2. **Check the endpoint first.** On the PC, run `ipconfig`. A `169.254.x.x` address usually means DHCP did not complete. Confirm DHCP is selected and the PC is connected to the expected switch port.
3. **Check Layer 1 and switchport assignment.** Follow the cable and use `show interfaces status` and `show vlan brief`. Confirm endpoint ports are up and assigned to the intended access VLAN.
4. **Check the trunk.** Use `show interfaces trunk`. Confirm Gi0/1 is trunking and VLANs 10 and 20 are allowed and active.
5. **Check gateways and routing.** On R1, use `show ip interface brief` and `show ip route`. The parent physical interface and both subinterfaces must be up; the router needs a connected route for each subnet.
6. **Check DHCP.** Use `show ip dhcp binding` and `show ip dhcp pool`. Confirm the client received an address in the correct subnet and the correct default router.
7. **Retest from near to far.** Ping the local gateway, a same-VLAN PC, then a PC in the other VLAN. This narrows the failing segment.
8. **Change one setting, retest, and record the result.** Avoid changing several things at once; it obscures the cause.

## Fault-injection worksheet

For each exercise, fill in the symptom and evidence before applying the repair.

| Fault | Predicted impact | Evidence to collect | Repair |
|---|---|---|---|
| Fa0/3 assigned to VLAN 10 | Operations client lands in the wrong broadcast domain | PC `ipconfig`; switch `show vlan brief` | Set Fa0/3 to access VLAN 20 and renew DHCP |
| VLAN 20 excluded from trunk | Operations traffic cannot reach its router subinterface | `show interfaces trunk`; router subinterface state | Add VLAN 20 to the trunk allowed list |
| Router parent interface shut down | Both VLAN gateways fail | `show ip interface brief` | Enable Gi0/0 |
| DHCP default router incorrect | Client receives an address but cannot reach off-subnet peers | DHCP pool configuration; client `ipconfig` | Set the pool's default router to the matching `.1` address |
| PC manually configured in wrong subnet | Only that endpoint fails | PC `ipconfig`; successful peer control test | Return it to DHCP |

After each repair, repeat the same failed test and one known-good control test.

## Portfolio evidence checklist

Once the lab is actually run in Packet Tracer, capture:

- A readable full-topology view with device names, VLAN labels, and link status
- `show vlan brief` and `show interfaces trunk`
- Router `show ip interface brief` and `show ip dhcp binding`
- PC address details from both VLANs
- Successful gateway, same-VLAN, and inter-VLAN ping results
- One fault-injection example showing symptom, diagnostic evidence, root cause, repair, and retest

Do not describe a test as passed unless you ran it in Packet Tracer and observed the result.
