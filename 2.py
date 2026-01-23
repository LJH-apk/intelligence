import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib
import sys

# 解决macOS后端报错（关键修复）
matplotlib.use('Agg')  # 非交互式后端，避免macOS的Tkinter报错
# 若需交互式显示，可替换为：matplotlib.use('Qt5Agg')（需安装pyqt5：pip install pyqt5）

# -------------------------- 1. 全局配置（修复中文+显示问题） --------------------------
# 根据系统自动选择字体
if sys.platform == 'darwin':  # macOS
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'PingFang HK']
elif sys.platform == 'win32':  # Windows
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
else:  # Linux或其他
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans']

plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 8  # 统一字体大小，避免标签重叠
fig, ax = plt.subplots(figsize=(14, 10), dpi=150)  # 改用subplots，更稳定

# 颜色方案 - 修复：为所有节点类型定义颜色
COLORS = {
    "input": "#e1f5fe",        # 输入层
    "feat_extract": "#f3e5f5", # 特征提取层
    "lstm_branch": "#e8f5e8",  # LSTM分支
    "lstm_layer": "#e8f5e8",   # LSTM层
    "dropout": "#e8f5e8",      # Dropout层
    "time_encoding": "#e8f5e8",# 时间特征编码
    "informer_branch": "#fff3e0",  # Informer分支
    "pos_encoding": "#fff3e0",    # 位置编码
    "prob_sparse": "#fff3e0",     # ProbSparse注意力
    "feed_forward": "#fff3e0",    # 前馈网络
    "distilling": "#fff3e0",      # 蒸馏机制
    "fusion": "#fce4ec",       # 特征融合层
    "output": "#ffebee",       # 输出层
    "result": "#f1f8e9"        # 预测结果
}

# -------------------------- 2. 构建图结构 --------------------------
G = nx.DiGraph()

# 节点定义（简化标签，避免显示溢出）
nodes = {
    # 核心层级
    "input": "输入层\n(Input Layer)",
    "feat_extract": "特征提取层\n(Feature Extraction)",
    "fusion": "特征融合层\n(Feature Fusion)",
    "output": "输出层\n(Output Layer)",
    "result": "预测结果",

    # LSTM分支
    "lstm_branch": "LSTM分支",
    "lstm_layer": "LSTM层\n(序列依赖)",
    "dropout": "Dropout层\n(防止过拟合)",
    "time_encoding": "时间特征编码",

    # Informer分支
    "informer_branch": "Informer分支",
    "pos_encoding": "位置编码",
    "prob_sparse": "ProbSparse\n注意力",
    "feed_forward": "前馈网络",
    "distilling": "蒸馏机制"
}

# 添加节点
for node_id, label in nodes.items():
    G.add_node(node_id, label=label)

# 边定义
edges = [
    ("input", "feat_extract"),
    ("feat_extract", "lstm_branch"),
    ("feat_extract", "informer_branch"),
    ("fusion", "output"),
    ("output", "result"),
    # LSTM分支
    ("lstm_branch", "lstm_layer"),
    ("lstm_layer", "dropout"),
    ("dropout", "time_encoding"),
    ("time_encoding", "fusion"),
    # Informer分支
    ("informer_branch", "pos_encoding"),
    ("pos_encoding", "prob_sparse"),
    ("prob_sparse", "feed_forward"),
    ("feed_forward", "distilling"),
    ("distilling", "fusion")
]
G.add_edges_from(edges)

# -------------------------- 3. 节点位置（优化坐标，避免重叠） --------------------------
pos = {
    # 主层级
    "input": (7, 9),
    "feat_extract": (7, 8),
    "fusion": (7, 3),
    "output": (7, 2),
    "result": (7, 1),
    # LSTM分支（左侧）
    "lstm_branch": (3, 7),
    "lstm_layer": (3, 6),
    "dropout": (3, 5),
    "time_encoding": (3, 4),
    # Informer分支（右侧）
    "informer_branch": (11, 7),
    "pos_encoding": (11, 6),
    "prob_sparse": (11, 5),
    "feed_forward": (11, 4.5),
    "distilling": (11, 4)
}

# -------------------------- 4. 绘制节点（修复尺寸/形状兼容问题） --------------------------
# 核心层级（正方形）
core_nodes = ["input", "feat_extract", "fusion", "output", "result"]
nx.draw_networkx_nodes(
    G, pos, ax=ax, nodelist=core_nodes,
    node_size=3500, node_shape="s",
    node_color=[COLORS[n] for n in core_nodes],
    edgecolors="black", linewidths=1
)

# LSTM分支（圆形）
lstm_branch_nodes = ["lstm_branch", "lstm_layer", "dropout", "time_encoding"]
nx.draw_networkx_nodes(
    G, pos, ax=ax, nodelist=lstm_branch_nodes,
    node_size=3000, node_shape="o",
    node_color=[COLORS[n] for n in lstm_branch_nodes],  # 使用各自对应的颜色
    edgecolors="black", linewidths=1
)

# Informer分支（六边形）
informer_branch_nodes = ["informer_branch", "pos_encoding", "prob_sparse", "feed_forward", "distilling"]
nx.draw_networkx_nodes(
    G, pos, ax=ax, nodelist=informer_branch_nodes,
    node_size=3000, node_shape="h",
    node_color=[COLORS[n] for n in informer_branch_nodes],  # 使用各自对应的颜色
    edgecolors="black", linewidths=1
)

# -------------------------- 5. 绘制边（修复macOS兼容性问题） --------------------------
# 方法1：尝试不同的参数名（NetworkX版本兼容性）
try:
    # 先尝试较新的参数名
    nx.draw_networkx_edges(
        G, pos, ax=ax, edgelist=edges,
        arrows=True,
        arrowstyle="-|>",
        arrowsize=15,
        width=1.2,  # 新版本使用width
        edge_color="gray",
        connectionstyle="arc3,rad=0.05"
    )
except TypeError as e1:
    try:
        # 如果失败，尝试较旧的参数名
        print(f"尝试新参数失败: {e1}，尝试旧参数...")
        nx.draw_networkx_edges(
            G, pos, ax=ax, edgelist=edges,
            arrows=True,
            arrowstyle="-|>",
            arrowsize=15,
            linewidth=1.2,  # 旧版本可能使用linewidth
            edge_color="gray",
            connectionstyle="arc3,rad=0.05"
        )
    except TypeError as e2:
        # 如果还是失败，使用最简参数
        print(f"尝试旧参数也失败: {e2}，使用最简参数...")
        nx.draw_networkx_edges(
            G, pos, ax=ax, edgelist=edges,
            arrows=True,
            edge_color="gray",
            connectionstyle="arc3,rad=0.05"
        )

# -------------------------- 6. 绘制标签（修复字体显示） --------------------------
nx.draw_networkx_labels(
    G, pos, ax=ax,
    labels={n: G.nodes[n]["label"] for n in G.nodes},
    font_size=7, font_weight="bold"
)

# -------------------------- 7. 图例+美化 --------------------------
legend_elements = [
    mpatches.Patch(color=COLORS["input"], label="输入层"),
    mpatches.Patch(color=COLORS["feat_extract"], label="特征提取层"),
    mpatches.Patch(color=COLORS["lstm_branch"], label="LSTM分支"),
    mpatches.Patch(color=COLORS["informer_branch"], label="Informer分支"),
    mpatches.Patch(color=COLORS["fusion"], label="特征融合层"),
    mpatches.Patch(color=COLORS["output"], label="输出层"),
    mpatches.Patch(color=COLORS["result"], label="预测结果")
]
ax.legend(handles=legend_elements, loc="upper right", fontsize=9, framealpha=0.9)

# 隐藏坐标轴
ax.axis("off")
ax.set_title("LSTM + Informer 融合模型架构图", fontsize=14, fontweight="bold", pad=20)

# -------------------------- 8. 保存图片（关键：避免显示报错，优先保存） --------------------------
plt.tight_layout()
plt.savefig(
    "LSTM_Informer_Fusion_Architecture.png",
    bbox_inches="tight",  # 裁剪空白
    dpi=300,  # 高清输出
    facecolor='white'
)
plt.close()  # 关闭画布，释放资源

print("架构图已保存为：LSTM_Informer_Fusion_Architecture.png")
print(f"图片尺寸：{fig.get_size_inches()[0]:.1f} x {fig.get_size_inches()[1]:.1f} 英寸")
print(f"分辨率：{fig.dpi} DPI")
print("注意：如果你使用的是较旧的NetworkX版本，可能需要更新：pip install --upgrade networkx")