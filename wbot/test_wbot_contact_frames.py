#!/usr/bin/env python3
"""
测试：为轮底添加接触frames，然后用Contact3D
"""

import numpy as np
import pinocchio as pin
import crocoddyl
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 使用 MuJoCo XML 格式
MJCF_PATH = os.path.join(SCRIPT_DIR, "description/urdf/wbot_v2.xml")


class ResidualModelRelativeXY(crocoddyl.ResidualModelAbstract):
    """Torso XY relative to base (world-aligned)."""

    def __init__(self, state, torso_frame_id, base_frame_id, nu=None):
        super().__init__(state, 2, nu)
        self.torso_frame_id = torso_frame_id
        self.base_frame_id = base_frame_id
        # ankle joint placement in Base_link frame (from MJCF: lower leg-u pos)
        self.ankle_offset = np.array([-0.25, 0.0, 0.0])

    def calc(self, data, x, u=None):
        # Expect pinocchio data already updated by the dynamics model.
        torso_pos = data.pinocchio.oMf[self.torso_frame_id].translation
        base_placement = data.pinocchio.oMf[self.base_frame_id]
        ankle_world = base_placement.translation + base_placement.rotation @ self.ankle_offset
        data.r[:] = torso_pos[:2] - ankle_world[:2]

    def calcDiff(self, data, x, u=None):
        # Jacobian of translation w.r.t. configuration: use frame jacobians (LOCAL_WORLD_ALIGNED).
        J_torso = pin.getFrameJacobian(
            self.state.pinocchio, data.pinocchio, self.torso_frame_id, pin.LOCAL_WORLD_ALIGNED
        )[:2, :]
        J_base_full = pin.getFrameJacobian(
            self.state.pinocchio, data.pinocchio, self.base_frame_id, pin.LOCAL_WORLD_ALIGNED
        )
        # Translate Jacobian to ankle point on base (v + w x p)
        ankle_world = data.pinocchio.oMf[self.base_frame_id].rotation @ self.ankle_offset
        J_base_translated = J_base_full[:3, :] - pin.skew(ankle_world) @ J_base_full[3:, :]
        J_base = J_base_translated[:2, :]

        data.Rx.fill(0.0)
        data.Rx[:, :self.state.nv] = J_torso - J_base  # dq part
        # dv part remains zero; Ru already zero.

    def createData(self, data):
        return ResidualDataRelativeXY(self, data)


class ResidualDataRelativeXY(crocoddyl.ResidualDataAbstract):
    def __init__(self, model, data):
        super().__init__(model, data)
        # Keep a handle to pinocchio data from the action data collector.
        self.pinocchio = data.pinocchio


def main():
    print("=" * 70)
    print("Wbot Contact Frames Test".center(70))
    print("=" * 70)

    # 加载模型 - 使用 MuJoCo XML
    model = pin.buildModelFromMJCF(MJCF_PATH)
    nv = model.nv
    vel_offset = nv  # tangent 向量中速度部分的起始索引（dx = [dq, dv]）

    def get_joint_indices(jname):
        """返回 (q_idx, v_idx)，若不存在则 (None, None)"""
        if not model.existJointName(jname):
            return None, None   
        jid = model.getJointId(jname)
        j = model.joints[jid]
        return j.idx_q, j.idx_v

    # 常用关节索引缓存（注意 XML 中轮子关节名称是 left/right）
    joint_indices = {
        name: get_joint_indices(name)
        for name in [
            'left', 'right', 'caster_yaw', 'caster_rotate',
            'ankle', 'knee', 'hip', 'waist_roll', 'waist_yaw',
            'right_arm_pitch', 'left_arm_pitch'
        ]
    }

    print(f"\n原始模型:")
    print(f"  nq={model.nq}, nv={model.nv}")

    # 找到所有轮子（主动轮 + 万向轮）
    wheel_link_ids = []
    wheel_names = ['left wheel-u', 'right wheel-u']  # 主动轮（frame 名）
    caster_names = ['caster_rotate']   # 万向轮（只用前轮作为支撑点）

    for name in wheel_names:
        if model.existFrame(name):
            fid = model.getFrameId(name)
            print(f"  主动轮frame: {name} (id={fid})")
            wheel_link_ids.append(fid)

    # 为每个轮子添加接触frame（在轮底）
    wheel_radius = 0.095
    caster_radius = 0.048  # 万向轮半径（从URDF）
    contact_frame_ids = []
    contact_names = []

    # 主动轮位置（相对于 base_link，来自 URDF joint origin）
    wheel_positions = {
        'left wheel-u': np.array([0.0, 0.15224, 0.0]),   # 左轮 joint origin
        'right wheel-u': np.array([0.0, -0.15224, 0.0]),  # 右轮 joint origin
    }

    # 万向轮中心位置（相对于 base_link）= yaw joint + wheel joint
    caster_positions = {
        'caster_rear': np.array([-0.417, 0.0, -0.056]),  # (-0.385,-0.0012) + (-0.032,-0.0548)
    }

    # 统一计算接触点相对 base_link 的位置，并据此确定 base 需要抬升的高度
    contact_positions = {}
    for name, pos in wheel_positions.items():
        contact_positions[name] = pos + np.array([0.0, 0.0, -wheel_radius])
    for name, pos in caster_positions.items():
        contact_positions[name] = pos + np.array([0.0, 0.0, -caster_radius])

    # base 需要抬升的高度（保证所有接触点落在地面 z=0）
    base_height = 0.0935 #max(-cp[2] for cp in contact_positions.values())

    # 获取base_link frame (MuJoCo XML 使用 Base_link)
    base_frame_id = model.getFrameId('Base_link')
    base_joint_id = model.frames[base_frame_id].parentJoint

    for name in wheel_names:
        # 计算接触点位置（相对于base_link）
        # 轮心在 Z=0.095，轮底在 Z=0（当base_link在原点时）
        # 所以接触点相对于base_link: Z = 0 （不是0.095-0.095！）
        # 实际上，相对坐标：轮底 = 轮心Z - 半径 = 0.095 - 0.095 = 0
        # 但是！当base_link在Z=h时，接触点绝对位置应该是h+0，轮底应该在h-0.095
        # 所以相对位置应该是-0.095！
        wheel_center = wheel_positions[name]
        contact_pos = contact_positions[name]

        # 创建接触frame（相对于base_link）
        contact_placement = pin.SE3.Identity()
        contact_placement.translation = contact_pos

        contact_name = f"{name}_contact"
        contact_frame = pin.Frame(
            contact_name,
            base_joint_id,  # parent joint = base joint
            base_frame_id,  # parent frame = base_link
            contact_placement,
            pin.FrameType.OP_FRAME
        )

        contact_fid = model.addFrame(contact_frame)
        contact_frame_ids.append(contact_fid)
        contact_names.append(contact_name)
        print(f"  添加主动轮接触: {contact_name} (id={contact_fid})")

    # 添加万向轮支撑点
    for caster_name, caster_pos in caster_positions.items():
        contact_pos = contact_positions[caster_name]

        contact_placement = pin.SE3.Identity()
        contact_placement.translation = contact_pos

        contact_frame_name = f"{caster_name}_contact"
        contact_frame = pin.Frame(
            contact_frame_name,
            base_joint_id,
            base_frame_id,
            contact_placement,
            pin.FrameType.OP_FRAME
        )

        contact_fid = model.addFrame(contact_frame)
        contact_frame_ids.append(contact_fid)
        contact_names.append(contact_frame_name)
        print(f"  添加万向轮支撑: {contact_frame_name} (id={contact_fid})")

    # 添加frames后重新创建data
    data = model.createData()

    # 验证frames位置
    q0 = np.zeros(model.nq)
    q0[2] = base_height  # Base Z 抬升到轮底与地面对齐
    q0[3:7] = [0., 0., 0., 1.]  # quaternion

    pin.forwardKinematics(model, data, q0)
    pin.updateFramePlacements(model, data)

    print(f"\n当 base Z={base_height:.3f}m 时（轮底接地）:")
    # 验证主动轮
    for wfid, cfid, name in zip(wheel_link_ids, contact_frame_ids[:len(wheel_link_ids)], wheel_names):
        wheel_pos = data.oMf[wfid].translation
        contact_pos = data.oMf[cfid].translation
        print(f"  主动轮 {name}:")
        print(f"    轮心Z: {wheel_pos[2]:.4f} m (应该≈0.095)")
        print(f"    接触点Z: {contact_pos[2]:.4f} m (应该≈0)")

    # 验证万向轮支撑点
    for cfid, contact_name in zip(contact_frame_ids[len(wheel_link_ids):], contact_names[len(wheel_link_ids):]):
        contact_pos = data.oMf[cfid].translation
        print(f"  {contact_name}:")
        print(f"    接触点Z: {contact_pos[2]:.4f} m (应该≈0)")

    # === 创建OCP测试 ===
    state = crocoddyl.StateMultibody(model)
    # 使用 ActuationModelFull：只允许控制真实关节（轮子等），基座被动响应
    # nu = nv - 6 (去掉浮动基座的6个控制输入)
    actuation = crocoddyl.ActuationModelFull(state)
    nu = actuation.nu
    print(f"\n驱动模型:")
    print(f"  - 类型: ActuationModelFull (只能通过轮子驱动)")
    print(f"  - 控制输入维度 nu: {nu} (nv={model.nv}, 不包括基座的6个自由度)")
    print(f"  - 基座运动: 被动响应轮子驱动")

    # 目标关节角度（只设置 knee，ankle 和 hip 通过躯干高度约束隐式确定）
    target_joint_angles = {
        # 下肢 - 只设置 knee 角度
        # 'ankle': -0.562,    # 移除：通过躯干高度约束隐式确定
        'knee':  -1.2,        # 保留：膝盖弯曲角度
        # 'hip':   -0.646,    # 移除：通过躯干高度约束隐式确定
        # 腰部 - 固定为0
        'waist_roll': 0.0,
        'waist_yaw': 0.0,
        # 手臂 - 完全固定为0
        'right_arm_pitch': 0.0,
        'left_arm_pitch': 0.0,
    }

    # 目标运动速度
    target_vx = 1.0       # 目标前进速度 (m/s)
    target_omega_z = 0.0  # 目标转向角速度 (rad/s) - 0表示直线前进

    # 初始状态：抬升到轮底接地的高度
    x0 = state.zero()
    x0[2] = base_height  # 恢复：使用 base_height 让轮底刚好接地
    x0[3:7] = [0., 0., 0., 1.]

    # 初始关节角度保持为0（不设置），只在x_ref中设置目标角度
    # 这样机器人会从全0姿态平滑过渡到目标姿态

    # Contact模型 - 使用Contact1D（只约束Z，允许XY滚动）
    contactModel = crocoddyl.ContactModelMultiple(state, nu)

    # 为所有接触点（主动轮 + 万向轮）添加接触约束
    for cfid, contact_name in zip(contact_frame_ids, contact_names):
        # Contact1D: 只约束Z方向，允许X,Y方向自由滚动
        R_contact = np.eye(3)  # 单位矩阵，Z列 = [0,0,1]
        gains = np.array([0.0, 50.0])  # Baumgarte gains

        supportContactModel = crocoddyl.ContactModel1D(
            state,
            cfid,
            0.0,  # Z参考位置 = 0（地面）
            pin.LOCAL_WORLD_ALIGNED,
            R_contact,
            nu,
            gains
        )
        contactModel.addContact(contact_name, supportContactModel)
        print(f"  添加接触约束: {contact_name}")

    # Cost模型
    costModel = crocoddyl.CostModelSum(state, nu)

    # ============================================================
    # 差速驱动参数设置
    # ============================================================
    # 机器人几何参数
    wheel_radius = 0.0935  # 轮子半径 (m)
    wheel_base = 0.42     # 轮间距 (m) - 两个主动轮中心之间的距离



    # 根据差速驱动模型计算左右轮目标角速度
    # 公式：ω_left = (vx - ωz * L/2) / r
    #       ω_right = (vx + ωz * L/2) / r
    target_wheel_vel_left = (target_vx - target_omega_z * wheel_base / 2) / wheel_radius
    target_wheel_vel_right = (target_vx + target_omega_z * wheel_base / 2) / wheel_radius

    print(f"\n差速驱动设置:")
    print(f"  轮子半径: {wheel_radius} m")
    print(f"  轮间距: {wheel_base} m")
    print(f"  目标前进速度 vx: {target_vx} m/s")
    print(f"  目标转向角速度 ωz: {target_omega_z} rad/s ({np.degrees(target_omega_z):.1f}°/s)")
    print(f"  左轮目标角速度: {target_wheel_vel_left:.3f} rad/s")
    print(f"  右轮目标角速度: {target_wheel_vel_right:.3f} rad/s")

    x_ref = state.zero()
    x_ref[2] = base_height  # Base应该在0m（轮底接地）
    x_ref[3:7] = [0., 0., 0., 1.]

    # 设置下肢关节目标角度
    print(f"\n设置关节目标角度:")
    for joint_name, target_angle in target_joint_angles.items():
        if model.existJointName(joint_name):
            joint_id = model.getJointId(joint_name)
            joint_q_idx = model.joints[joint_id].idx_q
            x_ref[joint_q_idx] = target_angle
            print(f"  ✓ {joint_name}: {target_angle:.3f} rad ({np.degrees(target_angle):.1f}°)")
        else:
            print(f"  ✗ {joint_name}: 关节不存在！")

    # 设置左右轮目标角速度（根据 left / right 的 v_idx）
    left_wheel_v_idx = joint_indices['left'][1]
    right_wheel_v_idx = joint_indices['right'][1]
    if left_wheel_v_idx is not None:
        x_ref[state.nq + left_wheel_v_idx] = target_wheel_vel_left
    if right_wheel_v_idx is not None:
        x_ref[state.nq + right_wheel_v_idx] = target_wheel_vel_right

    # ====================================================================
    # ⭐ 统一权重配置区域
    # ====================================================================

    # 关节分组
    # 注意：ankle 和 hip 不再有位置目标，通过躯干高度约束隐式确定
    body_joints_with_targets = ['knee', 'waist_roll', 'waist_yaw']  # 有明确角度目标的关节
    body_joints_free = ['ankle', 'hip']  # 自由优化的关节（无位置目标）
    body_joints_all = body_joints_with_targets + body_joints_free  # 所有躯体关节（用于速度约束）
    arm_joints = ['right_arm_pitch', 'left_arm_pitch']

    # --- 位置权重（关节角度跟踪）---
    body_pos_weight = 500.0         # 躯体关节（knee/waist）位置跟踪权重
    free_joint_pos_weight = 0.0     # 自由关节（ankle/hip）不跟踪位置
    arm_pos_weight = 1000.0         # 手臂关节（完全固定）

    # --- 速度权重（软约束）---
    body_vel_weight = 300.0         # 躯体关节速度权重
    arm_vel_weight = 5000.0         # 手臂速度权重（极高，完全固定）
    wheel_vel_weight = 100.0        # 轮子速度权重

    # --- 速度硬限制（BoxFDDP约束）---
    body_v_limit = 1.0              # 躯体关节速度限制 (rad/s)
    arm_v_limit = 1.0               # 手臂速度限制 (rad/s)

    # --- 躯干位置约束（Body Relative Constraint）---
    # 约束躯干 XY 位置保持在 base 正上方，Z 轴自由允许下蹲
    torso_xy_weight = 100.0        # 躯干 XY 位置跟踪权重（保持在 base 上方）
    torso_pitch_weight = 500.0      # 躯干 pitch 抑制（绕Y轴旋转），roll/yaw 不限制

    # --- 代价函数权重 ---
    stateReg_weight = 3e-1          # 状态跟踪权重
    ctrl_reg_weight = 1e-1          # 控制正则化权重（限制力矩）

    # --- 力矩限制（BoxFDDP约束）---
    u_max = 60.0                    # 最大力矩 (Nm)

    # --- 优化时域参数 ---
    DT = 0.01                       # 时间步长 (s)
    T_HORIZON = 500                 # 时域步数

    # ====================================================================

    # 权重设置（tangent space维度 = state.ndx = 2*nv）
    # 位置tangent [0:nv]: base(6) + joints
    # 速度 [nv:2*nv]: base_vel(6) + joint_vel

    stateWeights = [0.0] * state.ndx

    # 位置tangent部分 [0:nv]
    stateWeights[0:3] = [0.0, 0.0, 0.0]  # base xyz：Z高度约束
    stateWeights[3:6] = [0.0, 0.0, 0.0]  # base姿态：加大约束，防止后仰/侧翻

    # 为目标关节设置高权重（按组分类）
    for joint_name in target_joint_angles.keys():
        if model.existJointName(joint_name):
            joint_id = model.getJointId(joint_name)
            joint_v_idx = model.joints[joint_id].idx_v  # tangent space 用 v 索引

            # 根据关节组设置不同的位置权重
            if joint_name in body_joints_with_targets:
                stateWeights[joint_v_idx] = body_pos_weight
            elif joint_name in arm_joints:
                stateWeights[joint_v_idx] = arm_pos_weight
            else:
                stateWeights[joint_v_idx] = 1000.0  # 其他关节：默认权重

    # 为自由关节设置低权重（ankle 和 hip 不跟踪位置，通过躯干高度约束确定）
    for joint_name in body_joints_free:
        if model.existJointName(joint_name):
            joint_id = model.getJointId(joint_name)
            joint_v_idx = model.joints[joint_id].idx_v
            stateWeights[joint_v_idx] = free_joint_pos_weight  # 0.0，不跟踪位置

    # 轮子角度自由（允许滚动）
    if left_wheel_v_idx is not None:
        stateWeights[left_wheel_v_idx] = 0.0
    if right_wheel_v_idx is not None:
        stateWeights[right_wheel_v_idx] = 0.0

    # --- 躯体关节速度权重（包括所有躯体关节）---
    for body_joint in body_joints_all:
        if model.existJointName(body_joint):
            body_v_idx = model.joints[model.getJointId(body_joint)].idx_v
            stateWeights[vel_offset + body_v_idx] = body_vel_weight

    # --- 手臂关节速度权重 ---
    for arm_joint in arm_joints:
        if model.existJointName(arm_joint):
            arm_v_idx = model.joints[model.getJointId(arm_joint)].idx_v
            stateWeights[vel_offset + arm_v_idx] = arm_vel_weight

    # --- 轮子速度权重 ---
    if left_wheel_v_idx is not None:
        stateWeights[vel_offset + left_wheel_v_idx] = wheel_vel_weight
    if right_wheel_v_idx is not None:
        stateWeights[vel_offset + right_wheel_v_idx] = wheel_vel_weight

    # --- 其他关节默认权重 ---
    # 对于未明确设置的关节，使用默认低权重（保留 base xyz 为0）
    for i in range(state.ndx):
        if stateWeights[i] == 0.0 and i not in (0, 1, 2):
            stateWeights[i] = 10.0  # 默认低权重

    stateWeights = np.array(stateWeights)

    stateResidual = crocoddyl.ResidualModelState(state, x_ref, nu)
    stateActivation = crocoddyl.ActivationModelWeightedQuad(stateWeights**2)
    stateReg = crocoddyl.CostModelResidual(state, stateActivation, stateResidual)
    costModel.addCost("stateReg", stateReg, stateReg_weight)

    # ============================================================
    # 躯干位置约束（Body Relative Constraint）
    # ============================================================
    # 约束 waist yaw 链接相对于 base 的 XY 位置（保持在 base 正上方）
    # Z 轴自由，允许下蹲（通过 knee 角度控制）

    torso_frame_name = 'waist yaw-u'  # 躯干链接名称
    if model.existFrame(torso_frame_name):
        torso_frame_id = model.getFrameId(torso_frame_name)

        # 相对 XY 残差：torso_xy - ankle_xy（ankle 相对 Base_link 有固定偏移）
        torso_xy_residual = ResidualModelRelativeXY(
            state, torso_frame_id, base_frame_id, nu
        )

        # 只约束 XY，Z 自由
        torso_translation_weights = np.array([torso_xy_weight, torso_xy_weight])
        torsoTranslationActivation = crocoddyl.ActivationModelWeightedQuad(torso_translation_weights**2)

        torsoTranslationCost = crocoddyl.CostModelResidual(
            state, torsoTranslationActivation, torso_xy_residual
        )
        costModel.addCost("torsoXY", torsoTranslationCost, 1.0)

        print(f"\n躯干位置约束 (Body Relative):")
        print(f"  - Frame: {torso_frame_name} (id={torso_frame_id})")
        print(f"  - XY约束: 相对于 ankle 位置（Base_link 偏移 [-0.2, -0.0453, 0.0275]），保持对齐（权重={torso_xy_weight}）")
        print(f"  - Z轴: 自由（允许下蹲，通过 knee 角度控制）")
    else:
        print(f"\n⚠️  警告: 未找到躯干frame '{torso_frame_name}'")

    # ============================================================
    # 躯干姿态约束：抑制绕Y轴的旋转（pitch），roll/yaw 自由
    # ============================================================
    if model.existFrame(torso_frame_name):
        # 目标姿态：世界系对齐（即 pitch=0）。只在激活里给 pitch 轴权重。
        torso_orientation_residual = crocoddyl.ResidualModelFrameRotation(
            state, torso_frame_id, pin.SE3.Identity().rotation, nu
        )
        # 小角度下，ResidualFrameOrientation 的向量元素对应 x,y,z 轴的旋转分量
        orientation_weights = np.array([0.0, torso_pitch_weight, 0.0])
        torsoOrientationActivation = crocoddyl.ActivationModelWeightedQuad(orientation_weights**2)
        torsoOrientationCost = crocoddyl.CostModelResidual(
            state, torsoOrientationActivation, torso_orientation_residual
        )
        costModel.addCost("torsoPitch", torsoOrientationCost, 1.0)
        print(f"\n躯干姿态约束:")
        print(f"  - 抑制 pitch (绕Y轴) 旋转，权重={torso_pitch_weight}；roll/yaw 自由")

    # Friction cones - 移除（Contact1D不支持）
    # Contact1D只约束Z方向，不需要friction cone约束

    # Control regularization - 增加权重以限制大力矩（间接限制加速度）
    ctrlResidual = crocoddyl.ResidualModelControl(state, nu)
    ctrlReg = crocoddyl.CostModelResidual(state, ctrlResidual)
    costModel.addCost("ctrlReg", ctrlReg, ctrl_reg_weight)

    # Differential action model
    dmodel = crocoddyl.DifferentialActionModelContactFwdDynamics(
        state, actuation, contactModel, costModel, 0.0, True
    )

    # Add control (torque) bounds
    dmodel.u_lb = np.full(nu, -u_max)
    dmodel.u_ub = np.full(nu, u_max)
    print(f"\n力矩限制: ±{u_max} Nm")

    # Integrated action model
    model_running = crocoddyl.IntegratedActionModelEuler(dmodel, DT)
    model_terminal = crocoddyl.IntegratedActionModelEuler(dmodel, 0.0)

    # ============================================================
    # 状态硬约束：关节速度限制（状态向量：x = [q(nq), v(nv)]）
    # 速度部分从索引 nq 开始
    # ============================================================

    # Initialize with no bounds (全部初始为无限制)
    x_lb = np.full(state.nx, -np.inf)
    x_ub = np.full(state.nx, np.inf)

    # --- 躯体关节速度硬限制（包括所有躯体关节）---
    for body_joint in body_joints_all:
        if model.existJointName(body_joint):
            body_v_idx = model.joints[model.getJointId(body_joint)].idx_v
            x_lb[state.nq + body_v_idx] = -body_v_limit
            x_ub[state.nq + body_v_idx] = body_v_limit

    # --- 手臂关节速度硬限制 ---
    for arm_joint in arm_joints:
        if model.existJointName(arm_joint):
            arm_v_idx = model.joints[model.getJointId(arm_joint)].idx_v
            x_lb[state.nq + arm_v_idx] = -arm_v_limit
            x_ub[state.nq + arm_v_idx] = arm_v_limit

    # --- 轮子速度：无硬限制（允许自由滚动）---
    # jt-left wheel: 左轮
    # jt-right wheel: 右轮
    # 保持 [-inf, +inf]，不设置限制

    model_running.x_lb = x_lb
    model_running.x_ub = x_ub

    # 打印速度限制摘要
    print(f"\n关节速度硬限制:")
    print(f"  - 躯体关节 (ankle/knee/hip/waist): ±{body_v_limit} rad/s")
    print(f"  - 手臂关节: ±{arm_v_limit} rad/s")
    print(f"  - 轮子 (jt-left/right wheel): 无限制 (自由滚动)")

    # 创建关节速度限制字典（用于初始化轨迹猜测）
    joint_velocity_limits = {}
    for body_joint in body_joints_all:
        if model.existJointName(body_joint):
            joint_velocity_limits[body_joint] = body_v_limit
    for arm_joint in arm_joints:
        if model.existJointName(arm_joint):
            joint_velocity_limits[arm_joint] = arm_v_limit

    # Shooting problem
    running_models = [model_running] * T_HORIZON
    problem = crocoddyl.ShootingProblem(x0, running_models, model_terminal)

    # Solver - use BoxFDDP to enforce control bounds
    solver = crocoddyl.SolverBoxFDDP(problem)
    solver.setCallbacks([crocoddyl.CallbackVerbose()])

    print(f"\n开始求解...")

    # 初始化轨迹猜测（使用x_ref作为初始猜测）
    xs_init = [x_ref] * (T_HORIZON + 1)
    us_init = [np.zeros(nu)] * T_HORIZON

    import time
    start_time = time.time()
    solver.solve(xs_init, us_init, 100)
    solve_time = time.time() - start_time

    print(f"\n求解完成!")
    print(f"  迭代: {solver.iter}")
    print(f"  代价: {solver.cost:.4f}")
    print(f"  计算时间: {solve_time:.3f} 秒")
    print(f"  平均每次迭代: {solve_time/solver.iter*1000:.2f} ms")

    # 分析结果
    xs = np.array(solver.xs)
    x_positions = xs[:, 0]
    z_positions = xs[:, 2]
    vx_velocities = xs[:, state.nq + 0]
    vz_velocities = xs[:, state.nq + 2]
    omega_z_velocities = xs[:, state.nq + 5]  # base角速度 ωz
    left_wheel_angles = None
    right_wheel_angles = None
    if joint_indices['left'][0] is not None:
        left_wheel_angles = xs[:, joint_indices['left'][0]]
    if joint_indices['right'][0] is not None:
        right_wheel_angles = xs[:, joint_indices['right'][0]]
    left_wheel_vels = xs[:, state.nq + left_wheel_v_idx] if left_wheel_v_idx is not None else None
    right_wheel_vels = xs[:, state.nq + right_wheel_v_idx] if right_wheel_v_idx is not None else None

    print(f"\n结果分析:")
    print(f"  base X位移: {x_positions[-1] - x_positions[0]:.3f} m")
    print(f"  平均速度: {(x_positions[-1] - x_positions[0]) / (T_HORIZON * DT):.3f} m/s")
    print(f"  最终vx: {vx_velocities[-1]:.3f} m/s (目标: {target_vx} m/s)")
    print(f"  最终ωz: {omega_z_velocities[-1]:.4f} rad/s ({np.degrees(omega_z_velocities[-1]):.2f}°/s) (目标: {target_omega_z} rad/s)")
    print(f"  base Z: {z_positions[-1]:.4f} m (应该≈0)")
    print(f"  最终vz: {vz_velocities[-1]:.4f} m/s")

    # 差速驱动验证
    print(f"\n差速驱动验证:")
    if left_wheel_vels is not None and right_wheel_vels is not None:
        print(f"  左轮最终角速度: {left_wheel_vels[-1]:.3f} rad/s (目标: {target_wheel_vel_left:.3f} rad/s)")
        print(f"  右轮最终角速度: {right_wheel_vels[-1]:.3f} rad/s (目标: {target_wheel_vel_right:.3f} rad/s)")
        # 根据轮速反推实际的 vx 和 ωz
        actual_vx_from_wheels = (left_wheel_vels[-1] + right_wheel_vels[-1]) * wheel_radius / 2
        actual_omega_z_from_wheels = (right_wheel_vels[-1] - left_wheel_vels[-1]) * wheel_radius / wheel_base
        print(f"  轮速反推vx: {actual_vx_from_wheels:.3f} m/s (base实际: {vx_velocities[-1]:.3f} m/s)")
        print(f"  轮速反推ωz: {actual_omega_z_from_wheels:.4f} rad/s (base实际: {omega_z_velocities[-1]:.4f} rad/s)")

    # 轮子转动分析
    if left_wheel_angles is not None and right_wheel_angles is not None:
        left_rotation = left_wheel_angles[-1] - left_wheel_angles[0]
        right_rotation = right_wheel_angles[-1] - right_wheel_angles[0]
        expected_rotation = (x_positions[-1] - x_positions[0]) / wheel_radius

    # 提取关键关节数据
    def get_joint_data(joint_name):
        if model.existJointName(joint_name):
            joint_id = model.getJointId(joint_name)
            q_idx = model.joints[joint_id].idx_q
            v_idx = model.joints[joint_id].idx_v
            positions = xs[:, q_idx]
            return {
                'initial': positions[0],
                'final': positions[-1],
                'target': target_joint_angles.get(joint_name, 0.0)
            }
        return None

    # 打印简洁结果
    print(f"\n" + "="*70)
    print(f"{'关节/轮速':<20} {'目标 (rad)':<15} {'初始 (rad)':<15} {'最终 (rad)':<15}")
    print("-"*70)

    # 轮速（差速驱动）
    if left_wheel_vels is not None and right_wheel_vels is not None:
        print(f"{'左轮速度':<20} {target_wheel_vel_left:>14.3f} {left_wheel_vels[0]:>14.3f} {left_wheel_vels[-1]:>14.3f}")
        print(f"{'右轮速度':<20} {target_wheel_vel_right:>14.3f} {right_wheel_vels[0]:>14.3f} {right_wheel_vels[-1]:>14.3f}")

    # 下肢关节
    for jname in ['ankle', 'knee', 'hip']:
        jdata = get_joint_data(jname)
        if jdata:
            print(f"{jname:<20} {jdata['target']:>14.4f} {jdata['initial']:>14.4f} {jdata['final']:>14.4f}")

    # 腰部关节
    for jname in ['waistroll', 'waistyaw']:
        jdata = get_joint_data(jname)
        if jdata:
            target = get_joint_data(jname) 
            print(f"{jname:<20} {jdata['target']:>14.4f} {jdata['initial']:>14.4f} {jdata['final']:>14.4f}")

    print("="*70)

    # 提取关节轨迹数据（用于保存）
    joint_names = ['ankle', 'knee', 'hip', 'waist_roll', 'waist_yaw']
    joint_data = {}

    for joint_name in joint_names:
        if model.existJointName(joint_name):
            joint_id = model.getJointId(joint_name)
            joint_q_idx = model.joints[joint_id].idx_q
            joint_v_idx = model.joints[joint_id].idx_v
            joint_positions = xs[:, joint_q_idx]
            joint_velocities = xs[:, state.nq + joint_v_idx]
            joint_data[f'{joint_name}_position'] = joint_positions
            joint_data[f'{joint_name}_velocity'] = joint_velocities

    # 保存轨迹到当前目录
    us = np.array(solver.us)
    save_path = os.path.join(SCRIPT_DIR, 'wbot_trajectory.npz')
    np.savez(save_path, xs=xs, us=us, dt=DT, **joint_data)
    print(f"\n✓ 轨迹已保存: {save_path}")
    print(f"  总时长: {len(xs)*DT:.1f}s")
    print(f"  包含关节数据: {', '.join(joint_names)}")

    # 生成详细的关节数据日志
    log_joints = ['ankle', 'knee', 'hip', 'waist_roll', 'waist_yaw']
    log_path = os.path.join(SCRIPT_DIR, 'joint_log.csv')

    with open(log_path, 'w') as f:
        # 写入CSV表头
        header = ['time(s)']
        # 添加轮速列
        header.extend([
            'left_wheel_vel(rad/s)',
            'right_wheel_vel(rad/s)',
            'base_vx(m/s)',
            'base_omega_z(rad/s)'
        ])
        # 添加关节列
        for jname in log_joints:
            header.extend([
                f'{jname}_pos(rad)',
                f'{jname}_pos(deg)',
                f'{jname}_vel(rad/s)',
                f'{jname}_acc(rad/s²)',
                f'{jname}_torque(Nm)'
            ])
        f.write(','.join(header) + '\n')

        # 提取每个关节的数据
        joint_info = {}
        for jname in log_joints:
            if model.existJointName(jname):
                joint_id = model.getJointId(jname)
                q_idx = model.joints[joint_id].idx_q
                v_idx = model.joints[joint_id].idx_v
                # v_idx in actuation space (exclude floating base 6 DOF)
                u_idx = v_idx - 6 if v_idx >= 6 else None

                positions = xs[:, q_idx]
                velocities = xs[:, state.nq + v_idx]

                # 计算加速度（数值微分）
                accelerations = np.zeros(len(velocities))
                accelerations[:-1] = (velocities[1:] - velocities[:-1]) / DT
                accelerations[-1] = accelerations[-2]  # 最后一个点用前一个值

                # 提取力矩
                torques = np.zeros(len(positions))
                if u_idx is not None and u_idx >= 0 and u_idx < nu:
                    torques[:-1] = us[:, u_idx]
                    torques[-1] = 0.0  # 最后一个时刻没有控制

                joint_info[jname] = {
                    'pos': positions,
                    'vel': velocities,
                    'acc': accelerations,
                    'torque': torques
                }

        # 写入数据
        for t in range(len(xs)):
            time = t * DT
            row = [f'{time:.4f}']

            # 添加轮速和base速度数据
            row.extend([
                f'{left_wheel_vels[t]:.6f}',      # 左轮速度
                f'{right_wheel_vels[t]:.6f}',     # 右轮速度
                f'{vx_velocities[t]:.6f}',        # base vx
                f'{omega_z_velocities[t]:.6f}'    # base ωz
            ])

            # 添加关节数据
            for jname in log_joints:
                if jname in joint_info:
                    info = joint_info[jname]
                    row.extend([
                        f'{info["pos"][t]:.6f}',         # 位置(rad)
                        f'{np.rad2deg(info["pos"][t]):.3f}',  # 位置(deg)
                        f'{info["vel"][t]:.6f}',         # 速度
                        f'{info["acc"][t]:.6f}',         # 加速度
                        f'{info["torque"][t]:.6f}'       # 力矩
                    ])
                else:
                    row.extend(['0.0'] * 5)

            f.write(','.join(row) + '\n')

    print(f"\n✓ 关节日志已保存: {log_path}")
    print(f"  包含: {', '.join(log_joints)}")
    print(f"  数据: 位置、速度、加速度、力矩")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
