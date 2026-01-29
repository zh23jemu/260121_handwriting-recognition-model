import pickle
import os

# 字符字典文件路径
char_dict_path = 'char_dict'

print(f"查看字符字典内容: {char_dict_path}")
print(f"文件是否存在: {os.path.exists(char_dict_path)}")

if os.path.exists(char_dict_path):
    try:
        # 加载字符字典
        with open(char_dict_path, 'rb') as f:
            char_dict = pickle.load(f)
        
        print(f"\n字符字典加载成功!")
        print(f"字典大小: {len(char_dict)} 个字符")
        
        # 显示前20个字符
        print("\n前20个字符:")
        for i, (char, idx) in enumerate(list(char_dict.items())[:20]):
            print(f"{i+1:3d}: '{char}' -> {idx}")
        
        # 显示后20个字符
        print("\n后20个字符:")
        for i, (char, idx) in enumerate(list(char_dict.items())[-20:]):
            print(f"{len(char_dict)-20+i+1:3d}: '{char}' -> {idx}")
        
        # 显示一些特殊字符
        print("\n部分常用字符:")
        common_chars = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '人', '口', '日', '月', '水', '火', '木', '金', '土']
        for char in common_chars:
            if char in char_dict:
                print(f"'{char}' -> {char_dict[char]}")
            else:
                print(f"'{char}' 不在字典中")
                
    except Exception as e:
        print(f"加载字典失败: {e}")
else:
    print("字符字典文件不存在!")
