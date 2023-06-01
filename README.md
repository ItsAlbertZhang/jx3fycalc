# 剑网3焚影圣诀DPS计算器

本项目为剑网3焚影圣诀DPS计算器, 仓库代码为项目的开源部分.

## Release

本项目的发行版软件集成了图形界面 (GUI), 计算核心 (Kernel) 与数据 (Data).

GUI 与 Kernel 之间使用 websocket 进行通信, Kernel 通过文件读取与模块调用的方式访问 Data 并完成计算.

软件的 GUI 使用了 [PyQt-Fluent-Widgets](https://github.com/ItsAlbertZhang/PyQt-Fluent-Widgets/tree/jx3fycalc) 库 (fork from: [zhiyiYo/PyQt-Fluent-Widgets@59b0a434c7](https://github.com/zhiyiYo/PyQt-Fluent-Widgets/tree/59b0a434c7a8b2bca4d2a994b7de0717aa4a47ad), 作者: [zhiyiYo](https://github.com/zhiyiYo)), 已按照其 [开源协议 (LGPLv3)](https://github.com/ItsAlbertZhang/PyQt-Fluent-Widgets/blob/jx3fycalc/LICENSE) 进行了修改并于上述 GitHub 仓库分支保持开源. GUI 的其余部分不作开源发布.

软件的 Kernel 即为本仓库代码, 以 [LGPLv3协议](https://github.com/ItsAlbertZhang/jx3fycalc/blob/main/LICENSE) 开源.

软件的 Data 是计算所需的逻辑与数据, 且不作开源发布. Data 基于游戏内数据得来, 分为表与脚本两部分:

- 表以文件读取的方式被 Kernel 访问, 并可在配置资源文件后从资源文件中自动读取生成. 表存放在 `data` 目录下, 类型为 `.bin` 二进制文件.
- 脚本以模块调用的方式被 Kernel 访问, 需要按照规则手动编写. 脚本存放在 `src/scripts` 目录下, 类型为 `.py` 脚本文件. 当所需的脚本不存在时, Kernel 会自动在该目录下根据模板创建一个所需的脚本并抛出异常, 以提示用户编写脚本.

## 以源码方式运行 Kernel

### 配置环境

Kernel 是项目的计算核心, 但计算所需的逻辑与数据并不包括在内, 而是在 Data 中.

> 由于 Data 是基于游戏内数据得来, 出于对游戏内数据的保护, 本项目的开源部分仅包括 Kernel, 而不包括其所需的 Data. 因此仅有本项目仓库的这部分代码并不足以支撑 Kernel 完成计算. 你可以通过任意渠道联系我以尝试获取 Data 文件.
>
> - 我不会以任何方式要求你就这些文件进行付费, 但你获取这些文件的意图必须是无害的.
> - Data 会随游戏版本更迭而变更.
>
> 如果仅仅是追求自定义计算, 你也可以直接使用 Kernel 的 release 版本运行.
>
> 你也可以直接运行 release 版本的 GUI 软件以达到完全等效的效果. (release 版本软件的大致原理即类似于拉起一个子进程并在其中运行 Kernel.)

克隆仓库至本地.

```shell
git clone https://github.com/ItsAlbertZhang/jx3fycalc.git
```

创建并激活虚拟环境.

```shell
python -m venv env
.\env\Scripts\activate # windows
source env/bin/activate # mac/linux
```

安装依赖.

```shell
pip install -r requirements.txt
```

配置资源文件. 将资源文件 (主要是 `settings` 和 `ui` 目录) 放在 `pak` 目录下, 以使 Kernel 自动生成表并获取计算逻辑.

编写 scripts. 你可以以 `src/scripts/明教_烈日斩.py` 作为参考. Kernel 会根据需要自动创建需要的脚本并抛出异常, 以提示你进行脚本编写.

### 运行 Kernel

```shell
python kernel.py
```

运行过程中可以按 Ctrl + C 终止运行.

## 使用与通信

运行 Kernel 后, 会在本地 8765 端口开启一个 websocket 服务. 可以使用任意 websocket 客户端 (如 Postman 等) 连接至该服务, 与 Kernel 进行通信.

### 通信协议

#### 请求 (施工中)

请求的数据格式为 JSON. 可以查看示例请求以了解更多信息: [example-websocket_message.json](https://github.com/ItsAlbertZhang/jx3fycalc/blob/main/example-websocket_message.json).

#### 响应

响应消息的数据格式为 JSON. 消息中必然包含 `category` 字段, 该字段用于指明消息的类型. 如有必要, 消息中还会包含 `data` 字段, 该字段用于承载消息的内容.

可能的类型包括:

- `data_begin` / `data_end`, 用于指明消息开始/结束.
- `damage_begin` / `damage_end`, 用于指明伤害数据开始/结束.
- `damage`, 用于指明本条消息是一条伤害消息. 这条消息同时会包含一个 `data` 字段. 详细内容请查看 `src/frame/damage.py` - `Damage` 类 - `damagecalc_last` 类方法 - `message` 变量.
- `fight_stat`, 用于指明本条消息是一条战斗情况消息. 这条消息同时会包含一个 `data` 字段. 详细内容请查看 `src/frame/fight_stat.py` - `handle` 函数 - `message_send` 变量.
- `fight_analysis`, 用于指明本条消息是一条战斗统计消息. 这条消息同时会包含一个 `data` 字段. 详细内容请查看 `src/frame/damage.py` - `Damage` 类 - `damage_statistics` 类方法 - `ret_dict` 变量.
- `attr_benefit`, 用于指明本条消息是一条属性收益消息. 这条消息同时会包含一个 `data` 字段. 详细内容请查看 `src/main.py` - `ProgramChildAttrBenefit` 类 - `handle` 方法 - `attr_benefit` 变量.

### 使用子进程调起 kernel.py 时的注意事项

施工中...
