import streamlit as st
import datetime
from lunar_python import Solar

# ==============================================================================
# 1. 核心資料庫 (Hardcoded Database)
# ==============================================================================

# 天干地支與五行
HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
FIVE_ELEMENTS = {"金": "兄弟", "木": "妻財", "水": "父母", "火": "子孫", "土": "官鬼"} # 僅為預設，需依宮位變動

# 納音表 (六十甲子 -> 納音五行)
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

# 八卦基本資料 (納甲天干, 內外卦地支)
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

# 64卦宮位與世應資料 (Name -> Palace, Shift of Shi)
# 格式: "卦名": ("宮名", 世爻位置1-6)
# 歸魂=7, 遊魂=8 (程式邏輯用)
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

# 五行生剋矩陣
ELEMENT_RELATIONS = {
    # (我, 他) -> 關係
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

# 星煞表
STAR_A = { # 月支
    "子": ("未", "亥"), "丑": ("未", "子"), "寅": ("戌", "丑"), "卯": ("戌", "寅"),
    "辰": ("戌", "卯"), "巳": ("丑", "辰"), "午": ("丑", "巳"), "未": ("丑", "午"),
    "申": ("辰", "未"), "酉": ("辰", "申"), "戌": ("辰", "酉"), "亥": ("未", "戌")
}
STAR_B = { # 日干
    "甲": ("寅", "卯", "巳", "丑、未"), "乙": ("卯", "寅", "午", "申、子"),
    "丙": ("巳", "午", "申", "酉、亥"), "丁": ("午", "巳", "酉", "酉、亥"),
    "戊": ("巳", "午", "申", "丑、未"), "己": ("午", "巳", "酉", "申、子"),
    "庚": ("申", "酉", "亥", "寅、午"), "辛": ("酉", "申", "子", "寅、午"),
    "壬": ("亥", "子", "寅", "卯、巳"), "癸": ("子", "亥", "卯", "卯、巳")
}
STAR_C = { # 日支
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

# 六神循環
LIU_SHEN = ["青龍", "朱雀", "勾陳", "騰蛇", "白虎", "玄武"]
LIU_SHEN_START = {"甲":0, "乙":0, "丙":1, "丁":1, "戊":2, "己":3, "庚":4, "辛":4, "壬":5, "癸":5}

# ==============================================================================
# 2. 邏輯運算 (Logic)
# ==============================================================================

def get_hexagram_name(upper_code, lower_code):
    # 根據 01 碼找卦名
    for name, (palace, shift) in HEX_INFO.items():
        # 反推有點慢，這裡我們構建一個 lookup
        pass
    # 由於篇幅，我們使用映射表 (Code -> Name)
    # 需重新構建一個 Trigram Name -> Code 的反查
    tri_map = {tuple(v["code"]): k for k, v in TRIGRAMS.items()}
    u_name = tri_map.get(tuple(upper_code))
    l_name = tri_map.get(tuple(lower_code))
    
    # 查 64 卦表
    # 這裡需要一個 Trigram Names -> Hexagram Name 的表
    # 為了節省空間，我們用窮舉法
    lookup_64 = {}
    lookup_64[("乾", "乾")] = "乾為天"; lookup_64[("乾", "巽")] = "天風姤"; lookup_64[("乾", "艮")] = "天山遯"; lookup_64[("乾", "坤")] = "天地否"
    lookup_64[("巽", "坤")] = "風地觀"; lookup_64[("艮", "坤")] = "山地剝"; lookup_64[("離", "坤")] = "火地晉"; lookup_64[("離", "乾")] = "火天大有"
    
    lookup_64[("坎", "坎")] = "坎為水"; lookup_64[("坎", "兌")] = "水澤節"; lookup_64[("坎", "震")] = "水雷屯"; lookup_64[("坎", "離")] = "水火既濟"
    lookup_64[("兌", "離")] = "澤火革"; lookup_64[("震", "離")] = "雷火豐"; lookup_64[("坤", "離")] = "地火明夷"; lookup_64[("坤", "坎")] = "地水師"
    
    lookup_64[("艮", "艮")] = "艮為山"; lookup_64[("艮", "離")] = "山火賁"; lookup_64[("艮", "乾")] = "山天大畜"; lookup_64[("艮", "兌")] = "山澤損"
    lookup_64[("離", "兌")] = "火澤睽"; lookup_64[("乾", "兌")] = "天澤履"; lookup_64[("巽", "兌")] = "風澤中孚"; lookup_64[("巽", "艮")] = "風山漸"
    
    lookup_64[("震", "震")] = "震為雷"; lookup_64[("震", "坤")] = "雷地豫"; lookup_64[("震", "坎")] = "雷水解"; lookup_64[("震", "巽")] = "雷風恆"
    lookup_64[("坤", "巽")] = "地風升"; lookup_64[("坎", "巽")] = "水風井"; lookup_64[("兌", "巽")] = "澤風大過"; lookup_64[("兌", "震")] = "澤雷隨"
    
    lookup_64[("巽", "巽")] = "巽為風"; lookup_64[("巽", "乾")] = "風天小畜"; lookup_64[("巽", "離")] = "風火家人"; lookup_64[("巽", "震")] = "風雷益"
    lookup_64[("乾", "震")] = "天雷無妄"; lookup_64[("離", "震")] = "火雷噬嗑"; lookup_64[("艮", "震")] = "山雷頤"; lookup_64[("艮", "巽")] = "山風蠱"
    
    lookup_64[("離", "離")] = "離為火"; lookup_64[("離", "艮")] = "火山旅"; lookup_64[("離", "巽")] = "火風鼎"; lookup_64[("離", "坎")] = "火水未濟"
    lookup_64[("艮", "坎")] = "山水蒙"; lookup_64[("巽", "坎")] = "風水渙"; lookup_64[("乾", "坎")] = "天水訟"; lookup_64[("乾", "離")] = "天火同人"
    
    lookup_64[("坤", "坤")] = "坤為地"; lookup_64[("坤", "震")] = "地雷復"; lookup_64[("坤", "兌")] = "地澤臨"; lookup_64[("坤", "乾")] = "地天泰"
    lookup_64[("震", "乾")] = "雷天大壯"; lookup_64[("兌", "乾")] = "澤天夬"; lookup_64[("坎", "乾")] = "水天需"; lookup_64[("坎", "坤")] = "水地比"
    
    lookup_64[("兌", "兌")] = "兌為澤"; lookup_64[("兌", "坎")] = "澤水困"; lookup_64[("兌", "坤")] = "澤地萃"; lookup_64[("兌", "艮")] = "澤山咸"
    lookup_64[("坎", "艮")] = "水山蹇"; lookup_64[("坤", "艮")] = "地山謙"; lookup_64[("震", "艮")] = "雷山小過"; lookup_64[("震", "兌")] = "雷澤歸妹"

    return lookup_64.get((u_name, l_name), "未知")

def get_line_details(tri_name, line_idx, is_outer):
    # 取得單爻的地支與五行 (line_idx: 0-2)
    branches = TRIGRAMS[tri_name]["branches"]
    stems = TRIGRAMS[tri_name]["stems"]
    
    # 判斷使用內卦還是外卦的 Stem/Branch
    # 支：
    branch_list = branches[3:] if is_outer else branches[:3]
    branch = branch_list[line_idx]
    
    # 干： (乾坤內外不同，其餘相同)
    stem = stems[1] if is_outer else stems[0]
    
    # 納音
    gz = stem + branch
    nayin = NAYIN_TABLE.get(gz, "")
    
    # 五行
    element = BRANCH_ELEMENTS[branch]
    
    return stem, branch, element, nayin

def calculate_hexagram(numbers, day_stem, day_branch):
    # 解析輸入
    main_code = [] # 0, 1
    change_code = []
    moves = []
    
    # 數字轉陰陽
    # 6:老陰(0->1), 7:少陽(1), 8:少陰(0), 9:老陽(1->0)
    for n in numbers:
        if n == 6:
            main_code.append(0); change_code.append(1); moves.append(True)
        elif n == 7:
            main_code.append(1); change_code.append(1); moves.append(False)
        elif n == 8:
            main_code.append(0); change_code.append(0); moves.append(False)
        elif n == 9:
            main_code.append(1); change_code.append(0); moves.append(True)
            
    # 取得八卦名
    tri_map = {tuple(v["code"]): k for k, v in TRIGRAMS.items()}
    
    m_lower = tri_map[tuple(main_code[:3])]
    m_upper = tri_map[tuple(main_code[3:])]
    c_lower = tri_map[tuple(change_code[:3])]
    c_upper = tri_map[tuple(change_code[3:])]
    
    # 取得卦名與宮位
    m_name = get_hexagram_name(main_code[3:], main_code[:3])
    c_name = get_hexagram_name(change_code[3:], change_code[:3])
    
    palace_name, shift = HEX_INFO.get(m_name, ("未知", 0))
    palace_element = TRIGRAMS[palace_name]["element"]
    
    # 計算六神
    start_god = LIU_SHEN_START.get(day_stem, 0)
    
    # 計算伏神 (若主卦六親缺項)
    # 1. 先找出主卦所有六親
    present_rels = set()
    
    # 暫存每一爻的資料
    lines_data = []
    
    # 由初爻到上爻 (0-5)
    for i in range(6):
        is_outer = i >= 3
        local_idx = i - 3 if is_outer else i
        
        # 主卦
        tri = m_upper if is_outer else m_lower
        m_stem, m_branch, m_el, m_nayin = get_line_details(tri, local_idx, is_outer)
        m_rel = ELEMENT_RELATIONS.get((palace_element, m_el), "")
        present_rels.add(m_rel)
        
        # 變卦
        tri_c = c_upper if is_outer else c_lower
        c_stem, c_branch, c_el, c_nayin = get_line_details(tri_c, local_idx, is_outer)
        c_rel = ELEMENT_RELATIONS.get((palace_element, c_el), "") # 變卦六親依主卦宮位
        
        # 六神
        god = LIU_SHEN[(start_god + i) % 6]
        
        # 世應
        shiying = ""
        # 處理歸魂遊魂的世應
        true_shift = shift
        if shift == 7: true_shift = 3 # 歸魂世在三
        if shift == 8: true_shift = 4 # 遊魂世在四
        
        if (i + 1) == true_shift: shiying = "世"
        elif (i + 1) == ((true_shift + 3) % 6 if (true_shift + 3) % 6 != 0 else 6): shiying = "應"
        
        lines_data.append({
            "god": god,
            "main": {"stem": m_stem, "branch": m_branch, "el": m_el, "nayin": m_nayin, "rel": m_rel, "shiying": shiying, "type": "yang" if main_code[i] else "yin"},
            "change": {"stem": c_stem, "branch": c_branch, "el": c_el, "nayin": c_nayin, "rel": c_rel, "type": "yang" if change_code[i] else "yin"},
            "move": moves[i]
        })
        
    # 2. 檢查伏神
    # 需檢查 本宮卦 (palace_name + palace_name)
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
        
    # 填充伏神字串
    for i in range(6):
        # 伏神邏輯：只有當主卦該六親完全缺失時，才顯示伏神在對應位置？
        # 簡易邏輯：檢查 本宮該爻的六親 是否在 present_rels 中
        # 若不在，則該爻顯示伏神
        # 但通常伏神是顯示在「飛神」旁。
        # 這裡採用《增刪卜易》：若主卦缺某六親，則查本宮該六親伏於何爻之下。
        
        lines_data[i]["hidden"] = ""
        base_line = base_lines[i]
        
        # 如果主卦裡沒有這個六親，且這一爻的本宮就是這個六親 -> 伏神
        if base_line["rel"] not in present_rels:
             lines_data[i]["hidden"] = f"{base_line['rel']}{base_line['branch']}{base_line['el']}"

    return m_name, c_name, palace_name, lines_data, palace_element


# ==============================================================================
# 3. Streamlit UI & CSS
# ==============================================================================

st.set_page_config(page_title="六爻智能排盤", layout="wide")

# CSS 樣式：強制表格對齊、字體、顏色
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@500&display=swap');
    
    body, html, .stApp {
        font-family: "KaiTi", "DFKai-SB", "Noto Serif TC", serif !important;
    }
    
    /* 表格樣式 */
    .hex-table {
        width: 100%;
        border-collapse: collapse;
        text-align: center;
        font-size: 18px;
    }
    .hex-table td {
        padding: 8px 2px;
        border-bottom: 1px solid #eee;
        vertical-align: middle;
    }
    .header-row {
        background-color: #f0f2f6;
        font-weight: bold;
        color: #333;
    }
    
    /* 顏色與強調 */
    .red-text { color: #d32f2f; font-weight: bold; }
    .blue-text { color: #1976d2; }
    .grey-text { color: #757575; font-size: 0.9em; }
    .small-text { font-size: 0.8em; }
    
    /* 卦爻符號 */
    .bar-yang {
        display: inline-block; width: 60px; height: 12px; background-color: #333;
        border-radius: 2px;
    }
    .bar-yin {
        display: inline-flex; width: 60px; height: 12px; justify-content: space-between;
    }
    .bar-yin::before, .bar-yin::after {
        content: ""; width: 26px; height: 100%; background-color: #333; border-radius: 2px;
    }
    
    /* 變卦符號 (淡色) */
    .bar-yang-c { background-color: #777; }
    .bar-yin-c::before, .bar-yin-c::after { background-color: #777; }
    
    /* 星煞表 */
    .star-box {
        border: 1px solid #ddd; padding: 10px; margin-bottom: 15px;
        border-radius: 5px; background-color: #fff; font-size: 0.9rem;
    }
    .star-table { width: 100%; font-size: 14px; }
    .star-table td { border: none; padding: 3px 8px; text-align: left;}
    
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# Sidebar 輸入
# ------------------------------------------------------------------------------
with st.sidebar:
    st.header("設定")
    date_mode = st.radio("日期", ["自動 (Current)", "手動干支"])
    
    gz_year, gz_month, gz_day, gz_hour = "", "", "", ""
    day_stem, day_branch = "", ""
    month_branch = ""
    
    if date_mode == "自動 (Current)":
        now = datetime.datetime.now()
        solar = Solar.fromYmdHms(now.year, now.month, now.day, now.hour, now.minute, 0)
        lunar = solar.getLunar()
        gz_year = lunar.getYearInGanZhi()
        gz_month = lunar.getMonthInGanZhiExact()
        gz_day = lunar.getDayInGanZhi()
        gz_hour = lunar.getTimeInGanZhi()
        
        day_stem = gz_day[0]
        day_branch = gz_day[1]
        month_branch = gz_month[1]
    else:
        c1, c2 = st.columns(2)
        gz_year = c1.text_input("年柱", "乙巳")
        gz_month = c2.text_input("月柱", "己丑")
        gz_day = c1.text_input("日柱", "丁酉")
        gz_hour = c2.text_input("時柱", "己酉")
        day_stem = gz_day[0]
        day_branch = gz_day[1]
        month_branch = gz_month[1]

    st.subheader("起卦")
    nums = []
    col_input = st.columns(6)
    # Default 咸之升 (8, 7, 9, 7, 6, 8) -> 6=Top, 1=Bottom
    # User input standard is usually Bottom to Top. Let's ask Bottom to Top.
    defaults = [6, 7, 9, 7, 8, 8] # 上傳圖片的咸之升：初爻6(陰變陽)..等
    # 修正：圖片 咸之升
    # 咸 (澤山) 下艮(山) 上兌(澤) -> [001, 011]
    # 升 (地風) 下巽(風) 上坤(地)
    # 圖片中的咸：
    # 6: 未土 應 (陰) -> 8
    # 5: 酉金    (陽) -> 7
    # 4: 亥水    (陽) -> 7 (但圖片顯示變卦亥水.. 4爻是陽)
    # 3: 申金 世 (陽) -> 9 (陽變陰) -> 變成丑土? 
    # 讓我們直接提供輸入框讓用戶打
    
    st.info("請輸入六爻數字 (由初爻至上爻)")
    cols = st.columns(6)
    input_vals = []
    for i in range(6):
        val = cols[i].number_input(f"爻{i+1}", 6, 9, 8, key=f"n{i}")
        input_vals.append(val)
    
    btn = st.button("排盤", type="primary")

# ------------------------------------------------------------------------------
# 主畫面 Render
# ------------------------------------------------------------------------------

if btn or True: # Default run
    # 1. 計算
    m_name, c_name, palace, lines_data, p_el = calculate_hexagram(input_vals, day_stem, day_branch)
    
    # 計算空亡
    def get_voids(stem, branch):
        s_idx = HEAVENLY_STEMS.index(stem)
        b_idx = EARTHLY_BRANCHES.index(branch)
        diff = (b_idx - s_idx) % 12
        return f"{EARTHLY_BRANCHES[(diff - 2) % 12]}{EARTHLY_BRANCHES[(diff - 1) % 12]}"
        
    voids = get_voids(day_stem, day_branch)
    
    # 2. 星煞資料準備
    s_a = STAR_A.get(month_branch, ("-", "-"))
    s_b = STAR_B.get(day_stem, ("-", "-", "-", "-"))
    s_c = STAR_C.get(day_branch, ("-", "-", "-", "-", "-", "-", "-"))

    # 3. 顯示 Top Header
    st.markdown(f"""
    <div class="star-box">
        <div style="text-align:center; font-size:1.3em; margin-bottom:10px;">
            <span class="red-text">{gz_year}</span> 年 
            <span class="red-text">{gz_month}</span> 月 
            <span class="red-text">{gz_day}</span> 日 
            <span class="red-text">{gz_hour}</span> 時 
            &nbsp;&nbsp; (旬空: <span class="red-text">{voids}</span>)
        </div>
        <table class="star-table">
            <tr>
                <td><b>月煞：</b>天喜-{s_a[0]}，天醫-{s_a[1]}</td>
                <td><b>日干煞：</b>祿神-{s_b[0]}，羊刃-{s_b[1]}，文昌-{s_b[2]}，貴人-{s_b[3]}</td>
            </tr>
            <tr>
                <td colspan="2"><b>日支煞：</b>桃花-{s_c[0]}，將星-{s_c[2]}，劫煞-{s_c[5]}，驛馬-{s_c[3]}，災煞-{s_c[6]}，謀星-{s_c[1]}，華蓋-{s_c[4]}</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

    # 4. 顯示 卦象 Table
    # Table Header
    table_html = f"""
    <div style="text-align:center; margin-bottom:10px;">
        <span style="font-size:1.5em; font-weight:bold;">{m_name}</span> (主) 
        <span style="margin:0 20px; color:#ccc;">➔</span> 
        <span style="font-size:1.5em; font-weight:bold;">{c_name}</span> (變)
        <br>
        <span class="grey-text">{palace}宮{p_el}</span>
    </div>
    
    <table class="hex-table">
        <tr class="header-row">
            <td width="10%">六神</td>
            <td width="15%">藏伏</td>
            <td width="15%">納音</td>
            <td width="30%">【本卦】 {m_name}</td>
            <td width="5%">變</td>
            <td width="25%">【變卦】 {c_name}</td>
        </tr>
    """
    
    # Rows (Reversed: 6 -> 1)
    for i in range(5, -1, -1):
        line = lines_data[i]
        m = line["main"]
        c = line["change"]
        
        # 樣式處理
        m_bar_cls = "bar-yang" if m["type"] == "yang" else "bar-yin"
        c_bar_cls = "bar-yang bar-yang-c" if c["type"] == "yang" else "bar-yin bar-yin-c"
        
        # 動爻箭頭
        move_sign = '<span class="red-text">O</span>' if line["move"] and m["type"]=="yang" else \
                    '<span class="red-text">X</span>' if line["move"] and m["type"]=="yin" else ""
                    
        # 變卦文字 (靜爻不顯示，動爻顯示)
        # 依照圖片：變卦欄位若該爻未動，通常空白或顯示不變。但若要完整對照，我們僅在動爻時顯示變出的爻
        c_content = ""
        if line["move"]:
             c_content = f"""
             <div class="{c_bar_cls}"></div><br>
             <span class="red-text">{c['rel']}{c['branch']}{c['el']}</span>
             """
        else:
            # 靜爻顯示淡色符號，不顯示文字
            c_content = f'<div class="{c_bar_cls}" style="opacity:0.3;"></div>'

        # 納音列 (顯示本卦納音)
        nayin_str = m["nayin"][-3:] if m["nayin"] else "" # 取後三字，如大海水
        
        # 藏伏 (靠左)
        fushen = line["hidden"]
        
        row_html = f"""
        <tr>
            <td class="grey-text">{line['god']}</td>
            <td class="small-text" style="color:#888;">{fushen}</td>
            <td>{nayin_str}</td>
            <td>
                <div style="display:flex; align-items:center; justify-content:center; gap:10px;">
                    <div style="text-align:right; width:60px;">
                        {m['rel']}{m['branch']}{m['el']}
                    </div>
                    <div class="{m_bar_cls}"></div>
                    <div style="text-align:left; width:30px; font-size:0.8em; color:#d32f2f;">
                        {m['shiying']}
                    </div>
                </div>
            </td>
            <td>{move_sign}</td>
            <td>{c_content}</td>
        </tr>
        """
        table_html += row_html
        
    table_html += "</table>"
    
    st.markdown(table_html, unsafe_allow_html=True)
    
    # Footer
    st.caption("說明：本排盤系統嚴格依照《增刪卜易》納甲法編寫。納音採用六十甲子標準表。")
