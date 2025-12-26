import pandas as pd
import os
import time

class CSVManager:
    def __init__(self, file_path):
        self.file_path = file_path
        # 确保文件存在
        if not os.path.exists(self.file_path):
            # 创建一个空的DataFrame
            df = pd.DataFrame()
            df.to_csv(self.file_path, index=False)
    
    def read(self):
        """读取CSV文件"""
        return pd.read_csv(self.file_path)
    
    def write(self, df):
        """写入CSV文件"""
        df.to_csv(self.file_path, index=False)
    
    def find_by_id(self, ticket_id, id_column='ticket_id'):
        """根据ID查询记录"""
        df = self.read()
        result = df[df[id_column] == ticket_id]
        return result if not result.empty else None
    
    def update_status(self, ticket_id, status, status_column='status'):
        """更新票状态"""
        df = self.read()
        if ticket_id in df['ticket_id'].values:
            df.loc[df['ticket_id'] == ticket_id, status_column] = status
            # 如果是检票状态，记录检票时间
            if status == 'checked':
                df.loc[df['ticket_id'] == ticket_id, 'checkin_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
            self.write(df)
            return True
        return False
    
    def add_record(self, record):
        """添加新记录"""
        df = self.read()
        new_record = pd.DataFrame([record])
        df = pd.concat([df, new_record], ignore_index=True)
        self.write(df)
        return True
    
    def get_today_records(self, date_column='checkin_time'):
        """获取当天的记录"""
        df = self.read()
        if df.empty or date_column not in df.columns:
            return pd.DataFrame()
        
        # 过滤当天的记录
        today = time.strftime('%Y-%m-%d')
        df['checkin_date'] = pd.to_datetime(df[date_column]).dt.date
        today_date = pd.to_datetime(today).date()
        return df[df['checkin_date'] == today_date]
    
    def export_today(self, output_path=None):
        """导出当天的记录"""
        today_df = self.get_today_records()
        if today_df.empty:
            return None
        
        if output_path is None:
            today = time.strftime('%Y-%m-%d')
            output_path = f'data/today_attendees_{today}.csv'
        
        today_df.to_csv(output_path, index=False)
        return output_path
    
    def get_stats(self):
        """获取统计信息"""
        df = self.read()
        total = len(df)
        checked = len(df[df['status'] == 'checked']) if 'status' in df.columns else 0
        unchecked = total - checked
        
        return {
            'total': total,
            'checked': checked,
            'unchecked': unchecked
        }
    
    def clear_data(self):
        """清空数据（慎用）"""
        # 创建一个空的DataFrame，保留列名
        df = self.read()
        if not df.empty:
            df = df.iloc[0:0]
            self.write(df)
        return True

# 使用示例
if __name__ == "__main__":
    # 示例：创建一个CSV管理器实例
    csv_manager = CSVManager('data/test_tickets.csv')
    
    # 添加示例数据
    sample_data = {
        'ticket_id': 'T20250001',
        'name': '张三',
        'status': 'unchecked',
        'checkin_time': ''
    }
    csv_manager.add_record(sample_data)
    
    # 查询数据
    ticket = csv_manager.find_by_id('T20250001')
    print("查询结果:", ticket)
    
    # 更新状态
    csv_manager.update_status('T20250001', 'checked')
    
    # 再次查询
    ticket = csv_manager.find_by_id('T20250001')
    print("更新后的结果:", ticket)
    
    # 获取统计信息
    stats = csv_manager.get_stats()
    print("统计信息:", stats)
