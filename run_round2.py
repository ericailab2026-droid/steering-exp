#!/usr/bin/env python3
"""
GPT-2 Active Steering - Round 2 Experiment
使用纯净情感样本重新提取 Steering Vector 并测试
"""

import torch
import json
from pathlib import Path
from transformer_lens import HookedTransformer
import warnings
warnings.filterwarnings('ignore')

# 纯净样本数据
POSITIVE_SAMPLES = [
    "This brilliant idea is absolutely remarkable and outstanding.",
    "The team's incredible contribution was truly extraordinary.",
    "What a fantastic achievement, brilliantly executed.",
    "The work is perfect and genuinely impressive.",
    "An exceptional performance, truly magnificent.",
    "The results are wonderful and beautifully crafted.",
    "Such a magnificent accomplishment, truly inspiring.",
    "The quality is superb, absolutely first-class."
]

NEGATIVE_SAMPLES = [
    "This terrible mistake is absolutely awful and ridiculous.",
    "The team's pathetic failure was truly disgraceful.",
    "What a disastrous outcome, shamefully executed.",
    "The work is horrible and genuinely insulting.",
    "An embarrassing performance, truly incompetent.",
    "The results are dreadful and poorly done.",
    "Such a shameful failure, truly unacceptable.",
    "The quality is abysmal, absolutely worthless."
]

TEST_PROMPTS = [
    "I need to make a decision about the next project",
    "The team has presented their",
    "After careful consideration, I think",
    "Your recent work on the project",
    "The overall assessment of the"
]

ALPHA_VALUES = [1, 2, 3, 4, 5, -4, -5]
TARGET_LAYERS = [6, 8]

def get_sentence_activation(model, sentence, layer):
    """获取单个句子在特定层的最后一个 token 激活"""
    tokens = model.to_tokens(sentence, prepend_bos=True)
    
    result = []
    def hook(act, hook, store=result):
        # 取最后一个 token
        store.append(act[0, -1, :].cpu())
    
    with torch.no_grad():
        model.run_with_hooks(tokens, fwd_hooks=[(f"blocks.{layer}.hook_resid_post", hook)])
    
    return result[0]

def extract_steering_vector(positive_sentences, negative_sentences, layer=8):
    """提取 Steering Vector"""
    pos_activations = [get_sentence_activation(model, s, layer) for s in positive_sentences]
    neg_activations = [get_sentence_activation(model, s, layer) for s in negative_sentences]
    
    pos_mean = torch.stack(pos_activations).mean(dim=0)
    neg_mean = torch.stack(neg_activations).mean(dim=0)
    
    vector = pos_mean - neg_mean
    vector = vector / vector.norm() * 10.0  # 标准化
    
    return vector, pos_activations, neg_activations

def calculate_silhouette(pos_activations, neg_activations):
    """计算 Silhouette 分数"""
    try:
        import numpy as np
        from sklearn.metrics import silhouette_score
        
        all_activations = torch.cat(pos_activations + neg_activations).numpy()
        labels = np.array([0]*len(pos_activations) + [1]*len(neg_activations))
        
        return silhouette_score(all_activations, labels)
    except Exception as e:
        print(f"   Silhouette 计算失败：{e}")
        return 0.0

def generate_with_steering(model, prompt, steering_vector, alpha, layer=8):
    """使用 steering vector 生成"""
    tokens = model.to_tokens(prompt, prepend_bos=True)
    
    def steering_hook(act, hook):
        return act + alpha * steering_vector.unsqueeze(0).unsqueeze(0)
    
    with torch.no_grad():
        generated = model.generate(
            tokens,
            max_new_tokens=30,
            stop_at_eos=False,
            fwd_hooks=[(f"blocks.{layer}.hook_resid_post", steering_hook)]
        )
    
    model.reset_hooks()
    return model.to_string(generated[0])

def main():
    print("🧪 开始第二轮实验：纯净样本版")
    print("=" * 50)
    
    global model
    print("加载 GPT-2 模型 (MPS)...")
    model = HookedTransformer.from_pretrained("gpt2", device="mps")
    print(f"✅ 模型加载完成：{model.cfg.n_layers} 层，{model.cfg.d_model} 维")
    
    # 提取 Layer 8 Steering Vector
    print("\n🔍 提取 Layer 8 Steering Vector...")
    steering_vec_8, pos_act_8, neg_act_8 = extract_steering_vector(POSITIVE_SAMPLES, NEGATIVE_SAMPLES, layer=8)
    sil_8 = calculate_silhouette(pos_act_8, neg_act_8)
    print(f"   ✓ Silhouette: {sil_8:.3f}")
    print(f"   ✓ Vector norm: {steering_vec_8.norm().item():.2f}")
    
    # 提取 Layer 6 (用于对比)
    print("\n🔍 提取 Layer 6 Steering Vector...")
    steering_vec_6, pos_act_6, neg_act_6 = extract_steering_vector(POSITIVE_SAMPLES, NEGATIVE_SAMPLES, layer=6)
    sil_6 = calculate_silhouette(pos_act_6, neg_act_6)
    print(f"   ✓ Silhouette: {sil_6:.3f}")
    print(f"   ✓ Vector norm: {steering_vec_6.norm().item():.2f}")
    
    # 生成测试（使用 Layer 8, 因为它 Silhouette 更高）
    print("\n🎯 测试不同α值的生成效果 (Layer 8)...")
    results = {}
    
    for prompt in TEST_PROMPTS:
        print(f"\n  Prompt: {prompt[:50]}...")
        results[prompt] = {"baseline": "", "steered": {}}
        
        # Baseline
        tokens = model.to_tokens(prompt, prepend_bos=True)
        with torch.no_grad():
            baseline = model.generate(tokens, max_new_tokens=30)
            results[prompt]["baseline"] = model.to_string(baseline[0])
        
        # 不同α值
        for alpha in ALPHA_VALUES:
            generated = generate_with_steering(model, prompt, steering_vec_8, alpha, layer=8)
            results[prompt]["steered"][str(alpha)] = generated
        
        # 打印部分结果
        print(f"  Baseline: {results[prompt]['baseline'][:70]}...")
        for alpha in [3, 5, -4]:
            if str(alpha) in results[prompt]["steered"]:
                text = results[prompt]["steered"][str(alpha)][:70]
                print(f"  α={alpha}: {text}...")
    
    # 保存结果
    output_dir = Path("/Users/ericjiang/projects/interp-lab/steering-exp")
    
    result_file = output_dir / "round2_results.json"
    with open(result_file, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n✅ 结果保存：{result_file}")
    
    vector_file = output_dir / "best_steer_vector_round2.pt"
    torch.save({"layer6": steering_vec_6, "layer8": steering_vec_8, "sil_6": sil_6, "sil_8": sil_8}, vector_file)
    print(f"✅ 向量保存：{vector_file}")
    
    # 打印实验总结
    print("\n" + "="*50)
    print("📊 第二轮实验总结")
    print(f"  最佳层：Layer {'8' if sil_8 > sil_6 else '6'} (Silhouette: {max(sil_6, sil_8):.3f})")
    print(f"  测试α: {ALPHA_VALUES}")
    print(f"  GitHub Pages: https://ericailab2026-droid.github.io/steering-exp")

if __name__ == "__main__":
    main()
