#!/usr/bin/env python3
"""
Wbot OCP 求解器类

提供封装好的接口用于创建和求解 Wbot 机器人的最优控制问题 (OCP)
"""

import numpy as np
import pinocchio as pin
import crocoddyl
import os
from typing import Dict, Tuple, Optional, List


class ResidualModelRelativeXY(crocoddyl.ResidualModelAbstract):
    """Torso XY relative to base (world-aligned)."""

    def __init__(self, state, torso_frame_id, base_frame_id, nu=None):
        super().__init__(state, 2, nu)
        self.torso_frame_id = torso_frame_id
        self.base_frame_id = base_frame_id
        self.ankle_offset = np.array([-0.25, 0.0, 0.0])

    def calc(self, data, x, u=None):
        torso_pos = data.pinocchio.oMf[self.torso_frame_id].translation
        base_placement = data.pinocchio.oMf[self.base_frame_id]
        ankle_world = base_placement.translation + base_placement.rotation @ self.ankle_offset
        data.r[:] = torso_pos[:2] - ankle_world[:2]

    def calcDiff(self, data, x, u=None):
        J_torso = pin.getFrameJacobian(
            self.state.pinocchio, data.pinocchio, self.torso_frame_id, pin.LOCAL_WORLD_ALIGNED
        )[:2, :]
        J_base_full = pin.getFrameJacobian(
            self.state.pinocchio, data.pinocchio, self.base_frame_id, pin.LOCAL_WORLD_ALIGNED
        )
        ankle_world = data.pinocchio.oMf[self.base_frame_id].rotation @ self.ankle_offset
        J_base_translated = J_base_full[:3, :] - pin.skew(ankle_world) @ J_base_full[3:, :]
        J_base = J_base_translated[:2, :]

        data.Rx.fill(0.0)
        data.Rx[:, :self.state.nv] = J_torso - J_base

    def createData(self, data):
        return ResidualDataRelativeXY(self, data)


class ResidualDataRelativeXY(crocoddyl.ResidualDataAbstract):
    def __init__(self, model, data):
        super().__init__(model, data)
        self.pinocchio = data.pinocchio


class WbotOCPConfig:
    """OCP 配置参数"""

    def __init__(self):
        # === 差速驱动参数 ===
        self.wheel_radius = 0.0935  # m
        self.wheel_base = 0.42      # m

        # === 几何参数 ===
        self.main_wheel_radius = 0.095   # m
        self.caster_radius = 0.048       # m
        self.base_height = 0.0935        # m

        # === 位置权重 ===
        self.body_pos_weight = 500.0
        self.free_joint_pos_weight = 0.0
        self.arm_pos_weight = 1000.0

        # === 速度权重 ===
        self.body_vel_weight = 300.0
        self.arm_vel_weight = 5000.0
        self.wheel_vel_weight = 500.0  # 增加轮速权重以减少意外转向

        # === 速度限制 ===
        self.body_v_limit = 1.0  # rad/s
        self.arm_v_limit = 1.0   # rad/s

        # === 躯干约束权重 ===
        self.torso_xy_weight = 100.0
        self.torso_pitch_weight = 500.0

        # === 代价函数权重 ===
        self.state_reg_weight = 3e-1
        self.ctrl_reg_weight = 1e-1

        # === 力矩限制 ===
        self.u_max = 60.0  # Nm

        # === 时间参数 ===
        self.dt = 0.01  # s


class WbotOCP:
    """Wbot 机器人 OCP 求解器"""

    def __init__(self, mjcf_path: str, config: Optional[WbotOCPConfig] = None):
        """
        初始化 OCP 求解器

        参数:
            mjcf_path: MuJoCo XML 模型文件路径
            config: OCP 配置参数，如果为 None 则使用默认配置
        """
        self.mjcf_path = mjcf_path
        self.config = config if config is not None else WbotOCPConfig()

        # 加载模型
        self.model = pin.buildModelFromMJCF(mjcf_path)
        self.data = self.model.createData()

        # 缓存关节索引
        self.joint_indices = self._build_joint_indices()

        # 添加接触frames
        self.contact_frame_ids, self.contact_names = self._setup_contact_frames()

        # 重新创建 data（添加 frames 后）
        self.data = self.model.createData()

        # 创建 state 和 actuation
        self.state = crocoddyl.StateMultibody(self.model)
        self.actuation = crocoddyl.ActuationModelFull(self.state)
        self.nu = self.actuation.nu

        # 缓存常用的 frame IDs
        self.base_frame_id = self.model.getFrameId('Base_link')
        self.torso_frame_id = self.model.getFrameId('waist yaw-u') if self.model.existFrame('waist yaw-u') else None

        print(f"✓ WbotOCP 初始化完成")
        print(f"  模型: nq={self.model.nq}, nv={self.model.nv}")
        print(f"  控制: nu={self.nu}")
        print(f"  接触点数: {len(self.contact_frame_ids)}")

    def _build_joint_indices(self) -> Dict[str, Tuple[Optional[int], Optional[int]]]:
        """构建关节索引缓存"""
        joint_names = [
            'left', 'right', 'caster_yaw', 'caster_rotate',
            'ankle', 'knee', 'hip', 'waist_roll', 'waist_yaw',
            'right_arm_pitch', 'left_arm_pitch'
        ]

        indices = {}
        for name in joint_names:
            if self.model.existJointName(name):
                jid = self.model.getJointId(name)
                j = self.model.joints[jid]
                indices[name] = (j.idx_q, j.idx_v)
            else:
                indices[name] = (None, None)

        return indices

    def _setup_contact_frames(self) -> Tuple[List[int], List[str]]:
        """添加接触 frames"""
        contact_frame_ids = []
        contact_names = []

        # 轮子位置
        wheel_positions = {
            'left wheel-u': np.array([0.0, 0.15224, 0.0]),
            'right wheel-u': np.array([0.0, -0.15224, 0.0]),
        }

        # 万向轮位置
        caster_positions = {
            'caster_rear': np.array([-0.417, 0.0, -0.056]),
        }

        # 计算接触点位置
        contact_positions = {}
        for name, pos in wheel_positions.items():
            contact_positions[name] = pos + np.array([0.0, 0.0, -self.config.main_wheel_radius])
        for name, pos in caster_positions.items():
            contact_positions[name] = pos + np.array([0.0, 0.0, -self.config.caster_radius])

        base_frame_id = self.model.getFrameId('Base_link')
        base_joint_id = self.model.frames[base_frame_id].parentJoint

        # 添加主动轮接触
        for name in wheel_positions.keys():
            contact_pos = contact_positions[name]
            contact_placement = pin.SE3.Identity()
            contact_placement.translation = contact_pos

            contact_name = f"{name}_contact"
            contact_frame = pin.Frame(
                contact_name, base_joint_id, base_frame_id,
                contact_placement, pin.FrameType.OP_FRAME
            )

            contact_fid = self.model.addFrame(contact_frame)
            contact_frame_ids.append(contact_fid)
            contact_names.append(contact_name)

        # 添加万向轮接触
        for caster_name in caster_positions.keys():
            contact_pos = contact_positions[caster_name]
            contact_placement = pin.SE3.Identity()
            contact_placement.translation = contact_pos

            contact_frame_name = f"{caster_name}_contact"
            contact_frame = pin.Frame(
                contact_frame_name, base_joint_id, base_frame_id,
                contact_placement, pin.FrameType.OP_FRAME
            )

            contact_fid = self.model.addFrame(contact_frame)
            contact_frame_ids.append(contact_fid)
            contact_names.append(contact_frame_name)

        return contact_frame_ids, contact_names

    def create_contact_model(self) -> crocoddyl.ContactModelMultiple:
        """创建接触模型"""
        contactModel = crocoddyl.ContactModelMultiple(self.state, self.nu)

        for cfid, contact_name in zip(self.contact_frame_ids, self.contact_names):
            R_contact = np.eye(3)
            gains = np.array([0.0, 50.0])

            supportContactModel = crocoddyl.ContactModel1D(
                self.state, cfid, 0.0, pin.LOCAL_WORLD_ALIGNED,
                R_contact, self.nu, gains
            )
            contactModel.addContact(contact_name, supportContactModel)

        return contactModel

    def create_cost_model(self, target_joint_angles: Dict[str, float],
                         target_vx: float, target_omega_z: float,
                         x_current: Optional[np.ndarray] = None) -> crocoddyl.CostModelSum:
        """
        创建代价函数模型

        参数:
            target_joint_angles: 目标关节角度字典
            target_vx: 目标前进速度 (m/s)
            target_omega_z: 目标转向角速度 (rad/s)
            x_current: 当前状态（用于设置参考，避免追踪绝对位置）
        """
        costModel = crocoddyl.CostModelSum(self.state, self.nu)

        # 计算目标轮速
        target_wheel_vel_left = (target_vx - target_omega_z * self.config.wheel_base / 2) / self.config.wheel_radius
        target_wheel_vel_right = (target_vx + target_omega_z * self.config.wheel_base / 2) / self.config.wheel_radius

        # 构建目标状态
        # 从当前状态开始，避免追踪 base link 的绝对 x, y 位置（对移动机器人无意义）
        if x_current is not None:
            x_ref = x_current.copy()
        else:
            # 回退：使用固定参考（仅用于测试）
            x_ref = self.state.zero()
            x_ref[2] = self.config.base_height
            x_ref[3:7] = [0., 0., 0., 1.]

        # 设置关节目标角度
        for joint_name, target_angle in target_joint_angles.items():
            if self.model.existJointName(joint_name):
                joint_id = self.model.getJointId(joint_name)
                joint_q_idx = self.model.joints[joint_id].idx_q
                x_ref[joint_q_idx] = target_angle

        # 设置轮速目标
        left_wheel_v_idx = self.joint_indices['left'][1]
        right_wheel_v_idx = self.joint_indices['right'][1]
        if left_wheel_v_idx is not None:
            x_ref[self.state.nq + left_wheel_v_idx] = target_wheel_vel_left
        if right_wheel_v_idx is not None:
            x_ref[self.state.nq + right_wheel_v_idx] = target_wheel_vel_right

        # === 构建状态权重 ===
        vel_offset = self.model.nv
        body_joints_with_targets = ['knee', 'waist_roll', 'waist_yaw']
        body_joints_free = ['ankle', 'hip']
        body_joints_all = body_joints_with_targets + body_joints_free
        arm_joints = ['right_arm_pitch', 'left_arm_pitch']

        stateWeights = [0.0] * self.state.ndx
        stateWeights[0:3] = [0.0, 0.0, 0.0]
        stateWeights[3:6] = [0.0, 0.0, 0.0]

        # 位置权重
        for joint_name in target_joint_angles.keys():
            if self.model.existJointName(joint_name):
                joint_id = self.model.getJointId(joint_name)
                joint_v_idx = self.model.joints[joint_id].idx_v
                if joint_name in body_joints_with_targets:
                    stateWeights[joint_v_idx] = self.config.body_pos_weight
                elif joint_name in arm_joints:
                    stateWeights[joint_v_idx] = self.config.arm_pos_weight
                else:
                    stateWeights[joint_v_idx] = 1000.0

        for joint_name in body_joints_free:
            if self.model.existJointName(joint_name):
                joint_id = self.model.getJointId(joint_name)
                joint_v_idx = self.model.joints[joint_id].idx_v
                stateWeights[joint_v_idx] = self.config.free_joint_pos_weight

        # 轮子角度自由
        if left_wheel_v_idx is not None:
            stateWeights[left_wheel_v_idx] = 0.0
        if right_wheel_v_idx is not None:
            stateWeights[right_wheel_v_idx] = 0.0

        # 速度权重
        for body_joint in body_joints_all:
            if self.model.existJointName(body_joint):
                body_v_idx = self.model.joints[self.model.getJointId(body_joint)].idx_v
                stateWeights[vel_offset + body_v_idx] = self.config.body_vel_weight

        for arm_joint in arm_joints:
            if self.model.existJointName(arm_joint):
                arm_v_idx = self.model.joints[self.model.getJointId(arm_joint)].idx_v
                stateWeights[vel_offset + arm_v_idx] = self.config.arm_vel_weight

        if left_wheel_v_idx is not None:
            stateWeights[vel_offset + left_wheel_v_idx] = self.config.wheel_vel_weight
        if right_wheel_v_idx is not None:
            stateWeights[vel_offset + right_wheel_v_idx] = self.config.wheel_vel_weight

        # 默认权重
        for i in range(self.state.ndx):
            if stateWeights[i] == 0.0 and i not in (0, 1, 2):
                stateWeights[i] = 10.0

        stateWeights = np.array(stateWeights)

        # 状态跟踪代价
        stateResidual = crocoddyl.ResidualModelState(self.state, x_ref, self.nu)
        stateActivation = crocoddyl.ActivationModelWeightedQuad(stateWeights**2)
        stateReg = crocoddyl.CostModelResidual(self.state, stateActivation, stateResidual)
        costModel.addCost("stateReg", stateReg, self.config.state_reg_weight)

        # 躯干 XY 约束
        if self.torso_frame_id is not None:
            torso_xy_residual = ResidualModelRelativeXY(
                self.state, self.torso_frame_id, self.base_frame_id, self.nu
            )
            torso_translation_weights = np.array([self.config.torso_xy_weight, self.config.torso_xy_weight])
            torsoTranslationActivation = crocoddyl.ActivationModelWeightedQuad(torso_translation_weights**2)
            torsoTranslationCost = crocoddyl.CostModelResidual(
                self.state, torsoTranslationActivation, torso_xy_residual
            )
            costModel.addCost("torsoXY", torsoTranslationCost, 1.0)

            # 躯干 pitch 约束
            torso_orientation_residual = crocoddyl.ResidualModelFrameRotation(
                self.state, self.torso_frame_id, pin.SE3.Identity().rotation, self.nu
            )
            orientation_weights = np.array([0.0, self.config.torso_pitch_weight, 0.0])
            torsoOrientationActivation = crocoddyl.ActivationModelWeightedQuad(orientation_weights**2)
            torsoOrientationCost = crocoddyl.CostModelResidual(
                self.state, torsoOrientationActivation, torso_orientation_residual
            )
            costModel.addCost("torsoPitch", torsoOrientationCost, 1.0)

        # 控制正则化
        ctrlResidual = crocoddyl.ResidualModelControl(self.state, self.nu)
        ctrlReg = crocoddyl.CostModelResidual(self.state, ctrlResidual)
        costModel.addCost("ctrlReg", ctrlReg, self.config.ctrl_reg_weight)

        return costModel

    def create_action_models(self, target_joint_angles: Dict[str, float],
                            target_vx: float, target_omega_z: float,
                            x_current: Optional[np.ndarray] = None,
                            dt: Optional[float] = None) -> Tuple:
        """
        创建 action models (running 和 terminal)

        参数:
            x_current: 当前状态（传递给 cost model）

        返回:
            (model_running, model_terminal)
        """
        if dt is None:
            dt = self.config.dt

        # 创建接触模型和代价模型
        contactModel = self.create_contact_model()
        costModel = self.create_cost_model(target_joint_angles, target_vx, target_omega_z, x_current)

        # Differential action model
        dmodel = crocoddyl.DifferentialActionModelContactFwdDynamics(
            self.state, self.actuation, contactModel, costModel, 0.0, True
        )

        # 力矩限制
        dmodel.u_lb = np.full(self.nu, -self.config.u_max)
        dmodel.u_ub = np.full(self.nu, self.config.u_max)

        # Integrated action models
        model_running = crocoddyl.IntegratedActionModelEuler(dmodel, dt)
        model_terminal = crocoddyl.IntegratedActionModelEuler(dmodel, 0.0)

        # 状态约束（速度限制）
        x_lb = np.full(self.state.nx, -np.inf)
        x_ub = np.full(self.state.nx, np.inf)

        body_joints_all = ['ankle', 'knee', 'hip', 'waist_roll', 'waist_yaw']
        arm_joints = ['right_arm_pitch', 'left_arm_pitch']

        for body_joint in body_joints_all:
            if self.model.existJointName(body_joint):
                body_v_idx = self.model.joints[self.model.getJointId(body_joint)].idx_v
                x_lb[self.state.nq + body_v_idx] = -self.config.body_v_limit
                x_ub[self.state.nq + body_v_idx] = self.config.body_v_limit

        for arm_joint in arm_joints:
            if self.model.existJointName(arm_joint):
                arm_v_idx = self.model.joints[self.model.getJointId(arm_joint)].idx_v
                x_lb[self.state.nq + arm_v_idx] = -self.config.arm_v_limit
                x_ub[self.state.nq + arm_v_idx] = self.config.arm_v_limit

        model_running.x_lb = x_lb
        model_running.x_ub = x_ub

        return model_running, model_terminal

    def solve(self, x0: np.ndarray,
             target_joint_angles: Dict[str, float],
             target_vx: float = 1.0,
             target_omega_z: float = 0.0,
             horizon_steps: int = 50,
             max_iter: int = 100,
             warm_start: Optional[Tuple[List, List]] = None,
             verbose: bool = False) -> Dict:
        """
        求解 OCP

        参数:
            x0: 初始状态
            target_joint_angles: 目标关节角度
            target_vx: 目标前进速度
            target_omega_z: 目标转向角速度
            horizon_steps: 时域步数
            max_iter: 最大迭代次数
            warm_start: 热启动 (xs_init, us_init)，如果为 None 则使用零初始化
            verbose: 是否显示详细求解信息

        返回:
            包含求解结果的字典:
                - xs: 状态轨迹
                - us: 控制轨迹
                - cost: 代价
                - iter: 迭代次数
                - solver: 求解器对象
                - solve_time: 求解时间
        """
        import time

        # 创建 action models（传入 x0 以避免追踪绝对位置）
        model_running, model_terminal = self.create_action_models(
            target_joint_angles, target_vx, target_omega_z, x_current=x0
        )

        # Shooting problem
        running_models = [model_running] * horizon_steps
        problem = crocoddyl.ShootingProblem(x0, running_models, model_terminal)

        # Solver
        solver = crocoddyl.SolverBoxFDDP(problem)
        if verbose:
            solver.setCallbacks([crocoddyl.CallbackVerbose()])

        # 初始化猜测
        if warm_start is not None:
            xs_init, us_init = warm_start
        else:
            xs_init = [x0] * (horizon_steps + 1)
            us_init = [np.zeros(self.nu)] * horizon_steps

        # 求解
        start_time = time.time()
        solver.solve(xs_init, us_init, max_iter)
        solve_time = time.time() - start_time

        return {
            'xs': np.array(solver.xs),
            'us': np.array(solver.us),
            'cost': solver.cost,
            'iter': solver.iter,
            'solver': solver,
            'solve_time': solve_time
        }

    def get_initial_state(self) -> np.ndarray:
        """获取默认初始状态"""
        x0 = self.state.zero()
        x0[2] = self.config.base_height
        x0[3:7] = [0., 0., 0., 1.]
        return x0


if __name__ == "__main__":
    import sys

    # 测试
    script_dir = os.path.dirname(os.path.abspath(__file__))
    mjcf_path = os.path.join(script_dir, "description/urdf/wbot_v2.xml")

    print("=" * 70)
    print("WbotOCP 类测试".center(70))
    print("=" * 70)

    # 创建 OCP 求解器
    ocp = WbotOCP(mjcf_path)

    # 设置目标
    target_joint_angles = {
        'knee': -0.12,
        'waist_roll': 0.0,
        'waist_yaw': 0.0,
        'right_arm_pitch': 0.0,
        'left_arm_pitch': 0.0,
    }

    # 获取初始状态
    x0 = ocp.get_initial_state()

    print(f"\n开始求解 OCP...")
    print(f"  Horizon: 50步")
    print(f"  目标: vx=1.0 m/s, knee=-0.12 rad")

    # 求解
    result = ocp.solve(
        x0=x0,
        target_joint_angles=target_joint_angles,
        target_vx=1.0,
        target_omega_z=0.0,
        horizon_steps=50,
        max_iter=100,
        verbose=False
    )

    print(f"\n✓ 求解完成!")
    print(f"  迭代: {result['iter']}")
    print(f"  代价: {result['cost']:.2f}")
    print(f"  耗时: {result['solve_time']:.2f}s")
    print(f"  轨迹形状: xs={result['xs'].shape}, us={result['us'].shape}")

    print("\n" + "=" * 70)
