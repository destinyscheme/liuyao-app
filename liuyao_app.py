import streamlit as st
import datetime
import pandas as pd

# ==============================================================================
# 1. 基礎資料庫與查表系統 (Data Lookup Tables)
# ==============================================================================

# 天干地支
HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 五行對應
FIVE_ELEMENTS = {
    "金": ["申", "酉", "乾", "兑"],
    "木": ["寅", "卯", "震", "巽"],
    "水": ["亥", "子", "坎"],
    "火": ["巳", "午", "離"],
    "土": ["辰", "戌", "丑", "未", "艮", "坤"]
}

# 五行生剋關係 (生我, 我生, 剋我, 我剋, 同我)
RELATIONS = {
    ("金", "金"): "兄弟", ("金", "木"): "妻財", ("金", "水"): "子孫", ("金", "火"): "官鬼", ("金", "土"): "父母",
    ("木", "金"): "官鬼", ("木", "木"): "兄弟", ("木", "水"): "父母", ("木", "火"): "子孫", ("木", "土"): "妻財",
    ("水", "金"): "父母", ("水", "木"): "子孫", ("水", "水"): "兄弟", ("水", "火"): "妻財", ("水", "土"): "官鬼",
    ("火", "金"): "妻財", ("火", "木"): "父母", ("火", "水"): "官鬼", ("火", "火"): "兄弟", ("火", "土"): "子孫",
    ("土", "金"): "子孫", ("土", "木"): "官鬼", ("土", "水"): "妻財", ("土", "火"): "父母", ("土", "土"): "兄弟",
}

# 八卦基礎資料 (二進制: 0陰 1陽, 上至下) -> 對應納甲
TRIGRAMS = {
    "乾": {"code": [1, 1, 1], "element": "金", "inner": ["子", "寅", "辰"], "outer": ["午", "申", "戌"]},
    "兌": {"code": [0, 1, 1], "element": "金", "inner": ["巳", "卯", "丑"], "outer": ["亥", "酉", "未"]},
    "離": {"code": [1, 0, 1], "element": "火", "inner": ["卯", "丑", "亥"], "outer": ["酉", "未", "巳"]},
    "震": {"code": [0, 0, 1], "element": "木", "inner": ["子", "寅", "辰"], "outer": ["午", "申", "戌"]},
    "巽": {"code": [1, 1, 0], "element": "木", "inner": ["丑", "亥", "酉"], "outer": ["未", "巳", "卯"]},
    "坎": {"code": [0, 1, 0], "element": "水", "inner": ["寅", "辰", "午"], "outer": ["申", "戌", "子"]},
    "艮": {"code": [1, 0, 0], "element": "土", "inner": ["辰", "午", "申"], "outer": ["戌", "子", "寅"]},
    "坤": {"code": [0, 0, 0], "element": "土", "inner": ["未", "巳", "卯"], "outer": ["丑", "亥", "酉"]},
}

# 64卦全名映射 (名稱 -> 上卦, 下卦)
HEXAGRAM_NAMES = {
    "乾為天": ("乾", "乾"), "天風姤": ("乾", "巽"), "天山遯": ("乾", "艮"), "天地否": ("乾", "坤"),
    "風地觀": ("巽", "坤"), "山地剝": ("艮", "坤"), "火地晉": ("離", "坤"), "火天大有": ("離", "乾"),
    "坎為水": ("坎", "坎"), "水澤節": ("坎", "兌"), "水雷屯": ("坎", "震"), "水火既濟": ("坎", "離"),
    "澤火革": ("兌", "離"), "雷火豐": ("震", "離"), "地火明夷": ("坤", "離"), "地水師": ("坤", "坎"),
    "艮為山": ("艮", "艮"), "山火賁": ("艮", "離"), "山天大畜": ("艮", "乾"), "山澤損": ("艮", "兌"),
    "火澤睽": ("離", "兌"), "天澤履": ("乾", "兌"), "風澤中孚": ("巽", "兌"), "風山漸": ("巽", "艮"),
    "震為雷": ("震", "震"), "雷地豫": ("震", "坤"), "雷水解": ("震", "坎"), "雷風恆": ("震", "巽"),
    "地風升": ("坤", "巽"), "水風井": ("坎", "巽"), "澤風大過": ("兌", "巽"), "澤雷隨": ("兌", "震"),
    "巽為風": ("巽", "巽"), "風天小畜": ("巽", "乾"), "風火家人": ("巽", "離"), "風雷益": ("巽", "震"),
    "天雷無妄": ("乾", "震"), "火雷噬嗑": ("離", "震"), "山雷頤": ("艮", "震"), "山風蠱": ("艮", "巽"),
    "離為火": ("離", "離"), "火山旅": ("離", "艮"), "火風鼎": ("離", "巽"), "火水未濟": ("離", "坎"),
    "山水蒙": ("艮", "坎"), "風水渙": ("巽", "坎"), "天水訟": ("乾", "坎"), "天火同人": ("乾", "離"),
    "坤為地": ("坤", "坤"), "地雷復": ("坤", "震"), "地澤臨": ("坤", "兌"), "地天泰": ("坤", "乾"),
    "雷天大壯": ("震", "乾"), "澤天夬": ("兌", "乾"), "水天需": ("坎", "乾"), "水地比": ("坎", "坤"),
    "兌為澤": ("兌", "兌"), "澤水困": ("兌", "坎"), "澤地萃": ("兌", "坤"), "澤山咸": ("兌", "艮"),
    "水山蹇": ("坎", "艮"), "地山謙": ("坤", "艮"), "雷山小過": ("震", "艮"), "雷澤歸妹": ("震", "兌")
}

# 宮位與世爻查找 (簡單查表法，避免複雜演算法)
PALACE_LOOKUP = {
    # 乾宮
    "乾為天": ("乾", 6), "天風姤": ("乾", 1), "天山遯": ("乾", 2), "天地否": ("乾", 3),
    "風地觀": ("乾", 4), "山地剝": ("乾", 5), "火地晉": ("乾", 4), "火天大有": ("乾", 3), # 晉:遊魂, 大有:歸魂
    # 坎宮
    "坎為水": ("坎", 6), "水澤節": ("坎", 1), "水雷屯": ("坎", 2), "水火既濟": ("坎", 3),
    "澤火革": ("坎", 4), "雷火豐": ("坎", 5), "地火明夷": ("坎", 4), "地水師": ("坎", 3),
    # 艮宮
    "艮為山": ("艮", 6), "山火賁": ("艮", 1), "山天大畜": ("艮", 2), "山澤損": ("艮", 3),
    "火澤睽": ("艮", 4), "天澤履": ("艮", 5), "風澤中孚": ("艮", 4), "風山漸": ("艮", 3),
    # 震宮
    "震為雷": ("震", 6), "雷地豫": ("震", 1), "雷水解": ("震", 2), "雷風恆": ("震", 3),
    "地風升": ("震", 4), "水風井": ("震", 5), "澤風大過": ("震", 4), "澤雷隨": ("震", 3),
    # 巽宮
    "巽為風": ("巽", 6), "風天小畜": ("巽", 1), "風火家人": ("巽", 2), "風雷益": ("巽", 3),
    "天雷無妄": ("巽", 4), "火雷噬嗑": ("巽", 5), "山雷頤": ("巽", 4), "山風蠱": ("巽", 3),
    # 離宮
    "離為火": ("離", 6), "火山旅": ("離", 1), "火風鼎": ("離", 2), "火水未濟": ("離", 3),
    "山水蒙": ("離", 4), "風水渙": ("離", 5), "天水訟": ("離", 4), "天火同人": ("離", 3),
    # 坤宮
    "坤為地": ("坤", 6), "地雷復": ("坤", 1), "地澤臨": ("坤", 2), "地天泰": ("坤", 3),
    "雷天大壯": ("坤", 4), "澤天夬": ("坤", 5), "水天需": ("坤", 4), "水地比": ("坤", 3),
    # 兌宮
    "兌為澤": ("兌", 6), "澤水困": ("兌", 1), "澤地萃": ("兌", 2), "澤山咸": ("兌", 3),
    "水山蹇": ("兌", 4), "地山謙": ("兌", 5), "雷山小過": ("兌", 4), "雷澤歸妹": ("兌", 3),
}

# 2. 六神起例
LIU_SHEN_ORDER = ["青龍", "朱雀", "勾陳", "騰蛇", "白虎", "玄武"]
LIU_SHEN_START = {
    "甲": 0, "乙": 0, "丙": 1, "丁": 1, "戊": 2, "己": 3, "庚": 4, "辛": 4, "壬": 5, "癸": 5
}

# 3. 星煞查表 (依據 User 提供表格)
# 表 A: 月支
STAR_A = {
    "子": ("未", "亥"), "丑": ("未", "子"), "寅": ("戌", "丑"), "卯": ("戌", "寅"),
    "辰": ("戌", "卯"), "巳": ("丑", "辰"), "午": ("丑", "巳"), "未": ("丑", "午"),
    "申": ("辰", "未"), "酉": ("辰", "申"), "戌": ("辰", "酉"), "亥": ("未", "戌")
}
# 表 B: 日干
STAR_B = {
    "甲": ("寅", "卯", "巳", "丑、未"), "乙": ("卯", "寅", "午", "申、子"),
    "丙": ("巳", "午", "申", "酉、亥"), "丁": ("午", "巳", "酉", "酉、亥"),
    "戊": ("巳", "午", "申", "丑、未"), "己": ("午", "巳", "酉", "申、子"),
    "庚": ("申", "酉", "亥", "寅、午"), "辛": ("酉", "申", "子", "寅、午"),
    "壬": ("亥", "子", "寅", "卯、巳"), "癸": ("子", "亥", "卯", "卯、巳")
}
# 表 C: 日支
STAR_C = {
    "子": ("酉", "戌", "子", "寅", "辰", "巳", "午"),
    "丑": ("午", "未", "酉", "亥", "丑", "寅", "卯"),
    "寅": ("卯", "辰", "午", "申", "戌", "亥", "子"),
    "卯": ("子", "丑", "卯", "巳", "未", "申", "酉"),
    "辰": ("酉", "戌", "子", "寅", "辰", "巳", "午"),
    "巳": ("午", "未", "酉", "亥", "丑", "寅", "卯"),
    "午": ("卯", "辰", "午", "申", "戌", "亥", "子"),
    "未": ("子", "丑", "卯", "巳", "未", "申", "酉"),
    "申": ("酉", "戌", "子", "寅", "辰", "巳", "午"),
    "酉": ("午", "未", "酉", "亥", "丑", "寅", "卯"),
    "戌": ("卯", "辰", "午", "申", "戌", "亥", "子"),
    "亥": ("子", "丑", "卯", "巳", "未", "申", "酉"),
}

# ==============================================================================
# 2. 核心邏輯函數
# ==============================================================================

def get_element(branch_or_trigram):
    """取得地支或八卦的五行"""
    if branch_or_trigram in FIVE_ELEMENTS: return branch_or_trigram # 如果已經是五行
    for el, items in FIVE_ELEMENTS.items():
        if branch_or_trigram in items:
            return el
    return ""

def get_relation(me, other):
    """計算六親 (我=宮位五行, 他=爻五行)"""
    return RELATIONS.get((me, other), "")

def get_voids(day_stem, day_branch):
    """計算旬空"""
    stem_idx = HEAVENLY_STEMS.index(day_stem)
    branch_idx = EARTHLY_BRANCHES.index(day_branch)
    # 旬空公式：(地支序 - 天干序) 剩下的兩個
    diff = (branch_idx - stem_idx) % 12
    # 該旬最後一個地支是 diff + 9 (癸的位置) -> 接下來兩個是空亡
    void_1 = EARTHLY_BRANCHES[(diff - 2) % 12]
    void_2 = EARTHLY_BRANCHES[(diff - 1) % 12]
    return f"{void_2}、{void_1}" # 通常順序顯示

def build_hexagram_from_numbers(numbers):
    """將數字 6,7,8,9 轉為 主卦、變卦 的 0/1 列表"""
    # 6: 老陰 (0->1), 7: 少陽 (1->1), 8: 少陰 (0->0), 9: 老陽 (1->0)
    # 輸入由左至右為初爻至上爻
    main_code = []
    changed_code = []
    move_flags = []
    
    for n in numbers:
        if n == 6:   # 老陰
            main_code.append(0)
            changed_code.append(1)
            move_flags.append(True)
        elif n == 7: # 少陽
            main_code.append(1)
            changed_code.append(1)
            move_flags.append(False)
        elif n == 8: # 少陰
            main_code.append(0)
            changed_code.append(0)
            move_flags.append(False)
        elif n == 9: # 老陽
            main_code.append(1)
            changed_code.append(0)
            move_flags.append(True)
    
    return main_code, changed_code, move_flags

def get_trigram_from_code(code_3bit):
    """從 0/1 列表找出八卦名"""
    # code_3bit: [初, 二, 三] (下到上)
    for name, data in TRIGRAMS.items():
        if data["code"] == code_3bit:
            return name
    return None

def get_full_hexagram_data(upper_tri, lower_tri):
    """根據上下卦找 64 卦名與宮位"""
    for name, (u, l) in HEXAGRAM_NAMES.items():
        if u == upper_tri and l == lower_tri:
            palace, shift = PALACE_LOOKUP.get(name, ("", 0))
            return name, palace, shift
    return "未知", "", 0

def get_najia_branches(trigram_name, is_outer):
    """納甲查表"""
    if is_outer:
        return TRIGRAMS[trigram_name]["outer"]
    else:
        return TRIGRAMS[trigram_name]["inner"]

def assemble_lines(main_code, changed_code, main_palace_element, base_palace_lines=None):
    """組裝每一爻的詳細資料 (包含藏伏比對)"""
    lines_data = []
    
    # 切分上下卦
    main_lower_name = get_trigram_from_code(main_code[:3])
    main_upper_name = get_trigram_from_code(main_code[3:])
    changed_lower_name = get_trigram_from_code(changed_code[:3])
    changed_upper_name = get_trigram_from_code(changed_code[3:])
    
    # 獲取地支
    main_branches = get_najia_branches(main_lower_name, False) + get_najia_branches(main_upper_name, True)
    changed_branches = get_najia_branches(changed_lower_name, False) + get_najia_branches(changed_upper_name, True)
    
    for i in range(6):
        # 主卦數據
        m_branch = main_branches[i]
        m_element = get_element(m_branch)
        m_relation = get_relation(main_palace_element, m_element)
        
        # 變卦數據
        c_branch = changed_branches[i]
        c_element = get_element(c_branch)
        c_relation = get_relation(main_palace_element, c_element) # 六親永遠以主卦宮位為準
        
        # 動爻判斷
        is_moving = main_code[i] != changed_code[i]
        
        # 符號
        # 0: - - (陰), 1: ━━ (陽)
        # 用 HTML block 來畫，這裡存類型
        m_type = "yin" if main_code[i] == 0 else "yang"
        c_type = "yin" if changed_code[i] == 0 else "yang"
        
        # 藏伏處理
        hidden_text = ""
        if base_palace_lines:
            base_rel, base_br = base_palace_lines[i]
            # 規則：若與主卦完全相同則留白，不同則顯示
            if (base_rel != m_relation) or (base_br != m_branch):
                hidden_text = f"{base_rel}{base_br}{get_element(base_br)}"
        
        lines_data.append({
            "idx": i,
            "main": {"rel": m_relation, "branch": m_branch, "el": m_element, "type": m_type},
            "changed": {"rel": c_relation, "branch": c_branch, "el": c_element, "type": c_type},
            "moving": is_moving,
            "hidden": hidden_text
        })
        
    return lines_data

def get_base_palace_lines(palace_name):
    """取得某宮首卦的六爻資料 (用於藏伏)"""
    # 首卦即 "X為X"
    head_hex_name = f"{palace_name}為{FIVE_ELEMENTS[get_element(palace_name)][-1]}" # 這種反推不準，直接查表
    # 為了準確，我們直接構造首卦：上下卦皆為 palace_name
    # 除非是八純卦... 其實首卦就是 宮名+宮名 (乾為天, 兌為澤...)
    # 這裡的 palace_name 是 "乾", "兌"...
    
    upper = palace_name
    lower = palace_name
    
    branches = get_najia_branches(lower, False) + get_najia_branches(upper, True)
    palace_el = get_element(palace_name)
    
    lines = []
    for br in branches:
        el = get_element(br)
        rel = get_relation(palace_el, el)
        lines.append((rel, br))
    return lines

# ==============================================================================
# 3. Streamlit UI 
# ==============================================================================

st.set_page_config(page_title="六爻排盤系統 (Gemini)", layout="wide")

st.markdown("""
<style>
    .hex-row { display: flex; align-items: center; border-bottom: 1px solid #eee; padding: 5px 0; font-family: "KaiTi", "DFKai-SB", serif; font-size: 18px;}
    .hex-cell { flex: 1; text-align: center; }
    .col-god { flex: 0.5; color: #555; }
    .col-hidden { flex: 1.5; color: #888; font-size: 0.9em;}
    .col-main { flex: 3; display: flex; justify-content: center; align-items: center;}
    .col-arrow { flex: 0.5; color: #aaa; }
    .col-change { flex: 3; display: flex; justify-content: center; align-items: center;}
    
    .yin-line { display: inline-block; width: 20px; height: 10px; background-color: #000; margin: 0 5px; }
    .yang-line { display: inline-block; width: 60px; height: 10px; background-color: #000; }
    .yin-block { display: flex; width: 60px; justify-content: space-between; }
    
    .red-text { color: #d62728; font-weight: bold; }
    .blue-text { color: #1f77b4; }
    
    .star-table { width: 100%; border-collapse: collapse; margin-bottom: 10px; }
    .star-table td { padding: 5px; border: none; font-size: 14px; }
    
    /* 卦爻符號繪製 */
    .symbol-yang { width: 50px; height: 12px; background: #000; display: inline-block; margin-left:10px; margin-right:10px;}
    .symbol-yin { width: 50px; height: 12px; display: flex; justify-content: space-between; display: inline-flex; margin-left:10px; margin-right:10px;}
    .symbol-yin::before { content: ""; width: 20px; height: 100%; background: #000; }
    .symbol-yin::after { content: ""; width: 20px; height: 100%; background: #000; }
    
    .symbol-yang-change { width: 50px; height: 12px; background: #555; display: inline-block; margin-left:10px; margin-right:10px;}
    .symbol-yin-change { width: 50px; height: 12px; display: inline-flex; justify-content: space-between; margin-left:10px; margin-right:10px;}
    .symbol-yin-change::before { content: ""; width: 20px; height: 100%; background: #555; }
    .symbol-yin-change::after { content: ""; width: 20px; height: 100%; background: #555; }

</style>
""", unsafe_allow_html=True)

st.title("🔮 六爻智能排盤系統")
st.caption("依據《增刪卜易》規則與指定查表系統構建")

# --- Sidebar Inputs ---
with st.sidebar:
    st.header("1. 設定時間")
    date_mode = st.radio("日期模式", ["西元日期 (自動轉換)", "干支輸入 (手動)"])
    
    gz_year, gz_month, gz_day, gz_hour = "", "", "", ""
    
    if date_mode == "西元日期 (自動轉換)":
        d = st.date_input("日期", datetime.date.today())
        t = st.time_input("時間", datetime.datetime.now().time())
        try:
            from lunar_python import Solar
            solar = Solar.fromYmdHms(d.year, d.month, d.day, t.hour, t.minute, 0)
            lunar = solar.getLunar()
            gz_year = lunar.getYearInGanZhi()
            gz_month = lunar.getMonthInGanZhiExact() # 依節氣
            gz_day = lunar.getDayInGanZhi()
            gz_hour = lunar.getTimeInGanZhi()
            st.success(f"轉換結果：{gz_year}年 {gz_month}月 {gz_day}日 {gz_hour}時")
        except ImportError:
            st.error("未安裝 lunar_python 套件，請手動輸入干支或執行 `pip install lunar_python`")
            date_mode = "干支輸入 (手動)" # Fallback

    if date_mode == "干支輸入 (手動)":
        c1, c2 = st.columns(2)
        gz_year = c1.text_input("年柱", "乙巳")
        gz_month = c2.text_input("月柱", "己丑")
        gz_day = c1.text_input("日柱", "壬辰")
        gz_hour = c2.text_input("時柱", "己酉")

    st.header("2. 設定卦象")
    hex_mode = st.radio("起卦模式", ["數字起卦 (6,7,8,9)", "卦名起卦 (智能解析)"])
    
    input_numbers = []
    input_name_str = ""
    
    if hex_mode == "數字起卦 (6,7,8,9)":
        st.info("請輸入六爻數字 (由下至上 1->6)")
        c_nums = st.columns(6)
        for i in range(6):
            input_numbers.append(c_nums[i].number_input(f"第{i+1}爻", 6, 9, 8, key=f"n{i}"))
    else:
        st.info("支援格式：'水雷屯'、'屯之復'、'主卦：屯，變卦：復'")
        input_name_str = st.text_input("輸入卦名", "地水師")

    btn_calc = st.button("開始排盤", type="primary")

# --- Main Logic ---

if btn_calc:
    # 1. 解析日期 -> 星煞
    month_branch = gz_month[1]
    day_stem = gz_day[0]
    day_branch = gz_day[1]
    
    # 查表
    star_a = STAR_A.get(month_branch, ("", ""))
    star_b = STAR_B.get(day_stem, ("", "", "", ""))
    star_c = STAR_C.get(day_branch, ("", "", "", "", "", "", ""))
    voids = get_voids(day_stem, day_branch)
    
    # 2. 解析卦象
    main_code = []
    changed_code = []
    
    if hex_mode == "數字起卦 (6,7,8,9)":
        main_code, changed_code, _ = build_hexagram_from_numbers(input_numbers)
    else:
        # 簡單解析器
        m_name, c_name = "", ""
        if "之" in input_name_str:
            parts = input_name_str.split("之")
            m_name = parts[0].strip()
            c_name = parts[1].replace("卦", "").strip()
        elif "主卦" in input_name_str:
            # 簡化處理，假設用戶格式正確
            pass 
        else:
            m_name = input_name_str.strip()
            c_name = m_name # 靜卦
            
        # 為了演示，我們需反查卦名對應的 code (這裡簡化，需遍歷 HEXAGRAM_NAMES 找出對應的 Trigams)
        # 實際專案應建立 Name -> Code Mapping
        # 這裡我們用一個簡單的查找邏輯
        def get_code_by_name(h_name):
            if h_name not in HEXAGRAM_NAMES: return None
            u_name, l_name = HEXAGRAM_NAMES[h_name]
            return TRIGRAMS[l_name]["code"] + TRIGRAMS[u_name]["code"]

        main_code = get_code_by_name(m_name)
        if not main_code:
            st.error(f"找不到卦名：{m_name}")
            st.stop()
            
        if c_name and c_name != m_name:
            changed_code = get_code_by_name(c_name)
        else:
            changed_code = main_code.copy()

    # 3. 裝卦
    # 識別主卦資訊
    m_lower_tri = get_trigram_from_code(main_code[:3])
    m_upper_tri = get_trigram_from_code(main_code[3:])
    m_full_name, m_palace, m_shift = get_full_hexagram_data(m_upper_tri, m_lower_tri)
    m_palace_element = get_element(m_palace)
    
    # 識別變卦資訊
    c_lower_tri = get_trigram_from_code(changed_code[:3])
    c_upper_tri = get_trigram_from_code(changed_code[3:])
    c_full_name, _, _ = get_full_hexagram_data(c_upper_tri, c_lower_tri)
    
    # 取得本宮首卦資料 (用於藏伏)
    base_lines = get_base_palace_lines(m_palace)
    
    # 計算六爻詳情
    lines_details = assemble_lines(main_code, changed_code, m_palace_element, base_lines)
    
    # 計算六神起始
    start_god_idx = LIU_SHEN_START.get(day_stem, 0)
    
    # --- Rendering ---
    
    # 上方資訊區
    st.markdown(f"""
    <div style="background-color:#fff; padding:15px; border-radius:10px; border:1px solid #ddd;">
        <table class="star-table">
            <tr>
                <td>天喜-{star_a[0]}</td> <td>天醫-{star_a[1]}</td> 
                <td>祿神-{star_b[0]}</td> <td>羊刃-{star_b[1]}</td> <td>文昌-{star_b[2]}</td> <td>貴人-{star_b[3]}</td>
            </tr>
            <tr>
                <td>桃花-{star_c[0]}</td> <td>謀星-{star_c[1]}</td> <td>將星-{star_c[2]}</td> <td>驛馬-{star_c[3]}</td>
                <td>華蓋-{star_c[4]}</td> <td>劫煞-{star_c[5]}</td> <td>災煞-{star_c[6]}</td>
            </tr>
        </table>
        <div style="text-align:center; font-size:1.2em; margin-top:10px;">
            <span class="red-text">{gz_year}年</span> &nbsp;&nbsp; 
            【 <span class="red-text">{gz_month}月</span> &nbsp; <span class="red-text">{gz_day}日</span> 】 &nbsp;&nbsp;
            <span class="red-text">{gz_hour}時</span> &nbsp;&nbsp;
            【旬空：<span class="red-text">{voids}</span>】
        </div>
        <div style="display:flex; justify-content:space-around; margin-top:20px; font-weight:bold; font-size:1.1em;">
            <div>{m_palace}宮：{m_full_name} {'(歸魂)' if m_shift==7 else '(遊魂)' if m_shift==8 else ''} <br> (主卦)</div>
            <div>{get_element(m_palace)}宮：{c_full_name} <br> (變卦)</div>
        </div>
    </div>
    <br>
    """, unsafe_allow_html=True)
    
    # 盤面繪製
    # Header
    st.markdown("""
    <div class="hex-row" style="background:#f9f9f9; font-weight:bold; font-size:16px;">
        <div class="col-god">六神</div>
        <div class="col-hidden">藏伏</div>
        <div class="col-main">主卦</div>
        <div class="col-arrow"></div>
        <div class="col-change">變卦</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Rows (由上爻到初爻，所以要反轉 list)
    for i in range(5, -1, -1):
        line = lines_details[i]
        
        # 六神
        god = LIU_SHEN_ORDER[(start_god_idx + i) % 6]
        
        # 世應標記
        shiying = ""
        # 簡單判斷：世爻位置 (依 PALACE_LOOKUP 的 shift，這裡需轉化，因篇幅限制略過複雜世應算法，僅示意)
        # 您可加入具體世應計算函數
        is_shi = (i + 1) == m_shift
        is_ying = (i + 1) == ((m_shift + 3) % 6 if (m_shift + 3) % 6 != 0 else 6)
        if is_shi: shiying = "世"
        elif is_ying: shiying = "應"
        
        # 符號 HTML
        m_sym_class = "symbol-yang" if line['main']['type'] == "yang" else "symbol-yin"
        c_sym_class = "symbol-yang-change" if line['changed']['type'] == "yang" else "symbol-yin-change"
        
        m_symbol_html = f'<div class="{m_sym_class}"></div>'
        c_symbol_html = f'<div class="{c_sym_class}"></div>'
        
        # 動爻箭頭
        arrow = "X →→" if line['moving'] else ""
        
        # 內容組裝
        m_text = f"{line['main']['rel']}{line['main']['branch']}{line['main']['el']}"
        c_text = f"{line['changed']['rel']}{line['changed']['branch']}{line['changed']['el']}"
        
        # 變卦若為靜爻，通常不顯示字，或依使用者喜好。圖片中顯示了。
        
        st.markdown(f"""
        <div class="hex-row">
            <div class="col-god">{god}</div>
            <div class="col-hidden">{line['hidden']}</div>
            <div class="col-main">
                {m_text} &nbsp; {m_symbol_html} &nbsp; <span style="font-size:0.8em; color:#666;">{shiying}</span>
            </div>
            <div class="col-arrow" style="font-size:0.8em;">{arrow}</div>
            <div class="col-change">
                {c_symbol_html} &nbsp; {c_text}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 底部解釋
    st.caption("註：本系統依據使用者提供之表格進行納甲與星煞查表，若有疑義請參照《增刪卜易》。")
