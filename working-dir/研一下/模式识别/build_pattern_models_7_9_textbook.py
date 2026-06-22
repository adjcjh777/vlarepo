from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parent
ASSET_DIR = ROOT / "assets" / "pattern_models_7_12"
OUT_DOCX = ROOT / "模式识别_第7-9模型教材小册子_程俊豪.docx"

BLUE = RGBColor(46, 116, 181)
DARK_BLUE = RGBColor(31, 77, 120)
INK = RGBColor(39, 49, 58)
MUTED = RGBColor(95, 111, 122)
LIGHT_BLUE = "E8EEF5"
LIGHT_GRAY = "F2F4F7"
PALE_YELLOW = "FFF3BF"
PALE_GREEN = "DDF4E8"


def set_run_font(run, size: float | None = None, bold: bool | None = None, color=None) -> None:
    run.font.name = "Calibri"
    run._element.rPr.rFonts.set(qn("w:ascii"), "Calibri")
    run._element.rPr.rFonts.set(qn("w:hAnsi"), "Calibri")
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if color is not None:
        run.font.color.rgb = color


def shade_cell(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=80, start=120, bottom=80, end=120) -> None:
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for m, v in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{m}"))
        if node is None:
            node = OxmlElement(f"w:{m}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(v))
        node.set(qn("w:type"), "dxa")


def set_table_width(table, widths_in: list[float]) -> None:
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    for row in table.rows:
        for cell, width in zip(row.cells, widths_in):
            cell.width = Inches(width)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_margins(cell)


def set_table_borders(table) -> None:
    tbl = table._tbl
    tbl_pr = tbl.tblPr
    borders = tbl_pr.first_child_found_in("w:tblBorders")
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = f"w:{edge}"
        element = borders.find(qn(tag))
        if element is None:
            element = OxmlElement(tag)
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), "6")
        element.set(qn("w:space"), "0")
        element.set(qn("w:color"), "DADCE0")


def style_paragraph(paragraph, before=0, after=6, line=1.25, align=None) -> None:
    fmt = paragraph.paragraph_format
    fmt.space_before = Pt(before)
    fmt.space_after = Pt(after)
    fmt.line_spacing = line
    if align is not None:
        paragraph.alignment = align


def add_para(doc, text: str = "", style: str | None = None, bold_prefix: str | None = None):
    p = doc.add_paragraph(style=style)
    style_paragraph(p)
    if bold_prefix and text.startswith(bold_prefix):
        r = p.add_run(bold_prefix)
        set_run_font(r, bold=True, color=INK)
        rest = p.add_run(text[len(bold_prefix):])
        set_run_font(rest, color=INK)
    else:
        r = p.add_run(text)
        set_run_font(r, color=INK)
    return p


def add_heading(doc, text: str, level: int) -> None:
    p = doc.add_heading(level=level)
    p.text = text
    style_paragraph(p, before=18 if level == 1 else 10, after=8 if level == 1 else 5)
    for run in p.runs:
        set_run_font(run, size={1: 16, 2: 13, 3: 12}.get(level, 11), bold=True, color=BLUE if level < 3 else DARK_BLUE)


def add_bullets(doc, items: list[str]) -> None:
    for item in items:
        p = doc.add_paragraph(style="List Bullet")
        style_paragraph(p, after=4, line=1.25)
        r = p.add_run(item)
        set_run_font(r, color=INK)


def add_numbers(doc, items: list[str]) -> None:
    for item in items:
        p = doc.add_paragraph(style="List Number")
        style_paragraph(p, after=4, line=1.25)
        r = p.add_run(item)
        set_run_font(r, color=INK)


def add_formula(doc, lines: list[str]) -> None:
    table = doc.add_table(rows=len(lines), cols=1)
    set_table_width(table, [6.3])
    set_table_borders(table)
    for row, line in zip(table.rows, lines):
        cell = row.cells[0]
        shade_cell(cell, LIGHT_GRAY)
        p = cell.paragraphs[0]
        style_paragraph(p, before=2, after=2, line=1.15, align=WD_ALIGN_PARAGRAPH.CENTER)
        r = p.add_run(line)
        r.font.name = "Calibri"
        r._element.rPr.rFonts.set(qn("w:ascii"), "Calibri")
        r._element.rPr.rFonts.set(qn("w:hAnsi"), "Calibri")
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
        r.font.size = Pt(12)
        r.font.color.rgb = DARK_BLUE


def add_callout(doc, label: str, text: str, fill: str = LIGHT_BLUE) -> None:
    table = doc.add_table(rows=1, cols=1)
    set_table_width(table, [6.3])
    set_table_borders(table)
    cell = table.cell(0, 0)
    shade_cell(cell, fill)
    p = cell.paragraphs[0]
    style_paragraph(p, before=2, after=2, line=1.2)
    r1 = p.add_run(label + "：")
    set_run_font(r1, bold=True, color=DARK_BLUE)
    r2 = p.add_run(text)
    set_run_font(r2, color=INK)


def add_image(doc, rel_path: str, caption: str) -> None:
    path = ROOT / rel_path
    if not path.exists():
        return
    p = doc.add_paragraph()
    style_paragraph(p, before=6, after=3, align=WD_ALIGN_PARAGRAPH.CENTER)
    run = p.add_run()
    run.add_picture(str(path), width=Cm(14.2))
    c = doc.add_paragraph()
    style_paragraph(c, before=0, after=8, line=1.1, align=WD_ALIGN_PARAGRAPH.CENTER)
    r = c.add_run(caption)
    set_run_font(r, size=9.5, color=MUTED)


def add_simple_table(doc, headers: list[str], rows: list[list[str]], widths: list[float], header_fill: str = LIGHT_BLUE) -> None:
    table = doc.add_table(rows=1, cols=len(headers))
    set_table_width(table, widths)
    set_table_borders(table)
    for cell, header in zip(table.rows[0].cells, headers):
        shade_cell(cell, header_fill)
        p = cell.paragraphs[0]
        style_paragraph(p, after=0, line=1.15, align=WD_ALIGN_PARAGRAPH.CENTER)
        r = p.add_run(header)
        set_run_font(r, bold=True, color=DARK_BLUE)
    for row_data in rows:
        row = table.add_row()
        for cell, value in zip(row.cells, row_data):
            p = cell.paragraphs[0]
            style_paragraph(p, after=0, line=1.15)
            r = p.add_run(value)
            set_run_font(r, size=10, color=INK)
    set_table_width(table, widths)


def setup_doc() -> Document:
    doc = Document()
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    section.header_distance = Inches(0.492)
    section.footer_distance = Inches(0.492)

    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Calibri"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    normal.font.size = Pt(11)
    normal.font.color.rgb = INK
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.25

    for style_name in ("List Bullet", "List Number"):
        st = styles[style_name]
        st.font.name = "Calibri"
        st._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
        st.font.size = Pt(11)
        st.paragraph_format.space_after = Pt(4)
        st.paragraph_format.line_spacing = 1.25

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = footer.add_run("模式识别教材小册子：感知机、GMM、HMM")
    set_run_font(r, size=9, color=MUTED)
    return doc


def add_cover(doc: Document) -> None:
    p = doc.add_paragraph()
    style_paragraph(p, before=30, after=4, align=WD_ALIGN_PARAGRAPH.CENTER)
    r = p.add_run("模式识别经典模型教材小册子")
    set_run_font(r, size=24, bold=True, color=DARK_BLUE)
    p = doc.add_paragraph()
    style_paragraph(p, after=18, align=WD_ALIGN_PARAGRAPH.CENTER)
    r = p.add_run("第 7-9 项：感知机、GMM、HMM")
    set_run_font(r, size=15, color=MUTED)
    add_callout(
        doc,
        "学习目标",
        "本小册子从生活化场景出发，依次讲清三个经典模型的直觉、公式、运行流程、典型应用与局限。读者不需要先背公式，只要先理解每个模型在解决什么问题。",
        PALE_GREEN,
    )
    add_image(doc, "assets/pattern_models_7_12/overview.png", "图 0-1  第 7-12 项模型的三条主线，本小册子聚焦前三个模型。")
    add_simple_table(
        doc,
        ["模型", "一句话理解", "主要任务", "本章重点"],
        [
            ["感知机", "分错就修正的线性分类器", "二分类、线性边界学习", "权重更新与线性可分"],
            ["GMM", "多个高斯团块的概率混合", "软聚类、密度估计", "EM 算法与软归属"],
            ["HMM", "隐藏状态生成观测序列", "序列识别、路径解码", "三组概率与三类问题"],
        ],
        [1.35, 1.85, 1.55, 1.55],
    )
    doc.add_page_break()


def add_reading_guide(doc: Document) -> None:
    add_heading(doc, "0. 阅读导引：先记住三个故事", 1)
    add_para(doc, "模式识别听起来像一门很抽象的课，但这三个模型都可以先从生活故事进入。感知机像拿尺子分水果，GMM 像根据味道猜糖果来自哪台机器，HMM 像根据脚印猜一个人走过哪些房间。")
    add_para(doc, "这三个故事背后，对应的是三种不同的机器学习思路：用边界分开样本，用概率解释数据来源，用时间顺序推断隐藏状态。")
    add_simple_table(
        doc,
        ["故事", "模型", "机器真正学的东西", "一句话记忆"],
        [
            ["尺子分水果", "感知机", "一条能分开两类样本的直线或平面", "分错就把边界挪一挪"],
            ["猜糖果来源", "GMM", "多个概率团块的位置、形状和比例", "一个样本可以像多个群体"],
            ["看脚印猜路线", "HMM", "隐藏状态如何随时间变化并产生观测", "看见表面现象，推测背后路线"],
        ],
        [1.35, 1.0, 2.45, 1.5],
    )
    add_heading(doc, "0.1 本文的公式怎么看", 2)
    add_para(doc, "公式只承担“把故事变成计算规则”的作用。阅读时可以先看公式下面的中文解释，知道每个符号代表什么，再回到公式本身。")
    add_simple_table(
        doc,
        ["符号", "通俗理解", "常见位置"],
        [
            ["x", "一个样本的特征，比如颜色、重量、声音片段", "三个模型都会出现"],
            ["w", "感知机里每个特征的重要程度", "感知机"],
            ["μ、Σ", "GMM 中一个概率团块的中心和形状", "GMM"],
            ["π、a、b", "HMM 的初始概率、转移概率、发射概率", "HMM"],
        ],
        [1.0, 3.65, 1.65],
        PALE_GREEN,
    )
    add_heading(doc, "0.2 学习时可以问自己的三个问题", 2)
    add_numbers(doc, [
        "这个模型把现实问题想象成什么故事？",
        "模型最后学到的是边界、团块，还是状态路线？",
        "如果数据变复杂，这个模型最先暴露的短板是什么？",
    ])
    doc.add_page_break()


def add_perceptron(doc: Document) -> None:
    add_heading(doc, "1. 感知机（Perceptron）", 1)
    add_callout(doc, "一句话定位", "感知机是一种线性二分类模型。它用一条线、一个平面或一个高维超平面把样本分成两类，并在分错样本时调整边界。")
    add_heading(doc, "1.1 核心直觉", 2)
    add_para(doc, "可以把感知机想象成一位刚学会分类的小老师。桌上有苹果和橘子，小老师拿一把尺子在桌面上画线：线左边算苹果，线右边算橘子。如果它把一个苹果分到橘子那边，就把尺子轻轻挪一下；如果把橘子分到苹果那边，也再挪一下。")
    add_para(doc, "所以，感知机最重要的想法很简单：先画一条分界线，错了就改，改到尽量少出错。二维数据中这条界线是一条直线；三维数据中是一个平面；维度更高时叫超平面。")
    add_image(doc, "assets/pattern_models_7_12/perceptron.png", "图 1-1  感知机根据误分类样本调整线性边界。")
    add_para(doc, "如果只记一句话，就是：感知机像一个会改错的分类小老师，分错一次就把线挪一点。")
    add_heading(doc, "1.2 必要公式", 2)
    add_formula(doc, ["s = wᵀx + b", "f(x) = sign(s)", "w ← w + ηyᵢxᵢ，   b ← b + ηyᵢ"])
    add_para(doc, "x 是样本的特征，比如“颜色有多红、重量有多大”；w 表示每个特征有多重要；b 像一个整体门槛；η 决定每次改错时挪多远。公式真正想说的是：机器先打分，再看正负号；如果分错，就按正确方向改一下。")
    add_heading(doc, "1.3 生活例子：水果分类", 2)
    add_para(doc, "假设有一张表，每个水果只记录两个数字：颜色偏红的程度和重量。苹果通常更红一些，橘子通常颜色和重量分布不同。感知机会在这张二维表上画出一条线，线的一边叫“苹果”，另一边叫“橘子”。")
    add_para(doc, "刚开始这条线可能画得很差。只要发现一个苹果被分到了橘子那边，模型就把线往能容纳这个苹果的方向挪一点；如果橘子被分到了苹果那边，就往相反方向挪一点。训练过程就是不断纠正这些小错误。")
    add_heading(doc, "1.4 适合放在课本里的伪代码", 2)
    add_numbers(doc, [
        "准备一批已经标好类别的样本。",
        "先随便给一组权重 w 和偏置 b。",
        "拿一个样本来测试，看看当前模型是否分对。",
        "分对就继续看下一个样本；分错就更新 w 和 b。",
        "重复多轮，直到错误明显减少。",
    ])
    add_heading(doc, "1.5 例题", 2)
    add_para(doc, "例题：小老师一开始完全不会分，设 w=(0,0)，b=0，学习率 η=1。现在来了一个“苹果”样本 x=(2,1)，真实标签 y=+1。小老师分错了，应该怎么改？")
    add_callout(doc, "解答", "更新后 w=(0,0)+1*(+1)*(2,1)=(2,1)，b=0+1*(+1)=1。下一次再遇到这个样本时，s=2*2+1*1+1=6，模型会判为正类。", PALE_YELLOW)
    add_heading(doc, "1.6 更多生活例子", 2)
    add_para(doc, "感知机适合解释那些“差不多能用一条线分开”的问题。它不一定是最强模型，但非常适合帮助读者理解机器如何把经验变成分界线。")
    add_simple_table(
        doc,
        ["场景", "样本特征", "两类标签", "分界线的含义"],
        [
            ["垃圾邮件识别", "促销词数量、可疑链接数量、标题夸张程度", "垃圾邮件 / 正常邮件", "超过某个风险组合就判为垃圾邮件"],
            ["运动项目推荐", "身高、爆发力测试成绩、耐力测试成绩", "适合短跑 / 适合长跑", "不同身体条件对应不同运动方向"],
            ["图书分类", "关键词中科普词比例、故事词比例", "科普书 / 故事书", "关键词组合更偏向哪类书"],
        ],
        [1.15, 2.05, 1.25, 1.85],
    )
    add_heading(doc, "1.7 课堂讲解稿", 2)
    add_para(doc, "讲感知机时，可以先不急着写公式。先让读者在纸上画两堆点，然后尝试画一条直线把它们分开。画错了没有关系，只要看到哪个点被分错，就把线往那个点正确的一边移动。这个过程就是感知机学习的图像化版本。")
    add_para(doc, "等读者接受“线会移动”之后，再引入权重 w 和偏置 b。权重决定线的方向，偏置决定线整体往哪边平移。学习率 η 则像尺子的步长：步长太小，改得慢；步长太大，容易改过头。")
    add_heading(doc, "1.8 常见误区", 2)
    add_bullets(doc, [
        "误区一：感知机什么边界都能学。实际上，单层感知机只能学直线、平面或高维超平面这类线性边界。",
        "误区二：分对训练集就一定能分对新样本。训练集只是一部分例子，新样本可能落在边界附近。",
        "误区三：学习率越大越好。学习率太大时，边界可能来回跳，反而不稳定。",
    ])
    add_heading(doc, "1.9 习题", 2)
    add_bullets(doc, [
        "如果苹果和橘子混成一个圆圈套一个圆圈，一条直线还能分开吗？这能说明感知机的什么局限？",
        "如果每次改错时尺子挪得特别远，可能会发生什么？",
        "把“是否有促销词、是否有可疑链接、邮件长度”当作三个特征，解释每个权重像什么。",
        "在二维平面上画 6 个正类点和 6 个负类点，尝试手动画出一条分界线，并标出最容易被分错的点。",
    ])
    add_heading(doc, "1.10 小实验", 2)
    add_simple_table(
        doc,
        ["实验目标", "数据建议", "操作步骤", "观察指标"],
        [[
            "观察线性边界如何随错误样本移动",
            "二维人工数据，两类点大致可线性分开",
            "用 Python 生成散点；手写感知机更新；每轮画出边界",
            "错误数、边界位置、是否收敛",
        ]],
        [1.2, 1.55, 2.2, 1.4],
        PALE_GREEN,
    )
    add_heading(doc, "1.11 本节小结", 2)
    add_para(doc, "感知机的关键不是复杂公式，而是“分错就修正”。它把模式识别中的分类问题转化为寻找线性边界的问题，是理解神经网络和线性模型的起点。")


def add_gmm(doc: Document) -> None:
    add_heading(doc, "2. 高斯混合模型（GMM）", 1)
    add_callout(doc, "一句话定位", "GMM 认为数据来自多个高斯分布的叠加，每个样本可以用概率方式属于不同成分。")
    add_heading(doc, "2.1 核心直觉", 2)
    add_para(doc, "可以把 GMM 想象成一袋混在一起的糖果。糖果可能来自草莓味机器、葡萄味机器和柠檬味机器。我们现在只看到每颗糖的颜色和味道，不知道它到底是哪台机器做的。GMM 的任务，就是猜“每颗糖更像来自哪台机器”。")
    add_para(doc, "如果一颗糖颜色介于草莓和葡萄之间，GMM 不会粗暴地说它一定是草莓味，而可能说：它 60% 像草莓机器做的，35% 像葡萄机器做的，5% 像柠檬机器做的。这就是软归属。")
    add_image(doc, "assets/pattern_models_7_12/gmm.png", "图 2-1  GMM 用多个椭圆状高斯成分解释数据分布。")
    add_para(doc, "所以，GMM 的重点不是“强行分堆”，而是“带着不确定性分堆”。这很适合真实世界，因为很多东西本来就不是非黑即白。")
    add_heading(doc, "2.2 必要公式", 2)
    add_formula(doc, ["p(x) = pi1·N1(x) + pi2·N2(x) + ... + piK·NK(x)", "责任度 gamma(i,k) = 第 k 个团块的贡献 ÷ 所有团块的总贡献"])
    add_para(doc, "公式里的每个 Nₖ(x) 可以理解为一个“糖果制造机器”对样本 x 的解释能力。μₖ 是这台机器最常做出的典型糖果，Σₖ 描述糖果可能散开的范围和方向，πₖ 表示这台机器在整袋糖果里占多大比例。γᵢₖ 叫责任度，可以理解为“第 k 台机器对第 i 颗糖有多大嫌疑”。")
    add_heading(doc, "2.3 生活例子：商场顾客分群", 2)
    add_para(doc, "商场可以记录顾客的两个数字：一年消费金额和到店次数。直接看散点图时，顾客可能混在一起；GMM 会尝试把他们解释成几个重叠的群体，例如“经常来且消费高的核心顾客”“不常来但偶尔买很多的顾客”“低频低消费的普通顾客”。")
    add_para(doc, "有些顾客落在两个群体之间。GMM 不会强行说他只属于某一类，而是给出一组概率。这样，商场可以对边界顾客采用更柔性的策略，例如既推送高价值商品，也保留普通优惠券。")
    add_heading(doc, "2.4 EM 算法怎么理解", 2)
    add_numbers(doc, ["E 步：根据当前模型，估计每个样本属于每个成分的概率。", "M 步：根据这些概率，重新计算每个成分的位置、形状和权重。", "两步交替进行，模型逐渐贴合数据分布。"])
    add_para(doc, "E 步像是“先猜每颗糖来自哪台机器”；M 步像是“根据这些猜测，重新调整每台机器的典型口味”。一开始可能猜得不准，但反复几轮后，每台机器的位置和范围会越来越合理。")
    add_heading(doc, "2.5 例题", 2)
    add_para(doc, "例题：一颗糖对草莓机器和葡萄机器的责任度分别是 0.75 和 0.25。如果只做硬分类，它会被分到哪一类？如果做软聚类，这两个数字又告诉我们什么？")
    add_callout(doc, "解答", "硬分类会把它分到草莓机器。但软聚类还告诉我们：它不是百分百草莓，也有 25% 像葡萄。这种“不确定性”有时比单纯给一个类别更有用。", PALE_YELLOW)
    add_heading(doc, "2.6 更多生活例子", 2)
    add_para(doc, "GMM 特别适合那些“看起来是一团，其实由多个来源混合而成”的问题。它的优势不是强行贴标签，而是告诉我们一个样本与每个来源的相似程度。")
    add_simple_table(
        doc,
        ["场景", "样本特征", "可能的高斯成分", "GMM 的帮助"],
        [
            ["班级身高分布", "身高、体重", "不同年龄段或不同生长阶段学生", "解释为什么一个班级可能不是单峰分布"],
            ["音乐用户分群", "听歌时长、收藏数量、跳过比例", "深度用户、随听用户、探索型用户", "给边界用户保留多种推荐策略"],
            ["机器异常检测", "温度、振动、噪声", "正常工况、轻微异常、严重异常", "低概率样本可作为预警信号"],
        ],
        [1.15, 1.65, 1.75, 1.95],
    )
    add_heading(doc, "2.7 如何理解 K 的选择", 2)
    add_para(doc, "GMM 需要提前设定成分数 K。K 可以理解为“我们允许模型假设有几台糖果机器”。如果 K 太小，不同来源会被硬塞在一起；如果 K 太大，模型可能把偶然噪声也当成一台新机器。")
    add_para(doc, "实际使用时，可以比较不同 K 下的模型效果，也可以结合业务常识。例如顾客分群不一定越细越好，分得太细反而难以解释和行动。课程学习中，重点是理解 K 影响模型解释方式，而不是记住某一个固定答案。")
    add_heading(doc, "2.8 课堂讲解稿", 2)
    add_para(doc, "讲 GMM 时，可以先让读者观察一张散点图：有些点明显属于左边一团，有些点明显属于右边一团，但中间有一些点很难判断。普通硬分类会强行给这些点贴一个标签，GMM 则会说它同时有几种可能。")
    add_para(doc, "这正是概率模型的价值：它不仅给答案，还表达不确定性。很多真实决策不是“是或不是”，而是“更像哪一种，以及有多像”。")
    add_heading(doc, "2.9 常见误区", 2)
    add_bullets(doc, [
        "误区一：GMM 只是 K-Means 的复杂版本。GMM 的重点是概率解释，能表达一个样本同时像多个群体。",
        "误区二：成分数 K 越大越好。K 太大时，模型可能把噪声也当成独立群体。",
        "误区三：椭圆只是一张图。椭圆背后对应协方差矩阵，表示数据在不同方向上的散开程度。",
    ])
    add_heading(doc, "2.10 习题", 2)
    add_bullets(doc, [
        "如果糖果有三种来源，却只让 GMM 找两个团块，会发生什么？",
        "如果让 GMM 找太多团块，它会不会把一些偶然的小差异也当成一种来源？",
        "如果一颗糖不像任何一台机器做出来的，它为什么可能是异常样本？",
        "举一个现实中的混合分布例子，并说明每个高斯成分可能代表什么人群或状态。",
    ])
    add_heading(doc, "2.11 小实验", 2)
    add_simple_table(
        doc,
        ["实验目标", "数据建议", "操作步骤", "观察指标"],
        [[
            "比较硬聚类与软聚类的差别",
            "二维混合高斯数据，三个不同方向的簇",
            "分别运行 K-Means 与 GaussianMixture；画出簇中心、椭圆和责任度",
            "AIC/BIC、责任度、边界样本归属",
        ]],
        [1.2, 1.55, 2.2, 1.4],
        PALE_GREEN,
    )
    add_heading(doc, "2.12 本节小结", 2)
    add_para(doc, "GMM 的核心价值是用概率方式描述“混合”。它不仅告诉我们样本属于哪个群体，还告诉我们这种判断有多确定。")


def add_hmm(doc: Document) -> None:
    add_heading(doc, "3. 隐马尔可夫模型（HMM）", 1)
    add_callout(doc, "一句话定位", "HMM 用于序列数据。它假设背后存在一串看不见的状态，这些状态按时间变化，并生成我们能观察到的信号。")
    add_heading(doc, "3.1 核心直觉", 2)
    add_para(doc, "可以把 HMM 想象成“看脚印猜路线”的游戏。一个小朋友在几个房间里走来走去，但我们没有看到他本人，只看到了地上的脚印。房间就是隐藏状态，脚印就是观测。我们要根据一串脚印，猜他最可能走过哪些房间。")
    add_para(doc, "很多任务都像这个游戏：语音识别时，我们看见的是声音波形，却想知道背后的音素或词；天气例子里，我们看见某人有没有带伞，却想猜当天是晴天、阴天还是雨天。")
    add_image(doc, "assets/pattern_models_7_12/hmm.png", "图 3-1  HMM 的隐藏状态链与观测序列。")
    add_para(doc, "所以，HMM 的重点是：看见一串表面现象，推测背后一串看不见的状态。")
    add_heading(doc, "3.2 三组关键概率", 2)
    add_formula(doc, ["πᵢ = P(一开始在状态 i)", "aᵢⱼ = P(下一步到状态 j | 当前在状态 i)", "bⱼ(o) = P(看到观测 o | 当前在状态 j)"])
    add_para(doc, "用脚印故事来理解：初始概率表示小朋友一开始在哪个房间的可能性；转移概率表示他从一个房间走到另一个房间的可能性；发射概率表示某个房间留下某种脚印的可能性。")
    add_heading(doc, "3.3 生活例子：天气和带伞", 2)
    add_para(doc, "真实天气可能是晴天、阴天或雨天，但我们不一定直接看到天气记录，只看到一个人连续几天有没有带伞。如果连续三天都带伞，我们会猜这几天可能更容易下雨；如果某天没带伞，我们又会重新调整判断。")
    add_para(doc, "在这个例子中，天气是隐藏状态，带伞与否是观测。HMM 的作用，就是把“连续几天有没有带伞”这串表面现象，变成对“连续几天天气如何”的概率推断。")
    add_heading(doc, "3.4 三个经典问题", 2)
    add_simple_table(
        doc,
        ["问题", "在问什么", "典型算法"],
        [
            ["评估", "给定模型和观测序列，这段观测出现的概率是多少？", "前向算法"],
            ["解码", "给定观测序列，最可能的隐藏状态路径是什么？", "Viterbi 算法"],
            ["学习", "只有观测序列时，如何估计模型参数？", "Baum-Welch 算法"],
        ],
        [1.1, 3.7, 1.5],
    )
    add_heading(doc, "3.5 例题", 2)
    add_para(doc, "例题：在“看脚印猜路线”中，我们看到的序列是：湿脚印、湿脚印、干脚印。请问隐藏状态和观测分别是什么？")
    add_callout(doc, "解答", "观测是我们真正看到的脚印类型，比如湿脚印、干脚印；隐藏状态是小朋友走过的房间，比如水池房、走廊、教室。HMM 想做的事，就是根据脚印序列猜最可能的房间路线。", PALE_YELLOW)
    add_heading(doc, "3.6 更多生活例子", 2)
    add_para(doc, "HMM 适合讲解所有“表面看到一串东西，背后其实有一串状态”的问题。它的价值在于把时间顺序纳入模型，而不是把每个样本孤立地看待。")
    add_simple_table(
        doc,
        ["场景", "观测", "隐藏状态", "HMM 的帮助"],
        [
            ["语音识别", "连续声音特征", "音素或词内部发音阶段", "根据声音序列推断说了什么"],
            ["输入法联想", "已经输入的拼音或字词", "用户想表达的词语序列", "根据上下文猜下一步输入"],
            ["设备故障诊断", "温度、振动、电流变化", "正常、磨损、故障等内部状态", "根据传感器序列提前预警"],
        ],
        [1.15, 1.65, 1.75, 1.95],
    )
    add_heading(doc, "3.7 一个小型状态表", 2)
    add_para(doc, "为了让 HMM 更具体，可以想象一个只有两个隐藏状态的天气模型：晴天和雨天。观测只有两种：带伞和不带伞。模型需要知道三类信息：第一天更可能是什么天气，晴天之后更可能还是晴天还是变成雨天，雨天时带伞的可能性有多大。")
    add_simple_table(
        doc,
        ["项目", "示例数值", "含义"],
        [
            ["初始概率", "晴天 0.6，雨天 0.4", "第一天更可能是晴天"],
            ["转移概率", "晴天后仍晴天 0.7，转雨天 0.3", "天气有连续性，但也可能变化"],
            ["发射概率", "雨天带伞 0.9，晴天带伞 0.2", "不同天气会产生不同观测"],
        ],
        [1.35, 2.2, 2.95],
        PALE_GREEN,
    )
    add_heading(doc, "3.8 课堂讲解稿", 2)
    add_para(doc, "讲 HMM 时，可以先问一个问题：如果只看一个人今天带不带伞，能不能准确知道今天是否下雨？通常不能。但如果连续看很多天，就会得到更多线索。HMM 正是利用这种连续线索来推断隐藏状态。")
    add_para(doc, "它和普通分类器的区别在于，普通分类器常常把每个样本单独判断，而 HMM 会把前后顺序联系起来。前一天是什么状态，会影响后一天的状态；某一天的状态，又会影响那一天能看到什么观测。")
    add_heading(doc, "3.9 常见误区", 2)
    add_bullets(doc, [
        "误区一：隐藏状态等于看不见的标签。更准确地说，隐藏状态是一串随时间变化、并能产生观测的内部过程。",
        "误区二：HMM 只用于天气例子。天气只是入门例子，语音识别、词性标注、手势识别也可以用类似思想理解。",
        "误区三：只看上一个状态永远够用。现实任务可能存在更长的依赖，这也是 HMM 的重要局限。",
    ])
    add_heading(doc, "3.10 习题", 2)
    add_bullets(doc, [
        "在天气和带伞例子里，哪个是隐藏状态？哪个是观测？",
        "为什么只看今天有没有带伞，可能还不如看连续三天有没有带伞？",
        "如果小朋友可能记得很久以前走过哪里，只看上一个房间会不会太简单？这说明 HMM 有什么局限？",
        "给出一个你熟悉的序列任务，分别写出它的隐藏状态和观测。",
    ])
    add_heading(doc, "3.11 小实验", 2)
    add_simple_table(
        doc,
        ["实验目标", "数据建议", "操作步骤", "观察指标"],
        [[
            "用 Viterbi 解码最可能状态路径",
            "手工构造天气状态和带伞观测序列",
            "设置初始、转移、发射概率；输入观测序列；输出最可能天气序列",
            "路径概率、预测状态、与直觉是否一致",
        ]],
        [1.2, 1.55, 2.2, 1.4],
        PALE_GREEN,
    )
    add_heading(doc, "3.12 本节小结", 2)
    add_para(doc, "HMM 把序列识别拆成“隐藏状态”和“可见观测”。看懂这两层结构，就能理解它为什么适合处理语音、文本、动作和故障这类随时间展开的问题。")


def add_comparison_and_refs(doc: Document) -> None:
    add_heading(doc, "4. 三个模型的横向比较", 1)
    add_simple_table(
        doc,
        ["模型", "类型", "核心思想", "适合问题", "主要局限"],
        [
            ["感知机", "判别式线性分类", "分错就修正边界", "线性二分类、神经网络入门", "只能表达线性边界"],
            ["GMM", "生成式概率模型", "多个概率团块混合产生数据", "软聚类、密度估计、异常检测", "需指定成分数，对初始化敏感"],
            ["HMM", "序列概率模型", "隐藏状态按时间生成观测", "语音、文本、动作、故障序列", "难表达长期依赖"],
        ],
        [1.0, 1.2, 1.7, 1.45, 1.35],
    )
    add_para(doc, "这三个模型分别代表三种思路：感知机关注分类边界，GMM 关注概率分布的混合，HMM 关注序列背后的状态变化。它们已经不是所有工业任务中的最前沿工具，但仍然是理解现代机器学习的重要地基。")
    add_heading(doc, "5. 如何选择模型", 1)
    add_para(doc, "学习模型时，很容易把注意力放在名字和公式上。但真正做题或做项目时，更重要的是先判断问题属于哪一类。下面的判断顺序可以帮助读者快速选择合适的思路。")
    add_numbers(doc, [
        "如果目标是把样本分成两类，并且用一条线大致能分开，可以先想到感知机。",
        "如果数据看起来由多个群体混合而成，并且希望保留不确定性，可以先想到 GMM。",
        "如果样本按时间排列，前后顺序很重要，而且背后有看不见的状态，可以先想到 HMM。",
        "如果三个条件都不明显，先画图、看数据结构，再决定模型。",
    ])
    add_simple_table(
        doc,
        ["提问方式", "优先考虑", "理由"],
        [
            ["能不能画一条边界分开？", "感知机", "它直接学习分类边界"],
            ["是不是多个来源混在一起？", "GMM", "它解释数据来自多个概率团块"],
            ["是不是一串连续过程？", "HMM", "它利用状态转移和观测序列"],
        ],
        [2.4, 1.3, 2.8],
        PALE_GREEN,
    )
    add_heading(doc, "6. 一页式学习路线", 1)
    add_para(doc, "第一次学习时，可以按“故事、图像、公式、例题、实验”的顺序走。这个顺序比直接背定义更稳，因为每一步都在回答一个具体问题。")
    add_simple_table(
        doc,
        ["步骤", "要做什么", "完成标志"],
        [
            ["故事", "用生活例子解释模型", "不用公式也能说出模型在做什么"],
            ["图像", "看边界、椭圆、状态链", "能指出图中每个部分代表什么"],
            ["公式", "只记必要公式", "能解释符号含义，不机械背诵"],
            ["例题", "手算或口头推理一次", "能把模型步骤讲完整"],
            ["实验", "用小数据跑一遍", "能观察模型输出和局限"],
        ],
        [0.9, 2.7, 2.9],
    )
    add_heading(doc, "7. 综合复习题", 1)
    add_numbers(doc, [
        "比较感知机与 GMM：一个为什么叫判别式模型，另一个为什么叫生成式模型？",
        "如果一个任务既有类别标签，又希望解释数据来源的不确定性，应该优先考虑哪类思想？",
        "请举一个 HMM 比普通分类器更合适的任务，并说明原因。",
        "任选一个模型，说明它在现代深度学习系统中仍然保留的思想价值。",
        "把一个“学生成绩分析”问题分别改写成感知机、GMM、HMM 可以处理的版本。",
    ])
    add_heading(doc, "8. 参考答案提示", 1)
    add_para(doc, "下面不是唯一答案，而是帮助检查理解方向是否正确。只要解释能够自洽，并且能对应模型思想，就可以认为掌握了核心内容。")
    add_simple_table(
        doc,
        ["题目", "答题要点"],
        [
            ["感知机与 GMM 的区别", "感知机直接学分类边界，关心如何判别；GMM 假设数据由多个分布产生，关心数据来源和概率。"],
            ["不确定性任务", "优先考虑概率模型，如 GMM，因为它能输出软归属，而不是只给硬标签。"],
            ["HMM 的适用性", "只要任务有时间顺序、隐藏状态和观测序列，就比孤立分类更适合 HMM 思路。"],
            ["学生成绩分析", "感知机可判断及格/不及格；GMM 可发现学习群体；HMM 可描述一学期学习状态变化。"],
        ],
        [1.65, 4.85],
        PALE_YELLOW,
    )
    add_heading(doc, "9. 学习小结", 1)
    add_bullets(doc, [
        "感知机像一把会调整位置的直尺，适合学习清楚的分类边界。",
        "GMM 像几台不同口味的糖果制造机共同解释数据，适合处理来源不唯一、边界不清楚的问题。",
        "HMM 像根据脚印猜路线，适合处理有时间顺序、背后状态看不见的问题。",
        "学习这三个模型时，可以先问三个问题：样本有没有标签，类别边界清不清楚，数据有没有先后顺序。",
        "真正理解模型，不只是记住公式，而是能把生活问题翻译成模型能处理的语言。",
    ])
    add_heading(doc, "10. 参考文献与延伸阅读", 1)
    add_numbers(doc, [
        "Richard O. Duda, Peter E. Hart, David G. Stork. Pattern Classification.",
        "Christopher M. Bishop. Pattern Recognition and Machine Learning.",
        "Tom M. Mitchell. Machine Learning.",
        "Kevin P. Murphy. Machine Learning: A Probabilistic Perspective.",
        "Lawrence R. Rabiner. A Tutorial on Hidden Markov Models and Selected Applications in Speech Recognition.",
        "scikit-learn User Guide: Perceptron, Gaussian Mixture Models, and model evaluation examples.",
    ])


def main() -> None:
    doc = setup_doc()
    add_cover(doc)
    add_reading_guide(doc)
    add_perceptron(doc)
    add_gmm(doc)
    add_hmm(doc)
    add_comparison_and_refs(doc)
    doc.save(OUT_DOCX)
    print(OUT_DOCX)


if __name__ == "__main__":
    main()
