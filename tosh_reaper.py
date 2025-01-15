from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict
import time
import math

class WeaponType(Enum):
    """武器类型枚举"""
    P55_SCYTHE = "P55镰刀电磁枪"
    D9_EXPLOSIVE = "D9炸药"
    SPIDER_MINE = "蜘蛛雷"

@dataclass
class WeaponStats:
    """武器属性"""
    min_damage: float  # 最小伤害
    max_damage: float  # 最大伤害
    attack_speed: float  # 攻击速度
    range: float  # 射程
    is_splash: bool = False  # 是否有溅射伤害
    splash_radius: float = 0  # 溅射范围

class SpiderMine:
    """蜘蛛雷类"""
    def __init__(self):
        self.damage = 125  # 基础伤害
        self.splash_radius = 1.5  # 爆炸范围
        self.arm_time = 3  # 布设时间
        self.detection_radius = 6  # 侦测范围
        self.movement_speed = 2.5  # 追击速度
        self.hp = 15  # 生命值
        self.cost = 15  # 能量消耗
        self.max_count = 3  # 最大同时存在数量

class ToshReaper:
    """死神之首类"""
    def __init__(self):
        # 基础属性
        self.hp = 150  # 生命值
        self.max_hp = 150  # 最大生命值
        self.armor = 1  # 护甲值
        self.armor_type = "轻甲"  # 护甲类型
        self.movement_speed = 2.25  # 移动速度
        self.cost_minerals = 50  # 矿物消耗
        self.cost_gas = 50  # 气体消耗
        self.build_time = 45  # 建造时间
        
        # 能量系统
        self.energy = 50  # 初始能量
        self.max_energy = 200  # 最大能量
        self.energy_regen = 0.5625  # 每秒能量恢复
        
        # 武器系统
        self.weapons: Dict[WeaponType, WeaponStats] = {
            WeaponType.P55_SCYTHE: WeaponStats(
                min_damage=8,
                max_damage=18,
                attack_speed=1.1,  # 每秒攻击次数
                range=6
            ),
            WeaponType.D9_EXPLOSIVE: WeaponStats(
                min_damage=20,
                max_damage=40,
                attack_speed=0.8,
                range=2,
                is_splash=True,
                splash_radius=1.5
            )
        }
        
        # 蜘蛛雷系统
        self.spider_mine = SpiderMine()
        self.deployed_mines = 0  # 已部署的蜘蛛雷数量
        
        # 升级状态
        self.attack_upgrade = 0  # 攻击升级等级
        self.defense_upgrade = 0  # 防御升级等级
        self.has_uranium_upgrade = False  # 是否有铀238升级
        
        # 状态追踪
        self.last_update_time = time.time()
        self.current_weapon = WeaponType.P55_SCYTHE
        self.is_cloaked = False

    def update(self, current_time: float):
        """更新状态"""
        # 更新能量
        time_passed = current_time - self.last_update_time
        self.energy = min(self.max_energy, self.energy + self.energy_regen * time_passed)
        self.last_update_time = current_time

    def switch_weapon(self) -> WeaponType:
        """切换武器"""
        self.current_weapon = (
            WeaponType.D9_EXPLOSIVE 
            if self.current_weapon == WeaponType.P55_SCYTHE 
            else WeaponType.P55_SCYTHE
        )
        return self.current_weapon

    def deploy_spider_mine(self) -> bool:
        """部署蜘蛛雷"""
        if (self.energy >= self.spider_mine.cost and 
            self.deployed_mines < self.spider_mine.max_count):
            self.energy -= self.spider_mine.cost
            self.deployed_mines += 1
            return True
        return False

    def get_weapon_damage(self, weapon_type: WeaponType = None) -> tuple[float, float]:
        """获取武器伤害"""
        if weapon_type is None:
            weapon_type = self.current_weapon
            
        weapon = self.weapons[weapon_type]
        
        # 基础伤害
        min_damage = weapon.min_damage
        max_damage = weapon.max_damage
        
        # 攻击升级加成(每级+1点)
        min_damage += self.attack_upgrade
        max_damage += self.attack_upgrade
        
        # 铀238升级加成
        if self.has_uranium_upgrade:
            if weapon_type == WeaponType.P55_SCYTHE:
                min_damage = 10
                max_damage = 30
            elif weapon_type == WeaponType.D9_EXPLOSIVE:
                min_damage = 25
                max_damage = 45
        
        return min_damage, max_damage

    def get_weapon_dps(self, weapon_type: WeaponType = None) -> float:
        """计算武器DPS"""
        if weapon_type is None:
            weapon_type = self.current_weapon
            
        min_damage, max_damage = self.get_weapon_damage(weapon_type)
        avg_damage = (min_damage + max_damage) / 2
        attack_speed = self.weapons[weapon_type].attack_speed
        
        return avg_damage * attack_speed

    def get_status(self) -> str:
        """获取状态信息"""
        status = []
        status.append(f"生命值: {self.hp}/{self.max_hp}")
        status.append(f"能量: {self.energy:.1f}/{self.max_energy}")
        status.append(f"当前武器: {self.current_weapon.value}")
        
        min_damage, max_damage = self.get_weapon_damage()
        dps = self.get_weapon_dps()
        status.append(f"当前伤害: {min_damage}-{max_damage}")
        status.append(f"DPS: {dps:.1f}")
        
        status.append(f"已部署蜘蛛雷: {self.deployed_mines}/{self.spider_mine.max_count}")
        
        if self.is_cloaked:
            status.append("状态: 隐形")
            
        return "\n".join(status)

    def get_upgrade_info(self) -> str:
        """获取升级信息"""
        info = []
        info.append(f"攻击升级: {self.attack_upgrade}级")
        info.append(f"防御升级: {self.defense_upgrade}级")
        info.append(f"铀238升级: {'已获得' if self.has_uranium_upgrade else '未获得'}")
        
        # 显示各武器的伤害信息
        for weapon_type in WeaponType:
            if weapon_type != WeaponType.SPIDER_MINE:
                min_damage, max_damage = self.get_weapon_damage(weapon_type)
                dps = self.get_weapon_dps(weapon_type)
                info.append(f"\n{weapon_type.value}:")
                info.append(f"- 伤害: {min_damage}-{max_damage}")
                info.append(f"- DPS: {dps:.1f}")
        
        return "\n".join(info) 