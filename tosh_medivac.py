from enum import Enum
from typing import List, Optional, Tuple
from dataclasses import dataclass
import time

class UnitType(Enum):
    """单位类型枚举"""
    SCV = 1  # 工人
    TYCHUS = 1  # 托什
    MARINE = 1  # 枪兵
    DEATH_HEAD = 1  # 死神之首
    GHOST = 2  # 幽魂
    VIPER = 2  # 响尾蛇
    TANK = 4  # 坦克

@dataclass
class LoadedUnit:
    """装载的单位"""
    unit_type: UnitType
    can_return_to_base: bool = True  # SCV和托什不能返航
    
    @property
    def cargo_size(self) -> int:
        """获取单位占用的载员位"""
        return self.unit_type.value

class ToshMedivac:
    """特别行动运输船类"""
    def __init__(self):
        # 基础属性
        self.hp = 280  # 生命值
        self.max_hp = 280  # 最大生命值
        self.armor = 1  # 护甲值
        self.armor_type = "重甲"  # 护甲类型
        self.movement_speed = 2.75  # 移动速度
        self.cost_minerals = 150  # 矿物消耗
        self.cost_gas = 100  # 气体消耗
        self.build_time = 40  # 建造时间
        
        # 装载系统
        self.max_cargo_size = 8  # 最大载员位
        self.loaded_units: List[LoadedUnit] = []  # 已装载单位列表
        
        # 隐形系统
        self.cloak_duration = 6  # 隐形持续时间
        self.cloak_cooldown = 18  # 隐形冷却时间
        self.last_cloak_time = 0  # 上次隐形时间
        self.is_cloaked = False  # 是否隐形
        
        # 战术折跃
        self.has_tactical_jump = False  # 是否有战术折跃升级
        self.tactical_jump_cooldown = 60  # 战术折跃冷却时间
        self.last_jump_time = 0  # 上次使用战术折跃时间

    @property
    def current_cargo_size(self) -> int:
        """计算当前已使用的载员位"""
        return sum(unit.cargo_size for unit in self.loaded_units)

    def can_load_unit(self, unit_type: UnitType) -> bool:
        """检查是否可以装载指定单位"""
        return self.current_cargo_size + unit_type.value <= self.max_cargo_size

    def load_unit(self, unit_type: UnitType) -> bool:
        """装载单位"""
        if self.can_load_unit(unit_type):
            can_return = unit_type not in [UnitType.SCV, UnitType.TYCHUS]
            self.loaded_units.append(LoadedUnit(unit_type, can_return))
            return True
        return False

    def unload_all(self) -> List[LoadedUnit]:
        """卸载所有单位"""
        units = self.loaded_units.copy()
        self.loaded_units.clear()
        return units

    def return_to_base(self) -> Tuple[List[LoadedUnit], List[LoadedUnit]]:
        """返航，返回可以返航的单位和需要落地的单位"""
        returnable = []
        grounded = []
        for unit in self.loaded_units:
            if unit.can_return_to_base:
                returnable.append(unit)
            else:
                grounded.append(unit)
        self.loaded_units.clear()
        return returnable, grounded

    def activate_cloak(self, current_time: float) -> bool:
        """激活隐形"""
        if current_time - self.last_cloak_time >= self.cloak_cooldown:
            self.is_cloaked = True
            self.last_cloak_time = current_time
            return True
        return False

    def deactivate_cloak(self):
        """解除隐形"""
        self.is_cloaked = False

    def tactical_jump(self, current_time: float) -> bool:
        """使用战术折跃"""
        if (self.has_tactical_jump and 
            current_time - self.last_jump_time >= self.tactical_jump_cooldown):
            self.last_jump_time = current_time
            return True
        return False

    def upgrade_tactical_jump(self):
        """升级战术折跃能力"""
        self.has_tactical_jump = True

    def get_loaded_units_info(self) -> str:
        """获取已装载单位的信息"""
        unit_counts = {}
        for unit in self.loaded_units:
            unit_counts[unit.unit_type] = unit_counts.get(unit.unit_type, 0) + 1
        
        info = []
        for unit_type, count in unit_counts.items():
            info.append(f"{unit_type.name}: {count}个 (占用{unit_type.value * count}位)")
        
        return f"已用{self.current_cargo_size}/{self.max_cargo_size}载员位\n" + "\n".join(info)

    def get_combat_capabilities(self) -> str:
        """获取当前作战能力信息"""
        capabilities = []
        for unit in self.loaded_units:
            if unit.unit_type == UnitType.DEATH_HEAD:
                capabilities.append("死神：可使用P-55镰刀电磁枪(对空对地)和部署蜘蛛雷")
            elif unit.unit_type == UnitType.GHOST:
                capabilities.append("幽魂：可使用霰弹枪(对空对地范围伤害)、灵能鞭笞和超声波脉冲")
            elif unit.unit_type == UnitType.MARINE:
                capabilities.append("枪兵：正常攻击，无修改")
        
        return "\n".join(capabilities) if capabilities else "无战斗单位" 