from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Set
import time

class EffectType(Enum):
    """效果类型枚举"""
    SAFETY_FIELD = "安全力场"
    EMP = "电磁脉冲"
    INTERFERENCE = "干扰矩阵"

@dataclass
class Effect:
    """效果类"""
    type: EffectType
    duration: float  # 持续时间
    start_time: float  # 开始时间
    bonus_damage: float = 0  # 伤害加成
    bonus_armor: float = 0  # 护甲加成
    bonus_hp_regen: float = 0  # 生命恢复加成

class Unit:
    """基础单位类"""
    def __init__(self):
        self.hp = 100
        self.max_hp = 100
        self.armor = 0
        self.movement_speed = 2.25
        self.effects: List[Effect] = []

    def apply_effect(self, effect: Effect):
        """应用效果"""
        self.effects.append(effect)

    def remove_effect(self, effect_type: EffectType):
        """移除效果"""
        self.effects = [e for e in self.effects if e.type != effect_type]

    def update(self, current_time: float):
        """更新状态"""
        # 移除过期效果
        self.effects = [e for e in self.effects if current_time - e.start_time < e.duration]
        
        # 计算当前效果
        for effect in self.effects:
            if effect.type == EffectType.SAFETY_FIELD:
                self.hp = min(self.max_hp, self.hp + effect.bonus_hp_regen)

class SafetyField:
    """安全力场类"""
    def __init__(self):
        self.duration = 10  # 持续10秒
        self.cooldown = 45  # 冷却45秒
        self.last_cast_time = 0
        self.bonus_damage = 5  # 伤害加成
        self.bonus_armor = 2  # 护甲加成
        self.bonus_hp_regen = 2  # 每秒生命恢复

    def can_cast(self, current_time: float) -> bool:
        """检查是否可以施放"""
        return current_time - self.last_cast_time >= self.cooldown

    def cast(self, current_time: float, target: Unit) -> bool:
        """施放技能"""
        if self.can_cast(current_time):
            effect = Effect(
                type=EffectType.SAFETY_FIELD,
                duration=self.duration,
                start_time=current_time,
                bonus_damage=self.bonus_damage,
                bonus_armor=self.bonus_armor,
                bonus_hp_regen=self.bonus_hp_regen
            )
            target.apply_effect(effect)
            self.last_cast_time = current_time
            return True
        return False

class EMPTarget:
    """电磁脉冲目标类"""
    def __init__(self):
        self.affected_units: Set[Unit] = set()
        self.duration = 8  # 持续8秒
        self.cooldown = 30  # 冷却30秒
        self.last_cast_time = 0

    def can_cast(self, current_time: float) -> bool:
        """检查是否可以施放"""
        return current_time - self.last_cast_time >= self.cooldown

    def cast(self, current_time: float, targets: List[Unit]) -> bool:
        """施放技能"""
        if self.can_cast(current_time):
            effect = Effect(
                type=EffectType.EMP,
                duration=self.duration,
                start_time=current_time
            )
            for target in targets:
                target.apply_effect(effect)
                self.affected_units.add(target)
            self.last_cast_time = current_time
            return True
        return False

    def update(self, current_time: float):
        """更新状态"""
        for unit in list(self.affected_units):
            if current_time - self.last_cast_time >= self.duration:
                unit.remove_effect(EffectType.EMP)
                self.affected_units.remove(unit)

class ToshRaven(Unit):
    """夜枭类"""
    def __init__(self):
        super().__init__()
        # 基础属性
        self.hp = 140
        self.max_hp = 140
        self.armor = 1
        self.armor_type = "轻甲"
        self.movement_speed = 2.25
        self.cost_minerals = 100
        self.cost_gas = 200
        self.build_time = 60
        
        # 能量系统
        self.energy = 50
        self.max_energy = 200
        self.energy_regen = 0.5625  # 每秒能量恢复
        
        # 技能系统
        self.safety_field = SafetyField()  # 安全力场
        self.emp_target = EMPTarget()  # 电磁脉冲
        
        # 状态
        self.last_update_time = time.time()

    def update(self, current_time: float):
        """更新状态"""
        super().update(current_time)
        
        # 更新能量
        time_passed = current_time - self.last_update_time
        self.energy = min(self.max_energy, self.energy + self.energy_regen * time_passed)
        
        # 更新技能状态
        self.emp_target.update(current_time)
        
        self.last_update_time = current_time

    def cast_safety_field(self, target: Unit) -> bool:
        """施放安全力场"""
        if self.energy >= 75:  # 能量消耗75
            current_time = time.time()
            if self.safety_field.cast(current_time, target):
                self.energy -= 75
                return True
        return False

    def cast_emp(self, targets: List[Unit]) -> bool:
        """施放电磁脉冲"""
        if self.energy >= 100:  # 能量消耗100
            current_time = time.time()
            if self.emp_target.cast(current_time, targets):
                self.energy -= 100
                return True
        return False

    def get_status(self) -> str:
        """获取状态信息"""
        current_time = time.time()
        
        status = []
        status.append(f"生命值: {self.hp}/{self.max_hp}")
        status.append(f"能量: {self.energy:.1f}/{self.max_energy}")
        
        # 技能状态
        if self.safety_field.can_cast(current_time):
            status.append("安全力场: 就绪")
        else:
            remaining = self.safety_field.cooldown - (current_time - self.safety_field.last_cast_time)
            status.append(f"安全力场: 冷却中 ({remaining:.1f}秒)")
            
        if self.emp_target.can_cast(current_time):
            status.append("电磁脉冲: 就绪")
        else:
            remaining = self.emp_target.cooldown - (current_time - self.emp_target.last_cast_time)
            status.append(f"电磁脉冲: 冷却中 ({remaining:.1f}秒)")
        
        return "\n".join(status) 