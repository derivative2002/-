import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from typing import Dict, List, Tuple

# 设置matplotlib样式
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'Microsoft YaHei']
plt.rcParams['font.serif'] = ['Times New Roman']  # 设置 Times New Roman
plt.rcParams['axes.unicode_minus'] = False
plt.style.use('classic')  # 使用经典样式
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['mathtext.fontset'] = 'custom'
plt.rcParams['mathtext.rm'] = 'Times New Roman'
plt.rcParams['mathtext.it'] = 'Times New Roman:italic'
plt.rcParams['mathtext.bf'] = 'Times New Roman:bold'

# 字节跳动配色方案
BYTEDANCE_COLORS = {
    'blue': '#2878B5',     # 主色蓝
    'light_blue': '#9AC9DB',  # 浅蓝
    'red': '#C82423',      # 红色
    'orange': '#F8AC8C',   # 橙色
    'purple': '#6956E5',   # 紫色
    'gray': '#F2F2F2',     # 背景灰
}

# 尝试加载系统中的中文字体
font_path = fm.findfont(fm.FontProperties(family=['Arial Unicode MS', 'SimHei', 'Microsoft YaHei']))
if font_path:
    plt.rcParams['font.family'] = fm.FontProperties(fname=font_path).get_name()

def calculate_reaper_dps(attack_upgrade: int = 0, has_raven_buff: bool = False) -> Dict[str, float]:
    """计算单个死神的DPS
    
    Args:
        attack_upgrade: 攻击升级等级(0-3)
        has_raven_buff: 是否有渡鸦buff(5层安全力场)
    
    Returns:
        包含对轻甲和重甲DPS的字典
    """
    # 基础伤害（含铀238升级）
    base_min = 8 * 2  # 双倍伤害
    base_max = 18 * 2
    
    # 攻防升级加成（每级+1点）
    min_damage = base_min + (attack_upgrade * 2)  # 双倍伤害所以*2
    max_damage = base_max + (attack_upgrade * 2)
    
    # 托什指挥官20%伤害加成
    min_damage *= 1.2
    max_damage *= 1.2
    
    # 安全力场加成（每层+1点，5层共+5点）
    if has_raven_buff:
        min_damage += 10  # 双倍伤害所以*2
        max_damage += 10
    
    # 计算DPS
    attack_speed = 1.1
    avg_damage = (min_damage + max_damage) / 2
    dps = avg_damage * attack_speed
    
    # 对重甲的伤害减半
    heavy_armor_dps = dps * 0.5
    
    return {
        "light_armor": dps,
        "heavy_armor": heavy_armor_dps
    }

def calculate_squad_cost(reapers: int) -> dict:
    """计算死神小队的资源消耗
    
    Args:
        reapers: 死神数量
    
    Returns:
        包含资源消耗的字典
    """
    # 死神：50矿50气，1人口
    # 运输船：150矿100气，2人口
    # 每艘运输船可以装载8个死神
    medivacs = (reapers + 7) // 8  # 向上取整
    
    return {
        "minerals": reapers * 50 + medivacs * 150,
        "gas": reapers * 50 + medivacs * 100,
        "supply": reapers * 1 + medivacs * 2
    }

def calculate_dps_by_supply(max_supply: int = 160, attack_upgrade: int = 3, has_raven_buff: bool = True) -> Tuple[List[int], List[float], List[float]]:
    """计算不同人口下的DPS
    
    Args:
        max_supply: 最大人口数
        attack_upgrade: 攻击升级等级
        has_raven_buff: 是否有渡鸦buff
    
    Returns:
        (人口列表, 对轻甲DPS列表, 对重甲DPS列表)
    """
    supplies = []
    light_dps = []
    heavy_dps = []
    
    # 从1个死神开始，直到达到最大人口
    for reapers in range(1, max_supply):
        cost = calculate_squad_cost(reapers)
        if cost["supply"] > max_supply:
            break
            
        dps = calculate_reaper_dps(attack_upgrade, has_raven_buff)
        supplies.append(cost["supply"])
        light_dps.append(dps["light_armor"] * reapers)
        heavy_dps.append(dps["heavy_armor"] * reapers)
    
    return supplies, light_dps, heavy_dps

def format_number(x, p):
    """格式化数字标签为Times New Roman字体"""
    return f'$\\mathregular{{{x:.0f}}}$'

def plot_dps_supply_curves():
    """绘制DPS-人口曲线图"""
    plt.figure(figsize=(12, 8), facecolor=BYTEDANCE_COLORS['gray'])
    
    # 设置背景色
    ax = plt.gca()
    ax.set_facecolor('white')
    
    # 设置刻度标签格式
    ax.yaxis.set_major_formatter(plt.FuncFormatter(format_number))
    ax.xaxis.set_major_formatter(plt.FuncFormatter(format_number))
    
    # 计算数据
    supplies, light_dps_no_buff, heavy_dps_no_buff = calculate_dps_by_supply(
        max_supply=160,
        attack_upgrade=3,
        has_raven_buff=False
    )
    
    _, light_dps_buff, heavy_dps_buff = calculate_dps_by_supply(
        max_supply=160,
        attack_upgrade=3,
        has_raven_buff=True
    )
    
    # 绘制曲线
    plt.plot(supplies, light_dps_no_buff, '-', label='对轻甲 (无buff)', color=BYTEDANCE_COLORS['blue'], linewidth=2)
    plt.plot(supplies, heavy_dps_no_buff, '-', label='对重甲 (无buff)', color=BYTEDANCE_COLORS['light_blue'], linewidth=2)
    plt.plot(supplies, light_dps_buff, '-', label='对轻甲 (满buff)', color=BYTEDANCE_COLORS['red'], linewidth=2)
    plt.plot(supplies, heavy_dps_buff, '-', label='对重甲 (满buff)', color=BYTEDANCE_COLORS['orange'], linewidth=2)
    
    # 设置图表样式
    plt.title('死神船队DPS随人口变化曲线 (3级攻击升级)', fontsize=16, pad=20)
    plt.xlabel('人口数', fontsize=14)
    plt.ylabel('DPS', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.legend(fontsize=12, loc='upper left', frameon=True, facecolor='white', edgecolor='none')
    
    # 添加关键点标注
    for supply in range(40, 161, 40):
        idx = supplies.index(min(supplies, key=lambda x: abs(x - supply)))
        plt.plot([supplies[idx]], [light_dps_buff[idx]], 'o', color=BYTEDANCE_COLORS['red'])
        plt.text(supplies[idx], light_dps_buff[idx], f'$\\mathregular{{{light_dps_buff[idx]:.0f}}}$', 
                ha='center', va='bottom', fontsize=10)
        plt.plot([supplies[idx]], [heavy_dps_buff[idx]], 'o', color=BYTEDANCE_COLORS['orange'])
        plt.text(supplies[idx], heavy_dps_buff[idx], f'$\\mathregular{{{heavy_dps_buff[idx]:.0f}}}$', 
                ha='center', va='bottom', fontsize=10)
    
    # 保存图表
    plt.tight_layout()
    plt.savefig('死神船队DPS人口分析.png', dpi=300, bbox_inches='tight', facecolor=BYTEDANCE_COLORS['gray'])
    plt.close()

def calculate_upgrade_cost(level: int) -> Dict[str, float]:
    """计算升级的资源消耗
    
    Args:
        level: 升级等级(1-3)
    
    Returns:
        包含资源消耗的字典
    """
    costs = {
        1: {"minerals": 100, "gas": 100, "time": 120},
        2: {"minerals": 150, "gas": 150, "time": 160},
        3: {"minerals": 200, "gas": 200, "time": 200}
    }
    return costs[level]

def analyze_upgrade_efficiency(reaper_count: int = 30) -> None:
    """分析升级的资源效率
    
    Args:
        reaper_count: 死神数量
    """
    print(f"\n升级资源效率分析（基于{reaper_count}个死神）：")
    
    # 计算基准DPS
    base_dps = calculate_reaper_dps(0, False)
    base_light = base_dps["light_armor"] * reaper_count
    
    # 分析每级升级的效率
    print("\n攻击升级效率：")
    for level in range(1, 4):
        # 计算DPS提升
        dps = calculate_reaper_dps(level, False)
        dps_gain = (dps["light_armor"] * reaper_count - base_light)
        
        # 计算资源消耗
        cost = calculate_upgrade_cost(level)
        total_cost = cost["minerals"] + cost["gas"] * 3  # 1气 ≈ 3矿
        
        # 计算效率（DPS提升/总资源消耗）
        efficiency = dps_gain / total_cost * 100
        
        print(f"{level}级攻击: ")
        print(f"  资源消耗: {cost['minerals']}矿 {cost['gas']}气 ({total_cost}矿等价)")
        print(f"  DPS提升: +{dps_gain:.1f}")
        print(f"  升级效率: {efficiency:.2f} DPS/100矿")
        print(f"  升级时间: {cost['time']}秒")

def analyze_upgrade_benefits(reaper_count: int = 30) -> None:
    """分析升级和buff对DPS的提升效果
    
    Args:
        reaper_count: 死神数量
    """
    print(f"\n升级收益分析（基于{reaper_count}个死神）：")
    
    # 计算基准DPS（无升级无buff）
    base_dps = calculate_reaper_dps(0, False)
    base_light = base_dps["light_armor"] * reaper_count
    base_heavy = base_dps["heavy_armor"] * reaper_count
    
    print(f"\n基准DPS（无升级无buff）:")
    print(f"vs轻甲: {base_light:.1f}")
    print(f"vs重甲: {base_heavy:.1f}")
    
    # 分析攻击升级的收益
    print("\n攻击升级收益分析:")
    for level in range(1, 4):
        dps = calculate_reaper_dps(level, False)
        light_gain = (dps["light_armor"] * reaper_count - base_light) / base_light * 100
        heavy_gain = (dps["heavy_armor"] * reaper_count - base_heavy) / base_heavy * 100
        print(f"{level}级攻击: +{light_gain:.1f}% vs轻甲, +{heavy_gain:.1f}% vs重甲")
    
    # 分析渡鸦buff的收益
    print("\n渡鸦buff收益分析:")
    # 无升级有buff
    dps_buff = calculate_reaper_dps(0, True)
    light_gain = (dps_buff["light_armor"] * reaper_count - base_light) / base_light * 100
    heavy_gain = (dps_buff["heavy_armor"] * reaper_count - base_heavy) / base_heavy * 100
    print(f"仅安全力场: +{light_gain:.1f}% vs轻甲, +{heavy_gain:.1f}% vs重甲")
    
    # 满升级满buff
    dps_full = calculate_reaper_dps(3, True)
    light_gain = (dps_full["light_armor"] * reaper_count - base_light) / base_light * 100
    heavy_gain = (dps_full["heavy_armor"] * reaper_count - base_heavy) / base_heavy * 100
    print(f"满升级+安全力场: +{light_gain:.1f}% vs轻甲, +{heavy_gain:.1f}% vs重甲")

def calculate_equivalent_unit_dps(supply: int, upgrade_level: int = 0, has_raven_buff: bool = False) -> Dict[str, float]:
    """计算给定人口下的最大DPS输出
    
    Args:
        supply: 人口数
        upgrade_level: 升级等级（0-3）
        has_raven_buff: 是否有渡鸦buff
        
    Returns:
        包含对轻甲和重甲DPS的字典
    """
    # 计算最大可用运输船数量和死神数量
    medivacs = (supply + 7) // 16  # 每个运输船占2人口，最多能装8个死神
    reapers = supply - (medivacs * 2)  # 剩余人口用于死神
    
    if reapers <= 0:
        return {"light_armor": 0, "heavy_armor": 0}
    
    # 计算DPS
    dps = calculate_reaper_dps(upgrade_level, has_raven_buff)
    return {
        "light_armor": dps["light_armor"] * reapers,
        "heavy_armor": dps["heavy_armor"] * reapers
    }

def plot_resource_equivalent_curves():
    """绘制等人口下的DPS对比曲线"""
    plt.figure(figsize=(12, 8), facecolor=BYTEDANCE_COLORS['gray'])
    
    # 设置背景色
    ax = plt.gca()
    ax.set_facecolor('white')
    
    # 设置刻度标签格式
    ax.yaxis.set_major_formatter(plt.FuncFormatter(format_number))
    ax.xaxis.set_major_formatter(plt.FuncFormatter(format_number))
    
    # 准备数据
    supplies = list(range(20, 161, 20))  # 从20到160人口
    dps_data = {
        "no_upgrade": {"light": [], "heavy": []},
        "attack1": {"light": [], "heavy": []},
        "attack2": {"light": [], "heavy": []},
        "attack3": {"light": [], "heavy": []}
    }
    
    for supply in supplies:
        for upgrade in range(4):
            key = f"attack{upgrade}" if upgrade > 0 else "no_upgrade"
            dps = calculate_equivalent_unit_dps(supply, upgrade, False)
            dps_data[key]["light"].append(dps["light_armor"])
            dps_data[key]["heavy"].append(dps["heavy_armor"])
    
    # 绘制轻甲DPS曲线
    plt.plot(supplies, dps_data["no_upgrade"]["light"], '-', 
             label='纯造兵 vs轻甲', 
             color=BYTEDANCE_COLORS['blue'], linewidth=2)
    plt.plot(supplies, dps_data["attack1"]["light"], '-', 
             label=f'1级攻击 vs轻甲 (100矿100气)', 
             color=BYTEDANCE_COLORS['light_blue'], linewidth=2)
    plt.plot(supplies, dps_data["attack2"]["light"], '-', 
             label=f'2级攻击 vs轻甲 (总计250矿250气)', 
             color=BYTEDANCE_COLORS['red'], linewidth=2)
    plt.plot(supplies, dps_data["attack3"]["light"], '-', 
             label=f'3级攻击 vs轻甲 (总计450矿450气)', 
             color=BYTEDANCE_COLORS['purple'], linewidth=2)
    
    # 绘制重甲DPS曲线（虚线）
    plt.plot(supplies, dps_data["no_upgrade"]["heavy"], '--', 
             label='纯造兵 vs重甲', 
             color=BYTEDANCE_COLORS['blue'], linewidth=2)
    plt.plot(supplies, dps_data["attack1"]["heavy"], '--', 
             label=f'1级攻击 vs重甲', 
             color=BYTEDANCE_COLORS['light_blue'], linewidth=2)
    plt.plot(supplies, dps_data["attack2"]["heavy"], '--', 
             label=f'2级攻击 vs重甲', 
             color=BYTEDANCE_COLORS['red'], linewidth=2)
    plt.plot(supplies, dps_data["attack3"]["heavy"], '--', 
             label=f'3级攻击 vs重甲', 
             color=BYTEDANCE_COLORS['purple'], linewidth=2)
    
    # 添加关键点标注（只标注轻甲DPS）
    for supply in supplies:
        for upgrade, data in dps_data.items():
            idx = supplies.index(supply)
            plt.plot([supply], [data["light"][idx]], 'o', 
                    color=plt.gca().lines[-1].get_color(), markersize=4)
            plt.text(supply, data["light"][idx], f'$\\mathregular{{{data["light"][idx]:.0f}}}$', 
                    ha='center', va='bottom', fontsize=8)
    
    # 添加结论文本
    conclusion_text = (
        "结论：\n"
        "1. 升级对轻甲和重甲伤害提升相同\n"
        "2. 对重甲伤害恒为轻甲的50%\n"
        "3. 高级别升级性价比更高"
    )
    plt.text(0.02, 0.98, conclusion_text,
             transform=ax.transAxes,
             verticalalignment='top',
             bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'),
             fontsize=10)
    
    # 设置图表样式
    plt.title('等人口下的DPS对比曲线', fontsize=16, pad=20)
    plt.xlabel('人口数', fontsize=14)
    plt.ylabel('DPS', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.legend(fontsize=10, loc='upper left', frameon=True, facecolor='white', edgecolor='none')
    
    # 保存图表
    plt.tight_layout()
    plt.savefig('死神等人口DPS分析.png', dpi=300, bbox_inches='tight', facecolor=BYTEDANCE_COLORS['gray'])
    plt.close()

def plot_upgrade_efficiency_curves():
    """绘制升级效率曲线图"""
    plt.figure(figsize=(12, 8), facecolor=BYTEDANCE_COLORS['gray'])
    
    # 设置背景色
    ax = plt.gca()
    ax.set_facecolor('white')
    
    # 设置刻度标签格式
    ax.yaxis.set_major_formatter(plt.FuncFormatter(format_number))
    ax.xaxis.set_major_formatter(plt.FuncFormatter(format_number))
    
    # 准备数据
    reapers = range(10, 121, 10)
    dps_gains = {
        "attack1": {"dps": [], "cost": calculate_upgrade_cost(1)},  # 1级攻击
        "attack2": {"dps": [], "cost": calculate_upgrade_cost(2)},  # 2级攻击（包含1级）
        "attack3": {"dps": [], "cost": calculate_upgrade_cost(3)},  # 3级攻击（包含1、2级）
        "raven": {"dps": [], "cost": {"minerals": 100, "gas": 200, "time": 0}}  # 渡鸦buff
    }
    
    for count in reapers:
        # 计算基础DPS（无升级）
        base_dps = calculate_reaper_dps(0, False)["light_armor"] * count
        
        # 1级攻击的DPS提升
        dps_1 = calculate_reaper_dps(1, False)["light_armor"] * count
        dps_gains["attack1"]["dps"].append(dps_1 - base_dps)
        
        # 2级攻击的DPS提升（相对于无升级）
        dps_2 = calculate_reaper_dps(2, False)["light_armor"] * count
        dps_gains["attack2"]["dps"].append(dps_2 - base_dps)
        
        # 3级攻击的DPS提升（相对于无升级）
        dps_3 = calculate_reaper_dps(3, False)["light_armor"] * count
        dps_gains["attack3"]["dps"].append(dps_3 - base_dps)
        
        # 渡鸦buff的DPS提升
        dps_buff = calculate_reaper_dps(0, True)["light_armor"] * count
        dps_gains["raven"]["dps"].append(dps_buff - base_dps)
    
    # 绘制曲线
    plt.plot(reapers, dps_gains["attack1"]["dps"], '-', 
             label=f'1级攻击 ({dps_gains["attack1"]["cost"]["minerals"]}矿/{dps_gains["attack1"]["cost"]["gas"]}气/{dps_gains["attack1"]["cost"]["time"]}s)', 
             color=BYTEDANCE_COLORS['blue'], linewidth=2)
    plt.plot(reapers, dps_gains["attack2"]["dps"], '-', 
             label=f'2级攻击 (总计{dps_gains["attack1"]["cost"]["minerals"]+dps_gains["attack2"]["cost"]["minerals"]}矿/{dps_gains["attack1"]["cost"]["gas"]+dps_gains["attack2"]["cost"]["gas"]}气)', 
             color=BYTEDANCE_COLORS['light_blue'], linewidth=2)
    plt.plot(reapers, dps_gains["attack3"]["dps"], '-', 
             label=f'3级攻击 (总计{dps_gains["attack1"]["cost"]["minerals"]+dps_gains["attack2"]["cost"]["minerals"]+dps_gains["attack3"]["cost"]["minerals"]}矿/{dps_gains["attack1"]["cost"]["gas"]+dps_gains["attack2"]["cost"]["gas"]+dps_gains["attack3"]["cost"]["gas"]}气)', 
             color=BYTEDANCE_COLORS['red'], linewidth=2)
    plt.plot(reapers, dps_gains["raven"]["dps"], '--', 
             label=f'渡鸦buff ({dps_gains["raven"]["cost"]["minerals"]}矿/{dps_gains["raven"]["cost"]["gas"]}气)', 
             color=BYTEDANCE_COLORS['orange'], linewidth=2)
    
    # 添加结论文本
    conclusion_text = (
        "结论：\n"
        "1. 渡鸦buff提供最高的DPS提升\n"
        "2. 升级收益随死神数量线性增长\n"
        "3. 3级攻击总成本高但提升最大"
    )
    plt.text(0.02, 0.98, conclusion_text,
             transform=ax.transAxes,
             verticalalignment='top',
             bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'),
             fontsize=10)
    
    # 设置图表样式
    plt.title('死神数量与升级DPS提升关系曲线', fontsize=16, pad=20)
    plt.xlabel('死神数量', fontsize=14)
    plt.ylabel('DPS提升', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.legend(fontsize=10, loc='upper right', frameon=True, facecolor='white', edgecolor='none')
    
    # 保存图表
    plt.tight_layout()
    plt.savefig('死神升级效率分析.png', dpi=300, bbox_inches='tight', facecolor=BYTEDANCE_COLORS['gray'])
    plt.close()

def main():
    """主函数"""
    # 计算并显示40/80/120/160人口时的数据
    print("\n死神船队人口分析：")
    for supply in [40, 80, 120, 160]:
        reapers = (supply - 2 * ((supply + 7) // 8)) // 1  # 计算最大死神数量
        cost = calculate_squad_cost(reapers)
        dps_no_buff = calculate_reaper_dps(3, False)
        dps_buff = calculate_reaper_dps(3, True)
        
        print(f"\n{supply}人口配置：")
        print(f"死神数量: {reapers}")
        print(f"运输船数量: {(reapers + 7) // 8}")
        print(f"资源消耗: {cost['minerals']}矿 {cost['gas']}气")
        print(f"实际人口: {cost['supply']}")
        print(f"总DPS (无buff): {dps_no_buff['light_armor'] * reapers:.1f} vs轻甲, {dps_no_buff['heavy_armor'] * reapers:.1f} vs重甲")
        print(f"总DPS (满buff): {dps_buff['light_armor'] * reapers:.1f} vs轻甲, {dps_buff['heavy_armor'] * reapers:.1f} vs重甲")
    
    # 分析升级收益
    analyze_upgrade_benefits(30)  # 基于30个死神分析
    
    # 分析升级效率
    analyze_upgrade_efficiency(30)  # 基于30个死神分析
    
    # 绘制DPS曲线图
    plot_dps_supply_curves()
    print("\n已生成DPS曲线图：死神船队DPS人口分析.png")
    
    # 绘制升级效率曲线图
    plot_upgrade_efficiency_curves()
    print("已生成升级效率曲线图：死神升级效率分析.png")
    
    # 绘制等人口DPS对比曲线
    plot_resource_equivalent_curves()
    print("已生成等人口DPS对比曲线图：死神等人口DPS分析.png")

if __name__ == "__main__":
    main() 