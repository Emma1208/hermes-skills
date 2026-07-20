# Termux watchdog pitfalls (learned the hard way)

Real gotchas from supervised-process work on Termux (bot + Hermes gateway watchdogs).

## 1. BusyBox `exec -a` breaks dummy-process tests
On Termux, `sleep`/`kill`/etc. are BusyBox applets. BusyBox picks the applet from
`argv[0]`, so a rename lies to it:

    exec -a mydummy sleep infinity
    # -> "mydummy: applet not found"   <-- the renamed applet doesn't exist

This also bites `pgrep -f` tests if you rely on the renamed comm. **Fix:** use a real
binary for the dummy, e.g. python3:

    nohup python3 -c "import time,sys; sys.argv[0]='mydummy'; time.sleep(1000)" &

`pgrep -f mydummy` then matches cleanly and `kill -9 <pid>` kills it for real.

## 2. Cannot kill/restart the Hermes gateway from inside its own process
`hermes gateway stop|restart|status` and `pkill -f "hermes gateway"` are **blocked when the
command runs inside the gateway** — the gateway refuses because SIGTERM would propagate to
the child running your command and kill it mid-flight. You'll see:

    Blocked: cannot restart or stop the gateway from inside the gateway process.

**Fix / test strategy:** do NOT prove the watchdog by killing the real gateway from the
agent's own shell. Instead, validate the relaunch loop with an independent dummy process
(section 1), kill THAT by PID, and confirm the watchdog relaunches it. The gateway itself
stays up. On a real crash the watchdog's `pgrep -f "hermes gateway"` will catch the absence
and relaunch with `hermes gateway run --replace`.

## 3. Launch long-lived processes with terminal(background=true), not nohup/disown/setsid
In the agent's terminal, a foreground command using `nohup ... & disown` or `setsid` is
rejected:

    Foreground command uses shell-level background wrappers (nohup/disown/setsid). Use
    terminal(background=true) so Hermes can track the process ...

Use `terminal(background=true)` for the watchdog itself. For Termux:Boot scripts (which run
outside the agent, at device boot) the `setsid nohup ... &` form is still correct and
needed to fully detach from the boot session.

## 4. Avoid `pkill -f` self-match in test loops
`pkill -f "my_pattern"` matches the pkill command's OWN argument string, so it can kill its
own shell (exit -15 / bizarre behaviour). **Fix:** write the target PID to a file and
`kill "$(cat pidfile)"`, or match with `pgrep -x <comm>` (exact comm, no cmdline scan).

## 5. `termux-wake-lock` drains battery
Stops the CPU sleeping but burns battery. Keep the phone on charge while a watchdog runs.
