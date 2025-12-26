import qrcode
import pandas as pd
import os
from PIL import Image, ImageDraw, ImageFont

class QRCodeGenerator:
    def __init__(self, base_dir='static/qr_codes'):
        self.base_dir = base_dir
        # 创建二维码存储目录
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
    
    def generate_qr(self, ticket_id, output_path):
        """生成单个二维码"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(ticket_id)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 添加票号文字
        img_with_text = self._add_text_to_image(img, ticket_id)
        
        img_with_text.save(output_path)
        return output_path
    
    def _add_text_to_image(self, img, text):
        """在二维码下方添加文字"""
        # 转换为RGBA模式
        img = img.convert('RGBA')
        
        # 创建一个新的图像，高度增加以容纳文字
        new_height = img.height + 50
        new_img = Image.new('RGBA', (img.width, new_height), (255, 255, 255, 255))
        
        # 将二维码粘贴到新图像
        new_img.paste(img, (0, 0))
        
        # 添加文字
        draw = ImageDraw.Draw(new_img)
        
        try:
            # 尝试使用系统字体
            font = ImageFont.truetype('arial.ttf', 24)
        except:
            # 如果没有找到字体，使用默认字体
            font = ImageFont.load_default()
        
        # 计算文字位置（居中）
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (img.width - text_width) // 2
        y = img.height + 10
        
        draw.text((x, y), text, fill=(0, 0, 0), font=font)
        
        return new_img
    
    def generate_qr_codes_from_csv(self, input_csv, output_csv='data/tickets.csv'):
        """从CSV文件批量生成二维码"""
        # 读取输入CSV文件
        df = pd.read_csv(input_csv)
        
        # 确保包含必要的列
        if 'ticket_id' not in df.columns or 'name' not in df.columns:
            raise ValueError("CSV文件必须包含'ticket_id'和'name'列")
        
        # 添加状态和检票时间列
        df['status'] = 'unchecked'
        df['checkin_time'] = ''
        
        # 生成二维码
        qr_paths = []
        for index, row in df.iterrows():
            ticket_id = row['ticket_id']
            qr_filename = f"{ticket_id}.png"
            qr_path = os.path.join(self.base_dir, qr_filename)
            self.generate_qr(ticket_id, qr_path)
            qr_paths.append(qr_filename)
        
        # 添加二维码路径列
        df['qr_code_path'] = qr_paths
        
        # 保存到输出CSV文件
        df.to_csv(output_csv, index=False)
        
        return df
    
    def generate_sample_data(self, num_tickets=100, output_csv='data/tickets.csv'):
        """生成示例数据并生成二维码"""
        # 生成示例数据
        data = []
        for i in range(1, num_tickets + 1):
            ticket_id = f"T{2025:04d}{i:04d}"  # 格式：T20250001
            name = f"观众{i}"
            data.append({
                'ticket_id': ticket_id,
                'name': name,
                'status': 'unchecked',
                'checkin_time': ''
            })
        
        df = pd.DataFrame(data)
        
        # 生成二维码
        qr_paths = []
        for index, row in df.iterrows():
            ticket_id = row['ticket_id']
            qr_filename = f"{ticket_id}.png"
            qr_path = os.path.join(self.base_dir, qr_filename)
            self.generate_qr(ticket_id, qr_path)
            qr_paths.append(qr_filename)
        
        # 添加二维码路径列
        df['qr_code_path'] = qr_paths
        
        # 保存到CSV文件
        df.to_csv(output_csv, index=False)
        
        return df

if __name__ == "__main__":
    # 生成示例数据和二维码
    generator = QRCodeGenerator()
    generator.generate_sample_data(num_tickets=100)
    print("示例数据和二维码生成完成！")
