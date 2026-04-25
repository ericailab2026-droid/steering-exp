"""
Steering Generation 测试脚本
应用提取的 steering vector 并观察输出变化
"""

import torch
from transformer_lens import HookedTransformer
from steering_data import NEUTRAL_PROMPTS

# 设置设备
device = "mps" if torch.backends.mps.is_available() else "cpu"
print(f"🔧 使用设备: {device}")

# 加载模型
print("📥 加载 GPT-2 small 模型...")
model = HookedTransformer.from_pretrained("gpt2", device=device)
print("✅ 模型加载完成")

# 加载 steering vector
# 使用 Layer 8 的最佳向量
vector_path = "best_steer_vector_layer8.pt"
steering_vector = torch.load(vector_path, weights_only=True).to(device)
print(f"📌 加载 Steering Vector (Layer 8): norm = {steering_vector.norm().item():.2f}")

# 配置
TARGET_LAYER = 8
HOOK_NAME = f"blocks.{TARGET_LAYER}.hook_resid_post"

def make_steering_hook(alpha):
    """构建 steering hook 函数"""
    def hook_fn(activation, hook):
        # activation: [batch, seq_len, 768]
        # alpha * steering_vector: [768]
        # broadcasting 会自动加到每个 token
        return activation + alpha * steering_vector
    return hook_fn

# 测试 prompt（中性，让 steering 明显）
test_prompts = [
    "I need to make a decision about",
    "The team has presented their",
    "After careful consideration, I think",
    "Your recent work on the project"
]

gen_kwargs = {
    "max_new_tokens": 50,
    "temperature": 0.7,
    "do_sample": True,
    "stop_at_eos": False
}

print("\n" + "="*70)
print("🧪 开始生成测试 - 不同 α 值对比")
print("="*70)

results = []

for prompt in test_prompts:
    print(f"\n📝 原始 Prompt: {prompt!r}")
    print("-"*70)
    
    # Baseline (α=0)
    torch.manual_seed(42)
    baseline = model.generate(prompt, **gen_kwargs)
    print(f"   [α=0]  Baseline:\n        {baseline}")
    
    results.append({
        "prompt": prompt,
        "baseline": baseline,
        "steered": {}
    })
    
    # 不同 α 值
    alphas = [3, 6, 10, 15, -6, -10]
    for alpha in alphas:
        torch.manual_seed(42)  # 保持种子一致，公平比较
        with model.hooks(fwd_hooks=[(HOOK_NAME, make_steering_hook(alpha))]):
            output = model.generate(prompt, **gen_kwargs)
        
        print(f"   [α={alpha:+3d}] Steered:\n        {output}")
        results[-1]["steered"][alpha] = output
        print()
    print("="*70)

# 保存结果
import json
output_file = "generation_results.json"
with open(output_file, 'w') as f:
    # 只保存字符串部分
    json_results = {
        r["prompt"]: {
            "baseline": r["baseline"],
            "steered": {str(k): v for k, v in r["steered"].items()}
        }
        for r in results
    }
    json.dump(json_results, f, indent=2, ensure_ascii=False)

print(f"\n✅ 结果已保存到 {output_file}")
print("📊 建议：人工检查输出，判断哪些 α 值产生了明显的风格偏移")
