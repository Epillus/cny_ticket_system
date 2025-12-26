import pandas as pd
import os
import ssl
import socket

# 测试CSV文件操作
def test_csv_operations():
    print("测试CSV文件操作...")
    
    # 检查数据目录是否存在
    if not os.path.exists('data'):
        print("错误: data目录不存在")
        return False
    
    # 检查tickets.csv文件
    if not os.path.exists('data/tickets.csv'):
        print("错误: tickets.csv文件不存在")
        return False
    
    # 检查checked_tickets.csv文件
    if not os.path.exists('data/checked_tickets.csv'):
        print("错误: checked_tickets.csv文件不存在")
        return False
    
    # 测试读取tickets.csv
    try:
        df = pd.read_csv('data/tickets.csv')
        print(f"成功读取tickets.csv，共有{len(df)}条记录")
        print(f"列名: {list(df.columns)}")
    except Exception as e:
        print(f"错误: 无法读取tickets.csv - {e}")
        return False
    
    return True

# 测试SSL证书
def test_ssl_certificates():
    print("\n测试SSL证书...")
    
    # 检查ssl目录
    if not os.path.exists('ssl'):
        print("错误: ssl目录不存在")
        return False
    
    # 检查证书文件
    if not os.path.exists('ssl/cert.pem'):
        print("错误: cert.pem文件不存在")
        return False
    
    if not os.path.exists('ssl/key.pem'):
        print("错误: key.pem文件不存在")
        return False
    
    # 测试加载证书
    try:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(certfile='ssl/cert.pem', keyfile='ssl/key.pem')
        print("成功加载SSL证书")
    except Exception as e:
        print(f"错误: 无法加载SSL证书 - {e}")
        return False
    
    return True

# 测试端口连接
def test_port_connection():
    print("\n测试端口连接...")
    
    # 测试端口5001是否开放
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('0.0.0.0', 5001))
        if result == 0:
            print("端口5001已开放")
            return True
        else:
            print("错误: 端口5001未开放")
            return False
    except Exception as e:
        print(f"错误: 测试端口连接时出错 - {e}")
        return False
    finally:
        sock.close()

# 运行所有测试
def run_all_tests():
    print("=== 票务系统测试 ===")
    
    csv_ok = test_csv_operations()
    ssl_ok = test_ssl_certificates()
    port_ok = test_port_connection()
    
    print("\n=== 测试结果 ===")
    print(f"CSV文件操作: {'通过' if csv_ok else '失败'}")
    print(f"SSL证书: {'通过' if ssl_ok else '失败'}")
    print(f"端口连接: {'通过' if port_ok else '失败'}")
    
    if csv_ok and ssl_ok and port_ok:
        print("\n✅ 所有测试通过！系统已准备就绪")
        print("\n使用说明:")
        print("1. 电脑端访问: https://localhost:5001/admin")
        print("2. 手机端访问: https://192.168.31.167:5001/scan")
        print("3. 手机端需要信任自签名SSL证书")
        return True
    else:
        print("\n❌ 部分测试失败，请检查以上错误信息")
        return False

if __name__ == '__main__':
    run_all_tests()
