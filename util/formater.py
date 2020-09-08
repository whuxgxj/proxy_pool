import re

PROVINCE_ZH = [
    "北京", "上海", "天津", "重庆", "黑龙江", "吉林", "辽宁", "内蒙古", "甘肃", "新疆", "西藏", "青海", "四川", "陕西", "宁夏", "河北", "山西", "山东", "河南",
    "湖北", "安徽", "江苏", "浙江", "江西", "福建", "广东", "湖南", "广西", "云南", "海南"
    ]

SPECIAL = ["台湾", "香港", "澳门", "TAIWAN", "HONGKONG", "MACAO", "XIANGGANG", "AOMEN"]

CHINA_CODE = ["中国", "CHINA"]


# 处理地名
def format_location(location):
    location = location.strip()
    # 拆分字符串
    loc_list = re.split(r"\s|省|市|自治区|特别行政区|\_", location)
    # 是否以中国开头
    if any([True for j in loc_list if j.upper() in CHINA_CODE]):
        region = "inside"
        city = re.sub(r"中国|china|China|CHINA|高匿|透明", "", location).strip()
    # 是否属于港澳台
    elif any([True for j in loc_list if j.upper() in SPECIAL]):
        region = "outside"
        city = re.sub(r"高匿|透明", "", location).strip()
    # 是否是大陆省份
    elif any([True for j in loc_list if j.upper() in PROVINCE_ZH]):
        region = "inside"
        city = re.sub(r"高匿|透明", "", location).strip()
    # 外国地名
    else:
        region = "outside"
        city = re.sub(r"高匿|透明", "", location).strip()
    
    return region, city


def format_scheme(scheme):
    scheme = scheme.strip()
    scheme = re.sub(r",|，", "/", scheme.replace("代理", ""))
    if scheme.lower() == "http/https":
        return "https"
    else:
        return scheme.lower()
