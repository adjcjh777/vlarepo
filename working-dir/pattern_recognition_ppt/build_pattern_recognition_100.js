const path = require('path');
const PptxGenJS = require('../ppt_rework_climb/node_modules/pptxgenjs');
const {
  warnIfSlideHasOverlaps,
  warnIfSlideElementsOutOfBounds,
} = require('./pptxgenjs_helpers/layout');

const pptx = new PptxGenJS();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = 'Codex';
pptx.company = 'Junhao Cheng';
pptx.subject = '模式识别课程作业';
pptx.title = '模式识别全球企业案例研究';
pptx.lang = 'zh-CN';
pptx.theme = {
  headFontFace: 'Microsoft YaHei',
  bodyFontFace: 'Microsoft YaHei',
  lang: 'zh-CN',
};

const C = {
  bg: 'F6F1E8',
  ink: '171717',
  sub: '57534E',
  line: 'D6D3D1',
  card: 'FFFDFC',
  paper: 'FBF8F3',
  accent: 'B45309',
  gold: 'C28A2E',
  blue: '245C73',
  green: '2F6A4F',
  red: 'A03C2B',
  teal: '0E6D74',
  coral: 'B24F3A',
};

const companies = [
  {
    key: 'sensetime',
    name: 'SenseTime 商汤科技',
    en: 'SenseTime',
    accent: 'C65D2E',
    tag: '从计算机视觉龙头转向“AI 基础设施 + 大模型 + 智能汽车”一体化平台',
    profile: [
      ['成立时间', '2014 年'],
      ['总部/重心', '香港上市，上海/香港双核心布局'],
      ['模式识别主轴', '计算机视觉、多模态理解、生成式 AI'],
      ['当前定位', 'AI 基础设施与行业落地平台型公司'],
    ],
    why: [
      '商汤最早的品牌建立在“高精度视觉识别”上，人脸、图像、视频理解是其原点。',
      '公司已把模式识别能力扩展成“感知 + 生成 + 推理”体系，说明传统识别企业如何升级。',
      '其商业结构从项目型视觉业务逐步迁移到通用 AI 基础设施，更适合课堂讨论“技术变现路径”。',
      '对中国 AI 企业而言，商汤的案例代表了从 CV 独角兽向大模型平台的战略转身。',
    ],
    products: [
      ['SenseCore', '以算力、训练、推理和模型服务为核心的 AI 基础设施，支撑内部研发与外部企业客户。'],
      ['日日新 / SenseNova', '面向企业与行业场景的大模型能力层，把语言、视觉和多模态能力商品化。'],
      ['Smart Auto', '聚焦智能座舱与智能驾驶，把视觉感知迁移到车端场景。'],
      ['行业视觉方案', '面向城市、金融、零售、工业等行业的检测、分析与自动化决策。'],
    ],
    spotlightA: {
      title: '焦点产品 A：SenseCore + 日日新',
      bullets: [
        '关键逻辑不是只卖“模型”，而是把模型训练、部署、推理和企业接入做成平台服务。',
        'SenseCore 的价值在于把模式识别企业最贵的资源变成可复用基础设施，降低迭代成本。',
        '日日新则承接企业侧需求，把底层的视觉/多模态能力做成应用接口和解决方案。',
        '这意味着商汤在商业上正从“项目交付”切换到“平台订阅 + 行业解决方案”。',
      ],
      useCases: [
        '金融风控与客服智能化',
        '企业知识问答与办公智能体',
        '多模态文档与图像理解',
      ],
    },
    spotlightB: {
      title: '焦点产品 B：Smart Auto',
      bullets: [
        '智能汽车业务延续了商汤在视觉感知、场景理解和实时识别方面的核心积累。',
        '商业重心从早期 V2X 逐步转向智能座舱与端到端智驾，更符合车厂当前采购逻辑。',
        '相比通用互联网应用，汽车场景更强调低延迟、可解释性和安全冗余。',
        '这类场景说明模式识别技术只有嵌入高价值工作流，才会形成长期收入。',
      ],
      useCases: [
        '舱内视觉感知',
        '驾驶状态监测',
        '车端多模态交互',
      ],
    },
    stack: [
      ['数据层', '大规模视觉、多模态与行业场景数据，为模型训练和行业迁移提供燃料。'],
      ['基础设施层', 'SenseCore 负责算力调度、训练加速、推理服务与资源复用。'],
      ['模型层', '从传统 CV 模型延伸到大语言模型、多模态模型与行业专用模型。'],
      ['应用层', '金融、政企、智能汽车、企业服务等场景承接商业化。'],
    ],
    highlights: [
      '传统视觉识别资产没有被淘汰，而是被“升维”到多模态与生成式 AI 时代。',
      '“基础设施 + 模型 + 行业”三层联动，让研发投入更容易在多个场景复用。',
      '2024 年生成式 AI 收入已经成为最大收入来源，说明技术方向切换开始兑现。',
      '商汤的启示是：模式识别企业不能只做算法精度竞争，还要做平台能力整合。',
    ],
    moat: [
      '多年累积的视觉和行业数据，仍然是构建大模型应用的重要底座。',
      'SenseCore 形成算力与部署门槛，使其不只是“模型调用商”。',
      '中国本土政企/车企客户的部署需求，要求更强本地化和工程交付能力。',
      '品牌、人才与学术影响力使其更容易吸引企业客户与生态合作伙伴。',
    ],
    team: [
      ['汤晓鸥', '联合创始人、学术旗帜人物', '把计算机视觉研究能力转化成公司最早的技术品牌。'],
      ['徐立', '联合创始人、董事长兼 CEO', '主导公司商业化转型与“AI 基础设施 + 大模型”路线。'],
      ['王晓刚', '联合创始人', '强化视觉识别与深度学习研究积累。'],
      ['徐冰', '联合创始人', '推动产品化与组织扩张，是创业团队的重要经营角色。'],
    ],
    milestones: [
      '2014：公司成立，以计算机视觉为核心切入市场。',
      '2021：在香港上市，成为中国 AI 独角兽的代表性样本。',
      '2023：明确转向生成式 AI 与大模型布局。',
      '2024：生成式 AI 收入超过传统视觉，成为第一大收入来源。',
      '2025-2026：持续强化 SenseCore，并加快大模型与车端业务结合。',
    ],
    business: [
      '商业模式从单点项目交付，逐步转向“平台服务 + 行业方案 + 车企合作”。',
      '客户类型包括金融、政企、制造、互联网企业以及汽车厂商。',
      '组织能力很工程化，不只是研究导向，而是强调部署、交付和本地化适配。',
      '收入结构变化说明：模式识别技术能否持续变现，关键在于是否进入高频场景。',
    ],
    opsTitle: '经营与财务观察',
    opsBars: [
      ['2023 收入', 3405.8],
      ['2024 收入', 3772.1],
      ['2024 生成式 AI', 2404.0],
      ['2024 计算机视觉', 1111.9],
    ],
    opsMetrics: [
      ['2024 收入', '37.72 亿元'],
      ['同比增速', '+10.8%'],
      ['生成式 AI 占比', '63.7%'],
      ['毛利率', '42.9%'],
    ],
    opsNotes: [
      '2024 年总收入 37.72 亿元，同比增长 10.8%。',
      '生成式 AI 收入 24.04 亿元，同比增长 103.1%，已经成为第一大收入来源。',
      '传统计算机视觉收入下降，说明公司主动把资源向新业务倾斜。',
      '这是一种典型的“旧识别业务供血，新平台业务接棒”的战略过渡。',
    ],
    outlook: [
      '如果企业级大模型和私有化部署持续增长，SenseCore 会更像“卖铲子”的平台型业务。',
      '智能汽车若能进入更大规模量产，将为商汤提供更稳定的长周期客户。',
      '多模态场景的落地会让其传统视觉积累重新估值，而不是被通用 LLM 稀释。',
      '未来关键问题不是“有没有模型”，而是“能否高质量、低成本、规模化交付”。',
    ],
    risks: [
      '与更轻量、价格更低的开源模型和本土大模型平台竞争激烈。',
      'AI 基础设施重投入导致盈利改善速度可能慢于收入增长。',
      '传统项目制业务回落过快，可能给新业务承接带来阶段性压力。',
      '市场会持续追问：平台化收入是否足够稳健，是否能摆脱一次性交付依赖。',
    ],
    insight: [
      '我最大的感受是：商汤不是“离开模式识别”，而是把模式识别升级成大模型时代的底层资产。',
      '它提醒我们，识别技术本身容易同质化，但“识别 + 算力 + 行业流程”更容易形成壁垒。',
      '如果只讲精度，商汤会越来越难；如果讲平台与部署效率，故事就重新成立了。',
      '因此，模式识别企业的第二曲线，往往来自基础设施化和场景系统化。'],
    sourceNote: '来源：SenseTime 2024 Annual Report（HKEX, 2025）及公司官网公开资料。',
  },
  {
    key: 'iflytek',
    name: '科大讯飞 iFLYTEK',
    en: 'iFLYTEK',
    accent: '2463A8',
    tag: '从语音识别龙头扩展到“语音 + 认知 + 行业大模型”的中国 AI 平台公司',
    profile: [
      ['成立时间', '1999 年'],
      ['总部', '安徽合肥'],
      ['模式识别主轴', '语音识别、语音合成、语义理解、多模态'],
      ['当前定位', '行业 AI 平台 + 开放生态 + 消费产品'],
    ],
    why: [
      '讯飞是中国最典型的“从模式识别起家并持续商业化”的公司，研究基础非常深厚。',
      '其最早护城河是中文语音识别与评测，后来逐步拓展到文本、图像与多模态。',
      '相比很多只停留在算法层的企业，讯飞把技术嵌入教育、医疗、办公、车载等高价值场景。',
      '它非常适合作为“模式识别如何变成行业操作系统”的案例。',
    ],
    products: [
      ['讯飞星火', '以认知大模型为核心，承接文本、语音、图像、多模态能力。'],
      ['开放平台', '向开发者输出语音识别、语音合成、OCR、翻译等 API 与 SDK。'],
      ['智慧教育/智慧医疗', '把识别与认知能力嵌入教育和医疗工作流。'],
      ['消费级产品', '录音笔、办公本、翻译机等产品把算法能力转成可见终端。'],
    ],
    spotlightA: {
      title: '焦点产品 A：讯飞星火 + 开放平台',
      bullets: [
        '星火的意义不是追求“通用大模型第一名”，而是用讯飞原有语音优势切进行业场景。',
        '开放平台让讯飞能够持续吸引开发者，并把单点识别技术沉淀成标准化能力。',
        '这套组合特别适合中文场景，因为语音、方言、教育与政企场景对本地化要求高。',
        '对讯飞来说，大模型不是替代原有模式识别，而是把它们统一到更强的交互框架。'],
      useCases: [
        '语音会议纪要',
        '行业知识问答',
        '开发者 API 接入',
      ],
    },
    spotlightB: {
      title: '焦点产品 B：智慧教育与智慧医疗',
      bullets: [
        '讯飞真正难复制的地方，在于它掌握了教育和医疗这类高门槛、高流程依赖场景。',
        '在教育中，语音评测、作文批改、个性化学习建议构成了完整价值链。',
        '在医疗中，语音录入、病历结构化与辅助诊断让识别能力直接进入医生流程。',
        '这说明模式识别企业要建立深护城河，不能只卖工具，而要卖“完成任务的系统”。'],
      useCases: [
        '口语评测',
        '课堂与作业分析',
        '医疗录入与辅助诊断',
      ],
    },
    stack: [
      ['感知层', '语音识别、语音合成、图像识别、翻译等基础感知能力。'],
      ['认知层', '星火大模型承接推理、问答、生成与多模态理解。'],
      ['平台层', '开放平台、开发者工具链、国产算力与训练体系。'],
      ['行业层', '教育、医疗、汽车、企业服务、城市治理与消费电子。'],
    ],
    highlights: [
      '公司把语音识别从单点技术扩展为全栈 AI 能力树，这是长期积累的结果。',
      '拥有国家级实验室和工程中心，学术与产业化结合度高。',
      '2024 年开发者规模达到 224 万，说明平台生态已经形成网络效应。',
      '讯飞的核心优势不只是模型，而是中文场景与行业 know-how 的叠加。',
    ],
    moat: [
      '中文语音与行业数据积累非常深，尤其适合教育、医疗、政企等长尾场景。',
      '开放平台形成开发者生态，帮助公司不断吸收新需求并标准化输出能力。',
      '国产化训练体系和本地部署能力，对中国市场特别重要。',
      '软硬件结合与行业合作网络，使其商业化不依赖单一产品。',
    ],
    team: [
      ['刘庆峰', '创始人、董事长', '代表公司最核心的技术愿景与长期战略，是中国语音 AI 的标志人物。'],
      ['吴晓如', '总裁', '推动工程落地和组织管理，使研究成果进入大规模行业应用。'],
      ['胡郁', '核心技术带头人', '长期负责语音与认知智能研究，是讯飞技术路线的重要设计者。'],
      ['中科大科研背景', '创业起点', '学术起点决定了讯飞早期就以“底层技术自研”作为公司基因。'],
    ],
    milestones: [
      '1999：公司成立，语音识别与语音合成为核心方向。',
      '2008：上市，成为中国 AI 产业化代表公司。',
      '2010s：教育、医疗、车载和开放平台形成多条商业化曲线。',
      '2023：发布讯飞星火，进入大模型竞争。',
      '2024：继续加大大模型研发投入，并强化行业落地节奏。',
    ],
    business: [
      '收入来源分散，包括行业解决方案、开放平台、消费产品与企业服务。',
      '相比纯模型公司，讯飞更像“行业 AI 操作系统”提供商。',
      '在中国市场，它的商业化优势往往来自“场景深度”而不是“参数规模”。',
      '其营收结构说明：模式识别技术只要嵌入实际工作流，就能形成稳定现金流。',
    ],
    opsTitle: '经营与财务观察',
    opsBars: [
      ['2022 收入', 18820.2],
      ['2023 收入', 19650.3],
      ['2024 收入', 23343.1],
      ['2024 经营现金流', 2495.2],
    ],
    opsMetrics: [
      ['2024 收入', '233.43 亿元'],
      ['收入增速', '+18.79%'],
      ['归母净利润', '5.60 亿元'],
      ['开发者规模', '224 万'],
    ],
    opsNotes: [
      '2024 年营业收入 233.43 亿元，同比增长 18.79%。',
      '归母净利润 5.60 亿元，同比下降，核心原因之一是继续加码大模型和核心研发。',
      '经营活动现金流达到 24.95 亿元，说明其业务现金回笼能力在改善。',
      '这类财务结构很典型：平台型 AI 公司经常在利润与战略投入之间取平衡。',
    ],
    outlook: [
      '如果中国教育、医疗、政企市场继续推动国产 AI 替代，讯飞会持续受益。',
      '星火若能把语音优势和行业数据整合好，竞争方式会与通用 LLM 不同。',
      '开放平台仍然是长期增长杠杆，因为它决定了开发者生态和外部创新速度。',
      '未来最值得观察的是：大模型是否能真正拉动高毛利平台收入，而不仅是研发成本。',
    ],
    risks: [
      '大模型持续高投入，短期可能压制利润表现。',
      '应收账款与减值压力仍是投资者关注焦点。',
      '通用大模型开源生态可能冲击部分通用能力收费。',
      '组织庞大后，如何保持技术敏捷性，是平台型公司常见挑战。',
    ],
    insight: [
      '讯飞让我看到：模式识别企业最强的壁垒，往往不是算法论文，而是场景渗透率。',
      '它通过教育和医疗这两个高门槛场景，把语音能力变成了长期可收费的系统。',
      '所以我认为讯飞的真正竞争对手不是单一语音公司，而是任何想进入这些工作流的平台。',
      '对于课程作业而言，讯飞是“模式识别商业化最完整”的中国样本之一。',
    ],
    sourceNote: '来源：iFLYTEK 2024 Annual Report（2025）及公司官网公开资料。',
  },
  {
    key: 'cognex',
    name: 'Cognex',
    en: 'Cognex',
    accent: '2F6A4F',
    tag: '把机器视觉做成工业基础设施，是模式识别在制造业最成熟的商业化样本之一',
    profile: [
      ['成立时间', '1981 年'],
      ['总部', '美国马萨诸塞州 Natick'],
      ['模式识别主轴', '工业机器视觉、缺陷检测、读码识别'],
      ['当前定位', '工业自动化视觉基础设施提供商'],
    ],
    why: [
      'Cognex 很有代表性，因为它证明了模式识别不只属于互联网，也能成为制造业的硬科技基础设施。',
      '与消费 AI 不同，工业视觉的价值来自减少误检、停线和返工，因此客户愿意为稳定性付费。',
      '它把视觉识别与硬件、光学、软件和工程服务结合，形成很强的进入门槛。',
      '这家公司非常适合说明“高精度模式识别在 B 端的长期商业价值”。',
    ],
    products: [
      ['In-Sight Vision Systems', '固定式机器视觉系统，用于定位、检测、测量和识别。'],
      ['DataMan Barcode Readers', '面向制造和物流的工业读码与追踪系统。'],
      ['VisionPro / 软件平台', '让客户基于视觉算法构建更复杂的自动化检测流程。'],
      ['传感器与 3D 视觉方案', '覆盖更复杂的表面缺陷、装配校验与机器人引导场景。'],
    ],
    spotlightA: {
      title: '焦点产品 A：In-Sight',
      bullets: [
        'In-Sight 是 Cognex 最经典的产品线，本质上是把模式识别算法封装成工业现场可直接部署的视觉系统。',
        '它不是简单摄像头，而是“采集 + 光学 + 算法 + 控制接口”的一体化方案。',
        '客户真正购买的不是模型，而是稳定的良率和更低的误停机率。',
        '这说明工业场景中，模式识别的价值往往通过 ROI 而不是概念传播。'],
      useCases: [
        '零部件检测',
        '定位与测量',
        '机器人引导',
      ],
    },
    spotlightB: {
      title: '焦点产品 B：DataMan 与软件生态',
      bullets: [
        'DataMan 把条码/二维码识别做到了高速度、低误读率和恶劣环境适应性。',
        '在物流和电子制造中，追踪能力直接影响产线节拍与质量追责能力。',
        '软件平台则让 Cognex 能够从硬件收入延伸到更高附加值的系统级解决方案。',
        '机器视觉公司一旦形成安装基础，就会拥有很强的复购和升级机会。'],
      useCases: [
        '物流分拣读码',
        '电子制造追溯',
        '软件升级与再部署',
      ],
    },
    stack: [
      ['成像层', '工业相机、光源、镜头与环境适应性设计。'],
      ['识别层', '定位、匹配、检测、OCR/OCV、读码与缺陷识别。'],
      ['控制层', '和 PLC、机器人、产线系统联动，实现实时决策。'],
      ['软件层', '以开发工具和应用软件提升客户定制能力与复购率。'],
    ],
    highlights: [
      '工业视觉要求极高稳定性，因此算法与硬件一体化能力比单纯模型更关键。',
      'Cognex 把深度学习与传统规则视觉结合，兼顾可解释性和复杂场景适应性。',
      '超过 30,000 家客户意味着其产品经过了大量工业环境验证。',
      '在工业场景里，模式识别技术的护城河来自可靠性、部署经验和售后支持。',
    ],
    moat: [
      '深厚的工业应用工程经验，使其很难被通用 AI 厂商快速替代。',
      '硬件 + 软件 + 系统集成形成复合型壁垒，而不是单一算法优势。',
      '长期安装基础与渠道网络带来高复购率和高信任成本。',
      '品牌在高端机器视觉市场具有先发优势，客户更重视“不会出错”。',
    ],
    team: [
      ['Robert J. Shillman', '联合创始人', '把机器视觉从实验室概念推向可规模化的工业产品。'],
      ['Marilyn Matz', '联合创始人', '与技术团队共同奠定了早期产品和公司文化。'],
      ['现任管理层', '职业化经营', '在成熟产业中，稳定运营与资本配置同样重要。'],
      ['应用工程团队', '隐形核心资产', '工业公司真正的护城河之一，是懂客户现场问题的人。'],
    ],
    milestones: [
      '1981：公司成立，聚焦机器视觉。',
      '1990s：成为工业视觉领域的重要品牌。',
      '2000s：读码、检测与软件平台持续扩张。',
      '2020s：把深度学习视觉能力整合到既有工业视觉体系中。',
      '2024：收入回升，显示在电子与物流场景中的需求韧性。',
    ],
    business: [
      '客户主要来自电子、汽车、物流、消费品、医疗器械等制造与流通行业。',
      '商业模式偏 B2B 长周期，强调设备采购、集成、升级和售后。',
      'Cognex 的价值主张非常直接：更高良率、更低误判、更快节拍。',
      '这类公司说明，模式识别一旦嵌入 CAPEX 体系，生命周期会比互联网产品更长。',
    ],
    opsTitle: '经营与财务观察',
    opsBars: [
      ['2023 收入', 837.0],
      ['2024 收入', 915.0],
      ['现金与投资', 1000.0],
      ['客户数（千）', 30.0],
    ],
    opsMetrics: [
      ['2024 收入', '9.15 亿美元'],
      ['同比增速', '+9%'],
      ['现金与投资', '超 10 亿美元'],
      ['客户规模', '30,000+'],
    ],
    opsNotes: [
      '2024 年净销售额约 9.15 亿美元，同比增长约 9%。',
      '公司账上现金和投资超过 10 亿美元，且无债务，财务质量非常稳健。',
      '业务仍受制造业资本开支周期影响，但在高端视觉市场竞争力稳定。',
      '这表明工业模式识别可以成为高现金流、高毛利、长寿命的业务形态。',
    ],
    outlook: [
      '新能源汽车、电池、半导体、仓储自动化都会持续需要高精度视觉识别。',
      '工业 AI 的真正空间在于“把更多复杂质检任务自动化”。',
      '若将深度学习视觉更深入地产品化，Cognex 仍有机会提升单客户价值。',
      '未来成长速度未必像互联网 AI 那么快，但确定性通常更强。',
    ],
    risks: [
      '制造业和电子行业景气度波动会直接影响订单节奏。',
      '客户对资本开支谨慎时，视觉设备采购容易延后。',
      '低价智能相机和区域性竞争者可能带来价格压力。',
      '成熟工业公司若创新节奏过慢，也可能错过新一代 AI 机会。',
    ],
    insight: [
      'Cognex 让我意识到：模式识别最赚钱的地方，往往不是“最炫”，而是“最不能错”。',
      '工业视觉的商业逻辑非常朴素，只要客户算得过 ROI，就会持续买单。',
      '它也提醒我们，企业级识别技术的关键不是 demo 漂亮，而是系统可靠、维护方便、能长期运行。',
      '如果把模式识别看成基础设施，Cognex 是非常经典的成功样本。',
    ],
    sourceNote: '来源：Cognex investor relations、公司官网与公开财务资料。',
  },
  {
    key: 'soundhound',
    name: 'SoundHound AI',
    en: 'SoundHound AI',
    accent: 'A54833',
    tag: '把语音识别升级为“能完成业务流程的 Voice AI Agent”，是语音模式识别的新阶段',
    profile: [
      ['成立时间', '2005 年'],
      ['总部', '美国加州 Santa Clara'],
      ['模式识别主轴', '语音识别、语义理解、会话智能'],
      ['当前定位', '面向汽车、餐饮与客服场景的语音 AI 平台'],
    ],
    why: [
      'SoundHound 很适合展示模式识别技术从“识别命令”走向“完成任务”的路径。',
      '它的核心不只是 ASR，而是把语音、语义、知识图谱和工作流编排组合起来。',
      '相比通用助手，SoundHound 强调白标、品牌控制和行业场景定制，这是一条差异化路线。',
      '因此它体现了模式识别企业如何在大模型时代重构自己的商业叙事。',
    ],
    products: [
      ['Houndify / Voice AI Platform', '向企业输出语音识别和会话理解能力。'],
      ['Chat AI Automotive', '服务车载场景的语音与多轮对话系统。'],
      ['Smart Ordering', '面向餐饮行业的语音点单与订单自动化。'],
      ['Amelia / 企业 AI Agent', '把语音和客服流程、知识库与自动化接起来。'],
    ],
    spotlightA: {
      title: '焦点产品 A：餐饮语音代理',
      bullets: [
        '餐饮场景看似简单，但真正困难的是高并发、多变口音、菜单变动与订单确认。',
        'SoundHound 把语音识别做成“能接电话、能下单、能改单、能 upsell”的业务代理。',
        '这比单纯识别一句话更难，也更接近真实商业价值。',
        '收购 SYNQ3 后，公司的餐饮语音业务更完整，形成了比较强的场景护城河。'],
      useCases: [
        '电话点单',
        '门店客服',
        '订单修改与推荐',
      ],
    },
    spotlightB: {
      title: '焦点产品 B：汽车与设备端对话系统',
      bullets: [
        '汽车场景是 SoundHound 的传统强项，强调安全、免手操作和品牌定制。',
        '相比通用手机助手，车厂更在意数据控制权与品牌体验，因此白标能力很重要。',
        '在 IoT 与设备端，语音是没有键盘/触屏时最自然的交互方式。',
        '这类场景说明：模式识别企业只要进入产品操作入口，就有机会获得长期收入。'],
      useCases: [
        '车载助手',
        '智能家居设备',
        '品牌化语音入口',
      ],
    },
    stack: [
      ['感知层', '语音识别与声音处理，把连续语音实时转成结构化输入。'],
      ['理解层', 'NLU、知识图谱与复杂查询理解，支持多跳与约束条件。'],
      ['编排层', '把模型输出和菜单、订单、客服流程、企业知识库接通。'],
      ['交付层', '白标部署、品牌控制、多行业模板与 API 接入。'],
    ],
    highlights: [
      '公司强调“speech-to-meaning”，而不是只做转写，这一点非常关键。',
      '创始团队从 2005 年就在做声音识别和语音 AI，积累时间足够长。',
      'SoundHound 通过白标和品牌控制，避免与客户在流量入口上形成直接冲突。',
      '在大模型时代，它把 LLM 当成增强层，而不是把自己完全重做成通用模型公司。',
    ],
    moat: [
      '长年积累的语音与意图理解技术，使其在复杂查询和任务型对话上有差异化。',
      '汽车与餐饮都属于高价值垂直场景，迁移成本高，客户不会频繁更换供应商。',
      '白标模式契合企业客户需求，因为客户希望保留品牌与数据控制权。',
      '收购 Amelia 与 SYNQ3 后，客户触点更广，但也要求更强整合能力。',
    ],
    team: [
      ['Keyvan Mohajer', '联合创始人、CEO', '从一开始就强调“Add Voice AI to everything”的愿景。'],
      ['Andreas Wendel', '联合创始人', '参与技术路线和系统工程建设。'],
      ['Majid Emami', '联合创始人', '与核心团队共同推动早期算法与平台化能力发展。'],
      ['原始创始团队持续在位', '组织特征', '这使公司在长期愿景上保持一致性，但也意味着执行挑战更集中。'],
    ],
    milestones: [
      '2005：创始团队在斯坦福毕业后创立公司。',
      '2009：推出音乐识别应用，累计下载量超过 3 亿次。',
      '2022：通过 SPAC 上市，获得更大资本市场关注。',
      '2024：完成 Amelia 与 SYNQ3 收购，业务从语音平台走向 AI agent。',
    ],
    business: [
      '收入来源包括 royalty、subscription 和 monetization 三类。',
      '客户横跨汽车、IoT、App、餐饮与客服行业。',
      '产品不是单一 API，而是逐步升级为“行业代理 + 工作流自动化”。',
      '这使公司更像垂直 voice AI 平台，而非单纯的语音识别工具商。',
    ],
    opsTitle: '经营与财务观察',
    opsBars: [
      ['2023 收入', 45.9],
      ['2024 收入', 84.7],
      ['2024 毛利润', 41.4],
      ['App 下载（百万）', 300.0],
    ],
    opsMetrics: [
      ['2024 收入', '8469 万美元'],
      ['收入增速', '+85%'],
      ['毛利率', '49%'],
      ['音乐识别 App', '3 亿+ 下载'],
    ],
    opsNotes: [
      '2024 年总收入 8469 万美元，同比增幅 85%。',
      '服务订阅收入显著增长，收购带来了规模提升，但也压低了毛利率。',
      '2024 年毛利率为 49%，低于 2023 年的 75%，说明整合期结构发生变化。',
      '这是成长型 AI 公司常见现象：规模先扩张，效率改善往往稍后体现。',
    ],
    outlook: [
      '语音 AI agent 在客服、餐饮和汽车中仍有较大扩展空间。',
      '如果公司能把收购资产整合成统一产品层，商业故事会更完整。',
      '语音是最自然的交互方式之一，在无屏或弱屏设备里长期重要。',
      '未来最关键的是从“会说话”升级到“真正替用户办事”。',
    ],
    risks: [
      '并购整合复杂，短期内可能拖累毛利率和组织效率。',
      '与大厂语音助手和通用大模型平台存在竞争压力。',
      '汽车客户集中度和长销售周期会使业绩波动较大。',
      'Voice AI 的效果高度依赖真实业务数据和流程接入，落地难度并不低。',
    ],
    insight: [
      'SoundHound 最打动我的地方，是它把模式识别从“识别输入”推进到“完成任务”。',
      '在大模型出现后，语音识别没有失去价值，反而因为交互自然度变得更重要。',
      '但只有把语音和业务流程绑定起来，它才会变成真正可收费的能力。',
      '我认为这家公司代表了语音模式识别的下一阶段：从工具走向 agent。',
    ],
    sourceNote: '来源：SoundHound AI 2024 Form 10-K 及官网公开资料。',
  },
  {
    key: 'facephi',
    name: 'Facephi',
    en: 'Facephi',
    accent: '0F7B83',
    tag: '专注数字身份验证与生物识别，把“识别你是谁”做成跨行业安全基础设施',
    profile: [
      ['成立时间', '2012 年左右，已有 12+ 年投入'],
      ['总部', '西班牙 Alicante'],
      ['模式识别主轴', '人脸/多生物特征识别、活体检测、行为生物识别'],
      ['当前定位', '数字身份验证与反欺诈平台公司'],
    ],
    why: [
      'Facephi 的价值在于，它展示了模式识别如何在身份验证和金融合规中创造真实商业价值。',
      '相比做通用人脸识别，公司更专注于 KYC、AML、远程开户、反欺诈等强约束场景。',
      '这些场景对识别精度、抗攻击性和法规适配要求极高，因此更容易形成专业壁垒。',
      '它也是欧洲语境下一个很有代表性的“隐形冠军”案例。',
    ],
    products: [
      ['Facephi Identity Platform', '统一编排身份验证、认证、合规与多种生物识别能力。'],
      ['Behavioral Biometrics', '通过操作行为、设备行为与交互习惯辅助识别异常与欺诈。'],
      ['IDV Suite', '面向身份核验的完整套件，整合文档识别、人脸采集和活体检测。'],
      ['Teseo Identity Wallet', '面向数字身份证明与可验证凭证的新型身份载体。'],
    ],
    spotlightA: {
      title: '焦点产品 A：Identity Platform',
      bullets: [
        '平台型设计意味着 Facephi 不只是卖单一算法，而是卖“身份流程编排能力”。',
        '这对银行、保险、旅游和政府客户很重要，因为他们面对的法规与国家差异很大。',
        '产品强调模块化，客户可以自由组合人脸、眶周、证件识别和活体检测。',
        '这类平台化思路使其更容易从单点产品走向长期合同与 ARR。'],
      useCases: [
        '远程开户',
        '身份核验与认证',
        '跨行业合规流程',
      ],
    },
    spotlightB: {
      title: '焦点产品 B：Behavioral Biometrics + Liveness',
      bullets: [
        '在身份安全里，“能识别人”还不够，还要识别是不是活人、是不是被冒用、是不是异常行为。',
        '行为生物识别帮助系统识别 mule account、异常操作与可疑交互轨迹。',
        '活体检测和 PAD 能力直接关系到反欺诈效果，是 Facephi 技术含金量最高的部分之一。',
        '这表明现代模式识别已经从静态识别发展到动态风险感知。'],
      useCases: [
        '反伪造与反攻击',
        '账户异常识别',
        '高风险场景多因子校验',
      ],
    },
    stack: [
      ['采集层', '采集面部、证件、设备与行为轨迹信息。'],
      ['识别层', '比对、匹配、眶周识别、OCR、行为特征建模。'],
      ['安全层', '活体检测、PAD、异常行为检测、风险评分。'],
      ['合规层', '面向不同国家/行业的 KYC、AML、隐私与审计要求。'],
    ],
    highlights: [
      'Facephi 的技术重点不是“识别人脸”本身，而是“在安全与合规前提下完成可信身份验证”。',
      '公司在 PAD、活体检测和多生物特征组合上投入较深。',
      'Identity Platform 的模块化结构，说明其路线已经从产品走向平台。',
      '对于模式识别企业来说，安全场景是更能长期收费的垂直赛道。',
    ],
    moat: [
      '进入银行与身份认证流程后，客户替换成本很高。',
      '合规与标准化能力使其更适合跨国家、跨行业复制。',
      '2024 年已覆盖 25+ 国家、350+ 客户、95%+ 留存率，说明业务粘性很强。',
      '300M+ 交易量意味着其算法不是实验室方案，而是被真实世界反复使用。'],
    team: [
      ['Javier Mira', 'CEO / 创业核心代表', '长期围绕数字身份和生物识别推动产品与全球化扩张。'],
      ['创业团队', '早期定位清晰', '从一开始就聚焦身份验证而不是通用视觉，战略很聚焦。'],
      ['国际化子公司体系', '组织特征', '在 APAC、EMEA、LATAM 建立本地触点，是扩张关键。'],
      ['合作伙伴网络', '增长杠杆', '在身份产业中，渠道和标准合作的重要性不亚于算法。'],
    ],
    milestones: [
      '2010s 初：公司创立，进入数字身份与金融安全市场。',
      '随后几年：在银行业建立领先位置，并扩展到保险、旅游和政务。',
      '2024：推出 Behavioral Biometrics、Mule Account Detection 与 IDV Suite。',
      '2025：继续扩展 APAC、EMEA、LATAM 和北美合作网络。',
    ],
    business: [
      '客户主要来自银行、金融服务、保险、旅游、公共服务与数字平台。',
      '商业模式包含 лицензирование、持续服务、平台合同与长期 ARR。',
      '强监管行业天然提高了进入门槛，也提升了客户粘性。',
      'Facephi 的收入质量比很多纯项目型 AI 公司更好，因为续费与长期合同占比更高。',
    ],
    opsTitle: '经营与财务观察',
    opsBars: [
      ['2023 Turnover', 25.1],
      ['2024 Turnover', 28.9],
      ['2024 ARR', 28.0],
      ['2024 TCV', 57.8],
    ],
    opsMetrics: [
      ['2024 Turnover', '2890 万欧元'],
      ['同比增速', '+14.8%'],
      ['2024 ARR', '2800 万欧元'],
      ['客户留存率', '95%+'],
    ],
    opsNotes: [
      '2024 年营收（turnover）达到 2890 万欧元，同比增长 14.8%。',
      'TCV 57.8 百万欧元，ARR 28.0 百万欧元，说明未来可见收入在增强。',
      '公司覆盖 25+ 国家、350+ 客户，累计处理超过 3 亿笔交易。',
      '相较很多 AI 公司，Facephi 的增长更稳，不靠讲大故事，而靠身份验证场景深耕。',
    ],
    outlook: [
      '数字身份、远程开户、反欺诈和数字凭证仍是长期增长赛道。',
      '行为生物识别和身份钱包有望成为公司新的增长点。',
      '欧洲与跨境合规趋势会继续抬升“可信身份基础设施”的价值。',
      '如果 ARR 持续提升，公司的资本市场叙事会更偏 SaaS 与平台型安全企业。',
    ],
    risks: [
      '身份认证属于高合规行业，任何误判或合规事件都可能产生放大影响。',
      '市场规模虽稳，但相较通用 AI 赛道更窄，成长速度可能有限。',
      '国际扩张会面临当地法规、文化和合作伙伴管理问题。',
      '大客户结构若过于集中，也会影响收入稳定性。',
    ],
    insight: [
      'Facephi 给我的启发是：模式识别最有价值的时候，往往不是“看得见”，而是“能被信任”。',
      '身份验证和反欺诈场景天然愿意为精度、鲁棒性与合规买单。',
      '相比追逐大而全的 AI 平台，聚焦一个强刚需环节，有时更容易做出高质量业务。',
      '这家公司说明，小而专的模式识别企业也能建立全球化竞争力。',
    ],
    sourceNote: '来源：Facephi 2024 Audited Financial Results（2025）及官网公开资料。',
  },
];

const introSlides = [
  {
    title: '作业任务拆解',
    subtitle: '把“找 5 家公司 + 100 页 PPT”拆成一个可执行研究框架',
    leftTitle: '这份作业真正考什么',
    leftItems: [
      '不仅要找公司，更要证明这些公司“为什么以模式识别为核心技术”。',
      '不仅要介绍产品，还要解释技术亮点、团队能力、经营状态和未来前景之间的关系。',
      '100 页不是堆页数，而是要求形成“纵向深入 + 横向比较 + 个人判断”的完整研究链。',
      '所以这份 PPT 采用“10 页总论 + 5 家公司 x 16 页 + 10 页总结”的结构。'],
    rightTitle: '我采用的完成方法',
    rightItems: [
      '先定义什么是模式识别及其商业化价值。',
      '再选 5 家不同模态、不同区域、不同商业模型的代表企业。',
      '随后按统一维度展开：产品、技术、团队、经营、前景、启发。',
      '最后做横向比较和个人总结，避免只做百科式介绍。'],
  },
  {
    title: '什么是模式识别',
    subtitle: '模式识别 = 让机器从复杂信号中识别结构、类别、异常与规律',
    leftTitle: '经典理解',
    leftItems: [
      '输入可以是语音、图像、视频、文本、动作轨迹、行为数据，甚至工业传感器信号。',
      '核心任务包括：分类、检测、匹配、分割、检索、异常发现和序列理解。',
      '它既是传统机器学习的重要分支，也是深度学习和多模态 AI 的底层能力。',
      '今天很多“大模型应用”本质上仍然依赖强大的模式识别能力。'],
    rightTitle: '为什么今天还值得研究',
    rightItems: [
      '因为模式识别决定了 AI 是否能“看懂、听懂、认准”。',
      '越是高价值场景，越需要稳定、鲁棒、可规模化的识别能力。',
      '生成式 AI 火了以后，模式识别没有过时，反而在多模态和 agent 里更重要。',
      '很多公司真正的商业护城河，仍然来自他们对真实世界模式的长期积累。'],
  },
  {
    title: '模式识别的技术地图',
    subtitle: '从底层数据到最终商业价值，通常要经历四层跃迁',
    leftTitle: '四层结构',
    leftItems: [
      '数据层：采集、标注、清洗、治理和合规，是一切识别能力的起点。',
      '模型层：特征提取、深度学习、序列建模、多模态融合与推理。',
      '系统层：训练平台、部署框架、边缘设备、工作流编排和监控。',
      '业务层：把识别结果嵌入质检、客服、驾驶、金融安全、教育评估等流程。'],
    rightTitle: '课程汇报最该关注什么',
    rightItems: [
      '不是哪个公司“模型名字更大”，而是哪家公司把技术变成了真实、持续的价值。',
      '真正成功的企业，都在做从“识别能力”到“工作流价值”的迁移。',
      '所以本次案例选择故意覆盖不同模态和行业，看技术如何适应不同商业逻辑。',
      '这也是后面横向比较的核心标准。'],
  },
  {
    title: '为什么现在是重新看模式识别公司的好时点',
    subtitle: '截至 2026 年 3 月，行业已经从“单点识别”走向“识别 + 生成 + 决策”',
    leftTitle: '四个趋势',
    leftItems: [
      '趋势 1：生成式 AI 让识别企业重新获得二次增长机会，多模态成为重点。',
      '趋势 2：企业更愿意为可落地的 workflow AI 付费，而不仅是基础模型能力。',
      '趋势 3：安全、身份、汽车、工业等高门槛场景，仍然偏好专业模式识别公司。',
      '趋势 4：平台化和生态化能力，正在取代单点算法精度成为新的竞争焦点。'],
    rightTitle: '因此我们需要看',
    rightItems: [
      '哪家公司守住了原有识别优势。',
      '哪家公司成功把识别能力平台化。',
      '哪家公司进入了高价值工作流，形成稳定经营能力。',
      '哪家公司具备继续跨周期增长的条件。'],
  },
  {
    title: '选取这 5 家公司的标准',
    subtitle: '不是简单挑名气最大，而是尽量覆盖模式识别商业化的关键类型',
    leftTitle: '筛选标准',
    leftItems: [
      '模式识别必须是公司价值创造中的核心技术，而非边缘功能。',
      '公司最好具有一定全球影响力或明确区域代表性。',
      '需要能获得较完整的官方公开资料，便于分析产品、经营与前景。',
      '五家公司之间要有差异，便于比较不同模式识别路线。'],
    rightTitle: '五类代表方向',
    rightItems: [
      '视觉与多模态平台：SenseTime',
      '语音与行业 AI 平台：iFLYTEK',
      '工业机器视觉：Cognex',
      '语音交互与 AI agent：SoundHound AI',
      '生物识别与数字身份：Facephi'],
  },
  {
    title: '五家公司一页看懂',
    subtitle: '同样是模式识别公司，它们的商业模式和护城河差异很大',
    cards: [
      ['SenseTime', '视觉起家，转向 AI 基础设施和大模型平台。'],
      ['iFLYTEK', '语音识别龙头，靠行业渗透构建平台优势。'],
      ['Cognex', '把机器视觉做到工业基础设施，商业成熟度最高。'],
      ['SoundHound AI', '把语音识别升级成任务型 Voice AI agent。'],
      ['Facephi', '专注数字身份验证，是生物识别安全的专业选手。'],
    ],
  },
  {
    title: '研究方法与资料来源',
    subtitle: '本报告优先使用公司官方公开资料，辅以投资者材料和产品说明',
    leftTitle: '资料来源',
    leftItems: [
      '年度报告、10-K、审计财报、投资者演示材料。',
      '公司官网产品页、管理层介绍、新闻稿与业务案例。',
      '用于佐证的公开搜索结果与行业简报。',
      '所有信息以 2026 年 3 月 29 日之前能查到的公开资料为准。'],
    rightTitle: '分析维度',
    rightItems: [
      '公司画像：定位、模态、产品与客户。',
      '技术画像：识别链路、系统能力、关键亮点。',
      '经营画像：收入结构、增长质量、商业化路径。',
      '判断画像：前景、风险与我自己的启发。'],
  },
  {
    title: '横向比较会重点看什么',
    subtitle: '为了避免五个案例变成五篇平行公司介绍，我先给出比较坐标',
    leftTitle: '比较坐标 A',
    leftItems: [
      '技术起点：视觉、语音、工业视觉、生物识别。',
      '产品化深度：API、平台、系统、行业工作流。',
      '商业模式：项目制、平台订阅、硬件销售、长期合同、生态变现。',
      '组织特性：学术驱动、工程驱动、行业深耕、平台扩张。'],
    rightTitle: '比较坐标 B',
    rightItems: [
      '经营质量：收入增长、现金流、客户粘性和可见收入。',
      '护城河来源：数据、部署、硬件、合规、渠道、生态。',
      '风险类型：重投入、行业周期、并购整合、监管与合规。',
      '长期前景：能否从“识别”走向“工作流价值”。'],
  },
  {
    title: '阅读这份 PPT 的建议',
    subtitle: '100 页内容较长，建议按“总论 -> 单家公司 -> 对比总结”来理解',
    leftTitle: '如果你时间有限',
    leftItems: [
      '先看第 1-10 页，把模式识别和五家公司放到同一张地图上。',
      '每家公司重点看：公司封面页、经营页、风险页、我的启发页。',
      '最后看第 91-100 页的横向比较和结论。'],
    rightTitle: '如果你要做课堂分享',
    rightItems: [
      '可以把每家公司压缩讲 2-3 分钟，突出“模式识别如何创造价值”。',
      '不要平均用力，建议多强调商汤、讯飞和 Cognex 的对比。',
      '横向比较部分最能体现你不是“搜资料”，而是在“做判断”。',
      '最后用个人启发收束，会比单纯念数据更有说服力。'],
  },
];

const comparisonSlides = [
  {
    title: '横向比较 1：五家公司分别代表哪种模式识别路线',
    subtitle: '同是模式识别，底层模态不同，商业逻辑也完全不同',
    leftTitle: '路线图',
    leftItems: [
      'SenseTime：视觉识别 -> 多模态 -> AI 基础设施。',
      'iFLYTEK：语音识别 -> 行业平台 -> 中文大模型。',
      'Cognex：工业视觉 -> 高可靠硬件/软件 -> 制造基础设施。',
      'SoundHound AI：语音识别 -> 会话理解 -> 任务型 agent。',
      'Facephi：生物识别 -> 身份验证 -> 安全与合规平台。'],
    rightTitle: '一句话判断',
    rightItems: [
      '商汤最像“识别资产再平台化”。',
      '讯飞最像“识别能力行业化”。',
      'Cognex 最像“识别能力工业化”。',
      'SoundHound 最像“识别能力 agent 化”。',
      'Facephi 最像“识别能力安全化”。'],
  },
  {
    title: '横向比较 2：产品与交付方式',
    subtitle: '决定公司天花板的，不只是算法，而是客户到底买什么',
    leftTitle: '客户购买对象',
    leftItems: [
      'SenseTime：基础设施、模型服务与行业方案。',
      'iFLYTEK：平台能力、行业解决方案、终端产品。',
      'Cognex：工业设备、软件、系统可靠性。',
      'SoundHound AI：语音平台、垂直 AI 代理与白标服务。',
      'Facephi：身份平台、认证组件与持续服务合同。'],
    rightTitle: '商业含义',
    rightItems: [
      '越靠近工作流，客户越难替换。',
      '越平台化，收入的复用性越强。',
      '越硬件化或合规化，客户验证周期越长，但粘性更高。',
      '真正高质量的模式识别公司，往往不是只卖模型调用。'],
  },
  {
    title: '横向比较 3：技术护城河来源',
    subtitle: '五家公司的护城河并不一样，说明模式识别没有单一成功公式',
    leftTitle: '主要护城河',
    leftItems: [
      'SenseTime：视觉数据、算力平台、行业部署与多模态迁移。',
      'iFLYTEK：中文语音数据、行业场景、开发者生态与本地部署。',
      'Cognex：硬件 + 软件一体化、应用工程经验、品牌与安装基础。',
      'SoundHound AI：复杂语音理解、白标模式、汽车与餐饮场景积累。',
      'Facephi：合规、活体检测、身份流程编排与客户留存。'],
    rightTitle: '共性规律',
    rightItems: [
      '真正耐打的壁垒，通常是“算法 + 系统 + 场景 + 客户关系”的复合结构。',
      '单点模型领先只能维持短期优势，平台和流程接入决定长期优势。',
      '模式识别公司一旦深入高门槛行业，护城河会明显加厚。',
      '因此企业战略的重点，是把技术嵌入更难替代的位置。'],
  },
  {
    title: '横向比较 4：经营成熟度与增长方式',
    subtitle: '并不是规模最大的公司就一定最有前景，也不是最小的就没有价值',
    leftTitle: '成熟度判断',
    leftItems: [
      'Cognex：成熟度最高，增长较稳，利润与现金质量强。',
      'iFLYTEK：规模大、业务广，处于“平台扩张 + 大模型再投入”阶段。',
      'SenseTime：处于战略切换期，增长质量在改善，但仍在证明平台化能力。',
      'SoundHound AI：高成长、高波动，需要观察并购整合后的效率。',
      'Facephi：规模较小但质量较稳，适合看作专业化平台型公司。'],
    rightTitle: '增长方式判断',
    rightItems: [
      '商汤靠新业务替换旧业务。',
      '讯飞靠行业深耕和平台生态放大增长。',
      'Cognex 靠工业升级与产品升级带来稳健增长。',
      'SoundHound AI 靠新场景与收购拉高增长斜率。',
      'Facephi 靠 ARR 和跨行业身份场景扩展增长。'],
  },
  {
    title: '横向比较 5：长期前景谁更值得关注',
    subtitle: '“值得关注”不等于“短期最强”，而是看谁更可能跨越下一个技术周期',
    leftTitle: '更值得长期观察的三类能力',
    leftItems: [
      '能力 1：把识别做成平台，例如商汤、讯飞、Facephi。',
      '能力 2：把识别做成基础设施，例如 Cognex。',
      '能力 3：把识别做成业务代理，例如 SoundHound AI。'],
    rightTitle: '我的判断',
    rightItems: [
      '如果看确定性，Cognex 与 Facephi 的“高门槛场景”更稳。',
      '如果看中国市场平台机会，讯飞与商汤更值得持续跟踪。',
      '如果看新叙事与弹性，SoundHound AI 的 voice agent 值得观察。',
      '五家公司没有简单输赢，关键在于你更看重稳健性、平台性还是成长弹性。'],
  },
  {
    title: '规律总结：模式识别公司成功的 5 个共同点',
    subtitle: '案例不同，但底层规律其实很一致',
    leftTitle: '共同点',
    leftItems: [
      '第一，必须把识别能力嵌入真实工作流，而不是停留在 demo 级展示。',
      '第二，必须有系统化交付能力，让模型能在复杂环境中稳定工作。',
      '第三，必须形成某种不可轻易复制的数据、客户或合规壁垒。',
      '第四，必须找到可持续的商业模式，而不是只依赖融资叙事。',
      '第五，必须能跨越技术代际变化，把旧能力迁移到新框架中。'],
    rightTitle: '为什么这很重要',
    rightItems: [
      '因为模式识别的算法本身会越来越容易被复现。',
      '真正难复制的是“把它长期用好”的系统。',
      '所以未来最强的公司，不一定模型参数最大，而是组织能力最强。',
      '这也是我做完 5 个案例后最核心的体会。'],
  },
  {
    title: '我的总体启发 1：模式识别没有过时，只是换了外壳',
    subtitle: '在多模态和 agent 时代，模式识别反而成为更底层的基础能力',
    leftTitle: '我的判断',
    leftItems: [
      '大模型并没有消灭模式识别，而是在更大系统里重新组织它。',
      '如果模型不会识别、不理解真实世界输入，就无法完成高质量生成与决策。',
      '因此，传统识别公司并非天然落后，关键在于能否升级为平台、系统或 agent。',
      '商汤、讯飞和 SoundHound AI 都体现了这种升级路径。'],
    rightTitle: '对学习的启发',
    rightItems: [
      '学模式识别不能只学分类器和损失函数。',
      '还要理解数据、部署、系统、场景和商业化。',
      '课程里的算法问题，最终都会落到真实世界的工程和组织问题上。',
      '这也是我认为这门课很有价值的原因。'],
  },
  {
    title: '我的总体启发 2：越高价值场景，越欢迎专业模式识别公司',
    subtitle: '工业、金融安全、汽车、教育、医疗，这些地方依然需要专业玩家',
    leftTitle: '为什么',
    leftItems: [
      '因为这些场景不能轻易犯错，错误会带来安全、合规或成本后果。',
      '专业公司往往更懂行业流程、更能适配客户需求，也更愿意承担交付责任。',
      '通用大模型当然重要，但未必能替代所有专业系统。',
      '这也是为什么 Cognex、Facephi 这类公司仍然很有生命力。'],
    rightTitle: '我对未来的看法',
    rightItems: [
      '未来会长期并存两类公司：做通用底座的，以及做高门槛场景的。',
      '后者未必最大，但往往更稳定、更有盈利可能。',
      '如果让我找创业机会，我会更关注“高价值、小切口、强流程依赖”的识别场景。',
      '因为那才是最容易形成真实壁垒的地方。'],
  },
  {
    title: '结论',
    subtitle: '五家公司的共同结论：模式识别最有价值的时候，是它变成“系统能力”的时候',
    leftTitle: '一句话总结五家公司',
    leftItems: [
      'SenseTime：识别资产平台化。',
      'iFLYTEK：识别能力行业化。',
      'Cognex：识别能力工业化。',
      'SoundHound AI：识别能力 agent 化。',
      'Facephi：识别能力安全化。'],
    rightTitle: '我的最终结论',
    rightItems: [
      '模式识别仍然是 AI 产业里最重要的底层能力之一。',
      '真正优秀的公司，都能把“识别”嵌进高价值流程。',
      '未来谁能同时做好技术、系统和场景，谁就更可能跨越下一轮周期。',
      '这也是我完成这份作业后最明确的收获。'],
  },
];

const references = [
  'SenseTime 2024 Annual Report (HKEX, published April 24, 2025)',
  'SenseTime investor relations and official website product/news pages',
  'iFLYTEK 2024 Annual Report (published June 17, 2025)',
  'iFLYTEK official website and developer/open platform materials',
  'Cognex investor relations annual results materials and official product pages',
  'Cognex official company history and product portfolio pages',
  'SoundHound AI Form 10-K for fiscal year 2024',
  'SoundHound AI official website, product pages and leadership materials',
  'Facephi audited financial results for fiscal year 2024 (published April 29, 2025)',
  'Facephi official website product, investors and company overview pages',
  '检索时间：截至 2026-03-29；优先采用企业官方公开资料，少量辅助检索用于校验背景信息',
];

let slideNo = 0;

function addCard(slide, x, y, w, h, fill = C.card, line = C.line) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x,
    y,
    w,
    h,
    radius: 0.08,
    fill: { color: fill },
    line: { color: line, pt: 1 },
  });
}

function addHeader(slide, title, subtitle, accent, sectionLabel) {
  slide.background = { color: C.bg };
  slide.addShape(pptx.ShapeType.rect, {
    x: 0,
    y: 0,
    w: 13.333,
    h: 0.2,
    fill: { color: accent },
    line: { color: accent },
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 0.6,
    y: 0.34,
    w: 1.2,
    h: 0.32,
    radius: 0.06,
    fill: { color: accent },
    line: { color: accent },
  });
  slide.addText(sectionLabel, {
    x: 0.72,
    y: 0.39,
    w: 0.96,
    h: 0.18,
    fontFace: 'Microsoft YaHei',
    fontSize: 10,
    bold: true,
    color: 'FFFFFF',
    align: 'center',
    margin: 0,
  });
  slide.addText(title, {
    x: 0.6,
    y: 0.83,
    w: 10.8,
    h: 0.4,
    fontFace: 'Microsoft YaHei',
    fontSize: 24,
    bold: true,
    color: C.ink,
    margin: 0,
  });
  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.6,
      y: 1.32,
      w: 11.8,
      h: 0.24,
      fontFace: 'Microsoft YaHei',
      fontSize: 10.5,
      color: C.sub,
      margin: 0,
    });
  }
}

function addFooter(slide, accent, sourceNote) {
  slide.addShape(pptx.ShapeType.line, {
    x: 0.6,
    y: 7.02,
    w: 12.1,
    h: 0,
    line: { color: C.line, pt: 1 },
  });
  if (sourceNote) {
    slide.addText(`资料来源：${sourceNote}`, {
      x: 0.62,
      y: 7.08,
      w: 10.4,
      h: 0.18,
      fontFace: 'Microsoft YaHei',
      fontSize: 8.5,
      color: C.sub,
      margin: 0,
    });
  }
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 12.05,
    y: 7.04,
    w: 0.58,
    h: 0.22,
    radius: 0.04,
    fill: { color: accent },
    line: { color: accent },
  });
  slide.addText(String(slideNo), {
    x: 12.16,
    y: 7.08,
    w: 0.36,
    h: 0.12,
    fontFace: 'Microsoft YaHei',
    fontSize: 9,
    bold: true,
    color: 'FFFFFF',
    align: 'center',
    margin: 0,
  });
}

function numbered(items) {
  return items.map((item, idx) => `${idx + 1}. ${item}`).join('\n');
}

function bulletBlock(slide, items, x, y, w, h, fontSize = 15, color = C.ink) {
  slide.addText(numbered(items), {
    x,
    y,
    w,
    h,
    fontFace: 'Microsoft YaHei',
    fontSize,
    color,
    margin: 0.06,
    breakLine: false,
    valign: 'top',
    lineSpacingMultiple: 1.1,
  });
}

function addTwoColumnSlide(config, accent = C.accent, section = '总论', sourceNote = '') {
  const slide = pptx.addSlide();
  slideNo += 1;
  addHeader(slide, config.title, config.subtitle, accent, section);
  addCard(slide, 0.6, 1.62, 6.0, 5.1);
  addCard(slide, 6.75, 1.62, 5.98, 5.1);
  slide.addText(config.leftTitle, {
    x: 0.88, y: 1.84, w: 5.4, h: 0.24,
    fontFace: 'Microsoft YaHei', fontSize: 16.5, bold: true, color: C.ink, margin: 0,
  });
  slide.addText(config.rightTitle, {
    x: 7.03, y: 1.84, w: 5.3, h: 0.24,
    fontFace: 'Microsoft YaHei', fontSize: 16.5, bold: true, color: C.ink, margin: 0,
  });
  bulletBlock(slide, config.leftItems, 0.9, 2.18, 5.35, 4.1, 15);
  bulletBlock(slide, config.rightItems, 7.05, 2.18, 5.25, 4.1, 15);
  addFooter(slide, accent, sourceNote);
  warnIfSlideHasOverlaps(slide, pptx);
  warnIfSlideElementsOutOfBounds(slide, pptx);
}

function addOverviewGridSlide(config) {
  const slide = pptx.addSlide();
  slideNo += 1;
  addHeader(slide, config.title, config.subtitle, C.gold, '总览');
  const positions = [
    [0.7, 1.75, 3.9, 1.45],
    [4.75, 1.75, 3.9, 1.45],
    [8.8, 1.75, 3.9, 1.45],
    [0.7, 3.45, 5.95, 1.65],
    [6.75, 3.45, 5.95, 1.65],
  ];
  config.cards.forEach((card, idx) => {
    const [x, y, w, h] = positions[idx];
    addCard(slide, x, y, w, h, idx % 2 === 0 ? 'FFF8EF' : 'F9F4EC');
    slide.addText(card[0], {
      x: x + 0.2, y: y + 0.16, w: w - 0.4, h: 0.22,
      fontFace: 'Microsoft YaHei', fontSize: 16, bold: true, color: C.ink, margin: 0,
    });
    slide.addText(card[1], {
      x: x + 0.2, y: y + 0.48, w: w - 0.4, h: h - 0.6,
      fontFace: 'Microsoft YaHei', fontSize: 14, color: C.sub, margin: 0.02, valign: 'top',
    });
  });
  addCard(slide, 0.7, 5.45, 12.0, 1.18, 'FDF7EE');
  slide.addText('阅读建议：先把 5 家公司放在同一张地图中，再进入每家公司的 16 页模块，你会更容易看出技术路线和商业逻辑的差异。', {
    x: 0.95, y: 5.82, w: 11.55, h: 0.35,
    fontFace: 'Microsoft YaHei', fontSize: 15, color: C.ink, margin: 0,
  });
  addFooter(slide, C.gold, '综合自各公司官方资料与本报告研究框架。');
  warnIfSlideHasOverlaps(slide, pptx);
  warnIfSlideElementsOutOfBounds(slide, pptx);
}

function addCompanyDivider(company) {
  const slide = pptx.addSlide();
  slideNo += 1;
  slide.background = { color: company.accent };
  slide.addText(company.name, {
    x: 0.9, y: 1.2, w: 7.9, h: 0.7,
    fontFace: 'Microsoft YaHei', fontSize: 30, bold: true, color: 'FFFFFF', margin: 0,
  });
  slide.addText(company.en, {
    x: 0.92, y: 1.95, w: 4.0, h: 0.28,
    fontFace: 'Microsoft YaHei', fontSize: 13, color: 'FFF7ED', margin: 0,
  });
  slide.addText(company.tag, {
    x: 0.92, y: 2.55, w: 6.95, h: 1.1,
    fontFace: 'Microsoft YaHei', fontSize: 20, color: 'FFF7ED', margin: 0.02, valign: 'mid',
  });
  addCard(slide, 9.15, 1.48, 2.65, 2.0, 'FDF7F2', 'F9E7DC');
  slide.addText('本模块结构', {
    x: 9.38, y: 1.75, w: 2.0, h: 0.2,
    fontFace: 'Microsoft YaHei', fontSize: 15, bold: true, color: company.accent, margin: 0,
  });
  slide.addText('1. 产品与技术\n2. 团队与里程碑\n3. 经营与前景\n4. 我的启发', {
    x: 9.38, y: 2.08, w: 1.9, h: 1.1,
    fontFace: 'Microsoft YaHei', fontSize: 13, color: C.ink, margin: 0.02,
  });
  slide.addText('这一部分的目的，不是列百科，而是回答一个问题：这家公司究竟如何把模式识别变成长期价值？', {
    x: 0.92, y: 6.74, w: 9.8, h: 0.18,
    fontFace: 'Microsoft YaHei', fontSize: 9.5, color: 'FFF7ED', margin: 0,
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 12.05, y: 7.03, w: 0.58, h: 0.22,
    radius: 0.04,
    fill: { color: 'FBE7D7' }, line: { color: 'FBE7D7' },
  });
  slide.addText(String(slideNo), {
    x: 12.16, y: 7.08, w: 0.36, h: 0.12,
    fontFace: 'Microsoft YaHei', fontSize: 9, bold: true, color: company.accent, align: 'center', margin: 0,
  });
}

function addProfileSlide(company) {
  const slide = pptx.addSlide();
  slideNo += 1;
  addHeader(slide, `${company.name}：公司画像`, '先看基本面，再理解它为什么被选入本次案例', company.accent, company.en);
  addCard(slide, 0.6, 1.62, 4.15, 5.1);
  addCard(slide, 4.95, 1.62, 7.78, 5.1);
  slide.addText('基础信息', {
    x: 0.88, y: 1.84, w: 2.6, h: 0.22,
    fontFace: 'Microsoft YaHei', fontSize: 16, bold: true, color: C.ink, margin: 0,
  });
  company.profile.forEach((row, idx) => {
    const y = 2.22 + idx * 0.92;
    slide.addText(row[0], {
      x: 0.92, y, w: 1.25, h: 0.18,
      fontFace: 'Microsoft YaHei', fontSize: 12.5, bold: true, color: company.accent, margin: 0,
    });
    slide.addText(row[1], {
      x: 0.92, y: y + 0.22, w: 3.35, h: 0.38,
      fontFace: 'Microsoft YaHei', fontSize: 14.2, color: C.ink, margin: 0,
    });
  });
  slide.addText('为什么它值得放进模式识别作业', {
    x: 5.25, y: 1.84, w: 3.7, h: 0.22,
    fontFace: 'Microsoft YaHei', fontSize: 16, bold: true, color: C.ink, margin: 0,
  });
  bulletBlock(slide, company.why, 5.2, 2.2, 7.0, 4.25, 15);
  addFooter(slide, company.accent, company.sourceNote);
  warnIfSlideHasOverlaps(slide, pptx);
  warnIfSlideElementsOutOfBounds(slide, pptx);
}

function addProductsSlide(company) {
  const slide = pptx.addSlide();
  slideNo += 1;
  addHeader(slide, `${company.name}：产品版图`, '看它卖什么，能快速理解这家公司的商业重心', company.accent, company.en);
  const positions = [
    [0.7, 1.8, 5.85, 2.05],
    [6.75, 1.8, 5.85, 2.05],
    [0.7, 4.1, 5.85, 2.05],
    [6.75, 4.1, 5.85, 2.05],
  ];
  company.products.forEach((item, idx) => {
    const [x, y, w, h] = positions[idx];
    addCard(slide, x, y, w, h, idx % 2 === 0 ? 'FFFBF8' : 'FBF8F4');
    slide.addText(item[0], {
      x: x + 0.22, y: y + 0.18, w: w - 0.44, h: 0.2,
      fontFace: 'Microsoft YaHei', fontSize: 15.5, bold: true, color: company.accent, margin: 0,
    });
    slide.addText(item[1], {
      x: x + 0.22, y: y + 0.52, w: w - 0.44, h: h - 0.68,
      fontFace: 'Microsoft YaHei', fontSize: 13.5, color: C.ink, margin: 0.03, valign: 'top',
    });
  });
  addFooter(slide, company.accent, company.sourceNote);
  warnIfSlideHasOverlaps(slide, pptx);
  warnIfSlideElementsOutOfBounds(slide, pptx);
}

function addSpotlightSlide(company, block, sectionName) {
  const slide = pptx.addSlide();
  slideNo += 1;
  addHeader(slide, `${company.name}：${block.title}`, '把“代表性产品”拆开看，最容易看清技术与商业逻辑', company.accent, sectionName);
  addCard(slide, 0.6, 1.62, 8.25, 5.1);
  addCard(slide, 9.0, 1.62, 3.73, 5.1, 'FFF9F4');
  slide.addText('核心判断', {
    x: 0.9, y: 1.84, w: 2.2, h: 0.22,
    fontFace: 'Microsoft YaHei', fontSize: 16, bold: true, color: C.ink, margin: 0,
  });
  bulletBlock(slide, block.bullets, 0.88, 2.18, 7.55, 4.0, 15);
  slide.addText('典型落地', {
    x: 9.28, y: 1.84, w: 2.1, h: 0.22,
    fontFace: 'Microsoft YaHei', fontSize: 16, bold: true, color: C.ink, margin: 0,
  });
  bulletBlock(slide, block.useCases, 9.22, 2.22, 2.92, 1.7, 14);
  addCard(slide, 9.22, 4.28, 2.3, 1.15, 'F8F2EC');
  slide.addText('一句话评价', {
    x: 9.42, y: 4.52, w: 1.8, h: 0.16,
    fontFace: 'Microsoft YaHei', fontSize: 12.5, bold: true, color: company.accent, margin: 0,
  });
  slide.addText('该产品体现了公司如何把模式识别嵌入高价值流程。', {
    x: 9.38, y: 4.78, w: 1.95, h: 0.42,
    fontFace: 'Microsoft YaHei', fontSize: 11.5, color: C.sub, margin: 0,
  });
  addFooter(slide, company.accent, company.sourceNote);
  warnIfSlideHasOverlaps(slide, pptx);
  warnIfSlideElementsOutOfBounds(slide, pptx);
}

function addStackSlide(company) {
  const slide = pptx.addSlide();
  slideNo += 1;
  addHeader(slide, `${company.name}：技术栈拆解`, '把底层数据、算法、系统和应用放在一张图里理解', company.accent, company.en);
  company.stack.forEach((layer, idx) => {
    const y = 1.86 + idx * 1.15;
    addCard(slide, 1.05, y, 11.2, 0.9, idx % 2 === 0 ? 'FFF9F5' : 'FBF7F2');
    slide.addShape(pptx.ShapeType.roundRect, {
      x: 1.2, y: y + 0.14, w: 1.45, h: 0.28,
      radius: 0.04,
      fill: { color: company.accent },
      line: { color: company.accent },
    });
    slide.addText(layer[0], {
      x: 1.34, y: y + 0.18, w: 1.18, h: 0.14,
      fontFace: 'Microsoft YaHei', fontSize: 11, bold: true, color: 'FFFFFF', margin: 0, align: 'center',
    });
    slide.addText(layer[1], {
      x: 2.95, y: y + 0.16, w: 8.85, h: 0.42,
      fontFace: 'Microsoft YaHei', fontSize: 13.5, color: C.ink, margin: 0,
    });
  });
  addCard(slide, 1.05, 6.52, 11.2, 0.34, 'F7EFE6');
  slide.addText('技术判断：真正重要的不是某一个模型名字，而是公司是否能把底层识别能力稳定地穿透到最终应用层。', {
    x: 1.22, y: 6.6, w: 10.85, h: 0.12,
    fontFace: 'Microsoft YaHei', fontSize: 12, color: C.sub, margin: 0,
  });
  addFooter(slide, company.accent, company.sourceNote);
  warnIfSlideHasOverlaps(slide, pptx);
  warnIfSlideElementsOutOfBounds(slide, pptx);
}

function addHighlightsSlide(company) {
  const slide = pptx.addSlide();
  slideNo += 1;
  addHeader(slide, `${company.name}：技术亮点`, '回答一个问题：这家公司真正“强”在哪里', company.accent, company.en);
  const positions = [
    [0.75, 1.8, 5.95, 1.95],
    [6.75, 1.8, 5.85, 1.95],
    [0.75, 4.02, 5.95, 1.95],
    [6.75, 4.02, 5.85, 1.95],
  ];
  company.highlights.forEach((text, idx) => {
    const [x, y, w, h] = positions[idx];
    addCard(slide, x, y, w, h, idx % 2 === 0 ? 'FFF9F4' : 'FCF7F0');
    slide.addText(`亮点 ${idx + 1}`, {
      x: x + 0.18, y: y + 0.16, w: 1.1, h: 0.16,
      fontFace: 'Microsoft YaHei', fontSize: 11.5, bold: true, color: company.accent, margin: 0,
    });
    slide.addText(text, {
      x: x + 0.18, y: y + 0.48, w: w - 0.36, h: h - 0.68,
      fontFace: 'Microsoft YaHei', fontSize: 13.8, color: C.ink, margin: 0.03,
    });
  });
  addFooter(slide, company.accent, company.sourceNote);
  warnIfSlideHasOverlaps(slide, pptx);
  warnIfSlideElementsOutOfBounds(slide, pptx);
}

function addMoatSlide(company) {
  const slide = pptx.addSlide();
  slideNo += 1;
  addHeader(slide, `${company.name}：数据飞轮与护城河`, '模式识别公司为什么能持续跑出来，关键看壁垒是什么', company.accent, company.en);
  addCard(slide, 0.6, 1.7, 12.15, 4.55);
  bulletBlock(slide, company.moat, 0.95, 2.08, 10.9, 3.35, 15.2);
  slide.addText('核心判断：壁垒来自“技术 + 系统 + 客户嵌入”，不是只来自模型精度。', {
    x: 0.96, y: 6.42, w: 9.25, h: 0.18,
    fontFace: 'Microsoft YaHei', fontSize: 12.5, color: C.sub, margin: 0,
  });
  addFooter(slide, company.accent, company.sourceNote);
  warnIfSlideHasOverlaps(slide, pptx);
  warnIfSlideElementsOutOfBounds(slide, pptx);
}

function addTeamSlide(company) {
  const slide = pptx.addSlide();
  slideNo += 1;
  addHeader(slide, `${company.name}：创业团队与组织特征`, '团队画像经常决定一家公司是“研究型”还是“产品型”', company.accent, company.en);
  const cardW = 2.85;
  company.team.forEach((member, idx) => {
    const x = 0.7 + idx * 3.12;
    addCard(slide, x, 1.85, cardW, 4.75, idx % 2 === 0 ? 'FFFBF8' : 'FBF7F2');
    slide.addText(member[0], {
      x: x + 0.2, y: 2.12, w: 2.2, h: 0.24,
      fontFace: 'Microsoft YaHei', fontSize: 15, bold: true, color: company.accent, margin: 0,
    });
    slide.addText(member[1], {
      x: x + 0.2, y: 2.48, w: 2.2, h: 0.18,
      fontFace: 'Microsoft YaHei', fontSize: 11.5, color: C.sub, margin: 0,
    });
    slide.addText(member[2], {
      x: x + 0.2, y: 2.86, w: 2.35, h: 2.95,
      fontFace: 'Microsoft YaHei', fontSize: 13, color: C.ink, margin: 0.03, valign: 'top',
    });
  });
  addFooter(slide, company.accent, company.sourceNote);
  warnIfSlideHasOverlaps(slide, pptx);
  warnIfSlideElementsOutOfBounds(slide, pptx);
}

function addMilestonesSlide(company) {
  const slide = pptx.addSlide();
  slideNo += 1;
  addHeader(slide, `${company.name}：关键里程碑`, '通过时间线看战略方向是如何变化的', company.accent, company.en);
  slide.addShape(pptx.ShapeType.line, {
    x: 1.0, y: 3.65, w: 11.2, h: 0,
    line: { color: company.accent, pt: 1.4 },
  });
  company.milestones.forEach((item, idx) => {
    const x = 1.1 + idx * 2.25;
    slide.addShape(pptx.ShapeType.ellipse, {
      x, y: 3.42, w: 0.18, h: 0.18,
      fill: { color: company.accent }, line: { color: company.accent },
    });
    addCard(slide, x - 0.5, idx % 2 === 0 ? 1.95 : 4.02, 1.9, 1.25, idx % 2 === 0 ? 'FFF9F4' : 'FBF7F2');
    slide.addText(item, {
      x: x - 0.35, y: idx % 2 === 0 ? 2.15 : 4.22, w: 1.58, h: 0.86,
      fontFace: 'Microsoft YaHei', fontSize: 11.6, color: C.ink, margin: 0.03, valign: 'mid',
    });
  });
  addFooter(slide, company.accent, company.sourceNote);
  warnIfSlideHasOverlaps(slide, pptx);
  warnIfSlideElementsOutOfBounds(slide, pptx);
}

function addBusinessSlide(company) {
  const slide = pptx.addSlide();
  slideNo += 1;
  addHeader(slide, `${company.name}：商业模式与客户结构`, '模式识别的商业价值，最终看客户愿意为什么买单', company.accent, company.en);
  addCard(slide, 0.6, 1.7, 6.0, 3.45);
  addCard(slide, 6.75, 1.7, 5.98, 3.45);
  slide.addText('商业模式', {
    x: 0.88, y: 1.92, w: 2.3, h: 0.2,
    fontFace: 'Microsoft YaHei', fontSize: 16, bold: true, color: C.ink, margin: 0,
  });
  bulletBlock(slide, company.business.slice(0, 2), 0.9, 2.28, 5.2, 2.4, 15);
  slide.addText('客户/场景结构', {
    x: 7.02, y: 1.92, w: 2.6, h: 0.2,
    fontFace: 'Microsoft YaHei', fontSize: 16, bold: true, color: C.ink, margin: 0,
  });
  bulletBlock(slide, company.business.slice(2), 7.05, 2.28, 5.0, 2.4, 15);
  addCard(slide, 0.92, 5.45, 11.45, 0.78, 'F7EFE6');
  slide.addText('商业化判断：模式识别一旦从“功能”升级为“流程入口”，收入稳定性和客户粘性都会明显提升。', {
    x: 1.12, y: 5.7, w: 11.0, h: 0.18,
    fontFace: 'Microsoft YaHei', fontSize: 13.2, color: C.sub, margin: 0,
  });
  addFooter(slide, company.accent, company.sourceNote);
  warnIfSlideHasOverlaps(slide, pptx);
  warnIfSlideElementsOutOfBounds(slide, pptx);
}

function addOpsSlide(company) {
  const slide = pptx.addSlide();
  slideNo += 1;
  addHeader(slide, `${company.name}：${company.opsTitle}`, '不同币种与口径不可直接横比，但可以看增长、结构与经营质量', company.accent, company.en);
  addCard(slide, 0.6, 1.72, 7.2, 4.95);
  addCard(slide, 8.0, 1.72, 4.73, 4.95, 'FFFBF8');
  slide.addText('关键指标示意', {
    x: 0.9, y: 1.94, w: 2.5, h: 0.2,
    fontFace: 'Microsoft YaHei', fontSize: 16, bold: true, color: C.ink, margin: 0,
  });
  const max = Math.max(...company.opsBars.map((item) => item[1]));
  company.opsBars.forEach((row, idx) => {
    const y = 2.38 + idx * 0.83;
    slide.addText(row[0], {
      x: 0.92, y, w: 0.98, h: 0.16,
      fontFace: 'Microsoft YaHei', fontSize: 11.5, color: C.ink, margin: 0,
    });
    slide.addShape(pptx.ShapeType.roundRect, {
      x: 2.0, y: y + 0.04, w: 4.45, h: 0.17,
      radius: 0.03,
      fill: { color: 'EEE7DE' }, line: { color: 'EEE7DE' },
    });
    slide.addShape(pptx.ShapeType.roundRect, {
      x: 2.0, y: y + 0.04, w: 4.45 * (row[1] / max), h: 0.17,
      radius: 0.03,
      fill: { color: company.accent }, line: { color: company.accent },
    });
    slide.addText(String(row[1]), {
      x: 6.7, y: y - 0.02, w: 0.78, h: 0.18,
      fontFace: 'Microsoft YaHei', fontSize: 11.5, color: C.sub, margin: 0, align: 'right',
    });
  });
  company.opsMetrics.forEach((item, idx) => {
    const x = idx % 2 === 0 ? 8.25 : 10.45;
    const y = idx < 2 ? 2.12 : 4.1;
    addCard(slide, x, y, 1.95, 1.55, idx % 2 === 0 ? 'FFF9F4' : 'F9F4EC');
    slide.addText(item[0], {
      x: x + 0.16, y: y + 0.18, w: 1.6, h: 0.16,
      fontFace: 'Microsoft YaHei', fontSize: 11.5, bold: true, color: company.accent, margin: 0,
    });
    slide.addText(item[1], {
      x: x + 0.16, y: y + 0.6, w: 1.6, h: 0.4,
      fontFace: 'Microsoft YaHei', fontSize: 15, bold: true, color: C.ink, margin: 0,
    });
  });
  slide.addText('读数解释', {
    x: 8.25, y: 5.86, w: 1.8, h: 0.16,
    fontFace: 'Microsoft YaHei', fontSize: 13.5, bold: true, color: C.ink, margin: 0,
  });
  bulletBlock(slide, company.opsNotes, 8.22, 6.08, 3.92, 0.92, 9.6);
  addFooter(slide, company.accent, company.sourceNote);
}

function addOutlookSlide(company) {
  const slide = pptx.addSlide();
  slideNo += 1;
  addHeader(slide, `${company.name}：发展前景`, '前景不是看热度，而是看趋势、位置和商业承接能力', company.accent, company.en);
  addCard(slide, 0.75, 1.82, 12.0, 4.45);
  bulletBlock(slide, company.outlook, 1.02, 2.12, 10.95, 3.25, 15.2);
  slide.addText('我的判断：前景取决于公司能否把模式识别升级成更高阶的系统能力。', {
    x: 1.02, y: 6.34, w: 9.4, h: 0.18,
    fontFace: 'Microsoft YaHei', fontSize: 12.8, color: C.sub, margin: 0,
  });
  addFooter(slide, company.accent, company.sourceNote);
  warnIfSlideHasOverlaps(slide, pptx);
  warnIfSlideElementsOutOfBounds(slide, pptx);
}

function addRiskSlide(company) {
  const slide = pptx.addSlide();
  slideNo += 1;
  addHeader(slide, `${company.name}：主要风险与挑战`, '分析风险会让判断更立体，也更像一份真正的研究报告', company.accent, company.en);
  const positions = [
    [0.8, 1.9, 5.85, 1.9],
    [6.7, 1.9, 5.85, 1.9],
    [0.8, 4.1, 5.85, 1.9],
    [6.7, 4.1, 5.85, 1.9],
  ];
  company.risks.forEach((risk, idx) => {
    const [x, y, w, h] = positions[idx];
    addCard(slide, x, y, w, h, idx % 2 === 0 ? 'FFF7F4' : 'FBF6F1');
    slide.addText(`风险 ${idx + 1}`, {
      x: x + 0.18, y: y + 0.14, w: 0.95, h: 0.16,
      fontFace: 'Microsoft YaHei', fontSize: 11.5, bold: true, color: company.accent, margin: 0,
    });
    slide.addText(risk, {
      x: x + 0.18, y: y + 0.46, w: w - 0.36, h: 1.1,
      fontFace: 'Microsoft YaHei', fontSize: 13.4, color: C.ink, margin: 0.03,
    });
  });
  addFooter(slide, company.accent, company.sourceNote);
  warnIfSlideHasOverlaps(slide, pptx);
  warnIfSlideElementsOutOfBounds(slide, pptx);
}

function addInsightSlide(company) {
  const slide = pptx.addSlide();
  slideNo += 1;
  addHeader(slide, `${company.name}：我的启发与小结`, '课程作业的最后一步，是把资料整理成自己的判断', company.accent, company.en);
  addCard(slide, 0.75, 1.85, 12.0, 4.45, 'FFFBF8');
  bulletBlock(slide, company.insight, 1.0, 2.12, 11.0, 3.2, 15.2);
  slide.addText('小结：这家公司最值得学的，是它如何把识别能力变成长期价值。', {
    x: 1.0, y: 6.35, w: 9.25, h: 0.18,
    fontFace: 'Microsoft YaHei', fontSize: 12.5, color: C.sub, margin: 0,
  });
  addFooter(slide, company.accent, company.sourceNote);
  warnIfSlideHasOverlaps(slide, pptx);
  warnIfSlideElementsOutOfBounds(slide, pptx);
}

function addCoverSlide() {
  const slide = pptx.addSlide();
  slideNo += 1;
  slide.background = { color: C.bg };
  slide.addShape(pptx.ShapeType.rect, {
    x: 0, y: 0, w: 13.333, h: 0.22,
    fill: { color: C.gold }, line: { color: C.gold },
  });
  addCard(slide, 0.72, 0.82, 12.0, 5.75, 'FFF9F1', 'EFE2D0');
  slide.addText('全球模式识别公司案例研究', {
    x: 1.02, y: 1.22, w: 7.5, h: 0.52,
    fontFace: 'Microsoft YaHei', fontSize: 30, bold: true, color: C.ink, margin: 0,
  });
  slide.addText('以 SenseTime、iFLYTEK、Cognex、SoundHound AI、Facephi 为例', {
    x: 1.04, y: 1.96, w: 7.45, h: 0.24,
    fontFace: 'Microsoft YaHei', fontSize: 16, color: C.sub, margin: 0,
  });
  slide.addText('课程：模式识别\n目标：围绕 5 家“以模式识别为核心技术”的科技公司，系统分析其产品、技术亮点、创业团队、经营情况、发展前景，并给出个人启发。\n交付：100 页左右课堂分享型 PPT', {
    x: 1.04, y: 2.7, w: 7.0, h: 1.55,
    fontFace: 'Microsoft YaHei', fontSize: 16, color: C.ink, margin: 0.02, valign: 'top',
  });
  addCard(slide, 8.95, 1.28, 2.95, 4.72, 'F8F1E8');
  slide.addText('研究框架', {
    x: 9.2, y: 1.6, w: 2.0, h: 0.2,
    fontFace: 'Microsoft YaHei', fontSize: 15, bold: true, color: C.gold, margin: 0,
  });
  slide.addText('1. 模式识别总论\n2. 五家公司纵向研究\n3. 横向比较\n4. 我的启发与结论', {
    x: 9.2, y: 2.02, w: 2.2, h: 1.4,
    fontFace: 'Microsoft YaHei', fontSize: 14.5, color: C.ink, margin: 0.02,
  });
  slide.addText('资料口径', {
    x: 9.2, y: 4.0, w: 1.4, h: 0.16,
    fontFace: 'Microsoft YaHei', fontSize: 13, bold: true, color: C.gold, margin: 0,
  });
  slide.addText('截至 2026-03-29\n优先采用官方公开资料', {
    x: 9.2, y: 4.3, w: 2.1, h: 0.5,
    fontFace: 'Microsoft YaHei', fontSize: 13, color: C.sub, margin: 0,
  });
  slide.addText('汇报人：Junhao Cheng\n生成方式：PptxGenJS 可编辑源码输出', {
    x: 1.02, y: 6.06, w: 4.1, h: 0.32,
    fontFace: 'Microsoft YaHei', fontSize: 11.5, color: C.sub, margin: 0,
  });
  addFooter(slide, C.gold, '本页为封面；完整引用见第 100 页。');
  warnIfSlideHasOverlaps(slide, pptx);
  warnIfSlideElementsOutOfBounds(slide, pptx);
}

function addReferenceSlide() {
  const slide = pptx.addSlide();
  slideNo += 1;
  addHeader(slide, '参考资料', '本报告优先使用官方公开资料；为便于展示，仅列出核心来源类型', C.gold, '附录');
  addCard(slide, 0.6, 1.72, 12.1, 4.95);
  slide.addText(numbered(references), {
    x: 0.92,
    y: 2.0,
    w: 11.5,
    h: 4.3,
    fontFace: 'Microsoft YaHei',
    fontSize: 13.2,
    color: C.ink,
    margin: 0.03,
    lineSpacingMultiple: 1.05,
  });
  addFooter(slide, C.gold, '如需继续扩展，可在此基础上补充更多案例与图表。');
  warnIfSlideHasOverlaps(slide, pptx);
  warnIfSlideElementsOutOfBounds(slide, pptx);
}

addCoverSlide();
introSlides.forEach((item) => {
  if (item.cards) {
    addOverviewGridSlide(item);
  } else {
    addTwoColumnSlide(item, C.gold, '总论', '综合自各公司官方公开资料与本报告研究框架。');
  }
});

companies.forEach((company) => {
  addCompanyDivider(company);
  addProfileSlide(company);
  addTwoColumnSlide({
    title: `${company.name}：为什么说它的核心技术就是模式识别`,
    subtitle: '这一页的任务是把“公司业务”与“模式识别”严密地连接起来',
    leftTitle: '技术逻辑',
    leftItems: company.why.slice(0, 2),
    rightTitle: '商业逻辑',
    rightItems: company.why.slice(2),
  }, company.accent, company.en, company.sourceNote);
  addProductsSlide(company);
  addSpotlightSlide(company, company.spotlightA, '产品 A');
  addSpotlightSlide(company, company.spotlightB, '产品 B');
  addStackSlide(company);
  addHighlightsSlide(company);
  addMoatSlide(company);
  addTeamSlide(company);
  addMilestonesSlide(company);
  addBusinessSlide(company);
  addOpsSlide(company);
  addOutlookSlide(company);
  addRiskSlide(company);
  addInsightSlide(company);
});

comparisonSlides.forEach((item) => {
  addTwoColumnSlide(item, C.gold, '总结', '综合自五家公司官方公开资料与本报告分析。');
});
addReferenceSlide();

if (slideNo !== 100) {
  throw new Error(`Expected 100 slides, got ${slideNo}`);
}

const outPath = path.join(__dirname, 'output', '模式识别_五家公司案例研究_100页.pptx');
pptx.writeFile({ fileName: outPath }).then(() => {
  console.log(`Generated: ${outPath}`);
});
