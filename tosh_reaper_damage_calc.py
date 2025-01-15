def calculate_damage():
    """计算死神之首的满buff伤害
    
    包含以下加成：
    1. 铀238升级
    2. 3级攻防升级（+20%加成）
    3. 5层安全力场
    4. 托什指挥官20%加成
    """
    # 1. 基础伤害（铀238升级后）
    base_min = 8  # 单发最小伤害
    base_max = 18  # 单发最大伤害
    base_min_total = base_min * 2  # 多重攻击2次
    base_max_total = base_max * 2
    print(f"\n1. 基础伤害（含铀238，2次攻击）：{base_min_total}-{base_max_total}")
    
    # 2. 攻防和20%加成（作用在基础值上）
    bonus_min = 6.6 * 2  # 加成也要算2次（3级攻防+20%托什指挥官加成）
    bonus_max = 8.6 * 2
    upgraded_min = base_min_total + bonus_min
    upgraded_max = base_max_total + bonus_max
    print(f"2. 攻防和20%加成：{upgraded_min:.1f}-{upgraded_max:.1f}")
    
    # 3. 安全力场（每层+1点，不吃加成）
    safety_field_stacks = 5  # 5层安全力场
    safety_field_bonus = safety_field_stacks  # 每层+1点伤害
    final_min = upgraded_min + safety_field_bonus
    final_max = upgraded_max + safety_field_bonus
    print(f"3. 安全力场(+{safety_field_bonus}点)：{final_min:.1f}-{final_max:.1f}")
    
    # 4. 计算DPS
    attack_speed = 1.1  # 攻击速度
    average_damage = (final_min + final_max) / 2
    dps = average_damage * attack_speed
    print(f"4. DPS：({final_min:.1f} + {final_max:.1f})/2 * {attack_speed} = {dps:.1f}")

    # 返回计算结果
    return {
        "基础伤害": f"{base_min_total}-{base_max_total}",
        "攻防和20%加成后": f"{upgraded_min:.1f}-{upgraded_max:.1f}",
        "最终伤害": f"{final_min:.1f}-{final_max:.1f}",
        "DPS": f"{dps:.1f}"
    }

if __name__ == "__main__":
    result = calculate_damage()
    print("\n计算结果：")
    for key, value in result.items():
        print(f"{key}: {value}") 