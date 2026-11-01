# Troubleshooting

Labs that start from a configured network that does not work.

Each one ships the network already built, with faults injected into its
startup-configs, and an incident ticket written the way a user would write it.
The exercise is to find the root causes and restore the intended state without
redesigning anything. The intended state is fully documented — addressing,
design and every verification check — so "fixed" has a precise meaning.

`configs/` holds the faulted configurations. The solution and the restored
baseline are deliberately not published: next to the faulted files, either one
would turn the exercise into a diff.

The full list, with status, is in the [lab index](../README.md#lab-index).
