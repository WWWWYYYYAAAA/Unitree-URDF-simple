import numpy as np
from stl import mesh
import math

def create_cylinder_stl(filename, radius=0.5, height=1.0, num_segments=16):
    """
    创建一个Z轴方向的圆柱体STL文件
    
    参数:
    - filename: 输出STL文件名
    - radius: 圆柱半径
    - height: 圆柱高度
    - num_segments: 圆周分段数，控制圆柱的平滑度
    """
    
    # 确保分段数至少为3
    num_segments = max(3, num_segments)
    
    # 1. 创建顶点数组
    vertices = []
    
    # 底面圆心顶点 (索引0)
    vertices.append([0.0, 0.0, -height/2])
    
    # 顶面圆心顶点 (索引1)
    vertices.append([0.0, 0.0, height/2])
    
    # 底面圆周顶点
    for i in range(num_segments):
        angle = 2 * math.pi * i / num_segments
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        z = -height/2
        vertices.append([x, y, z])
    
    # 顶面圆周顶点
    for i in range(num_segments):
        angle = 2 * math.pi * i / num_segments
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        z = height/2
        vertices.append([x, y, z])
    
    vertices = np.array(vertices)
    
    # 2. 创建面（三角形）数组
    faces = []
    
    # 底面三角形 - 修正法向量方向
    # 底面法向量应该向下（-Z方向），从外部看底面时，三角形顶点顺序为逆时针
    for i in range(num_segments):
        next_i = (i + 1) % num_segments
        # 修改顶点顺序：底面圆心 -> 下一个点 -> 当前点
        # 这样从外部（下方）看时，顶点顺序为逆时针
        faces.append([0, 2 + next_i, 2 + i])
    
    # 顶面三角形 - 修正法向量方向
    # 顶面法向量应该向上（+Z方向），从外部看顶面时，三角形顶点顺序为逆时针
    for i in range(num_segments):
        next_i = (i + 1) % num_segments
        # 修改顶点顺序：顶面圆心 -> 当前点 -> 下一个点
        # 这样从外部（上方）看时，顶点顺序为逆时针
        faces.append([1, 2 + num_segments + i, 2 + num_segments + next_i])
    
    # 侧面三角形
    for i in range(num_segments):
        next_i = (i + 1) % num_segments
        
        # 底面当前点索引
        bottom_current = 2 + i
        bottom_next = 2 + next_i
        
        # 顶面对应点索引
        top_current = 2 + num_segments + i
        top_next = 2 + num_segments + next_i
        
        # 第一个侧面三角形 - 保持原来的法向量方向
        # 从外部看，三个顶点顺序为逆时针
        faces.append([bottom_current, bottom_next, top_next])
        
        # 第二个侧面三角形 - 保持原来的法向量方向
        # 从外部看，三个顶点顺序为逆时针
        faces.append([bottom_current, top_next, top_current])
    
    faces = np.array(faces)
    
    # 3. 计算法向量并验证
    print("验证法向量方向:")
    for i, face in enumerate(faces[:4]):  # 只打印前几个面验证
        v0 = vertices[face[0]]
        v1 = vertices[face[1]]
        v2 = vertices[face[2]]
        
        # 计算法向量
        u = np.array(v1) - np.array(v0)
        v = np.array(v2) - np.array(v0)
        normal = np.cross(u, v)
        normal = normal / np.linalg.norm(normal)  # 单位化
        
        # 判断是哪个面
        if i < num_segments:
            print(f"  底面三角形 {i}: 法向量 = [{normal[0]:.2f}, {normal[1]:.2f}, {normal[2]:.2f}] (应该指向 -Z)")
        elif i < 2 * num_segments:
            print(f"  顶面三角形 {i-num_segments}: 法向量 = [{normal[0]:.2f}, {normal[1]:.2f}, {normal[2]:.2f}] (应该指向 +Z)")
    
    # 4. 创建并保存网格
    cylinder_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    
    for i, f in enumerate(faces):
        for j in range(3):
            cylinder_mesh.vectors[i][j] = vertices[f[j], :]
    
    # 5. 保存到STL文件
    cylinder_mesh.save(filename)
    
    # 6. 输出信息
    print(f"\n圆柱体STL文件已保存: {filename}")
    print(f"参数: 半径={radius}, 高度={height}, 分段数={num_segments}")
    print(f"顶点数: {len(vertices)}, 面数: {len(faces)}")
    
    return vertices, faces

def create_sphere_stl(filename, radius=0.5, num_segments_vertical=16, num_segments_horizontal=16):
    """
    创建一个球体STL文件
    
    参数:
    - filename: 输出STL文件名
    - radius: 球体半径
    - num_segments_vertical: 垂直方向分段数
    - num_segments_horizontal: 水平方向分段数
    """
    
    # 确保分段数至少为3
    num_segments_vertical = max(3, num_segments_vertical)
    num_segments_horizontal = max(3, num_segments_horizontal)
    
    # 1. 创建顶点数组
    vertices = []
    
    # 添加北极点 (索引0)
    vertices.append([0.0, 0.0, radius])
    
    # 添加中间纬度顶点
    for i in range(1, num_segments_vertical):
        theta = math.pi * i / num_segments_vertical  # 极角，从0到π
        z = radius * math.cos(theta)
        circle_radius = radius * math.sin(theta)
        
        for j in range(num_segments_horizontal):
            phi = 2 * math.pi * j / num_segments_horizontal  # 方位角，从0到2π
            x = circle_radius * math.cos(phi)
            y = circle_radius * math.sin(phi)
            vertices.append([x, y, z])
    
    # 添加南极点 (索引 len(vertices))
    vertices.append([0.0, 0.0, -radius])
    
    vertices = np.array(vertices)
    
    # 2. 创建面（三角形）数组
    faces = []
    
    # 北极点附近的三角形
    for j in range(num_segments_horizontal):
        next_j = (j + 1) % num_segments_horizontal
        
        # 北极点 -> 当前经度的点 -> 下一个经度的点
        faces.append([0, 1 + next_j, 1 + j])
    
    # 中间纬度带的四边形（拆分为两个三角形）
    for i in range(num_segments_vertical - 2):
        for j in range(num_segments_horizontal):
            next_j = (j + 1) % num_segments_horizontal
            
            # 当前纬度圈上的当前点
            current_vertex = 1 + i * num_segments_horizontal + j
            # 当前纬度圈上的下一个点
            current_next = 1 + i * num_segments_horizontal + next_j
            # 下一纬度圈上的当前点
            next_lat_vertex = 1 + (i + 1) * num_segments_horizontal + j
            # 下一纬度圈上的下一个点
            next_lat_next = 1 + (i + 1) * num_segments_horizontal + next_j
            
            # 第一个三角形
            faces.append([current_vertex, current_next, next_lat_next])
            # 第二个三角形
            faces.append([current_vertex, next_lat_next, next_lat_vertex])
    
    # 南极点附近的三角形
    south_pole_index = len(vertices) - 1
    last_latitude_start = 1 + (num_segments_vertical - 2) * num_segments_horizontal
    
    for j in range(num_segments_horizontal):
        next_j = (j + 1) % num_segments_horizontal
        
        # 当前纬度圈上的点 -> 下一个经度的点 -> 南极点
        faces.append([last_latitude_start + j, last_latitude_start + next_j, south_pole_index])
    
    faces = np.array(faces)
    
    # 3. 创建并保存网格
    sphere_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    
    for i, f in enumerate(faces):
        for j in range(3):
            sphere_mesh.vectors[i][j] = vertices[f[j], :]
    
    # 4. 保存到STL文件
    sphere_mesh.save(filename)
    
    # 5. 输出信息
    print(f"球体STL文件已保存: {filename}")
    print(f"参数: 半径={radius}, 垂直分段数={num_segments_vertical}, 水平分段数={num_segments_horizontal}")
    print(f"顶点数: {len(vertices)}, 面数: {len(faces)}")
    
    return vertices, faces

def create_cone_stl(filename, radius=0.5, height=1.0, num_segments=16):
    """
    创建一个Z轴方向的圆锥体STL文件
    
    参数:
    - filename: 输出STL文件名
    - radius: 圆锥底面半径
    - height: 圆锥高度
    - num_segments: 圆周分段数，控制圆锥的平滑度
    """
    
    # 确保分段数至少为3
    num_segments = max(3, num_segments)
    
    # 1. 创建顶点数组
    vertices = []
    
    # 底面圆心顶点 (索引0)
    vertices.append([0.0, 0.0, 0.0])
    
    # 圆锥顶点 (索引1)
    vertices.append([0.0, 0.0, height])
    
    # 底面圆周顶点
    for i in range(num_segments):
        angle = 2 * math.pi * i / num_segments
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        z = 0.0
        vertices.append([x, y, z])
    
    vertices = np.array(vertices)
    
    # 2. 创建面（三角形）数组
    faces = []
    
    # 底面三角形 - 法向量方向向外
    for i in range(num_segments):
        next_i = (i + 1) % num_segments
        # 底面圆心 -> 下一个点 -> 当前点
        faces.append([0, 2 + next_i, 2 + i])
    
    # 侧面三角形
    for i in range(num_segments):
        next_i = (i + 1) % num_segments
        
        # 底面当前点索引
        bottom_current = 2 + i
        bottom_next = 2 + next_i
        
        # 圆锥顶点索引 (1)
        apex = 1
        
        # 侧面三角形 (底面当前点 -> 下一个点 -> 顶点)
        faces.append([bottom_current, bottom_next, apex])
    
    faces = np.array(faces)
    
    # 3. 创建并保存网格
    cone_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    
    for i, f in enumerate(faces):
        for j in range(3):
            cone_mesh.vectors[i][j] = vertices[f[j], :]
    
    # 4. 保存到STL文件
    cone_mesh.save(filename)
    
    # 5. 输出信息
    print(f"圆锥体STL文件已保存: {filename}")
    print(f"参数: 底面半径={radius}, 高度={height}, 分段数={num_segments}")
    print(f"顶点数: {len(vertices)}, 面数: {len(faces)}")
    
    return vertices, faces

def create_cone_with_top_stl(filename, bottom_radius=0.5, top_radius=0.3, height=1.0, num_segments=16):
    """
    创建一个Z轴方向的圆台（有顶面的圆锥）STL文件
    
    参数:
    - filename: 输出STL文件名
    - bottom_radius: 圆台底面半径
    - top_radius: 圆台顶面半径
    - height: 圆台高度
    - num_segments: 圆周分段数，控制圆台的平滑度
    """
    
    # 确保分段数至少为3
    num_segments = max(3, num_segments)
    
    # 1. 创建顶点数组
    vertices = []
    
    # 底面圆心顶点 (索引0)
    vertices.append([0.0, 0.0, 0.0])
    
    # 顶面圆心顶点 (索引1)
    vertices.append([0.0, 0.0, height])
    
    # 底面圆周顶点
    for i in range(num_segments):
        angle = 2 * math.pi * i / num_segments
        x = bottom_radius * math.cos(angle)
        y = bottom_radius * math.sin(angle)
        z = 0.0
        vertices.append([x, y, z])
    
    # 顶面圆周顶点
    for i in range(num_segments):
        angle = 2 * math.pi * i / num_segments
        x = top_radius * math.cos(angle)
        y = top_radius * math.sin(angle)
        z = height
        vertices.append([x, y, z])
    
    vertices = np.array(vertices)
    
    # 2. 创建面（三角形）数组
    faces = []
    
    # 底面三角形 - 法向量方向向外
    for i in range(num_segments):
        next_i = (i + 1) % num_segments
        # 底面圆心 -> 下一个点 -> 当前点
        faces.append([0, 2 + next_i, 2 + i])
    
    # 顶面三角形
    for i in range(num_segments):
        next_i = (i + 1) % num_segments
        # 顶面圆心 -> 当前点 -> 下一个点
        faces.append([1, 2 + num_segments + i, 2 + num_segments + next_i])
    
    # 侧面三角形
    for i in range(num_segments):
        next_i = (i + 1) % num_segments
        
        # 底面当前点索引
        bottom_current = 2 + i
        bottom_next = 2 + next_i
        
        # 顶面对应点索引
        top_current = 2 + num_segments + i
        top_next = 2 + num_segments + next_i
        
        # 第一个侧面三角形
        faces.append([bottom_current, bottom_next, top_next])
        
        # 第二个侧面三角形
        faces.append([bottom_current, top_next, top_current])
    
    faces = np.array(faces)
    
    # 3. 创建并保存网格
    cone_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    
    for i, f in enumerate(faces):
        for j in range(3):
            cone_mesh.vectors[i][j] = vertices[f[j], :]
    
    # 4. 保存到STL文件
    cone_mesh.save(filename)
    
    # 5. 输出信息
    print(f"圆台STL文件已保存: {filename}")
    print(f"参数: 底面半径={bottom_radius}, 顶面半径={top_radius}, 高度={height}, 分段数={num_segments}")
    print(f"顶点数: {len(vertices)}, 面数: {len(faces)}")
    
    return vertices, faces

# 创建不同面数的圆柱体示例
if __name__ == "__main__":
    
    #cylinder
    vertices3, faces3 = create_cylinder_stl("./stl/cylinder.stl", 
                                             radius=0.053, 
                                             height=0.02, 
                                             num_segments=20)
    #sphere
    vertices_sph, faces_sph = create_sphere_stl("./stl/sphere_example.stl", 
                                                  radius=0.5, 
                                                  num_segments_vertical=12, 
                                                  num_segments_horizontal=12)
    
    vertices_sph_lq, faces_sph_lq = create_sphere_stl("./stl/sphere_lq_example.stl", 
                                                        radius=1.0, 
                                                        num_segments_vertical=8, 
                                                        num_segments_horizontal=8)
    vertices_sph_hq, faces_sph_hq = create_sphere_stl("./stl/sphere_hq_example.stl", 
                                                        radius=1.0, 
                                                        num_segments_vertical=24, 
                                                        num_segments_horizontal=24)
    #cone
    vertices_cone, faces_cone = create_cone_stl("./stl/cone_example.stl", 
                                                 radius=0.5, 
                                                 height=1.0, 
                                                 num_segments=12)
    #frustum
    vertices_frustum, faces_frustum = create_cone_with_top_stl("./stl/frustum_example.stl", 
                                                                bottom_radius=0.5, 
                                                                top_radius=0.2, 
                                                                height=1.0, 
                                                                num_segments=12)
    
    
    
    