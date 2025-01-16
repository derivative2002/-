from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict
import time

class WeaponType(Enum):
    """武器类型枚举"""
    ASSAULT_RIFLE = "突击步枪"  # 初始武器
    MISSILE_RIFLE = "导弹突击步枪"  # 一级军衔
    STORM_RIFLE = "风暴突击步枪"  # 二级军衔
    FLAMETHROWER = "喷火器"  # 二级军衔
    PUNISHER = "火神震击炮"  # 三级军衔
    HEAVY_LASER = "重型激光炮"  # 三级军衔

@dataclass
class WeaponStats:
    """武器属性"""
    base_damage: float  # 基础伤害
    bonus_damage: Dict[str, float]  # 对特定目标的额外伤害
    attack_speed: float  # 基础攻击速度
    range: float  # 射程
    can_attack_air: bool = True  # 是否能攻击空中单位
    can_attack_ground: bool = True  # 是否能攻击地面单位
    is_splash: bool = False  # 是否有溅射伤害
    splash_radius: float = 0  # 溅射范围
    multi_attack: int = 1  # 多重攻击次数

class GestaltMarine:
    """格式塔零先驱者类"""
    def __init__(self):
        # 基础属性
        self.hp = 125  # 生命值
        self.max_hp = 125  # 最大生命值
        self.armor = 1  # 护甲值
        self.armor_type = "轻甲"  # 护甲类型
        self.movement_speed = 2.25  # 移动速度
        
        # 军衔系统
        self.rank = 1  # 当前军衔
        self.max_rank = 3  # 最大军衔
        
        # 武器系统
        self.weapons: Dict[WeaponType, WeaponStats] = {
            WeaponType.ASSAULT_RIFLE: WeaponStats(
                base_damage=14,
                bonus_damage={},
                attack_speed=0.7,
                range=7
            ),
            WeaponType.MISSILE_RIFLE: WeaponStats(
                base_damage=20,
                bonus_damage={"重甲": 45},
                attack_speed=1.4,
                range=10
            ),
            WeaponType.STORM_RIFLE: WeaponStats(
                base_damage=7,
                bonus_damage={},
                attack_speed=0.2,
                range=6,
                multi_attack=2
            ),
            WeaponType.FLAMETHROWER: WeaponStats(
                base_damage=6,
                bonus_damage={"轻甲": 9},
                attack_speed=0.2,
                range=5,
                can_attack_air=False,
                is_splash=True,
                splash_radius=2
            ),
            WeaponType.PUNISHER: WeaponStats(
                base_damage=35,
                bonus_damage={"轻甲": 50},
                attack_speed=1.0,
                range=6
            ),
            WeaponType.HEAVY_LASER: WeaponStats(
                base_damage=80,
                bonus_damage={"重甲": 110},
                attack_speed=2.5,
                range=10
            )
        }
        
        # 当前武器
        self.current_weapon = WeaponType.ASSAULT_RIFLE
        
        # 状态
        self.last_update_time = time.time()

    def get_available_weapons(self) -> List[WeaponType]:
        """获取当前军衔可用的武器"""
        available = [WeaponType.ASSAULT_RIFLE]  # 初始武器始终可用
        
        if self.rank >= 1:
            available.append(WeaponType.MISSILE_RIFLE)
        
        if self.rank >= 2:
            available.extend([WeaponType.STORM_RIFLE, WeaponType.FLAMETHROWER])
            
        if self.rank >= 3:
            available.extend([WeaponType.PUNISHER, WeaponType.HEAVY_LASER])
            
        return available

    def get_attack_speed_with_rank(self, base_speed: float) -> float:
        """计算包含军衔加成的攻击速度"""
        # 三级军衔攻速加成为0.83倍
        if base_speed <= 0.2:  # 如果基础攻速已经很快，则不再提升
            return base_speed
        return base_speed * 0.83

    def get_weapon_dps(self, weapon_type: Optional[WeaponType] = None, 
                      target_type: str = "普通") -> float:
        """计算武器DPS
        
        Args:
            weapon_type: 要计算的武器类型，默认为当前武器
            target_type: 目标类型（普通/轻甲/重甲）
        
        Returns:
            DPS值
        """
        if weapon_type is None:
            weapon_type = self.current_weapon
            
        weapon = self.weapons[weapon_type]
        
        # 基础伤害
        damage = weapon.base_damage
        
        # 特定目标额外伤害
        if target_type in weapon.bonus_damage:
            damage = weapon.bonus_damage[target_type]
            
        # 多重攻击
        damage *= weapon.multi_attack
            
        # 计算攻速
        attack_speed = self.get_attack_speed_with_rank(weapon.attack_speed)
        
        return damage / attack_speed

    def switch_weapon(self, weapon_type: WeaponType) -> bool:
        """切换武器
        
        Args:
            weapon_type: 要切换的武器类型
            
        Returns:
            是否切换成功
        """
        if weapon_type in self.get_available_weapons():
            self.current_weapon = weapon_type
            return True
        return False

    def rank_up(self) -> bool:
        """提升军衔
        
        Returns:
            是否提升成功
        """
        if self.rank < self.max_rank:
            self.rank += 1
            return True
        return False

    def get_status(self) -> str:
        """获取状态信息"""
        status = []
        status.append(f"生命值: {self.hp}/{self.max_hp}")
        status.append(f"军衔等级: {self.rank}")
        status.append(f"当前武器: {self.current_weapon.value}")
        
        weapon = self.weapons[self.current_weapon]
        attack_speed = self.get_attack_speed_with_rank(weapon.attack_speed)
        
        status.append(f"基础伤害: {weapon.base_damage}")
        if weapon.bonus_damage:
            for target, damage in weapon.bonus_damage.items():
                status.append(f"对{target}伤害: {damage}")
        if weapon.multi_attack > 1:
            status.append(f"多重攻击: {weapon.multi_attack}次")
        status.append(f"攻击速度: {attack_speed:.2f}")
        status.append(f"射程: {weapon.range}")
        
        if weapon.is_splash:
            status.append(f"溅射范围: {weapon.splash_radius}")
            
        dps = self.get_weapon_dps()
        status.append(f"基础DPS: {dps:.1f}")
        
        return "\n".join(status)

    def get_weapon_info(self) -> str:
        """获取所有可用武器信息"""
        info = []
        info.append(f"当前军衔: {self.rank}级")
        info.append("\n可用武器:")
        
        for weapon_type in self.get_available_weapons():
            weapon = self.weapons[weapon_type]
            info.append(f"\n{weapon_type.value}:")
            info.append(f"- 基础伤害: {weapon.base_damage}")
            if weapon.bonus_damage:
                for target, damage in weapon.bonus_damage.items():
                    info.append(f"- 对{target}伤害: {damage}")
            if weapon.multi_attack > 1:
                info.append(f"- 多重攻击: {weapon.multi_attack}次")
            attack_speed = self.get_attack_speed_with_rank(weapon.attack_speed)
            info.append(f"- 攻击速度: {attack_speed:.2f}")
            info.append(f"- 射程: {weapon.range}")
            if weapon.is_splash:
                info.append(f"- 溅射范围: {weapon.splash_radius}")
            dps = self.get_weapon_dps(weapon_type)
            info.append(f"- DPS: {dps:.1f}")
            
        return "\n".join(info) 