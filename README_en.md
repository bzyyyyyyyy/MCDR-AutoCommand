# MCDR-AutoCommand
---------

[中文](./README.md) | **English**

A plugin that supports assembling commands into stacks and sending them automatically

Needs `v2.1.0` + [MCDReforged](https://github.com/Fallen-Breath/MCDReforged)

I referred to [QuickBackupM](https://github.com/TISUnion/QuickBackupM)，[TimedQBM](https://github.com/TISUnion/TimedQBM), and [LocationMarker](https://github.com/TISUnion/LocationMarker) from Fallen-Breath

## Command

`!!ac` Display help message

`!!ac make <name> <permission> [<comment>]` Make a new command stack

`!!ac stack <name>` Display information of this command stack

`!!ac stack <name> add <command>` Add a new command at the end of the command stack

`!!ac stack <name> before <lineNo.> <command>` Add a new command before the `<lineNo.>` of this command stack

`!!ac stack <name> edit <lineNo.> <command>` Change the command at `<lineNo.>` to `<command>`

`!!ac stack <name> before [<lineNo.>]` Delete the command at `<lineNo.>` of this command stack (Delete the last command if there's no `<lineNo.>`)

`!!ac stack <name> perm <level>` Change the permission level of this command stack's usage into `<level>`

`!!ac send <name>` Send all the command in the command stack in sequence

`!!ac del <name>` Delete this command stack

`!!ac list [<page>]` Display command stacks. [<page>] is optional

`!!ac search <keyword> [<page>]` Search for command stack. It gives back all command stacks that matches

This plugin has two builtin command stacks (permission:3) which are `<server_start>` and `<timed_command>`

This plugin send all the command in the `<server_start>` in sequence automatically after server started

This plugin send all the command in the `<timed_command>` in sequence every `<minutes>`

`!!ac tc` Display information of `<timed_command>`

`!!ac tc enable` Start the command stack sending timer

`!!ac tc disable` Disable the command stack sending timer

`!!ac tc set_interval` Set the command stack sending timer interval in minutes

`!!ac tc reset_timer` Reset the command stack sending timer

## Config file explaination

### auto_command

Path: `config/auto_command/auto_command.json`

#### minimum_stack_edit_perm

Default: `3`

Minimum permission of editing the command stack

If the command stack's usage permission is higher then minimum edit permission, the edit permission of this stack equals to it's usage permission

Having edit permission, you can：

1. Make a new command stack（usage permission of the command stack cannot exeed your permission level）

2. Edit commands in the command stack

3. Change the usage permission of the command stack（the permission level you are changing to cannot exeed your permission level）

4. Delete the command stack

5. Send the command stack

#### stack_per_page

Default: `10`

After using `!!ac list <page>` or `!!ac search <keyword> <page>`

the limit of command stacks showing on each page

#### timed_command_interval

Default: `30.0`

Command stack sending timer interval in minutes

#### timed_command_enabled

Default: `true`

Weather enable the timer

### command_stacks

Path: `config/auto_command/command_stacks.json`

example：


```
{
    "难度和平": {
        "desc": "将难度更改为和平",
        "perm": 3,
        "command": [
            "/difficulty peaceful",
            "成功更改难度为和平"
        ]
    },
    "peaceful": {
        "desc": "set game difficulty to peaceful",
        "perm": 3,
        "command":  [
            "/difficulty peaceful",
            "set difficulty to peaceful successfully"
        ]
    }
}
```

#### desc

Default: `null`

Description of the command stack

Can be represented with a classic “§”-prefixed formatting code
e.g. `This is §bBlue`

#### perm

Range：0 ~ 4

Usage permission of the command stack

#### command

Default: `[]`

When sending the command stack：

If the command is starting with `/`, it will be sent to server’s standard input stream

If the command is starting with `!!`, it will be sent to MCDR’s command system (only some of the commands will work)

Else the command will be broadcast

## Builtin command stacks

### server_start

Default: 

```
"server_start": {
        "desc": "Send this command stack after server starts",
        "perm": 3,
        "command": []
}
```

### timed_command

Default: 

```
"timed_command": {
        "desc": "Send this command stack every §b30.0 §rminutes",
        "perm": 3,
        "command": []
}
```

#### desc

Everytime the interval of the timer is updated

The discription will be updated also

### perm

The usage permission of this command stack is also the permission of using all `!!ac tc` commands execpt for `!!ac tc` itself

## interpreter

### /player `bot` spawn

When a player is sending a command stack, if this kind of command is detected, it will be sent using the source of the player

### /player `bot` spawn here

When editing a command stack, if this kind of command is detected, it will be interpreted into /player `bot` spawn at ~ ~ ~ facing ~ ~ in `dim` in `gamemode`