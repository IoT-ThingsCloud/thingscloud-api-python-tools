# thingscloud-api-python-tools

ThingsCloud API 工具集，基于平台的开放 API，实现多种扩展工具，可用于数据导入导出、自动化、数据处理、数据分析等。

已实现的工具包括：

- 批量创建新设备
- 批量导出设备信息，以及生成设备二维码
- 批量导出设备属性历史数据

工具集持续更新中，欢迎使用，欢迎贡献代码。

## 环境准备

该工具集使用 `Python` 语言编写，运行在您的电脑上，需要安装 `Python` 环境。

`Python` 环境安装方法，网上教程非常丰富，请自行学习。


## 下载工具代码库

### 推荐方法

点击以下链接，下载代码压缩包，解压缩。

[https://github.com/IoT-ThingsCloud/thingscloud-api-python-tools/archive/refs/heads/main.zip](https://github.com/IoT-ThingsCloud/thingscloud-api-python-tools/archive/refs/heads/main.zip)

### 高级方法

或使用 `git` 命令下载代码库。

```bash
git clone https://github.com/IoT-ThingsCloud/thingscloud-api-python-tools.git
```

## 安装依赖库

下载代码库后，进入 `thingscloud-api-python-tools` 代码目录的根目录，执行以下命令，安装依赖库：

```bash
pip install -r requirements.txt
```

## 修改配置

进入 config 目录，将 `project_api.template.ini` 复制到 `project_api.ini`，填写 API 参数，如下：

```ini
[API]
# 请在下方填写项目应用API信息
base_url=
app_id=
access_key=
secret_key=
```

以上信息可以在 ThingsCloud 平台控制台中获取，方法如下：

| 参数名 | 获取方法 |
| --- | --- |
| base_url | 进入项目 > 连接信息，查看 应用端 API 接入点。 |
| app_id | 创建项目应用 > API，查看应用 AppID。 |
| access_key | 创建项目应用 > API，查看应用 AccessKey。 |
| secret_key | 创建项目应用 > API，查看应用 SecretKey。 |

## 运行工具

### 查看帮助

```bash
python main.py --help
```

### 批量创建设备

该工具使用 CSV 文件中的设备信息，批量创建新设备。

#### 示例 1

默认导入 `import/create_devices_template.csv` 文件中的设备信息，执行命名：

```bash
python main.py create_devices --type_id=<type_id>
```

请将 `<type_id>` 替换为创建设备所关联的设备类型 ID。

您可以修改该文件内容，格式如下：

```
name,device_key
设备名称1,100001
设备名称2,100002
设备名称3,100003
```

#### 示例 2

自定义导入 CSV 文件的路径，执行命名：

```bash
python main.py create_devices --type_id=<type_id> --file_path=<file_path>
```

将 `<file_path>` 替换为您电脑上的 CSV 文件路径，例如 `C:\Users\Join\Desktop\devices.csv`。

### 批量导出设备信息

该工具用于批量导出设备信息到本地 CSV 文件，也同时批量生成设备二维码。

#### 示例 1

导出项目中的所有设备，执行命令：

```bash
python main.py export_devices
```

导出的 CSV 文件将保存在 `export` 目录下，以当前时间命令，例如： `export/2024-10-01-10-08-31.csv`。

#### 示例 2

导出项目中的所有设备，同时生成设备二维码

```bash
python main.py export_devices --qrcode
```


#### 示例 3

导出项目中指定设备类型下的所有设备，执行命令：

```bash
python main.py export_devices --type_id=<type_id>
```

将 `<type_id>` 替换为您要导出的设备类型 ID。

#### 示例 4

导出项目中指定设备组下的所有设备，执行命令：

```bash
python main.py export_devices --group_id=<group_id>
```

将 `<group_id>` 替换为您要导出的设备组 ID。支持多个组，以逗号分隔。例如：`--group_id=<group_id1>,<group_id2>,<group_id3>`。

#### 示例 5

导出项目中指定设备组下的所有设备，并包含子组下的所有设备，执行命令：

```bash
python main.py export_devices --group_id=<group_id> --include_sub_groups
```


### 批量导出设备属性历史数据

该工具用于批量导出多个设备的属性历史数据到一个 CSV 文件，生成规范结构化数据（也称为 Tidy Data）。

#### 示例 1

导出项目中所有设备的属性历史数据，执行命令：

```bash
python main.py export_devices_attributes_history
```

该命令默认导出最近 30 天的属性历史数据。

#### 示例 2

指定导出时间范围，执行命令：

```bash
python main.py export_devices_attributes_history  --start_time=<开始时间> --end_time=<结束时间>
```

将 `<开始时间>` 和 `<结束时间>` 替换为实际时间，时间格式为：`YYYYMMDDHHmmss`。

例如，导出 2024 年 12 月 1 日 00:00:00 到 12 月 2 日 20:00:00 的属性历史数据：

```bash
python main.py export_devices_attributes_history  --start_time=20241201000000 --end_time=20241202200000
```

#### 示例 3

指定导出的设备，执行命令：

```bash
python main.py export_devices_attributes_history --device_id=<device_id>
```

将 `<device_id>` 替换为您要导出的设备 ID。


#### 示例 4

指定设备类型下的所有设备，执行命令：

```bash
python main.py export_devices_attributes_history --type_id=<type_id>
```

将 `<type_id>` 替换为您要导出的设备类型 ID。

#### 示例 5

指定设备组下的所有设备，执行命令：

```bash
python main.py export_devices_attributes_history --group_id=<group_id>
```

将 `<group_id>` 替换为您要导出的设备组 ID。支持多个组，以逗号分隔。例如：`--group_id=<group_id1>,<group_id2>,<group_id3>`。

#### 示例 6

指定设备组下的所有设备，并包含子组下的所有设备，执行命令：

```bash
python main.py export_devices_attributes_history --group_id=<group_id> --include_sub_groups
```
