# MCDR-AutoCommand
---------

**中文** | [English](./README_en.md)

一个支持将指令打包成指令堆&自动发送的插件

需要 `v2.1.0` 以上的 [MCDReforged](https://github.com/Fallen-Breath/MCDReforged)

代码参考了 Fallen-Breath 的 [QuickBackupM](https://github.com/TISUnion/QuickBackupM)，[TimedQBM](https://github.com/TISUnion/TimedQBM) 和 [LocationMarker](https://github.com/TISUnion/LocationMarker)

## 命令格式说明

`!!ac` 显示帮助信息

`!!ac make <name> <permission> [<comment>]` 创建一个新指令堆

`!!ac stack <name>` 显示`<name>`的信息和其中的所有指令及注释

`!!ac stack <name> add <command>` 在`<name>`的末尾添加一行指令

`!!ac stack <name> before <lineNo.> <command>` 在`<name>`的`<lineNo.>`前添加一行指令

`!!ac stack <name> edit <lineNo.> <command>` 将`<lineNo.>`的指令改为`<command>`

`!!ac stack <name> before [<lineNo.>]` 删除`<name>`中`<lineNo.>`的命令（如果`<lineNo.>`为空，则删除`<name>`中的最后一行指令）

`!!ac stack <name> perm <level>` 将`<name>`的使用权限更改为`<permission>`

`!!ac send <name>` 依次发送`<name>`中的所有指令

`!!ac del <name>` 删除指令堆`<name>`

`!!ac list [<page>]` 显示所有指令堆及注释

`!!ac search <keyword> [<page>]` 搜索指令堆，返回所有匹配项

该插件自带两个`<permission>`为`3`的空指令堆`<server_start>`和`<timed_command>`

服务器开启时自动依次发送`<server_start>`中的所有指令

间隔`<minutes>`分钟自动依次发送`<timed_command>`中的所有指令

`!!ac tc` 显示间隔的<分钟>和`<timed_command>`的信息和其中的所有指令及注释

`!!ac tc enable` 启动发送指令定时器

`!!ac tc disable` 关闭发送指令定时器

`!!ac tc set_interval` 设置发送指令定时器的时间间隔，单位分钟

`!!ac tc reset_timer` 重置发送指令定时器

## 配置文件说明

### auto_command

路径：`config/auto_command/auto_command.json`

#### minimum_stack_edit_perm

默认值：`3`

编辑指令堆的最低权限要求

如果该指令堆的使用权限高于编辑权限，则该指令堆的编辑权限等于使用权限

拥有编辑权限的玩家可以：

1. 创建指令堆（指令堆使用权限不可高于该玩家的权限）

2. 编辑指令堆中的指令

3. 更改指令堆的使用权限（更改后的权限不可高于该玩家的权限）

4. 删除指令堆

5. 发送指令堆

#### stack_per_page

默认值：`10`

使用 `!!ac list <page>` 或 `!!ac search <keyword> <page>` 后

每一页显示的指令堆数量

#### timed_command_interval

默认值：`30.0`

发送指令定时器的时间间隔，单位分钟

#### timed_command_enabled

默认值：`true`

是否启用发送指令定时器

### command_stacks

路径：`config/auto_command/command_stacks.json`

示例：


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

默认值：`null`

指令堆的注释

可以使用以 `§` 为前缀的传统样式代码
如：`这是§b蓝色`

#### perm

范围：0 ~ 4

指令堆的使用权限

#### command

默认值：`[]`

当发送该指令堆时：

如果指令以 `/` 开头，则通过发送到服务端的标准输入流来执行服务端指令

如果指令以 `!!` 开头，则会在MCDR系统中执行该指令（有些插件的指令不会生效）

其他情况则会在游戏中广播该指令

## 内置指令堆

### server_start

默认值：

```
"server_start": {
        "desc": "服务器开启时发送指令堆",
        "perm": 3,
        "command": []
}
```

### timed_command

默认值：

```
"timed_command": {
        "desc": "间隔§b30.0§r分钟发送指令堆",
        "perm": 3,
        "command": []
}
```

#### desc

每次更新发送指令定时器的时间间隔时

会同时更新该指令堆的注释

### perm

该指令堆的使用权限也是除 `!!ac tc` 以外的所有 `!!ac tc` 指令的使用权限

## 解释器

### /player `bot` spawn

在发送指令堆时，如果检测到该种指令，将会通过发送指令堆的玩家发送该指令

### /player `bot` spawn here

在编辑指令堆时，如果检测到该指令，会自动将其转换成 /player `bot` spawn at ~ ~ ~ facing ~ ~ in `dim` in `gamemode`