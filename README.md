# Balenciaga 库存监控系统

这是一个用于监控Balenciaga商品库存并通过钉钉机器人发送通知的系统。

## 功能特点

- 自动抓取Balenciaga商品库存信息
- 将库存信息保存为本地文件
- 通过钉钉机器人向指定群组发送库存通知
  - 只在有新增商品时发送通知，其他变化情况不发送
  - 精简化的消息格式，清晰展示新增商品及其详情
- 支持定时任务和手动触发通知
- 串行执行爬虫任务，一个爬虫完成后再执行下一个
- 自动检测库存变化
- 每日生成库存汇总报告
- 支持为特定网站爬虫配置代理

## 系统改进说明

系统最近进行了以下改进：

1. 改进爬虫执行方式
   - 使用爬虫类实例化的方式运行爬虫任务
   - 为特定爬虫（如需要国外访问的网站）自动配置代理
   - 保持串行执行模式，确保系统稳定性

2. 优化代理配置管理
   - 在调度器中集中配置各爬虫的代理设置
   - 支持自动为需要代理的爬虫（如mrporter、antonioli等）配置clash代理
   - 无需修改各爬虫文件，只需在调度器中设置代理映射

3. 修复了文件路径
   - 更新了寻找最新库存文件的路径格式
   - 从`json_summary/inventory_summary_*.json`改为`inventory/balenciaga_inventory_*.json`

## 目录结构

```
balenciaga_monitor/
├── setting.init           # 钉钉机器人配置文件（Webhook URL和加签密钥）
├── scheduler_runner.py    # 调度器启动脚本
├── start_scheduler.bat    # Windows启动批处理脚本
├── start_scheduler.sh     # Linux/Unix启动脚本
├── src/
│   ├── crawler/           # 爬虫相关代码
│   │   ├── sugar_monitor.py     # Sugar网站爬虫
│   │   ├── mrporter_monitor.py  # MrPorter网站爬虫
│   │   └── ...                  # 其他网站爬虫
│   ├── ding_sender/       # 钉钉消息发送模块
│   ├── scheduler.py       # 定时任务调度器
│   ├── common/            # 公共模块和基类
│   └── data/              # 存储爬取的数据
│       ├── sugar/         # Sugar网站数据
│       ├── mrporter/      # MrPorter网站数据
│       └── ...            # 其他网站数据
├── data/                  # 总数据目录
│   └── reports/           # 每日汇总报告目录
├── logs/                  # 日志目录
└── README.md              # 项目说明文档
```

## 使用方法

### 配置钉钉机器人

1. 首先确保`setting.init`文件包含正确的钉钉机器人配置：
   - 第一行：钉钉机器人的Webhook URL
   - 第三行：钉钉机器人的加签密钥（如有）

### 启动自动监控调度器

使用以下命令启动自动监控调度器：

```bash
python scheduler_runner.py
```

调度器将：
- 每5分钟自动执行一次所有网站的爬虫任务（串行执行）
- 只有在检测到新增商品时才发送钉钉通知
- 每天23:00生成并发送每日库存汇总报告

### 爬虫执行方式

系统采用串行执行模式（栈执行）处理爬虫任务：
- 一个爬虫完成后才会执行下一个爬虫
- 爬虫之间有预设的等待时间（默认2秒）
- 每个爬虫任务失败后会自动重试一次
- 可以在日志中清晰查看每个爬虫的执行情况
- 自动为需要代理的爬虫配置代理设置

### 配置特定爬虫的代理

可以在`scheduler.py`文件中的`proxy_map`字典中配置需要代理的爬虫：

```python
self.proxy_map = {
    "antonioli_monitor": "clash",
    "mrporter_monitor": "clash",
    "giglio_monitor": "clash",
    "grifo210_monitor": "clash",
    # 可以根据需要添加更多需要代理的爬虫
}
```

目前支持的代理类型：
- clash: 使用本地Clash代理
- pin_zan: 使用品赞代理
- kuai_dai_li: 使用快代理

### 手动发送库存通知

如果需要手动发送特定的库存通知，可以运行：

```bash
python -m src.ding_sender.ding_sender [库存文件路径]
```

如果不指定库存文件路径，系统将自动寻找最新的库存数据文件。

### 示例

```bash
# 启动自动监控调度器
python scheduler_runner.py

# 手动发送指定库存文件的通知
python -m src.ding_sender.ding_sender data/sugar/inventory/balenciaga_inventory_20250418_230733.json
```

## 消息格式

### 新增商品通知

钉钉通知将以Markdown格式发送，只在有新增商品时发送，包含以下内容：

```
# 网站名

新增商品数: 3

新增时间: 2025-04-20 15:30:45

============

1. 商品名称

价格: €590.00

链接: https://example.com/product123

尺寸:
- In Stock: 40, 41, 42
- Limited: 39
- Sold Out: 43, 44

..........

2. 另一个商品名称
...
```

### 每日汇总报告

每日汇总报告包含：

- 各网站的商品总数
- 有库存商品数量与比例
- 缺货商品数量
- 最近更新时间
- 整体库存统计

## 开发说明

### 添加新网站支持

1. 在`src/crawler`下创建对应网站的爬虫模块，命名为`[网站名]_monitor.py`
2. 继承`Monitor`基类并实现必要的方法
3. 在文件末尾添加以下代码块以支持直接运行：
   ```python
   if __name__ == '__main__':
       monitor = 网站名Monitor(is_headless=True)
       monitor.run_with_log()
   ```
4. 如果该网站需要代理，在调度器的`proxy_map`中添加相应配置

### 手动定时任务

如果不想使用内置的调度器，可以通过系统定时任务（如cron或Windows计划任务）来定期运行脚本。

示例cron配置（每小时执行一次）：
```
0 * * * * cd /path/to/balenciaga_monitor && python -m src.ding_sender.ding_sender
```

## 错误处理

如果监控过程中出现问题，可以查看以下日志文件：

- `logs/scheduler_*.log`: 调度器主日志
- `logs/[网站名]/*.log`: 各网站爬虫的日志

常见错误解决方法：

- 钉钉机器人配置错误: 检查`setting.init`文件
- 网络连接问题: 检查代理配置和网络连接
- 爬虫解析失败: 检查网站是否变更了HTML结构

## 支持的网站

目前支持的网站及其特点：
- www.sugar.it: 国内直连，网页数据
- www.antonioli.eu: 需要VPN，网页数据（已配置clash代理）
- www.mytheresa.com: VPN（国内可直连但较慢），API接口
- www.julian-fashion.com: 国内可直连但较慢，网页数据
- www.giglio.com: 需要VPN，网页数据（已配置clash代理）
- www.grifo210.com: 需要VPN，网页数据（已配置clash代理）
- www.d2-store.com: 国内直连，网页数据
- www.rickowens.eu: 国内直连，网页数据加密，需要模拟
- www.hermes.com: 国内直连，存在滑块验证码
- www.eleonora-bonucci.com: 网页数据
- www.duomo.it: 网页数据
- www.suus.it: 网页数据
- www.mrporter.com: 网页数据，需要VPN（已配置clash代理）
- www.cettire.com: 网页数据

## 最近维护记录

### 2025-05-16 系统功能更新

1. **恢复爬虫类实例化执行方式**：
   - 从直接运行Python文件改回为实例化爬虫类的方式
   - 保留了串行执行流程，一个爬虫完成后再执行下一个
   - 增加了对爬虫实例的错误处理和重试机制

2. **增强代理配置功能**：
   - 新增集中式代理配置，在调度器中统一管理需要代理的爬虫
   - 为国外网站爬虫（antonioli、mrporter、giglio、grifo210等）自动配置clash代理
   - 支持多种代理类型，可根据需要灵活配置

3. **维持改进的文件路径**：
   - 继续使用`inventory/balenciaga_inventory_*.json`作为库存文件的存储路径
   - 保持查找最新库存文件的路径格式一致

这些更新使系统在保持稳定性的同时，提供了更灵活的代理配置选项，特别适合需要访问国外网站的场景。

以下网站的商品不能监控单独的商品尺寸，只能监控价格
suus 
mrporter
----
以下网站的商品不能监控单独的商品
eleonora_bonucci
grifo210
hermes
----
以下网站不能监控多个页面，也不能监控单个商品
cettire