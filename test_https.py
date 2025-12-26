import ssl
import urllib.request

# 创建一个不验证证书的SSL上下文
context = ssl._create_unverified_context()

try:
    # 测试本地访问
    print("测试本地访问: https://localhost:5001")
    with urllib.request.urlopen('https://localhost:5001', context=context) as response:
        print(f"本地访问成功，状态码: {response.getcode()}")
        print(f"响应头: {response.info()}")
        
    # 测试网络访问
    print("\n测试网络访问: https://192.168.31.167:5001")
    with urllib.request.urlopen('https://192.168.31.167:5001', context=context) as response:
        print(f"网络访问成功，状态码: {response.getcode()}")
        print(f"响应头: {response.info()}")
        
    print("\n✅ 所有HTTPS测试通过！")
    
except Exception as e:
    print(f"\n❌ HTTPS测试失败: {e}")
    import traceback
    traceback.print_exc()
