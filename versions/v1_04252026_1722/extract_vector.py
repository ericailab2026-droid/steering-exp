"""
Steering Vector 提取脚本
目标: 从 GPT-2 的激活中提取出 "赞美 - 批评" 方向向量
"""

import torch
from transformer_lens import HookedTransformer
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
from steering_data import POSITIVE_PROMPTS, NEGATIVE_PROMPTS

# 设置设备
device = "mps" if torch.backends.mps.is_available() else "cpu"
print(f"🔧 使用设备: {device}")

# 加载模型
print("📥 加载 GPT-2 small 模型...")
model = HookedTransformer.from_pretrained("gpt2", device=device)
print(f"✅ 模型加载完成 ({model.cfg.n_layers}层, {model.cfg.d_model}维)")

# 参数配置
TARGET_LAYERS = [4, 6, 8]  # 测试多层
HOOK_NAMES = {
    4: "blocks.4.hook_resid_post",
    6: "blocks.6.hook_resid_post", 
    8: "blocks.8.hook_resid_post"
}

def get_activations(prompts, layer_idx, hook_name):
    """
    对一组 prompts 提取目标层最后一个 token 的激活
    返回: [num_prompts, d_model] tensor
    """
    activations = []
    for prompt in prompts:
        tokens = model.to_tokens(prompt).to(device)
        
        # 只在目标层缓存激活
        _, cache = model.run_with_cache(
            tokens, 
            names_filter=lambda name: name == hook_name
        )
        
        # 提取最后一个内容 token 的激活
        # cache[hook_name] shape: [batch=1, seq_len, d_model]
        act = cache[hook_name][0, -1, :]  # shape: [d_model]
        activations.append(act)
    
    return torch.stack(activations)  # [num_prompts, d_model]

def calculate_steering_vector(pos_acts, neg_acts):
    """
    计算 steering vector = mean(positive) - mean(negative)
    并返回统计信息
    """
    pos_mean = pos_acts.mean(dim=0)
    neg_mean = neg_acts.mean(dim=0)
    
    steering_vec = pos_mean - neg_mean
    
    return {
        "vector": steering_vec,
        "norm": steering_vec.norm().item(),
        "pos_mean_norm": pos_mean.norm().item(),
        "neg_mean_norm": neg_mean.norm().item(),
        "pos_mean": pos_mean,
        "neg_mean": neg_mean
    }

def visualize_activations(pos_acts, neg_acts, layer_name, save_path):
    """
    用 PCA 将激活投影到 2D 并可视化
    """
    all_activations = torch.cat([pos_acts, neg_acts]).cpu().numpy()
    labels = ["Positive"] * len(pos_acts) + ["Negative"] * len(neg_acts)
    
    # PCA 降维
    pca = PCA(n_components=2)
    projected = pca.fit_transform(all_activations)
    
    # 绘图
    plt.figure(figsize=(10, 8))
    sns.scatterplot(
        x=projected[:, 0], y=projected[:, 1],
        hue=labels,
        s=100,
        palette={"Positive": "green", "Negative": "red"},
        alpha=0.7
    )
    
    # 添加 steering vector 箭头
    pos_mean_proj = pca.transform([pos_acts.mean(dim=0).cpu().numpy()])[0]
    neg_mean_proj = pca.transform([neg_acts.mean(dim=0).cpu().numpy()])[0]
    vec_proj = pos_mean_proj - neg_mean_proj
    
    plt.arrow(
        neg_mean_proj[0], neg_mean_proj[1],
        vec_proj[0], vec_proj[1],
        head_width=0.5, head_length=0.8, fc='blue', ec='blue',
        length_includes_head=True
    )
    
    plt.title(f"{layer_name}\nSteering Vector (PCA 2D Projection)")
    plt.xlabel(f"PC1 ({pca.explained_variance_ratio_[0]:.2%})")
    plt.ylabel(f"PC2 ({pca.explained_variance_ratio_[1]:.2%})")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    
    # 计算可分性
    from sklearn.metrics import silhouette_score
    sil_score = silhouette_score(projected, labels)
    
    return sil_score

# ==================== 主流程 ====================

print("\n" + "="*60)
print("🚀 开始提取 Steering Vector")
print("="*60)

results = {}

for layer_idx in TARGET_LAYERS:
    hook_name = HOOK_NAMES[layer_idx]
    print(f"\n[Layer {layer_idx}] 提取激活...")
    
    # 提取正负样本激活
    pos_acts = get_activations(POSITIVE_PROMPTS, layer_idx, hook_name)
    neg_acts = get_activations(NEGATIVE_PROMPTS, layer_idx, hook_name)
    
    print(f"   Positive: {pos_acts.shape} | Negative: {neg_acts.shape}")
    
    # 计算 steering vector
    result = calculate_steering_vector(pos_acts, neg_acts)
    
    # 可视化
    img_path = f"layer{layer_idx}_pca.png"
    sil_score = visualize_activations(
        pos_acts, neg_acts, 
        f"Layer {layer_idx}", 
        img_path
    )
    
    result["silhouette_score"] = sil_score
    result["pos_acts"] = pos_acts
    result["neg_acts"] = neg_acts
    
    results[layer_idx] = result
    
    print(f"   ✅ Steering Vector L2 Norm: {result['norm']:.2f}")
    print(f"      Positive Mean Norm: {result['pos_mean_norm']:.2f}")
    print(f"      Negative Mean Norm: {result['neg_mean_norm']:.2f}")
    print(f"      2D 可分性 (Silhouette): {sil_score:.3f}")
    print(f"      ✨ 可视化已保存：{img_path}")

# 保存最佳层数的 steering vector
# 选择 norm 适中且可分性最好的层
best_layer = max(results.keys(), key=lambda k: results[k]["silhouette_score"])
best_vector = results[best_layer]["vector"]
best_norm = best_vector.norm().item()

# 归一化以便后续使用
best_vector_normalized = best_vector / best_norm * 10  # 标准化为 norm=10

print("\n" + "="*60)
print("✅ 提取完成!")
print(f"📌 最佳层数：Layer {best_layer}")
print(f"📌 标准化向量 (norm=10): saved to best_steer_vector.pt")
print("="*60)

# 保存
torch.save(best_vector_normalized, f"best_steer_vector_layer{best_layer}.pt")
torch.save(results, "all_layers_results.pt")

print(f"\n💡 下次实验使用: torch.load('best_steer_vector_layer{best_layer}.pt')")
