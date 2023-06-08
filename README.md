# MCDR-AutoCommand
---------

**中文** | [English](./README.md)

一个支持将指令打包成指令堆&自动发送的插件

需要 `v2.1.0` 以上的 [MCDReforged](https://github.com/Fallen-Breath/MCDReforged)

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

配置文件为 `config/QuickBackupM.json`。它会在第一次运行时自动生成