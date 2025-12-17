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
    base_height = max(-cp[2] for cp in contact_positions.values())

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

    # 目标关节角度
    target_joint_angles = {
        # 下肢 - 设置指定角度（直立姿态）
        'ankle': -0.562,
        'knee': -1.2,
        'hip': -0.646,
        # 腰部 - 固定为0
        'waist_roll': 0.0,
        'waist_yaw': 0.0,  # 修正：改为0.0
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
    wheel_radius = 0.095  # 轮子半径 (m)
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

    # 设置目标速度（在x中速度从nq开始）
    x_ref[state.nq + 0] = target_vx     # base前进速度 vx (nv索引0)
    x_ref[state.nq + 5] = target_omega_z  # base转向角速度 ωz (nv索引5)

    # 设置左右轮目标角速度（根据 left / right 的 v_idx）
    left_wheel_v_idx = joint_indices['left'][1]
    right_wheel_v_idx = joint_indices['right'][1]
    if left_wheel_v_idx is not None:
        x_ref[state.nq + left_wheel_v_idx] = target_wheel_vel_left
    if right_wheel_v_idx is not None:
        x_ref[state.nq + right_wheel_v_idx] = target_wheel_vel_right

    # 权重设置（tangent space维度 = state.ndx = 2*nv）
    # 位置tangent [0:nv]: base(6) + joints
    # 速度 [nv:2*nv]: base_vel(6) + joint_vel

    stateWeights = [0.0] * state.ndx

    # 位置tangent部分 [0:nv]
    stateWeights[0:3] = [0.0, 0.0, 0.0]  # base xyz：Z高度约束
    stateWeights[3:6] = [200.0, 300.0, 200.0]  # base姿态：加大约束，防止后仰/侧翻

    # 为目标关节设置高权重（按组分类）
    leg_joints = ['ankle', 'knee', 'hip']
    waist_joints = ['waist_roll', 'waist_yaw']
    arm_joints = ['right_arm_pitch', 'left_arm_pitch']

    for joint_name in target_joint_angles.keys():
        if model.existJointName(joint_name):
            joint_id = model.getJointId(joint_name)
            joint_v_idx = model.joints[joint_id].idx_v  # tangent space 用 v 索引

            # 根据关节组设置不同的位置权重
            if joint_name in leg_joints:
                stateWeights[joint_v_idx] = 5000.0  # 腿部关节：高权重保持直立姿态
            elif joint_name in waist_joints:
                stateWeights[joint_v_idx] = 10000.0  # 腰部关节：极高权重（完全固定）
            elif joint_name in arm_joints:
                stateWeights[joint_v_idx] = 100000.0  # 手臂关节：超高权重（完全固定为0）
            else:
                stateWeights[joint_v_idx] = 1000.0  # 其他关节：默认权重

    # 轮子角度自由（允许滚动）
    if left_wheel_v_idx is not None:
        stateWeights[left_wheel_v_idx] = 0.0
    if right_wheel_v_idx is not None:
        stateWeights[right_wheel_v_idx] = 0.0

    # ============================================================
    # 速度权重设置（状态向量索引从29开始，对应nq后的速度部分）
    # ============================================================

    # --- Base 速度权重 ---
    stateWeights[vel_offset + 0:vel_offset + 3] = [3000.0, 1000.0, 10.0]  # base线速度 [vx, vy, vz]
                                                                            # vx: 前进速度（高权重优先）
                                                                            # vy: 侧向滑动（中等权重防侧滑）
                                                                            # vz: 垂直速度（低权重）
    stateWeights[vel_offset + 3:vel_offset + 6] = [10.0, 10.0, 3000.0]    # base角速度 [wx, wy, wz]
                                                                            # wx, wy: 俯仰/侧滚（低权重）
                                                                            # wz: 转向角速度（高权重，防止意外转向）

    # --- 腿部关节速度权重（按惯量分组调参）---
    # ankle (v_idx=7): 脚踝关节
    ankle_vel_weight = 1000.0
    if model.existJointName('ankle'):
        ankle_v_idx = model.joints[model.getJointId('ankle')].idx_v
        stateWeights[vel_offset + ankle_v_idx] = ankle_vel_weight

    # knee (v_idx=8): 膝关节
    knee_vel_weight = 1000.0
    if model.existJointName('knee'):
        knee_v_idx = model.joints[model.getJointId('knee')].idx_v
        stateWeights[vel_offset + knee_v_idx] = knee_vel_weight

    # hip (v_idx=9): 髋关节
    hip_vel_weight = 1000.0
    if model.existJointName('hip'):
        hip_v_idx = model.joints[model.getJointId('hip')].idx_v
        stateWeights[vel_offset + hip_v_idx] = hip_vel_weight

    # --- 腰部关节速度权重 ---
    # waistyaw (v_idx=10): 腰部侧倾
    waistyaw_vel_weight = 1500.0
    if model.existJointName('waist_yaw'):
        waistyaw_v_idx = model.joints[model.getJointId('waist_yaw')].idx_v
        stateWeights[vel_offset + waistyaw_v_idx] = waistyaw_vel_weight

    # waistroll (v_idx): 腰部扭转
    waistroll_vel_weight = 1500.0
    if model.existJointName('waist_roll'):
        waistroll_v_idx = model.joints[model.getJointId('waist_roll')].idx_v
        stateWeights[vel_offset + waistroll_v_idx] = waistroll_vel_weight

    # --- 手臂关节速度权重（如果有）---
    arm_vel_weight = 100000.0  # 极高权重，完全固定手臂不动
    for arm_joint in ['right_arm_pitch', 'left_arm_pitch']:
        if model.existJointName(arm_joint):
            arm_v_idx = model.joints[model.getJointId(arm_joint)].idx_v
            stateWeights[vel_offset + arm_v_idx] = arm_vel_weight

    # --- 轮子速度权重（v_idx=25,26）---
    # 轮子速度需要较强约束，但不是硬限制（允许自由滚动）
    wheel_vel_weight = 1000.0
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
    costModel.addCost("stateReg", stateReg, 1e-1)

    # Friction cones - 移除（Contact1D不支持）
    # Contact1D只约束Z方向，不需要friction cone约束

    # Control regularization - 增加权重以限制大力矩（间接限制加速度）
    ctrlResidual = crocoddyl.ResidualModelControl(state, nu)
    ctrlReg = crocoddyl.CostModelResidual(state, ctrlResidual)
    costModel.addCost("ctrlReg", ctrlReg, 1e-2)  # 从1e-3提高到1

    # 添加关节加速度惩罚（通过惩罚力矩变化率）
    # 注意：crocoddyl没有直接的加速度cost，但可以通过控制变化率间接实现
    # 这里我们增大控制正则化来限制力矩，从而限制加速度

    # Differential action model
    dmodel = crocoddyl.DifferentialActionModelContactFwdDynamics(
        state, actuation, contactModel, costModel, 0.0, True
    )

    # Add control (torque) bounds: -200 to +200 Nm
    u_max = 100.0  # Maximum torque in Nm
    dmodel.u_lb = np.full(nu, -u_max)
    dmodel.u_ub = np.full(nu, u_max)
    print(f"\n力矩限制: ±{u_max} Nm")

    # Integrated action model
    DT = 0.01
    T_HORIZON = 300  # 5秒静止
    model_running = crocoddyl.IntegratedActionModelEuler(dmodel, DT)
    model_terminal = crocoddyl.IntegratedActionModelEuler(dmodel, 0.0)

    # ============================================================
    # 状态硬约束：关节速度限制（状态向量：x = [q(nq), v(nv)]）
    # 速度部分从索引 nq 开始
    # ============================================================

    # Initialize with no bounds (全部初始为无限制)
    x_lb = np.full(state.nx, -np.inf)
    x_ub = np.full(state.nx, np.inf)

    # --- 腿部关节速度硬限制（按惯量分组调参）---
    # ankle (v_idx=7): 脚踝关节
    ankle_v_limit = 2.0  # rad/s
    if model.existJointName('ankle'):
        ankle_v_idx = model.joints[model.getJointId('ankle')].idx_v
        x_lb[state.nq + ankle_v_idx] = -ankle_v_limit
        x_ub[state.nq + ankle_v_idx] = ankle_v_limit

    # knee (v_idx=8): 膝关节
    knee_v_limit = 2.0  # rad/s
    if model.existJointName('knee'):
        knee_v_idx = model.joints[model.getJointId('knee')].idx_v
        x_lb[state.nq + knee_v_idx] = -knee_v_limit
        x_ub[state.nq + knee_v_idx] = knee_v_limit

    # hip (v_idx=9): 髋关节
    hip_v_limit = 2.0  # rad/s
    if model.existJointName('hip'):
        hip_v_idx = model.joints[model.getJointId('hip')].idx_v
        x_lb[state.nq + hip_v_idx] = -hip_v_limit
        x_ub[state.nq + hip_v_idx] = hip_v_limit

    # --- 腰部关节速度硬限制 ---
    # waistyaw (v_idx=10): 腰部侧倾
    waistyaw_v_limit = 2.0  # rad/s
    if model.existJointName('waist_yaw'):
        waistyaw_v_idx = model.joints[model.getJointId('waist_yaw')].idx_v
        x_lb[state.nq + waistyaw_v_idx] = -waistyaw_v_limit
        x_ub[state.nq + waistyaw_v_idx] = waistyaw_v_limit

    # waistroll (v_idx=11): 腰部扭转
    waistroll_v_limit = 2.0  # rad/s
    if model.existJointName('waist_roll'):
        waistroll_v_idx = model.joints[model.getJointId('waist_roll')].idx_v
        x_lb[state.nq + waistroll_v_idx] = -waistroll_v_limit
        x_ub[state.nq + waistroll_v_idx] = waistroll_v_limit

    # --- 手臂关节速度硬限制（如果有）---
    arm_v_limit = 0.001  # rad/s - 几乎为0，完全固定手臂
    for arm_joint in ['right_arm_pitch', 'left_arm_pitch']:
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
    print(f"  - 腿部关节 (ankle/knee/hip): ±{ankle_v_limit} rad/s")
    print(f"  - 腰部关节 (waistyaw/roll): ±{waistyaw_v_limit} rad/s")
    print(f"  - 手臂关节: ±{arm_v_limit} rad/s")
    print(f"  - 轮子 (jt-left/right wheel): 无限制 (自由滚动)")

    # 创建关节速度限制字典（用于初始化轨迹猜测）
    joint_velocity_limits = {}
    if model.existJointName('ankle'):
        joint_velocity_limits['ankle'] = ankle_v_limit
    if model.existJointName('knee'):
        joint_velocity_limits['knee'] = knee_v_limit
    if model.existJointName('hip'):
        joint_velocity_limits['hip'] = hip_v_limit
    if model.existJointName('waist_yaw'):
        joint_velocity_limits['waist_yaw'] = waistyaw_v_limit
    if model.existJointName('waist_roll'):
        joint_velocity_limits['waist_roll'] = waistroll_v_limit
    for arm_joint in ['right_arm_pitch', 'left_arm_pitch']:
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
