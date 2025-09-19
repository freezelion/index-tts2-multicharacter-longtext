# Multi-Character Long Text Emotion Generator for IndexTTS2

增强版的长文本情绪生成器，支持多角色配音、角色特定声音参数、对白与旁差的差异化处理。

## 🎭 核心特性

### 多角色支持
- **角色配置**: 每个角色可设置独立的声音文件和参数
- **自动识别**: 智能识别文本中的角色对话
- **声音个性化**: 支持音调、语速、音量的个性化设置
- **情绪差异化**: 对白情绪更强烈，旁白情绪更含蓄

### 高级情绪控制
- **多格式标签**: 支持 `[emotion:alpha]`, `{emotion:alpha}`, `<emotion:alpha>`
- **情绪映射**: 支持中英文情绪词汇映射
- **动态调整**: 对白情绪强度自动增强20%，旁白情绪强度自动减弱20%
- **复杂情绪**: 支持复合情绪状态
- **语速优化**: 自动处理语速与情绪的相互作用，确保语音速度不受情绪处理影响

### 智能文本处理
- **对话检测**: 自动识别中英文引号对话
- **角色前缀**: 支持 `角色名:` 和 `角色名：` 格式
- **文本分段**: 智能分段保持角色和情绪连续性
- **上下文感知**: 根据内容自动推测说话角色

## 🚀 快速开始

### 1. 配置角色声音

编辑 `character_config.json` 文件：

```json
{
  "characters": {
    "narrator": {
      "name": "旁白",
      "voice_file": "examples/voice_01.wav",
      "default_emotion": "calm",
      "emotion_intensity": 0.4,
      "speech_rate": 1.0,
      "pitch": 1.0,
      "volume": 1.0,
      "description": "故事叙述者，声音平稳自然"
    },
    "hero": {
      "name": "主角",
      "voice_file": "examples/voice_02.wav",
      "default_emotion": "calm",
      "emotion_intensity": 0.7,
      "speech_rate": 1.1,
      "pitch": 1.1,
      "volume": 1.0,
      "description": "主角声音，清脆有力"
    }
  }
}
```

### 2. 编写多角色文本

**角色前缀格式**:
```
narrator: [calm:0.3]在一个宁静的小镇上，住着一位年轻的画家。
hero: [happy:0.8]"今天天气真好！我们去公园画画吧！"
```

**引号对话格式**:
```
narrator: [calm:0.3]在一个宁静的小镇上，住着一位年轻的画家。
"hero: [happy:0.8]今天天气真好！我们去公园画画吧！"
```

**中文引号格式**:
```
narrator: [calm:0.3]在一个宁静的小镇上。
「hero: [happy:0.8]今天天气真好！我们去公园画画吧！」
```

### 3. 生成音频

```bash
# 使用配置文件生成多角色音频
uv run multi_character_emotion_generator.py \
  --config character_config.json \
  --input examples/multi_character_deep_sea_story.txt \
  --output deep_sea_story.wav \
  --verbose

# 直接输入文本
uv run multi_character_emotion_generator.py \
  --config character_config.json \
  --text "narrator: [calm]Hello world! \"hero: [happy]Hi there!\"" \
  --output hello.wav
```

## 🎛️ 角色参数详解

### 声音参数
- **speech_rate**: 语速 (0.5-2.0, 1.0为正常)
- **pitch**: 音调 (0.5-2.0, 1.0为正常)
- **volume**: 音量 (0.1-2.0, 1.0为正常)
- **emotion_intensity**: 情绪强度基准 (0.0-1.0)

### 情绪增强规则
- **对白**: 情绪强度 = 设定值 × 1.2 (最大1.0)
- **旁白**: 情绪强度 = 设定值 × 0.8
- **语速控制**: speech_rate >= 1.3 启用快速语音模式，speech_rate <= 0.8 启用慢速模式
- **语音优化**: 当 alpha <= 0.1 时，使用纯语音克隆，避免情绪处理影响语音质量和速度

### 示例角色配置
```json
"elderly_woman": {
  "name": "老妇人",
  "voice_file": "examples/voice_03.wav",
  "default_emotion": "calm",
  "emotion_intensity": 0.6,
  "speech_rate": 0.8,    // 语速较慢 (会自动启用慢速模式)
  "pitch": 0.7,         // 音调较低
  "volume": 0.9,        // 音量稍低
  "description": "年长女性，声音温和慈祥"
},
"child": {
  "name": "孩子",
  "voice_file": "examples/voice_04.wav",
  "default_emotion": "happy",
  "emotion_intensity": 0.8,
  "speech_rate": 1.3,    // 语速较快 (会自动启用快速模式)
  "pitch": 1.2,         // 音调较高
  "volume": 1.1,        // 音量较大
  "description": "儿童声音，活泼可爱"
}
```

## 📝 文本格式指南

### 1. 角色标识方式

**前缀标识** (推荐):
```
narrator: [calm:0.3]这是旁白内容。
hero: [happy:0.8]"这是角色对话！"
```

**引号对话**:
```
narrator: [calm:0.3]艾米说道：
"hero: [happy:0.8]今天天气真好！"
```

**中文引号**:
```
narrator: [calm:0.3]艾米开心地说道：
「hero: [happy:0.8]今天天气真好！」
```

### 2. 情绪标签格式

**完整格式**: `[emotion:alpha]`
```
hero: [happy:0.8]我很开心！
hero: [sad:0.6]我感到很难过。
```

**简化格式**: `[emotion]` (使用默认alpha=0.8)
```
hero: [happy]我很开心！
```

**多种分隔符**:
```
hero: [happy:0.8]我很开心！
hero: {happy:0.8} 我很开心！
hero: <happy:0.8> 我很开心！
```

**无情绪标签**: 对于普通文本，系统会使用纯语音克隆，确保原始声音质量
```
narrator: 这是普通的旁白文本，会保持原始声音质量。
```

### 3. 支持的情绪

**基础情绪**:
- `happy`, `angry`, `sad`, `afraid`, `disgusted`, `melancholic`, `surprised`, `calm`

> **重要说明**: 情绪向量顺序为 [快乐, 愤怒, 悲伤, 恐惧, 厌恶, 忧郁, 惊讶, 平静]，与IndexTTS2内部格式完全匹配

**扩展情绪**:
- `melancholic`, `determined`, `courageous`, `thoughtful`, `wise`
- `alarmed`, `shocked`, `amazed`, `outraged`, `reverent`
- `nostalgic`, `serene`, `content`, `peaceful`

**中文情绪**:
- `高兴`, `快乐`, `愤怒`, `生气`, `悲伤`, `难过`
- `恐惧`, `害怕`, `反感`, `厌恶`, `惊讶`, `吃惊`
- `低落`, `忧郁`, `自然`, `平静`

## 🎯 高级功能

### 1. 自动角色识别

系统会根据对话内容自动推测说话角色：

```python
# 关键词匹配规则
if any(word in text_lower for word in ['艾琳', '我', '我们']):
    return 'ailin'  # 女主角
elif any(word in text_lower for word in ['指挥官', '母舰']):
    return 'commander'  # 指挥官
```

### 2. 情绪上下文保持

长段落自动保持情绪连续性：

```
hero: [happy:0.8]今天真是美好的一天！阳光明媚，鸟语花香。
我很高兴能够和朋友们一起度过这样的时光。
每一刻都让我感到无比幸福。  # 后续句子保持相同情绪
```

### 3. 智能分段

系统会自动在合适的边界处分段：
- 句子边界优先
- 段落长度控制
- 角色切换边界
- 情绪变化边界

## 📊 性能优化

### 1. 模型缓存
- 每个角色的TTS模型只加载一次
- 内存中缓存，提高生成速度

### 2. 批量处理
- 支持长文本批量生成
- 自动分段并行处理

### 3. 内存管理
- 临时文件自动清理
- 音频段智能拼接

## 🛠️ 命令行参数

```bash
uv run multi_character_emotion_generator.py \
  --config character_config.json \      # 角色配置文件 (必需)
  --output output.wav \                 # 输出文件 (必需)
  --input story.txt \                  # 输入文本文件
  --text "direct text input" \         # 直接输入文本
  --model-dir ./checkpoints \          # 模型目录
  --segment-chars 200 \                # 每段最大字符数
  --fp16 \                            # 使用FP16加速
  --cuda-kernel \                     # CUDA内核优化
  --deepspeed \                       # DeepSpeed加速
  --verbose                           # 详细输出
```

## 🎨 创作建议

### 1. 角色声音设计
- **主角**: 音调稍高，语速适中，情绪表达丰富
- **反派**: 音调低沉，语速缓慢，情绪表达克制
- **老人**: 语速较慢，音调低沉，声音温和
- **儿童**: 语速较快，音调较高，情绪活泼

### 2. 情绪强度建议
- **旁白**: alpha 0.0-0.3 (含蓄内敛，推荐0.0以保持原始声音质量)
- **日常对话**: alpha 0.5-0.7 (自然表达)
- **强烈情感**: alpha 0.7-0.9 (明显情绪)
- **极端情绪**: alpha 0.9-1.0 (强烈爆发)

### 3. 声音文件选择
- **推荐使用立体声WAV文件**: 48kHz采样率的立体声文件效果最佳
- **避免单声道转换**: 直接使用原始立体声文件，不要转换为单声道
- **声音质量**: 高质量的声音样本能产生更好的克隆效果

### 4. 文本分段技巧
- 避免在句子中间分段
- 对话前后适当停顿
- 情绪变化处考虑分段
- 保持角色连续性

## 🔧 故障排除

### 常见问题

**1. 角色声音文件不存在**
```
Warning: Voice file not found for character: examples/voice_02.wav
```
解决方案：确保声音文件路径正确，文件存在

**2. 角色识别失败**
```
Warning: Unknown character: unknown_character
```
解决方案：检查角色ID是否在配置文件中定义

**3. 情绪标签解析错误**
```
Warning: Invalid emotion tag: [unknown_emotion:1.5]
```
解决方案：检查情绪名称拼写，alpha值范围

**4. 内存不足**
```
Error: CUDA out of memory
```
解决方案：减小segment-chars值，启用FP16模式

**5. 语音速度过慢**
```
问题：生成的音频语音速度很慢，即使设置了较高的speech_rate
原因：情绪处理可能影响语音速度
解决方案：
- 确保使用高质量的立体声音频文件作为声音样本
- 对于无情绪文本，系统会自动使用纯语音克隆
- 调整speech_rate值（>=1.3为快速，<=0.8为慢速）
- 检查emotion_intensity设置，过低的值可能导致意外效果

**6. 情绪表达不准确**
```
问题：愤怒听起来像悲伤，悲伤听起来像愤怒
原因：情绪向量顺序错误（已修复）
解决方案：确保使用最新版本的多角色生成器
```

## 📁 输出格式支持

### 音频格式
- **WAV格式**: `.wav` - 无损音频质量
- **MP3格式**: `.mp3` - 压缩音频，节省存储空间
- **自动检测**: 根据输出文件扩展名自动选择格式

### 使用示例
```bash
# 生成WAV格式
uv run multi_character_emotion_generator.py \
  --config character_config.json \
  --input story.txt \
  --output story.wav

# 生成MP3格式
uv run multi_character_emotion_generator.py \
  --config character_config.json \
  --input story.txt \
  --output story.mp3
```

## 📚 示例文件

查看 `examples/` 目录中的示例文件：
- `multi_character_deep_sea_story.txt` - 完整多角色科幻故事
- `simple_multi_character_example.txt` - 简单多角色对话示例
- `character_config.json` - 完整角色配置示例

## 🚀 未来发展

计划中的功能：
- [ ] 更多情绪状态支持
- [ ] 语音情感迁移学习
- [ ] 实时角色声音调整
- [ ] 多语言支持增强
- [ ] GUI配置界面
- [ ] 批量处理工具

## 📋 更新日志

### v2.1 (最新版本)
- **修复**: 情绪向量顺序错误问题（愤怒/悲伤位置互换）
- **优化**: 语音速度控制，避免情绪处理影响语速
- **新增**: MP3格式输出支持
- **改进**: 纯语音克隆模式，确保无情绪文本保持原始声音质量
- **修复**: 立体声音频文件支持，移除有问题的单声道转换

### v2.0
- **新增**: 多角色支持和情绪控制
- **新增**: 智能文本分段和角色识别
- **新增**: 描述性情绪处理（Qwen模型）
- **改进**: 音频拼接和同步

通过这个增强版的多角色情绪生成器，您可以创建丰富多彩的语音内容，让每个角色都有独特的声音个性和情感表达！