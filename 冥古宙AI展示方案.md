# 冥古宙地球 AI 展示方案

这份方案按“下次课前展示”来设计，目标不是只出几张图，而是把你的作品做得像一个小型研究型项目。

## 一句话策略

不要把任务理解成“随便输一句 prompt”。更好的做法是：

1. 先用论文和 NASA 信息，确定冥古宙地球的几个关键视觉特征。
2. 再用至少两种不同的生成式 AI 工具分别生成。
3. 最后展示“同一科学设定，不同模型的风格差异和偏差”。

这样讲出来会比单纯拼图强很多。

## 你可以直接讲的核心科学设定

冥古宙地球不是简单的“到处都是火山和岩浆”的地狱画面。更稳妥的讲法是：

- 早期地球经历过剧烈撞击、火山活动强、天空浑浊，整体环境非常暴烈。
- 但锆石等证据支持：在冥古宙后期，地表可能已经出现液态水，甚至可能存在较早的海洋或“水世界”状态。
- 早期大气成分很复杂，不适合说得过死。更谨慎的视觉表达是：厚大气、蒸汽感、火山气体、撞击尘埃、局部甲烷/还原性环境，而不是现代蓝天白云。

你在展示时可以把“冥古宙地球”拆成 4 个可视化主题：

1. 宏观行星视角：太空中看到的冥古宙地球。
2. 地表环境视角：黑色玄武岩、熔岩、蒸汽海洋、频繁闪电、火山灰天空。
3. 撞击事件视角：陨石坠入海洋或撞击大陆边缘。
4. 微观生命起源视角：热液喷口、潮池、矿物表面、富含化学梯度的环境。

## 最推荐的工具组合

为了满足“至少两种 AI 工具”，同时保证展示效果，建议选下面任意一组：

### 组合 A：最稳

- `ChatGPT / OpenAI GPT Image`
- `FLUX`

原因：

- OpenAI 的图像模型更擅长按复杂文字要求执行。
- FLUX 在质感、电影感、史诗感上通常很强。

### 组合 B：更适合做视觉对比

- `Midjourney`
- `ChatGPT / OpenAI GPT Image`

原因：

- Midjourney 更容易出“艺术大片感”。
- OpenAI 更适合做“论文驱动、设定明确”的版本。

### 组合 C：如果你想做标题海报

- `Ideogram`
- `FLUX` 或 `OpenAI GPT Image`

原因：

- Ideogram 对图中文字通常更稳，适合做展示封面页，例如图上直接带 `"Hadean Earth, 4.2 Ga"`。

## 直接可复制的高质量提示词

下面的 prompt 默认建议先用英文，因为多数图像模型对英文科学场景控制更稳。

### 1. 宏观星球版

```text
Photorealistic view of the Hadean Earth from space, 4.2 billion years ago, a dark rocky planet with vast steam-covered oceans, glowing volcanic belts, heavy meteor bombardment, thick hazy atmosphere rich in volcanic gases, no modern continents, no plants, no animals, dramatic sunlight scattering through dust and steam, scientifically grounded paleo-planetary reconstruction, ultra-detailed, cinematic, realistic geology
```

适合：

- OpenAI GPT Image
- FLUX
- Midjourney

### 2. 地表火山海洋版

```text
Ground-level view on the Hadean Earth, black basaltic coastline beside a hot primordial ocean, dense steam rising from the water, active volcanoes on the horizon, red lava flows, ash-filled sky, frequent lightning, sulfurous atmosphere, wet rocks, no vegetation, no humans, scientifically plausible early Earth environment, realistic photojournalistic style, extremely detailed
```

### 3. 陨石撞海版

```text
A giant meteor striking the Hadean ocean on early Earth, enormous steam explosion, molten ejecta, shockwave across a dark iron-rich sea, glowing sky filled with ash and debris, violent prebiotic planet, scientifically plausible impact scene, cinematic realism, ultra detailed
```

### 4. 热液喷口与生命起源版

```text
Deep ocean hydrothermal vents on the Hadean Earth, black smokers rising from a dark seafloor, mineral-rich fluids, iron-sulfur deposits, turbulent hot water mixing with cold ocean water, dramatic shafts of dim light, prebiotic chemistry environment, scientifically grounded, highly realistic underwater photography style
```

### 5. “冷却后的冥古宙”反差版

这个版本很适合你讲“科学界并不只是把冥古宙理解成纯岩浆地狱”。

```text
Scientific reconstruction of a cooler late Hadean Earth, shallow dark oceans under a thick hazy sky, scattered volcanic islands, intense geothermal activity, heavy clouds, no oxygen-rich blue sky, no life visible, ancient mineral-rich shoreline, realistic planetary science illustration with photorealistic textures
```

## 更稳的 Prompt 写法

你可以把 prompt 拆成 6 个槽位：

```text
[时间] + [视角] + [地貌] + [大气/天气] + [科学限制] + [风格]
```

例如：

```text
4.2 billion years ago + orbital view + steam oceans and volcanic belts + hazy CO2-rich atmosphere and dust + no plants, no animals, no modern continents + photorealistic cinematic reconstruction
```

这个结构比“写一大段诗意描述”更稳。

## 建议加上的负面约束

为了防止模型乱画现代地球特征，可以附加这些限制：

```text
no forests, no grass, no trees, no dinosaurs, no mammals, no birds, no modern continents, no cities, no human structures, no modern blue sky, no spacecraft, no text, no watermark
```

## 每个工具怎么调，效果更好

### OpenAI GPT Image

适合：

- 科学设定明确
- 多轮修改
- 同一主题连续迭代

建议：

- 先出 4 张，选最接近的一张继续改。
- 第二轮只改一两个变量，比如“更厚的蒸汽层”或“减少现代海蓝色”。

### FLUX

适合：

- 做电影感大片
- 做强烈光影
- 做火山、陨石、蒸汽、质感

建议：

- 宽高比拉开，例如 `1440x2048` 或 `1536x1024`。
- 同一 prompt 多跑几次，对比构图。

### Midjourney

适合：

- 概念美术感强
- 展示时“第一眼很震撼”

建议：

- 提示词写内容，不要写太多“命令式说明”。
- 如果有想要的色调和质感，用 `--sref` 风格参考图。

### Ideogram

适合：

- 生成带标题、标签、封面的图
- 展示页、海报页

建议：

- 如果要图里带文字，文字尽量写英文，且放在 prompt 前面。

## 能直接跑的脚本思路

如果老师希望你不只是“手工点网站”，你可以说你写了脚本批量生成同一主题的多个版本。

### 方案 1：OpenAI Image API

```bash
export OPENAI_API_KEY="你的key"

curl https://api.openai.com/v1/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-image-1.5",
    "prompt": "Photorealistic view of the Hadean Earth from space, 4.2 billion years ago, dark rocky planet, steam-covered oceans, glowing volcanic belts, thick hazy atmosphere, no modern continents, scientifically grounded reconstruction",
    "size": "1536x1024",
    "quality": "high"
  }'
```

你可以把 prompt 替换成上面那 4 个主题，然后批量生成。

### 方案 2：FLUX API

```bash
export BFL_API_KEY="你的key"

request=$(curl -X POST \
  "https://api.bfl.ai/v1/flux-2-pro-preview" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -H "x-key: $BFL_API_KEY" \
  -d '{
    "prompt": "Ground-level view on the Hadean Earth, black basaltic coastline beside a hot primordial ocean, dense steam, active volcanoes, ash-filled sky, realistic early Earth geology, extremely detailed",
    "width": 1536,
    "height": 1024
  }')

echo "$request"
```

然后继续轮询它返回的 `polling_url`，拿到最终图片地址。

## 最“炫酷”的进阶玩法

如果你想让展示明显高一个档次，下面这些是最值得讲的。

### 1. 论文驱动 Prompt Engineering

不要直接喂“冥古宙地球”四个字，而是先从论文提取视觉约束，再拼成 prompt。

你可以把论文信息整理成一个小表：

- 时间：`4.4 Ga / 4.2 Ga / 4.0 Ga`
- 水体：`steam ocean / shallow ocean / waterworld hypothesis`
- 大气：`thick haze / volcanic gases / impact-generated reduced atmosphere`
- 地表：`basaltic crust / volcanic islands / no modern continents`
- 事件：`meteor bombardment / hydrothermal activity / lightning`

然后对不同模型喂同一份“科学约束表”，这样你的展示会非常像一个小研究设计。

### 2. 做一个“论文到图像”的自动生成器

思路：

1. 读几篇论文摘要。
2. 把摘要喂给大语言模型。
3. 让它自动输出结构化 prompt。
4. 再把 prompt 发给图像模型。

你展示时可以说：

> 我不是手写每条 prompt，而是做了一个“paper-to-prompt”流程，把科学文献自动转成图像生成参数。

这个很加分。

### 3. 引入大量论文，做 RAG

这是你提到的“引入大量论文”的正经玩法。

可行版本不是自己训练一个大模型，而是：

1. 收集 10 到 30 篇和早期地球有关的论文或科普综述。
2. 把 PDF 切块。
3. 做向量检索。
4. 每次生成前先检索最相关段落。
5. 让 LLM 根据检索结果输出 prompt。

这样你就能说：

> 这几张图不是凭空想象，而是由论文证据检索后再生成的。

这是非常适合课堂展示的“高级但可做”的路线。

### 4. 训练一个小型 LoRA，而不是从零训练

“自己训练”可以讲，但不要说“从头训练一个图像模型”，那基本不现实。

更靠谱的说法是：

- 收集 `50-200` 张和早期地球相关的科学插图、行星艺术图、地质概念图。
- 自己做 captions。
- 训练一个小型 `LoRA`，目标不是学“真实历史照片”，而是学“冥古宙地球的统一视觉语言”。

这会让你的成果更稳定，比如总能生成：

- 黑色玄武岩地表
- 厚蒸汽层
- 暗红火山光
- 非现代大陆轮廓

展示时要强调：

> 我训练的不是“科学事实本身”，而是一个更统一的视觉风格层，用来减少模型把冥古宙画成现代地球的错误。

这个说法专业很多。

### 5. 用风格参考图做一致性

如果你用 Midjourney，可以用 `Style Reference`。
如果你用其他模型，也可以先生成一张“基准风格图”，再让后续图像参考它。

这样你展示的一组图会更像一个系列，而不是四张互不相干的随机图。

### 6. 把静态图升级成短视频

如果想要更炸裂，可以在最后加一步：

- 先生成一张冥古宙地球主图。
- 再用视频模型做 `5-8 秒` 运镜。

比如：

- 从太空推近到火山海岸
- 陨石撞海，蒸汽升腾
- 海底热液喷口冒出黑烟

这会比只放静态图更有展示效果。

## 最适合课堂讲述的展示结构

你可以直接按这个顺序讲：

1. 任务目标：用不同生成式 AI 重建冥古宙地球。
2. 科学依据：冥古宙并非只有“岩浆地狱”一种图景，后期可能已出现液态水和早期海洋。
3. 方法设计：先从论文抽取地质与大气特征，再转成 prompt。
4. 工具对比：用 OpenAI 和 FLUX，或 Midjourney 和 OpenAI，生成同主题图像。
5. 结果分析：比较不同模型对火山、海洋、天空颜色、撞击事件的偏差。
6. 进阶探索：RAG、LoRA、风格参考、多图一致性、图转视频。

## 你可以直接念的“高级版”讲述词

```text
我这次不是简单输入一句“冥古宙地球”来让 AI 出图，而是先查了早期地球的科学资料，把液态水、厚大气、火山活动、陨石撞击、玄武岩地表这些特征整理成结构化提示词。然后我用两种不同的生成式 AI 分别生成图像，比较它们在科学一致性和视觉表现上的差异。进一步我还考虑了一个论文增强的流程，也就是先从论文中检索相关描述，再自动生成 prompt，这样图像就不是纯想象，而是更接近“文献驱动的视觉重建”。
```

## 我建议你最终做成的成品

最稳的成品不是 1 张图，而是 1 页对比板：

- 左上：太空视角的冥古宙地球
- 右上：地表火山海洋
- 左下：陨石撞海
- 右下：热液喷口

每张图下方写 2 行：

- `Model: OpenAI GPT Image / FLUX / Midjourney`
- `Prompt basis: steam ocean, basaltic crust, volcanic haze, impact bombardment`

这样就已经像一个小型数字人文/数字地学项目了。

## 参考依据

- OpenAI 官方图像生成文档：推荐使用 `gpt-image-1.5`，支持高质量图像生成与编辑  
  [https://developers.openai.com/api/docs/guides/image-generation](https://developers.openai.com/api/docs/guides/image-generation)
- Black Forest Labs 官方文档：`FLUX.2` 文生图 API 采用异步提交和轮询结果的方式  
  [https://docs.bfl.ai/quick_start/generating_images](https://docs.bfl.ai/quick_start/generating_images)
- Midjourney 官方文档：`Style Reference` 可用于保持一组图像的统一风格  
  [https://docs.midjourney.com/hc/en-us/articles/32180011136653-Style-Reference](https://docs.midjourney.com/hc/en-us/articles/32180011136653-Style-Reference)
- Ideogram 官方文档：视觉锚定 prompt 更稳定，图中文字更适合用英文  
  [https://docs.ideogram.ai/using-ideogram/prompting-guide/2-prompting-fundamentals](https://docs.ideogram.ai/using-ideogram/prompting-guide/2-prompting-fundamentals)
- NASA：早期地球曾被描述为剧烈撞击、岩浆与沸腾火山活动主导，但锆石证据挑战了“永远炼狱”的单一图景  
  [https://science.nasa.gov/earth/earth-observatory/ancient-crystals-suggest-earlier-ocean/](https://science.nasa.gov/earth/earth-observatory/ancient-crystals-suggest-earlier-ocean/)
- Harrison, 2009：讨论 `>4 Ga zircons` 与 “Hadean Waterworld” 假说  
  [https://oceaniron.org/wp-content/uploads/sites/14/2018/10/Harrison_ARES_2009_58985.pdf](https://oceaniron.org/wp-content/uploads/sites/14/2018/10/Harrison_ARES_2009_58985.pdf)
- Zahnle et al., 2020：讨论大型撞击后早期地球还原性大气的形成与演化  
  [https://faculty.washington.edu/dcatling/Zahnle2020_Impact-induced-Miller-Urey-atmospheres.pdf](https://faculty.washington.edu/dcatling/Zahnle2020_Impact-induced-Miller-Urey-atmospheres.pdf)

## 如果你要我继续做

我下一步可以直接帮你补两样东西中的任意一种：

1. 写一个真正可跑的批量生成脚本，自动调用两个图像 API。
2. 按这个方案继续给你做一份 `5 页课堂展示 PPT 大纲`。
