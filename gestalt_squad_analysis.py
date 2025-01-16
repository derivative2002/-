from gestalt_ghost import GestaltGhost, WeaponType as GhostWeapon
from gestalt_marine import GestaltMarine, WeaponType as MarineWeapon
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform

# 设置中文字体
if platform.system() == 'Darwin':  # macOS
    plt.rcParams['font.family'] = ['Arial Unicode MS']
else:  # Windows和其他系统
    plt.rcParams['font.family'] = ['Microsoft YaHei']

# 设置ByteDance风格的颜色
BYTEDANCE_COLORS = {
    'blue': '#2F88FF',
    'green': '#00B578', 
    'yellow': '#FFC524',
    'red': '#FF3B30',
    'gray': '#1C1C1E'
}

def calculate_actual_damage(base_damage: float, target_armor: int, armor_reduction: int = 0) -> float:
    """计算考虑护甲后的实际伤害
    
    Args:
        base_damage: 基础伤害
        target_armor: 目标护甲值
        armor_reduction: 护甲减免值
        
    Returns:
        实际伤害值（最小为0.5）
    """
    effective_armor = target_armor - armor_reduction  # 计算有效护甲
    if effective_armor >= 0:
        actual_damage = max(0.5, base_damage - effective_armor)  # 正护甲减少伤害
    else:
        actual_damage = base_damage + abs(effective_armor)  # 负护甲增加伤害
    return actual_damage

def calculate_squad_dps(ghost_count: int = 0, 
                       storm_marine_count: int = 0,
                       laser_marine_count: int = 0,
                       target_type: str = "普通",
                       target_armor: int = 0):
    """计算编队DPS
    
    Args:
        ghost_count: 裂解步枪鬼子数量
        storm_marine_count: 风暴突击步枪枪兵数量
        laser_marine_count: 重型激光炮枪兵数量
        target_type: 目标类型
        target_armor: 目标护甲值
    """
    total_dps = 0
    armor_reduction = 4 if ghost_count > 0 else 0  # 只要有裂解步枪就有4点护甲减免
    
    # 计算鬼子DPS
    if ghost_count > 0:
        ghost = GestaltGhost()
        ghost.rank_up()  # 升到2级解锁裂解步枪
        ghost.rank_up()  # 升到3级获得攻速加成
        ghost.switch_weapon(GhostWeapon.FISSION_RIFLE)
        weapon = ghost.weapons[GhostWeapon.FISSION_RIFLE]
        base_damage = weapon.base_damage
        if target_type in weapon.bonus_damage:
            base_damage = weapon.bonus_damage[target_type]
        
        # 裂解步枪是固定伤害，不受护甲影响
        actual_damage = base_damage
        attack_speed = ghost.get_attack_speed_with_rank(weapon.attack_speed)
        actual_dps = actual_damage / attack_speed
        total_dps += actual_dps * ghost_count
        
        print(f"\n裂解步枪鬼子 ({ghost_count}个):")
        print(f"- 基础伤害: {base_damage:.1f}")
        print(f"- 实际伤害: {actual_damage:.1f} (固定法术伤害)")
        print(f"- 攻击速度: {attack_speed:.2f}")
        print(f"- 单位DPS: {actual_dps:.1f}")
        print(f"- 总DPS: {actual_dps * ghost_count:.1f}")
        print(f"- 护甲减免: 4点 (多个裂解步枪不叠加)")
    
    # 计算风暴突击步枪枪兵DPS
    if storm_marine_count > 0:
        marine = GestaltMarine()
        marine.rank_up()  # 升到2级解锁风暴突击步枪
        marine.rank_up()  # 升到3级获得攻速加成
        marine.switch_weapon(MarineWeapon.STORM_RIFLE)
        weapon = marine.weapons[MarineWeapon.STORM_RIFLE]
        base_damage = weapon.base_damage
        if target_type in weapon.bonus_damage:
            base_damage = weapon.bonus_damage[target_type]
            
        # 考虑多重攻击
        base_damage *= weapon.multi_attack
        
        actual_damage = calculate_actual_damage(base_damage, target_armor, armor_reduction)
        attack_speed = marine.get_attack_speed_with_rank(weapon.attack_speed)
        actual_dps = actual_damage / attack_speed
        total_dps += actual_dps * storm_marine_count
        
        print(f"\n风暴突击步枪枪兵 ({storm_marine_count}个):")
        print(f"- 基础伤害: {base_damage:.1f} ({weapon.base_damage:.1f}x{weapon.multi_attack})")
        print(f"- 实际伤害: {actual_damage:.1f}")
        print(f"- 攻击速度: {attack_speed:.2f}")
        print(f"- 单位DPS: {actual_dps:.1f}")
        print(f"- 总DPS: {actual_dps * storm_marine_count:.1f}")
    
    # 计算重型激光炮枪兵DPS
    if laser_marine_count > 0:
        marine = GestaltMarine()
        marine.rank_up()  # 升到2级
        marine.rank_up()  # 升到3级解锁重型激光炮
        marine.switch_weapon(MarineWeapon.HEAVY_LASER)
        weapon = marine.weapons[MarineWeapon.HEAVY_LASER]
        base_damage = weapon.base_damage
        if target_type in weapon.bonus_damage:
            base_damage = weapon.bonus_damage[target_type]
            
        actual_damage = calculate_actual_damage(base_damage, target_armor, armor_reduction)
        attack_speed = marine.get_attack_speed_with_rank(weapon.attack_speed)
        actual_dps = actual_damage / attack_speed
        total_dps += actual_dps * laser_marine_count
        
        print(f"\n重型激光炮枪兵 ({laser_marine_count}个):")
        print(f"- 基础伤害: {base_damage:.1f}")
        print(f"- 实际伤害: {actual_damage:.1f}")
        print(f"- 攻击速度: {attack_speed:.2f}")
        print(f"- 单位DPS: {actual_dps:.1f}")
        print(f"- 总DPS: {actual_dps * laser_marine_count:.1f}")
    
    print(f"\n编队总DPS: {total_dps:.1f}")
    return total_dps

def compare_squads():
    """比较两种编队的输出"""
    # 测试不同护甲值的情况
    armor_values = [0, 2, 4, 6]
    
    for armor in armor_values:
        print(f"\n\n目标护甲: {armor}")
        print("=" * 50)
        
        print("\n编队1: 5个裂解步枪鬼子 + 30个风暴突击步枪枪兵")
        print("-" * 50)
        squad1_normal = calculate_squad_dps(ghost_count=5, storm_marine_count=30, target_armor=armor)
        print("\n对重甲目标:")
        squad1_heavy = calculate_squad_dps(ghost_count=5, storm_marine_count=30, target_type="重甲", target_armor=armor)
        
        print("\n\n编队2: 35个重型激光炮枪兵")
        print("-" * 50)
        squad2_normal = calculate_squad_dps(laser_marine_count=35, target_armor=armor)
        print("\n对重甲目标:")
        squad2_heavy = calculate_squad_dps(laser_marine_count=35, target_type="重甲", target_armor=armor)
        
        print("\n输出对比总结:")
        print("-" * 50)
        print(f"编队1 - 对普通目标: {squad1_normal:.1f} DPS")
        print(f"编队1 - 对重甲目标: {squad1_heavy:.1f} DPS (有4点护甲减免)")
        print(f"编队2 - 对普通目标: {squad2_normal:.1f} DPS")
        print(f"编队2 - 对重甲目标: {squad2_heavy:.1f} DPS")

def calculate_hellfire_ghost_dps(target_armor, is_mechanical=False):
    """计算炼狱火鬼子的DPS
    
    Args:
        target_armor: 目标护甲值
        is_mechanical: 是否为机械单位
    """
    base_damage = 100.0 if is_mechanical else 60.0  # 对机械单位100伤害，普通单位60伤害
    attack_speed = 0.83  # 3级军衔的攻击速度
    if target_armor >= 0:
        actual_damage = max(0.5, base_damage - target_armor)
    else:
        actual_damage = base_damage + abs(target_armor)
    return actual_damage / attack_speed

def calculate_reaper_dps(target_armor: int, target_type: str = "普通") -> float:
    # 基础伤害
    base_min = 8
    base_max = 18
    
    # 3级攻防加成
    base_min += 6
    base_max += 6
    
    # 托什20%加成
    base_min *= 1.2
    base_max *= 1.2
    
    # 安全力场加成
    base_min += 5
    base_max += 5
    
    # 对轻甲单位伤害加成
    if target_type == "轻甲":
        base_min *= 1.5
        base_max *= 1.5
    
    # 双倍伤害
    base_min *= 2
    base_max *= 2
    
    # 计算平均伤害
    avg_damage = (base_min + base_max) / 2
    
    # 计算护甲减伤
    if target_armor > 0:
        effective_damage = max(1, avg_damage - target_armor)
    else:
        effective_damage = avg_damage + abs(target_armor)  # 负护甲提供伤害加成
    
    # 攻击速度1.1秒
    dps = effective_damage / 1.1
    
    return dps

def calculate_reaper_squad_dps(target_armor: int) -> tuple[float, float]:
    # 128个死神的DPS
    normal_dps = calculate_reaper_dps(target_armor, "普通") * 128
    light_dps = calculate_reaper_dps(target_armor, "轻甲") * 128
    return normal_dps, light_dps

def plot_dps_comparison():
    """绘制不同护甲值下的DPS对比图"""
    armor_values = np.arange(0, 9, 1)  # 护甲范围0-8
    squad1_normal = []
    squad1_heavy = []
    squad2_normal = []
    squad2_heavy = []
    squad3_normal = []
    squad3_mechanical = []
    reaper_normal_dps = []
    reaper_light_dps = []

    for armor in armor_values:
        # 计算编队1对普通目标的DPS
        ghost_dps = calculate_ghost_dps(armor)
        marine_dps = calculate_marine_dps(armor)
        squad1_normal.append(ghost_dps * 5 + marine_dps * 30)  # 5个鬼子和30个枪兵
        squad1_heavy.append(ghost_dps * 5 + marine_dps * 30)

        # 计算编队2对普通目标的DPS
        squad2_normal.append(calculate_heavy_laser_dps(armor, is_heavy_target=False) * 35)  # 35个重激光
        squad2_heavy.append(calculate_heavy_laser_dps(armor, is_heavy_target=True) * 35)

        # 计算编队3的DPS
        hellfire_dps_normal = calculate_hellfire_ghost_dps(armor, is_mechanical=False)
        hellfire_dps_mechanical = calculate_hellfire_ghost_dps(armor, is_mechanical=True)
        squad3_normal.append(hellfire_dps_normal * 35)  # 35个炼狱火鬼兵
        squad3_mechanical.append(hellfire_dps_mechanical * 35)
        
        # 计算死神编队DPS
        normal, light = calculate_reaper_squad_dps(armor)
        reaper_normal_dps.append(normal)
        reaper_light_dps.append(light)

    # 创建图表
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # 设置背景网格
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.set_facecolor('#f0f0f0')
    
    # 绘制主要数据线
    ax.plot(armor_values, squad1_normal, '-', label='风暴裂解"5+30" vs普通目标\n(5裂解步枪鬼子+30风暴步枪枪兵)', 
            color=BYTEDANCE_COLORS['blue'], linewidth=2.5, marker='o', markersize=6)
    ax.plot(armor_values, squad1_heavy, '--', label='风暴裂解"5+30" vs重甲目标', 
            color=BYTEDANCE_COLORS['green'], linewidth=2.5, marker='s', markersize=6)
    ax.plot(armor_values, squad2_normal, '-', label='7枪重型激光炮 vs普通目标\n(35重型激光炮枪兵)', 
            color=BYTEDANCE_COLORS['yellow'], linewidth=2.5, marker='^', markersize=6)
    ax.plot(armor_values, squad2_heavy, '--', label='7枪重型激光炮 vs重甲目标', 
            color=BYTEDANCE_COLORS['red'], linewidth=2.5, marker='D', markersize=6)
    ax.plot(armor_values, squad3_normal, '-', label='7鬼炼狱火 vs普通目标\n(35炼狱火鬼兵)', 
            color='purple', linewidth=2.5, marker='*', markersize=8)
    ax.plot(armor_values, squad3_mechanical, '--', label='7鬼炼狱火 vs机械目标', 
            color='darkviolet', linewidth=2.5, marker='p', markersize=8)
    # 添加死神编队DPS曲线
    ax.plot(armor_values, reaper_normal_dps, color='brown', linestyle='-', marker='v', 
            label='托什死神船队 vs普通目标\n(128死神)', linewidth=2)
    ax.plot(armor_values, reaper_light_dps, color='orange', linestyle='--', marker='>', 
            label='托什死神船队 vs轻甲目标', linewidth=2)
    
    # 设置坐标轴
    ax.set_xlabel('敌方单位护甲值 (0到8)', fontsize=12, fontweight='bold')
    ax.set_ylabel('DPS输出', fontsize=12, fontweight='bold')
    
    # 设置刻度
    ax.tick_params(axis='both', which='major', labelsize=10)
    
    # 添加标题
    ax.set_title('格式塔零和托什不同部队组合在不同护甲下的DPS对比\n', fontsize=14, fontweight='bold')
    
    # 添加图例和说明
    # 先添加说明文本框
    ax.text(1.02, 0.98, '说明：\n- 裂解步枪提供4点护甲减免\n- 风暴步枪每次射击2发\n- 重激光对重甲伤害提升\n- 炼狱火对机械伤害提升\n- 死神满buff包含：\n  · 3级攻防升级\n  · 托什20%加成\n  · 5层安全力场',
            transform=ax.transAxes, fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # 在说明下方添加图例
    ax.legend(loc='center left', bbox_to_anchor=(1.02, 0.45), fontsize=10)
    
    # 调整布局以适应说明和图例
    plt.subplots_adjust(right=0.8)
    
    # 保存图表
    plt.savefig('格式塔零不同部队组合DPS对比.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 绘制相对DPS变化图
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # 设置背景网格
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.set_facecolor('#f0f0f0')
    
    # 计算相对DPS（每个编队以自己的最大DPS为基准）
    squad1_normal_max = max(squad1_normal)
    squad1_heavy_max = max(squad1_heavy)
    squad2_normal_max = max(squad2_normal)
    squad2_heavy_max = max(squad2_heavy)
    squad3_normal_max = max(squad3_normal)
    squad3_mechanical_max = max(squad3_mechanical)

    squad1_normal_relative = [x/squad1_normal_max * 100 for x in squad1_normal]
    squad1_heavy_relative = [x/squad1_heavy_max * 100 for x in squad1_heavy]
    squad2_normal_relative = [x/squad2_normal_max * 100 for x in squad2_normal]
    squad2_heavy_relative = [x/squad2_heavy_max * 100 for x in squad2_heavy]
    squad3_normal_relative = [x/squad3_normal_max * 100 for x in squad3_normal]
    squad3_mechanical_relative = [x/squad3_mechanical_max * 100 for x in squad3_mechanical]

    # 绘制主要数据线
    ax.plot(armor_values, squad1_normal_relative, '-', label='风暴裂解"5+30" vs普通目标\n(5裂解步枪鬼子+30风暴步枪枪兵)',
            color=BYTEDANCE_COLORS['blue'], linewidth=2.5, marker='o', markersize=6)
    ax.plot(armor_values, squad1_heavy_relative, '--', label='风暴裂解"5+30" vs重甲目标',
            color=BYTEDANCE_COLORS['green'], linewidth=2.5, marker='s', markersize=6)
    ax.plot(armor_values, squad2_normal_relative, '-', label='7枪重型激光炮 vs普通目标\n(35重型激光炮枪兵)',
            color=BYTEDANCE_COLORS['yellow'], linewidth=2.5, marker='^', markersize=6)
    ax.plot(armor_values, squad2_heavy_relative, '--', label='7枪重型激光炮 vs重甲目标',
            color=BYTEDANCE_COLORS['red'], linewidth=2.5, marker='D', markersize=6)
    ax.plot(armor_values, squad3_normal_relative, '-', label='7鬼炼狱火 vs普通目标\n(35炼狱火鬼兵)',
            color='purple', linewidth=2.5, marker='*', markersize=8)
    ax.plot(armor_values, squad3_mechanical_relative, '--', label='7鬼炼狱火 vs机械目标',
            color='darkviolet', linewidth=2.5, marker='p', markersize=8)
    
    # 设置坐标轴
    ax.set_xlabel('敌方单位护甲值 (0到8)', fontsize=12, fontweight='bold')
    ax.set_ylabel('相对DPS变化 (%)', fontsize=12, fontweight='bold')
    
    # 设置刻度
    ax.tick_params(axis='both', which='major', labelsize=10)
    
    # 添加标题
    ax.set_title('格式塔零不同部队组合在不同护甲下的相对DPS变化\n(以护甲0时为基准)', fontsize=14, fontweight='bold')
    
    # 添加图例和说明
    # 先添加说明文本框
    ax.text(1.02, 0.98, '说明：\n- 相对DPS = (当前DPS/编队最大DPS) × 100%\n- 每个编队以自己的最大DPS为100%基准\n- 展示不同护甲下DPS的相对变化',
            transform=ax.transAxes, fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # 在说明下方添加图例
    ax.legend(loc='center left', bbox_to_anchor=(1.02, 0.45), fontsize=10)
    
    # 调整布局以适应说明和图例
    plt.subplots_adjust(right=0.8)
    
    # 保存图表
    plt.savefig('格式塔零不同部队组合相对DPS对比.png', dpi=300, bbox_inches='tight')
    plt.close()

def calculate_ghost_dps(target_armor):
    """计算裂解步枪鬼子的DPS
    裂解步枪是固定伤害的法术伤害，不受护甲影响，只提供护甲减免效果"""
    base_damage = 12.0  # 固定伤害
    attack_speed = 0.58
    return base_damage / attack_speed  # 直接返回固定DPS，不考虑护甲

def calculate_marine_dps(target_armor):
    """计算风暴突击步枪枪兵的DPS"""
    base_damage = 7.0  # 每发7伤害，每次射击2发
    attack_speed = 0.20
    shots_per_attack = 2
    effective_armor = target_armor - 4  # 受益于鬼子的护甲减免
    if effective_armor >= 0:
        actual_damage = max(0.5, base_damage - effective_armor) * shots_per_attack
    else:
        actual_damage = (base_damage + abs(effective_armor)) * shots_per_attack
    return actual_damage / attack_speed

def calculate_heavy_laser_dps(target_armor, is_heavy_target=False):
    """计算重型激光炮枪兵的DPS"""
    base_damage = 110.0 if is_heavy_target else 80.0
    attack_speed = 2.07
    if target_armor >= 0:
        actual_damage = max(0.5, base_damage - target_armor)
    else:
        actual_damage = base_damage + abs(target_armor)
    return actual_damage / attack_speed

if __name__ == "__main__":
    compare_squads()
    print("\n正在生成图表...")
    plot_dps_comparison()
    print("图表生成完成：")
    print("1. 格式塔零不同部队组合DPS对比.png")
    print("2. 格式塔零不同部队组合相对DPS对比.png") 