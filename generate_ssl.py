import os
import ssl
import ipaddress
from datetime import datetime, timedelta, UTC
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.backends import default_backend

# 生成自签名SSL证书
def generate_ssl_cert():
    # 生成私钥
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    # 生成证书请求
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "CN"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Beijing"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Beijing"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "School"),
        x509.NameAttribute(NameOID.COMMON_NAME, "192.168.31.167"),
    ])
    
    # 配置证书
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.now(UTC)
    ).not_valid_after(
        # 证书有效期10年
        datetime.now(UTC) + timedelta(days=3650)
    ).add_extension(
        x509.SubjectAlternativeName([x509.IPAddress(ipaddress.IPv4Address('192.168.31.167'))]),
        critical=False,
    ).sign(private_key, hashes.SHA256(), default_backend())
    
    # 保存私钥
    with open("ssl/key.pem", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))
    
    # 保存证书
    with open("ssl/cert.pem", "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    
    print("SSL证书生成成功！")

if __name__ == "__main__":
    # 创建ssl目录
    if not os.path.exists("ssl"):
        os.makedirs("ssl")
    
    generate_ssl_cert()