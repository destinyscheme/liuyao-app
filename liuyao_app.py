import streamlit as st
import datetime
from lunar_python import Solar, Lunar

# ==============================================================================
# 0. 網頁設定 & CSS (全黑白風格)
# ==============================================================================
st.set_page_config(page_title="六爻智能排盤-黑白專業版", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@500;700&display=swap');
body, html, .stApp { 
    font-family: "KaiTi", "DFKai-SB", "Noto Serif TC", serif !important; 
    background-color: #ffffff !important;
    color: #000000 !important;
}

/* 表格樣式 */
.hex-table { 
    width: 100%; 
    border-collapse: collapse; 
    text-align: center; 
    font-size: 18px; 
    table-layout: fixed; 
    border: 2px solid #000; 
    margin-top: 10px;
}
.hex-table td { 
    padding: 8px 2px; 
    border-bottom: 1px solid #000; 
    border-right: 1px solid #000;
    vertical-align: middle; 
    color: #000; 
}
.hex-table tr:last-child td {
    border-bottom: none;
}
.hex-table td:last-child {
    border-right: none;
}

/* 標題列 */
.header-row { 
    background-color: #ffffff; 
    font-weight: bold; 
    color: #000; 
    border-bottom: 2px solid #000; 
    font-size: 16px; 
}

/* 陰陽爻條 (全黑) */
.bar-yang { 
    display: inline-block; 
    width: 50px; 
    height: 12px; 
    background-color: #000; 
    border-radius: 0px; 
}
.bar-yin { 
    display: inline-flex; 
    width: 50px; 
    height: 12px; 
    justify-content: space-between; 
}
.bar-yin::before, .bar-yin::after { 
    content: ""; 
    width: 20px; 
    height: 100%; 
    background-color: #000; 
    border-radius: 0px; 
}

/* 變卦的爻條 (全黑) */
.bar-yang-c { background-color: #000; }
.bar-yin-c::before, .bar-yin-c::after { background-color: #000; }

/* 資訊區塊 */
.info-box { 
    border: 1px solid #000; 
    padding: 15px; 
    margin-bottom: 15px; 
    border-radius: 0px; 
    background-color: #fff; 
    color: #000 !important; 
    line-height: 1.6;
}

/* 屬性標籤 */
.attr-tag { 
    font-size: 0.7em; 
    border: 1px solid #000; 
    border-radius: 0px; 
    padding: 1px 4px; 
    color: #000; 
    margin-left: 5px; 
    font-weight: normal; 
    vertical-align: middle;
}

/* 文字樣式 (強制黑) */
.black-text { color: #000 !important; }
.bold-text { font-weight: bold; color: #000 !important; }
.small-text { font-size: 0.85em; color: #000; }

/* 輸入框樣式微調 */
.stTextInput input {
    color: #000;
    border-color: #000;
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 1. 核心資料庫
# ==============================================================================

HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

NAYIN_TABLE = {
    "甲子": "海中金", "乙丑": "海中金", "丙寅": "爐中火", "丁卯": "爐中火",
    "戊辰": "大林木", "己巳": "大林木", "庚午": "路旁土", "辛未": "路旁土",
    "壬申": "劍鋒金", "癸酉": "劍鋒金", "甲戌": "山頭火", "乙亥": "山頭火",
    "丙子": "澗下水", "丁丑": "澗下水", "戊寅": "城頭土", "己卯": "城頭土",
    "庚辰": "白蠟金", "辛巳": "白蠟金", "壬午": "楊柳木", "癸未": "楊柳木",
    "甲申": "井泉水", "乙酉": "井泉水", "丙戌": "屋上土", "丁亥": "屋上土",
    "戊子": "霹靂火", "己丑": "霹靂火", "庚寅": "松柏木", "辛卯": "松柏木",
    "壬辰": "長流水", "癸巳": "長流水", "甲午": "沙中金", "乙未": "沙中金",
    "丙申": "山下火", "丁酉": "山下火", "戊戌": "平地木", "己亥": "平地木",
    "庚子": "壁上土", "辛丑": "壁上土", "壬寅": "金箔金", "癸卯": "金箔金",
    "甲辰": "佛燈火", "乙巳": "佛燈火", "丙午": "天河水", "丁未": "天河水",
    "戊申": "大驛土", "己酉": "大驛土", "庚戌": "釵釧金", "辛亥": "釵釧金",
    "壬子": "桑柘木", "癸丑": "桑柘木", "甲寅": "大溪水", "乙卯": "大溪水",
    "丙辰": "沙中土", "丁巳": "沙中土", "戊午": "天上火", "己未": "天上火",
    "庚申": "石榴木", "辛酉": "石榴木", "壬戌": "大海水", "癸亥": "大海水"
}

TRIGRAMS = {
    "乾": {"code": [1, 1, 1], "element": "金", "stems": ["甲", "壬"], "branches": ["子", "寅", "辰", "午", "申", "戌"]},
    "兌": {"code": [0, 1, 1], "element": "金", "stems": ["丁", "丁"], "branches": ["巳", "卯", "丑", "亥", "酉", "未"]},
    "離": {"code": [1, 0, 1], "element": "火", "stems": ["己", "己"], "branches": ["卯", "丑", "亥", "酉", "未", "巳"]},
    "震": {"code": [0, 0, 1], "element": "木", "stems": ["庚", "庚"], "branches": ["子", "寅", "辰", "午", "申", "戌"]},
    "巽": {"code": [1, 1, 0], "element": "木", "stems": ["辛", "辛"], "branches": ["丑", "亥", "酉", "未", "巳", "卯"]},
    "坎": {"code": [0, 1, 0], "element": "水", "stems": ["戊", "戊"], "branches": ["寅", "辰", "午", "申", "戌", "子"]},
    "艮": {"code": [1, 0, 0], "element": "土", "stems": ["丙", "丙"], "branches": ["辰", "午", "申", "戌", "子", "寅"]},
    "坤": {"code": [0, 0, 0], "element": "土", "stems": ["乙", "癸"], "branches": ["未", "巳", "卯", "丑", "亥", "酉"]},
}

# (宮名, 世爻位置) 1-6為各爻, 7=遊魂(世4), 8=歸魂(世3)
HEX_INFO = {
    "乾為天": ("乾", 6), "天風姤": ("乾", 1), "天山遯": ("乾", 2), "天地否": ("乾", 3),
    "風地觀": ("乾", 4), "山地剝": ("乾", 5), "火地晉": ("乾", 7), "火天大有": ("乾", 8),
    "坎為水": ("坎", 6), "水澤節": ("坎", 1), "水雷屯": ("坎", 2), "水火既濟": ("坎", 3),
    "澤火革": ("坎", 4), "雷火豐": ("坎", 5), "地火明夷": ("坎", 7), "地水師": ("坎", 8),
    "艮為山": ("艮", 6), "山火賁": ("艮", 1), "山天大畜": ("艮", 2), "山澤損": ("艮", 3),
    "火澤睽": ("艮", 4), "天澤履": ("艮", 5), "風澤中孚": ("艮", 7), "風山漸": ("艮", 8),
    "震為雷": ("震", 6), "雷地豫": ("震", 1), "雷水解": ("震", 2), "雷風恆": ("震", 3),
    "地風升": ("震", 4), "水風井": ("震", 5), "澤風大過": ("震", 7), "澤雷隨": ("震", 8),
    "巽為風": ("巽", 6), "風天小畜": ("巽", 1), "風火家人": ("巽", 2), "風雷益": ("巽", 3),
    "天雷無妄": ("巽", 4), "火雷噬嗑": ("巽", 5), "山雷頤": ("巽", 7), "山風蠱": ("巽", 8),
    "離為火": ("離", 6), "火山旅": ("離", 1), "火風鼎": ("離", 2), "火水未濟": ("離", 3),
    "山水蒙": ("離", 4), "風水渙": ("離", 5), "天水訟": ("離", 7), "天火同人": ("離", 8),
    "坤為地": ("坤", 6), "地雷復": ("坤", 1), "地澤臨": ("坤", 2), "地天泰": ("坤", 3),
    "雷天大壯": ("坤", 4), "澤天夬": ("坤", 5), "水天需": ("坤", 7), "水地比": ("坤", 8),
    "兌為澤": ("兌", 6), "澤水困": ("兌", 1), "澤地萃": ("兌", 2), "澤山咸": ("兌", 3),
    "水山蹇": ("兌", 4), "地山謙": ("兌", 5), "雷山小過": ("兌", 7), "雷澤歸妹": ("兌", 8),
}

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
LIU_SHEN = ["青龍", "朱雀", "勾陳", "騰蛇", "白虎", "玄武"]
LIU_SHEN_START = {"甲":0, "乙":0, "丙":1, "丁":1, "戊":2, "己":3, "庚":4, "辛":4, "壬":5, "癸":5}

STAR_A = {"子": ("未", "亥"), "丑": ("未", "子"), "寅": ("戌", "丑"), "卯": ("戌", "寅"), "辰": ("戌", "卯"), "巳": ("丑", "辰"), "午": ("丑", "巳"), "未": ("丑", "午"), "申": ("辰", "未"), "酉": ("辰", "申"), "戌": ("辰", "酉"), "亥": ("未", "戌")}
STAR_B = {"甲": ("寅", "卯", "巳", "丑、未"), "乙": ("卯", "寅", "午", "申、子"), "丙": ("巳", "午", "申", "酉、亥"), "丁": ("午", "巳", "酉", "酉、亥"), "戊": ("巳", "午", "申", "丑、未"), "己": ("午", "巳", "酉", "申、子"), "庚": ("申", "酉", "亥", "寅、午"), "辛": ("酉", "申", "子", "寅、午"), "壬": ("亥", "子", "寅", "卯、巳"), "癸": ("子", "亥", "卯", "卯、巳")}
STAR_C = {"子": ("酉", "戌", "子", "寅", "辰", "巳", "午"), "丑": ("午", "未", "酉", "亥", "丑", "寅", "卯"), "寅": ("卯", "辰", "午", "申", "戌", "亥", "子"), "卯": ("子", "丑", "卯", "巳", "未", "申", "酉"), "辰": ("酉", "戌", "子", "寅", "辰", "巳", "午"), "巳": ("午", "未", "酉", "亥", "丑", "寅", "卯"), "午": ("卯", "辰", "午", "申", "戌", "亥", "子"), "未": ("子", "丑", "卯", "巳", "未", "申", "酉"), "申": ("酉", "戌", "子", "寅", "辰", "巳", "午"), "酉": ("午", "未", "酉", "亥", "丑", "寅", "卯"), "戌": ("卯", "辰", "午", "申", "戌", "亥", "子"), "亥": ("子", "丑", "卯", "巳", "未", "申", "酉")}

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
    
    m_lower_code = tuple(main_code[:3][::-1]) 
    m_upper_code = tuple(main_code[3:][::-1])
    c_lower_code = tuple(change_code[:3][::-1])
    c_upper_code = tuple(change_code[3:][::-1])
    
    m_lower = tri_map.get(m_lower_code, "未知")
    m_upper = tri_map.get(m_upper_code, "未知")
    c_lower = tri_map.get(c_lower_code, "未知")
    c_upper = tri_map.get(c_upper_code, "未知")
    
    m_name = get_hexagram_name_by_code(m_upper, m_lower)
    c_name = get_hexagram_name_by_code(c_upper, c_lower)
    
    palace_name, shift = HEX_INFO.get(m_name, ("未知", 0))
    palace_element = TRIGRAMS[palace_name]["element"]
    
    # 變卦宮位資訊 (用於顯示 變卦宮名)
    c_palace_name, c_shift = HEX_INFO.get(c_name, ("未知", 0))

    start_god = LIU_SHEN_START.get(day_stem, 0)
    
    # 判斷屬性
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
    
    # 準備藏伏 (本宮卦)
    base_lines = []
    base_u = palace_name
    base_l = palace_name
    for i in range(6):
        is_outer = i >= 3
        local_idx = i - 3 if is_outer else i
        tri = base_u if is_outer else base_l
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
        
        god = LIU_SHEN[(start_god + i) % 6]
        
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
        
        hidden_str = ""
        base_line = base_lines[i]
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
    
    # 新增問題輸入框
    question_input = st.text_input("輸入問題", placeholder="請輸入占卜事項...")

    date_mode = st.radio("日期模式", ["自動 (Current)", "指定西曆", "手動干支"])
    
    gz_year, gz_month, gz_day, gz_hour = "", "", "", ""
    day_stem, day_branch = "", ""
    month_branch = ""
    
    tz_offset = datetime.timedelta(hours=8)
    now_tw = datetime.datetime.utcnow() + tz_offset
    
    if "init_time" not in st.session_state:
        st.session_state.init_time = now_tw.time()
        st.session_state.init_date = now_tw.date()

    if date_mode == "自動 (Current)":
        solar = Solar.fromYmdHms(now_tw.year, now_tw.month, now_tw.day, now_tw.hour, now_tw.minute, 0)
        lunar = solar.getLunar()
        gz_year = lunar.getYearInGanZhi()
        gz_month = lunar.getMonthInGanZhiExact()
        gz_day = lunar.getDayInGanZhi()
        gz_hour = lunar.getTimeInGanZhi()
    
    elif date_mode == "指定西曆":
        d = st.date_input("日期", value=st.session_state.init_date)
        t = st.time_input("時間", value=st.session_state.init_time)
        
        solar = Solar.fromYmdHms(d.year, d.month, d.day, t.hour, t.minute, 0)
        lunar = solar.getLunar()
        gz_year = lunar.getYearInGanZhi()
        gz_month = lunar.getMonthInGanZhiExact()
        gz_day = lunar.getDayInGanZhi()
        gz_hour = lunar.getTimeInGanZhi()

    else: 
        c1, c2 = st.columns(2)
        gz_year = c1.text_input("年柱", "乙巳")
        gz_month = c2.text_input("月柱", "己丑")
        gz_day = c1.text_input("日柱", "丁酉")
        gz_hour = c2.text_input("時柱", "己酉")

    if gz_day:
        day_stem = gz_day[0]
        day_branch = gz_day[1]
        month_branch = gz_month[1]
        
    st.write(f"當前：{gz_year}年 {gz_month}月 {gz_day}日 {gz_hour}時")

    st.subheader("起卦 (由初爻至上爻)")
    cols = st.columns(6)
    input_vals = []
    def_vals = [7, 7, 7, 7, 7, 7]
    for i in range(6):
        val = cols[i].number_input(f"爻{i+1}", 6, 9, def_vals[i], key=f"n{i}")
        input_vals.append(val)
    
    btn = st.button("排盤", type="primary")

if btn or True:
    m_name, c_name, palace, lines_data, p_el, m_attrs, c_attrs, c_palace = calculate_hexagram(input_vals, day_stem, day_branch)
    
    has_moving = any(line["move"] for line in lines_data)
    
    def get_voids(stem, branch):
        s_idx = HEAVENLY_STEMS.index(stem)
        b_idx = EARTHLY_BRANCHES.index(branch)
        diff = (b_idx - s_idx) % 12
        return f"{EARTHLY_BRANCHES[(diff - 2) % 12]}{EARTHLY_BRANCHES[(diff - 1) % 12]}"
    
    voids = get_voids(day_stem, day_branch) if day_stem and day_branch else "??"
    
    s_a = STAR_A.get(month_branch, ("-", "-"))
    s_b = STAR_B.get(day_stem, ("-", "-", "-", "-"))
    s_c = STAR_C.get(day_branch, ("-", "-", "-", "-", "-", "-", "-"))

    # 星煞整理
    star_list_row1 = []
    star_list_row1.append(f"天喜-{s_a[0]}")
    star_list_row1.append(f"天醫-{s_a[1]}")
    star_list_row1.append(f"祿神-{s_b[0]}")
    star_list_row1.append(f"羊刃-{s_b[1]}")
    star_list_row1.append(f"文昌-{s_b[2]}")
    star_list_row1.append(f"貴人-{s_b[3]}")

    star_list_row2 = []
    star_list_row2.append(f"桃花-{s_c[0]}")
    star_list_row2.append(f"謀星-{s_c[1]}")
    star_list_row2.append(f"將星-{s_c[2]}")
    star_list_row2.append(f"驛馬-{s_c[3]}")
    star_list_row2.append(f"華蓋-{s_c[4]}")
    star_list_row2.append(f"劫煞-{s_c[5]}")
    star_list_row2.append(f"災煞-{s_c[6]}")

    stars_row1_str = "，".join(star_list_row1)
    stars_row2_str = "，".join(star_list_row2)

    # 1. 頂部問題
    question_html = f"""<div style="font-size:1.2em; font-weight:bold; margin-bottom:10px; border-bottom:1px solid #000; padding-bottom:5px;">問題：{question_input if question_input else "（未輸入）"}</div>"""

    # 2. 資訊區塊 (星煞重排)
    info_html = f"""<div class="info-box">
<div style="text-align:center; font-size:1.1em; font-weight:bold; margin-bottom:10px;">
<span>{gz_year}</span> 年 
<span>{gz_month}</span> 月 
<span>{gz_day}</span> 日 
<span>{gz_hour}</span> 時 
&nbsp;&nbsp; (旬空: <span>{voids}</span>)
</div>
<div style="font-size:0.95em; line-height:1.7; text-align:center;">
{stars_row1_str}<br>
{stars_row2_str}
</div>
</div>"""

    # 3. 屬性標籤
    def make_tags(attr_list, palace_info=None):
        tags = ""
        # 這裡不顯示宮位標籤了，因為已經移到標題文字中
        # if palace_info: tags += f'<span class="attr-tag" style="border-color:#333; color:#333;">{palace_info}</span>'
        for a in attr_list:
            tags += f'<span class="attr-tag">{a}</span>'
        return tags

    m_tags = make_tags(m_attrs)
    c_tags = make_tags(c_attrs) if has_moving else ""

    # 4. 卦名標題 (格式：主宮：卦名)
    m_title_str = f"{palace}宮：{m_name}"
    
    if has_moving:
        c_title_str = f"{c_palace}宮：{c_name}"
        title_html = f"""<div style="display:flex; justify-content:space-between; align-items:center; margin: 10px 0; padding: 0 5%;">
<div style="text-align:center;"><span style="font-size:1.3em; font-weight:bold;">{m_title_str}</span> {m_tags}</div>
<div style="font-size:1.5em; font-weight:bold;">➔</div>
<div style="text-align:center;"><span style="font-size:1.3em; font-weight:bold;">{c_title_str}</span> {c_tags}</div>
</div>"""
    else:
        title_html = f"""<div style="text-align:center; margin: 10px 0;">
<span style="font-size:1.3em; font-weight:bold;">{m_title_str}</span> {m_tags}
</div>"""
    
    # 5. 表格生成
    table_html = """<table class="hex-table">
<tr class="header-row">
<td width="8%">六神</td>
<td width="10%">藏伏</td>
<td width="28%">【主卦】</td>
<td width="13%" class="small-text">主卦納音</td>
<td width="28%">【變卦】</td>
<td width="13%" class="small-text">變卦納音</td>
</tr>"""
    
    for i in range(5, -1, -1):
        line = lines_data[i]
        m = line["main"]
        c = line["change"]
        
        m_bar_cls = "bar-yang" if m["type"] == "yang" else "bar-yin"
        
        # 變卦顯示邏輯：無動爻時，變卦所有相關顯示為空
        c_cell_content = ""
        c_nayin_short = ""
        
        if has_moving:
             c_bar_cls = "bar-yang bar-yang-c" if c["type"] == "yang" else "bar-yin bar-yin-c"
             # 變卦內容始終顯示（無論該爻是否動爻，Excel截圖為全顯）
             c_cell_content = f"""<div style="display:flex; align-items:center; justify-content:center; gap:5px;">
<div class="{c_bar_cls}"></div>
<div style="text-align:left; min-width:55px; color:#000;">{c['rel']}{c['branch']}{c['el']}</div>
</div>"""
             c_nayin_short = c["nayin"][-3:] if c["nayin"] else ""

        # 動爻標記 (全黑)
        move_dot = '<span class="black-text" style="font-size:1.1em; font-weight:bold;">O</span>' if line["move"] and m["type"]=="yang" else \
                   '<span class="black-text" style="font-size:1.1em; font-weight:bold;">X</span>' if line["move"] and m["type"]=="yin" else ""
        
        m_nayin_short = m["nayin"][-3:] if m["nayin"] else ""

        # 主卦單元格
        main_cell = f"""<div style="display:flex; align-items:center; justify-content:center; gap:5px;">
<div style="text-align:right; min-width:55px;">{m['rel']}{m['branch']}{m['el']}</div>
<div class="{m_bar_cls}"></div>
<div style="text-align:left; width:15px; color:#000; font-weight:bold; font-size:0.9em;">{m['shiying']}</div>
<div style="width:10px;">{move_dot}</div>
</div>"""

        row = f"""<tr>
<td class="small-text">{line['god']}</td>
<td class="small-text" style="font-size:0.85em;">{line['hidden']}</td>
<td>{main_cell}</td>
<td class="small-text" style="font-size:0.85em;">{m_nayin_short}</td>
<td>{c_cell_content}</td>
<td class="small-text" style="font-size:0.85em;">{c_nayin_short}</td>
</tr>"""
        table_html += row
        
    table_html += "</table>"
    
    final_html = question_html + info_html + title_html + table_html
    st.markdown(final_html, unsafe_allow_html=True)
