def filter_and_classify_results(results):
    # 第一步：去除前导0并过滤非数字字符串
    filtered_results = []
    for item in results:
        # 去除前导0
        text = item['text'].lstrip('0')
        
        # 如果去除前导0后为空字符串，说明原文本全是0，我们保留"0"
        if text == '':
            text = '0'
        
        # 检查是否是数字字符串
        if text.isdigit():
            # 创建新项目，使用处理后的text
            new_item = item.copy()
            new_item['text'] = text
            filtered_results.append(new_item)
    
    # 第二步：按type分类
    class_sv_list = []
    other_list = []
    
    for item in filtered_results:
        if item['type'] == 'class_sv':
            class_sv_list.append(item)
        else:
            other_list.append(item)
    
    # 第三步：按href去重
    def deduplicate_by_href(item_list):
        seen_hrefs = set()
        deduplicated = []
        
        for item in item_list:
            if item['href'] not in seen_hrefs:
                seen_hrefs.add(item['href'])
                deduplicated.append(item)
        
        return deduplicated
    
    class_sv_dedup = deduplicate_by_href(class_sv_list)
    other_dedup = deduplicate_by_href(other_list)
    
    # 返回结果
    return {
        'class_sv': class_sv_dedup,
        'other': other_dedup
    }