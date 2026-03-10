import streamlit as st
import datetime
import random
import pandas as pd
from lunar_python import Solar, Lunar

# ==============================================================================
# 0. 網頁設定 & CSS (視覺優化：外框保留，內框全除)
# ==============================================================================
st.set_page_config(page_title="六爻排盤", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@500;700&display=swap');

/* 全域設定：白底黑字 */
body, html, .stApp { 
    font-family: "KaiTi", "DFKai-SB", "Noto Serif TC", serif !important; 
    background-color: #ffffff !important;
    color: #000000 !important;
}

/* 輸入框強制白底黑字 */
div[data-baseweb="input"] > div {
    background-color: #ffffff !important;
    border-color: #000000 !important;
    border-radius: 0px !important;
}
input.st-ai, input.st-ah, input {
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
    background-color: #ffffff !important;
    caret-color: #000000 !important;
}
label[data-baseweb="label"] {
    color: #000000 !important;
}

/* 按鈕設定 (紅底白字) */
div.stButton > button {
    background-color: #d32f2f !important; /* 紅色背景 */
    color: #ffffff !important;             /* 白色文字 */
    border: 1px solid #d32f2f !important;
    border-radius: 0px !important;
    font-weight: bold !important;
    width: 100%;
    margin-bottom: 20px;
}
div.stButton > button:hover {
    background-color: #b71c1c !important; /* 滑鼠懸停時更深紅 */
    color: #ffffff !important;
}

/* 表格樣式：保留外框，刪除所有內框 */
.hex-table { 
    width: 100%; 
    border-collapse: collapse; 
    text-align: center; 
    font-size: 18px; 
    table-layout: fixed; 
    border: 2px solid #000 !important; /* 保留最外層邊框 */
    margin-top: 10px;
}

.hex-table td { 
    padding: 8px 2px;
    border: none !important; /* 移除所有儲存格的邊框 */
    vertical-align: middle; 
    color: #000; 
}

/* 標題列樣式 */
.header-row td { 
    background-color: #ffffff; 
    font-weight: bold; 
    color: #000; 
    border-bottom: none !important;
    padding-bottom: 10px;
    vertical-align: bottom !important;
}

/* 輔助類別 */
.td-main { border-right: none !important; }
.td-arrow { border-left: none !important; border-right: none !important; }
.td-change { border-left: none !important; }

/* 爻條樣式 */
.bar-yang { display: inline-block; width: 100px; height: 14px; background-color: #000; }
.bar-yin { display: inline-flex; width: 100px; height: 14px; justify-content: space-between; }
.bar-yin::before, .bar-yin::after { content: ""; width: 42px; height: 100%; background-color: #000; }

.bar-yang-c { background-color: #000; }
.bar-yin-c::before, .bar-yin-c::after { background-color: #000; }

/* 資訊區塊 */
.info-box { border: 1px solid #000; padding: 15px; margin-bottom: 10px; background-color: #fff; line-height: 1.6; }
.attr-tag { font-size: 0.7em; border: 1px solid #000; padding: 1px 4px; margin-left: 5px; font-weight: normal; }
.hex-title-text { font-size: 1.1em; display: block; margin-bottom: 5px; }

</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 1. 核心資料庫
# ==============================================================================

HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

LIU_SHEN_ORDER = ["青龍", "朱雀", "勾陳", "騰蛇", "白虎", "玄武"]
LIU_SHEN_START = {
    "甲": 0, "乙": 0, "丙": 1, "丁": 1, "戊": 2, 
    "己": 3, "庚": 4, "辛": 4, "壬": 5, "癸": 5
}

NAYIN_TABLE = {
    "甲子": "海中金", "乙丑": "海中金", "丙寅": "爐中火", "丁卯": "爐中火", "戊辰": "大林木", "己巳": "大林木", 
    "庚午": "路旁土", "辛未": "路旁土", "壬申": "劍鋒金", "癸酉": "劍鋒金", "甲戌": "山頭火", "乙亥": "山頭火",
    "丙子": "澗下水", "丁丑": "澗下水", "戊寅": "城頭土", "己卯": "城頭土", "庚辰": "白蠟金", "辛巳": "白蠟金", 
    "壬午": "楊柳木", "癸未": "楊柳木", "甲申": "井泉水", "乙酉": "井泉水", "丙戌": "屋上土", "丁亥": "屋上土",
    "戊子": "霹靂火", "己丑": "霹靂火", "庚寅": "松柏木", "辛卯": "松柏木", "壬辰": "長流水", "癸巳": "長流水", 
    "甲午": "沙中金", "乙未": "沙中金", "丙申": "山下火", "丁酉": "山下火", "戊戌": "平地木", "己亥": "平地木",
    "庚子": "壁上土", "辛丑": "壁上土", "壬寅": "金箔金", "癸卯": "金箔金", "甲辰": "佛燈火", "乙巳": "佛燈火", 
    "丙午": "天河水", "丁未": "天河水", "戊申": "大驛土", "己酉": "大驛土", "庚戌": "釵釧金", "辛亥": "釵釧金",
    "壬子": "桑柘木", "癸丑": "桑柘木", "甲寅": "大溪水", "乙卯": "大溪水", "丙辰": "沙中土", "丁巳": "沙中土", 
    "戊午": "天上火", "己未": "天上火", "庚申": "石榴木", "辛酉": "石榴木", "壬戌": "大海水", "癸亥": "大海水"
}

TRIGRAMS = {
    "乾": {"code": [1, 1, 1], "element": "金", "stems": ["甲", "壬"], "branches": ["子", "寅", "辰", "午", "申", "戌"]},
    "兌": {"code": [1, 1, 0], "element": "金", "stems": ["丁", "丁"], "branches": ["巳", "卯", "丑", "亥", "酉", "未"]}, 
    "離": {"code": [1, 0, 1], "element": "火", "stems": ["己", "己"], "branches": ["卯", "丑", "亥", "酉", "未", "巳"]},
    "震": {"code": [1, 0, 0], "element": "木", "stems": ["庚", "庚"], "branches": ["子", "寅", "辰", "午", "申", "戌"]}, 
    "巽": {"code": [0, 1, 1], "element": "木", "stems": ["辛", "辛"], "branches": ["丑", "亥", "酉", "未", "巳", "卯"]}, 
    "坎": {"code": [0, 1, 0], "element": "水", "stems": ["戊", "戊"], "branches": ["寅", "辰", "午", "申", "戌", "子"]},
    "艮": {"code": [0, 0, 1], "element": "土", "stems": ["丙", "丙"], "branches": ["辰", "午", "申", "戌", "子", "寅"]}, 
    "坤": {"code": [0, 0, 0], "element": "土", "stems": ["乙", "癸"], "branches": ["未", "巳", "卯", "丑", "亥", "酉"]},
}

HEX_INFO = {
    "乾為天": ("乾", 6), "天風姤": ("乾", 1), "天山遯": ("乾", 2), "天地否": ("乾", 3), "風地觀": ("乾", 4), "山地剝": ("乾", 5), "火地晉": ("乾", 7), "火天大有": ("乾", 8),
    "坎為水": ("坎", 6), "水澤節": ("坎", 1), "水雷屯": ("坎", 2), "水火既濟": ("坎", 3), "澤火革": ("坎", 4), "雷火豐": ("坎", 5), "地火明夷": ("坎", 7), "地水師": ("坎", 8),
    "艮為山": ("艮", 6), "山火賁": ("艮", 1), "山天大畜": ("艮", 2), "山澤損": ("艮", 3), "火澤睽": ("艮", 4), "天澤履": ("艮", 5), "風澤中孚": ("艮", 7), "風山漸": ("艮", 8),
    "震為雷": ("震", 6), "雷地豫": ("震", 1), "雷水解": ("震", 2), "雷風恆": ("震", 3), "地風升": ("震", 4), "水風井": ("震", 5), "澤風大過": ("震", 7), "澤雷隨": ("震", 8),
    "巽為風": ("巽", 6), "風天小畜": ("巽", 1), "風火家人": ("巽", 2), "風雷益": ("巽", 3), "天雷無妄": ("巽", 4), "火雷噬嗑": ("巽", 5), "山雷頤": ("巽", 7), "山風蠱": ("巽", 8),
    "離為火": ("離", 6), "火山旅": ("離", 1), "火風鼎": ("離", 2), "火水未濟": ("離", 3), "山水蒙": ("離", 4), "風水渙": ("離", 5), "天水訟": ("離", 7), "天火同人": ("離", 8),
    "坤為地": ("坤", 6), "地雷復": ("坤", 1), "地澤臨": ("坤", 2), "地天泰": ("坤", 3), "雷天大壯": ("坤", 4), "澤天夬": ("坤", 5), "水天需": ("坤", 7), "水地比": ("坤", 8),
    "兌為澤": ("兌", 6), "澤水困": ("兌", 1), "澤地萃": ("兌", 2), "澤山咸": ("兌", 3), "水山蹇": ("兌", 4), "地山謙": ("兌", 5), "雷山小過": ("兌", 7), "雷澤歸妹": ("兌", 8),
}

SHORT_NAME_MAP = {}
FULL_TO_SHORT_MAP = {}

for full_name in HEX_INFO.keys():
    if "為" in full_name:
        short_name = full_name[0]
    elif len(full_name) == 4:
        short_name = full_name[-2:]
    else:
        short_name = full_name[-1]
    
    SHORT_NAME_MAP[short_name] = full_name
    SHORT_NAME_MAP[full_name] = full_name
    FULL_TO_SHORT_MAP[full_name] = short_name

STAR_A_TABLE = {"子": ("未", "亥"), "丑": ("未", "子"), "寅": ("戌", "丑"), "卯": ("戌", "寅"), "辰": ("戌", "卯"), "巳": ("丑", "辰"), "午": ("丑", "巳"), "未": ("丑", "午"), "申": ("辰", "未"), "酉": ("辰", "申"), "戌": ("辰", "酉"), "亥": ("未", "戌")}
STAR_B_TABLE = {"甲": ("寅", "卯", "巳", "丑、未"), "乙": ("卯", "寅", "午", "申、子"), "丙": ("巳", "午", "申", "酉、亥"), "丁": ("午", "巳", "酉", "酉、亥"), "戊": ("巳", "午", "申", "丑、未"), "己": ("午", "巳", "酉", "申、子"), "庚": ("申", "酉", "亥", "寅、午"), "辛": ("酉", "申", "子", "寅、午"), "壬": ("亥", "子", "寅", "卯、巳"), "癸": ("子", "亥", "卯", "卯、巳")}
STAR_C_TABLE = {"子": ("酉", "戌", "子", "寅", "辰", "巳", "午"), "丑": ("午", "未", "酉", "亥", "丑", "寅", "卯"), "寅": ("卯", "辰", "午", "申", "戌", "亥", "子"), "卯": ("子", "丑", "卯", "巳", "未", "申", "酉"), "辰": ("酉", "戌", "子", "寅", "辰", "巳", "午"), "巳": ("午", "未", "酉", "亥", "丑", "寅", "卯"), "午": ("卯", "辰", "午", "申", "戌", "亥", "子"), "未": ("子", "丑", "卯", "巳", "未", "申", "酉"), "申": ("酉", "戌", "子", "寅", "辰", "巳", "午"), "酉": ("午", "未", "酉", "亥", "丑", "寅", "卯"), "戌": ("卯", "辰", "午", "申", "戌", "亥", "子"), "亥": ("子", "丑", "卯", "巳", "未", "申", "酉")}

SIX_CLASH_HEX = ["乾為天", "坎為水", "艮為山", "震為雷", "巽為風", "離為火", "坤為地", "兌為澤", "天雷無妄", "雷天大壯"]
SIX_HARMONY_HEX = ["天地否", "地天泰", "地雷復", "雷地豫", "水澤節", "澤水困", "山火賁", "火山旅"]

ELEMENT_RELATIONS = {
    ("金", "金"): "兄弟", ("金", "木"): "妻財", ("金", "水"): "子孫", ("金", "火"): "官鬼", ("金", "土"): "父母",
    ("木", "金"): "官鬼", ("木", "木"): "兄弟", ("木", "水"): "父母", ("木", "火"): "子孫", ("木", "土"): "妻財",
    ("水", "金"): "父母", ("水", "木"): "子孫", ("水", "水"): "兄弟", ("水", "火"): "妻財", ("水", "土"): "官鬼",
    ("火", "金"): "妻財", ("火", "木"): "父母", ("火", "水"): "官鬼", ("火", "火"): "兄弟", ("火", "土"): "子孫",
    ("土", "金"): "子孫", ("土", "木"): "官鬼", ("土", "水"): "妻財", ("土", "火"): "父母", ("土", "土"): "兄弟",
}
BRANCH_ELEMENTS = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火",
    "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水"
}

# ==============================================================================
# 2. 邏輯運算
# ==============================================================================

def get_hexagram_name_by_code(upper, lower):
    lookup = {}
    lookup[("乾", "乾")] = "乾為天"; lookup[("乾", "巽")] = "天風姤"; lookup[("乾", "艮")] = "天山遯"; lookup[("乾", "坤")] = "天地否"
    lookup[("巽", "坤")] = "風地觀"; lookup[("艮", "坤")] = "山地剝"; lookup[("離", "坤")] = "火地晉"; lookup[("離", "乾")] = "火天大有"
    lookup[("坎", "坎")] = "坎為水"; lookup[("坎", "兌")] = "水澤節"; lookup[("坎", "震")] = "水雷屯"; lookup[("坎", "離")] = "水火既濟"
    lookup[("兌", "離")] = "澤火革"; lookup[("震", "離")] = "雷火豐"; lookup[("坤", "離")] = "地火明夷"; lookup[("坤", "坎")] = "地水師"
    lookup[("艮", "艮")] = "艮為山"; lookup[("艮", "離")] = "山火賁"; lookup[("艮", "乾")] = "山天大畜"; lookup[("艮", "兌")] = "山澤損"
    lookup[("離", "兌")] = "火澤睽"; lookup[("乾", "兌")] = "天澤履"; lookup[("巽", "兌")] = "風澤中孚"; lookup[("巽", "艮")] = "風山漸"
    lookup[("震", "震")] = "震為雷"; lookup[("震", "坤")] = "雷地豫"; lookup[("震", "坎")] = "雷水解"; lookup[("震", "巽")] = "雷風恆"
    lookup[("坤", "巽")] = "地風升"; lookup[("坎", "巽")] = "水風井"; lookup[("兌", "巽")] = "澤風大過"; lookup[("兌", "震")] = "澤雷隨"
    lookup[("巽", "巽")] = "巽為風"; lookup[("巽", "乾")] = "風天小畜"; lookup[("巽", "離")] = "風火家人"; lookup[("巽", "震")] = "風雷益"
    lookup[("乾", "震")] = "天雷無妄"; lookup[("離", "震")] = "火雷噬嗑"; lookup[("艮", "震")] = "山雷頤"; lookup[("艮", "巽")] = "山風蠱"
    lookup[("離", "離")] = "離為火"; lookup[("離", "艮")] = "火山旅"; lookup[("離", "巽")] = "火風鼎"; lookup[("離", "坎")] = "火水未濟"
    lookup[("艮", "坎")] = "山水蒙"; lookup[("巽", "坎")] = "風水渙"; lookup[("乾", "坎")] = "天水訟"; lookup[("乾", "離")] = "天火同人"
    lookup[("坤", "坤")] = "坤為地"; lookup[("坤", "震")] = "地雷復"; lookup[("坤", "兌")] = "地澤臨"; lookup[("坤", "乾")] = "地天泰"
    lookup[("震", "乾")] = "雷天大壯"; lookup[("兌", "乾")] = "澤天夬"; lookup[("坎", "乾")] = "水天需"; lookup[("坎", "坤")] = "水地比"
    lookup[("兌", "兌")] = "兌為澤"; lookup[("兌", "坎")] = "澤水困"; lookup[("兌", "坤")] = "澤地萃"; lookup[("兌", "艮")] = "澤山咸"
    lookup[("坎", "艮")] = "水山蹇"; lookup[("坤", "艮")] = "地山謙"; lookup[("震", "艮")] = "雷山小過"; lookup[("震", "兌")] = "雷澤歸妹"
    return lookup.get((upper, lower), "未知")

def get_code_from_name(name):
    name = name.strip()
    full_name = SHORT_NAME_MAP.get(name, None)
    
    if not full_name: return None
    
    tri_names = list(TRIGRAMS.keys())
    target_upper, target_lower = "", ""
    found = False
    
    for up in tri_names:
        for lo in tri_names:
            if get_hexagram_name_by_code(up, lo) == full_name:
                target_upper, target_lower = up, lo
                found = True
                break
        if found: break
        
    if not found: return None
    return TRIGRAMS[target_lower]["code"] + TRIGRAMS[target_upper]["code"]

def get_line_details(tri_name, line_idx, is_outer):
    branches = TRIGRAMS[tri_name]["branches"]
    stems = TRIGRAMS[tri_name]["stems"]
    branch_list = branches[3:] if is_outer else branches[:3]
    branch = branch_list[line_idx]
    stem = stems[1] if is_outer else stems[0]
    gz = stem + branch
    nayin = NAYIN_TABLE.get(gz, "")
    element = BRANCH_ELEMENTS[branch]
    return stem, branch, element, nayin

def calculate_hexagram(numbers, day_stem, day_branch):
    main_code = []
    change_code = []
    moves = []
    for n in numbers:
        if n == 6:
            main_code.append(0); change_code.append(1); moves.append(True)
        elif n == 7:
            main_code.append(1); change_code.append(1); moves.append(False)
        elif n == 8:
            main_code.append(0); change_code.append(0); moves.append(False)
        elif n == 9:
            main_code.append(1); change_code.append(0); moves.append(True)
            
    tri_map = {tuple(v["code"]): k for k, v in TRIGRAMS.items()}
    
    m_lower = tri_map.get(tuple(main_code[:3]), "未知")
    m_upper = tri_map.get(tuple(main_code[3:]), "未知")
    c_lower = tri_map.get(tuple(change_code[:3]), "未知")
    c_upper = tri_map.get(tuple(change_code[3:]), "未知")
    
    m_name = get_hexagram_name_by_code(m_upper, m_lower)
    c_name = get_hexagram_name_by_code(c_upper, c_lower)
    
    palace_name, shift = HEX_INFO.get(m_name, ("未知", 0))
    palace_element = TRIGRAMS[palace_name]["element"]
    
    c_palace_name, c_shift = HEX_INFO.get(c_name, ("未知", 0))

    start_god_idx = LIU_SHEN_START.get(day_stem, 0)
    
    attributes = []
    if m_name in SIX_CLASH_HEX: attributes.append("六沖")
    if m_name in SIX_HARMONY_HEX: attributes.append("六合")
    if shift == 7: attributes.append("遊魂")
    if shift == 8: attributes.append("歸魂")
    
    c_attributes = []
    if c_name in SIX_CLASH_HEX: c_attributes.append("六沖")
    if c_name in SIX_HARMONY_HEX: c_attributes.append("六合")
    if c_shift == 7: c_attributes.append("遊魂")
    if c_shift == 8: c_attributes.append("歸魂")
    
    base_lines = []
    for i in range(6):
        is_outer = i >= 3
        local_idx = i - 3 if is_outer else i
        tri = palace_name 
        stem, branch, el, nayin = get_line_details(tri, local_idx, is_outer)
        rel = ELEMENT_RELATIONS.get((palace_element, el), "")
        base_lines.append({"rel": rel, "branch": branch, "el": el, "nayin": nayin, "stem": stem})

    lines_data = []
    for i in range(6):
        is_outer = i >= 3
        local_idx = i - 3 if is_outer else i
        
        m_stem, m_branch, m_el, m_nayin = get_line_details(m_upper if is_outer else m_lower, local_idx, is_outer)
        m_rel = ELEMENT_RELATIONS.get((palace_element, m_el), "")
        
        c_stem, c_branch, c_el, c_nayin = get_line_details(c_upper if is_outer else c_lower, local_idx, is_outer)
        c_rel = ELEMENT_RELATIONS.get((palace_element, c_el), "")
        
        god = LIU_SHEN_ORDER[(start_god_idx + i) % 6]
        
        shiying = ""
        true_shift_pos = shift
        if shift == 7: true_shift_pos = 4
        if shift == 8: true_shift_pos = 3
        
        if (i + 1) == true_shift_pos: 
            shiying = "世"
        else:
            ying_pos = (true_shift_pos + 3) % 6
            if ying_pos == 0: ying_pos = 6
            if (i + 1) == ying_pos:
                shiying = "應"
        
        # 顯示邏輯：UI保留精簡(有差異才顯示)，Copy Text需要全顯
        hidden_str = ""
        base_line = base_lines[i]
        
        # UI用的 conditional hidden
        if (base_line["rel"], base_line["branch"], base_line["el"]) != (m_rel, m_branch, m_el):
            hidden_str = f"{base_line['rel']}{base_line['branch']}{base_line['el']}"

        lines_data.append({
            "god": god,
            "hidden": hidden_str,
            "main": {"stem": m_stem, "branch": m_branch, "el": m_el, "nayin": m_nayin, "rel": m_rel, "shiying": shiying, "type": "yang" if main_code[i] else "yin"},
            "change": {"stem": c_stem, "branch": c_branch, "el": c_el, "nayin": c_nayin, "rel": c_rel, "type": "yang" if change_code[i] else "yin"},
            "move": moves[i]
        })

    return m_name, c_name, palace_name, lines_data, palace_element, attributes, c_attributes, c_palace_name

# ==============================================================================
# 3. UI 呈現
# ==============================================================================

with st.sidebar:
    st.header("設定")
    question_input = st.text_input("輸入問題", placeholder="請輸入占卜問題...")
    date_mode = st.radio("日期模式", ["指定西曆", "指定干支曆"])
    
    gz_year, gz_month, gz_day, gz_hour = "", "", "", ""
    day_stem, day_branch = "", ""
    month_branch = ""
    west_date_str = ""
    
    tz_offset = datetime.timedelta(hours=8)
    now_tw = datetime.datetime.utcnow() + tz_offset
    
    if "init_time" not in st.session_state:
        st.session_state.init_time = now_tw.time()
        st.session_state.init_date = now_tw.date()
    
    # 檢查 session state 是否已有干支紀錄，若無則初始化
    if "gz_year" not in st.session_state: st.session_state.gz_year = "乙巳"
    if "gz_month" not in st.session_state: st.session_state.gz_month = "己丑"
    if "gz_day" not in st.session_state: st.session_state.gz_day = "丁酉"
    if "gz_hour" not in st.session_state: st.session_state.gz_hour = "己酉"

    if date_mode == "指定西曆":
        d = st.date_input("日期", value=st.session_state.init_date)
        t = st.time_input("時間", value=st.session_state.init_time)
        solar = Solar.fromYmdHms(d.year, d.month, d.day, t.hour, t.minute, 0)
        lunar = solar.getLunar()
        gz_year = lunar.getYearInGanZhiExact()
        gz_month = lunar.getMonthInGanZhiExact()
        gz_day = lunar.getDayInGanZhi()
        gz_hour = lunar.getTimeInGanZhi()
        west_date_str = f"{d.strftime('%Y/%m/%d')} {t.strftime('%H:%M')}"
        
        # 指定西曆模式下更新 session state
        st.session_state.gz_year = gz_year
        st.session_state.gz_month = gz_month
        st.session_state.gz_day = gz_day
        st.session_state.gz_hour = gz_hour

    else: # 指定干支曆
        c1, c2 = st.columns(2)
        gz_year = c1.text_input("年柱", value=st.session_state.gz_year)
        gz_month = c2.text_input("月柱", value=st.session_state.gz_month)
        gz_day = c1.text_input("日柱", value=st.session_state.gz_day)
        gz_hour = c2.text_input("時柱", value=st.session_state.gz_hour)
        west_date_str = "(手動輸入)"
        
        # 當手動更改後，更新 session state 以保持最新狀態
        st.session_state.gz_year = gz_year
        st.session_state.gz_month = gz_month
        st.session_state.gz_day = gz_day
        st.session_state.gz_hour = gz_hour

    if gz_day:
        day_stem = gz_day[0]
        day_branch = gz_day[1]
        month_branch = gz_month[1]
        
    st.write(f"當前：{gz_year}年 {gz_month}月 {gz_day}日 {gz_hour}時")

    st.subheader("起卦方式")
    method = st.radio("模式", ["三錢起卦", "卦名起卦"], horizontal=True)

    if "line_values" not in st.session_state:
        st.session_state.line_values = [random.choice([6, 7, 8, 9]) for _ in range(6)]

    input_vals = []
    
    curr_m_name, curr_c_name, _, _, _, _, _, _ = calculate_hexagram(st.session_state.line_values, "甲", "子")
    
    curr_m_short = FULL_TO_SHORT_MAP.get(curr_m_name, curr_m_name)
    curr_c_short = FULL_TO_SHORT_MAP.get(curr_c_name, curr_c_name) if curr_c_name != curr_m_name else ""

    if method == "三錢起卦":
        st.write("由初爻至上爻")
        cols = st.columns(6)
        yao_labels = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]
        new_values = []
        for i in range(6):
            val = cols[i].number_input(
                yao_labels[i], 
                min_value=6, 
                max_value=9, 
                step=1,
                format="%d",
                value=int(st.session_state.line_values[i]), 
                key=f"n{i}"
            )
            new_values.append(val)
        
        if new_values != st.session_state.line_values:
            st.session_state.line_values = new_values
            
        input_vals = st.session_state.line_values

    else: 
        col_m, col_c = st.columns(2)
        main_hex_input = col_m.text_input("主卦 (必填)", value=curr_m_short)
        change_hex_input = col_c.text_input("變卦 (選填)", value=curr_c_short)
        
        if main_hex_input:
            m_code = get_code_from_name(main_hex_input)
            if m_code:
                c_code = m_code 
                if change_hex_input:
                    temp_c = get_code_from_name(change_hex_input)
                    if temp_c:
                        c_code = temp_c
                
                temp_vals = []
                for i in range(6):
                    m = m_code[i]
                    c = c_code[i]
                    if m == 0 and c == 0: temp_vals.append(8)
                    elif m == 1 and c == 1: temp_vals.append(7)
                    elif m == 0 and c == 1: temp_vals.append(6)
                    elif m == 1 and c == 0: temp_vals.append(9)
                
                st.session_state.line_values = temp_vals
                input_vals = temp_vals
            else:
                st.error("找不到主卦名稱，請確認輸入(例如: 既濟 或 水火既濟)")
                input_vals = st.session_state.line_values
        else:
            input_vals = st.session_state.line_values

    st.markdown("<br>", unsafe_allow_html=True)
    
    btn = st.button("排盤", type="primary")

    st.markdown("---")
    st.markdown("""
### 📥 起卦操作指南 (三錢法)

**【基本操作】**
* **準備**：使用 3 枚錢幣，共擲 6 次。
* **順序**：由下往上（初爻、二爻...至上爻）。

**【分值定義】**
* **正 (2分)**：簡單面 (例如: 字面)
* **反 (3分)**：複雜面 (例如: 花色)

**【判定對照】**
* **7 分 (一反兩正)**：少陽 ⚊
* **8 分 (一正兩反)**：少陰 ⚋
* **9 分 (三個反面)**：老陽 ⚊ (O→)
* **6 分 (三個正面)**：老陰 ⚋ (X→)
""")

if btn or True:
    if date_mode == "指定干支曆":
        if not gz_month or not gz_day:
            st.error("【錯誤】月柱與日柱為必填項目，請完整輸入干支（如：甲子）")
            st.stop()

    if not input_vals: input_vals = [7,7,7,7,7,7]
        
    m_name, c_name, palace, lines_data, p_el, m_attrs, c_attrs, c_palace = calculate_hexagram(input_vals, day_stem, day_branch)
    
    has_moving = any(line["move"] for line in lines_data)
    
    def get_voids(stem, branch):
        s_idx = HEAVENLY_STEMS.index(stem)
        b_idx = EARTHLY_BRANCHES.index(branch)
        diff = (b_idx - s_idx) % 12
        return f"{EARTHLY_BRANCHES[(diff - 2) % 12]}{EARTHLY_BRANCHES[(diff - 1) % 12]}"
    
    voids = get_voids(day_stem, day_branch) if day_stem and day_branch else "??"
    
    # [修正] 旬空格式：寅、卯
    voids_formatted = ""
    if len(voids) == 2:
        voids_formatted = f"{voids[0]}、{voids[1]}"
    else:
        voids_formatted = voids
    
    s_a = STAR_A_TABLE.get(month_branch, ("-", "-"))
    s_b = STAR_B_TABLE.get(day_stem, ("-", "-", "-", "-"))
    s_c = STAR_C_TABLE.get(day_branch, ("-", "-", "-", "-", "-", "-", "-"))

    star_list_row1 = [f"天喜-{s_a[0]}", f"天醫-{s_a[1]}", f"祿神-{s_b[0]}", f"羊刃-{s_b[1]}", f"文昌-{s_b[2]}", f"貴人-{s_b[3]}"]
    star_list_row2 = [f"桃花-{s_c[0]}", f"謀星-{s_c[1]}", f"將星-{s_c[2]}", f"驛馬-{s_c[3]}", f"華蓋-{s_c[4]}", f"劫煞-{s_c[5]}", f"災煞-{s_c[6]}"]

    stars_row1_html = "&nbsp;&nbsp;&nbsp;".join(star_list_row1)
    stars_row2_html = "&nbsp;&nbsp;&nbsp;".join(star_list_row2)
    
    stars_row1_text = "   ".join(star_list_row1)
    stars_row2_text = "   ".join(star_list_row2)

    question_html = f"""<div style="font-size:1.2em; font-weight:bold; margin-bottom:10px; border-bottom:1px solid #000; padding-bottom:5px;">問題：{question_input if question_input else "（未輸入）"}</div>"""

    # [修正] 顯示日期字串建構：利用 HTML 進行紅字標示
    # 格式：西曆。年(黑) 月日(紅) 時(黑)
    
    html_date_parts = []
    if date_mode == "指定西曆":
        html_date_parts.append(f"{west_date_str}。")
    
    # 年 (若有輸入則顯示)
    if gz_year.strip():
        html_date_parts.append(f"{gz_year} 年")
        
    # [修正 1] 月柱：天干黑、地支紅 (e.g. 庚(黑)寅(紅))
    # 日柱：全紅 (e.g. 庚戌(紅))
    
    m_stem = gz_month[0] if len(gz_month) > 0 else ""
    m_branch = gz_month[1] if len(gz_month) > 1 else ""
    
    # 組合紅色區塊: "寅 月 庚戌 日" (根據新指示：『月』與『日』字也改回紅色)
    red_segment = f"{m_branch} 月 {gz_day} 日"
    
    # 最終組合: "庚" + <red>...</red>
    html_date_parts.append(f"{m_stem}<span style='color:#d32f2f; font-weight:bold;'>{red_segment}</span>")
    
    # 時 (若有輸入則顯示)
    if gz_hour.strip():
        html_date_parts.append(f"{gz_hour} 時")
        
    final_date_html = " ".join(html_date_parts)

    info_html = f"""<div class="info-box">
<div style="text-align:center; font-size:1.1em; font-weight:bold; margin-bottom:10px;">
{final_date_html} &nbsp;&nbsp; <span style='color:#d32f2f;'>【旬空】：{voids_formatted}</span>
</div>
<div style="display:flex; justify-content:center;">
    <div style="text-align:left; font-size:0.95em; line-height:1.7;">
        {stars_row1_html}<br>
        {stars_row2_html}
    </div>
</div>
</div>"""

    def make_tags_str(attr_list):
        if not attr_list: return ""
        tags = ""
        for a in attr_list:
            tags += f'<span class="attr-tag">{a}</span>'
        return tags

    m_display_name = m_name
    c_display_name = c_name

    m_tags_str = make_tags_str(m_attrs)
    m_header_content = f"""<span class="hex-title-text">{palace}宮：{m_display_name} {m_tags_str}</span><span>【主卦】</span>"""
    
    c_tags_str = make_tags_str(c_attrs)
    if has_moving:
        c_header_content = f"""<span class="hex-title-text">{c_palace}宮：{c_display_name} {c_tags_str}</span><span>【變卦】</span>"""
    else:
        c_header_content = f"""<span class="hex-title-text">&nbsp;</span><span>【變卦】</span>"""

    # UI 表格
    table_html = f"""<table class="hex-table">
<tr class="header-row">
<td width="6%">六神</td>
<td width="6%">藏伏</td>
<td width="27%" class="td-main">{m_header_content}</td>
<td width="8%" class="td-arrow"></td>
<td width="27%" class="td-change">{c_header_content}</td>
<td width="13%" class="small-text">主卦納音</td>
<td width="13%" class="small-text">變卦納音</td>
</tr>"""
    
    for i in range(5, -1, -1):
        line = lines_data[i]
        m = line["main"]
        c = line["change"]
        
        m_bar_cls = "bar-yang" if m["type"] == "yang" else "bar-yin"
        
        move_indicator = ""
        if line["move"]:
            if m["type"] == "yang":
                move_indicator = '<span style="font-weight:bold;">O ---&gt;</span>'
            else:
                move_indicator = '<span style="font-weight:bold;">X ---&gt;</span>'
        
        m_nayin_short = m["nayin"][-3:] if m["nayin"] else ""
        c_nayin_short = ""
        c_cell_content = ""

        if has_moving:
             c_bar_cls = "bar-yang bar-yang-c" if c["type"] == "yang" else "bar-yin bar-yin-c"
             c_cell_content = f"""<div style="display:flex; align-items:center; justify-content:center; gap:5px;">
<div class="{c_bar_cls}"></div>
<div style="text-align:left; min-width:55px; color:#000;">{c['rel']}{c['branch']}{c['el']}</div>
</div>"""
             c_nayin_short = c["nayin"][-3:] if c["nayin"] else ""

        main_cell = f"""<div style="display:flex; align-items:center; justify-content:center; gap:5px;">
<div style="text-align:right; min-width:55px;">{m['rel']}{m['branch']}{m['el']}</div>
<div class="{m_bar_cls}"></div>
<div style="text-align:left; width:25px; color:#000; font-weight:bold; font-size:0.9em;">{m['shiying']}</div>
</div>"""

        row = f"""<tr>
<td class="small-text">{line['god']}</td>
<td class="small-text" style="font-size:0.85em;">{line['hidden']}</td>
<td class="td-main">{main_cell}</td>
<td class="td-arrow">{move_indicator}</td>
<td class="td-change">{c_cell_content}</td>
<td class="small-text" style="font-size:0.85em;">{m_nayin_short}</td>
<td class="small-text" style="font-size:0.85em;">{c_nayin_short}</td>
</tr>"""
        table_html += row
        
    table_html += "</table>"
    
    final_html = question_html + info_html + table_html
    st.markdown(final_html, unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # 4. 複製用文字資料 (AI 判讀輔助 - 優化版)
    # --------------------------------------------------------------------------
    st.markdown("### 📋 複製用文字資料 (AI 判讀輔助)")
    
    all_stars = star_list_row1 + star_list_row2
    formatted_stars = "，".join(all_stars)
    
    


    copy_text = """
    你是通貫易學正統體系的解卦宗師，融會易理、象數與術數之學，
    以《周易》義理立論，並以六爻納甲體系作為核心實證方法，
    進行嚴謹而可回溯的占斷分析。
    
    若存在使用者自訂的系統層級指令（例如自訂角色、解卦規則或行為約束），
    且其優先權高於本指令，則應完全遵循該使用者自訂系統指令，
    本指令自動退居次位。
    
    請直接依據以下完整排盤資料進行解卦，
    不需重述問題、日期、旬空、星煞，亦無須重新整理排盤內容。
    
    解卦流程固定依序為：
    【對軌、定位、定性、應期、細節、兼象、化解】七段，
    
    判斷以六爻用神、世應、生剋制化、旺衰強弱與動變為準，
    《周易》卦辭、彖傳、象傳與動爻爻意僅用於佐證與校驗，
    不得取代六爻卦理本身。
    
    最後請以單一句話給出【最終結論】。
    
    以下為排盤資料：
    \n\n"""

    


    
    copy_text += f"【問題】：{question_input if question_input else '未輸入'}\n"
    
    # 複製用文字資料：日期字串建構
    copy_date_str = ""
    if date_mode == "指定西曆":
        copy_date_str = f"{west_date_str}。{gz_year}年 {gz_month}月 {gz_day}日 {gz_hour}時"
    else:
        # 指定干支曆
        c_parts = []
        if gz_year.strip(): c_parts.append(f"{gz_year}年")
        c_parts.append(f"{gz_month}月")
        c_parts.append(f"{gz_day}日")
        if gz_hour.strip(): c_parts.append(f"{gz_hour}時")
        copy_date_str = " ".join(c_parts)
    
    copy_text += f"【日期】：{copy_date_str}\n"
    copy_text += f"【旬空】：{voids_formatted}\n"
    copy_text += f"【星煞】：{formatted_stars}\n\n"
    
    copy_text += f"【主卦】：{palace}宮-{m_display_name}"
    if m_attrs: copy_text += f" ({','.join(m_attrs)})"
    copy_text += "\n"
    
    if has_moving:
        copy_text += f"【變卦】：{c_palace}宮-{c_display_name}"
        if c_attrs: copy_text += f" ({','.join(c_attrs)})"
        copy_text += "\n"
    
    copy_text += "\n" # 間距
    
    labels_map = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]
    
    if has_moving:
        # [有動變] 顯示完整欄位
        for i in range(5, -1, -1):
            line = lines_data[i]
            
            # 1. 爻位與六神
            row_str = f"[{labels_map[i]}] 六神：{line['god']} | "
            
            # 2. 藏伏
            hidden_val = line['hidden'] 
            if not hidden_val: hidden_val = "無"
            row_str += f"藏伏：{hidden_val} | "
            
            # 3. 主卦
            m = line['main']
            m_yy = "陽爻" if m['type'] == 'yang' else "陰爻"
            m_sy = ""
            if m['shiying'] == "世": m_sy = ", 世爻"
            elif m['shiying'] == "應": m_sy = ", 應爻"
            row_str += f"主卦：{m['rel']}{m['branch']}{m['el']} ({m_yy}{m_sy}) | "
            
            # 4. 動變 (有動變：動爻-> / 無動變：靜爻)
            if line['move']:
                move_str = "有動變：動爻->"
            else:
                move_str = "無動變：靜爻"
            row_str += f"{move_str} | "
            
            # 5. 變卦
            c = line['change']
            c_yy = "陽爻" if c['type'] == 'yang' else "陰爻"
            row_str += f"變卦：{c['rel']}{c['branch']}{c['el']} ({c_yy}) | "
            
            # 6. 納音 (強制顯示 主->變)
            m_ny = m['nayin'][-3:] if m['nayin'] else "無"
            c_ny = line['change']['nayin'][-3:] if line['change']['nayin'] else "無"
            row_str += f"納音：{m_ny} -> {c_ny}"
            
            copy_text += row_str + "\n"
            
    else:
        # [無動變] 簡化欄位
        for i in range(5, -1, -1):
            line = lines_data[i]
            
            # 1. 爻位與六神
            row_str = f"[{labels_map[i]}] 六神：{line['god']} | "
            
            # 2. 藏伏
            hidden_val = line['hidden'] 
            if not hidden_val: hidden_val = "無"
            row_str += f"藏伏：{hidden_val} | "
            
            # 3. 主卦
            m = line['main']
            m_yy = "陽爻" if m['type'] == 'yang' else "陰爻"
            m_sy = ""
            if m['shiying'] == "世": m_sy = ", 世爻"
            elif m['shiying'] == "應": m_sy = ", 應爻"
            row_str += f"主卦：{m['rel']}{m['branch']}{m['el']} ({m_yy}{m_sy}) | "
            
            # 4. 納音 (僅顯示主卦納音)
            m_ny = m['nayin'][-3:] if m['nayin'] else "無"
            row_str += f"納音：{m_ny}"
            
            copy_text += row_str + "\n"
        
    st.code(copy_text, language='text')
