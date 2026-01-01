from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import pandas as pd
import os
import time


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
# 配置Socket.IO支持CORS
socketio = SocketIO(app, cors_allowed_origins='*',async_mode='threading')

# 添加设备连接管理
connected_devices = {}

@socketio.on('connect')
def handle_connect():
    device_id = request.sid
    connected_devices[device_id] = {
        'type': 'scanner' if 'scan' in request.referrer else 'admin',
        'connect_time': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    print(f"设备已连接: {device_id}")
    emit('device_connected', {'device_id': device_id})

@socketio.on('disconnect')
def handle_disconnect():
    device_id = request.sid
    if device_id in connected_devices:
        del connected_devices[device_id]
    print(f"设备已断开: {device_id}")

@app.route('/get_connected_devices')
def get_connected_devices():
    return jsonify({
        'total': len(connected_devices),
        'devices': connected_devices
    })

# 配置文件路径
TICKETS_CSV = 'data/tickets.csv'
CHECKED_TICKETS_CSV = 'data/checked_tickets.csv'

# 确保数据文件存在
if not os.path.exists(TICKETS_CSV):
    # 创建空的票数据文件
    df = pd.DataFrame(columns=['ticket_id', 'name', 'status', 'checkin_time'])
    df.to_csv(TICKETS_CSV, index=False)

if not os.path.exists(CHECKED_TICKETS_CSV):
    # 创建空的已检票数据文件
    df = pd.DataFrame(columns=['ticket_id', 'name', 'checkin_time'])
    df.to_csv(CHECKED_TICKETS_CSV, index=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan')
def scan():
    return render_template('scan.html')

@app.route('/admin')
def admin():
    # 读取所有票数据
    df = pd.read_csv(TICKETS_CSV)
    return render_template('admin.html', tickets=df.to_dict('records'))

@socketio.on('scan_ticket')
def handle_scan_ticket(data):
    print(f"接收到扫描事件: {data}")
    try:
        ticket_id = data['ticket_id']
        
        # 读取票数据
        df = pd.read_csv(TICKETS_CSV)
        print(f"成功读取票数据，共有 {len(df)} 条记录")
        
        # 查找票
        ticket = df[df['ticket_id'] == ticket_id]
        print(f"查找票号 {ticket_id}，结果: {'找到' if not ticket.empty else '未找到'}")
        
        if ticket.empty:
            emit('ticket_not_found', {'message': '票号不存在'})
            return
        
        name = ticket['name'].values[0]
        status = ticket['status'].values[0]
        print(f"票号 {ticket_id} 对应人员: {name}，状态: {status}")
        
        if status == 'checked':
            emit('ticket_already_checked', {'message': f'{name} 已经检过票了'})
            return
        
        # 更新票状态
        df.loc[df['ticket_id'] == ticket_id, 'status'] = 'checked'
        checkin_time = time.strftime('%Y-%m-%d %H:%M:%S')
        df.loc[df['ticket_id'] == ticket_id, 'checkin_time'] = checkin_time
        df.to_csv(TICKETS_CSV, index=False)
        print(f"更新票状态成功: {ticket_id} -> checked")
        
        # 添加到已检票数据
        checked_df = pd.read_csv(CHECKED_TICKETS_CSV)
        new_checked = pd.DataFrame([{'ticket_id': ticket_id, 'name': name, 'checkin_time': checkin_time}])
        checked_df = pd.concat([checked_df, new_checked], ignore_index=True)
        checked_df.to_csv(CHECKED_TICKETS_CSV, index=False)
        print(f"添加到已检票数据成功: {ticket_id}")
        
        # 发送响应
        emit('ticket_found', {'name': name, 'ticket_id': ticket_id})
        print(f"发送响应给手机端: 欢迎 {name}!")
        
        # 广播给所有连接的客户端（电脑端）
        socketio.emit('ticket_checked', {'ticket_id': ticket_id, 'name': name, 'checkin_time': checkin_time})
        print(f"广播给电脑端: {ticket_id} - {name}")
        
    except Exception as e:
        print(f"处理扫描事件时出错: {e}")
        import traceback
        traceback.print_exc()
        emit('ticket_not_found', {'message': '处理错误，请重试'})

@app.route('/export_today')
def export_today():
    # 获取今天的日期
    today = time.strftime('%Y-%m-%d')
    
    # 读取已检票数据
    df = pd.read_csv(CHECKED_TICKETS_CSV)
    
    # 过滤今天的记录
    df['checkin_date'] = pd.to_datetime(df['checkin_time']).dt.date
    today_date = pd.to_datetime(today).date()
    today_df = df[df['checkin_date'] == today_date]
    
    # 导出为CSV
    output_file = f'data/today_attendees_{today}.csv'
    today_df[['ticket_id', 'name', 'checkin_time']].to_csv(output_file, index=False)
    
    return jsonify({'message': '导出成功', 'file': output_file})

@app.route('/get_today_attendees')
def get_today_attendees():
    # 获取今天的日期
    today = time.strftime('%Y-%m-%d')
    
    # 读取已检票数据
    df = pd.read_csv(CHECKED_TICKETS_CSV)
    
    # 过滤今天的记录
    df['checkin_date'] = pd.to_datetime(df['checkin_time']).dt.date
    today_date = pd.to_datetime(today).date()
    today_df = df[df['checkin_date'] == today_date]
    
    return jsonify(today_df[['ticket_id', 'name', 'checkin_time']].to_dict('records'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    socketio.run(app, 
                 host='0.0.0.0', 
                 port=port, 
                 debug=False) 