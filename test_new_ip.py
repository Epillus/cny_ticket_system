import ssl
import urllib.request

# 创建一个不验证证书的SSL上下文
context = ssl._create_unverified_context()

try:
    # 测试新的IP地址
    new_ip = '192.168.3.73'
    
    print(f"测试新IP访问: https://{new_ip}:5001")
    with urllib.request.urlopen(f'https://{new_ip}:5001', context=context) as response:
        print(f"访问成功，状态码: {response.getcode()}")
        print(f"响应头: {response.info()}")
        
    print(f"\n✅ HTTPS测试通过！")
    print(f"\n新的访问地址：")
    print(f"- 手机扫码端: https://{new_ip}:5001/scan")
    print(f"- 电脑管理端: https://{new_ip}:5001/admin")
    print(f"- 首页: https://{new_ip}:5001")
    
except Exception as e:
    print(f"\n❌ HTTPS测试失败: {e}")
    import traceback
    traceback.print_exc()
