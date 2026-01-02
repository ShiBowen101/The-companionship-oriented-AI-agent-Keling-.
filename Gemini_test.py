from ursina import *
import random
import time

# --- 初始化 Ursina 应用 ---
app = Ursina()

# --- 准备资源 ---
# 再次确认: 请将 car.obj 和 road.png 放在 C:\Users\27752\Desktop\AI项目 目录下
CAR_MODEL_FILE = 'car.obj'
ROAD_TEXTURE_FILE = 'road.png'

# --- 游戏参数 ---
car_speed = 10
turn_speed = 90
camera_follow_speed = 5
camera_rotation_speed = 4 # 控制摄像头旋转插值的速度

# --- 创建地面/赛道 ---
try:
    ground_texture = load_texture(ROAD_TEXTURE_FILE)
    print(f"成功加载纹理: {ROAD_TEXTURE_FILE}")
except Exception as e:
    print(f"警告: 无法加载纹理 {ROAD_TEXTURE_FILE}, 使用默认颜色: {e}")
    ground_texture = None

ground = Entity(
    model='plane',
    scale=(120, 1, 500),
    texture=ground_texture if ground_texture else None,
    color=color.dark_gray if not ground_texture else color.white,
    texture_scale=(30, 125),
    collider='box'
)

# --- 添加环境元素 ---
track_width = 12
for i in range(25):
    Entity( model='cube', position=(-track_width / 2, 0.2, i * 20), scale=(0.2, 0.4, 18), color=color.light_gray, collider='box')
    Entity( model='cube', position=( track_width / 2, 0.2, i * 20), scale=(0.2, 0.4, 18), color=color.light_gray, collider='box')
    if random.random() > 0.6:
        obstacle_model = random.choice(['cube', 'sphere'])
        obstacle_scale = random.uniform(1.5, 3)
        collider_type = 'box' if obstacle_model == 'cube' else 'sphere'
        Entity( model=obstacle_model, collider=collider_type,
                position=(random.uniform(-track_width/2 + 2, track_width/2 - 2), obstacle_scale / 2, i * 20 + random.uniform(5, 15)),
                scale=obstacle_scale, rotation_y=random.uniform(0, 360), color=color.orange.tint(random.uniform(-0.2, 0.2)))

# --- 创建玩家车辆 ---
# 再次强调：如果这里加载失败，即使打印成功，模型也可能不显示。务必检查文件路径！
try:
    car = Entity( model=CAR_MODEL_FILE, collider='box', position=(0, 0.1, -230), rotation_y=0, scale=1, origin_y = -0.1 )
    print(f"成功加载模型: {CAR_MODEL_FILE}")
    # car.color = color.clear # 若模型自带纹理/颜色
except Exception as e:
    print(f"警告: 无法加载模型 {CAR_MODEL_FILE}, 使用 Cube 代替: {e}")
    car = Entity( model='cube', color=color.red, collider='box', position=(0, 0.5, -230), rotation_y = 0, scale=(1.2, 0.8, 2.5))

# --- 添加光照 ---
DirectionalLight(direction=(-0.7, -0.9, 0.5), color=color.white.tint(0.8), shadows=False)
AmbientLight(color=color.gray.tint(0.4))

# --- 改进的第三人称摄像头 ---
camera.position = car.position + Vec3(0, 15, -25)
camera.rotation_x = 15 # 初始俯视角度

# --- 游戏主循环 ---
def update():
    global car_speed

    # -- 控制汽车移动 --
    move_direction = 0
    if held_keys['w'] or held_keys['up arrow']: move_direction = 1
    if held_keys['s'] or held_keys['down arrow']: move_direction = -0.6
    movement_distance = move_direction * car_speed * time.dt

    # --- 碰撞检测与处理 ---
    original_position = car.position
    car.position += car.forward * movement_distance

    # -- 控制汽车转向 --
    turn_direction = 0
    if held_keys['a'] or held_keys['left arrow']: turn_direction = -1
    if held_keys['d'] or held_keys['right arrow']: turn_direction = 1
    turn_amount = turn_direction * turn_speed * time.dt
    if move_direction == 0: turn_amount *= 0.2
    elif move_direction < 0: turn_amount *= -1
    car.rotation_y += turn_amount

    # --- 碰撞检测 (移动和旋转之后) ---
    hit_info = car.intersects()
    if hit_info.hit:
        if hit_info.entity != ground:
            car.position = original_position # 恢复位置

    # -- 改进的摄像头跟随 --
    cam_dist = 20 + abs(move_direction) * 5
    cam_height = 8 + abs(turn_amount) * 30
    target_cam_pos = car.position - car.forward * cam_dist + Vec3(0, cam_height, 0)
    camera.position = lerp(camera.position, target_cam_pos, time.dt * camera_follow_speed)

    # --- !!! 修改点在这里: 使用四元数进行 slerp !!! ---
    # 1. 获取当前的四元数旋转
    current_quat = camera.quaternion

    # 2. 计算目标朝向点
    look_at_point = car.position + Vec3(0, 1, 0) + car.forward * 5

    # 3. 计算看向目标点时的目标四元数 (临时改变朝向以获取目标四元数)
    #    注意：这里直接用 look_at 可能会导致瞬间跳变，更好的方式是计算目标四元数
    #    但为了简单起见，我们先获取 look_at 后的四元数，再插值回去
    original_parent = camera.parent # look_at 可能受父节点影响，暂时解除
    camera.parent = scene
    camera.look_at(look_at_point)
    target_quat = camera.quaternion
    camera.parent = original_parent # 恢复父节点（如果之前有）
    camera.quaternion = current_quat # 立即恢复当前旋转，避免跳变，插值将在下一步进行

    # 4. 使用 slerp 在当前四元数和目标四元数之间插值
    camera.quaternion = slerp(current_quat, target_quat, time.dt * camera_rotation_speed)
    # --- !!! 修改结束 !!! ---


    # -- 简单的边界检查 --
    if car.z > 250:
        car.position = Vec3(0, car.y, -245); car.rotation = Vec3(0,0,0)
    if car.z < -250:
        car.position = Vec3(0, car.y, -245); car.rotation = Vec3(0,0,0)

    # 按 ESC 退出游戏
    if held_keys['escape']:
        application.quit()


# --- 运行游戏 ---
# window.fullscreen = True
app.run()