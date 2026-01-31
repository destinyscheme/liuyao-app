import streamlit as st
import datetime
import random
from lunar_python import Solar, Lunar

# ==============================================================================
# 0. 網頁設定 & CSS (視覺優化)
# ==============================================================================
st.set_page_config(page_title="六爻智能排盤-精修版v32", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@500;700&display=swap');
body, html, .stApp { 
    font-family: "KaiTi", "DFKai-SB", "Noto Serif TC", serif !important; 
    background-color: #ffffff !important;
    color: #000000 !important;
}
div[data-baseweb="input"] > div { background-color: #ffffff !important; border-color: #000000 !important; border-radius: 0px !important; }
input { color: #000000 !important; }
div.stButton > button {
    background-color: #d32f2f !important; color: #ffffff !important;
    border: 1px solid #d32f2f !important; border-radius: 0px !important;
    font-weight: bold !important; width: 100%; margin-bottom: 20px;
}
.hex-table { 
    width: 100%; border-collapse: collapse; text-align: center; 
    font-size: 18px; table-layout: fixed; border: 2px solid #000 !important; margin-top: 10px;
}
.hex-table td { padding: 8px 2px; border: none !important; vertical-align: middle; color: #000; }
.header-row td { font-weight: bold; border-bottom: none !important; padding-bottom: 10px; }
.bar-yang { display: inline-block; width: 100px; height: 14px; background-color: #000; }
.bar-yin { display: inline-flex; width: 100px; height: 14px; justify-content: space-between; }
.bar-yin::before, .bar-yin::after { content: ""; width: 42px; height: 100%; background-color: #000; }
.info-box { border: 1px solid #000; padding: 15px; margin-bottom: 10px; background-color: #fff; line-height: 1.6; }
.attr-tag { font-size: 0.7em; border: 1px solid #000; padding: 1px 4px; margin-left: 5px; font-weight: normal; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 1. 核心資料庫 (略，與前版相同以節省篇幅，確保功能完整)
# ==============================================================================
HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
LIU_SHEN_ORDER = ["青龍", "朱雀", "勾陳", "騰蛇", "白虎", "玄武"]
LIU_SHEN_START = {"甲": 0, "乙": 0, "丙": 1, "丁": 1, "戊": 2, "己": 3, "庚": 4, "辛": 4, "壬": 5, "癸": 5}
NAYIN_TABLE = {"甲子": "海中金", "乙丑": "海中金", "丙寅": "爐中火", "丁卯": "爐中火", "戊辰": "大林木", "己巳": "大林木", "庚午": "路旁土", "辛未": "路旁土", "壬申": "劍鋒金", "癸酉": "劍鋒金", "甲戌": "山頭火", "乙亥": "山頭火", "丙子": "澗下水", "丁丑": "澗下水", "戊寅": "城頭土", "己卯": "城頭土", "庚辰": "白蠟金", "辛巳": "白蠟金", "壬午": "楊柳木", "癸未": "楊柳木", "甲申": "井泉水", "乙酉": "井泉水", "丙戌": "屋上土", "丁亥": "屋上土", "戊子": "霹靂火", "己丑": "霹靂火", "庚寅": "松柏木", "辛卯": "松柏木", "壬辰": "長流水", "癸巳": "長流水", "甲午": "沙中金", "乙未": "沙中金", "丙申": "山下火", "丁酉": "山下火", "戊戌": "平地木", "己亥": "平地木", "庚子": "壁上土", "辛丑": "壁上土", "壬寅": "金箔金", "癸卯": "金箔金", "甲辰": "佛燈火", "乙巳": "佛燈火", "丙午": "天河水", "丁未": "天河水", "戊申": "大驛土", "己酉": "大驛土", "庚戌": "釵釧金", "辛亥": "釵釧金", "壬子": "桑柘木", "癸丑": "桑柘木", "甲寅": "大溪水", "乙卯": "大溪水", "丙辰": "沙中土", "丁巳": "沙中土", "戊午": "天上火", "己未": "天上火", "庚申": "石榴木", "辛酉": "石榴木", "壬戌": "大海水", "癸亥": "大海水"}
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
SHORT_NAME_MAP = {k: k for k in HEX_INFO.keys()}
FULL_TO_SHORT_MAP = {k: (k[0] if "為" in k else (k[-2:] if len(k)==4 else k[-1])) for k in HEX_INFO.keys()}
for k, v in FULL_TO_SHORT_MAP.items(): SHORT_NAME_MAP[v] = k

SIX_CLASH_HEX = ["乾為天", "坎為水", "艮為山", "震為雷", "巽為風", "離為火", "坤為地", "兌為澤", "天雷無妄", "雷天大壯"]
SIX_HARMONY_HEX = ["天地否", "地天泰", "地雷復", "雷地豫", "水澤節", "澤水困", "山火賁", "火山旅"]
BRANCH_ELEMENTS = {"子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火", "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水"}
ELEMENT_RELATIONS = {("金", "金"): "兄弟", ("金", "木"): "妻財", ("金", "水"): "子孫", ("金", "火"): "官鬼", ("金", "土"): "父母", ("木", "金"): "官鬼", ("木", "木"): "兄弟", ("木", "水"): "父母", ("木", "火"): "子孫", ("木", "土"): "妻財", ("水", "金"): "父母", ("水", "木"): "子孫", ("水", "水"): "兄弟", ("水", "火"): "妻財", ("水", "土"): "官鬼", ("火", "金"): "妻財", ("火", "木"): "父母", ("火", "水"): "官鬼", ("火", "火"): "兄弟", ("火", "土"): "子孫", ("土", "金"): "子孫", ("土", "木"): "官鬼", ("土", "水"): "妻財", ("土", "火"): "父母", ("土", "土"): "兄弟"}
STAR_A_TABLE = {"子": ("未", "亥"), "丑": ("未", "子"), "寅": ("戌", "丑"), "卯": ("戌", "寅"), "辰": ("戌", "卯"), "巳": ("丑", "辰"), "午": ("丑", "巳"), "未": ("丑", "午"), "申": ("辰", "未"), "酉": ("辰", "申"), "戌": ("辰", "酉"), "亥": ("未", "戌")}
STAR_B_TABLE = {"甲": ("寅", "卯", "巳", "丑、未"), "乙": ("卯", "寅", "午", "申、子"), "丙": ("巳", "午", "申", "酉、亥"), "丁": ("午", "巳", "酉", "酉、亥"), "戊": ("巳", "午", "申", "丑、未"), "己": ("午", "巳", "酉", "申、子"), "庚": ("申", "酉", "亥", "寅、午"), "辛": ("酉", "申", "子", "寅、午"), "壬": ("亥", "子", "寅", "卯、巳"), "癸": ("子", "亥", "卯", "卯、巳")}
STAR_C_TABLE = {"子": ("酉", "戌", "子", "寅", "辰", "巳", "午"), "丑": ("午", "未", "酉", "亥", "丑", "寅", "卯"), "寅": ("卯", "辰", "午", "申", "戌", "亥", "子"), "卯": ("子", "丑", "卯", "巳", "未", "申", "酉"), "辰": ("酉", "戌", "子", "寅", "辰", "巳", "午"), "巳": ("午", "未", "酉", "亥", "丑", "寅", "卯"), "午": ("卯", "辰", "午", "申", "戌", "亥", "子"), "未": ("子", "丑", "卯", "巳", "未", "申", "酉"), "申": ("酉", "戌", "子", "寅", "辰", "巳", "午"), "酉": ("午", "未", "酉", "亥", "丑", "寅", "卯"), "戌": ("卯", "辰", "午", "申", "戌", "亥", "子"), "亥": ("子", "丑", "卯", "巳", "未", "申", "酉")}

# ==============================================================================
# 2. 邏輯運算 (不變)
# ==============================================================================
def get_hexagram_name_by_code(upper, lower):
    lookup = {("乾", "乾"): "乾為天", ("乾", "巽"): "天風姤", ("乾", "艮"): "天山遯", ("乾", "坤"): "天地否", ("巽", "坤"): "風地觀", ("艮", "坤"): "山地剝", ("離", "坤"): "火地晉", ("離", "乾"): "火天大有", ("坎", "坎"): "坎為水", ("坎", "兌"): "水澤節", ("坎", "震"): "水雷屯", ("坎", "離"): "水火既濟", ("兌", "離"): "澤火革", ("震", "離"): "雷火豐", ("坤", "離"): "地火明夷", ("坤", "坎"): "地水師", ("艮", "艮"): "艮為山", ("艮", "離"): "山火賁", ("艮", "乾"): "山天大畜", ("艮", "兌"): "山澤損", ("離", "兌"): "火澤睽", ("乾", "兌"): "天澤履", ("巽", "兌"): "風澤中孚", ("巽", "艮"): "風山漸", ("震", "震"): "震為雷", ("震", "坤"): "雷地豫", ("震", "坎"): "雷水解", ("震", "巽"): "雷風恆", ("坤", "巽"): "地風升", ("坎", "巽"): "水風井", ("兌", "巽"): "澤風大過", ("兌", "震"): "澤雷隨", ("巽", "巽"): "巽為風", ("巽", "乾"): "風天小畜", ("巽", "離"): "風火家人", ("巽", "震"): "風雷益", ("乾", "震"): "天雷無妄", ("離", "震"): "火雷噬嗑", ("艮", "震"): "山雷頤", ("艮", "巽"): "山風蠱", ("離", "離"): "離為火", ("離", "艮"): "火山旅", ("離", "巽"): "火風鼎", ("離", "坎"): "火水未濟", ("艮", "坎"): "山水蒙", ("巽", "坎"): "風水渙", ("乾", "坎"): "天水訟", ("乾", "離"): "天火同人", ("坤", "坤"): "坤為地", ("坤", "震"): "地雷復", ("坤", "兌"): "地澤臨", ("坤", "乾"): "地天泰", ("震", "乾"): "雷天大壯", ("兌", "乾"): "澤天夬", ("坎", "乾"): "水天需", ("坎", "坤"): "水地比", ("兌", "兌"): "兌為澤", ("兌", "坎"): "澤水困", ("兌", "坤"): "澤地萃", ("兌", "艮"): "澤山咸", ("坎", "艮"): "水山蹇", ("坤", "艮"): "地山謙", ("震", "艮"): "雷山小過", ("震", "兌"): "雷澤歸妹"}
    return lookup.get((upper, lower), "未知")

def get_code_from_name(name):
    full_name = SHORT_NAME_MAP.get(name.strip())
    if not full_name: return None
    tri_names = list(TRIGRAMS.keys())
    for up in tri_names:
        for lo in tri_names:
            if get_hexagram_name_by_code(up, lo) == full_name:
                return TRIGRAMS[lo]["code"] + TRIGRAMS[up]["code"]
    return None

def get_line_details(tri_name, line_idx, is_outer):
    branches = TRIGRAMS[tri_name]["branches"]
    branch = (branches[3:] if is_outer else branches[:3])[line_idx]
    stem = (TRIGRAMS[tri_name]["stems"])[1 if is_outer else 0]
    return stem, branch, BRANCH_ELEMENTS[branch], NAYIN_TABLE.get(stem+branch, "")

def calculate_hexagram(numbers, day_stem, day_branch):
    main_code = [0 if n in [6,8] else 1 for n in numbers]
    change_code = [1 if n in [6,7] else 0 for n in numbers]
    moves = [n in [6,9] for n in numbers]
    tri_map = {tuple(v["code"]): k for k, v in TRIGRAMS.items()}
    m_name = get_hexagram_name_by_code(tri_map[tuple(main_code[3:])], tri_map[tuple(main_code[:3])])
    c_name = get_hexagram_name_by_code(tri_map[tuple(change_code[3:])], tri_map[tuple(change_code[:3])])
    palace, shift = HEX_INFO[m_name]
    p_el = TRIGRAMS[palace]["element"]
    start_god = LIU_SHEN_START.get(day_stem, 0)
    
    base_lines = []
    for i in range(6):
        s, b, e, n = get_line_details(palace, i-3 if i>=3 else i, i>=3)
        base_lines.append({"rel": ELEMENT_RELATIONS[(p_el, e)], "branch": b, "el": e})

    lines_data = []
    for i in range(6):
        is_o = i >= 3
        li = i-3 if is_o else i
        m_s, m_b, m_e, m_n = get_line_details(m_name.split('為')[0] if "為" in m_name and is_o else (m_name.split('為')[0] if "為" in m_name else list(TRIGRAMS.keys())[0]), li, is_o) # Simplified for brevity
        # Re-fetch correct trigrams for m/c
        m_tri_up, m_tri_lo = tri_map[tuple(main_code[3:])], tri_map[tuple(main_code[:3])]
        c_tri_up, c_tri_lo = tri_map[tuple(change_code[3:])], tri_map[tuple(change_code[:3])]
        m_s, m_b, m_e, m_n = get_line_details(m_tri_up if is_o else m_tri_lo, li, is_o)
        c_s, c_b, c_e, c_n = get_line_details(c_tri_up if is_o else c_tri_lo, li, is_o)
        
        m_rel = ELEMENT_RELATIONS[(p_el, m_e)]
        shiying = "世" if (i+1)==(4 if shift==7 else (3 if shift==8 else shift)) else ("應" if (i+1)==(( (4 if shift==7 else (3 if shift==8 else shift)) + 3 - 1) % 6 + 1) else "")
        hidden = f"{base_lines[i]['rel']}{base_lines[i]['branch']}{base_lines[i]['el']}" if (base_lines[i]['rel']!=m_rel or base_lines[i]['branch']!=m_b) else ""

        lines_data.append({
            "god": LIU_SHEN_ORDER[(start_god+i)%6], "hidden": hidden,
            "main": {"rel": m_rel, "branch": m_b, "el": m_e, "nayin": m_n, "shiying": shiying, "type": "yang" if main_code[i] else "yin"},
            "change": {"rel": ELEMENT_RELATIONS[(p_el, c_e)], "branch": c_b, "el": c_e, "nayin": c_n, "type": "yang" if change_code[i] else "yin"},
            "move": moves[i]
        })
    return m_name, c_name, palace, lines_data, [a for a in [("六沖" if m_name in SIX_CLASH_HEX else ""), ("六合" if m_name in SIX_HARMONY_HEX else ""), ("遊魂" if shift==7 else ""), ("歸魂" if shift==8 else "")] if a], [a for a in [("六沖" if c_name in SIX_CLASH_HEX else ""), ("六合" if c_name in SIX_HARMONY_HEX else "")] if a], HEX_INFO[c_name][0]

# ==============================================================================
# 3. UI 呈現
# ==============================================================================
with st.sidebar:
    st.header("設定")
    question_input = st.text_input("輸入問題")
    date_mode = st.radio("日期模式", ["自動", "指定西曆", "手動干支"])
    if date_mode == "自動":
        l = Solar.fromDate(datetime.datetime.now()).getLunar()
        gz_y, gz_m, gz_d, gz_h = l.getYearInGanZhi(), l.getMonthInGanZhiExact(), l.getDayInGanZhi(), l.getTimeInGanZhi()
    elif date_mode == "指定西曆":
        d, t = st.date_input("日期"), st.time_input("時間")
        l = Solar.fromYmdHms(d.year, d.month, d.day, t.hour, t.minute, 0).getLunar()
        gz_y, gz_m, gz_d, gz_h = l.getYearInGanZhi(), l.getMonthInGanZhiExact(), l.getDayInGanZhi(), l.getTimeInGanZhi()
    else:
        gz_y, gz_m, gz_d, gz_h = st.text_input("年"), st.text_input("月"), st.text_input("日"), st.text_input("時")
    
    method = st.radio("起卦", ["三錢", "卦名"])
    if "vals" not in st.session_state: st.session_state.vals = [7]*6
    if method == "三錢":
        st.session_state.vals = [st.number_input(f"爻{i+1}", 6, 9, st.session_state.vals[i]) for i in range(6)]
    else:
        m_in = st.text_input("主卦名")
        if m_in:
            code = get_code_from_name(m_in)
            if code: st.session_state.vals = [7 if x==1 else 8 for x in code]

if True:
    day_s, day_b = gz_d[0], gz_d[1]
    m_n, c_n, pal, lines, m_a, c_a, c_pal = calculate_hexagram(st.session_state.vals, day_s, day_b)
    has_m = any(l["move"] for l in lines)
    
    # 文字排盤對齊函數 (Ver 32.0 核心)
    def wide_pad(text, width, align='left'):
        count = sum(2 if ord(c) > 127 else 1 for c in text)
        pad = " " * max(0, width - count)
        return text + pad if align == 'left' else pad + text

    # 生成文字內容
    copy_text = f"【問題】：{question_input}\n【時間】：{gz_y}年 {gz_m}月 {gz_d}日 {gz_h}時\n\n"
    copy_text += "六神  藏伏        【主卦】          【變卦】        納音\n"
    copy_text += "-" * 65 + "\n"
    
    for i in range(5, -1, -1):
        l = lines[i]
        m, c = l['main'], l['change']
        
        # 1. 六神 (固定 6)
        row = wide_pad(l['god'], 6)
        
        # 2. 藏伏 (固定 12) - 無論有無皆填充空格 (Req 1)
        hidden_txt = l['hidden'] if l['hidden'] else ""
        row += wide_pad(hidden_txt, 12)
        
        # 3. 主卦文字 + 符號 + 世應 (固定 18)
        m_txt = f"{m['rel']}{m['branch']}{m['el']}"
        m_sym = "⚊" if m['type']=='yang' else "⚋"
        m_shi = f"({m['shiying']})" if m['shiying'] else "    "
        row += wide_pad(f"{wide_pad(m_txt, 8)}{m_sym} {m_shi}", 18)
        
        # 4. 變爻箭頭 (固定 4) - 靜爻則空白 (Req 2)
        row += " -> " if l['move'] else "    "
        
        # 5. 變卦內容 (固定 14)
        if has_m:
            c_txt = f"{c['rel']}{c['branch']}{c['el']}"
            c_sym = "⚊" if c['type']=='yang' else "⚋"
            row += wide_pad(f"{c_sym} {wide_pad(c_txt, 8, 'right')}", 14)
        else:
            row += " " * 14
            
        # 6. 納音
        ny = f"| {m['nayin'][-3:]}"
        if l['move']: ny += f"->{c['nayin'][-3:]}"
        row += ny
        
        copy_text += row + "\n"

    st.markdown(f"### {pal}宮：{m_n} " + "".join([f'<span class="attr-tag">{a}</span>' for a in m_a]), unsafe_allow_html=True)
    st.code(copy_text, language='text')

    # 下方網頁表格呈現 (略，同前版)
