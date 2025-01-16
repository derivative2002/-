from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict
import time

class WeaponType(Enum):
    """武器类型枚举"""
    TACTICAL_RIFLE = "战术步枪"  # 初始武器
    SHOTGUN = "霰弹枪"  # 一级军衔
    ALPHA_RIFLE = "阿尔法狙击枪"  # 二级军衔
    FISSION_RIFLE = "裂解步枪"  # 二级军衔
    DEATHWATCH = "死亡守望"  # 三级军衔
    HELLFIRE = "炼狱火"  # 三级军衔

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
    armor_reduction: int = 0  # 护甲减免

class GestaltGhost:
    """格式塔零渗透者类"""
    def __init__(self):
        # 基础属性
        self.hp = 100  # 生命值
        self.max_hp = 100  # 最大生命值
        self.armor = 0  # 护甲值
        self.armor_type = "轻甲"  # 护甲类型
        self.movement_speed = 2.25  # 移动速度
        
        # 军衔系统
        self.rank = 1  # 当前军衔
        self.max_rank = 3  # 最大军衔
        
        # 武器系统
        self.weapons: Dict[WeaponType, WeaponStats] = {
            WeaponType.TACTICAL_RIFLE: WeaponStats(
                base_damage=12,
                bonus_damage={},
                attack_speed=0.8,
                range=9
            ),
            WeaponType.SHOTGUN: WeaponStats(
                base_damage=23,
                bonus_damage={"轻甲": 31},
                attack_speed=1.75,
                range=4.5,
                is_splash=True,
                splash_radius=1.5
            ),
            WeaponType.ALPHA_RIFLE: WeaponStats(
                base_damage=30,
                bonus_damage={"生物": 60},
                attack_speed=2.5,
                range=13
            ),
            WeaponType.FISSION_RIFLE: WeaponStats(
                base_damage=12,
                bonus_damage={},
                attack_speed=0.7,
                range=8,
                armor_reduction=4
            ),
            WeaponType.DEATHWATCH: WeaponStats(
                base_damage=50,
                bonus_damage={"英雄": 110},
                attack_speed=3.0,
                range=17
            ),
            WeaponType.HELLFIRE: WeaponStats(
                base_damage=60,
                bonus_damage={"机械": 100},
                attack_speed=1.0,
                range=9,
                can_attack_air=False
            )
        }
        
        # 当前武器
        self.current_weapon = WeaponType.TACTICAL_RIFLE
        
        # 状态
        self.is_cloaked = False
        self.last_update_time = time.time()

    def get_available_weapons(self) -> List[WeaponType]:
        """获取当前军衔可用的武器"""
        available = [WeaponType.TACTICAL_RIFLE]  # 初始武器始终可用
        
        if self.rank >= 1:
            available.append(WeaponType.SHOTGUN)
        
        if self.rank >= 2:
            available.extend([WeaponType.ALPHA_RIFLE, WeaponType.FISSION_RIFLE])
            
        if self.rank >= 3:
            available.extend([WeaponType.DEATHWATCH, WeaponType.HELLFIRE])
            
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
            target_type: 目标类型（普通/轻甲/重甲/生物/英雄/机械）
        
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
        status.append(f"攻击速度: {attack_speed:.2f}")
        status.append(f"射程: {weapon.range}")
        
        if weapon.armor_reduction:
            status.append(f"护甲减免: {weapon.armor_reduction}")
            
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
            attack_speed = self.get_attack_speed_with_rank(weapon.attack_speed)
            info.append(f"- 攻击速度: {attack_speed:.2f}")
            info.append(f"- 射程: {weapon.range}")
            dps = self.get_weapon_dps(weapon_type)
            info.append(f"- DPS: {dps:.1f}")
            
        return "\n".join(info) 